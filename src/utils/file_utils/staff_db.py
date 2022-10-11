from sqlalchemy.orm import Session

from CustomErrors import DBUnableToCrateUser
from db.models import Staff
from db.mysql_db import init_db


def create_staff_user(user_id: str, session: Session = None) -> Session:
    """ Insert a user into the db. """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    staff = Staff(user_id=user_id)
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

    staff = local_session.query(Staff).filter_by(user_id=user_id).first()
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

    staff = local_session.query(Staff).filter_by(user_id=user_id).first()
    local_session.delete(staff)
    local_session.commit()

    if session is not None:
        return local_session


def update_user(user_id: str,
                first_name: str = None,
                last_name: str = None,
                pnr: str = None,
                email: str = None,
                domain: str = "linkom",
                session: Session = None) -> Session:
    """ Update a user in the db. """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    staff = local_session.query(Staff).filter_by(user_id=user_id).first()
    if staff is None:  # if user does not exist, create it
        session = create_staff_user(user_id=user_id, session=local_session)
        staff = local_session.query(Staff).filter_by(user_id=user_id).first()
        if staff is None:
            raise DBUnableToCrateUser("Could not create user                            2022-10-11 10:59:36")

    if first_name is not None:  # om värde skickas in uppdatera
        staff.first_name = first_name
    if last_name is not None:  # om värde skickas in uppdatera
        staff.last_name = last_name
    if pnr is not None:  # om värde skickas in uppdatera
        staff.pnr = pnr
    if email is not None:  # om värde skickas in uppdatera
        staff.email = email
    staff.domain = domain  # har alltid ett värde
    local_session.commit()
    if session is not None:
        return local_session


if __name__ == '__main__':
    pass
    update_user(user_id="lyadol2", first_name="Lyam2", last_name="Dolk2", pnr="0000000000")
