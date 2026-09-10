# ============================================================
# TRAIN PRODUCTION MACHINE LEARNING MODEL
# ============================================================

from ml import (
    build_multi_season_ml_dataset,
    train_production_model
)

from model_io import save_model


def main():

    # ------------------------------------------------------------
    # BUILD TRAINING DATA
    # ------------------------------------------------------------

    print(
        "\nBUILDING PRODUCTION TRAINING DATASET"
    )
    print(
        "------------------------------------"
    )

    training_dataset = (
        build_multi_season_ml_dataset(
            2021,
            2025
        )
    )

    print(
        f"\nTotal Training Rows: "
        f"{len(training_dataset)}"
    )

    # ------------------------------------------------------------
    # TRAIN PRODUCTION MODEL
    # ------------------------------------------------------------

    print(
        "\nTRAINING PRODUCTION MODEL"
    )
    print(
        "-------------------------"
    )

    model = train_production_model(
        training_dataset
    )

    # ------------------------------------------------------------
    # SAVE MODEL
    # ------------------------------------------------------------

    save_model(
        model,
        "logistic_model.joblib"
    )

    print(
        "\nPRODUCTION MODEL READY"
    )
    print(
        "----------------------"
    )

    print(
        "Training seasons: 2021-2025"
    )

    print(
        "Prediction season: 2026"
    )


if __name__ == "__main__":
    main()