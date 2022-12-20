""" Hjälp funktioner för faktura delning"""
from database.models import FakturaRad_dbo
from settings.enhetsinfo import FOLKUNGA_GY_ENHETER, FOLKUNGA_GRU_ENHETER, STLARS_ENHETER
from utils.EunomiaEnums import Skola


def set_school_information(faktura_rad: FakturaRad_dbo) -> None:
    """ Översätter från skolans namn till enheter som finns på skolan att dela över som backup om det inte finns någon fasit rad"""
    if faktura_rad.fakturamarkning.startswith("S:t Lars"):
        faktura_rad.dela_over_enheter = STLARS_ENHETER
        faktura_rad.skola = Skola.ST_LARS
    elif faktura_rad.fakturamarkning.startswith("Folkungaskolan"):
        faktura_rad.dela_over_enheter = FOLKUNGA_GY_ENHETER | FOLKUNGA_GRU_ENHETER
        faktura_rad.skola = Skola.FOLKUNGA
    else:
        raise Exception("Unknown fakturamarkning       2022-11-22 15:16:18")

