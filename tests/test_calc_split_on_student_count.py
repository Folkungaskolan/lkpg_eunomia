""" Test för calc_split_on_student_count """

import pytest

from conftest import FLOAT_TOLERANCE_IN_TESTS
from utils.dbutil.student_db import calc_split_on_student_count

""" Testa expandera enheter """
from utils.EunomiaEnums import EnhetsAggregering


def test_wrong_id(base_student_numbers) -> None:
    """ en felaktigenhet """
    with pytest.raises(ValueError):
        calc_split_on_student_count(year=1900, month=13, enheter_to_split_over=["123456"])


def test655122(base_student_numbers) -> None:
    """ en specifik enhet """
    exp = {"655122": 1}
    actual = calc_split_on_student_count(year=1900,
                                         month=13,
                                         enheter_to_split_over=["655122"])
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test655(base_student_numbers) -> None:
    """ En huvudenhet """
    exp = {'655119': 0.1724137931034483,
           '655122': 0.2413793103448276,
           '655125': 0.3793103448275862,
           '655123': 0.20689655172413793}
    actual = calc_split_on_student_count(year=1900,
                                         month=13,
                                         enheter_to_split_over=["655"])
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test655_656(base_student_numbers) -> None:
    """ Två huvudenheter """
    exp = {'655122': 0.12500000000000003,
           '655119': 0.0892857142857143,
           '656310': 0.1785714285714286,
           '655125': 0.19642857142857145,
           '656520': 0.16071428571428575,
           '656510': 0.14285714285714288,
           '655123': 0.10714285714285715}
    actual = calc_split_on_student_count(year=1900,
                                         month=13,
                                         enheter_to_split_over=["655", "656"])
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test_ALLA(base_student_numbers) -> None:
    """ EnhetsAggregering.ALLA funkar?"""
    exp = {'654300': 0.11111111111111113,
           '654500': 0.126984126984127,
           '655125': 0.08730158730158731,
           '655122': 0.055555555555555566,
           '654400': 0.11904761904761907,
           '654200': 0.1031746031746032,
           '656510': 0.0634920634920635,
           '656520': 0.07142857142857144,
           '655123': 0.04761904761904763,
           '654100': 0.09523809523809526,
           '655119': 0.03968253968253969,
           '656310': 0.07936507936507937}
    actual = calc_split_on_student_count(year=1900,
                                         month=13,
                                         enheter_to_split_over=EnhetsAggregering.ALLA)
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test_CB(base_student_numbers) -> None:
    """ EnhetsAggregering.CB funkar?"""
    exp = {'654200': 0.16049382716049382,
           '656520': 0.1111111111111111,
           '654300': 0.1728395061728395,
           '655119': 0.06172839506172839,
           '655123': 0.07407407407407407,
           '654400': 0.18518518518518517,
           '655122': 0.08641975308641975,
           '654100': 0.14814814814814814}
    actual = calc_split_on_student_count(year=1900, month=13,
                                         enheter_to_split_over=EnhetsAggregering.CB)
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test_F_GY(base_student_numbers) -> None:
    """ EnhetsAggregering.F_GY funkar?"""
    exp = {'655119': 0.2777777777777778,
           '655123': 0.3333333333333333,
           '655122': 0.3888888888888889}
    actual = calc_split_on_student_count(year=1900, month=13,
                                         enheter_to_split_over=EnhetsAggregering.F_GY)
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test_GRU(base_student_numbers) -> None:
    """ EnhetsAggregering.GRU funkar?"""
    exp = {'656510': 0.2962962962962963,
           '656310': 0.37037037037037035,
           '656520': 0.3333333333333333}
    actual = calc_split_on_student_count(year=1900, month=13,
                                         enheter_to_split_over=EnhetsAggregering.GRU)
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test_GRU4_6(base_student_numbers) -> None:
    """ EnhetsAggregering.GRU4_6 funkar?"""
    exp = {'656510': 1.0}
    actual = calc_split_on_student_count(year=1900, month=13,
                                         enheter_to_split_over=EnhetsAggregering.GRU4_6)
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test_GRU7_9(base_student_numbers) -> None:
    """ EnhetsAggregering.GRU7_9 funkar?"""
    exp = {'656520': 1.0}
    actual = calc_split_on_student_count(year=1900, month=13,
                                         enheter_to_split_over=EnhetsAggregering.GRU7_9)
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)


def test_STL(base_student_numbers) -> None:
    """ EnhetsAggregering.STL funkar?"""
    exp = {'654200': 0.18571428571428572,
           '654500': 0.22857142857142856,
           '654300': 0.2,
           '654400': 0.21428571428571427,
           '654100': 0.17142857142857143}
    actual = calc_split_on_student_count(year=1900, month=13,
                                         enheter_to_split_over=EnhetsAggregering.STL)
    # print(actual)
    for value in exp:
        assert value in actual
        assert actual[value] == pytest.approx(exp[value], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual) == len(exp)
    assert sum(actual.values()) == pytest.approx(1, FLOAT_TOLERANCE_IN_TESTS)
