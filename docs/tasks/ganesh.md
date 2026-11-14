# Requirements: Ganesh

**Role:** data and results owner. You own the data code and the data tests, you keep notebook 01 correct, and you write two report sections: Problem and data, and Results.

Read `docs/PLAN.md` first. Every task below has the same parts:
- **Task:** what to do.
- **Steps:** the order to do it in.
- **Expectations:** the quality bar.
- **Acceptance criteria:** a checklist your reviewer will tick. A task is done only when every box is ticked.

## Your tasks at a glance

| ID | Task | Due | Time | Branch | Reviewer |
|---|---|---|---|---|---|
| G1 | Set up and first run | Sat 14 | 1 to 2 h | none | Neeraj |
| G2 | Align notebook 01 with the final features | Sun 15 | 2 to 3 h | `ganesh/notebook01` | Niranjan |
| G3 | Tests for the data code | Sun 15 | 2 h | `ganesh/test_data` | Neeraj |
| G4 | Draft Problem and data | Mon 16 | 1.5 h | `ganesh/problem_and_data` | Sai |
| G5 | Draft Results | Wed 18 | 2 h | `ganesh/results_section` | Niranjan |
| G6 | Number check | Fri 20 | 1 h | PR comment | Sai |
| G7 | Cold start test and README check | Sun 22 and Mon 23 | 2 h | `ganesh/cold_start` | Neeraj |
| G8 | Baseline variants check (notebook 07) | Tue 17 | 3 h | `ganesh/baseline_variants` | Neeraj |
| G9 | Word count script | Mon 16 | 2 h | `ganesh/count_words` | Niranjan |

## What you need to understand first

- **Randomized experiment.** Criteo randomly decided who got the advertisement. So the treated group and the control group are alike on average, and a difference in outcomes between them is caused by the advertisement.
- **Treatment, visit, conversion.** `treatment` is 1 if a user was targeted. `visit` is 1 if the user visited the site. `conversion` is 1 if the user bought. Ignore the `exposure` column.
- **The file is ordered.** The first 5.57 million rows are all treated users. Taking the first rows gives no control group at all.
- **The fixed holdout.** We set aside 2,000,000 random users once, by seed. Nobody trains, tunes or selects features on them. They are only used to score models.
- **Nested samples.** Training samples of 100k, 500k, 1M and 5M users are the first n rows of one shuffled pool, so each contains the smaller one.

The functions you will use all live in `src/uplift/data.py`: `make_splits`, `take`, `treated_share_ok`, `verify_checksum`, `to_parquet`, `download`.

---

## G1. Set up and first run

**Task.** Get the project running on your laptop and prove it.

**Steps.**
1. Clone the repo and check out the branch `analysis-pipeline`.
2. Create a Python 3.12 environment: `python3.12 -m venv .venv`, then `source .venv/bin/activate`.
3. Install: `pip install -r requirements.txt`, then `pip install -e .`.
4. Download and convert the data. If `python -m uplift.data` exists in your branch, run it. If not, follow the two calls in `data/README.md`.
5. Run `pytest`.
6. Start `jupyter lab` from the activated environment and run notebook 02 from top to bottom.
7. Post one comment on the pull request with your operating system, Python version, and how long each step took.

**Expectations.**
- Start Jupyter only from the activated environment. Otherwise Jupyter may pick another Python and fail with `No module named 'uplift'`.
- If any step fails, do not work around it silently. Write down the exact error.

**Acceptance criteria.**
- [ ] `pytest` passes with 10 tests
- [ ] Notebook 02 runs top to bottom without an error
- [ ] The comment on the PR lists operating system, Python version and run times
- [ ] Any broken instruction is fixed in `README.md` through a pull request

---

## G2. Align notebook 01 with the final features

**Task.** Notebook 01 currently keeps the first 10 features by position (`f0` to `f9`). The project keeps the 10 features in `results/kept_features.json`. Update the notebook so the balance check and the average effect use the right features and the right rows.

