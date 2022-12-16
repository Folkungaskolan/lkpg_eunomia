""" tester för funktionen decode_klass_to_id_komplement_pa"""

from utils.student.student import decode_klass_to_id_komplement_pa


def test_EK20B_FOL():
    """ test Ek1 """
    assert decode_klass_to_id_komplement_pa(klass_namn="Ek20B_FOL") == ['655119']


def test_EK21C_FOL():
    """ test Ek2 """
    assert decode_klass_to_id_komplement_pa(klass_namn="Ek21C_FOL") == ['655119']


def test_SA21D_FOL():
    """ test Ek2 """
    assert decode_klass_to_id_komplement_pa(klass_namn="SA21D_FOL") == ['655122']


def test_7A_FOL15():
    """ test 7A """
    assert decode_klass_to_id_komplement_pa(klass_namn="7A_FOL15") == ['656520']
