from __future__ import annotations

from pathlib import Path
import fasttext

_NSFW_MODEL = None
_TOXIC_MODEL = None


def _load_model(possible_names: list[str]):
    for name in possible_names:
        path = Path(name)
        if path.exists():
            return fasttext.load_model(str(path))
    raise FileNotFoundError(f"Could not find any of these model files: {possible_names}")


def _get_nsfw_model():
    global _NSFW_MODEL
    if _NSFW_MODEL is None:
        _NSFW_MODEL = _load_model([
            "cs336_data/assets/dolma_fasttext_nsfw_jigsaw_model.bin",
            "assets/dolma_fasttext_nsfw_jigsaw_model.bin",
            "dolma_fasttext_nsfw_jigsaw_model.bin",
        ])
    return _NSFW_MODEL


def _get_toxic_model():
    global _TOXIC_MODEL
    if _TOXIC_MODEL is None:
        _TOXIC_MODEL = _load_model([
            "cs336_data/assets/dolma_fasttext_hatespeech_jigsaw_model.bin",
            "assets/dolma_fasttext_hatespeech_jigsaw_model.bin",
            "dolma_fasttext_hatespeech_jigsaw_model.bin",
        ])
    return _TOXIC_MODEL


def _normalize_label(label: str) -> str:
    label = label.replace("__label__", "").lower()

    # normalize a few likely variants
    if label in {"1", "true", "yes", "positive", "nsfw"}:
        return "nsfw"
    if label in {"0", "false", "no", "negative", "safe", "sfw"}:
        return "sfw"
    if label in {"toxic", "hate", "hatespeech", "hate_speech"}:
        return "toxic"
    if label in {"non-toxic", "non_toxic", "clean", "neutral", "not_toxic"}:
        return "non-toxic"

    return label


def classify_nsfw(text: str) -> tuple[str, float]:
    model = _get_nsfw_model()
    labels, scores = model.predict(text.replace("\n", " "), k=1)
    return _normalize_label(labels[0]), float(scores[0])


def classify_toxic_speech(text: str) -> tuple[str, float]:
    model = _get_toxic_model()
    labels, scores = model.predict(text.replace("\n", " "), k=1)
    return _normalize_label(labels[0]), float(scores[0])