**Inputs.**
- `data/criteo.parquet`
- `results/kept_features.json` (the kept feature list)
- `uplift.data`: `make_splits`, `take`

**Steps.**
1. Load the parquet file and call `make_splits(len(df))` to get `test_ids` and `pool_ids`.
2. Build the development sample: `dev = take(df, pool_ids[:1_000_000])`. Build the holdout: `hold = take(df, test_ids)`.
3. Read the kept list with `json.load`. Do not type the list by hand.
4. For each kept feature compute the standardized mean difference between treated and control on `dev`:
   `smd = (mean_treated - mean_control) / sqrt((var_treated + var_control) / 2)`
5. Build a table with columns `feature, mean_treated, mean_control, SMD, abs_SMD`, sorted by `abs_SMD` from largest to smallest. Save it to `results/balance_table_1m.csv`, overwriting the old file.
6. Draw a horizontal bar chart of `abs_SMD` per feature with a vertical dashed line at 0.1. Save it to `results/balance_smd_1m.png`, overwriting the old file.
7. For each of the two samples (`dev`, `hold`) and each outcome (`visit`, `conversion`) compute:
   - the outcome rate in the treated group and in the control group,
   - the average treatment effect `ate = rate_treated - rate_control`,
   - the standard error `se = sqrt(p1*(1-p1)/n1 + p0*(1-p0)/n0)`,
   - the 95 percent interval `ate ± 1.96 * se`.
   Save one row per combination to `results/ate_visit_conversion.csv`.
8. Add a markdown cell that states whether the largest `abs_SMD` is below 0.1 and what that means in one sentence. Use f strings, so the text can never disagree with the table.

**Output files.**
- `results/balance_table_1m.csv` with columns `feature, mean_treated, mean_control, SMD, abs_SMD`, 10 rows
- `results/balance_smd_1m.png`
- `results/ate_visit_conversion.csv` with columns `sample, outcome, n_treated, n_control, rate_treated, rate_control, ate, ci_lo, ci_hi`, 4 rows

**Expectations.**
- No number typed by hand in any markdown cell.
- Plot labels in plain English, axis labels and a title.
- The notebook runs in under 3 minutes.

**Acceptance criteria.**
- [ ] The notebook runs top to bottom from a fresh kernel
- [ ] The balance table has exactly the 10 features in `kept_features.json`
- [ ] The three output files exist with the exact names and columns above
- [ ] The average effect for visits on the holdout is close to 0.0100 (it should match the value in notebook 02)
- [ ] The markdown conclusion about the 0.1 threshold is correct for your table
- [ ] The old line `KEEP_FEATURES = FEATURES[:10]` is gone

**Common mistakes.** Using the whole 14M file instead of the development sample. Typing the feature list by hand. Forgetting to commit the regenerated PNG.

**Be ready to explain.** What a standardized mean difference measures. Why randomization means the groups should be balanced. What the average effect tells us.

**Pull request.** Branch `ganesh/notebook01`. Commit message: `Align notebook 01 with the final features`.

---

## G3. Tests for the data code

**Task.** Write `tests/test_data.py` so the split can never silently break.

**Setup that every test shares.** Build a small frame so tests run in seconds:
- 10,000 rows, columns `f0` to `f11` (random numbers), `treatment`, `visit`, `conversion`, `exposure`.
- Call `make_splits(10_000, holdout=2_000, seed=42)`.

**Tests required.**
1. **No overlap and full coverage.** The holdout and the pool share no row. Joined together they contain every number from 0 to 9,999 exactly once.
2. **Holdout size.** `len(test_ids)` equals 2,000.
3. **Nested samples.** For sizes 100, 500 and 1,000, the sample `pool[:n]` is contained in the next larger one, and none of them contains a holdout row.
4. **Deterministic.** The same seed returns identical arrays. A different seed returns different arrays.
5. **Ordered file trap.** Build a frame where the first 5,000 rows are treated and the rest are mixed. `treated_share_ok` must return False for `df.head(1000)` and True for a random sample of 1,000 rows.
6. **Row ids kept.** `take(df, ids).index.name` equals `"row_id"` and its index equals `ids`.
7. **Checksum.** Write a small file to `tmp_path`, compute its SHA256 with `hashlib`, and check `verify_checksum` returns True. Change one byte and check it returns False.

