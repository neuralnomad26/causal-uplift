# Requirements: Neeraj

**Role:** project lead and technical owner. You carry the complex work: the evaluation code and its verification, the two statistical analyses (sleeping dogs and relative uplift), the H1 verdict, and the three hardest report sections (Methods, Analysis and discussion, Abstract). You also run the plan, merge the code, freeze the results, and submit.

Read `docs/PLAN.md` first. Every task below has the same parts:
- **Task:** what to do.
- **Steps:** the order to do it in.
- **Expectations:** the quality bar.
- **Acceptance criteria:** a checklist your reviewer will tick. A task is done only when every box is ticked.

## Your tasks at a glance

| ID | Task | Due | Time | Branch | Reviewer |
|---|---|---|---|---|---|
| R1 | Open the pull requests and prepare the data command | Sat 14 | 1 h | `analysis-pipeline` and others | the team |
| R2 | Review teammates' pull requests | all week | 4 h | PR comments | none |
| R3 | Merge the code and pass Gate G2 | Tue 17 | 1 h | none | none |
| R4 | Hand worked tests for the evaluation code | Sun 15 to Mon 16 | 3 h | `neeraj/test_metrics_toy` | Sai |
| R5 | Audit and verify the results | Mon 16 | 3 h | `neeraj/audit` | Niranjan |
| R6 | Sleeping dogs check | Wed 18 | 3 h | `neeraj/sleeping_dogs` | Ganesh |
| R7 | Relative uplift analysis | Thu 19 | 3 h | `neeraj/relative_uplift` | Sai |
| R8 | Run the Gate G3 call and decide H1 | Tue 17 | 2 h | decision log | the team |
| R9 | Methods section | Draft Fri 20, final Sat 21 | 3 h | `neeraj/methods` | Ganesh |
| R10 | Analysis and discussion section | Sat 21 to Sun 22 | 3 h | `neeraj/analysis_section` | Niranjan |
| R11 | Freeze and tag `v1.0` | Fri 20 | 1 h | tag | none |
| R12 | Abstract | Sun 22 | 1 h | `neeraj/abstract` | Sai |
| R13 | Contribution and Roles table | Tue 24 and Wed 25 | 1 h | in the report | the team |
| R14 | Submission | Thu 26 | 2 h | none | the team |
| R15 | Keep the plan alive | daily | 15 min | none | none |

---

## R1. Open the pull requests and prepare the data command

**Task.** Get the work in front of the team, through pull requests only.

