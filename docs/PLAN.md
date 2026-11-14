# Project plan: execution to submission

CSC1181, Group 12. This is the master plan from Sat 14 Nov to submission on Thu 26 Nov. Each person also has a requirements document in `docs/tasks/`. Read this page first, then your own page.

## 1. What we submit

| Deliverable | Rule |
|---|---|
| Report | One PDF, two columns, at most 5 pages, 11 pt or larger, under 1,000 words. The bibliography, tables, figures and footnotes do not count. A link to this repo must be inside the report. |
| Code | This repo. It must run from a clean clone and match the report. |
| Oral assessment | In person, Week 13, from Mon 30 Nov. Every member answers questions on the whole project, not only their own part. |

Deadline: Fri 27 Nov, 11:59 PM. We submit on Thu 26 Nov. Only one person submits.

## 2. Where we are (Sat 14 Nov)

Done and tested:
- Data downloaded, checksummed and converted. A fixed 2M row holdout and nested training samples of 100k, 500k, 1M and 5M rows.
- Feature cut from 12 to 10 features. Response baseline built (AUC 0.947 on visits).
- S, T and X learners, Qini evaluation, paired bootstrap, uplift by decile, pipeline and 10 unit tests.
- Gate G1 passed: the average effect on visits is positive, and a quick T learner beats random targeting.
- All models fitted at four training sizes. Evaluation, planted effect test, seed stability, data size curve and policy simulation are run.

First results (to be confirmed at Gate G3):
- On visits, the S learner reliably beats the response baseline, but only by a small margin. The T and X learners lean the same way and do not clear the corrected test.
- At a 10 percent budget all three learners gain over the baseline. At 20 and 30 percent they do not.
- On conversion, the baseline is as good or better.
- The S learner beats the baseline from 100k training rows. The T learner needs about 1M and the X learner about 5M.

Open: the pull requests are not open yet, no report section is written, and the H1 verdict is not agreed.

## 3. Phases and gates

| Phase | Dates | Gate | Exit criteria |
|---|---|---|---|
| 1 Execution | Sat 14 to Tue 17 | G2, Sun 15 | The code PRs are merged. Two people have rerun the tests and one notebook on their own laptop. |
| | | G3, Tue 17 | The results PR is merged. Headline numbers, all figures and the H1 verdict are agreed in a call. |
| 2 Finalisation | Wed 18 to Thu 26 | G4, Fri 20 | Results freeze. Repo tagged `v1.0`. Every report section has a full draft. |
| | | G5, Thu 26 | PDF submitted once, with a working code link. |

After G4 nobody runs new experiments. We write, check and clean up. Anything unfinished goes into Future Work.

## 4. Day by day

Task IDs refer to each person's requirements page. Every person has work every day.

| Day | Neeraj | Ganesh | Sai | Niranjan |
|---|---|---|---|---|
| Sat 14 | R1 open the pull requests, data command | G1 set up and first run | S1 set up and first run | N1 set up and first run |
| Sun 15 | R3 merge, **G2**. R4 hand worked Qini tests | G2 notebook 01. G3 data tests | S2 review. S3 pipeline tests | N2 review. N3 X learner tests |
| Mon 16 | R5 audit. R6 sleeping dogs. R9 Methods draft | G4 Problem and data. G9 word count script | S4 tuning sensitivity. S5 Literature review | N4 report template |
| Tue 17 | R7 relative uplift. R8 **G3 call**, H1 verdict | G8 baseline variants | S7 bibliography. S8 segments | N5 calibration |
| Wed 18 | R10 Analysis and discussion | G5 Results | S6 Ethics and legal | N6 Conclusion |
| Thu 19 | R9 Methods final. Review Ethics and Conclusion | Review Methods and Ethics | Review Literature review check, proofread | N7 merge the drafts |
| Fri 20 | R11 freeze, tag `v1.0`, **G4** | G6 number check | S9 number check | N7 number check |
| Sat 21 | R12 Abstract | Read the whole report | Check references and captions | N8 assemble the PDF |
| Sun 22 | Edit | G7 cold start test | Check references and captions | N8 layout |
| Mon 23 | Edit | G7 fix what you found | Read the whole report | N8 finish the PDF |
| Tue 24 | R13 send the roles table. Second full read | Second full read | Second full read | Second full read |
| Wed 25 | R13 final. Link test in a private window | Proofread | S9 proofread the PDF | N9 final PDF checks |
| Thu 26 | R14 submit once, **G5** | Confirm the receipt | Confirm the receipt | Confirm the receipt |
| Fri 27 | Spare day. Do not plan work. | | | |
| Sat 28 and Sun 29 | Mock oral assessments, five random questions each | | | |

## 5. Who owns what

