from pathlib import Path
import fasttext

_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    candidate_paths = [
        Path("lid.176.bin"),
        Path("models/lid.176.bin"),
        Path("assets/lid.176.bin"),
        Path("cs336-data/lid.176.bin"),
        Path("cs336-data/models/lid.176.bin"),
    ]

    for path in candidate_paths:
        if path.exists():
            _MODEL = fasttext.load_model(str(path))
            return _MODEL

    raise FileNotFoundError(
        "Could not find lid.176.bin. Put the fastText language ID model in the repo root, "
        "models/, or assets/."
    )


def identify_language(text: str) -> tuple[str, float]:
    model = _get_model()
    labels, scores = model.predict(text.replace("\n", " "), k=1)

    label = labels[0]
    score = float(scores[0])

    if label.startswith("__label__"):
        label = label.replace("__label__", "")

    # normalize Chinese variants for the assignment test
    if label.startswith("zh"):
        label = "zh"

    return label, score