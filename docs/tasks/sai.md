# Requirements: Sai

**Role:** learners and analysis owner. You own the tests for the pipeline, two analysis notebooks (tuning sensitivity and segments), and three pieces of the report: the Literature review, the Ethics and legal section and the bibliography.

Read `docs/PLAN.md` first. Every task below has the same parts:
- **Task:** what to do.
- **Steps:** the order to do it in.
- **Expectations:** the quality bar.
- **Acceptance criteria:** a checklist your reviewer will tick. A task is done only when every box is ticked.

## Your tasks at a glance

| ID | Task | Due | Time | Branch | Reviewer |
|---|---|---|---|---|---|
| S1 | Set up and first run | Sat 14 | 1 to 2 h | none | Neeraj |
| S2 | Review the S and T learners and the pipeline | Mon 16 | 2 h | PR comments | Ganesh |
| S3 | Tests for the pipeline | Tue 17 to Wed 18 | 3 h | `sai/test_pipeline` | Neeraj |
| S4 | Tuning sensitivity check (notebook 06) | Thu 19 to Fri 20 | 3 h | `sai/tuning_sensitivity` | Ganesh |
| S5 | Draft Literature review | Sat 21 to Sun 22 | 2 h | `sai/literature_review` | Niranjan |
| S6 | Draft Ethics and legal | Sat 21 | 1.5 h | `sai/ethics_and_legal` | Ganesh |
| S7 | Bibliography | Sun 22 | 1.5 h | `sai/references` | Niranjan |
| S8 | Segment analysis (notebook 08) | Wed 18 to Fri 20 | 3 h | `sai/segments` | Ganesh |
| S9 | Number check and proofreading | Mon 23 and Wed 25 | 2 h | PR comments | Ganesh |

## What you need to understand first

- **Uplift.** The effect of an offer on one user: what happens with the offer minus what would have happened without it. We never see both, so we estimate it from groups of similar users.
- **S learner.** One model that takes the features and the treatment flag. A user's uplift score is the prediction with treatment set to 1 minus the prediction with treatment set to 0.
- **T learner.** Two models: one fitted on treated users, one on control users. The uplift score is the difference of their predictions.
- **Response baseline.** A model that predicts who is likely to visit and ignores treatment. Every uplift model must beat it.
- **Tuning.** We pick one set of LightGBM settings per outcome by 3 fold cross validation on training rows, then every model uses it. Training rows only.
- **Scores file.** `results/scores_5m.parquet` has one row per holdout user with `treatment`, `visit`, `conversion` and a column `{model}_{outcome}` for `response, s, t, x`. Evaluation only reads it.

Read the S and T learner sections of Künzel et al. (2019) before you start. The link is in the reading list in `README.md`.

---

## S1. Set up and first run

**Task.** Get the project running on your laptop and prove it.

**Steps.**
1. Clone the repo and check out the branch `analysis-pipeline`.
2. Create a Python 3.12 environment: `python3.12 -m venv .venv`, then `source .venv/bin/activate`.
3. Install: `pip install -r requirements.txt`, then `pip install -e .`.
4. Prepare the data. If `python -m uplift.data` exists in your branch, run it. If not, follow `data/README.md`.
5. Run `pytest`.
6. Start `jupyter lab` from the activated environment and run notebook 02 top to bottom.
7. Post one comment on the pull request with your operating system, Python version and how long each step took.

**Expectations.** Start Jupyter only from the activated environment. If a step fails, write down the exact error.

**Acceptance criteria.**
- [ ] `pytest` passes with 10 tests
- [ ] Notebook 02 runs top to bottom without an error
- [ ] The PR comment lists operating system, Python version and run times
- [ ] Any broken instruction is fixed in `README.md` through a pull request

---

## S2. Review the S and T learners and the pipeline

**Task.** Review `src/uplift/learners.py` (the `SLearner` and `TLearner` classes) and `src/uplift/pipeline.py` in the pipeline pull request.

**Steps.** Read each function, then check every item below and write what you found.
1. `SLearner.fit` adds the treatment column to the features and fits one model.
2. `SLearner.predict_uplift` predicts twice, once with `treatment=1` and once with `treatment=0`, and subtracts. The order is treated minus not treated.
3. `TLearner.fit` fits `mu1_` only on treated rows and `mu0_` only on control rows.
4. `TLearner.predict_uplift` is `mu1_` minus `mu0_`.
5. `select_features` only sees training rows and takes the lowest importance features.
6. `tune_base` only sees training rows and uses a validation split inside them.
7. `fit_and_score` fits the response baseline without the treatment column.
8. `build_scores` takes train and test ids as separate arguments and never mixes them.
9. Every model receives the same tuned settings.
10. Nothing reads the holdout before scoring.

