""" läs in FASIT datat TILL DATABASEN"""
from utils.dbutil.fasit_db import load_fasit_to_db, update_staff_from_fasit_file

if __name__ == '__main__':
    load_fasit_to_db()
