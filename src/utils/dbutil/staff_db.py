from functools import cache

from sqlalchemy.orm import Session

from CustomErrors import DBUnableToCrateUser, NoUserFoundError, NoValidEnheterFoundError
from database.models import Staff_dbo, Tjf_dbo, FasitCopy
from database.mysql_db import init_db, MysqlDb
from utils.faktura_utils.normalize import normalize
from utils.pnr_utils import pnr10_to_pnr12


def get_staff_user_from_db_based_on_user_id(user_id: str, create_on_missing: bool = False) -> Staff_dbo:
    """ Get a user from the database.
    lyadol -> Staff_dbo
    """
    s = MysqlDb().session()

    staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
    if staff is None and create_on_missing:  # if user does not exist, create it
        create_staff_user_from_user_id(user_id=user_id)
        staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
        if staff is None:
            raise DBUnableToCrateUser("Could not create user                            2022-10-11 10:59:36")
    return staff


def create_staff_user_from_user_id(user_id: str) -> None:
    """ Insert a user into the database. """
    s = MysqlDb().session()
    staff = Staff_dbo(user_id=user_id)
    s.add(staff)
    s.commit()


def print_user(user_id: str) -> None:
    """ Print a user from the database. """
    s = MysqlDb().session()

    staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
    print(staff)
    print(type(staff))


def delete_user(user_id: str) -> None:
    """ Delete a user from the database. """
    s = MysqlDb().session()

    staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
    s.delete(staff)
    s.commit()


def update_staff_user(user_id: str,
                      first_name: str = None,
                      last_name: str = None,
                      pnr12: str = None,
                      email: str = None,
                      domain: str = "linkom",
                      titel: str = None) -> None:
    """ Update a user in the database. """
    s = MysqlDb().session()

    staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
    if staff is None:  # if user does not exist, create it
        create_staff_user_from_user_id(user_id=user_id)
        staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
        if staff is None:
            raise DBUnableToCrateUser("Could not create user                            2022-10-11 10:59:36")

    if first_name is not None:  # om värde skickas in uppdatera
        staff.first_name = first_name
    if last_name is not None:  # om värde skickas in uppdatera
        staff.last_name = last_name
    if pnr12 is not None:  # om värde skickas in uppdatera
        if len(pnr12) == 10:
            pnr12 = pnr10_to_pnr12(pnr10=pnr12)
        staff.pnr12 = pnr12
    if email is not None:  # om värde skickas in uppdatera
        staff.email = email
    if titel is not None:  # om värde skickas in uppdatera
        staff.titel = titel
    staff.domain = domain  # har alltid ett värde
    s.commit()


@cache  # personnummret kommer inte att ändras så denna kan cachas
def get_pnr_from_user_id(user_id: str) -> str:
    """ Hämta personnummer från user_id
    197709269034 -> lyadol
    """

    s = MysqlDb().session()
    pnr = s.query(Staff_dbo.pnr12).filter(Staff_dbo.user_id == user_id).first()
    if pnr is not None:
        return pnr[0]
    else:
        raise NoUserFoundError(f"Kunde inte hitta användare med user_id: {user_id}")


CASHED_GET_TJF_FOR_ENHET = {}


def get_tjf_for_enhet(enheter: list[str], month: int) -> dict[str, float]:
    """ get tjf for enhet """
    valid_enheter = []
    key = f"{enheter.sort()}-{month}"
    if key in CASHED_GET_TJF_FOR_ENHET:  # om enhet finns i cachad lista, returnera
        return CASHED_GET_TJF_FOR_ENHET[key]

    s = MysqlDb().session()
    id_komplement_pas = s.query(Tjf_dbo.id_komplement_pa).distinct().all()
    for id_komplement_pa in id_komplement_pas:
        for enhet in enheter:
            if id_komplement_pa.id_komplement_pa.startswith(enhet):
                valid_enheter.append(id_komplement_pa.id_komplement_pa)
    tjfs = s.query(Tjf_dbo).filter(Tjf_dbo.id_komplement_pa.in_(valid_enheter)
                                   ).all()
    if tjfs is None:
        raise NoValidEnheterFoundError(f"Kunde inte hitta tjf för givna enheter{enheter}")
    t = {}
    for tjf in tjfs:
        if month == 1:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.jan
        elif month == 2:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.feb
        elif month == 3:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.mar
        elif month == 4:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.apr
        elif month == 5:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.maj
        elif month == 6:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.jun
        elif month == 7:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.jul
        elif month == 8:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.aug
        elif month == 9:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.sep
        elif month == 10:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.okt
        elif month == 11:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.nov
        elif month == 12:
            t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.dec
        elif month > 13:
            raise ValueError("month must be between 1-12")
    result = normalize(t)
    CASHED_GET_TJF_FOR_ENHET[key] = result
    return result


