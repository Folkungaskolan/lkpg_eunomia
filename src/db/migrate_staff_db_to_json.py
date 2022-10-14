""" flytta medarbetare från db till json. """

from db.models import Staff_dbo
from db.mysql_db import init_db
from utils.file_utils.staff_files import save_staff_as_json


def move_staff_db_to_json() -> None:
    """ Move staff db in MySql to json. """
    session = init_db()
    all_staff = session.query(Staff_dbo).all()
    # all_staff = session.query(Staff_dbo).filter(or_(Staff_dbo.user_id == "janbor", Staff_dbo.user_id == "lyadol")).all()
    print(f"all_staff: {all_staff}")
    for staff in all_staff:
        print(staff.get_as_dict())
        if staff.user_id is None:
            continue
        if staff.u_created_date is None:
            u_create = ""
        else:
            u_create = staff.u_created_date.strftime("%Y-%m-%d %H:%M:%S")
        if staff.u_changed_date is None:
            u_change = ""
        else:
            u_change = staff.u_changed_date.strftime("%Y-%m-%d %H:%M:%S")
        save_staff_as_json(account_user_name=staff.user_id,
                           first_name=staff.first_name,
                           last_name=staff.last_name,
                           email=staff.email,
                           telefon=staff.telefon,
                           personnummer=staff._pnr12,
                           user_created=u_create,
                           user_last_changed=u_change,
                           domain=staff.domain,
                           titel=staff.titel
                           )
        print(f"{staff.user_id} Saved as json")


if __name__ == '__main__':
    move_staff_db_to_json()
