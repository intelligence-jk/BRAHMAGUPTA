from fractions import Fraction as F
from formulacards import CARDS, verify_all, to_markdown, to_html, quiz
from formulacards import core


def test_all_cards_verify():
    assert verify_all() == []


def test_checks_use_other_values_too():
    assert core._ap_sum(F(-2), F(7, 3), 4) and core._gp_sum(F(5), F(-2), 5)
    assert core._sum_n(1) and core._sum_sq(1) and core._compound(F(10), F(1, 3), 3)


def test_a_wrong_formula_is_caught():
    bad = core.Card("x", "t", "wrong", "(a + b)^2", "a^2 + b^2", lambda: F(3, 7) ** 2 + F(5) ** 2 == (F(3, 7) + 5) ** 2)
    assert verify_all([bad]) == ["x"]


def test_ids_unique():
    ids = [c.id for c in CARDS]
    assert len(ids) == len(set(ids))


def test_markdown_groups_topics():
    md = to_markdown()
    assert "## Quadratics" in md and "Discriminant" in md


def test_html_escapes_and_has_cards():
    h = to_html()
    assert h.count("class='card'") == len(CARDS)
    assert "|x1" in h


def test_quiz_hides_answer():
    q = quiz()
    assert len(q) == len(CARDS)
    assert all("=" in p and p.endswith("?") for p, _ in q)


def test_no_dashes_in_text():
    for c in CARDS:
        assert chr(0x2014) not in c.formula + c.title and chr(0x2013) not in c.formula + c.title
