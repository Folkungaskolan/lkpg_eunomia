""" hanterar uppdelning av fakturarader """

from db.models import FakturaRad_dbo, SplitMethods_dbo
from db.mysql_db import init_db


def copy_uniqe_tjanst():
    """ kopiera unika tjänster till ny kolumn """
    local_session = init_db()
    results = local_session.query(FakturaRad_dbo.tjanst).distinct().all()
    for result in results:
        print(result.tjanst)
        exists = local_session.query(SplitMethods_dbo).filter_by(tjanst=result.tjanst).first()
        if exists is None:
            local_session.add(SplitMethods_dbo(tjanst=result.tjanst))
            local_session.commit()


def split_row() -> None:
    """ split row """
    copy_uniqe_tjanst()


if __name__ == "__main__":
    split_row()
