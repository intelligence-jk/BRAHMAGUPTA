"""Printable formula cards with ONE source of truth per formula.

Each card stores its formula as a small expression string. The printed text is
rendered from that same expression, and `verify_all` evaluates that same
expression with exact `fractions.Fraction` arithmetic against an independent
definitional computation (an actual sum, a repeated product, an expanded
polynomial, a base times height). Mistype the expression and verify fails.

Expressions are parsed with `ast` and only numbers, names, + - * / **,
parentheses and abs() are allowed; nothing else is ever evaluated.
"""
import ast
from dataclasses import dataclass, field
from fractions import Fraction as F
from html import escape


class Label(str):
    """Display-only text for a left-hand side. It is never evaluated; the
    reference computation defines what it means."""


# ---------------------------------------------------------------- parser
_BIN = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)


def parse(expr):
    tree = ast.parse(expr, mode="eval").body
    _check(tree)
    return tree


def _check(n):
    if isinstance(n, ast.BinOp) and isinstance(n.op, _BIN):
        _check(n.left)
        _check(n.right)
    elif isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
        _check(n.operand)
    elif isinstance(n, ast.Constant) and type(n.value) is int:
        pass
    elif isinstance(n, ast.Name):
        pass
    elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "abs"
          and len(n.args) == 1 and not n.keywords):
        _check(n.args[0])
    else:
        raise ValueError(f"not allowed in a formula: {ast.dump(n)}")


def evaluate(expr, env):
    return _ev(parse(expr), env)


def _ev(n, env):
    if isinstance(n, ast.Constant):
        return F(n.value)
    if isinstance(n, ast.Name):
        return F(env[n.id])
    if isinstance(n, ast.UnaryOp):
        v = _ev(n.operand, env)
        return -v if isinstance(n.op, ast.USub) else v
    if isinstance(n, ast.Call):
        return abs(_ev(n.args[0], env))
    a, b = _ev(n.left, env), _ev(n.right, env)
    if isinstance(n.op, ast.Add):
        return a + b
    if isinstance(n.op, ast.Sub):
        return a - b
    if isinstance(n.op, ast.Mult):
        return a * b
    if isinstance(n.op, ast.Div):
        return a / b
    if b.denominator != 1:
        raise ValueError("exponent must be a whole number")
    return a ** int(b)


# -------------------------------------------------------------- renderer
_ATOM = 5


def _prec(n):
    if isinstance(n, ast.BinOp):
        return {ast.Add: 1, ast.Sub: 1, ast.Mult: 2, ast.Div: 2, ast.Pow: 4}[type(n.op)]
    if isinstance(n, ast.UnaryOp):
        return 3
    return _ATOM


def _wrap(n, need):
    t = _r(n)
    return f"({t})" if _prec(n) < need else t


def _r(n):
    if isinstance(n, ast.Constant):
        return str(n.value)
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Call):
        return "|" + _r(n.args[0]) + "|"
    if isinstance(n, ast.UnaryOp):
        return ("-" if isinstance(n.op, ast.USub) else "") + _wrap(n.operand, 4)
    op = n.op
    if isinstance(op, ast.Add):
        return f"{_r(n.left)} + {_r(n.right)}"
    if isinstance(op, ast.Sub):
        return f"{_r(n.left)} - {_wrap(n.right, 2)}"
    if isinstance(op, ast.Div):
        return f"{_wrap(n.left, 2)}/{_wrap(n.right, 3)}"
    if isinstance(op, ast.Pow):
        e = _r(n.right) if isinstance(n.right, (ast.Name, ast.Constant)) else f"({_r(n.right)})"
        return f"{_wrap(n.left, _ATOM)}^{e}"
    lt, rt = _wrap(n.left, 2), _wrap(n.right, 3)
    lnode, rnode = n.left, n.right
    if rt.startswith("("):
        sep = " " if isinstance(lnode, (ast.Div, ast.BinOp)) and isinstance(lnode.op, (ast.Div, ast.Pow)) else ""
    elif (isinstance(rnode, ast.Name) and len(rnode.id) == 1 and (lt[-1].isalnum() or lt[-1] == ")")
          and not (isinstance(lnode, ast.BinOp) and isinstance(lnode.op, (ast.Pow, ast.Div)))):
        sep = ""
    else:
        sep = " "
    return lt + sep + rt


def render(expr):
    """Printed text of an expression: n*(n+1)/2 becomes n(n + 1)/2."""
    return _r(parse(expr))


