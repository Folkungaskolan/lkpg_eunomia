""" Import av faktura filer """
import re
from pathlib import Path

import pandas as pd
from sqlalchemy.sql.elements import and_

from database.models import FakturaRad_dbo
from database.mysql_db import init_db
from settings.folders import FAKTURA_EXCEL_FAKTURA_RADER_FOLDER
from utils.print_progress_bar import print_progress_bar


def import_invoice_file() -> None:
    """ importera en faktura fil """
    filelist = list(Path(FAKTURA_EXCEL_FAKTURA_RADER_FOLDER).rglob('*.[Xx][Ll][Ss][Xx]'))
    for filepath in filelist:
        df = pd.read_excel(filepath, usecols="A:J", sheet_name="Sheet1")
        # print(df.columns)
        # print(df.dtypes)
        df = df.astype({"Avser": "str", 'Pris': "str", 'Summa': "str", 'Antal': "int"})
        # print(df.dtypes)
        # print(df)
        local_session = init_db()

        list_length = len(df.index)
        print_progress_bar(0, list_length, prefix='Staff Export Progress:', suffix='Complete', length=50)
        for index, row in df.iterrows():
            # if index > 5:
            #     break
            if index % 100 == 0:
                print_progress_bar(iteration=index + 1, total=list_length,
                                   prefix=F'Staff  Export Progress:{index}/{list_length}  ', suffix='Complete',
                                   length=50)
            period = str(row["Period"])
            faktura_year = int(period.split("-")[0])
            faktura_month = int(period.split("-")[1])
            # if "IT-Bastjänst Extra Lagring Std" not in row["Tjänst"] or faktura_month != 8:
            #     continue
            try:
                if row["Pris"].startswith("−"):
                    pris = -float(re.sub("[^0123456789,.]", "", row["Pris"]).replace(",", "."))
                else:
                    pris = float(re.sub("[^0123456789,.]", "", row["Pris"]).replace(",", "."))

                if row["Summa"].startswith("−"):
                    summa = -float(re.sub("[^0123456789,.]", "", row["Summa"]).replace(",", "."))
                else:
                    summa = float(re.sub("[^0123456789,.]", "", row["Summa"]).replace(",", "."))
            except ValueError:
                print(f"Error: {row}")
                continue
            local_session.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.avser == row["Avser"],
                                                            FakturaRad_dbo.avser == faktura_month,
                                                            FakturaRad_dbo.avser == faktura_year
                                                            )
                                                       ).first()

            f_rad = FakturaRad_dbo(tjanst=row['Tjänst'],
                                   kundnummer=row['Kundnummer'],
                                   faktura_year=faktura_year,
                                   faktura_month=faktura_month,
                                   fakturamarkning=row['Fakturamärkning'],
                                   fakturakod=row['Fakturakod'],
                                   anvandare=row['Användare'],
                                   avser=row['Avser'],
                                   antal=row['Antal'],
                                   pris=pris,
                                   summa=summa)
            # print(f_rad)
            # print("----------------------")
            local_session.add(f_rad)
        local_session.commit()


if __name__ == "__main__":
    pd.set_option('display.max_columns', 75)
    pd.set_option('display.expand_frame_repr', False)
    import_invoice_file()
