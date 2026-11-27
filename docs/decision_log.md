# Decision log

One line per decision, and why. Every member needs to be able to explain these in the oral assessment.

| Date | Decision | Why |
|---|---|---|
| 28 Oct 2026 | Download from the GitHub mirror, not the official link | The official download link returns an error. The mirror's SHA256 matches the one published in the libuplift documentation. |
| 28 Oct 2026 | Always draw a random, seeded sample. Never take the first rows | The file is ordered. The first 5.57M rows are all treated, so they contain no control group. |
| 28 Oct 2026 | Develop on visits first, keep conversion as a secondary outcome until Gate G1 | A 1M sample has about 290 control conversions, too few for a stable Qini curve. Visits are about 20 times more frequent. |
| 28 Oct 2026 | The 1M sample is a subset of the 5M sample | The train and test split must not leak across sample sizes. |
| 2 Nov 2026 | Project approved. Plan re-based on 2 Nov | Results freeze Fri 20 Nov. We submit Thu 26 Nov, a day before the Fri 27 Nov deadline. |
| 13 Nov 2026 | Hold out a fixed 2M row test set from the full file. Training samples of 100k, 500k, 1M and 5M are nested prefixes of one shuffled pool | A 30 percent split of a 1M sample has about 90 control conversions. A 2M holdout has about 580 and about 11,500 control visits. Nested samples make the data size curve fair. |
| 13 Nov 2026 | Cut features by importance on training rows, dropping f1 and f5 | Both have importance of 0.001 in a response model. On a validation slice inside the training data, AUC is 0.9465 without them and 0.9466 with all 12. |
| 13 Nov 2026 | One tuned LightGBM setting per outcome, shared by the baseline and all three learners | Tuning effort is then identical, so differences between models come from the strategy. |
| 13 Nov 2026 | Qini curve in population scaled form: users targeted times the difference in outcome rates | Rates make the 85/15 split irrelevant, and the curve ends at the average effect, so it reads as extra outcomes per user. |
| 13 Nov 2026 | Test H1 with a paired bootstrap against the response baseline, Bonferroni corrected over 3 learners | Every resample scores all models on the same rows. We run 3 comparisons per outcome, so p values are multiplied by 3. |
| 13 Nov 2026 | X-learner weights the two effect models with the treated share (0.85) | Treatment was randomized, so the propensity is constant. |
| 22 Nov 2026 | Keep every row, including the 11.8 percent that are exact copies of an earlier row | The copies have almost no visits (2 in 100,000) and are 96 percent treated, so dropping them would inflate every visit rate. The file has no user id, so repeats cannot be told from different users with the same features. Notebook 10 scores only the holdout rows with no feature twin in the training rows: the model ranking is unchanged and the gaps to the response baseline are at least as large. |
| 27 Nov 2026 | H1 verdict: partly supported. On visits only the S-learner beats the response baseline (corrected p 0.015). The X-learner is borderline (corrected p 0.075, or 0.045 with another bootstrap seed) and the T-learner is not significant (0.33). On conversion no learner beats the baseline. At a 10 percent budget the X-learner adds 1,133 visits per 100,000 contacted over the baseline (interval 728 to 1,442), and at 20 and 30 percent the intervals include zero | Sources: results/h1_tests_5m.csv, results/policy_simulation_5m.csv and results/audit.md. The report must not say that H1 is supported in general, that the X-learner is significantly better on visits, or that the T-learner beats the baseline on visits. |
