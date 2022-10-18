""" Import av faktura filer """
from pathlib import Path

import pandas as pd

from settings.folders import FAKTURA_EXCEL_FAKTURA_RADER_FOLDER


def import_invoice_file() -> None:
    """ importera en faktura fil """
    filelist = list(Path(FAKTURA_EXCEL_FAKTURA_RADER_FOLDER).rglob('*.[Xx][Ll][Ss][Xx]'))
    for filepath in filelist:
        df = pd.read_excel(filepath, usecols="A:J", sheet_name="Sheet1")
        # print(df.columns)
        # print(df.dtypes)
        df = df.astype({"Avser": "str", 'Pris': "str", 'Summa': "str", 'Antal': "int"})
        print(df.dtypes)
        # print(df)
        # session = init_db()
        for index, row in df.iterrows():
            if "E38337" not in row["Avser"]:
                continue
            period = str(row["Period"])
            faktura_year = int(period.split("-")[0])
            faktura_month = int(period.split("-")[1])
            if row["Pris"].startswith("-"):
                pris = -float(row["Pris"].strip().replace("-", ""))
            else:
                pris = float(row["Pris"])
            print(F"pris:{pris}, row('Pris'):{row['Pris']}")
        # session.query(FakturaRad_dbo).filter(and_(FakturaRad_dbo.avser == row["Avser"],
        #                                           FakturaRad_dbo.avser == faktura_month,
        #                                           FakturaRad_dbo.avser == faktura_year
        #                                           )
        #                                      ).first()
        # print(F"Tjänst:{row['Tjänst']},Kundnummer:{row['Kundnummer']},Fakturamärkning:{row['Fakturamärkning']},Fakturakod:{row['Fakturakod']},Användare:{row['Användare']},Avser:{row['Avser']},Period:{row['Period']},Antal:{row['Antal']},Pris:{row['Pris']},Summa:{row['Summa']}")

        # f_rad = FakturaRad_dbo(tjanst=row['Tjänst'],
        #                        kundnummer=row['Kundnummer'],
        #                        faktura_year=faktura_year,
        #                        faktura_month=faktura_month,
        #                        fakturamarkning=row['Fakturamärkning'],
        #                        fakturakod=row['Fakturakod'],
        #                        anvandare=row['Användare'],
        #                        avser=row['Avser'],
        #                        antal=row['Antal'],
        #                        pris=float(row['Pris'].strip()),
        #                        summa=float(row['Summa']))
        # print(f_rad)
        #     session.add(f_rad)
        # session.commit()


if __name__ == "__main__":
    pd.set_option('display.max_columns', 75)
    pd.set_option('display.expand_frame_repr', False)
    import_invoice_file()
