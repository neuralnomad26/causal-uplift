# Who Actually Benefits?

Causal machine learning for targeted intervention, on the Criteo Uplift dataset. CSC1181, Group 12.

A normal prediction model finds who is likely to convert. It cannot tell us whose decision an offer actually changed, because some of those people would have converted anyway. This project estimates the effect of the offer for each person (uplift), so a limited budget goes to the people it persuades.

**Hypothesis H1.** At the same budget, uplift targeting delivers more incremental conversions than response targeting.

**Our own question.** How much data does uplift targeting need before it beats response targeting? We rerun the best model on 100k, 500k, 1M and 5M rows.

## Method

1. Check that treatment was randomized (standardized differences between treated and control).
2. Baseline: a response model that predicts the outcome and ignores treatment.
3. Uplift models behind one interface: S-learner, T-learner and X-learner.
4. Evaluate with Qini and AUUC curves, bootstrap confidence intervals and a hypothesis test on the Qini gap.
5. Simulate a targeting policy: the top 10 to 30 percent by uplift, by response and at random.

We use 10 of the 12 anonymized features. Development is on visits first, then final results on 5M rows. See `docs/decision_log.md` for why.

## Data

See [data/README.md](data/README.md) for the links, the checksum and two warnings: the file is ordered, so never take the first rows, and conversion is rare.

## Setup

Python 3.12.

```
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
`

Windows (PowerShell):

`
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

The second install makes `import uplift` work inside the notebooks. Conda also works: `conda env create -f environment.yml`, then `pip install -e .`.

On a Mac, LightGBM needs libomp: `brew install libomp`.

## Repo layout

```
causal-uplift/
  README.md
  requirements.txt     pinned versions
  environment.yml      conda wrapper around requirements.txt
  data/                README only, data files are ignored by git
  notebooks/
    01_eda_balance.ipynb
    02_split_baseline.ipynb
    03_learners.ipynb
    04_evaluation.ipynb
    05_policy_simulation.ipynb
  src/uplift/
    data.py            download, verify, sample, split
    learners.py        S, T and X learners with one interface
    metrics.py         Qini, AUUC, bootstrap
    pipeline.py        end-to-end experiment runner
  results/             scores.parquet, tables and figures
  report/              figures used in the PDF
  docs/decision_log.md one line per decision, and why
```

Notebook numbers match the stages, so the repo reads in the same order as the report.

## Plan

| Stage | Dates | Gate |
|---|---|---|
| 0 Set up and align | Mon 2 to Tue 3 Nov | G0 Tue 3 Nov: everyone can load the data and run the starter notebook |
| 1 Data and baseline | Wed 4 to Mon 9 Nov | G1 Mon 9 Nov: average effect positive and the quick Qini beats random on visits |
| 2 Causal models | Tue 10 to Fri 13 Nov | G2 Fri 13 Nov: one scores file for response, S, T and X |
| 3 Validate and analyse | Sat 14 to Tue 17 Nov | G3 Tue 17 Nov: headline numbers and all figures exist |
| 4 Decide, reflect, freeze | Wed 18 to Fri 20 Nov | G4 Fri 20 Nov: results freeze, tag v1.0 |
| 5 Assemble, review, submit | Sat 21 to Thu 26 Nov | G5 Thu 26 Nov: submitted |

The report is due Fri 27 Nov, 11:59 PM. Oral assessments are in Week 13.

## Working rules

- One branch per task, merged by pull request, with one reviewer from another tier.
- Fixed seeds and one frozen split on disk. Nobody splits again.
- The scores file is the contract: models write `results/scores.parquet`, evaluation only reads it. The file is not committed, so rerun notebook 03 to rebuild it.
- Every figure in the report has code that regenerates it.
- Results freeze on Fri 20 Nov. Tag the repo v1.0.
- Never commit the raw data.

## Result to report section map

Filled in as results land, so every number in the PDF can be traced to code.

| Report section | Notebook | Output |
|---|---|---|
| Problem and data | 01 | |
| Methods | 02, 03 | |
| Results | 04, 05 | |
| Analysis and discussion | 04 | |

## Licence and ethics

The dataset is CC BY-NC-SA 4.0, so we use it for coursework only, with attribution to Criteo. It is anonymized and contains no personally identifying information.
