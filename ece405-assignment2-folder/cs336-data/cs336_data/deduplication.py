from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import os
import re
import unicodedata


def exact_line_deduplication(
    input_files: list[os.PathLike],
    output_directory: os.PathLike,
) -> None:
    input_paths = [Path(p) for p in input_files]
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Count all lines across all files
    line_counts: Counter[str] = Counter()

    for path in input_paths:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_counts[line] += 1

    # Write only unique lines
    for path in input_paths:
        out_path = output_dir / path.name
        with path.open("r", encoding="utf-8", errors="ignore") as f_in, \
             out_path.open("w", encoding="utf-8") as f_out:

            for line in f_in:
                if line_counts[line] == 1:
                    f_out.write(line)



def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _word_ngrams(text: str, n: int) -> set[str]:
    words = _normalize_text(text).split()
    if not words:
        return set()
    if len(words) < n:
        return {" ".join(words)}
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}


def _stable_hash(s: str, seed: int) -> int:
    data = f"{seed}::{s}".encode("utf-8", errors="ignore")
    return int(hashlib.md5(data).hexdigest(), 16)


def _minhash_signature(shingles: set[str], num_hashes: int) -> list[int]:
    if not shingles:
        return [0] * num_hashes

    signature = []
    for seed in range(num_hashes):
        minsig = min(_stable_hash(shingle, seed) for shingle in shingles)
        signature.append(minsig)
    return signature


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


class _UnionFind:
    def __init__(self, items: list[int]) -> None:
        self.parent = {x: x for x in items}

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def minhash_deduplication(
    input_files: list[os.PathLike],
    num_hashes: int,
    num_bands: int,
    ngrams: int,
    jaccard_threshold: float,
    output_directory: os.PathLike,
) -> None:

    input_paths = [Path(p) for p in input_files]
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    if num_hashes % num_bands != 0:
        raise ValueError("num_hashes must be divisible by num_bands")

    rows_per_band = num_hashes // num_bands

    texts = []
    shingles_list = []
    signatures = []

    for path in input_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        texts.append(text)

        shingles = _word_ngrams(text, ngrams)
        shingles_list.append(shingles)

        signatures.append(_minhash_signature(shingles, num_hashes))

    # LSH buckets
    buckets = defaultdict(list)

    for doc_idx, signature in enumerate(signatures):
        for band in range(num_bands):
            start = band * rows_per_band
            end = start + rows_per_band
            band_sig = tuple(signature[start:end])
            buckets[(band, band_sig)].append(doc_idx)

    candidate_pairs = set()

    for docs in buckets.values():
        if len(docs) > 1:
            for i in range(len(docs)):
                for j in range(i + 1, len(docs)):
                    candidate_pairs.add((docs[i], docs[j]))

    # Cluster using Union-Find
    uf = _UnionFind(list(range(len(input_paths))))

    for a, b in candidate_pairs:
        sim = _jaccard(shingles_list[a], shingles_list[b])
        if sim >= jaccard_threshold:
            uf.union(a, b)

    clusters = defaultdict(list)
    for i in range(len(input_paths)):
        clusters[uf.find(i)].append(i)

    # Keep one per cluster
    keep = set()
    for members in clusters.values():
        rep = min(members, key=lambda i: str(input_paths[i]))
        keep.add(rep)

    for i, path in enumerate(input_paths):
        if i in keep:
            out_path = output_dir / path.name
            out_path.write_text(texts[i], encoding="utf-8")