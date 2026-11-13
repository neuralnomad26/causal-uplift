# Project plan: execution to submission

CSC1181, Group 12. This is the master plan from Sat 14 Nov to submission on Thu 26 Nov. Each person also has a requirements document in `docs/tasks/`. Read this page first, then your own page.

## 1. What we submit

| Deliverable | Rule |
|---|---|
| Report | One PDF, two columns, at most 5 pages, 11 pt or larger, under 1,000 words. The bibliography, tables, figures and footnotes do not count. A link to this repo must be inside the report. |
| Code | This repo. It must run from a clean clone and match the report. |
| Oral assessment | In person, Week 13, from Mon 30 Nov. Every member answers questions on the whole project, not only their own part. |

Deadline: Fri 27 Nov, 11:59 PM. We submit on Thu 26 Nov. Only one person submits.

## 2. Where we are (Fri 13 Nov, night)

Done and tested:
- Data downloaded, checksummed and converted. A fixed 2M row holdout and nested training samples of 100k, 500k, 1M and 5M rows.
- Feature cut from 12 to 10 features. Response baseline built (AUC 0.947 on visits).
- S, T and X learners, Qini evaluation, paired bootstrap, uplift by decile, pipeline and 10 unit tests.
- Gate G1 passed: the average effect on visits is positive, and a quick T learner beats random targeting.

Running: the model fits at all four training sizes, the full evaluation and the policy simulation (notebooks 03 to 05).

Open: the code is not on GitHub yet, no report section is written, and the H1 verdict is not known.

## 3. Phases and gates

| Phase | Dates | Gate | Exit criteria |
|---|---|---|---|
| 1 Execution | Sat 14 to Tue 17 | G2, Sun 15 | The code PRs are merged. Two people have rerun the tests and one notebook on their own laptop. |
| | | G3, Tue 17 | The results PR is merged. Headline numbers, all figures and the H1 verdict are agreed in a call. |
| 2 Finalisation | Wed 18 to Thu 26 | G4, Fri 20 | Results freeze. Repo tagged `v1.0`. Every report section has a full draft. |
| | | G5, Thu 26 | PDF submitted once, with a working code link. |

After G4 nobody runs new experiments. We write, check and clean up. Anything unfinished goes into Future Work.

## 4. Day by day

| Day | Neeraj | Ganesh | Sai | Niranjan |
|---|---|---|---|---|
| Sat 14 | Open the pipeline PR and the results PR | Open the data PR. Start `tests/test_data.py` | Install, run `pytest` and notebook 02. Start the review | Install, run `pytest` and notebook 02. Start the review |
| Sun 15 | Answer review comments. Merge. **G2** | Align notebook 01. Finish tests | Finish `tests/test_pipeline.py` and the review | Finish `tests/test_xlearner.py` and the review |
| Mon 16 | Check the numbers. Draft Methods | Draft Problem and data | Tuning sensitivity. Draft Literature review | Sleeping dogs check. Report template ready |
| Tue 17 | Run the **G3** call. Agree the H1 verdict | Draft Results with the agreed numbers | Relative uplift table for Analysis | Bibliography. Word count script |
| Wed 18 | Draft Abstract outline | Finish Results | Draft Analysis and discussion | Draft Ethics and Conclusion |
| Thu 19 | Methods final. Check all numbers against `results/` | Review Methods | Review Ethics and Conclusion | Merge all drafts into the template |
| Fri 20 | Tag `v1.0`. **G4** freeze | Check every number in his sections | Check every number in her sections | Check every number in his sections |
| Sat 21 | Write the Abstract | Read the whole report | Trim to the word limit | Assemble the two column PDF |
| Sun 22 | Edit | Clean the repo and README | Check references and captions | Layout and page count |
| Mon 23 | Edit | Cold start test: clone, install, run | Cold start test | Fix layout |
| Tue 24 | Second full read of the report | Second full read | Second full read | Second full read |
| Wed 25 | Contribution and Roles table. Link test in a private window | Proofread | Proofread | Final PDF checks |
| Thu 26 | Submit once. **G5** | Confirm receipt | Confirm receipt | Confirm receipt |
| Fri 27 | Spare day. Do not plan work. | | | |
| Sat 28 and Sun 29 | Mock oral assessments, five random questions each | | | |

## 5. Who owns what

| Area | Owner | Also reviewed by |
|---|---|---|
| Data, split, EDA, baseline (`data.py`, notebooks 01 and 02) | Ganesh | Niranjan |
| S and T learners, tuning, pipeline (`learners.py`, `pipeline.py`, notebook 03) | Sai | Ganesh |
| X learner, policy simulation (notebook 05) | Niranjan | Sai |
| Evaluation, bootstrap, H1 test (`metrics.py`, notebook 04) | Neeraj | Sai |

Owning an area means you can explain every line of it, defend its design, and fix a bug in it.

## 6. The report

| Section | Words | Author | Reviewer | Draft due | Source files |
|---|---|---|---|---|---|
| Abstract | 70 | Neeraj | Sai | Sat 21 | all results |
| Problem and data | 130 | Ganesh | Sai | Mon 16 | `balance_table_1m.csv`, `data/README.md` |
| Literature review | 110 | Sai | Niranjan | Mon 16 | the reading list |
| Methods | 220 | Neeraj | Ganesh | Mon 16 | `kept_features.json`, `best_params.json`, `docs/decision_log.md` |
| Results | 130 | Ganesh | Niranjan | Wed 18 | `qini_results_*_5m.csv`, `h1_tests_5m.csv` |
| Analysis and discussion | 130 | Sai | Neeraj | Wed 18 | `uplift_by_decile_5m.csv`, `seed_stability_visit.csv`, `size_curve.csv` |
| Ethics and legal | 70 | Niranjan | Neeraj | Wed 18 | `data/README.md` |
| Conclusion and future work | 70 | Niranjan | Neeraj | Wed 18 | `h1_tests_5m.csv` |
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
