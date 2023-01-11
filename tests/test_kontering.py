import pytest

from conftest import FLOAT_TOLERANCE_IN_TESTS
from database.models import FakturaRad_dbo
from utils.faktura_utils._3_1_kontering import decode_kontering_in_fritext


def test_kontering_A513(base_student_numbers):
    # Kontering>A513
    actual = decode_kontering_in_fritext(konterings_string="Kontering>A513",
                                         faktura_rad=FakturaRad_dbo(faktura_month=13,
                                                                    faktura_year=1900))
    expected = ({'655123': 12 / (12 + 10 + 14),
                 '655119': 10 / (12 + 10 + 14),
                 '655122': 14 / (12 + 10 + 14)},
                'p',
                'Kontering>A513')
    print(actual)
    for key, value in expected[0].items():
        assert key in actual[0].keys()
        assert expected[0][key] == pytest.approx(actual[0][key], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual[0].keys()) == len(expected[0].keys())
    assert actual[1] == 'p'
    assert actual[2] == 'Kontering>A513'


def test_kontering_GruTeknik(base_student_numbers):
    """Kontering>GruTeknik"""
    expected = ({'656520': 16 / (16 + 18),
                 '656510': 18 / (16 + 18)
                 },
                'p', 'Kontering>GruTeknik')
    actual = decode_kontering_in_fritext(konterings_string="Kontering>GruTeknik", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    print(actual)
    for key, value in expected[0].items():
        assert key in actual[0].keys()
        assert expected[0][key] == pytest.approx(actual[0][key], FLOAT_TOLERANCE_IN_TESTS)
    assert len(actual[0].keys()) == len(expected[0].keys())

    assert actual[1] == 'p'
    assert actual[2] == 'Kontering>GruTeknik'


def test_kontering_Musikproduktion(base_student_numbers):
    #     Kontering>Musikproduktion
    actual = decode_kontering_in_fritext(konterings_string="Kontering>Musikproduktion", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    assert ({'656520': 1}, 'p', 'Kontering>Musikproduktion') == actual


def test_kontering_FolkungaBibliotek(base_student_numbers):
    #     Kontering>FolkungaBibliotek
    actual = decode_kontering_in_fritext(konterings_string="Kontering>FolkungaBibliotek", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    assert len(actual[0].keys()) == 7

    expected = {'656520': 0.16071428571428573,
                '655125': 0.19642857142857142,
                '655123': 0.10714285714285714,
                '656310': 0.17857142857142858,
                '656510': 0.14285714285714285,
                '655119': 0.08928571428571429,
                '655122': 0.125}
    for key, value in expected.items():
        assert key in actual[0].keys()
        assert expected[key] == pytest.approx(actual[0][key], FLOAT_TOLERANCE_IN_TESTS)
    assert actual[1] == 'p'
    assert actual[2] == 'Kontering>FolkungaBibliotek'


def test_kontering_EnheterGiven(base_student_numbers):
    #     Kontering>Enheter<656:0.1;655:0.9     exv
    actual = decode_kontering_in_fritext(konterings_string='Kontering>Enheter<656:0.1;655:0.9|aktivitet:p',
                                         faktura_rad=FakturaRad_dbo(faktura_month=13,
                                                                    faktura_year=1900)
                                         )
    # print(actual) # ({'656': 0.1, '655': 0.9}, 'p', 'Kontering>Enheter<656:0.1;655:0.9')
    assert len(actual[0].keys()) == 2

    expected = {'656': 0.1, '655': 0.9}
    for key, value in expected.items():
        assert key in actual[0].keys()
        assert actual[0][key] == pytest.approx(expected[key], FLOAT_TOLERANCE_IN_TESTS)
    assert actual[1] == 'p'
    assert actual[2] == 'Kontering>Enheter<656:0.1;655:0.9'


def test_kontering_EnheterStar(base_student_numbers):
    #     Kontering>Enheter<656:0.1;655:*      * innebär "resten"
    actual = decode_kontering_in_fritext(konterings_string="Kontering>Enheter<656:0.1;655:*|aktivitet:p", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    # print(actual) ({'656': 0.1, '655': 0.9}, 'p', 'Kontering>Enheter<656:0.1;655:*')
    assert len(actual[0].keys()) == 2

    expected = {'656': 0.1, '655': 0.9}
    for key, value in expected.items():
        assert key in actual[0].keys()
        assert actual[0][key] == pytest.approx(expected[key], FLOAT_TOLERANCE_IN_TESTS)
    assert actual[1] == 'p'
    assert actual[2] == 'Kontering>Enheter<656:0.1;655:*'


def test_kontering_DirektElev(base_student_numbers, base_student_account):
    #     Kontering>DirektElev<användarnamn
    actual = decode_kontering_in_fritext(konterings_string="Kontering>DirektElev<abcabc123", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    # print(actual)  ({'655119': 1.0}, 'p', 'Kontering>DirektElev<abcabc123')
    expected = {'655119': 1.0}
    for key, value in expected.items():
        assert key in actual[0].keys()
        assert actual[0][key] == pytest.approx(expected[key], FLOAT_TOLERANCE_IN_TESTS)
    assert actual[1] == 'p'
    assert actual[2] == 'Kontering>DirektElev<abcabc123'
