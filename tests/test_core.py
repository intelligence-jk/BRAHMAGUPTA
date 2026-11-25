from dataclasses import replace
from fractions import Fraction as F
import pytest
from formulacards import CARDS, verify_all, to_markdown, to_html, quiz
from formulacards import core


def card(i):
    return next(c for c in CARDS if c.id == i)


def test_all_cards_verify():
    assert verify_all() == []


def test_printed_text_is_rendered_from_the_checked_expression():
    assert core.render("n*(n+1)/2") == "n(n + 1)/2"
    assert card("sum-n").formula == "1 + 2 + ... + n = n(n + 1)/2"
    assert "a(r^n - 1)/(r - 1)" in card("gp-sum").formula
    assert "n(n + 1)/2" in to_markdown()


def test_the_task_mutation_is_caught():
    c = card("sum-n")
    bad = replace(c, pairs=((c.pairs[0][0], "n*(n-1)/2"),))
    assert bad.formula.endswith("n(n - 1)/2")      # the printed text changes with it
    assert verify_all([bad]) == ["sum-n"]
    assert verify_all([c]) == []


@pytest.mark.parametrize("c", CARDS, ids=lambda c: c.id)
def test_every_card_fails_when_its_formula_is_changed(c):
    left, right = c.pairs[0]
    bad = replace(c, pairs=((left, f"({right})+1"),) + c.pairs[1:])
    assert verify_all([bad]) == [c.id]


def test_expression_left_side_is_checked_too():
    c = card("sq-sum")
    bad = replace(c, pairs=(("(a+b)**2+a", c.pairs[0][1]),))
    assert verify_all([bad]) == ["sq-sum"]


def test_second_part_of_a_card_is_checked():
    c = card("index")
    bad = replace(c, pairs=(c.pairs[0], ("(a**m)**n", "a**(m+n)")))
    assert verify_all([bad]) == ["index"]


def test_sum_formulas_match_real_sums_for_n_1_to_50():
    for n in range(1, 51):
        assert core.evaluate("n*(n+1)/2", {"n": n}) == sum(range(1, n + 1))
        assert core.evaluate("n*(n+1)*(2*n+1)/6", {"n": n}) == sum(k * k for k in range(1, n + 1))
    assert len(card("sum-n").samples) == 50


def test_roots_substituted_into_the_quadratic_give_exactly_zero():
    c = card("roots")
    for r, s in [(F(2, 3), F(-5, 4)), (F(3), F(1, 2)), (F(-7), F(-7)), (F(0), F(9, 5))]:
        b = core.evaluate(c.pairs[0][1], {"r": r, "s": s})
        cc = core.evaluate(c.pairs[1][1], {"r": r, "s": s})
        assert r * r + b * r + cc == 0 and s * s + b * s + cc == 0
    assert len(c.samples) >= 6


def test_roots_check_catches_a_wrong_constant_term():
    c = card("roots")
    bad = replace(c, pairs=(c.pairs[0], (c.pairs[1][0], "r*s+1")))
    assert verify_all([bad]) == ["roots"]


def test_extra_check_alone_would_catch_it():
    c = card("roots")
    assert c.extra({"r": F(2), "s": F(3)}, [F(-5), F(6)])
    assert not c.extra({"r": F(2), "s": F(3)}, [F(-5), F(7)])


@pytest.mark.parametrize("bad", ["__import__('os')", "n.real", "abs(1, 2)", "[1]", "n if n else 1",
                                 "2.5", "len(n)", "n % 2", "lambda: 1"])
def test_parser_refuses_anything_else(bad):
    with pytest.raises((ValueError, SyntaxError)):
        core.parse(bad)


def test_non_whole_exponent_is_refused():
    with pytest.raises(ValueError):
        core.evaluate("a**n", {"a": 2, "n": F(1, 2)})


def test_ids_unique():
    ids = [c.id for c in CARDS]
    assert len(ids) == len(set(ids)) == 14


def test_markdown_groups_topics():
    md = to_markdown()
    assert "## Quadratics" in md and "Discriminant" in md


def test_html_escapes_and_has_cards():
    h = to_html()
    assert h.count("class='card'") == len(CARDS)
    assert "|x1(y2 - y3)" in h


def test_quiz_hides_answer():
    q = quiz()
    assert len(q) == len(CARDS) + 3     # roots, index and section have two parts, asked part by part
    assert all("=" in p and p.endswith("?") for p, _ in q)
    assert not any(a in p for p, a in q)


def test_no_dashes_in_text():
    for c in CARDS:
        assert chr(0x2014) not in c.formula + c.title and chr(0x2013) not in c.formula + c.title
