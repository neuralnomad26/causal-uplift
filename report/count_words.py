from pathlib import Path
import re
import sys

BUDGETS = {
    "abstract": 70,
    "problem_and_data": 130,
    "literature_review": 110,
    "methods": 220,
    "results": 130,
    "analysis": 130,
    "ethics_and_legal": 70,
    "conclusion": 70,
}

MAX_TOTAL = 1000


def count_words(text: str) -> int:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    kept_lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("|"):
            continue
        if re.match(r"^!\[[^\]]*\]\([^)]*\)\s*$", stripped):
            continue
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        kept_lines.append(line)
    cleaned = "\n".join(kept_lines)
    return sum(1 for tok in cleaned.split() if any(ch.isalnum() for ch in tok))


def evaluate_sections(sections_dir: Path) -> tuple[list[tuple[str, int, int, str]], int, int]:
    rows = []
    any_over = False
    total_words = 0

    known = list(BUDGETS.keys())
    extra = sorted(
        p.stem
        for p in (sections_dir.glob("*.md") if sections_dir.exists() else [])
        if p.stem != "references" and p.stem not in BUDGETS
    )

    for section in known + extra:
        budget = BUDGETS.get(section, 0)
        path = sections_dir / f"{section}.md"
        if not path.exists():
            rows.append((section, 0, budget, "MISSING"))
            continue
        words = count_words(path.read_text(encoding="utf-8"))
        total_words += words
        if budget and words > budget:
            status = "OVER"
            any_over = True
        else:
            status = "OK"
        rows.append((section, words, budget, status))

    exit_code = 1 if (any_over or total_words > MAX_TOTAL) else 0
    return rows, total_words, exit_code


def main(sections_dir: Path | None = None) -> int:
    if sections_dir is None:
        sections_dir = Path("report") / "sections"
    rows, total_words, exit_code = evaluate_sections(sections_dir)
    total_budget = sum(BUDGETS.values())
    total_status = "OVER" if total_words > MAX_TOTAL else "OK"

    print(f"{'section':<20} {'words':>6} {'budget':>6} {'status':<8}")
    print("-" * 44)
    for section, words, budget, status in rows:
        print(f"{section:<20} {words:>6} {budget:>6} {status:<8}")
    print("-" * 44)
    print(f"{'total':<20} {total_words:>6} {total_budget:>6} {total_status:<8}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