**Expectations.**
- One test per behaviour, each named for what it checks, for example `test_holdout_and_pool_do_not_overlap`.
- Use `pytest` fixtures for the shared frame.
- The whole file runs in under 10 seconds.

**Acceptance criteria.**
- [ ] `pytest tests/test_data.py` passes
- [ ] All seven tests above exist
- [ ] **Break it on purpose once:** change `make_splits` temporarily so the holdout has one extra row, and confirm at least one test fails. Undo the change. Mention this in the PR.
- [ ] `pytest` on the whole repo still passes

**Be ready to explain.** Why the ordered file trap matters. Why the same seed must always give the same split.

**Pull request.** Branch `ganesh/test_data`. Commit message: `Add tests for the holdout split and sampling`.

---

## G4. Draft Problem and data

**Task.** Write the Problem and data section in at most 130 words.

**File.** `report/sections/problem_and_data.md`, plain Markdown, no title line.

**Inputs.** `results/balance_table_1m.csv` (after G2), `results/ate_visit_conversion.csv`, `data/README.md`.

**Structure.** Six sentences, in this order. Replace every bracket with a number from the named file.
1. **Question.** Who actually benefits from an offer, not who is likely to respond, and why that matters for a limited budget.
2. **Dataset.** Criteo Uplift v2.1, 13,979,592 users from a randomized advertising experiment, 85 percent treated and 15 percent control, 12 anonymized features, two outcomes.
3. **Randomization.** The largest standardized difference is `[max abs_SMD from balance_table_1m.csv]`, below the 0.1 threshold.
4. **Split.** A fixed holdout of 2,000,000 users is never used for fitting, tuning or feature selection. Training samples from 100,000 to 5,000,000 users are nested.
5. **Features.** We keep 10 of 12 features, dropping the two least important.
6. **Ordering.** The file is ordered by treatment, so we always sample at random with a fixed seed.

**Expectations.**
- Plain words, no jargon without a short explanation.
- After every number, add an HTML comment naming its source, for example `13,979,592 <!-- source: data/README.md -->`.
- No dashes anywhere. Write ranges as "100,000 to 5,000,000".

**Acceptance criteria.**
- [ ] 130 words or fewer when counted by `report/count_words.py` (or by hand if the script is not ready)
- [ ] All six sentences are present
- [ ] Every number has a source comment and matches that file exactly
- [ ] Sai has reviewed it and approved the pull request

**Be ready to explain.** Every sentence. A marker may ask why we hold out 2M rows.

**Pull request.** Branch `ganesh/problem_and_data`. Commit message: `Draft Problem and data section`.

---

## G5. Draft Results

**Task.** Write the Results section in at most 130 words, after Gate G3 on Tue 17.

**File.** `report/sections/results.md`.

**Inputs.** Only these files, and only the numbers agreed at the G3 call:
- `results/qini_results_visit_5m.csv` and `results/qini_results_conversion_5m.csv`: one row per model, columns `qini_coef, ci_lo, ci_hi, auuc, extra_per_1000_at_10pct, extra_per_1000_at_20pct, extra_per_1000_at_30pct`
- `results/h1_tests_5m.csv`: columns `outcome, model, diff_vs_response, ci_lo, ci_hi, p_one_sided, p_bonferroni`

**Structure.** Results states facts. It does not explain them. The explaining belongs to Analysis and discussion.
1. **Verdict.** One sentence for each outcome, copied from the decision log entry written at G3.
2. **Visits.** The Qini coefficient of the response baseline and of each learner, each with its 95 percent interval.
3. **Tests.** The gain of each learner over the baseline, its interval and its corrected p value.
4. **Fixed budget.** Extra visits per 1,000 users contacted when targeting the top 10 percent, for the baseline and each learner.
5. **Conversion.** The same facts, in one or two sentences.
6. **Figures.** Name the figures by file: `report/qini_curves.png` and `report/policy_simulation.png`.

