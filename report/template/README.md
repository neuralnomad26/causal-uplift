# Report template

Two column A4 LaTeX template for the CSC1181 Group 12 report. Body, captions, table and references are all 11 pt, margins 2 cm.

| File | What it is |
|---|---|
| `main.tex` | The layout: title block, the nine headings, the four figures, the roles table, the references |
| `sections/*.tex` | One file per section. Paste the final text of `report/sections/<name>.md` here |
| `sections/roles.tex` | Contribution and Roles table |
| `sections/references.tex` | Numbered reference list, same order as `report/references.md` |
| `main.pdf` | The built report |
| `dummy_test.tex`, `make_dummy.py`, `dummy_test.pdf` | Page limit test: 930 words of dummy text at each section's word budget, the four figures, a filled roles table. Builds to 4 pages |

The figures are read from `report/` (`qini_curves.png`, `uplift_by_decile.png`, `size_curve.png`, `policy_simulation.png`).

## Build

With [Tectonic](https://tectonic-typesetting.github.io) (one program, it downloads the LaTeX packages it needs on the first run):

```
cd report/template
tectonic main.tex
```

Page limit test:

```
python make_dummy.py
tectonic dummy_test.tex
```

Any other LaTeX works too (`pdflatex main.tex` from this folder). On Overleaf, upload this folder and the four PNG files from `report/` into the project root.

## Pasting a section in

1. Copy the paragraphs from `report/sections/<name>.md` into `sections/<name>.tex`. One name differs: `report/sections/analysis.md` goes into `sections/analysis_and_discussion.tex`.
2. Escape `%`, `&`, `_` and `#` as `\%`, `\&`, `\_`, `\#`. Turn each `**Label.**` run-in heading (Methods and Ethics and legal) into `\textbf{Label.}`, or it prints as asterisks. Write a negative number as `$-0.000091$` so the minus sign cannot be left at the end of a line.
3. Delete the HTML comments (`<!-- ... -->`). Do not turn them into `%` comments: a `%` hides the rest of a one line paragraph. The sources stay in `report/sections/`. Then close up the spaces the deletion leaves: no double spaces and no space before a comma, full stop, semicolon or bracket.
4. Cite as `[1]` in the Markdown becomes `\cite{ascarza2018}`, or keep the plain `[1]` text. Both print as [1].
5. Refer to figures as `Figure~\ref{fig:qini}`, `\ref{fig:decile}`, `\ref{fig:size}`, `\ref{fig:policy}`.
