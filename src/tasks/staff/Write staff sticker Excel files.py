""" kör personalens data till excel fil"""

from utils.file_utils.excel import write_staff_xlsx_from_mysql

if __name__ == '__main__':
    write_staff_xlsx_from_mysql()
