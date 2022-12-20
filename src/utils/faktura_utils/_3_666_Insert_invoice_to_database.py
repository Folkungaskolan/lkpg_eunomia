import inspect

from sqlalchemy import and_

from database.models import FakturaRadSplit_dbo, FakturaRad_dbo
from database.mysql_db import MysqlDb
from settings.enhetsinfo import ID_AKTIVITET
from utils.EunomiaEnums import FakturaRadState, Aktivitet
from utils.dbutil.kategori_db import get_kategorier_for
from utils.dbutil.student_db import calc_split_on_student_count
from utils.faktura_utils._3_0_print_table import print_faktura_tail, printfakturainfo


@printfakturainfo
def insert_failsafe_row(faktura_rad: FakturaRad_dbo) -> None:
    """ Om allt misslyckas så lägger vi in raden som en failsafe rad. """
    faktura_rad.split_method_used = "Failsafe elevantal Åtgärda"
    faktura_rad.user_aktivitet_char = Aktivitet.A
    faktura_rad.split = calc_split_on_student_count(enheter_to_split_over=faktura_rad.dela_over_enheter, month=faktura_rad.faktura_month, year=faktura_rad.faktura_year)
    faktura_rad.split_status = FakturaRadState.SPLIT_BY_ELEVANTAL_SUCCESSFUL
    insert_split_into_database(faktura_rad=faktura_rad)

@printfakturainfo
def insert_split_into_database(faktura_rad: FakturaRad_dbo, verbose: bool = False) -> None:
    """ generera split raderna """
    s = MysqlDb().session()
    # print(f"insert_split_into_database start                         2022-11-21 12:57:00")
    if faktura_rad.ready_to_be_split(verbose=verbose):
        for enhet in faktura_rad.split.keys():
            if faktura_rad.split[enhet] == 0:  # vi sparar inte noll rader
                continue
            old = s.query(FakturaRadSplit_dbo).filter(and_(FakturaRadSplit_dbo.faktura_year == faktura_rad.faktura_year,
                                                           FakturaRadSplit_dbo.faktura_month == faktura_rad.faktura_month,
                                                           FakturaRadSplit_dbo.id_komplement_pa == enhet,
                                                           FakturaRadSplit_dbo.split_id == faktura_rad.id)
                                                      ).first()
            if old is not None:
                old.anvandare = faktura_rad.anvandare
                old.avser = faktura_rad.avser
                old.tjanst = faktura_rad.tjanst
                old.split_summa = faktura_rad.split[enhet] * faktura_rad.summa
                old.split_metod = faktura_rad.split_method_used[:145]
                old.aktivitet = ID_AKTIVITET[enhet][faktura_rad.user_aktivitet_char.value]
                old.tjanst_kategori_lvl1, old.tjanst_kategori_lvl2 = get_kategorier_for(tjanst=faktura_rad.tjanst)

            else:
                new = FakturaRadSplit_dbo(
                    split_id=faktura_rad.id, faktura_year=faktura_rad.faktura_year, faktura_month=faktura_rad.faktura_month,
                    tjanst=faktura_rad.tjanst, avser=faktura_rad.avser, anvandare=faktura_rad.anvandare,
                    split_method_used=faktura_rad.split_method_used[:145], split_summa=faktura_rad.split[enhet] * faktura_rad.summa,
                    id_komplement_pa=enhet, aktivitet=ID_AKTIVITET[enhet][faktura_rad.user_aktivitet_char.value])
                new.tjanst_kategori_lvl1, new.tjanst_kategori_lvl2 = get_kategorier_for(tjanst=faktura_rad.tjanst)
                s.add(new)
            s.commit()
        faktura_rad.split_done = 1
        s.commit()
        print_faktura_tail(faktura_rad=faktura_rad)
    else:
        pass
        if verbose:
            print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")
            print()
            faktura_rad.print_split_status()
            faktura_rad.ready_to_be_split()
            print(f"{faktura_rad=}")


if __name__ == '__main__':
    pass
