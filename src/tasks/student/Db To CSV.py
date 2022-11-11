""" write the csv file for keys and passwords """
from utils.file_utils.excel import write_student_csv_from_mysql

if __name__ == '__main__':
    write_student_csv_from_mysql()
