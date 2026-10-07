# Predicting Eruptive Events at Volcanoes from Earthquake Data

Mini-project for UE24CS352A Machine Learning, Section E.

Team: Muhammad Uzair (PES2UG24CS287) and Mokshithreddy Nallaballe (PES2UG24CS284).

This project studies whether earthquake-catalog features can identify whether Kīlauea's Pu'u 'O'o system was erupting when an earthquake occurred. It uses the public earthquake catalog and eruption chronology distributed with the reference project.

## Project structure

```text
data/raw/                 Source earthquake catalog and eruption chronology
src/train.py              Feature engineering, training, threshold tuning, evaluation, plots
src/make_artifacts.py     Two-page report and review presentation generator
outputs/                  Reproducible metrics, engineered features, figures, feature importance
report/                   Final PDF write-up
slides/                   Final presentation
```

## Setup and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/train.py
python src/make_artifacts.py
```

The pipeline uses a chronological split: 70% training, 15% development, and 15% held-out test data. It prevents future earthquake records from entering the feature history of earlier observations. The target is `erupting = 1` when an earthquake timestamp falls inside a dated Pu'u 'O'o eruption interval and `0` otherwise. The development split selects the classification threshold before test evaluation.

## Models and evaluation

The project compares a majority baseline, balanced Logistic Regression, and balanced Random Forest. Features include earthquake location, depth, magnitude, distance from the vent, and earthquake count/maximum magnitude in the preceding 1, 7, and 30 days. The pipeline also writes `feature_importance.csv` and `feature_importance.png`. Because the target is time-dependent and the data distribution changes across the four-year catalog, the report emphasizes ROC-AUC, F1, recall, precision, and Cohen's kappa rather than accuracy alone.

## Data provenance

The raw files originate from the public repository `bmullet/PEEVED`, which accompanies the supplied 2019 CS229 report. The earthquake catalog is attributed there to ANSS/WOVOdat, and the eruption chronology cites the Hawaii Center for Volcanology. This project keeps the raw files unchanged and records the transformation in `src/train.py`.

## Limitations

This is an educational retrospective model, not an operational eruption warning system. It uses catalog events rather than continuous waveform, deformation, gas, or tremor data. The supplied labels describe contemporaneous eruption status, which is different from forecasting an eruption several days in advance. Results should therefore be interpreted as evidence of signal in the catalog, not as a deployable warning capability.