@cache  # tjänstefördelningen kommer inte förändras inom samma körning så den kan cachas
def gen_tjf_for_staff(user_id: str, month: int) -> dict[str, float]:
    """ Genererar tjf för personalen """
    """ hämta tjänstefördelning för användaren för given månad"""
    pnr12 = get_pnr_from_user_id(user_id=user_id)
    s = MysqlDb().session()
    tjf_s = s.query(Tjf_dbo).filter(Tjf_dbo.pnr12 == pnr12).all()
    t = {}
    if month == 1:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.jan
    elif month == 2:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.feb
    elif month == 3:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.mar
    elif month == 4:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.apr
    elif month == 5:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.maj
    elif month == 6:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.jun
    elif month == 7:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.jul
    elif month == 8:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.aug
    elif month == 9:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.sep
    elif month == 10:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.okt
    elif month == 11:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.nov
    elif month == 12:
        for tjf in tjf_s:
            t[tjf.id_komplement_pa] = tjf.dec
    elif month > 13:
        raise ValueError("month must be between 1-12")
    set_tjf_sum_on_staff(user_id=user_id, month=month, summa=sum(t.values()))
    return normalize(tjf=t)


def set_tjf_sum_on_staff(user_id: str, month: int, summa: float) -> None:
    """ Uppdatera tjf_sum på staff för given månad"""
    s = MysqlDb().session()
    staff = s.query(Staff_dbo).filter(Staff_dbo.user_id == user_id).first()
    if month == 1:
        if staff.sum_tjf_jan == summa * 100:
            return
        staff.sum_tjf_jan = summa * 100

    elif month == 2:
        if staff.sum_tjf_feb == summa * 100:
            return
        staff.sum_tjf_feb = summa * 100

    elif month == 3:
        if staff.sum_tjf_mar == summa * 100:
            return
        staff.sum_tjf_mar = summa * 100

    elif month == 4:
        if staff.sum_tjf_apr == summa * 100:
            return
        staff.sum_tjf_apr = summa * 100

    elif month == 5:
        if staff.sum_tjf_maj == summa * 100:
            return
        staff.sum_tjf_maj = summa * 100

    elif month == 6:
        if staff.sum_tjf_jun == summa * 100:
            return
        staff.sum_tjf_jun = summa * 100

    elif month == 7:
        if staff.sum_tjf_jul == summa * 100:
            return
        staff.sum_tjf_jul = summa * 100

    elif month == 8:
        if staff.sum_tjf_aug == summa * 100:
            return
        staff.sum_tjf_aug = summa * 100

    elif month == 9:
        if staff.sum_tjf_sep == summa * 100:
            return
        staff.sum_tjf_sep = summa * 100

    elif month == 10:
        if staff.sum_tjf_okt == summa * 100:
            return
        staff.sum_tjf_okt = summa * 100

    elif month == 11:
        if staff.sum_tjf_nov == summa * 100:
            return
        staff.sum_tjf_nov = summa * 100

    elif month == 12:
        if staff.sum_tjf_dec == summa * 100:
            return
        staff.sum_tjf_dec = summa * 100

    elif month > 13:
        raise ValueError("month must be between 1-12")
    s.commit()
    return


if __name__ == '__main__':
    pass
    print(get_tjf_for_enhet(enheter=["655", "656"], month=1))
    print(get_tjf_for_enhet(enheter=["655", "656"], month=1))

    # set_tjf_sum_on_staff(user_id="lyadol", month=1, summa=0.0)

# set_tjf_month_okflagg(user_id="lyadol", month=10)
# update_staff_user(user_id="sarqva",
#                   first_name="Sara",
#                   last_name="Qvarnström",
#                   pnr12="197307190525",
#                   email="Sara.Qvarnstrom@utb.linkoping.se",
#                   titel="Rektor")
