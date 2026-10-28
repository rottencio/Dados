import pytest

from dice_logic import DiceExpressionError, roll_dice


def sequence_rng(values):
    values = iter(values)
    return lambda low, high: next(values)


@pytest.mark.parametrize(
    ("expression", "values", "expected"),
    [
        ("d20", [14], 14),
        ("1d20+5", [14], 19),
        ("2d6+3", [4, 2], 9),
        ("2D6 - 2", [6, 1], 5),
        ("d100", [100], 100),
    ],
)
def test_normal_rolls(expression, values, expected):
    result = roll_dice(expression, rng=sequence_rng(values))
    assert result.total == expected


def test_four_d6_keep_three_highest():
    result = roll_dice("4d6", keep="highest", rng=sequence_rng([1, 4, 5, 6]))
    assert result.rolls == (1, 4, 5, 6)
    assert result.kept_rolls == (6, 5, 4)
    assert result.total == 15


def test_four_d6_keep_three_lowest():
    result = roll_dice("4d6", keep="lowest", rng=sequence_rng([1, 4, 5, 6]))
    assert result.kept_rolls == (1, 4, 5)
    assert result.total == 10


def test_advantage_uses_highest_of_two_d20():
    result = roll_dice("1d20+3", advantage="advantage", rng=sequence_rng([4, 17]))
    assert result.rolls == (4, 17)
    assert result.kept_rolls == (17,)
    assert result.total == 20


def test_disadvantage_uses_lowest_of_two_d20():
    result = roll_dice("d20-2", advantage="disadvantage", rng=sequence_rng([4, 17]))
    assert result.kept_rolls == (4,)
    assert result.total == 2


@pytest.mark.parametrize(
    "expression",
    [
        "", "0d6", "101d6", "d1", "d1001", "d20+9999999",
        "__import__('os').system('echo unsafe')", "2d6+3;4d6",
    ],
)
def test_invalid_expressions_are_rejected(expression):
    with pytest.raises(DiceExpressionError):
        roll_dice(expression)


def test_advantage_rejects_non_d20():
    with pytest.raises(DiceExpressionError):
        roll_dice("2d6", advantage="advantage", rng=sequence_rng([2, 4]))


def test_rng_out_of_range_is_rejected():
    with pytest.raises(ValueError):
        roll_dice("d6", rng=lambda low, high: 0)
