""" expandera enheter för id_komplement_pa """
import enum

from utils.EunomiaEnums import EnhetsAggregering

from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET, ENHETER_SOM_HAR_CBS, STLARS_ENHETER, FOLKUNGA_GY_ENHETER, FOLKUNGA_GRU_ENHETER


def expandera_enheter(enheter_att_expandera: list[str|EnhetsAggregering]) -> list[str]:
    """ Expandera enheter för id_komplement_pa """
    s = MysqlDb().session()
    expandrade_enheter = []
    alla_enheter = set(ID_AKTIVITET.keys())
    # if enheter_att_expandera is
    for enhet in alla_enheter:
        for e in enheter_att_expandera:
            if isinstance(e,EnhetsAggregering):
                if e == EnhetsAggregering.ALLA:  # Alla Enheter
                    enheter_i_enhetsinfo = ID_AKTIVITET.keys()
                elif e == EnhetsAggregering.CB: # Alla som har Chromebooks
                    enheter_i_enhetsinfo=ENHETER_SOM_HAR_CBS
                elif e == EnhetsAggregering.F_GY: # F_GY = "F_GY"
                    enheter_i_enhetsinfo=  FOLKUNGA_GY_ENHETER
                elif e == EnhetsAggregering.GRU:
                    enheter_i_enhetsinfo = FOLKUNGA_GRU_ENHETER
                elif e == EnhetsAggregering.GRU4_6:
                    enheter_i_enhetsinfo = {"656510"}
                elif e == EnhetsAggregering.GRU7_9:
                    enheter_i_enhetsinfo = {"656520"}
                elif e == EnhetsAggregering.STL:
                    enheter_i_enhetsinfo = STLARS_ENHETER
                #expandera ovanstående
                for e_enhet in enheter_i_enhetsinfo:
                        expandrade_enheter.append(e_enhet)
            if isinstance(e, str) and enhet.startswith(e):
                expandrade_enheter.append(enhet)
    return expandrade_enheter


if __name__ == '__main__':
    print(expandera_enheter(["655", "656"]))
    print(expandera_enheter(["655"]))
