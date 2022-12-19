""" expandera enheter för id_komplement_pa """

from settings.enhetsinfo import ID_AKTIVITET, ENHETER_SOM_HAR_CBS, STLARS_ENHETER, FOLKUNGA_GY_ENHETER, FOLKUNGA_GRU_ENHETER
from utils.EunomiaEnums import EnhetsAggregering


def expandera_enheter(enheter_att_expandera: list[str | EnhetsAggregering]) -> list[str]:
    """ Expandera enheter för id_komplement_pa """
    expandrade_enheter = []
    enheter_i_enhetsinfo = []
    alla_enheter = set(ID_AKTIVITET.keys())
    # if enheter_att_expandera is
    for enhet in alla_enheter:
        if isinstance(enheter_att_expandera, EnhetsAggregering):
            if enheter_att_expandera == EnhetsAggregering.ALLA:  # Alla Enheter
                enheter_i_enhetsinfo = ID_AKTIVITET.keys()
            elif enheter_att_expandera == EnhetsAggregering.CB:  # Alla som har Chromebooks
                enheter_i_enhetsinfo = ENHETER_SOM_HAR_CBS
            elif enheter_att_expandera == EnhetsAggregering.F_GY:  # F_GY = "F_GY"
                enheter_i_enhetsinfo = FOLKUNGA_GY_ENHETER
            elif enheter_att_expandera == EnhetsAggregering.GRU:
                enheter_i_enhetsinfo = FOLKUNGA_GRU_ENHETER
            elif enheter_att_expandera == EnhetsAggregering.GRU4_6:
                return ["656510"]
            elif enheter_att_expandera == EnhetsAggregering.GRU7_9:
                return ["656520"]
            elif enheter_att_expandera == EnhetsAggregering.STL:
                enheter_i_enhetsinfo = STLARS_ENHETER
            elif enheter_att_expandera == EnhetsAggregering.FOLKUNGA:
                enheter_i_enhetsinfo = FOLKUNGA_GY_ENHETER | FOLKUNGA_GRU_ENHETER

        if isinstance(enheter_att_expandera, list):
            for e in enheter_att_expandera:
                if enhet.startswith(e):
                    expandrade_enheter.append(enhet)
    # expandera ovanstående
    if enheter_i_enhetsinfo is not None:
        for e_enhet in enheter_i_enhetsinfo:
            expandrade_enheter.append(e_enhet)
    return expandrade_enheter


if __name__ == '__main__':
    print(expandera_enheter(EnhetsAggregering.ALLA))
    # print(expandera_enheter("123456"))
    # print(expandera_enheter(["655122"]))