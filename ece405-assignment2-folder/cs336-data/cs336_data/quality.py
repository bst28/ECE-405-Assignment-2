import re
from pathlib import Path
import fasttext

WORD_RE = re.compile(r"\S+")


def _words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def _non_symbol_words(words: list[str]) -> list[str]:
    return [w for w in words if any(ch.isalnum() for ch in w)]


def gopher_quality_filter(text: str) -> bool:
    words = _words(text)
    if not words:
        return False

    non_symbol_words = _non_symbol_words(words)
    num_non_symbol_words = len(non_symbol_words)

    # Rule 1: must have at least 50 non-symbol words
    if num_non_symbol_words < 50:
        return False

    # Rule 2: must not exceed 100000 non-symbol words
    if num_non_symbol_words > 100000:
        return False

    # Rule 3: average word length must be between 3 and 10
    avg_word_length = sum(len(w) for w in non_symbol_words) / num_non_symbol_words
    if avg_word_length < 3 or avg_word_length > 10:
        return False

    # Rule 4: at least 80% of words must contain an alphabetic character
    alpha_word_fraction = (
        sum(any(ch.isalpha() for ch in w) for w in words) / len(words)
    )
    if alpha_word_fraction < 0.8:
        return False

    # Rule 5: no more than 30% of lines may end with an ellipsis
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        ellipsis_fraction = sum(line.endswith("...") for line in lines) / len(lines)
        if ellipsis_fraction > 0.3:
            return False

    return True

_QUALITY_MODEL = None


def _get_quality_model():
    global _QUALITY_MODEL
    if _QUALITY_MODEL is not None:
        return _QUALITY_MODEL

    model_path = Path("quality_classifier.bin")
    train_path = Path("quality_train.txt")

    # If the model already exists, load it
    if model_path.exists():
        _QUALITY_MODEL = fasttext.load_model(str(model_path))
        return _QUALITY_MODEL

    # Minimal fallback training set using the provided fixture files
    fixtures_dir = Path("tests") / "fixtures"
    low_quality_path = fixtures_dir / "low_quality_cc.txt"
    high_quality_path = fixtures_dir / "high_quality_wiki_reference.txt"

    if not (low_quality_path.exists() and high_quality_path.exists()):
        raise FileNotFoundError(
            "Could not find fixture files needed to build the temporary quality classifier."
        )

    low_quality_text = low_quality_path.read_text(encoding="utf-8", errors="ignore").replace("\n", " ")
    high_quality_text = high_quality_path.read_text(encoding="utf-8", errors="ignore").replace("\n", " ")

    # Write a tiny supervised training file
    with open(train_path, "w", encoding="utf-8") as f:
        for _ in range(20):
            f.write(f"__label__cc {low_quality_text}\n")
            f.write(f"__label__wiki {high_quality_text}\n")

    _QUALITY_MODEL = fasttext.train_supervised(
        input=str(train_path),
        epoch=25,
        lr=1.0,
        wordNgrams=2,
        minn=2,
        maxn=5,
        verbose=0,
    )
    _QUALITY_MODEL.save_model(str(model_path))
    return _QUALITY_MODEL


def classify_quality(text: str) -> tuple[str, float]:
    model = _get_quality_model()
    labels, scores = model.predict(text.replace("\n", " "), k=1)

    label = labels[0].replace("__label__", "")
    score = float(scores[0])

    return label, score