**Expectations.**
- Round Qini coefficients to 5 decimals and extra visits to 1 decimal.
- A source comment after every number, naming the file.
- No interpretation, no words like "because" or "which suggests".

**Acceptance criteria.**
- [ ] 130 words or fewer
- [ ] Every number matches its CSV after rounding
- [ ] The verdict sentences are identical to the decision log
- [ ] Niranjan has reviewed it and approved the pull request

**Pull request.** Branch `ganesh/results_section`. Commit message: `Draft Results section`.

---

## G6. Number check

**Task.** On Fri 20 Nov, prove that every number in your two sections is right.

**Steps.** Open both sections. For each number, find it in its source file and write one line in a PR comment: the number, the file, the row and column. Fix anything that does not match.

**Acceptance criteria.**
- [ ] A comment lists every number with its source
- [ ] There are zero mismatches left
- [ ] Sai has confirmed the list

---

## G7. Cold start test and README check

**Task.** Prove that a stranger could run the project.

**Steps.**
1. In a new empty folder, clone the repo, create a fresh environment from `requirements.txt`, run `pip install -e .`.
2. Prepare the data, run `pytest`, then run notebooks 01 and 02.
3. Read `README.md` as a marker would. Note every sentence that is wrong, unclear or out of date.
4. Fix what you found through a pull request.

**Acceptance criteria.**
- [ ] A clean clone installs and runs `pytest` with no manual steps beyond the README
- [ ] The PR description lists operating system, Python version and run times
- [ ] Every README problem you found is fixed or listed

**Pull request.** Branch `ganesh/cold_start`. Commit message: `Fix problems found in the cold start test`.

---

## G8. Baseline variants check (notebook 07)

**Task.** A reader will ask: is the response baseline a fair benchmark? Show whether our conclusion changes if we build the baseline differently. Create `notebooks/07_baseline_variants.ipynb`.

**Inputs.** `data/criteo.parquet`, `results/kept_features.json`, `results/best_params.json`, `results/scores_1m.parquet` (the 1M training run, with column `s_visit` for the S learner), and `uplift.metrics`.

**Steps.**
1. Load the data and build `dev = take(df, pool_ids[:1_000_000])` and `hold = take(df, test_ids)` exactly as in notebook 03. Load the kept features and the tuned parameters for visits (`best_params["visit"]`).
2. Fit three baseline variants for the outcome `visit` on `dev`:
   - **A. All rows, treatment ignored.** `LGBMClassifier` with the tuned parameters on all development rows. This is our baseline.
   - **B. Treated rows only.** The same model fitted only on rows with `treatment == 1`. It predicts visit probability given the offer.
   - **C. Logistic regression.** A scikit-learn pipeline with `StandardScaler` and `LogisticRegression` on all development rows.
3. Score the holdout rows with each variant (probability of visit).
4. Read the S learner scores from `scores_1m.parquet` and align them to `hold` by row id (both are indexed by `row_id`).
5. Call `bootstrap_metrics(y, t, scores, n_boot=200)` once with all four score sets, so every comparison uses the same resamples.
6. For each variant, report the Qini coefficient and its 95 percent interval, and the paired difference "S learner minus this variant" with its interval and one sided p value, using `paired_difference`.
7. Write two sentences at the end of the notebook: does the S learner still beat every baseline variant, and does any variant beat our baseline A?

**Output.** `results/baseline_variants_visit.csv` with columns `variant, qini_coef, ci_lo, ci_hi, s_minus_variant, diff_lo, diff_hi, p_one_sided` and 3 rows.

**Expectations.**
- Sanity check in a cell: the Qini coefficient of variant A matches the response row of `results/qini_results_visit_5m.csv` only approximately (different training size), but it must match `response_visit` in `scores_1m.parquet` to within 0.0001. If not, find the bug before going on.
- Use the same random seeds as the rest of the project.
- State plainly if a variant is better than A. A surprising result is fine. A hidden one is not.