# ------------------------------------------------------------------ cards
@dataclass(frozen=True)
class Card:
    id: str
    topic: str
    title: str
    pairs: tuple          # ((left, right), ...): left is an expression or a Label; right is an expression
    reference: callable   # independent computation: reference(**vars) -> one value per pair
    samples: tuple        # dicts of variable values, as Fractions or ints
    extra: callable = None  # optional further check: extra(vars, right_values)

    @property
    def formula(self):
        return " and ".join(f"{l if isinstance(l, Label) else render(l)} = {render(r)}"
                            for l, r in self.pairs)


def check_card(c):
    """True if every sample point agrees: the right-hand expression (and the left
    one when it is an expression) equals the independent reference, exactly."""
    try:
        for v in c.samples:
            want = c.reference(**v)
            vals = []
            for (left, right), w in zip(c.pairs, want):
                got = evaluate(right, v)
                vals.append(got)
                if got != w:
                    return False
                if not isinstance(left, Label) and evaluate(left, v) != w:
                    return False
            if len(want) != len(c.pairs):
                return False
            if c.extra and not c.extra(v, vals):
                return False
        return bool(c.samples)
    except (ArithmeticError, ValueError, KeyError, SyntaxError, TypeError):
        return False


# independent definitional computations -----------------------------------
def _poly_mul(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i + j] += x * y
    return out


def _ref_sum_n(n):
    return (F(sum(range(1, n + 1))),)


def _ref_sum_sq(n):
    return (F(sum(k * k for k in range(1, n + 1))),)


def _ref_ap_term(a, d, n):
    t = F(a)
    for _ in range(n - 1):
        t += d
    return (t,)


def _ref_ap_sum(a, d, n):
    s, t = F(0), F(a)
    for _ in range(n):
        s += t
        t += d
    return (s,)


def _ref_gp_sum(a, r, n):
    s, t = F(0), F(a)
    for _ in range(n):
        s += t
        t *= r
    return (s,)


def _ref_roots(r, s):
    # expand (x - r)(x - s) = x^2 + b x + c, coefficients from highest power
    _, b, c = _poly_mul([F(1), -F(r)], [F(1), -F(s)])
    return (b, c)


def _extra_roots(v, vals):
    b, c = vals
    return all(x * x + b * x + c == 0 for x in (F(v["r"]), F(v["s"])))


def _ref_disc(a, r, s):
    A, B, C = [F(a) * k for k in _poly_mul([F(1), -F(r)], [F(1), -F(s)])]
    return (B * B - 4 * A * C,)


def _ref_sq_sum(a, b):
    return (F(a + b) * F(a + b),)


def _ref_diff_sq(a, b):
    return (F(a) * F(a) - F(b) * F(b),)


def _power(a, k):
    out = F(1)
    for _ in range(k):
        out *= a
    return out


def _ref_index(a, m, n):
    return (_power(a, m) * _power(a, n), _power(_power(a, m), n))


def _ref_distance(x1, y1, x2, y2):
    dx, dy = F(x2) - x1, F(y2) - y1
    return (dx * dx + dy * dy,)


def _ref_section(x1, y1, x2, y2, m, n):
    t = F(m, m + n)           # fraction of the way from the first point to the second
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def _ref_area(x1, y1, x2, y2, x3, y3):
    cross = (F(x2) - x1) * (F(y3) - y1) - (F(x3) - x1) * (F(y2) - y1)   # base times height
    return (abs(cross) / 2,)


def _ref_compound(P, r, n):
    v = F(P)
    for _ in range(n):
        v *= 1 + F(r)
    return (v,)


# sample points -------------------------------------------------------------
_FR = (F(3, 2), F(-5, 4), F(2, 3), F(7), F(-1, 3), F(5, 7))


def _n_range(*extra):
    return tuple({"n": n} for n in range(1, 51))


