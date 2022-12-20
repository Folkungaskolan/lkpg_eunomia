import pytest

from conftest import FLOAT_TOLERANCE_IN_TESTS
from database.models import FakturaRad_dbo
from utils.faktura_utils._3_1_kontering import decode_kontering_in_fritext


def test_kontering_A513(base_student_numbers):
    # Kontering>A513
    actual = decode_kontering_in_fritext(konterings_string="Kontering>A513", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    exp = ({'655123': 0.20689655172413793,
            '655125': 0.3793103448275862,
            '655119': 0.1724137931034483,
            '655122': 0.2413793103448276},
           'p',
           'Kontering>A513')
    assert exp == actual


def test_kontering_GruTeknik(base_student_numbers):
    # Kontering>GruTeknik
    test_dict = {'656310': 0.37037037037037035,
                 '656510': 0.2962962962962963,
                 '656520': 0.3333333333333333}

    actual = decode_kontering_in_fritext(konterings_string="Kontering>GruTeknik", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    # print(actual)
    actual_dict = actual[0]
    for key in test_dict.keys():
        assert key in actual[0].keys()
        assert actual_dict[key] == pytest.approx(test_dict[key], FLOAT_TOLERANCE_IN_TESTS)
    assert actual[1] == 'p'
    assert actual[2] == 'Kontering>GruTeknik'
    assert len(actual[0].keys()) == 3


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
