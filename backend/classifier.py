"""Loads the trained TF-IDF + Linear SVM pipeline and predicts a ticket category."""
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "model" / "ticket_classifier.pkl"

_model = None


def get_model():
    """Load the trained pipeline once and reuse it."""
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run: python data/train_model.py"
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_category(subject: str, body: str) -> str:
    """Return the predicted category for a ticket's subject and body."""
    text = f"{subject} {body}".strip()
    return str(get_model().predict([text])[0])
