# Predicting Eruptive Events from Earthquake Data

**Kilauea Pu'u 'O'o eruption-status classification**
UE24CS352A Machine Learning Mini-Project, Section E

**Authors:** Muhammad Uzair, Mokshithreddy Nallaballe

---

## Overview

This project asks a focused question:

> Can earthquake-catalog features identify whether Kilauea was erupting when an earthquake occurred?

We train classifiers on a historical earthquake catalog and test, on a later held-out period, how well they separate earthquakes that happened **during an eruption** from those that happened **during repose**.

**Scope.** This is a retrospective, educational model. It detects a *signal* in the catalog; it does **not** forecast eruptions days in advance and must not be used as an operational warning system.

## Dataset

| Item | Value |
|---|---|
| Records | 6,485 earthquakes |
| Period | 1983-1986 |
| Documented eruption intervals | 49 |
| Positive rate (engineered data) | 68.9% |

<!-- TODO: add the data source / citation and the file path of the raw catalog and eruption-interval table. -->

**Labels**

- `1` - the earthquake falls inside a documented eruption interval
- `0` - the earthquake occurs during repose

## Method

1. **Labeling:** match each earthquake timestamp against the 49 eruption intervals.
2. **Feature engineering**
   - *Event features:* latitude, longitude, depth, magnitude, distance from the vent.
   - *History features:* earthquake count and maximum magnitude over the previous 1, 7 and 30 days.
   - The current earthquake is **excluded** from its own rolling-history window to prevent direct leakage.
3. **Chronological split:** 70% train / 15% development / 15% held-out test, in time order. A random split would leak information between neighbouring-in-time earthquakes.
4. **Models:** Majority baseline, Logistic Regression, Random Forest.
5. **Thresholds** are selected on the development set only, then applied once to the held-out test set (Random Forest: 0.75).

## Results (held-out test set)

| Model | Accuracy | F1 | Kappa | ROC-AUC |
|---|---|---|---|---|
| Majority Baseline | 0.550 | 0.710 | 0.000 | 0.500 |
| Logistic Regression | 0.475 | 0.086 | 0.041 | **0.961** |
| Random Forest | **0.636** | 0.541 | **0.308** | 0.822 |

**How to read this**

- Logistic Regression ranks eruptive events best (ROC-AUC 0.961), but its accuracy and F1 at the chosen cutoff are poor. Ranking quality and a good cutoff are different things.
- Random Forest, with its threshold tuned on development data, is the most balanced model on the held-out period (best accuracy and kappa).
- The test period is 55% eruptive (the majority baseline's accuracy), versus 68.9% overall, so accuracy alone is misleading.

## Limitations

- **Retrospective:** classifies status at the time of the quake; no forecasting.
- **Few independent intervals:** only 49 eruption intervals, and quakes within one interval are correlated.
- **Threshold sensitivity:** accuracy and F1 shift noticeably with the decision cutoff.
- **Single volcano, single era:** Kilauea, 1983-1986; not tested elsewhere.

## Future work

- Calibrate thresholds on a dedicated development period.
- Use blocked / event-based validation.
- Add waveform, tremor, GPS and gas-emission features.

## Repository structure

<!-- TODO: replace with the real tree. Run `tree -L 2` (or `git ls-files`) in the repo and paste it here, with one line per file saying what it does. -->

```
volcano-eruption-ml/
├── README.md
├── requirements.txt        # TODO: confirm
├── data/                   # TODO: raw + engineered data
├── notebooks/ or src/      # TODO: preprocessing, features, training, evaluation
└── results/                # TODO: metrics tables, figures
```

## Getting started

```bash
git clone https://github.com/mokshithr530/volcano-eruption-ml.git
cd volcano-eruption-ml
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

<!-- TODO: add the exact command or notebook order that reproduces the results table above. -->

## Team

| Name | Contribution |
|---|---|
| Muhammad Uzair | Data, labels, feature engineering, validation split |
| Mokshithreddy Nallaballe | Models, evaluation, results analysis, limitations |

<!-- TODO: edit the table to match who actually did what. -->

## License

<!-- TODO: add a license (for a course project, MIT is common) or remove this section. -->
