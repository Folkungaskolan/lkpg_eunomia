""" hämtar personal i lista och skriver ut email adresserna  """
from database.models import Staff_dbo
from database.mysql_db import init_db

if __name__ == "__main__":
    anv_list = ["ceccel", "larkri", "lineks", "berulr", "antlun", "micwel", "gorsch", "sustil", "flowen", "riclon", "jonwoo", "gunlua", "marwil", "chrcle"]
    local_session = init_db()
    staff_list = local_session.query(Staff_dbo).filter(Staff_dbo.user_id.in_(anv_list)).all()
    for staff in staff_list:
        print(staff.email, end=";")
