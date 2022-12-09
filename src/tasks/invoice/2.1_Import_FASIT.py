""" Importera senaste Fasit data till fakturor """
from utils.dbutil.fasit_db import load_fasit_to_db

if __name__ == '__main__':
    load_fasit_to_db(verbose=True)