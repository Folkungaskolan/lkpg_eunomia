""" Testa expandera enheter """
from settings.enhetsinfo import ID_AKTIVITET, ENHETER_SOM_HAR_CBS, FOLKUNGA_GY_ENHETER, FOLKUNGA_GRU_ENHETER, STLARS_ENHETER
from utils.EunomiaEnums import EnhetsAggregering
from utils.dbutil.expandera_enheter import expandera_enheter


def test_expandera_enheter_wrong_id() -> None:
    """ en felaktigenhet """
    exp = []
    result = expandera_enheter(["123456"])
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_655122():
    """ en specifik enhet """
    exp = ["655122"]
    result = expandera_enheter(["655122"])
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_655():
    """ En huvudenhet """
    exp = ['655122', '655123', '655119', '655125']
    result = expandera_enheter(["655"])
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_655_656():
    """ två huvuenheter """
    exp = ['655122', '655123', '655119', '656520', '656510', '656310', '655125']
    result = expandera_enheter(["655", "656"])
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_expandera_ALLA():
    """ EnhetsAggregering.ALLA funkar?"""
    exp = ID_AKTIVITET.keys()
    result = expandera_enheter(EnhetsAggregering.ALLA)
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_expandera_CB():
    """ EnhetsAggregering.CB funkar?"""
    exp = ENHETER_SOM_HAR_CBS
    result = expandera_enheter(EnhetsAggregering.CB)
    for value in exp:
        assert value in result
    assert len(result) == len(exp)

def test_expandera_enheter_expandera_CB():
    """ EnhetsAggregering.CB funkar?"""
    exp = ENHETER_SOM_HAR_CBS
    result = expandera_enheter({EnhetsAggregering.CB})
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_F_GY():
    """ EnhetsAggregering.F_GY funkar?"""
    exp = FOLKUNGA_GY_ENHETER
    result = expandera_enheter(EnhetsAggregering.F_GY)
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_GRU():
    """ EnhetsAggregering.GRU funkar?"""
    exp = FOLKUNGA_GRU_ENHETER
    result = expandera_enheter(EnhetsAggregering.GRU)
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_GRU4_6():
    """ EnhetsAggregering.GRU4_6 funkar?"""
    exp = ["656510"]
    result = expandera_enheter(EnhetsAggregering.GRU4_6)
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_GRU7_9():
    """ EnhetsAggregering.GRU7_9 funkar?"""
    exp = ["656520"]
    result = expandera_enheter(EnhetsAggregering.GRU7_9)
    for value in exp:
        assert value in result
    assert len(result) == len(exp)


def test_expandera_enheter_STL():
    """ EnhetsAggregering.STL funkar?"""
    exp = STLARS_ENHETER
    result = expandera_enheter(EnhetsAggregering.STL)
    for value in exp:
        assert value in result
    assert len(result) == len(exp)