**Expectations.**
- At least five comments on specific lines, each saying what you checked and whether it is right.
- One summary comment: items 1 to 10, each marked correct or questioned.
- If you are unsure about something, ask a question. A good question is a valid review comment.

**Acceptance criteria.**
- [ ] At least 5 line comments plus 1 summary comment on the PR
- [ ] The summary covers all 10 items
- [ ] Every question you raised has an answer in the PR

---

## S3. Tests for the pipeline

**Task.** Write `tests/test_pipeline.py` so the feature cut, the tuning and the scores file contract cannot silently break.

**Shared setup.** Build a synthetic frame of 20,000 rows in a fixture:
- columns `f0` to `f11` drawn from a normal distribution
- the outcome probability depends strongly on `f0` to `f9` (for example, a logistic function of a weighted sum with weights between 1 and 3) and not at all on `f10` and `f11`
- `treatment` random with 85 percent ones, and `visit` and `conversion` built from the same signal
- fast model settings: `n_estimators=30, learning_rate=0.1, num_leaves=7, min_child_samples=50`

**Tests required.**
1. **Feature cut.** `select_features(train, FEATURES, n_keep=10, n_rows=20_000)` returns 10 features, and the two it drops are `f10` and `f11`. The log has one row per dropped feature.
2. **Tuning.** With a grid of 2 settings, `tune_base(train, kept, "visit", grid=grid, n_rows=5_000, folds=2)` returns a setting that is one of the two in the grid, and the table has 2 rows with a `cv_logloss` column.
3. **Scores contract.** `build_scores(df, train_ids, test_ids, kept, {"visit": fast, "conversion": fast})` returns a frame with exactly the columns `treatment, visit, conversion` followed by one column for each of `response, s, t, x` and each outcome (`response_visit`, `s_visit`, and so on, 8 score columns). It has one row per test id, no missing values, score columns of type float32, and its index name is `row_id`.
4. **Response ignores treatment.** Fit twice with the training treatment column randomly flipped the second time. The `response_visit` column must be identical both times. The `s_visit` column must differ.

**Expectations.**
- Each test has a name that states what it checks.
- The whole file runs in under 60 seconds.
- Use a fixed seed so the tests never flake.

**Acceptance criteria.**
- [ ] `pytest tests/test_pipeline.py` passes
- [ ] All four tests exist
- [ ] **Break it on purpose once:** change `select_features` so it drops the highest importance features instead, and confirm test 1 fails. Undo it and mention this in the PR.
- [ ] `pytest` on the whole repo still passes

**Pull request.** Branch `sai/test_pipeline`. Commit message: `Add tests for the feature cut, tuning and scores contract`.

---

## S4. Tuning sensitivity check (notebook 06)

**Task.** Show whether our conclusion depends on tuning. Create `notebooks/06_sensitivity.ipynb`.

**Inputs.** `data/criteo.parquet`, `results/kept_features.json`, `results/best_params.json`, `uplift.learners.TLearner`, `uplift.metrics`.

**Steps.**
1. Load the data. Call `make_splits(len(df))`. Build `dev = take(df, pool_ids[:1_000_000])` and `hold = take(df, test_ids)`.
2. Load the kept features and `best_params["visit"]`.
3. Fit two T learners on `dev` for visits: `TLearner(best_params["visit"])` (tuned) and `TLearner()` (untuned, library defaults in `BASE_PARAMS`).
4. Score `hold` with each.
5. Call `bootstrap_metrics(y, t, {"tuned": ..., "untuned": ...}, n_boot=200)` once, so both use the same resamples.
6. Report the Qini coefficient of each with its 95 percent interval, and the paired difference tuned minus untuned with its interval (`paired_difference`).
7. Write one sentence at the end: does tuning matter for the Qini coefficient?

**Output.** `results/sensitivity_tuning_visit.csv`, columns `setting, qini_coef, ci_lo, ci_hi`, three rows: `tuned`, `untuned`, `difference`.

**Expectations.**
- Same seeds and same features as the rest of the project.
- State the result honestly even if tuning makes no difference.

