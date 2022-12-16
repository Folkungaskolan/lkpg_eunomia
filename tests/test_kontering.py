from database.models import FakturaRad_dbo
from utils.faktura_utils.kontering import decode_kontering_in_fritext


def test_kontering_A513(base_student_numbers):
    # Kontering>A513
    split = decode_kontering_in_fritext(konterings_string="Kontering>A513", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    assert ({'655123': 0.20689655172413793, '655125': 0.3793103448275862, '655119': 0.1724137931034483, '655122': 0.2413793103448276}, 'p', 'Kontering>A513') == split


def test_kontering_GruTeknik(base_student_numbers):
    # Kontering>GruTeknik
    split = decode_kontering_in_fritext(konterings_string="Kontering>GruTeknik", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    assert "656510" in split[0].keys()
    assert round(split[0]["656510"], 13) == round(0.296296296296296, 13)
    assert "656310" in split[0].keys()
    assert round(split[0]["656310"], 13) == round(0.37037037037037035, 13)
    assert "656520" in split[0].keys()
    assert round(split[0]["656520"], 13) == round(0.3333333333333333, 13)
    assert len(split[0].keys()) == 3


def test_kontering_Musikproduktion(base_student_numbers):
    #     Kontering>Musikproduktion
    split = decode_kontering_in_fritext(konterings_string="Kontering>Musikproduktion", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    assert ({'656520': 1}, 'p', 'Kontering>Musikproduktion') == split


def test_kontering_FolkungaBibliotek(base_student_numbers):
    #     Kontering>FolkungaBibliotek
    split = decode_kontering_in_fritext(konterings_string="Kontering>FolkungaBibliotek", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    assert len(split[0].keys()) == 7

    expected = {'656520': 0.16071428571428573, '655125': 0.19642857142857142,
                '655123': 0.10714285714285714, '656310': 0.17857142857142858,
                '656510': 0.14285714285714285, '655119': 0.08928571428571429,
                '655122': 0.125}
    for key, value in expected.items():
        assert key in split[0].keys()
        assert round(split[0][key], 13) == round(value, 13)
    assert split[1] == 'p'
    assert split[2] == 'Kontering>FolkungaBibliotek'


def test_kontering_EnheterGiven(base_student_numbers):
    #     Kontering>Enheter<656:0.1;655:0.9     exv
    split = decode_kontering_in_fritext(konterings_string='Kontering>Enheter<656:0.1;655:0.9|aktivitet:p',
                                        faktura_rad=FakturaRad_dbo(faktura_month=13,
                                                                   faktura_year=1900)
                                        )
    # print(split) # ({'656': 0.1, '655': 0.9}, 'p', 'Kontering>Enheter<656:0.1;655:0.9')
    assert len(split[0].keys()) == 2

    expected = {'656': 0.1, '655': 0.9}
    for key, value in expected.items():
        assert key in split[0].keys()
        assert round(split[0][key], 13) == round(value, 13)
    assert split[1] == 'p'
    assert split[2] == 'Kontering>Enheter<656:0.1;655:0.9'


def test_kontering_EnheterStar(base_student_numbers):
    #     Kontering>Enheter<656:0.1;655:*      * innebär "resten"
    split = decode_kontering_in_fritext(konterings_string="Kontering>Enheter<656:0.1;655:*|aktivitet:p", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    # print(split) ({'656': 0.1, '655': 0.9}, 'p', 'Kontering>Enheter<656:0.1;655:*')
    assert len(split[0].keys()) == 2

    expected = {'656': 0.1, '655': 0.9}
    for key, value in expected.items():
        assert key in split[0].keys()
        assert round(split[0][key], 13) == round(value, 13)
    assert split[1] == 'p'
    assert split[2] == 'Kontering>Enheter<656:0.1;655:*'

def test_kontering_DirektElev(base_student_numbers, base_student_account):
    #     Kontering>DirektElev<användarnamn
    split = decode_kontering_in_fritext(konterings_string="Kontering>DirektElev<abcabc123", faktura_rad=FakturaRad_dbo(faktura_month=13, faktura_year=1900))
    # print(split)  ({'655119': 1.0}, 'p', 'Kontering>DirektElev<abcabc123')
    expected = {'655119': 1.0}
    for key, value in expected.items():
        assert key in split[0].keys()
        assert round(split[0][key], 13) == round(value, 13)
    assert split[1] == 'p'
    assert split[2] == 'Kontering>DirektElev<abcabc123'