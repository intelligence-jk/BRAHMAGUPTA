"""Printable formula cards. Every card carries a check that tests the formula
with exact Fraction arithmetic against a direct calculation."""
from dataclasses import dataclass
from fractions import Fraction as F
from html import escape


@dataclass(frozen=True)
class Card:
    id: str
    topic: str
    title: str
    left: str
    right: str
    check: callable

    @property
    def formula(self):
        return f"{self.left} = {self.right}"


def _sum_n(n=12):
    return sum(range(1, n + 1)) == F(n * (n + 1), 2)


def _sum_sq(n=9):
    return sum(k * k for k in range(1, n + 1)) == F(n * (n + 1) * (2 * n + 1), 6)


def _ap_term(a=F(3, 2), d=F(5, 4), n=11):
    t = a
    for _ in range(n - 1):
        t += d
    return t == a + (n - 1) * d


def _ap_sum(a=F(3, 2), d=F(5, 4), n=11):
    s, t = F(0), a
    for _ in range(n):
        s += t
        t += d
    return s == F(n, 2) * (2 * a + (n - 1) * d)


def _gp_sum(a=F(2, 3), r=F(3, 2), n=7):
    s, t = F(0), a
    for _ in range(n):
        s += t
        t *= r
    return s == a * (r ** n - 1) / (r - 1)


def _roots(r=F(2, 3), s=F(-5, 4)):
    # x^2 - (r+s)x + rs has roots r and s
    b, c = -(r + s), r * s
    return all(x * x + b * x + c == 0 for x in (r, s)) and (r + s, r * s) == (-b, c)


def _discriminant(a=2, b=-7, c=3):
    d = b * b - 4 * a * c
    r1, r2 = F(3), F(1, 2)    # known roots of 2x^2 - 7x + 3
    return d == (a * (r1 - r2)) ** 2 and a * r1 ** 2 + b * r1 + c == 0


def _sq_sum(a=F(3, 7), b=F(-5, 3)):
    return (a + b) ** 2 == a * a + 2 * a * b + b * b


def _diff_sq(a=F(9, 4), b=F(2, 5)):
    return a * a - b * b == (a - b) * (a + b)


def _distance(p=(1, 2), q=(4, 6)):
    return (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 == 25     # 3-4-5 triangle


def _section(p=(F(1), F(2)), q=(F(7), F(11)), m=2, n=1):
    x = (m * q[0] + n * p[0]) / (m + n)
    y = (m * q[1] + n * p[1]) / (m + n)
    # the point is on the line and splits the segment 2 : 1
    return (x - p[0]) * (q[1] - p[1]) == (y - p[1]) * (q[0] - p[0]) and (x - p[0]) * n == (q[0] - x) * m


def _area(a=(0, 0), b=(8, 0), c=(3, 5)):
    area = F(abs(a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1])), 2)
    return area == F(8 * 5, 2)     # base 8, height 5


def _compound(p=F(1000), r=F(1, 20), n=6):
    v = p
    for _ in range(n):
        v *= 1 + r
    return v == p * (1 + r) ** n


def _index(a=F(3, 2), m=5, n=3):
    return a ** m * a ** n == a ** (m + n) and (a ** m) ** n == a ** (m * n)


CARDS = [
    Card("sum-n", "Series", "Sum of the first n counting numbers", "1 + 2 + ... + n", "n(n + 1)/2", _sum_n),
    Card("sum-sq", "Series", "Sum of the first n squares", "1^2 + 2^2 + ... + n^2", "n(n + 1)(2n + 1)/6", _sum_sq),
    Card("ap-term", "Sequences", "nth term of an arithmetic progression", "T(n)", "a + (n - 1)d", _ap_term),
    Card("ap-sum", "Sequences", "Sum of n terms of an arithmetic progression", "S(n)", "n/2 (2a + (n - 1)d)", _ap_sum),
    Card("gp-sum", "Sequences", "Sum of n terms of a geometric progression (r not 1)", "S(n)", "a(r^n - 1)/(r - 1)", _gp_sum),
    Card("roots", "Quadratics", "Sum and product of the roots", "x^2 + bx + c with roots r, s", "r + s = -b and rs = c", _roots),
    Card("disc", "Quadratics", "Discriminant", "b^2 - 4ac", "a^2 (r - s)^2", _discriminant),
    Card("sq-sum", "Algebra", "Square of a sum", "(a + b)^2", "a^2 + 2ab + b^2", _sq_sum),
    Card("diff-sq", "Algebra", "Difference of two squares", "a^2 - b^2", "(a - b)(a + b)", _diff_sq),
    Card("index", "Algebra", "Laws of indices", "a^m a^n and (a^m)^n", "a^(m + n) and a^(mn)", _index),
    Card("distance", "Coordinates", "Distance between two points", "d^2", "(x2 - x1)^2 + (y2 - y1)^2", _distance),
    Card("section", "Coordinates", "Section formula, internal, ratio m : n", "(x, y)", "((m x2 + n x1)/(m + n), (m y2 + n y1)/(m + n))", _section),
    Card("area", "Coordinates", "Area of a triangle from its corners", "Area", "1/2 |x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)|", _area),
    Card("compound", "Money", "Compound growth", "A", "P(1 + r)^n", _compound),
]


def verify_all(cards=CARDS):
    """Return the ids of cards whose check fails (empty means all verified)."""
    return [c.id for c in cards if not c.check()]


def to_markdown(cards=CARDS):
    out, topic = [], None
    for c in sorted(cards, key=lambda c: c.topic):
        if c.topic != topic:
            topic = c.topic
            out.append(f"\n## {topic}\n")
        out.append(f"- **{c.title}**: {c.formula}")
    return "\n".join(out).strip() + "\n"


def to_html(cards=CARDS):
    body = "".join(
        f"<div class='card'><h3>{escape(c.title)}</h3><p>{escape(c.formula)}</p></div>"
        for c in cards)
    return ("<!doctype html><meta charset='utf-8'><title>Formula cards</title>"
            "<style>.card{display:inline-block;width:45%;border:1px solid #333;margin:6px;padding:8px}</style>"
            + body)


def quiz(cards=CARDS):
    """(prompt, answer) pairs with the right-hand side hidden."""
    return [(f"{c.title}: {c.left} = ?", c.right) for c in cards]
