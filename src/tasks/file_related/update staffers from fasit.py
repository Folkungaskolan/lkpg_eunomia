""" separerad körnings fil för ändamålet att uppdatera staff från fasit """
from utils.dbutil.fasit_db import update_staff_from_fasit_file

if __name__ == '__main__':
    update_staff_from_fasit_file()
