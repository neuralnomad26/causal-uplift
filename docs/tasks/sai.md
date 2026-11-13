# Requirements: Sai

**Role:** learners and tuning owner. You own the S and T learners, the tuning and the scores pipeline, and you write the Literature review and the Analysis and discussion sections.

Read `docs/PLAN.md` first. This page tells you exactly what to build, what files to produce, and how we will check it.

## What you own

| Code | Files |
|---|---|
| S learner, T learner and the shared interface | `src/uplift/learners.py` |
| Feature cut, tuning and the scores file builder | `src/uplift/pipeline.py` |
| Fitting at four training sizes and writing the scores files | `notebooks/03_learners.ipynb` |

You can explain every line of these, defend the design, and fix a bug in them.

## Background you need first
Read Künzel et al. (2019), the sections on the S and T learners. The paper is on the reading list in `README.md`. In plain words:
- **S learner:** one model that takes the features and the treatment flag. Uplift for a user is the prediction with treatment set to 1 minus the prediction with treatment set to 0.
- **T learner:** two models, one fitted on treated users and one on control users. Uplift is the difference of their predictions.

## Deliverables

| ID | Task | Due | Reviewer |
|---|---|---|---|
| S1 | Install, run `pytest`, run notebook 02 | Sat 14 | Neeraj |
| S2 | Review of the S and T learners and the pipeline | Sun 15 | Ganesh |
| S3 | `tests/test_pipeline.py` | Sun 15 | Neeraj |
| S4 | Tuning sensitivity check | Mon 16 | Ganesh |
| S5 | Draft Literature review (110 words) | Mon 16 | Niranjan |
| S6 | Relative uplift table, added to notebook 04 | Tue 17 | Neeraj |
| S7 | Draft Analysis and discussion (130 words) | Wed 18 | Neeraj |
| S8 | Number check of your sections | Fri 20 | Ganesh |

### S1. Environment check
Clone the repo, create the environment from `requirements.txt`, run `pip install -e .`, then `pytest`, then notebook 02. Write a comment on the pipeline PR with your operating system, Python version and run times. If anything fails, say exactly what, and fix the instructions in `README.md` through a PR.

### S2. Review
Review the S and T learners in `src/uplift/learners.py` and `src/uplift/pipeline.py` in the pipeline PR. Leave at least five specific comments. Check at least these:
1. The S learner reads both predictions from the same fitted model and subtracts them.
2. The T learner fits each model only on its own group.
3. `tune_base` and `select_features` use training rows only.
4. All learners share the same tuned settings, so the comparison is fair.
5. Nothing in the pipeline touches the holdout before scoring.
Write what you checked, not only what you found.

### S3. Tests for the pipeline
Create `tests/test_pipeline.py` using a small synthetic frame (about 20,000 rows) so it runs in seconds. Tests required:
1. `select_features` on a frame with 12 features, where 2 are pure noise, drops exactly those 2 and returns 10 features. The log has one row per dropped feature.
2. `tune_base` with a tiny grid of 2 settings returns one of them, and its table has one row per setting.
3. `build_scores` returns a frame with the columns `treatment`, `visit`, `conversion` and one column `{model}_{outcome}` for each of `response, s, t, x` and each outcome, with no missing values and one row per test id.
4. The response column does not change if you change only the treatment column of the training rows. (It must ignore treatment.)

Acceptance: `pytest tests/test_pipeline.py` passes in under 60 seconds.

### S4. Tuning sensitivity check
Question: does our conclusion depend on tuning? Create `notebooks/06_sensitivity.ipynb`.
1. Load the development training sample (1M rows) and the holdout, as in notebook 03.
2. Fit the T learner twice on visits: once with the tuned settings from `results/best_params.json`, once with the untuned `BASE_PARAMS`.
3. Compute the Qini coefficient of each on the holdout, with 95 percent bootstrap intervals from `metrics.bootstrap_metrics`, using the same resamples for both.
4. Report the difference and its interval.

Output: `results/sensitivity_tuning_visit.csv` with columns `setting, qini_coef, ci_lo, ci_hi`. End the notebook with one sentence saying whether tuning matters.

### S5. Draft Literature review (110 words)
File: `report/sections/literature_review.md`. Cite at least these four, with the reasons:
- Radcliffe (2007): the Qini curve and uplift evaluation.
- Künzel et al. (2019): the S, T and X learners.
- Gutierrez and Gérardy (2017): a review of uplift modelling.
- Diemert et al. (2018): the benchmark dataset.
Optionally add Ascarza (2018) on why targeting by response can fail. Finish with one sentence on what our project adds: a head to head comparison of response targeting and the three learners at scale, with a data size curve. Send Niranjan the full reference for each citation.

### S6. Relative uplift table
Add a cell to `notebooks/04_evaluation.ipynb`, in a pull request. For the 5M scores file and for visits: split holdout users into 10 deciles of the response score. For each decile give the control outcome rate, the observed uplift, and the ratio of uplift to the control rate (relative uplift). Output `results/relative_uplift_response_deciles.csv`.
Why: if relative uplift is roughly flat across deciles, then users who respond more also gain more in absolute terms, which would explain why the response baseline is competitive. This is the key piece of evidence for the Analysis section.

### S7. Draft Analysis and discussion (130 words)
File: `report/sections/analysis.md`. Explain why the results look the way they do. Use only evidence in `results/`: the decile table, the seed stability table, the data size curve, the planted effect test and your relative uplift table. State what the evidence supports and what it does not. Keep claims as strong as the intervals allow.

### S8. Number check
Fri 20: tick every number in your two sections against its source file and fix any mismatch.

## Reviews you owe

| Review | When |
|---|---|
| Neeraj's evaluation code (`metrics.py`) in the pipeline PR | Sun 15 |
| Ganesh's Problem and data section | Tue 17 |
| Neeraj's Abstract | Sat 21 |

## Oral assessment: questions you must answer well
1. How does the S learner turn one model into an uplift score, and what can go wrong with it?
2. How does the T learner differ, and why can it be noisy for a small control group?
3. Why do all models share one tuned setting?
4. How was the tuning done, and why only on training rows?
5. Why does the response baseline ignore treatment?
6. What does the scores file contain, and why does the evaluation only read it?
7. Did tuning change our conclusion? What does your sensitivity check show?
8. How do you explain the relative uplift table?

## Definition of done
- [ ] Every deliverable above is merged
- [ ] The code runs from a clean clone
- [ ] Every number in your report sections traces to a file in `results/`
- [ ] You can answer the eight questions without notes