_AP = tuple({"a": a, "d": d, "n": n} for a in _FR[:4] for d in _FR[1:5] for n in (1, 2, 5, 11, 30))
_GP = tuple({"a": a, "r": r, "n": n} for a in _FR[:3] for r in (F(3, 2), F(-2), F(1, 3), F(5)) for n in (1, 2, 7, 12))
_ROOTS = tuple({"r": r, "s": s} for r in _FR for s in _FR)
_DISC = tuple({"a": a, "r": r, "s": s} for a in (F(1), F(2), F(-3), F(1, 2)) for r in _FR[:4] for s in _FR[2:])
_AB = tuple({"a": a, "b": b} for a in _FR for b in _FR)
_IDX = tuple({"a": a, "m": m, "n": n} for a in _FR[:4] for m in (0, 1, 3, 5) for n in (0, 2, 3, 6))
_PT = ((0, 0), (4, 6), (F(1, 2), F(-3, 2)), (-2, 5), (F(7, 3), 1))
_DIST = tuple({"x1": p[0], "y1": p[1], "x2": q[0], "y2": q[1]} for p in _PT for q in _PT)
_SEC = tuple({**d, "m": m, "n": n} for d in _DIST for m, n in ((2, 1), (1, 3), (5, 2)))
_AREA = tuple({"x1": p[0], "y1": p[1], "x2": q[0], "y2": q[1], "x3": s[0], "y3": s[1]}
              for p in _PT[:3] for q in _PT[1:4] for s in _PT[2:])
_COMP = tuple({"P": P, "r": r, "n": n} for P in (F(1000), F(250, 3)) for r in (F(1, 20), F(1, 3), F(3, 50)) for n in (1, 2, 6, 10))

CARDS = (
    Card("sum-n", "Series", "Sum of the first n counting numbers",
         ((Label("1 + 2 + ... + n"), "n*(n+1)/2"),), _ref_sum_n, _n_range()),
    Card("sum-sq", "Series", "Sum of the first n squares",
         ((Label("1^2 + 2^2 + ... + n^2"), "n*(n+1)*(2*n+1)/6"),), _ref_sum_sq, _n_range()),
    Card("ap-term", "Sequences", "nth term of an arithmetic progression",
         ((Label("T(n)"), "a+(n-1)*d"),), _ref_ap_term, _AP),
    Card("ap-sum", "Sequences", "Sum of n terms of an arithmetic progression",
         ((Label("S(n)"), "n/2*(2*a+(n-1)*d)"),), _ref_ap_sum, _AP),
    Card("gp-sum", "Sequences", "Sum of n terms of a geometric progression (r not 1)",
         ((Label("S(n)"), "a*(r**n-1)/(r-1)"),), _ref_gp_sum, _GP),
    Card("roots", "Quadratics", "x^2 + bx + c with roots r and s: b and c in terms of the roots",
         ((Label("b"), "-(r+s)"), (Label("c"), "r*s")), _ref_roots, _ROOTS, _extra_roots),
    Card("disc", "Quadratics", "Discriminant of ax^2 + bx + c, whose roots are r and s",
         ((Label("b^2 - 4ac"), "a**2*(r-s)**2"),), _ref_disc, _DISC),
    Card("sq-sum", "Algebra", "Square of a sum",
         (("(a+b)**2", "a**2+2*a*b+b**2"),), _ref_sq_sum, _AB),
    Card("diff-sq", "Algebra", "Difference of two squares",
         (("a**2-b**2", "(a-b)*(a+b)"),), _ref_diff_sq, _AB),
    Card("index", "Algebra", "Laws of indices",
         (("a**m*a**n", "a**(m+n)"), ("(a**m)**n", "a**(m*n)")), _ref_index, _IDX),
    Card("distance", "Coordinates", "Distance between (x1, y1) and (x2, y2)",
         ((Label("d^2"), "(x2-x1)**2+(y2-y1)**2"),), _ref_distance, _DIST),
    Card("section", "Coordinates", "Section formula, internal, ratio m : n, from (x1, y1) to (x2, y2)",
         ((Label("x"), "(m*x2+n*x1)/(m+n)"), (Label("y"), "(m*y2+n*y1)/(m+n)")), _ref_section, _SEC),
    Card("area", "Coordinates", "Area of a triangle from its corners",
         ((Label("Area"), "abs(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))/2"),), _ref_area, _AREA),
    Card("compound", "Money", "Compound growth",
         ((Label("A"), "P*(1+r)**n"),), _ref_compound, _COMP),
)


def verify_all(cards=CARDS):
    """Return the ids of cards whose check fails (empty means all verified)."""
    return [c.id for c in cards if not check_card(c)]


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
    """(prompt, answer) pairs with the right-hand side hidden. Cards with
    several parts are asked part by part."""
    out = []
    for c in cards:
        for l, r in c.pairs:
            left = l if isinstance(l, Label) else render(l)
            out.append((f"{c.title}: {left} = ?", render(r)))
    return out
