# Audit of the results

Written by `notebooks/12_audit.ipynb`. The file is regenerated every time the notebook runs, so do not edit it by hand.

| Check | Result | Comment |
| --- | --- | --- |
| 1. No leakage | PASS | The holdout has 2,000,000 unique ids and shares 0 ids with the training samples of 100k, 500k, 1m, 5m rows. 4 of 4 scores files have exactly the holdout ids as index, in make_splits order, with treatment, visit and conversion equal to the data file. This does not show which rows a model was trained on, check 8 does that at 100k by a bit exact refit on pool_ids[:n]. |
| 2. Treated share | PASS | Treated share runs from 0.8497 to 0.8506 across the holdout and the 4 training samples. The largest gap from 0.85 is 0.061 percentage points. |
| 3. Curve end equals the average effect | PASS | The curve end matches the observed holdout average effect from ate_visit_conversion.csv for 32 of 32 curves (4 files, 2 outcomes, 4 models). The largest gap is 0.00e+00. The curve end is an identity for its own rows, the independent part is the reference file. |
| 4. Intervals contain the estimates | PASS | 8 of 8 rows have ci_lo <= qini_coef <= ci_hi. The smallest margin to an interval end is 0.000070. |
| 5. Bounded by the oracle | PASS | Committed planted test: the oracle gives 0.006317, the T-learner 0.005956, noise margin 0.000506, and the oracle, random and reversed rows are reproduced to 4.8e-07. Unit test data: the largest learner minus oracle is 0.000023 and 0 of 3 learners have an interval entirely above zero. |
| 6. Bootstrap stability | FAIL | Seed 7 against seed 42 on 6 learner and outcome tests: verdict flips for X-learner on visit (fragile). Bonferroni p values for visits S, T, X: 0.0149, 0.2388, 0.0448 (seed 7) against 0.0149, 0.3284, 0.0746 (seed 42). For the X-learner on visits, 4 of 200 resamples did not beat the response baseline at seed 42 and 2 at seed 7. Explained below. |
| 7. Seed spread | FAIL | T-learner spread across 3 seeds is 0.000340 against a claimed gain of 0.000177 (1.9 times the gain), and the response spread is 0.000008. The T-learner minus response is -0.000189 to 0.000155 across seeds. S and X have no seed runs. |
| 8. Scores file is reproducible | PASS | T-learner on visits at 100k rows: Qini coefficient 0.002723 in the file and 0.002723 after refit, a difference of 0.00e+00. The largest difference in any single score is 0.00e+00. This also shows the 100k model was trained on pool_ids[:100_000]. |
| 9. 5M scores file holds the holdout ids | PASS | The 5M scores file has 2,000,000 rows. The id set equals the make_splits holdout: True. Same order: True. Treatment, visit and conversion equal the data file at those ids: True. |

7 of 9 checks pass.

Failed checks: 6, 7. A claim that depends on a failed check must be dropped or qualified in the report.

## Check 6 explained: bootstrap stability

Check 6 fails because one verdict flips. With bootstrap seed 42 (notebook 04) the X-learner on visits has a Bonferroni p value of 0.0746, which is not below 0.05, so the test is not supported. With bootstrap seed 7 it has 0.0448 and a lower interval end of 0.000044, so the test is supported.

The test resolution is p = (k + 1) / (200 + 1), where k is the number of resamples in which the learner did not beat the response baseline. The X-learner on visits had k = 4 at seed 42 and k = 2 at seed 7. After the Bonferroni factor of 3 this is p = 0.0746 and p = 0.0448. A difference of 2 resamples out of 200 is enough to cross 0.05, so this verdict sits on the line.

The other verdicts do not move. Supported under both seeds: S-learner on visit. Not supported under either seed: T-learner on visit, S-learner on conversion, T-learner on conversion, X-learner on conversion. The S-learner on visits has Bonferroni p 0.0149 (seed 42) and 0.0149 (seed 7). The T-learner on visits has 0.3284 and 0.2388. All six conversion p values (3 learners, 2 seeds) are at least 1.0000, so none is below 0.05.

With bootstrap seeds 1 to 12 on visits, the Bonferroni p value is below 0.05 in 12 of 12 seeds for the S-learner, 0 of 12 for the T-learner and 10 of 12 for the X-learner. The X-learner verdict therefore depends on the bootstrap seed. Seed 7 is in this range and seed 42 is not.

Consequence for the report: it must not say that the X-learner is significantly better than the response baseline on visits. It may say that the X-learner gain on visits is borderline and depends on the bootstrap seed. The S-learner gain on visits holds up under bootstrap noise. The T-learner on visits and every learner on conversions stay not supported.

Visit tests for bootstrap seeds 1 to 12, how often the Bonferroni p value is below 0.05 (same 200 resamples, same correction over 3 learners):

| Learner (visits) | Seeds with Bonferroni p below 0.05 (of 12) | Smallest p | Median p | Largest p |
| --- | --- | --- | --- | --- |
| S-learner | 12 | 0.0149 | 0.0149 | 0.0149 |
| T-learner | 0 | 0.2388 | 0.3582 | 0.5075 |
| X-learner | 10 | 0.0149 | 0.0448 | 0.0597 |

## Check 7 explained: seed spread

Check 7 fails because the spread of the T-learner Qini coefficient across the 3 seeds (0.000340) is 1.9 times its claimed gain over the response baseline on visits (0.000177). The response baseline itself is steady, with a spread of 0.000008.

The sign is not stable. The T-learner minus the response baseline is -0.000086, -0.000189, 0.000155 for seeds 1, 2, 3, negative in 2 of 3 seeds, with a mean of -0.000040. Changing the training sample and the model seed can turn the T-learner from worse than the response baseline into better.

Consequence for the report: the T-learner advantage on visits must not be claimed. The bootstrap interval of the T-learner minus the response baseline already includes zero (-0.000091 to 0.000457), and the seed runs agree.

Limits of this check. The seed runs use 1M training rows, while the headline is at 5M, so the spread at 5M may be smaller or larger. That is untested. The S-learner and the X-learner have no seed runs, so their gains over the response baseline (0.000157 and 0.000285) have not been compared with a seed spread at all.

## Claims the report must not make

1. Do not say that the X-learner is significantly better than the response baseline on visits. Say that it is borderline and depends on the bootstrap seed: its Bonferroni p value is 0.0746 with seed 42 and 0.0448 with seed 7, and it is below 0.05 in 10 of 12 further seeds.
2. Do not claim that the T-learner beats the response baseline on visits. Its Bonferroni p value is 0.3284 at seed 42 and it is below 0.05 in 0 of 12 further seeds. Its seed spread of 0.000340 is 1.9 times its claimed gain of 0.000177, and its difference to the response baseline is negative in 2 of 3 seed runs.
3. Do not claim that any uplift learner beats the response baseline on conversions. All 3 conversion tests are not supported at both bootstrap seeds. The T-learner on conversions is below the response baseline (-0.000132, interval -0.000212 to -0.000055).
4. Do not say that H1 is supported in general. The tests supported at both bootstrap seeds are: S-learner on visit. Nothing else may be reported as supported.
5. Do not describe the S-learner gain on visits as stable across training samples. It holds under bootstrap noise (p below 0.05 in 12 of 12 further seeds), but the S-learner and the X-learner have no seed runs, so the effect of refitting on another training sample is untested for them.
6. Do not say that the seed spread measured at 1M training rows also holds at 5M, and do not say that it does not. The seed runs are at 1M rows and the headline is at 5M, so the 5M spread is untested.
