""" Testing student funktions"""
# import pytest
# from conftest import setup_test1
# from database.mysql_db import MysqlDb
# from utils.student.student import decode_klass_to_id_komplement_pa, get_klasser_for_all_students

#
# def test_all_classes_get_a_decode_klass_to_id_komplement_pa()->None:
#     """ test all classes get a decode klass to id komplement pa """
#     # s = MysqlDb().session()
#     klasslist = get_klasser_for_all_students()
#     assert len(klasslist) > 0
#     for klass in klasslist:
#         assert decode_klass_to_id_komplement_pa(klass_namn=klass) is not None
#
# def test_decode_klass_to_id_komplement_pa_on_bad_klass_raises_exception()->None:
#     """ test decode klass to id komplement pa on bad klass raises exception """
#     with pytest.raises(Exception):
#         decode_klass_to_id_komplement_pa(klass_namn="bad klass")

# def test_first_test()->None:
#     """ test first test """
#     expected = {1,2,3}
#     actual = {1,2,4}
#     assert expected == actual

# def test_myf()->None:
#     """ test myf """
#     assert myf(3) == 3
# def myf(x):
#     return x + 1
# def test_more_test(setup_test1)->None:
#     """ test first test """
#     print(" 43153452345"+setup_test1)
#     assert True
# def test_second_test()->None:
#     """ test second test """
#     assert False
#
# class test_some_Stuff:
#     """ test some stuff """
#     def test_three(self):
#         assert {1,2,3} == {1,2}
#
#     def test_four(self):
#         assert {1, 2, 3} == {1, 2}
