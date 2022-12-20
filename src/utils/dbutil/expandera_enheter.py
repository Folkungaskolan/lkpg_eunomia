""" expandera enheter för id_komplement_pa """

from settings.enhetsinfo import ID_AKTIVITET, ENHETER_SOM_HAR_CBS, STLARS_ENHETER, FOLKUNGA_GY_ENHETER, FOLKUNGA_GRU_ENHETER, ALLA_ENHETER
from utils.EunomiaEnums import EnhetsAggregering


def expandera_enheter(enheter_att_expandera: set[str] | set[EnhetsAggregering]) -> set[str]:
    """ Expandera enheter för id_komplement_pa """
    expandrade_enheter = set()
    enheter_i_enhetsinfo = {}
    # if enheter_att_expandera is
    if isinstance(enheter_att_expandera, EnhetsAggregering):
        if enheter_att_expandera == EnhetsAggregering.ALLA:  # Alla Enheter
            enheter_i_enhetsinfo = ALLA_ENHETER
        elif enheter_att_expandera == EnhetsAggregering.CB:  # Alla som har Chromebooks
            enheter_i_enhetsinfo = ENHETER_SOM_HAR_CBS
        elif enheter_att_expandera == EnhetsAggregering.F_GY:  # F_GY = "F_GY"
            enheter_i_enhetsinfo = FOLKUNGA_GY_ENHETER
        elif enheter_att_expandera == EnhetsAggregering.GRU:
            enheter_i_enhetsinfo = FOLKUNGA_GRU_ENHETER
        elif enheter_att_expandera == EnhetsAggregering.GRU4_6:
            return {"656510"}
        elif enheter_att_expandera == EnhetsAggregering.GRU7_9:
            return {"656520"}
        elif enheter_att_expandera == EnhetsAggregering.STL:
            enheter_i_enhetsinfo = STLARS_ENHETER
        elif enheter_att_expandera == EnhetsAggregering.FOLKUNGA:
            enheter_i_enhetsinfo = FOLKUNGA_GY_ENHETER | FOLKUNGA_GRU_ENHETER
        for e_enhet in enheter_i_enhetsinfo:
            expandrade_enheter.add(e_enhet)

    elif isinstance(enheter_att_expandera, set):
        for enhet in ALLA_ENHETER:
            for e in enheter_att_expandera:
                if enhet.startswith(e):
                    expandrade_enheter.add(enhet)
                    continue

    return expandrade_enheter


if __name__ == '__main__':
    print(expandera_enheter(EnhetsAggregering.CB))
    # print(expandera_enheter("123456"))
    # print(expandera_enheter(["655122"]))