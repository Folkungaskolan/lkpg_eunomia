""" Kontroller för att säkerställa kvaliten på datat"""
from sqlalchemy import func

from database.models import FakturaRadSplit_dbo, FakturaRad_dbo
from database.mysql_db import MysqlDb


def back_calc_error_in_splits_to_invoice_table() -> None:
    """ Summerar hur mycket som finns i delade rade och jämför med fakturad summa"""
    s = MysqlDb().session()
    split_ids = s.query(FakturaRadSplit_dbo.split_id).distinct().all()
    for split_id in split_ids:
        invoice_id = split_id.split_id
        print(invoice_id)
        split_sum_for_id = s.query(FakturaRadSplit_dbo.split_id,
                                   func.sum(FakturaRadSplit_dbo.split_summa).label("split_sum")
                                   ).group_by(FakturaRadSplit_dbo.split_id
                                              ).filter(FakturaRadSplit_dbo.split_id == invoice_id
                                                       ).first()
        print(split_sum_for_id.split_sum)
        inv_row = s.query(FakturaRad_dbo).filter(FakturaRad_dbo.id == invoice_id).first()
        inv_row.split_sum = split_sum_for_id.split_sum
        inv_row.split_sum_error = inv_row.summa - split_sum_for_id.split_sum
    s.commit()


def räkna_ut_total_tjf_för_personal() -> None:  # TODO 2022-12-06 11:49:17
    """ Räkna ut total tjänsteförmån för personal """
    pass


if __name__ == '__main__':
    back_calc_error_in_splits_to_invoice_table()