| Area | Owner | Reviewed by |
|---|---|---|
| Data, split, notebooks 01 and 02, data tests (`data.py`) | Ganesh | Niranjan |
| Baseline variants (notebook 07), word count script | Ganesh | Neeraj, Niranjan |
| S and T learners, tuning, pipeline tests (`learners.py`, `pipeline.py`) | Sai | Ganesh |
| Tuning sensitivity (notebook 06), segments (notebook 08), bibliography | Sai | Ganesh, Niranjan |
| X learner tests, calibration (notebook 09), report template and assembly | Niranjan | Sai, Neeraj |
| Evaluation, bootstrap, H1 test (`metrics.py`, notebook 04), audit (notebook 10), sleeping dogs, relative uplift | Neeraj | Sai, Niranjan |

Owning an area means you can explain every line of it, defend its design, and fix a bug in it.

## 6. The report

| Section | Words | Author | Reviewer | Draft due | Source files |
|---|---|---|---|---|---|
| Abstract | 70 | Neeraj | Sai | Sat 21 | all results |
| Problem and data | 130 | Ganesh | Sai | Mon 16 | `balance_table_1m.csv`, `ate_visit_conversion.csv`, `data/README.md` |
| Literature review | 110 | Sai | Niranjan | Mon 16 | the reading list |
| Methods | 220 | Neeraj | Ganesh | Mon 16, final Thu 19 | `kept_features.json`, `best_params.json`, `docs/decision_log.md` |
| Results | 130 | Ganesh | Niranjan | Wed 18 | `qini_results_*_5m.csv`, `h1_tests_5m.csv` |
| Analysis and discussion | 130 | Neeraj | Niranjan | Wed 18 | `size_curve.csv`, `relative_uplift_response_deciles.csv`, `sleeping_dogs_5m.csv`, `calibration_slopes_5m.csv` |
| Ethics and legal | 70 | Sai | Ganesh | Wed 18 | `data/README.md`, `sleeping_dogs_5m.csv` |
| Conclusion and future work | 70 | Niranjan | Neeraj | Wed 18 | `h1_tests_5m.csv`, the decision log |
| Total | 930 | | | | |

Each draft is a plain Markdown file in `report/sections/`, named after the section. Niranjan merges them into the two column template. Every number in a draft must be copied from a file in `results/` and carry a comment naming that file.

## 7. How we work

1. **Nothing goes to `main` directly.** Work on a branch named `yourname/task_name`, open a pull request, get one approval from the reviewer, then merge.
2. **Review matrix.** The reviewer for each task is in your requirements document. Review within 12 hours of the request. A review has at least three specific comments or an explicit statement of what you checked.
3. **Small pull requests.** One task per PR. Push every day by 9 PM, even if it is not finished, as a draft PR.
4. **Commit messages.** One short line in plain words that says what changed. No trailers and no signatures.
5. **No large files.** Never commit data files or scores files. Figures and CSV tables under `results/` are fine.
6. **Blocked?** Say so in the group chat the same day. Do not wait.
7. **Daily call.** 15 minutes each evening. Each person says what is done, what is next and what blocks them.
8. **Definition of done** for any task: the code runs from a clean clone, tests pass, outputs are in `results/` with the names in your document, the PR is approved and merged, and you can explain it.
9. **Decisions** go in `docs/decision_log.md`, one row each, with the reason.

## 8. Dependencies

| Task | Needs |
|---|---|
| Any teammate task | The pipeline PR is open and readable. Neeraj, Sat 14 |
| Results section | Gate G3 numbers |
| Analysis section | `uplift_by_decile_5m.csv`, `size_curve.csv` and the relative uplift table |
| Final PDF | All eight drafts merged in `report/sections/` |
| Tag `v1.0` | Gate G4 |

## 9. Risks and fallbacks

| Risk | Fallback |
|---|---|
| H1 is not supported: the response baseline matches the uplift learners | Report it honestly with the confidence interval. A well tested negative result is valid. The Analysis section explains why, using the decile and size curve results. |
| Conversion results are too noisy | Visits is the primary outcome. Report conversion as secondary with its wide intervals. |
| A teammate is unavailable for a day | The reviewer for that area takes over the task. Say so in the chat. |
| Code works on one laptop only | The cold start test on Sun 22 and Mon 23 catches it. Fix `requirements.txt`. |
| The report is over 1,000 words | Cut the Literature review first, then the Analysis, then Methods detail. Detail lives in the code. |
| A late change to a number | Not allowed after Fri 20. Put the idea in Future Work. |
| The code link fails | Test it in a private window on Wed 25 and again just before submitting. |

## 10. Final submission checklist

- [ ] PDF, two columns, 5 pages or fewer, 11 pt or larger
- [ ] Under 1,000 words, counted with the word count script
- [ ] The response baseline is in the report
- [ ] About 10 features, and the cut is explained
- [ ] A working link to the repo is inside the report
- [ ] Every number matches a file in `results/`
- [ ] Ethics and legal covers privacy, the licence, bias and deployment
- [ ] The Contribution and Roles table is agreed by all four
- [ ] A clean clone installs and runs the tests
- [ ] The module rules on academic integrity and assistance are met, including any disclosure requirement
- [ ] One person submits, and the other three confirm

## 11. Oral assessment

Everyone answers questions on the whole project. The eight questions every member must be able to answer are in the README and in the Oral section of each requirements document. After each gate, the owner of each area walks the other three through it for 10 minutes.
