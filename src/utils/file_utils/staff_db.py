from sqlalchemy.orm import Session

from CustomErrors import DBUnableToCrateUser
from database.models import Staff_dbo
from database.mysql_db import init_db, MysqlDb
from utils.pnr_utils import pnr10_to_pnr12


def get_staff_user_from_db_based_on_user_id(user_id: str, create_on_missing: bool = False) -> Staff_dbo:
    """ Get a user from the database. """
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


if __name__ == '__main__':
    pass

    # update_staff_user(user_id="sarqva",
    #                   first_name="Sara",
    #                   last_name="Qvarnström",
    #                   pnr12="197307190525",
    #                   email="Sara.Qvarnstrom@utb.linkoping.se",
    #                   titel="Rektor")
