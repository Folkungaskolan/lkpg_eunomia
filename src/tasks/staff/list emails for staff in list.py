""" hämtar personal i lista och skriver ut email adresserna  """
from database.models import Staff_dbo
from database.mysql_db import MysqlDb

if __name__ == "__main__":
    anv_list = ["ceccel", "larkri", "lineks", "berulr", "antlun", "micwel", "gorsch", "sustil", "flowen", "riclon", "jonwoo", "gunlua", "marwil", "chrcle"]
    s = MysqlDb().session()
    staff_list = s.query(Staff_dbo).filter(Staff_dbo.user_id.in_(anv_list)).all()
    for staff in staff_list:
        print(staff.email, end=";")
