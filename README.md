# formula-cards

Printable maths formula cards where every formula is tested, not just typed.

## What it solves
A wrong formula on a revision card is worse than none. Each card here carries a check that tests the formula on exact fractions against a direct calculation (for example, the sum formula against adding the terms one by one). Output is Markdown or HTML for printing, and a quiz list with the right-hand side hidden. Pure Python 3.10+, standard library only. The cards are standard results written in our own words.

## Example
```bash
python -m formulacards verify
```
```
All cards verified.
```
(Output pasted from a real run.)

## The maths behind it
Example: the sum of n terms of a geometric progression is a(r^n - 1)/(r - 1). The check adds a, ar, ar^2, ... one at a time with exact fractions and compares with the formula, for a = 2/3, r = 3/2, n = 7. If a formula were mistyped in a card, the check would fail and `verify` would exit with an error; a test proves this. There are 14 cards: series, sequences, quadratics, algebra, coordinates and compound growth.

## Install and run
```bash
python -m pip install -e .
python -m pytest
```

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
