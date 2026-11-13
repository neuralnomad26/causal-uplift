# Requirements: Niranjan

**Role:** X learner and policy owner, and report assembly owner. You own the X learner and the policy simulation. You write the Ethics and legal and Conclusion sections, and you build the final PDF.

Read `docs/PLAN.md` first. This page tells you exactly what to build, what files to produce, and how we will check it.

## What you own

| Code and files | Where |
|---|---|
| X learner | `src/uplift/learners.py` (class `XLearner`) |
| Policy simulation | `notebooks/05_policy_simulation.ipynb` |
| Report template, word count script, bibliography, final PDF | `report/` |

You can explain every line of these, defend the design, and fix a bug in them.

## Background you need first
Read Künzel et al. (2019), the section on the X learner. In plain words, it has three stages:
1. Fit the two outcome models, as in the T learner: one on treated users, one on control users.
2. For every treated user, the imputed effect is their real outcome minus what the control model predicts for them. For every control user it is what the treated model predicts minus their real outcome. Fit one regressor on each set of imputed effects.
3. Blend the two effect models with weights from the share of treated users. Ours is 85 percent treated, so the model learned from the control group's imputed effects gets the larger weight.

## Deliverables

| ID | Task | Due | Reviewer |
|---|---|---|---|
| N1 | Install, run `pytest`, run notebook 02 | Sat 14 | Neeraj |
| N2 | Review of the X learner and of `metrics.py` | Sun 15 | Sai |
| N3 | `tests/test_xlearner.py` | Sun 15 | Neeraj |
| N4 | Sleeping dogs check in notebook 05 | Mon 16 | Sai |
| N5 | Report template and word count script | Mon 16 | Neeraj |
| N6 | Bibliography | Tue 17 | Sai |
| N7 | Draft Ethics and legal (70 words) and Conclusion (70 words) | Wed 18 | Neeraj |
| N8 | Merge all drafts into the template | Thu 19 | Neeraj |
| N9 | Number check of your sections | Fri 20 | Neeraj |
| N10 | Assemble and polish the two column PDF | Sat 21 to Mon 23 | Sai |
| N11 | Final PDF checks | Wed 25 | Ganesh |

### N1. Environment check
Clone the repo, create the environment from `requirements.txt`, run `pip install -e .`, then `pytest`, then notebook 02. Comment on the pipeline PR with your operating system, Python version and run times. Fix any broken instruction in `README.md` through a PR.

### N2. Review
Review the `XLearner` class and the evaluation code in `src/uplift/metrics.py` in the pipeline PR. Leave at least five specific comments. Check at least:
1. Stage 2 uses the other group's outcome model to impute effects, with the signs right for each group.
2. The final blend is `g * tau0 + (1 - g) * tau1` with `g` equal to the treated share.
3. In `metrics.py`, the Qini curve uses rates, so the 85 and 15 split does not distort it.
4. The bootstrap resamples rows once and scores every model on those rows.
5. The p value is one sided and corrected, and Bonferroni is applied in notebook 04.

### N3. Tests for the X learner
Create `tests/test_xlearner.py` with a synthetic frame (about 20,000 rows). Tests required:
1. After fitting, `g_` equals the share of treated rows.
2. `predict_uplift` equals `g_ * tau0_.predict(X) + (1 - g_) * tau1_.predict(X)` computed from the fitted parts.
3. With a treated share of 0.5 the two parts are weighted equally, and with 0.9 the control based part gets weight 0.9.
4. On a planted effect (see `tests/conftest.py`), the X learner's scores correlate with the true effect above 0.3.

### N4. Sleeping dogs check in notebook 05
A sleeping dog is a user the intervention pushes away. Check whether our models can find any. In `notebooks/05_policy_simulation.ipynb`, using the 5M scores file:
1. For the S, T and X learners and for both outcomes, take users whose predicted uplift is below zero. Report their share of all holdout users.
2. For that group, and for the rest, compute the observed uplift (treated outcome rate minus control outcome rate) with a 95 percent confidence interval. The standard error is the square root of `p1(1-p1)/n1 + p0(1-p0)/n0`.
3. Do the same for the bottom 10 percent by predicted uplift.
4. End with two sentences: does the data show real harm in the predicted negative group (interval entirely below zero), or only noise?

