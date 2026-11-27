"""Write dummy section text at the planned word budgets, for the 5 page test.

Run from report/template:  python make_dummy.py
Then build:                tectonic dummy_test.tex
"""
from pathlib import Path

# Word budgets from docs/PLAN.md section 6 (total 930).
BUDGETS = {
    "abstract": 70,
    "problem_and_data": 130,
    "literature_review": 110,
    "methods": 220,
    "results": 130,
    "analysis_and_discussion": 130,
    "ethics_and_legal": 70,
    "conclusion": 70,
}

# A neutral 20 word sentence, repeated and cut to length.
SENTENCE = ("Dummy text for the layout test only. The uplift learners rank users by the "
            "expected gain from treatment over control.").split()

HERE = Path(__file__).parent
OUT = HERE / "dummy"


def dummy_words(n: int) -> str:
    words = [SENTENCE[i % len(SENTENCE)] for i in range(n)]
    # A paragraph break about every 60 words, like real text.
    paras = [" ".join(words[i:i + 60]) for i in range(0, n, 60)]
    return "\n\n".join(paras) + "\n"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    total = 0
    for slot, n in BUDGETS.items():
        (OUT / f"{slot}.tex").write_text(dummy_words(n), encoding="utf-8")
        total += n
    roles = (HERE / "sections" / "roles.tex").read_text(encoding="utf-8")
    filled = "Dummy description of this member's work, about fifteen words long, for the layout test."
    for name in ["Neeraj", "Ganesh", "Sai", "Niranjan"]:
        roles = roles.replace(f"{name:<8} & \\\\", f"{name:<8} & {filled} \\\\")
    (OUT / "roles.tex").write_text(roles, encoding="utf-8")
    (OUT / "references.tex").write_text(
        (HERE / "sections" / "references.tex").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {len(BUDGETS)} dummy sections, {total} words in total, to {OUT}")


if __name__ == "__main__":
    main()
