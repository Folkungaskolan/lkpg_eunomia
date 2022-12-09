import inspect
from functools import cache

from sqlalchemy import and_

from CustomErrors import DBUnableToCrateUser, NoUserFoundError, NoValidEnheterFoundError, ExtrapolationError, NoTjfFoundError
from database.models import Staff_dbo, Tjf_dbo
from database.mysql_db import MysqlDb, init_db
from statics.eunomia_date_helpers import MONTHS_NAMES, MONTHS_int_to_name
from utils.faktura_utils.normalize import normalize
from utils.pnr_utils import pnr10_to_pnr12


def get_staff_user_from_db_based_on_user_id(*, user_id: str, create_on_missing: bool = False, verbose: bool = False) -> Staff_dbo:
    """ Get a user from the database.
    lyadol -> Staff_dbo
    """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = init_db()

    staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
    if staff is None and create_on_missing:  # if user does not exist, create it
        staff = create_staff_user_from_user_id(user_id=user_id)
        staff.first_name = "unknown"
        staff.last_name = "unknown"
        staff.pnr12 = ""
        staff.email = ""
        staff.telefon = ""
        staff.skola = "unknown"
        staff.domain = "update_from_web"
        staff.titel = ""
        s.commit()
        staff = s.query(Staff_dbo).filter_by(user_id=user_id).first()
        if staff is None:
            raise DBUnableToCrateUser("Could not create user                            2022-10-11 10:59:36")
    return staff


def create_staff_user_from_user_id(user_id: str, verbose: bool = False) -> None:
    """ Insert a user into the database. """
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = init_db()
    staffer = Staff_dbo(user_id=user_id)
    s.add(staffer)
    s.commit()
    return staffer

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
def gen_tjf_for_staff(*, user_id: str, month_nr: str, verbose: bool = False) -> dict[str, float]:
    """ Genererar tjf för personalen """
    """ hämta tjänstefördelning för användaren för given månad"""
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    pnr12 = get_pnr_from_user_id(user_id=user_id)
    s = MysqlDb().session()
    tjf_s = s.query(Tjf_dbo).filter(Tjf_dbo.pnr12 == pnr12).all()
    if tjf_s is None:
        raise NoTjfFoundError(f"Kunde inte hitta tjf för användare med user_id: {user_id}")
    t = {}
    for tjf in tjf_s:
        exec(f"t[tjf.id_komplement_pa] = tjf.{MONTHS_int_to_name[month_nr]}")
    set_tjf_sum_on_staff(user_id=user_id, month_nr=month_nr, summa=sum(t.values()))
    if sum(t.values()) > 0:
        return normalize(tjf=t)
    else:
        if len(t.keys()) == 1:  # if its is 1 long there is only one enhet
            k = list(t.keys())[0]
            t[k] = 1
            return t
        else:
            extrapolation_list = []
            for id_komplement_pa in t.keys():
                extr_month, t[id_komplement_pa] = extrapolera_tjf_from_known_months_given_pnr12(pnr12=pnr12, id_komplement_pa=id_komplement_pa, month_nr=month_nr)
                extrapolation_list.append(extr_month)
            print(f"extrapolation_list: {extrapolation_list}")
            if len(set(extrapolation_list)) == 1:
                return normalize(tjf=t)
            else:
                raise ExtrapolationError(f"Kunde inte extrapolera tjf för {user_id} för månad {month_nr} då olika id gav olika extrapoleringar")


def set_tjf_sum_on_staff(user_id: str, month_nr: int, summa: float, verbose: bool = False) -> None:
    """ Uppdatera tjf_sum på staff för given månad"""
    if verbose:
        print(F"function start: {inspect.stack()[0][3]} called from {inspect.stack()[1][3]}")

    s = MysqlDb().session()
    staff = s.query(Staff_dbo).filter(Staff_dbo.user_id == user_id).first()
    exec(f"staff.sum_tjf_{MONTHS_int_to_name[month_nr]} = summa * 100")
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


def extrapolera_tjf_from_known_months_given_user_id(user_id: str, id_komplement_pa: str, month_nr: int, riktning: str = "ner") -> (int, float):
    """ wrapper för att skriva extrapoleringen via User_id """
    return extrapolera_tjf_from_known_months_given_pnr12(pnr12=get_pnr_from_user_id(user_id=user_id),
                                                         id_komplement_pa=id_komplement_pa,
                                                         month_nr=month_nr,
                                                         riktning=riktning)


def extrapolera_tjf_from_known_months_given_pnr12(pnr12: str, id_komplement_pa: str, month_nr: int, riktning: str = "ner") -> (int, float):
    """ Extrapolera tjf för personalen
     försöker först hitta tjf "tidigre" i tiden, om det inte finns så försöker den hitta "senare" i tiden
     """
    # print(f"{pnr12:}, {id_komplement_pa}, {month_nr:}")
    s = MysqlDb().session()
    if month_nr < 1:  # om vi gått hela vägen upp, och inte hittat ett värde att extrapolera med byt riktning
        return extrapolera_tjf_from_known_months_given_pnr12(pnr12=pnr12, id_komplement_pa=id_komplement_pa, month_nr=1, riktning="upp")
    if month_nr > 12:  # Inget hittat: returnera 0
        return 0.0
    tjf = s.query(Tjf_dbo).filter(and_(Tjf_dbo.pnr12 == pnr12, Tjf_dbo.id_komplement_pa == id_komplement_pa)).first()
    # print(tjf)
    # print(F'month nr: {month_nr}:{eval(F"tjf.{MONTHS_int_to_name[month_nr]}")}')

    if (eval(F"tjf.{MONTHS_int_to_name[month_nr]}") is None) or (eval(F"tjf.{MONTHS_int_to_name[month_nr]}") == 0):
        if riktning == "upp":
            new_month = month_nr + 1
        else:
            new_month = month_nr - 1
        return extrapolera_tjf_from_known_months_given_pnr12(pnr12=pnr12, id_komplement_pa=id_komplement_pa, month_nr=new_month)
    else:
        return month_nr, eval(F"tjf.{MONTHS_int_to_name[month_nr]}")


if __name__ == '__main__':
    # tjf_lyam = gen_tjf_for_staff(user_id="lyadol", faktura_rad=FakturaRad_dbo(faktura_month=10))
    # print(tjf_lyam)
    # print(tjf_lyam.values())
    # print(sum(tjf_lyam.values()))
    # print(get_user_id_for_staff_user_based_on_full_name("Sundstedt Sanna"))
    print(gen_tjf_for_staff(user_id="tilpal", month_nr=8))
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