**Acceptance criteria.**
- [ ] The notebook runs top to bottom in under 10 minutes
- [ ] The CSV exists with the exact columns and 3 rows
- [ ] The closing sentence matches the numbers
- [ ] Ganesh has reviewed and approved the pull request

**Pull request.** Branch `sai/tuning_sensitivity`. Commit message: `Add tuning sensitivity check`.

---

## S5. Draft Literature review

**Task.** Write the Literature review in at most 110 words, in plain Markdown.

**File.** `report/sections/literature_review.md`.

**Read first.** The abstract and introduction of each paper in the reading list in `README.md`. Only claim what a paper says.

**Structure.** Six sentences. Use numbered citations like [1]. The numbers must match your bibliography (task S7).
1. Targeting by predicted response can miss whom an offer changes (Ascarza, 2018).
2. Uplift modelling estimates the effect of an offer for each person from randomized data (Gutierrez and Gérardy, 2017).
3. Radcliffe (2007) introduced the Qini curve, which we use to evaluate targeting.
4. Künzel et al. (2019) defined the S, T and X learners that we compare.
5. Diemert et al. (2018) released the Criteo data as a benchmark for uplift modelling.
6. What we add: a direct comparison of response targeting with the three learners on the full data, a fixed holdout, and a data size curve.

**Expectations.**
- Every claim traceable to a paper in the list.
- Plain words. No dashes. Write ranges as "from 2007 to 2019".

**Acceptance criteria.**
- [ ] 110 words or fewer
- [ ] All six sentences present and each citation supported by its paper
- [ ] Citation numbers match `report/references.md`
- [ ] Niranjan has reviewed and approved the pull request

**Pull request.** Branch `sai/literature_review`. Commit message: `Draft Literature review`.

---

## S6. Draft Ethics and legal

**Task.** Write the Ethics and legal section in at most 70 words.

**File.** `report/sections/ethics_and_legal.md`.

**Inputs.** `data/README.md` and the sleeping dogs result in `results/sleeping_dogs_5m.csv` (Neeraj delivers it on Wed 18).

**Structure.** Four short parts, one sentence each, in this order.
1. **Privacy.** The data is anonymized and contains no personal information.
2. **Licence.** CC BY NC SA 4.0: we use the data for coursework only, with attribution to Criteo.
3. **Bias and fairness.** The features are anonymized, so we cannot test whether any group is treated unfairly. This is a limitation.
4. **Deployment.** An intervention can push some users away. In our results, `[the sleeping dogs finding]`. Any real use needs human review.

**Expectations.** No claim beyond what `data/README.md` and the sleeping dogs file support. A source comment after each fact.

**Acceptance criteria.**
- [ ] 70 words or fewer
- [ ] All four parts present
- [ ] The sleeping dogs sentence matches the CSV
- [ ] Ganesh has reviewed and approved the pull request

**Pull request.** Branch `sai/ethics_and_legal`. Commit message: `Draft Ethics and legal section`.

---

## S7. Bibliography

**Task.** Build `report/references.md`, numbered, in one consistent style.

**Steps.**
1. Start from this list. For each, open the link and complete the full author list and venue from the page. Do not guess.
   - Künzel et al. (2019), Metalearners for Estimating Heterogeneous Treatment Effects Using Machine Learning, PNAS: https://www.pnas.org/doi/10.1073/pnas.1804597116
   - Radcliffe (2007), Using Control Groups to Target on Predicted Lift: Building and Assessing Uplift Models, Direct Marketing Analytics Journal: https://www.research.ed.ac.uk/en/publications/using-control-groups-to-target-on-predicted-lift-building-and-ass/
   - Diemert et al. (2018), A Large Scale Benchmark for Uplift Modeling, AdKDD: http://papers.adkdd.org/2018/papers/adkdd18-diemert-large-scale.pdf
   - Gutierrez and Gérardy (2017), Causal Inference and Uplift Modelling: A Review of the Literature, PMLR: https://proceedings.mlr.press/v67/gutierrez17a.html
   - Ascarza (2018), Retention Futility: Targeting High Risk Customers Might Be Ineffective, Journal of Marketing Research: https://www.hbs.edu/ris/download.aspx?name=ascarza_jmr_18.pdf
   - Criteo Uplift Prediction Dataset v2.1: https://ailab.criteo.com/criteo-uplift-prediction-dataset/
2. Number the entries in the order they are first cited in the report.
3. Keep only entries that some section actually cites.

