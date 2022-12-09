""" Steg som behövs för att förbereda databasen för att kunna hantera fakturor"""

from utils.dbutil.kategori_db import update_kategorier_for_all_tables, copy_distinct_tjansts_to_tjanst_kategorisering, list_tjanst_with_no_info

if __name__ == '__main__':
    copy_distinct_tjansts_to_tjanst_kategorisering()
    list_tjanst_with_no_info()
    update_kategorier_for_all_tables()
