from sqlalchemy.orm import Session

from CustomErrors import DBUnableToCrateUser
from db.models import Staff_dbo
from db.mysql_db import init_db
from utils.pnr_utils import pnr10_to_pnr12


def get_staff_user_from_db_based_on_user_id(user_id: str, session: Session = None, create_on_missing: bool = False) \
        -> (Staff_dbo, Session):
    """ Get a user from the db. """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    staff = local_session.query(Staff_dbo).filter_by(user_id=user_id).first()
    if staff is None and create_on_missing:  # if user does not exist, create it
        session = create_staff_user_from_user_id(user_id=user_id, session=local_session)
        staff = local_session.query(Staff_dbo).filter_by(user_id=user_id).first()
        if staff is None:
            raise DBUnableToCrateUser("Could not create user                            2022-10-11 10:59:36")

    if session is not None:
        return staff, local_session
    return staff, local_session


def create_staff_user_from_user_id(user_id: str, session: Session = None) -> Session:
    """ Insert a user into the db. """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    staff = Staff_dbo(user_id=user_id)
    local_session.add(staff)
    local_session.commit()
    if session is not None:
        return local_session


def print_user(user_id: str, session: Session = None) -> Session:
    """ Print a user from the db. """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    staff = local_session.query(Staff_dbo).filter_by(user_id=user_id).first()
    print(staff)
    print(type(staff))
    if session is not None:
        return local_session


def delete_user(user_id: str, session: Session = None) -> Session:
    """ Delete a user from the db. """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    staff = local_session.query(Staff_dbo).filter_by(user_id=user_id).first()
    local_session.delete(staff)
    local_session.commit()

    if session is not None:
        return local_session


def update_staff_user(user_id: str,
                      first_name: str = None,
                      last_name: str = None,
                      pnr12: str = None,
                      email: str = None,
                      domain: str = "linkom",
                      session: Session = None,
                      titel: str = None) -> Session:
    """ Update a user in the db. """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    staff = local_session.query(Staff_dbo).filter_by(user_id=user_id).first()
    if staff is None:  # if user does not exist, create it
        session = create_staff_user_from_user_id(user_id=user_id, session=local_session)
        staff = local_session.query(Staff_dbo).filter_by(user_id=user_id).first()
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
    local_session.commit()
    if session is not None:
        return local_session


if __name__ == '__main__':
    pass

    # update_staff_user(user_id="sarqva",
    #                   first_name="Sara",
    #                   last_name="Qvarnström",
    #                   pnr12="197307190525",
    #                   email="Sara.Qvarnstrom@utb.linkoping.se",
    #                   titel="Rektor")
