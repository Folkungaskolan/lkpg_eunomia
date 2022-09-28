""" Funktioner assosierade med manipulering av FASIT"""
import pandas as pd
import requests

from settings.URLs import FASIT_CSV_URL

test_csv_respons = '''
sep=	
"name"	"color"	"unmanaged"	"status"	"attribute.adress"	"attribute.användare"	"attribute.användarnamn"	"attribute.byggnad"	"attribute.delad"	"attribute.domän"	"attribute.elev"	"attribute.elev_epost"	"attribute.epost"	"attribute.faktura"	"attribute.fakturakod"	"attribute.faktureras_ej"	"attribute.fasit_admin"	"attribute.fasit_admin_html"	"attribute.hyresperiodens_slut"	"attribute.imei"	"attribute.it_kontakt"	"attribute.jobbtitel"	"attribute.klass"	"attribute.kund"	"attribute.kundnummer"	"attribute.mobilnummer"	"attribute.modell"	"attribute.mottagare_av_faktura"	"attribute.mottagare_av_fakturaspecifikation"	"attribute.noteringar"	"attribute.plats"	"attribute.senast_inloggade"	"attribute.senast_online"	"attribute.serienummer"	"attribute.servicestatus"	"attribute.servicestatus_full"	"attribute.skola"	"attribute.tillverkare"	"attribute.tjänster"	"attribute.återlämningsdatum"	"tag.anknytning"	"tag.användare"	"tag.chromebook"	"tag.chromebox"	"tag.dator"	"tag.domän"	"tag.faktura"	"tag.funktionskonto"	"tag.kund"	"tag.mobiltelefon"	"tag.pekplatta"	"tag.person"	"tag.plats"	"tag.rcard"	"tag.skrivare"	"tag.skärm"	"tag.tv"	"tag.utrustning"	"tag.videoprojektor"
"2053"	""	""	""	""	"Riccono Rebecca"	""	""	""	""	""	""	""	"Folkungaskolan gy; Faktura 1"	""	"false"	""	""	""	""	""	""	""	""	"655"	"0730689792"	""	""	""	""	"FOLKUNGAGATAN 20"	""	""	""	""	""	""	""	""	""	"1"	""	""	""	""	""	""	""	""	""	""	""	""	""	""	""	""	"1"	""
"2006"	""	""	""	""	"Borg Matilda"	""	""	""	""	""	""	""	"Folkungaskolan gy; Faktura 1"	""	"false"	""	""	""	""	""	""	""	""	"655"	"0730314992"	""	""	""	""	"FOLKUNGAGATAN 20"	""	""	""	""	""	""	""	""	""	"1"	""	""	""	""	""	""	""	""	""	""	""	""	""	""	""	""	"1"	""
'''


def download_fasit_csv_from_web() -> pd.DataFrame:
    """ Hämtar en csv fil med all fasit information"""
    r = requests.get(FASIT_CSV_URL)
    if r.status_code == 200:
        print(r.text)
    else:
        raise ValueError("could not download csv")


# TODO Skriv hä

if __name__ == "__main__":
    # download_fasit_csv_from_web()
    print(test_csv_respons)
