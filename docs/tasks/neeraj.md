# Requirements: Neeraj

**Role:** project lead and evaluation owner. You run the plan and the daily call, you own the evaluation code and the H1 verdict, you write the Abstract and Methods, and you submit.

Read `docs/PLAN.md` first. This page tells you exactly what to deliver, what files to produce, and how we will check it.

## What you own

| Code and files | Where |
|---|---|
| Qini, AUUC, bootstrap, paired test, uplift by decile | `src/uplift/metrics.py` |
| Evaluation of every model from the scores files | `notebooks/04_evaluation.ipynb` |
| The plan, the decision log, the tag and the submission | `docs/`, the repo, the PDF |

You can explain every line of the evaluation code, derive the Qini coefficient on paper, and fix a bug in it.

## Deliverables

| ID | Task | Due | Reviewer |
|---|---|---|---|
| R1 | Open the pipeline pull request and the results pull request | Sat 14 | Sai, Niranjan, Ganesh |
| R2 | Review Ganesh's data pull request | Sat 14 | none |
| R3 | Merge the code pull requests. Gate G2 | Sun 15 | none |
| R4 | `tests/test_metrics_toy.py` with a hand worked example | Sun 15 | Sai |
| R5 | Check every number in the results. Draft Methods | Mon 16 | Ganesh |
| R6 | Run the Gate G3 call and decide the H1 verdict | Tue 17 | the group |
| R7 | Methods final | Thu 19 | Ganesh |
| R8 | Tag `v1.0`. Gate G4 freeze | Fri 20 | none |
| R9 | Draft Abstract (70 words) | Sat 21 | Sai |
| R10 | Contribution and Roles table | Tue 24 draft, Wed 25 agreed | the group |
| R11 | Submit. Gate G5 | Thu 26 | the group |

### R1. Open the pull requests
1. The pipeline PR contains the code and tests. Branch: `analysis-pipeline`.
2. The results PR contains the executed notebooks 02 to 05 and every table and figure in `results/` and `report/`.
3. In each description write what changed, how to run it, what you checked, and who should review which part. Use the review matrix in `docs/PLAN.md`.
4. Answer every review comment within 12 hours.

### R2. Review Ganesh's data PR
Check that nothing reads the holdout during fitting, tuning or feature selection, that checksum verification runs before conversion, and that the notebook runs from a clean clone. Leave specific comments.

### R3. Merge and Gate G2
G2 is passed when both code PRs are merged and two people other than you have run `pytest` and notebook 02 on their own laptop. Write the result in the decision log.

### R4. A hand worked Qini example
Create `tests/test_metrics_toy.py`. Write 8 users on paper (treatment flag, outcome, score), work out the Qini curve and the Qini coefficient by hand, and assert that the code returns exactly those numbers. Put the working in the docstring of the test. Do the same for `uplift_by_decile` with 2 groups. This is your oral assessment evidence.

### R5. Check the results and draft Methods
1. Open each CSV in `results/` and read it against the figures. Look for anything that looks wrong: a Qini coefficient above the oracle, intervals that do not contain the point estimate, identical columns.
2. Rerun notebook 04 once on a second seed of the bootstrap and confirm the conclusions do not change.
3. Draft Methods (220 words) in `report/sections/methods.md`. Cover, in order:
   - Data split: fixed 2M row holdout, nested training samples, never used for fitting, tuning or selection.
   - Features: 12 to 10, by importance on training rows.
   - Baseline: response model on visits, ignores treatment.
   - Learners: S, T and X with one shared tuned LightGBM setting from 3 fold cross validation.
   - Evaluation: Qini coefficient, paired bootstrap with 200 resamples, one sided test against the baseline with Bonferroni correction over 3 comparisons.
   - Policy simulation and the data size curve.
   - Reproducibility: fixed seeds, the repo link.
   Every number comes from a file in `results/`, with an HTML comment naming the file.

### R6. Gate G3 call, Tue 17
Agenda, 30 minutes:
1. **H1 verdict.** For each outcome, how many of the three learners beat the response baseline with a Bonferroni corrected p value under 0.05 and an interval above zero? Write the verdict in one sentence per outcome.
2. **Primary outcome.** Confirm visits is primary and conversion is secondary. Log it.
3. **Headline numbers.** Agree the exact figures that go in Results, and who copies them.
4. **Figures.** Choose at most four for the report. Default: Qini curves, uplift by decile, data size curve, policy simulation.
5. **Allowed claims.** Agree the strongest claim the evidence supports, and write it in the decision log. No claim stronger than that goes in the report.
6. **Bad news plan.** If H1 is not supported, agree that the report says so plainly and the Analysis explains why.

### R7. Methods final
Thu 19: update Methods with any change from the G3 call. Ganesh reviews. Keep to 220 words.

### R8. Freeze and tag, Fri 20
1. Confirm every notebook in `main` is executed and its outputs match the tables in `results/`.
2. Update the result map in `README.md` if any file name changed.
3. Create the tag: `git tag v1.0` then push the tag. The tag is pushed on its own, not as part of a branch.
4. Post in the group chat: results are frozen.

### R9. Draft Abstract (70 words)
Sat 21, after the freeze. File: `report/sections/abstract.md`. In order: the question, the data, the method, the H1 verdict with the key number, and the main caveat. Check it against the Results section.

### R10. Contribution and Roles table
Draft on Tue 24, agreed by all four on Wed 25. It lists what each person did, in their own words, honestly. Each person reads their own row and confirms it.

### R11. Submission, Thu 26
1. Confirm the module's rules on academic integrity and on assistance are met, including any disclosure requirement.
2. Make sure the code link inside the PDF opens for the marker. Test it in a private browser window with no login.
3. Check the PDF against the checklist in `docs/PLAN.md`.
4. Submit once. Save the receipt in the group chat.
5. The other three confirm they see the same receipt.

## Running the project

- **Daily call:** 15 minutes each evening. Each person says done, next, blocked.
- **Decisions:** one row in `docs/decision_log.md` per decision, with the reason.
- **Unblocking:** a blocked person is helped the same day by the reviewer of their area.
- **Direct pushes to `main` are not allowed.** Everything, including your own work, goes through a pull request with one approval.

## Reviews you owe

| Review | When |
|---|---|
| Ganesh's data pull request | Sat 14 |
| Niranjan's Ethics and Conclusion | Thu 19 |
| Sai's Analysis and discussion | Wed 18 |
| Niranjan's PDF | Sat 21 and Wed 25 |

## Oral assessment: questions you must answer well
1. What does a Qini curve show, and how do you read it?
2. Derive the Qini coefficient for a small example.
3. Why is the curve built from rates and not counts?
4. How does the paired bootstrap work, and why pair the resamples?
5. Why a Bonferroni correction, and what does it cost?
6. What does the H1 test conclude and how sure are we?
7. What would make you distrust the result?
8. What would you do differently with more time?

## Definition of done
- [ ] Every deliverable above is merged
- [ ] The code runs from a clean clone
- [ ] Every number in your report sections traces to a file in `results/`
- [ ] The submission is made once and confirmed by all four
- [ ] You can answer the eight questions without notes
