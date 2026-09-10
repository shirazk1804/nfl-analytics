# ============================================================
# MODEL SAVE / LOAD
# ============================================================

from pathlib import Path
import joblib


MODELS_DIR = (
    Path(__file__).resolve().parent /
    "models"
)

MODELS_DIR.mkdir(
    exist_ok=True
)


def save_model(
    model,
    filename
):

    model_path = (
        MODELS_DIR /
        filename
    )

    joblib.dump(
        model,
        model_path
    )

    print(
        f"\nModel saved: {model_path}"
    )

    return model_path


def load_model(
    filename
):

    model_path = (
        MODELS_DIR /
        filename
    )

    model = joblib.load(
        model_path
    )

    return model