**Expectations.** One style for every entry: authors, year, title, venue, link. Links must open.

**Acceptance criteria.**
- [ ] Every citation in `report/sections/` has an entry, and every entry is cited
- [ ] Author lists and venues checked against the linked pages
- [ ] Niranjan has reviewed and approved the pull request

**Pull request.** Branch `sai/references`. Commit message: `Add bibliography`.

---

## S8. Segment analysis (notebook 08)

**Task.** Show who benefits: does the real effect of the offer change across groups of users defined by a feature? Create `notebooks/08_segments.ipynb`.

**Inputs.** `data/criteo.parquet`, `results/feature_selection.csv` (importances), `results/kept_features.json`, `results/scores_5m.parquet` (column `s_visit`), `uplift.data`.

**Steps.**
1. Load the data and build `hold = take(df, test_ids)`. Load the 5M scores file. Both are indexed by `row_id`, so align them with `.loc`.
2. Pick the 3 kept features with the highest importance from `feature_selection.csv`. Do this in code, not by hand.
3. For each of the 3 features, cut the holdout users into 5 groups of about equal size with `pd.qcut(..., 5, duplicates="drop")`. Some features have many identical values, so fewer than 5 groups may form. Report how many did.
4. For each group compute, for visits: `n, n_treated, n_control, rate_treated, rate_control`, the observed uplift `rate_treated - rate_control`, its 95 percent interval (`± 1.96 * se`, with `se = sqrt(p1*(1-p1)/n1 + p0*(1-p0)/n0)`), and the average predicted uplift from `s_visit`.
5. Draw one panel per feature: groups on the x axis, observed uplift with its interval as error bars, the S learner's average prediction as a second line, and a dashed line at the overall average effect. Save it as `results/segment_uplift_visit.png`.
6. Write two sentences at the end: which feature shows the clearest change in uplift across groups, and does the S learner's prediction follow the observed pattern?

**Output.** `results/segment_uplift_visit.csv`, columns `feature, group, group_low, group_high, n, n_treated, n_control, rate_treated, rate_control, uplift, ci_lo, ci_hi, mean_pred_s`, plus the PNG.

**Expectations.**
- Every number in the closing sentences comes from the table through f strings.
- Plain axis labels, a title and a legend.

**Acceptance criteria.**
- [ ] The notebook runs top to bottom in under 10 minutes
- [ ] The CSV has the exact columns and 3 features
- [ ] The PNG exists and is legible at half size
- [ ] The closing sentences match the table
- [ ] Ganesh has reviewed and approved the pull request

**Be ready to explain.** Why we compare treated and control inside each group, and why the intervals matter.

**Pull request.** Branch `sai/segments`. Commit message: `Add segment analysis`.

---

## S9. Number check and proofreading

**Task.** On Mon 23 Nov, check every number in your three pieces (Literature review, Ethics and legal, bibliography entries). On Wed 25 Nov, proofread the final PDF.

**Steps.** For each number, find its source and write one line in a PR comment: the number, the file, the row and column. On Wed 25, read the full PDF aloud once, and note every typo, unclear sentence and broken link.

**Acceptance criteria.**
- [ ] A comment lists every number with its source and there are zero mismatches
- [ ] A list of PDF problems is posted on Wed 25 and every item is resolved or explained

---

## Reviews you owe

| Review | What to check | When |
|---|---|---|
| `metrics.py` in the pipeline PR | The Qini formula, the bootstrap and the test | Mon 16 |
| Ganesh's Problem and data | Facts match `data/README.md` and the results | Sat 21 |
| Neeraj's Abstract | Matches the Results section | Mon 23 |

A review needs at least three specific comments, or an explicit statement of what you checked and found correct.

## Oral assessment: questions you must answer well
1. How does the S learner turn one model into an uplift score, and what can go wrong with it?
2. How does the T learner differ, and why can it be noisy when the control group is small?
3. Why do all models share one tuned setting?
4. How was the tuning done, and why only on training rows?
5. Why does the response baseline ignore treatment?
6. What does the scores file contain, and why does evaluation only read it?
7. Did tuning change our conclusion? What does your sensitivity check show?
8. What does your segment analysis show about who benefits?

## Definition of done
- [ ] Every task above is merged and its acceptance criteria are ticked
- [ ] The code runs from a clean clone
- [ ] Every number in your report sections traces to a file in `results/`
- [ ] You can answer the eight questions without notes
