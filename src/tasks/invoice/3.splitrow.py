""" Hanterar uppdelning av fakturarader """

from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import and_

from database.models import FakturaRad_dbo, SplitMethods_dbo, Tjf_dbo
from database.mysql_db import init_db
from utils.intergration_utils.obsidian import extract_variable_value_from_gear_name


def copy_unique_tjanst(session: Session = None) -> Session:
    """ Kopiera unika tjänster till Split method registret """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    print(F"start copy_unique_tjanst")
    results = local_session.query(FakturaRad_dbo.tjanst).distinct().all()
    for result in results:

        exists = local_session.query(SplitMethods_dbo).filter(SplitMethods_dbo.tjanst == result.tjanst).first()
        if exists is None:
            print(f"adding : {result.tjanst} as new split")
            local_session.add(SplitMethods_dbo(tjanst=result.tjanst))
            local_session.commit()
    print(F"end copy_unique_tjanst")
    return local_session


def split_row() -> None:
    """ split row """
    local_session = init_db()
    # local_session = copy_unique_tjanst(session=local_session)
    known_splits = local_session.query(SplitMethods_dbo).filter(SplitMethods_dbo.method_to_use != None).all()
    for split in known_splits:
        print(f"splitting on {split.tjanst},with method:  {split.method_to_use}")
        eval(split.method_to_use)(tjanst=split.tjanst, session=local_session)


def dela_enl_obsidian(tjanst: str, session: Session = None) -> None:
    """ split på datat i obsidian"""
    print(f"splitting on {tjanst},with method:  {dela_enl_obsidian.__name__}")
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    faktura_rader = local_session.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.tjanst == tjanst,
                                                                    FakturaRad_dbo.split_done == None)).limit(5).all()
    for faktura_rad in faktura_rader:
        kontering = extract_variable_value_from_gear_name(faktura_rad.avser, variable_name="kontering")
        print(f"{faktura_rad.avser}, kontering: {kontering}")
        eval(kontering)(faktura_rad, session=local_session)


def dela_enl_total_tjf(faktura_rad: FakturaRad_dbo, session: Session) -> None:
    """ split på total tjf """
    print(faktura_rad)


# @cache
def generate_total_tjf_for_month(month: int, session: Session = None) -> dict[str, float]:
    """ sum and create a proportion for each tjanstcode in a month """
    if session is None:
        local_session = init_db()
    else:
        local_session = session
    empty_aktivitet = local_session.query(Tjf_dbo.aktivitet).filter(Tjf_dbo.aktivitet == None).all()
    if empty_aktivitet is not None:
        raise ValueError("There are empty numeric aktivitet in tjf")
        raise ValueError("fix !!!")
    id_komplement_pas = local_session.query(Tjf_dbo.id_komplement_pa).distinct().all()
    id_komplement_pas = local_session.query(Tjf_dbo.aktivitet_s).distinct().all()
    for id_komplement_pa in id_komplement_pas:
        id_komplement_pa: str = id_komplement_pa[0]
        print(id_komplement_pa)


if __name__ == "__main__":
    generate_total_tjf_for_month(1)
    # split_row()
