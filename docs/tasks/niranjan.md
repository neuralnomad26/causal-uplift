# Requirements: Niranjan

**Role:** X learner and report owner. You own the tests for the X learner, a calibration analysis (notebook 09), the Conclusion section, and the whole report build: the template, merging the drafts, assembling the final two column PDF and checking it.

Read `docs/PLAN.md` first. Every task below has the same parts:
- **Task:** what to do.
- **Steps:** the order to do it in.
- **Expectations:** the quality bar.
- **Acceptance criteria:** a checklist your reviewer will tick. A task is done only when every box is ticked.

## Your tasks at a glance

| ID | Task | Due | Time | Branch | Reviewer |
|---|---|---|---|---|---|
| N1 | Set up and first run | Sat 14 | 1 to 2 h | none | Neeraj |
| N2 | Review the X learner and the evaluation code | Mon 16 | 2 h | PR comments | Sai |
| N3 | Tests for the X learner | Tue 17 | 2 h | `niranjan/test_xlearner` | Neeraj |
| N4 | Report template | Wed 18 to Fri 20 | 4 h | `niranjan/report_template` | Neeraj |
| N5 | Calibration analysis (notebook 09) | Wed 18 to Thu 19 | 3 h | `niranjan/calibration` | Neeraj |
| N6 | Draft Conclusion and future work | Sat 21 | 1.5 h | `niranjan/conclusion` | Neeraj |
| N7 | Merge the drafts and check numbers | Sat 21 and Sun 22 | 2 h | `niranjan/merge_drafts` | Neeraj |
| N8 | Assemble the two column PDF | Sun 22 to Tue 24 | 5 h | `niranjan/final_pdf` | Sai |
| N9 | Final PDF checks | Wed 25 | 2 h | PR comments | Ganesh |

## What you need to understand first

- **X learner, in three stages.**
  1. Fit two outcome models as in the T learner: `mu1_` on treated users and `mu0_` on control users.
  2. For every treated user, the imputed effect is their real outcome minus what `mu0_` predicts for them. For every control user, it is what `mu1_` predicts minus their real outcome. Fit one regressor on each set of imputed effects: `tau1_` on treated users, `tau0_` on control users.
  3. Blend: `tau(x) = g * tau0(x) + (1 - g) * tau1(x)`, where `g` is the share of treated users, about 0.85. The control based effect model `tau0_` gets the larger weight because it relies on `mu1_`, which was learned from the large treated group.
- **Uplift by decile.** Sort users by predicted uplift, cut into 10 equal groups, and measure the real treated minus control outcome rate in each. A good model shows high real uplift in group 1 and falling uplift after.
- **Calibration.** Predicted uplift is calibrated if, in each group, the average predicted uplift is close to the real observed uplift.

Read the X learner section of Künzel et al. (2019) before you start. The link is in the reading list in `README.md`.

---

## N1. Set up and first run

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

## N2. Review the X learner and the evaluation code

**Task.** Review the `XLearner` class in `src/uplift/learners.py` and the whole of `src/uplift/metrics.py` in the pipeline pull request.

**Steps.** Check every item and write what you found.
1. `XLearner.fit` fits `mu1_` on treated rows only and `mu0_` on control rows only.
2. The imputed effect for treated users is `y - mu0_(x)`. For control users it is `mu1_(x) - y`. The signs are right.
3. `tau1_` is fitted on treated rows with the treated imputed effects. `tau0_` is fitted on control rows with the control imputed effects.
4. `g_` is the share of treated users.
5. `predict_uplift` is `g_ * tau0_.predict(X) + (1 - g_) * tau1_.predict(X)`.
6. In `metrics.py`, the Qini curve is built from outcome rates, so the 85 and 15 split does not distort it.
7. `qini_coefficient` is the area between the curve and the random line.
8. `bootstrap_metrics` draws one set of row indices per resample and scores every model on those rows.
9. `paired_difference` returns a one sided p value, and notebook 04 multiplies it by 3 (Bonferroni).
10. `uplift_by_decile` sorts by score from highest to lowest and returns the standard error of each group.

**Expectations.**
- At least five comments on specific lines, each saying what you checked and whether it is right.
- One summary comment: items 1 to 10, each marked correct or questioned.
- A good question is a valid review comment.

**Acceptance criteria.**
- [ ] At least 5 line comments plus 1 summary comment on the PR
- [ ] The summary covers all 10 items
- [ ] Every question you raised has an answer in the PR

---

## N3. Tests for the X learner

**Task.** Write `tests/test_xlearner.py` so the X learner's three stages cannot silently break.

**Shared setup.** Use the `planted` fixture in `tests/conftest.py`. It gives `X, t, y, tau` where the true effect `tau` is 0.10 for users with `x0 > 0` and 0 for the others. Use the fast settings `dict(n_estimators=60, learning_rate=0.1, num_leaves=15, min_child_samples=200)` and fit on the first half of the rows.

