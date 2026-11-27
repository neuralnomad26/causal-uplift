import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "report"))
from count_words import count_words, main


def test_plain_sentence(tmp_path):
    f = tmp_path / "sec.md"
    f.write_text("One two three four five.", encoding="utf-8")
    assert count_words(f.read_text(encoding="utf-8")) == 5


def test_html_comment_ignored(tmp_path):
    f = tmp_path / "sec.md"
    f.write_text("<!-- single line comment -->\n<!-- multi\nline\ncomment -->\nHello world", encoding="utf-8")
    assert count_words(f.read_text(encoding="utf-8")) == 2


def test_table_adds_zero(tmp_path):
    f = tmp_path / "sec.md"
    f.write_text("| col1 | col2 |\n| --- | --- |\n| val1 | val2 |\n", encoding="utf-8")
    assert count_words(f.read_text(encoding="utf-8")) == 0


def test_image_line_adds_zero(tmp_path):
    f = tmp_path / "sec.md"
    f.write_text("![some caption here](figures/plot.png)\n", encoding="utf-8")
    assert count_words(f.read_text(encoding="utf-8")) == 0


def test_link_counts_anchor_text_only(tmp_path):
    f = tmp_path / "sec.md"
    f.write_text("[three words here](https://x.y)", encoding="utf-8")
    assert count_words(f.read_text(encoding="utf-8")) == 3


def test_heading_counts_words_not_hashes(tmp_path):
    f = tmp_path / "sec.md"
    f.write_text("## Two words\n", encoding="utf-8")
    assert count_words(f.read_text(encoding="utf-8")) == 2


def test_over_budget_returns_exit_code_1(tmp_path):
    (tmp_path / "abstract.md").write_text(" ".join(["word"] * 75), encoding="utf-8")
    assert main(tmp_path) == 1
