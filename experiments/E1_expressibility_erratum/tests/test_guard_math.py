"""Minimal computational check of the proof in ERRATUM.md §2 (exact Decimal arithmetic, no data).

For integer q and two-decimal u, r = q*u:   q > 0  =>  (r >= 100*q  <=>  u >= 100)
q == 0 admits every u; q < 0 reverses the inequality (u > 100 excluded, u < 100 admitted).
"""
from decimal import Decimal

PRICES = [Decimal(x) for x in ("0.01", "44.06", "99.98", "99.99", "100.00", "100.01", "368.30", "1083.32")]


def derived(q: int, u: Decimal) -> bool:
    return q * u >= 100 * q


def test_equivalence_for_positive_quantity():
    for q in range(1, 6):  # the generator's range randint(1, 5), plus nothing else
        for u in PRICES:
            assert derived(q, u) == (u >= 100), (q, u)


def test_zero_quantity_admits_everything():
    assert all(derived(0, u) for u in PRICES)
    assert any(u < 100 for u in PRICES)  # so membership diverges


def test_negative_quantity_reverses():
    for q in (-1, -3):
        for u in PRICES:
            assert derived(q, u) == (u <= 100), (q, u)
    assert derived(-1, Decimal("44.06")) and not derived(-1, Decimal("368.30"))


def test_inexact_revenue_breaks_boundary():
    # If revenue were rounded (e.g. stored to whole units), a 99.99 line could pass: 3 * 99.99 = 299.97 -> 300.
    q, u = 3, Decimal("99.99")
    rounded = (q * u).quantize(Decimal("1"))
    assert not derived(q, u) and rounded >= 100 * q