**Tests required.**
1. **Weight.** After fitting, `model.g_` equals the share of treated rows in the training half (use `pytest.approx`).
2. **Blend.** `model.predict_uplift(X_test)` equals `g * model.tau0_.predict(X_test) + (1 - g) * model.tau1_.predict(X_test)` computed from the fitted parts (`np.allclose`).
3. **Weight follows the data.** Build two training sets from the fixture by sampling so that 50 percent and 90 percent of rows are treated. The fitted `g_` is about 0.5 and about 0.9.
4. **Finds the planted effect.** The scores on the second half correlate with the true `tau` above 0.3, and the Qini coefficient (`uplift.metrics.qini_coefficient`) is above 0.004.
5. **Output shape.** One finite score per test row, no NaN.

**Expectations.**
- Test names state the behaviour, for example `test_blend_uses_the_treated_share`.
- Fixed seeds. The file runs in under 60 seconds.

**Acceptance criteria.**
- [ ] `pytest tests/test_xlearner.py` passes
- [ ] All five tests exist
- [ ] **Break it on purpose once:** swap `tau0_` and `tau1_` in `predict_uplift`, confirm a test fails, undo it, and say so in the PR
- [ ] `pytest` on the whole repo still passes

**Pull request.** Branch `niranjan/test_xlearner`. Commit message: `Add tests for the X learner`.

---

## N4. Report template

**Task.** Build the template that all eight sections drop into, so assembling the report is quick.

**Where.** A folder `report/template/` with the source file and the built PDF.

**Requirements.**
1. A4 page, two columns, body text 11 pt or larger, margins at least 2 cm.
2. Sections in this order, with these exact headings: Abstract, Problem and data, Literature review, Methods, Results, Analysis and discussion, Ethics and legal, Conclusion and future work, References.
3. A title block with the project title "Who Actually Benefits? Causal Machine Learning for Targeted Intervention", course CSC1181, Group 12.
4. A line with the code link: `https://github.com/neuralnomad26/causal-uplift` (we will confirm the final link on Wed 25).
5. Room for four figures with captions: Qini curves, uplift by decile, data size curve, policy simulation. The images are already in `report/` as `qini_curves.png`, `uplift_by_decile.png`, `size_curve.png`, `policy_simulation.png`.
6. A table "Contribution and Roles" with one row per member and columns name, what they did.
7. A numbered reference list.
8. Source files kept in the repo so anyone can rebuild the PDF. LaTeX (for example on Overleaf) or Word are both fine, but the rule is: if you delete the PDF, we can rebuild it from the repo.

**Test the template.** Fill it with 930 words of dummy text and the four figures and the table. It must fit in 5 pages or fewer. If it does not fit, change figure sizes and spacing now, not on Sat 21.

**Expectations.**
- Figures readable on a phone at full page width. Axis labels at least 8 pt after scaling.
- Plain, professional layout. No decoration.

**Acceptance criteria.**
- [ ] A PDF built from the source: two columns, A4, 11 pt body
- [ ] The nine headings are present and in the order above
- [ ] The dummy filled version is 5 pages or fewer
- [ ] The Contribution and Roles table, the code link and the reference list are in place
- [ ] The repo has the source and the PDF, and Neeraj has approved the pull request

**Pull request.** Branch `niranjan/report_template`. Commit message: `Add two column report template`.

---

## N5. Calibration analysis (notebook 09)

**Task.** Check whether the predicted uplift scores are calibrated: does the predicted uplift in each group match the real one? Create `notebooks/09_calibration.ipynb`.

**Inputs.** `results/scores_5m.parquet` (columns `treatment`, `visit`, `conversion`, and `s_visit`, `t_visit`, `x_visit`, `s_conversion`, `t_conversion`, `x_conversion`) and `uplift.metrics.uplift_by_decile`.

**Steps.**
1. Load the scores file.
2. For each outcome (`visit`, `conversion`) and each learner (`s`, `t`, `x`), call `uplift_by_decile(y, t, score, bins=10)`. The result has the columns `decile, n, n_treated, n_control, rate_treated, rate_control, uplift, se, mean_score`. Here `mean_score` is the average predicted uplift and `uplift` is the observed uplift.
3. Do not include the response baseline: its scores are probabilities, not uplifts.
4. For each outcome and learner, fit a straight line of observed on predicted across the 10 groups with `np.polyfit(mean_score, uplift, 1)`. The slope is the calibration slope. A slope near 1 means the predictions are well scaled. Below 1 means the model exaggerates differences between groups. Also compute the rank correlation between the decile number and the observed uplift (`scipy.stats.spearmanr`).
5. Draw one panel per learner for visits: predicted uplift on the x axis, observed uplift on the y axis with 95 percent interval error bars (`± 1.96 * se`), and the diagonal where predicted equals observed. Save `results/calibration_5m.png`.
6. Write two sentences at the end: which learner is best calibrated, and does any learner exaggerate or understate the differences?

**Output.**
- `results/calibration_5m.csv`, columns `outcome, model, decile, mean_pred, observed, se, ci_lo, ci_hi`, 60 rows
- `results/calibration_slopes_5m.csv`, columns `outcome, model, slope, spearman`, 6 rows
- `results/calibration_5m.png`

**Expectations.**
- Every number in the closing sentences comes from the tables through f strings.
- State honestly if the slope is far from 1. A poor calibration is a finding, not a failure.

