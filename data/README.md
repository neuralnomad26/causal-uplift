# Data

We use the Criteo Uplift Prediction Dataset, version 2.1.

- Official page, cite this one in the report: https://ailab.criteo.com/criteo-uplift-prediction-dataset/
- Download mirror, 311 MB: https://github.com/jszymon/uplift_sklearn_data/releases/download/Criteo/criteo-research-uplift-v2.1.csv.gz

The official download link returns an error, so we use the mirror. The mirror is a third party copy. Its checksum matches the one published in the libuplift documentation:

```
SHA256  2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc
```

Check it after downloading:

```
shasum -a 256 criteo-research-uplift-v2.1.csv.gz
```

## What is in the file

13,979,592 rows and 16 columns: `f0` to `f11` (anonymized features), `treatment`, `conversion`, `visit` and `exposure`.

| | Treated | Control |
|---|---|---|
| Share of rows | 85% | 15% |
| Conversion rate | 0.309% | 0.194% |
| Visit rate | 4.85% | 3.82% |

Use the `treatment` column, not `exposure`.

## Two things that will break the analysis

1. The file is ordered, not shuffled. The first 5.57M rows are all treated. Never take the first rows or use `nrows`. Always draw a random sample with a fixed seed, then check that the treated share is about 85%.
2. Conversion is rare. A 1M row sample has only about 290 control conversions, and about 90 in a 30% test split. That is too few for a stable Qini curve, so we develop on visits first and rerun final results on 5M rows.

## Samples

| Sample | Rows | Use |
|---|---|---|
| 5M | random, seeded | final results and the data size curve |
| 1M | subset of the 5M sample | development |

The 1M sample sits inside the 5M sample, so the train and test split never leaks across sizes.

Data files are ignored by git. Run the download script in `src/uplift/data.py` to rebuild them.

## Licence

CC BY-NC-SA 4.0. We use the data for coursework only, with attribution to Criteo.
