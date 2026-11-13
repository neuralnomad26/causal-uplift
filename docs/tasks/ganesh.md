# Requirements: Ganesh

**Role:** data owner. You own the data, the frozen split, the EDA and the response baseline, and you write the Problem and data and Results sections.

Read `docs/PLAN.md` first. This page tells you exactly what to build, what files to produce, and how we will check it.

## What you own

| Code | Files |
|---|---|
| Data loading, checksum, sampling, the fixed holdout split | `src/uplift/data.py` |
| EDA, balance check and average effect | `notebooks/01_eda_balance.ipynb` |
| Frozen split, feature cut and response baseline | `notebooks/02_split_baseline.ipynb` |

You can explain every line of these, defend the design, and fix a bug in them.

## Deliverables

| ID | Task | Due | Reviewer |
|---|---|---|---|
| G1 | Open your Stage 1 branch as a pull request | Sat 14 | Neeraj and Niranjan |
| G2 | Align notebook 01 with the final 10 features | Sun 15 | Niranjan |
| G3 | `tests/test_data.py` | Sun 15 | Neeraj |
| G4 | Draft Problem and data (130 words) | Mon 16 | Sai |
| G5 | Draft Results (130 words) | Wed 18 | Niranjan |
| G6 | Number check of your sections | Fri 20 | Sai |
| G7 | Repo cleanup and cold start test | Sun 22 and Mon 23 | Neeraj |

### G1. Open the data pull request
Your branch `ganesh-dev` has the data pipeline and the first EDA. Open a pull request into `main`.
- Title: a short plain description of the change.
- Description: what changed, how to run it, what you checked.
- Do not merge it yourself. Two approvals are needed because everything else builds on it.

Acceptance: the PR is open on Sat 14 and the reviewers have what they need to run it.

### G2. Align notebook 01 with the final features
Today notebook 01 keeps the first 10 features (`f0` to `f9`) by position. The project keeps the 10 features in `results/kept_features.json`, which are `f0, f2, f3, f4, f6, f7, f8, f9, f10, f11`.

Requirements:
1. Load the kept list from `results/kept_features.json`. Do not type the list by hand.
2. Use the development training sample, not a fresh random draw: `make_splits(len(df))`, then `take(df, pool_ids[:1_000_000])`.
3. Recompute the balance table (standardized mean differences, treated vs control) for the 10 kept features, and the figure.
4. Report the average effect with a 95 percent confidence interval for visits and conversion, on the development sample and on the holdout.
5. State in a markdown cell whether the largest absolute standardized difference is below 0.1, and what that means.

Outputs, overwriting the old ones: `results/balance_table_1m.csv`, `results/balance_smd_1m.png`, and a new `results/ate_visit_conversion.csv` with columns `sample, outcome, ate, ci_lo, ci_hi`.

Acceptance: the notebook runs top to bottom from a clean kernel, and every number in the text matches the CSV.

### G3. Tests for the data code
Create `tests/test_data.py`. Use a small `n_rows` such as 10,000 and a small holdout so it runs in seconds. Tests required:
1. The holdout and the training pool have no row in common, and together they cover every row exactly once.
2. The 100k sample is a prefix of the 500k sample, which is a prefix of the 1M sample.
3. The same seed gives the same split. A different seed gives a different split.
4. `treated_share_ok` returns False for a sample taken from the top of an ordered frame (build a small frame with all treated rows first), and True for a random sample of it.
5. `verify_checksum` returns True for a small file with a known hash and False after one byte changes.

Acceptance: `pytest tests/test_data.py` passes, and each test fails if you break the behaviour it checks (try it once, on purpose).

### G4. Draft Problem and data (130 words)
File: `report/sections/problem_and_data.md`. Cover, in order:
1. The question, in one sentence: who actually benefits from an offer, not who is likely to respond.
2. The dataset: Criteo Uplift v2.1, 13,979,592 rows from a randomized experiment, 85 percent treated and 15 percent control, 12 anonymized features of which we keep 10, outcomes visit and conversion.
3. The randomization check and its result.
4. How we split: a fixed 2M row holdout never used for fitting, tuning or feature selection.
5. One sentence on the ordered file and why we sample at random.

Every number must come from a file in `results/` or from `data/README.md`. Put an HTML comment after each number naming its source file.

### G5. Draft Results (130 words)
File: `report/sections/results.md`. Start after Gate G3 on Tue 17, using only the agreed numbers from `results/qini_results_visit_5m.csv`, `results/qini_results_conversion_5m.csv` and `results/h1_tests_5m.csv`. State the H1 verdict first. Give the Qini coefficient of each model with its 95 percent interval, and the extra outcomes per 1,000 contacted at a fixed budget. Refer to the figures by name. Do not interpret here. Interpretation belongs to the Analysis section.

### G6. Number check
On Fri 20, open every number in your two sections and tick it against its source file. List any mismatch in the PR and fix it. After the freeze, no number changes.

### G7. Repo cleanup and cold start test
Sun 22 and Mon 23: clone the repo into a new folder, create a fresh environment from `requirements.txt`, run `pytest` and notebooks 01 and 02. Fix anything that fails. Record the machine, the Python version and the run time in the PR description.

## Reviews you owe

| Review | When |
|---|---|
| Neeraj's Methods section | Thu 19 |
| Sai's learner code (S and T) in the pipeline PR | Sun 15 |

## Oral assessment: questions you must answer well
1. Why is the file ordered, and what would happen if we used its first rows?
2. Why hold out 2M rows, and why are the training samples nested?
3. What does a standardized mean difference measure, and what does your table show?
4. How did you choose the 10 features, and what did dropping the other two cost?
5. What is the average treatment effect on visits and on conversion, and how sure are we?
6. Why do we also develop on visits when the business outcome is conversion?
7. What does the response baseline predict, and why is it the right benchmark?
8. How do we know no test row was used for fitting, tuning or feature selection?

## Definition of done
- [ ] Every deliverable above is merged
- [ ] The code runs from a clean clone
- [ ] Every number in your report sections traces to a file in `results/`
- [ ] You can answer the eight questions without notes
