# formula-cards

Printable maths formula cards where every formula is stored once and tested exactly.

## What it solves
A wrong formula on a revision card is worse than none. Each card here has ONE source of truth: the formula is stored as a small expression, the printed text is rendered from that same expression, and `verify` evaluates that same expression with exact fractions against an independent computation done the long way (an actual sum, a repeated product, an expanded product of brackets, a base times a height). If someone mistypes the expression, the printed card changes with it and `verify` fails. Output is Markdown or HTML for printing, and a quiz list with the right-hand side hidden. Pure Python 3.10+, standard library only. The cards are standard results written in our own words.

## Example
```bash
python -m formulacards verify
```
```
All cards verified.
```
```bash
python -m formulacards
```
Start of the output (the text is rendered from the checked expressions):
```
## Algebra

- **Square of a sum**: (a + b)^2 = a^2 + 2ab + b^2
- **Difference of two squares**: a^2 - b^2 = (a - b)(a + b)
- **Laws of indices**: a^m a^n = a^(m + n) and (a^m)^n = a^(mn)
```
(Output pasted from real runs.)

## The maths behind it
Example: the sum of the first n counting numbers is stored as the expression `n*(n+1)/2`. It is printed as n(n + 1)/2 and checked against an actual sum `1 + 2 + ... + n` for every n from 1 to 50. If the expression were changed to `n*(n-1)/2`, the printed card would change and `verify` would fail; a test (`test_the_task_mutation_is_caught`) does exactly this, and another test changes every one of the 14 cards and checks that each one fails.

How each card is verified, all with `fractions.Fraction`, so there is no rounding anywhere:
- Sum of n numbers and sum of n squares: against the real sum, n = 1 to 50.
- nth term, sum of an arithmetic progression, sum of a geometric progression (r not 1): against repeated addition or multiplication, over many fractional values of a, d, r and several n.
- Roots (b = -(r + s), c = rs): against the coefficients of (x - r)(x - s) expanded term by term. Then each root is substituted into x^2 + bx + c using the card's own b and c, and the result must be exactly 0, for 36 pairs of roots.
- Discriminant a^2 (r - s)^2: against b^2 - 4ac of the expanded a(x - r)(x - s).
- Square of a sum, difference of two squares, laws of indices: both sides against direct multiplication; both sides of each equation are stored as expressions, so both are checked.
- Distance, section formula, triangle area: against differences and a dot product, a point a fraction of the way along the segment, and a base-times-height cross product.
- Compound growth: against repeated multiplication.

Every card is exact. No card needs a numerical (rounded) check, because none has an irrational result.

What is NOT checked: a left-hand side written as a label (for example "1 + 2 + ... + n", "T(n)", "S(n)", "d^2", "Area") is display text. Its meaning is defined by the independent computation it is compared with, so a typo in a label alone would not make `verify` fail. The title text is also not checked. Expressions are parsed with `ast` and only whole numbers, names, + - * / **, brackets and abs() are accepted; nothing else is ever evaluated.

There are 14 cards: series, sequences, quadratics, algebra, coordinates and compound growth.

## Install and run
```bash
python -m pip install -e .
python -m pytest
```

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