Output: `results/sleeping_dogs_5m.csv` with columns `outcome, model, group, share_of_users, n, uplift, ci_lo, ci_hi`.

### N5. Report template and word count script
In `report/`:
1. A two column A4 template with 11 pt or larger text. The source goes in the repo (LaTeX or a Word file), so anyone can rebuild the PDF. Sections in the order of the module guideline: Abstract, Problem and data, Literature review, Methods, Results, Analysis and discussion, Ethics and legal, Conclusion and future work, then the bibliography. Add the Contribution and Roles table and the code link.
2. Room for at most four figures: Qini curves, uplift by decile, data size curve, policy simulation. All four already exist in `report/*.png`.
3. `report/count_words.py`: reads `report/sections/*.md`, removes HTML comments, tables, image lines and the bibliography, prints the word count per section against the budget in `docs/PLAN.md`, prints the total, and exits with an error if the total is over 1,000.
Acceptance: the template builds a PDF of two columns, and the script runs on a sample.

### N6. Bibliography
File: `report/references.md`. One consistent style: authors, year, title, venue, link. Include every paper cited by any section, with numbers that match the citations. Sai sends you the Literature review citations by Mon 16.

### N7. Draft Ethics and legal (70 words) and Conclusion (70 words)
Files: `report/sections/ethics_and_legal.md` and `report/sections/conclusion.md`.
- **Ethics and legal must cover four things:** privacy (the data is anonymized, no personal information), the licence (CC BY NC SA 4.0, coursework only, attribution to Criteo), bias and fairness (anonymized features mean we cannot test subgroups, which is a limitation), and deployment (an intervention can harm some users, so a human must review any real use). Use your sleeping dogs result.
- **Conclusion and future work:** state the H1 verdict in one sentence, the main lesson in one sentence, the main limitations (one dataset, anonymized features, no cost model, rare conversions) and two ideas for future work (for example SHAP on the best model, or a cost aware policy). Use only numbers from `results/`.

### N8. Merge the drafts
Thu 19: put the eight drafts from `report/sections/` into the template. Run `count_words.py`. If the total is over 1,000, send the list of sections to cut to the authors. Do not cut text yourself without telling them.

### N9. Number check
Fri 20: tick every number in your two sections against its source file.

### N10. Assemble and polish
Sat 21 to Mon 23: finish the PDF. Check page count (5 at most), font size (11 pt or larger in body, figures legible at phone size), column layout, figure captions, the code link and the Contribution and Roles table. Fix layout, not content. Content changes go through the section author.

### N11. Final PDF checks
Wed 25: open the PDF on a phone and on a laptop. Check that fonts are embedded, links are clickable, the word count script still passes and the page count is right.

## Reviews you owe

| Review | When |
|---|---|
| Ganesh's data pull request | Sun 15 |
| Sai's Literature review | Tue 17 |
| Ganesh's Results section | Thu 19 |

## Oral assessment: questions you must answer well
1. What are the three stages of the X learner?
2. Why does the control based effect model get the larger weight in our data?
3. When is the X learner expected to beat the T learner, and did it here?
4. How does the policy simulation turn scores into extra outcomes per 100,000 users contacted?
5. What is a sleeping dog, and what does our check show?
6. What is the main ethical risk of deploying a targeting model?
7. What does the licence allow and not allow?
8. What are the three main limitations of our study?

## Definition of done
- [ ] Every deliverable above is merged
- [ ] The code runs from a clean clone
- [ ] Every number in your report sections traces to a file in `results/`
- [ ] The final PDF passes the checklist in `docs/PLAN.md`
- [ ] You can answer the eight questions without notes
