import inspect
from functools import cache

from sqlalchemy.orm import Session

from CustomErrors import DBUnableToCrateUser, NoUserFoundError, NoValidEnheterFoundError
from database.models import Staff_dbo, Tjf_dbo, FasitCopy, FakturaRad_dbo
from database.mysql_db import init_db, MysqlDb
from statics.eunomia_date_helpers import MONTHS_name_to_int, MONTHS_NAMES, MONTHS_int_to_name
from utils.faktura_utils.normalize import normalize
from utils.pnr_utils import pnr10_to_pnr12


def get_staff_user_from_db_based_on_user_id(user_id: str, create_on_missing: bool = False, verbose: bool = False) -> Staff_dbo:
    """ Get a user from the database.
    lyadol -> Staff_dbo
    """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()

    staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
    if staff is None and create_on_missing:  # if user does not exist, create it
        create_staff_user_from_user_id(user_id=user_id)
        staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
        if staff is None:
            raise DBUnableToCrateUser("Could not create user                            2022-10-11 10:59:36")
    return staff


def create_staff_user_from_user_id(user_id: str, verbose: bool = False) -> None:
    """ Insert a user into the database. """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    staff = Staff_dbo(user_id=user_id)
    s.add(staff)
    s.commit()


def print_user(user_id: str, verbose: bool = False) -> None:
    """ Print a user from the database. """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
    print(staff)
    print(type(staff))


def delete_user(user_id: str, verbose: bool = False) -> None:
    """ Delete a user from the database. """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

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
                      titel: str = None, verbose: bool = False) -> None:
    """ Update a user in the database. """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

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
def get_pnr_from_user_id(user_id: str, verbose: bool = False) -> str:
    """ Hämta personnummer från user_id
    197709269034 -> lyadol
    """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    pnr = s.query(Staff_dbo.pnr12).filter(Staff_dbo.user_id == user_id).first()
    if pnr is not None:
        return pnr[0]
    else:
        raise NoUserFoundError(f"Kunde inte hitta användare med user_id: {user_id}")


CASHED_GET_TJF_FOR_ENHET = {}


def get_tjf_for_enhet(enheter: list[str], month: int, verbose: bool = False) -> dict[str, float]:
    """ get tjf for enhet """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

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
        for month in MONTHS_NAMES:
            exec(F"t[tjf.id_komplement_pa] = t.get(tjf.id_komplement_pa, 0) + tjf.{month}")
    result = normalize(t)
    CASHED_GET_TJF_FOR_ENHET[key] = result
    return result


@cache  # tjänstefördelningen kommer inte förändras inom samma körning så den kan cachas
def gen_tjf_for_staff(user_id: str, faktura_rad: FakturaRad_dbo, verbose: bool = False) -> dict[str, float]:
    """ Genererar tjf för personalen """
    """ hämta tjänstefördelning för användaren för given månad"""
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    pnr12 = get_pnr_from_user_id(user_id=user_id)
    s = MysqlDb().session()
    tjf_s = s.query(Tjf_dbo).filter(Tjf_dbo.pnr12 == pnr12).all()
    t = {}
    for tjf in tjf_s:
        for month in MONTHS_NAMES:  # jan,feb, osv...
            exec(f"t[tjf.id_komplement_pa] = tjf.{month}")
    set_tjf_sum_on_staff(user_id=user_id, month=faktura_rad.faktura_month, summa=sum(t.values()))
    return normalize(tjf=t)


def set_tjf_sum_on_staff(user_id: str, month: int, summa: float, verbose: bool = False) -> None:
    """ Uppdatera tjf_sum på staff för given månad"""
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    staff = s.query(Staff_dbo).filter(Staff_dbo.user_id == user_id).first()
    exec(f"staff.sum_tjf_{MONTHS_int_to_name[month]} = summa * 100")
    if round(summa * 100, 3) > 100:
        staff.tjf_error = True
    s.commit()
    return


def get_user_id_for_staff_user_based_on_full_name(full_name: str, verbose: bool = False) -> str:
    """ Hämtar user_id om "fullname" matchar """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    user_id = s.query(Staff_dbo.user_id).filter(Staff_dbo.full_name == full_name).first()
    if user_id is not None:
        return user_id[0]
    else:
        NoUserFoundError(f"Kunde inte hitta användare med attribute_anvandare: {full_name}")


if __name__ == '__main__':
    # tjf_lyam = gen_tjf_for_staff(user_id="lyadol", faktura_rad=FakturaRad_dbo(faktura_month=10))
    # print(tjf_lyam)
    # print(tjf_lyam.values())
    # print(sum(tjf_lyam.values()))
    print(get_user_id_for_staff_user_based_on_full_name("Sundstedt Sanna"))
    pass
    # print(get_tjf_for_enhet(enheter=["655", "656"], month=1))
    # print(get_tjf_for_enhet(enheter=["655", "656"], month=1))
    # set_tjf_sum_on_staff(user_id="lyadol", month=1, summa=0.0)

# set_tjf_month_okflagg(user_id="lyadol", month=10)
# update_staff_user(user_id="sarqva",
#                   first_name="Sara",
#                   last_name="Qvarnström",
#                   pnr12="197307190525",
#                   email="Sara.Qvarnstrom@utb.linkoping.se",
#                   titel="Rektor")