**Steps.**
1. Add a one command data preparation: `python -m uplift.data` downloads the file, checks the checksum and converts it to parquet. Put it in `data.py` with a short note in `data/README.md`.
2. Open these pull requests into `main`, each with a plain description (what changed, how to run it, who reviews what):
   - `analysis-pipeline`: code, tests, executed notebooks 02 to 05, results, README (contains Ganesh's Stage 1 commit)
   - `docs_team_plan`: this plan and the requirements pages
3. Request reviewers as in the review matrix in `docs/PLAN.md`.

**Expectations.** No direct push to `main`. No commit message or description carries any signature or footer.

**Acceptance criteria.**
- [ ] `python -m uplift.data` works from a clean clone
- [ ] Both pull requests are open and reviewers are assigned
- [ ] Every description says how to run the change

---

## R2. Review teammates' pull requests

**Task.** Approve or request changes on every teammate pull request within 12 hours.

**Steps.** For each PR: pull the branch, run `pytest`, run the notebook it adds or changes, read the diff, and check it against the acceptance criteria in its task. Leave at least three specific comments, or say plainly what you checked and found correct. Approve only when every acceptance box is ticked.

**Acceptance criteria.**
- [ ] No teammate PR waits more than 12 hours for a first review
- [ ] Every approval states what you ran

---

## R3. Merge the code and pass Gate G2

**Task.** Merge the code pull requests and close Gate G2 on the morning of Tue 17, before the G3 call.

**Gate G2 is passed when all of this is true:**
- [ ] The pipeline PR and the docs PR are merged
- [ ] Two people other than you have run `pytest` and notebook 02 on their own laptops, and said so in a PR comment
- [ ] The decision log has a row for G2

---

## R4. Hand worked tests for the evaluation code

**Task.** Prove the Qini code is right in two independent ways, so you can defend it in the oral. Create `tests/test_metrics_toy.py`.

**Part A. A toy example worked by hand.** Write 8 users on paper with treatment flag, outcome and score, for example:

| user | score | treatment | outcome |
|---|---|---|---|
| 1 | 0.9 | 1 | 1 |
| 2 | 0.8 | 0 | 0 |
| 3 | 0.7 | 1 | 1 |
| 4 | 0.6 | 0 | 1 |
| 5 | 0.5 | 1 | 0 |
| 6 | 0.4 | 0 | 0 |
| 7 | 0.3 | 1 | 1 |
| 8 | 0.2 | 0 | 0 |

Work out `Q(i) = i * (rate_treated - rate_control)` for the top i users, for i = 1 to 8, then the Qini curve, the area and the Qini coefficient. Write the working in the docstring of the test. Assert that `metrics.qini_curve`, `metrics.auuc` and `metrics.qini_coefficient` return those exact numbers. Add a second hand worked case with two groups for `metrics.uplift_by_decile` (`bins=2`).

**Part B. A slow but obvious implementation.** In the test file, write a plain Python function that computes `Q(i)` with loops and no vectorization. Generate 3,000 random users, and assert that it equals the vectorized `qini_coefficient` to within 1e-9.

**Expectations.** The working in the docstring must be readable by a teammate who did not write the code.

**Acceptance criteria.**
- [ ] `pytest tests/test_metrics_toy.py` passes
- [ ] Part A covers the curve, the area and the coefficient with numbers worked on paper
- [ ] Part B passes on 3 different random seeds
- [ ] You can reproduce Part A on a whiteboard without notes

**Pull request.** Branch `neeraj/test_metrics_toy`. Commit message: `Add hand worked tests for the evaluation code`.

---

## R5. Audit and verify the results

**Task.** Before the team writes numbers into the report, prove the results are right. Create `notebooks/10_audit.ipynb` and `results/audit.md`.

**Checks.** Each check prints PASS or FAIL.
1. **No leakage.** For every training size in `TRAIN_SIZES`, the training ids `pool_ids[:n]` share no id with `test_ids`.
2. **Treated share.** The share of treated users in the holdout and in each training sample is within 1 percentage point of 85 percent.
3. **Curve end equals the average effect.** For every model and outcome, the last point of `qini_curve` equals the observed average effect (treated rate minus control rate) to within 1e-6.
4. **Intervals contain the estimates.** For every row of `qini_results_*_5m.csv`, `ci_lo <= qini_coef <= ci_hi`.
5. **Bounded by the oracle.** The Qini coefficient of no model exceeds the planted effect oracle in `results/sanity_planted_effect.csv` by more than noise (compare only within the planted test).
6. **Bootstrap stability.** Rerun the H1 test in notebook 04 with a different bootstrap seed (for example 7). The verdicts must not change. If a verdict flips, the result is fragile and the report must say so.
7. **Seed spread.** Read `results/seed_stability_visit.csv`. The spread in Qini coefficient across seeds must be smaller than the gain you claim. If not, do not claim it.
8. **Scores file is reproducible.** Fit the T learner again at 100k rows and confirm the Qini coefficient matches `results/scores_100k.parquet` to within 0.0001.

**Output.** `results/audit.md`: a table with the check, the result and a one line comment.

**Expectations.** A FAIL is not hidden. If a check fails, find out why before any number is quoted.

**Acceptance criteria.**
- [ ] All 8 checks run and are recorded
- [ ] Any failure is explained and fixed, or the claim it affects is dropped
- [ ] `results/audit.md` is committed
- [ ] Niranjan has reviewed and approved the pull request

**Pull request.** Branch `neeraj/audit`. Commit message: `Add audit of the results`.

---

## R6. Sleeping dogs check

**Task.** A sleeping dog is a user the offer pushes away: their real uplift is negative. Check whether our models find any. This feeds the Ethics section and the Analysis. Add a section to `notebooks/05_policy_simulation.ipynb`.

**Inputs.** `results/scores_5m.parquet`: columns `treatment`, `visit`, `conversion`, `s_visit`, `t_visit`, `x_visit` and the conversion equivalents.

**Steps.**
1. For each learner (`s`, `t`, `x`) and each outcome, take the holdout users whose predicted uplift is below zero. Report the share of all users in that group and its size.
2. For that group, and for the rest, compute the observed uplift (treated rate minus control rate), its standard error `sqrt(p1*(1-p1)/n1 + p0*(1-p0)/n0)` and the 95 percent interval.
3. Do the same for the bottom 10 percent of users by predicted uplift.
4. Add the response baseline as a reference using its lowest 10 percent.
5. Write two sentences at the end: does the data show real harm in the predicted negative group (interval entirely below zero), or only noise? Be exact.

**Output.** `results/sleeping_dogs_5m.csv`, columns `outcome, model, group, share_of_users, n, uplift, ci_lo, ci_hi`.

**Expectations.** A group with an interval that includes zero is not evidence of harm. Say so.

**Acceptance criteria.**
- [ ] The CSV has the exact columns and a row for each outcome, model and group
- [ ] The conclusion matches the intervals
- [ ] The notebook still runs top to bottom
- [ ] Ganesh has reviewed and approved the pull request

**Pull request.** Branch `neeraj/sleeping_dogs`. Commit message: `Add sleeping dogs check`.

---

## R7. Relative uplift analysis

**Task.** Test a specific explanation: if users who respond more also gain more, in proportion, then ranking by response ranks by uplift almost as well, and the response baseline is hard to beat. Add a section to `notebooks/04_evaluation.ipynb`.

**Inputs.** `results/scores_5m.parquet`, columns `treatment`, `visit`, `response_visit`.

**Steps.**
1. Sort holdout users by `response_visit` and cut into 10 groups of equal size.
2. For each group compute the control outcome rate, the treated outcome rate, the observed uplift, and the relative uplift: `uplift / control_rate`. Add 95 percent intervals for the uplift (standard error as in R6).
3. Compute the rank correlation between `response_visit` and the S learner score `s_visit` across all users.
4. Draw two panels: observed uplift by group, and relative uplift by group, both with intervals.
5. Write two sentences: is relative uplift roughly flat across groups, and what does that mean for H1?

**Output.** `results/relative_uplift_response_deciles.csv`, columns `decile, n, control_rate, treated_rate, uplift, ci_lo, ci_hi, relative_uplift`; the rank correlation printed in the notebook and in `results/relative_uplift_rank_correlation.csv` (columns `pair, spearman`); and `results/relative_uplift.png`.

**Expectations.** If relative uplift is not flat, say so and do not use this explanation.

**Acceptance criteria.**
- [ ] The CSV has 10 rows and the exact columns
- [ ] The figure shows both panels with intervals
- [ ] The two closing sentences match the table
- [ ] Sai has reviewed and approved the pull request

**Pull request.** Branch `neeraj/relative_uplift`. Commit message: `Add relative uplift analysis`.

---

## R8. Run the Gate G3 call and decide H1

**Task.** On Tue 17, lead a 30 minute call that ends with decisions written in `docs/decision_log.md`.

**Prepare before the call.** Everyone has read `results/h1_tests_5m.csv`, the audit and the analyses.

**Agenda.**
1. **H1 verdict.** For each outcome, how many of the three learners beat the response baseline with an interval above zero and a Bonferroni corrected p value under 0.05? Write one sentence per outcome. Current numbers to confirm: on visits the S learner passes the main test and T and X do not; on conversion none passes. At a 10 percent budget all three learners gain over the baseline in `policy_simulation_5m.csv` (about 7 to 11 extra visits per 1,000 contacted, intervals above zero), but those budget by budget intervals are not corrected for multiple comparisons, so agree the exact wording.
2. **Primary outcome.** Confirm visits is primary and conversion secondary.
3. **Headline numbers.** The exact figures that go into Results, and who copies them.
4. **Figures.** At most four for the report. Default: Qini curves, uplift by decile, data size curve, policy simulation.
5. **Allowed claims.** The strongest claim the evidence supports, written in one sentence. No stronger claim goes in the report.
6. **If H1 is only partly supported.** Agree that the report says so plainly, and the Analysis explains why.

**Acceptance criteria.**
- [ ] Six decision log rows exist, one per agenda item
- [ ] Every member has said they agree, or their objection is recorded
- [ ] The verdict sentences are posted in the group chat for Ganesh and Niranjan to copy

---

## R9. Methods section

**Task.** Write the Methods section in at most 220 words.

**File.** `report/sections/methods.md`. Draft on Fri 20, final on Sat 21.

**Structure.** Eight sentences or short groups, in this order. Every number has an HTML comment naming its source file.
1. **Data split.** A fixed 2,000,000 user holdout, nested training samples from 100,000 to 5,000,000, none of it used for fitting, tuning or feature selection.
2. **Features.** 12 reduced to 10 by importance in a response model, on training rows only.
3. **Baseline.** A LightGBM response model on visits that ignores treatment.
4. **Learners.** S, T and X learners, using LightGBM with one setting chosen by 3 fold cross validation on training rows, shared by all models.
5. **Evaluation.** The Qini coefficient: the area between the Qini curve and the random line, with the curve built from outcome rates.
6. **Test.** A paired bootstrap with 200 resamples comparing each learner with the baseline, one sided, with a Bonferroni correction over 3 comparisons.
7. **Further analyses.** Uplift by decile, a data size curve, a policy simulation at fixed budgets, and a planted effect test of the evaluation code.
8. **Reproducibility.** Fixed seeds and the repository link.

**Expectations.** A reader who knows machine learning but not uplift must follow it. Define the Qini coefficient in one clause.

**Acceptance criteria.**
- [ ] 220 words or fewer
- [ ] Every item above is present
- [ ] Every statement is true for the code (Ganesh checks this)
- [ ] Ganesh has reviewed and approved the pull request

**Pull request.** Branch `neeraj/methods`. Commit message: `Draft Methods section`.

---

## R10. Analysis and discussion section

**Task.** Explain why the results look the way they do, in at most 130 words. This is the hardest section. Draft it on Sat 21 and Sun 22, after the extra analyses are merged and the numbers are frozen on Fri 20.

**File.** `report/sections/analysis.md`.

**Evidence you may use.** Only evidence in `results/`, with a source comment after each number:
- Uplift learners beat the baseline on visits only by a small margin, and the S learner reliably (`h1_tests_5m.csv`)
- The gain is concentrated at the smallest budget: top 10 percent (`qini_results_visit_5m.csv`)
- Conversion: the baseline is as good or better, and the T learner is worse (`h1_tests_5m.csv`)
- The data size curve (`size_curve.csv`): the S learner is above the baseline from 100k rows, the T learner needs about 1M rows to catch up, and the X learner needs about 5M. Confirm each with its interval before writing it
- Seed stability (`seed_stability_visit.csv`): the T learner's Qini coefficient moves by about 10 percent between seeds, while the baseline barely moves. Say so when you discuss T
- Relative uplift across response groups (R7)
- Sleeping dogs (R6)
- Calibration (Niranjan), baseline variants (Ganesh), tuning sensitivity (Sai), segments (Sai)
- The planted effect test shows the code finds a real effect when one exists (`sanity_planted_effect.csv`)

**Structure.** Five or six sentences.
1. The headline pattern in one sentence.
2. The most likely explanation, tied to R7.
3. Where the learners do help (small budgets) and where they do not.
4. Why conversion differs (rare events, `size_curve.csv`).
5. One caution from calibration or sleeping dogs.
6. What the planted effect test tells us about whether a null result is due to the code.

**Expectations.** Claims as strong as the intervals allow and no stronger. No causal story that the evidence does not support. If the evidence is mixed, say so.

**Acceptance criteria.**
- [ ] 130 words or fewer
- [ ] Every claim has a source comment pointing at a file
- [ ] No sentence contradicts the decision log
- [ ] Niranjan has reviewed and approved the pull request

**Pull request.** Branch `neeraj/analysis_section`. Commit message: `Draft Analysis and discussion section`.

---

## R11. Freeze and tag `v1.0`

**Task.** On Fri 20, lock the results.

**Steps.**
1. Confirm every notebook on `main` is executed and its outputs match the tables in `results/`.
2. Update the result map in `README.md` if any file name changed.
3. Check that no report section contains a number that is not in a file.
4. Create the tag `v1.0` and push it on its own.
5. Post in the group chat: results are frozen.

**Acceptance criteria.**
- [ ] The tag exists on GitHub and points at the merged `main`
- [ ] The group chat message is posted
- [ ] From now on, no number changes. Late ideas go into Future Work.

---

## R12. Abstract

**Task.** Write the Abstract in at most 70 words, on Sun 22, after the freeze.

**File.** `report/sections/abstract.md`.

**Structure.** Five sentences: the question, the data, the method, the H1 verdict with the key number, the main caveat. Check each against the Results section.

**Acceptance criteria.**
- [ ] 70 words or fewer
- [ ] The key number matches `results/h1_tests_5m.csv`
- [ ] Sai has reviewed and approved the pull request

**Pull request.** Branch `neeraj/abstract`. Commit message: `Draft Abstract`.

---

## R13. Contribution and Roles table

**Task.** Collect what each person did, in their own words, honestly.

**Steps.** Tue 24: send a short template to each member, with their own row pre filled from their requirements page. Each person edits their row and confirms it. Wed 25: send the final table to Niranjan for the PDF.

**Acceptance criteria.**
- [ ] Every row is confirmed by the person it describes
- [ ] The table matches the work history in the repository

---

## R14. Submission

**Task.** Submit once, on Thu 26 Nov.

**Steps.**
1. Confirm the module's rules on academic integrity and on assistance are met, including any disclosure requirement.
2. Open the PDF link inside the report in a private browser window with no login. It must open.
3. Check the PDF against the final checklist in `docs/PLAN.md`.
4. Submit once. Save the receipt in the group chat.
5. The other three confirm they see the same receipt.

**Acceptance criteria.**
- [ ] One submission, with the receipt posted
- [ ] All four confirm
- [ ] The code link works for a person with no login

---

## R15. Keep the plan alive

**Task.** Run the five checkpoint meetings (Sun 15, Tue 17, Thu 19, Mon 23, Wed 25), one hour each, and keep the days between them light.

**Steps.** At each meeting, each person says what is done, what is next and what is blocked, and says whether another deadline means a task should move. Write blockers and decisions in `docs/decision_log.md` that evening. A blocked person is helped the same day by the reviewer of their area. On other days, ask for a group chat update only when something changed.

**Acceptance criteria.**
- [ ] All five checkpoint meetings happen, each with decisions written down
- [ ] Every blocker has an owner and a time

---

## Reviews you owe

| Review | When |
|---|---|
| Ganesh: tests, notebook 01, Problem and data, Results, baseline variants | Mon 16, Tue 17, Thu 19, Fri 20, Sat 21 |
| Sai: pipeline tests, Ethics, segments | Wed 18, Fri 20, Sun 22 |
| Niranjan: X learner tests, template, calibration, Conclusion | Tue 17, Thu 19, Fri 20, Sat 21 |
| Niranjan: the final PDF | Mon 23 and Wed 25 |

## Oral assessment: questions you must answer well
1. What does a Qini curve show, and how do you read it?
2. Derive the Qini coefficient for a small example on paper.
3. Why is the curve built from rates and not counts?
4. How does the paired bootstrap work, and why pair the resamples?
5. Why a Bonferroni correction, and what does it cost?
6. What does the H1 test conclude, and how sure are we?
7. Why might the response baseline be hard to beat on this data?
8. What would make you distrust the result, and what did the audit check?

## Definition of done
- [ ] Every task above is merged and its acceptance criteria are ticked
- [ ] The submission is made once and confirmed by all four
- [ ] Every number in your sections traces to a file in `results/`
- [ ] You can answer the eight questions without notes