**Acceptance criteria.**
- [ ] The notebook runs top to bottom in under 10 minutes
- [ ] `results/baseline_variants_visit.csv` exists with the exact columns and 3 rows
- [ ] The sanity check cell for variant A passes
- [ ] The two closing sentences are correct for your table
- [ ] Neeraj has reviewed and approved the pull request

**Be ready to explain.** What each variant predicts. Why the treated only model is a reasonable alternative.

**Pull request.** Branch `ganesh/baseline_variants`. Commit message: `Add baseline variants check`.

---

## G9. Word count script

**Task.** The report has a hard limit of 1,000 words, and the budget is 930. Write a script that counts words the way the module counts them, so nobody has to guess.

**File.** `report/count_words.py`, and `tests/test_count_words.py`.

**Behaviour required.**
1. Run from the repo root: `python report/count_words.py`. It reads every `report/sections/*.md` file except `references.md`.
2. For each file it removes, before counting:
   - HTML comments, including ones that run over several lines
   - Markdown tables (lines that start with `|`)
   - image lines (`![caption](path)`)
   - link addresses, keeping the link text: `[text](url)` becomes `text`
   Heading words and body words are counted. Heading marks (`#`) are not words.
3. A word is a run of characters between spaces that contains at least one letter or digit.
4. It prints a table with the columns `section, words, budget, status`, then a total line. The budgets are in a dictionary in the script and match `docs/PLAN.md`: abstract 70, problem_and_data 130, literature_review 110, methods 220, results 130, analysis 130, ethics_and_legal 70, conclusion 70.
5. Status is `OK` if the words are within budget and `OVER` if not. A missing file shows `MISSING`.
6. Exit code 0 if no section is over budget and the total is 1,000 or fewer. Exit code 1 otherwise.

**Tests required (`tests/test_count_words.py`).** Use temporary files and call the counting function directly:
- a plain sentence of 5 words counts 5
- an HTML comment adds 0, including a multi line comment
- a table adds 0
- an image line adds 0
- `[three words here](https://x.y)` counts 3
- a heading `## Two words` counts 2
- an over budget section returns exit code 1

**Expectations.** Keep the counting in one function that takes text and returns a number, so it can be tested. Plain Python, standard library only.

**Acceptance criteria.**
- [ ] `python report/count_words.py` runs and prints the table, even when some sections are missing
- [ ] All seven tests pass
- [ ] An over budget file makes the exit code 1 (show it in the PR)
- [ ] Niranjan has reviewed and approved the pull request

**Pull request.** Branch `ganesh/count_words`. Commit message: `Add report word count script and tests`.

---

## Reviews you owe

| Review | What to check | When |
|---|---|---|
| The `data.py` split code in the pipeline PR | No holdout row reaches training. The seed makes it repeatable. | Sun 15 |
| Neeraj's Methods section | Every sentence is true for the code. | Thu 19 |
| Sai's Ethics and legal section | Facts match `data/README.md`. | Thu 19 |

A review needs at least three specific comments, or an explicit statement of what you checked and found correct.

## Oral assessment: questions you must answer well
1. Why is the file ordered, and what goes wrong if we use its first rows?
2. Why hold out 2,000,000 users, and why are the training samples nested?
3. What does a standardized mean difference measure, and what does your table show?
4. How did we choose the 10 features, and what did dropping 2 cost?
5. What is the average treatment effect on visits and on conversion, and how sure are we?
6. Why do we develop on visits when the business outcome is conversion?
7. What does the response baseline predict, and why is it the right benchmark?
8. How do we know no test row was used for fitting, tuning or feature selection?

## Definition of done
- [ ] Every task above is merged and its acceptance criteria are ticked
- [ ] The code runs from a clean clone
- [ ] Every number in your report sections traces to a file in `results/`
- [ ] You can answer the eight questions without notes