**Acceptance criteria.**
- [ ] The notebook runs top to bottom in under 5 minutes
- [ ] The two CSV files have the exact columns and row counts
- [ ] The PNG exists with labelled axes and a legend
- [ ] The closing sentences match the tables
- [ ] Neeraj has reviewed and approved the pull request

**Be ready to explain.** What calibration means, and what a slope below 1 tells us.

**Pull request.** Branch `niranjan/calibration`. Commit message: `Add calibration analysis`.

---

## N6. Draft Conclusion and future work

**Task.** Write the Conclusion and future work in at most 70 words.

**File.** `report/sections/conclusion.md`.

**Inputs.** The H1 verdict agreed at the G3 call (decision log), `results/h1_tests_5m.csv`.

**Structure.** Four sentences.
1. **Verdict.** The H1 verdict in one sentence, copied from the decision log.
2. **Lesson.** The main lesson in one sentence, such as when the learners help and when they do not.
3. **Limits.** One sentence naming the main limits: one dataset, anonymized features, no cost model, rare conversions.
4. **Future work.** One sentence with two ideas, for example explaining which features drive the effect, and a cost aware policy.

**Expectations.** No claim stronger than the decision log allows. A source comment after every number. No dashes.

**Acceptance criteria.**
- [ ] 70 words or fewer
- [ ] All four sentences present
- [ ] The verdict sentence is identical to the decision log
- [ ] Neeraj has reviewed and approved the pull request

**Pull request.** Branch `niranjan/conclusion`. Commit message: `Draft Conclusion and future work`.

---

## N7. Merge the drafts and check numbers

**Task.** Put the eight drafts together and check them.

**Steps.**
1. Sat 21 and Sun 22: as each section is ready, copy it from `report/sections/` into the template. Run `python report/count_words.py` (Ganesh builds it).
2. If any section is over budget or the total is over 1,000, post the list in the group chat and ask the authors to cut. Do not cut other people's text yourself.
3. Sun 22: check every number in your Conclusion and in the calibration results against its file.

**Acceptance criteria.**
- [ ] All eight sections are in the template
- [ ] The word count script exits with 0
- [ ] A PR comment lists every number in your section with its source, and there are zero mismatches

**Pull request.** Branch `niranjan/merge_drafts`. Commit message: `Merge section drafts into the template`.

---

## N8. Assemble the two column PDF

**Task.** Produce the final PDF from the template and the sections, Sun 22 to Tue 24.

**Steps.**
1. Place all final sections and the four figures. Write a caption for each figure that says what it shows and how to read it.
2. Refer to every figure in the text.
3. Fill the Contribution and Roles table with the text Neeraj collects.
4. Make sure the code link is clickable and correct.
5. Build the PDF. Check the page count (5 or fewer), the font size (11 pt or larger), two columns throughout, and that every figure is readable.
6. Fix layout problems yourself. If a content change is needed, send it to the section author.

**Acceptance criteria.**
- [ ] PDF is 5 pages or fewer, two columns, A4, body 11 pt or larger
- [ ] The word count script exits with 0
- [ ] No placeholder text such as `TODO`, `[...]` or `lorem`
- [ ] Figures are referenced and captioned
- [ ] The PDF is built from sources in the repo
- [ ] Sai has reviewed and approved the pull request

**Pull request.** Branch `niranjan/final_pdf`. Commit message: `Assemble the final report PDF`.

---

## N9. Final PDF checks

**Task.** Wed 25 Nov. Check the final PDF as the marker will see it.

**Checklist.** Tick every line in a PR comment.
- [ ] Open on a phone and on a laptop. Both readable
- [ ] 5 pages or fewer
- [ ] Two columns on every page
- [ ] Fonts embedded, body 11 pt or larger
- [ ] The code link opens in a private browser window with no login
- [ ] Reference links open
- [ ] The word count script exits with 0
- [ ] Contribution and Roles table present and agreed
- [ ] No placeholder text and no tool or draft marks
- [ ] File name is `CSC1181_Group12_Report.pdf`

---

## Reviews you owe

| Review | What to check | When |
|---|---|---|
| Ganesh's word count script | The counting rules in task G9 | Thu 19 |
| Sai's Literature review and bibliography | Citations match, claims match the papers | Sun 22 |
| Ganesh's Results section | Every number matches its file | Sun 22 |

A review needs at least three specific comments, or an explicit statement of what you checked and found correct.

## Oral assessment: questions you must answer well
1. What are the three stages of the X learner?
2. Why does the control based effect model get the larger weight in our data?
3. When is the X learner expected to beat the T learner, and did it here?
4. What does your calibration analysis show?
5. How does the policy simulation turn scores into extra outcomes per 100,000 users?
6. What are the three main limitations of our study?
7. How do you know the word count and page limit are met?
8. What does each figure in the report show, and how do you read it?

## Definition of done
- [ ] Every task above is merged and its acceptance criteria are ticked
- [ ] The final PDF passes the checklist in `docs/PLAN.md`
- [ ] Every number in your section traces to a file in `results/`
- [ ] You can answer the eight questions without notes
