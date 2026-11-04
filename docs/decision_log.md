# Decision log

One line per decision, and why. Every member needs to be able to explain these in the oral assessment.

| Date | Decision | Why |
|---|---|---|
| 28 Oct 2026 | Download from the GitHub mirror, not the official link | The official download link returns an error. The mirror's SHA256 matches the one published in the libuplift documentation. |
| 28 Oct 2026 | Always draw a random, seeded sample. Never take the first rows | The file is ordered. The first 5.57M rows are all treated, so they contain no control group. |
| 28 Oct 2026 | Develop on visits first, keep conversion as a secondary outcome until Gate G1 | A 1M sample has about 290 control conversions, too few for a stable Qini curve. Visits are about 20 times more frequent. |
| 28 Oct 2026 | The 1M sample is a subset of the 5M sample | The train and test split must not leak across sample sizes. |
| 2 Nov 2026 | Project approved. Plan re-based on 2 Nov | Results freeze Fri 20 Nov. We submit Thu 26 Nov, a day before the Fri 27 Nov deadline. |
