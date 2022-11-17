""" allt som har med fasit hanteringen i databasen att göra"""
from functools import cache

from CustomErrors import GearNotFoundError
from database.models import FasitCopy, Staff_dbo
from database.mysql_db import MysqlDb
from sqlalchemy import and_

from utils.file_utils.fasit_file import load_fasit_csv
from utils.student.student_mysql import update_student_examen_year


def load_fasit_to_db() -> None:
    """ Ladda in fasit informationen till databasen"""
    df = load_fasit_csv()
    print(df)
    df = df.fillna(0, inplace=False)
    s = MysqlDb().session()

    for index, row in df.iterrows():
        fasit_item = s.query(FasitCopy).filter(FasitCopy.name == row["name"]).first()
        if fasit_item is None:
            fasit_item = FasitCopy(
                name=row['name'],
                color=row['color'],
                unmanaged=row['unmanaged'],
                status=row['status'],
                attribute_adress=row['attribute.adress'],
                attribute_anvandare=row['attribute.användare'],
                attribute_anvandarnamn=row['attribute.användarnamn'],
                attribute_byggnad=row['attribute.byggnad'],
                attribute_delad=row['attribute.delad'],
                attribute_domain=row['attribute.domän'],
                attribute_elev=row['attribute.elev'],
                attribute_elev_epost=row['attribute.elev_epost'],
                attribute_epost=row['attribute.epost'],
                attribute_faktura=row['attribute.faktura'],
                attribute_fakturakod=row['attribute.fakturakod'],
                attribute_faktureras_ej=row['attribute.faktureras_ej'],
                attribute_fasit_admin=row['attribute.fasit_admin'],
                attribute_fasit_admin_html=row['attribute.fasit_admin_html'],
                attribute_hyresperiodens_slut=row['attribute.hyresperiodens_slut'],
                attribute_it_kontakt=row['attribute.it_kontakt'],
                attribute_jobbtitel=row['attribute.jobbtitel'],
                attribute_klass=row['attribute.klass'],
                attribute_kund=row['attribute.kund'],
                attribute_kundnummer=row['attribute.kundnummer'],
                attribute_mobilnummer=row['attribute.mobilnummer'],
                attribute_modell=row['attribute.modell'],
                attribute_mottagare_av_faktura=row['attribute.mottagare_av_faktura'],
                attribute_mottagare_av_fakturaspecifikation=row['attribute.mottagare_av_fakturaspecifikation'],
                attribute_noteringar=row['attribute.noteringar'],
                attribute_plats=row['attribute.plats'],
                attribute_senast_inloggade=extract_cb_student_userids_login_list(row['attribute.senast_inloggade']),
                attribute_senast_online=row['attribute.senast_online'],
                attribute_serienummer=row['attribute.serienummer'],
                attribute_servicestatus=row['attribute.servicestatus'],
                attribute_servicestatus_full=row['attribute.servicestatus_full'],
                attribute_skola=row['attribute.skola'],
                attribute_tillverkare=row['attribute.tillverkare'],
                attribute_tjanster=row['attribute.tjänster'],
                attribute_aterlamnings_datum=row['attribute.återlämningsdatum'],
                tag_anknytning=row['tag.anknytning'],
                tag_anvandare=row['tag.användare'],
                tag_chromebook=row['tag.chromebook'],
                tag_chromebox=row['tag.chromebox'],
                tag_dator=row['tag.dator'],
                tag_domain=row['tag.domän'],
                tag_faktura=row['tag.faktura'],
                tag_funktionskonto=row['tag.funktionskonto'],
                tag_kund=row['tag.kund'],
                tag_mobiltelefon=row['tag.mobiltelefon'],
                tag_pekplatta=row['tag.pekplatta'],
                tag_person=row['tag.person'],
                tag_plats=row['tag.plats'],
                tag_rcard=row['tag.rcard'],
                tag_skrivare=row['tag.skrivare'],
                tag_skarm=row['tag.skärm'],
                tag_tv=row['tag.tv'],
                tag_utrustning=row['tag.utrustning'],
                tag_videoprojektor=row['tag.videoprojektor']
            )
            s.add(fasit_item)
        else:
            fasit_item.color = row['color']
            fasit_item.unmanaged = row['unmanaged']
            fasit_item.status = row['status']
            fasit_item.attribute_adress = row['attribute.adress']
            fasit_item.attribute_anvandare = row['attribute.användare']
            fasit_item.attribute_anvandarnamn = row['attribute.användarnamn']
            fasit_item.attribute_byggnad = row['attribute.byggnad']
            fasit_item.attribute_delad = row['attribute.delad']
            fasit_item.attribute_domain = row['attribute.domän']
            fasit_item.attribute_elev = row['attribute.elev']
            fasit_item.attribute_elev_epost = row['attribute.elev_epost']
            fasit_item.attribute_epost = row['attribute.epost']
            fasit_item.attribute_faktura = row['attribute.faktura']
            fasit_item.attribute_fakturakod = row['attribute.fakturakod']
            fasit_item.attribute_faktureras_ej = row['attribute.faktureras_ej']
            fasit_item.attribute_fasit_admin = row['attribute.fasit_admin']
            fasit_item.attribute_fasit_admin_html = row['attribute.fasit_admin_html']
            fasit_item.attribute_hyresperiodens_slut = row['attribute.hyresperiodens_slut']
            fasit_item.attribute_it_kontakt = row['attribute.it_kontakt']
            fasit_item.attribute_jobbtitel = row['attribute.jobbtitel']
            fasit_item.attribute_klass = row['attribute.klass']
            fasit_item.attribute_kund = row['attribute.kund']
            fasit_item.attribute_kundnummer = row['attribute.kundnummer']
            fasit_item.attribute_mobilnummer = row['attribute.mobilnummer']
            fasit_item.attribute_modell = row['attribute.modell']
            fasit_item.attribute_mottagare_av_faktura = row['attribute.mottagare_av_faktura']
            fasit_item.attribute_mottagare_av_fakturaspecifikation = row['attribute.mottagare_av_fakturaspecifikation']
            fasit_item.attribute_noteringar = row['attribute.noteringar']
            fasit_item.attribute_plats = row['attribute.plats']
            fasit_item.attribute_senast_inloggade = extract_cb_student_userids_login_list(row['attribute.senast_inloggade'])
            fasit_item.attribute_senast_online = row['attribute.senast_online']
            fasit_item.attribute_serienummer = row['attribute.serienummer']
            fasit_item.attribute_servicestatus = row['attribute.servicestatus']
            fasit_item.attribute_servicestatus_full = row['attribute.servicestatus_full']
            fasit_item.attribute_skola = row['attribute.skola']
            fasit_item.attribute_tillverkare = row['attribute.tillverkare']
            fasit_item.attribute_tjanster = row['attribute.tjänster']
            fasit_item.attribute_aterlamnings_datum = row['attribute.återlämningsdatum']
            fasit_item.tag_anknytning = row['tag.anknytning']
            fasit_item.tag_anvandare = row['tag.användare']
            fasit_item.tag_chromebook = row['tag.chromebook']
            fasit_item.tag_chromebox = row['tag.chromebox']
            fasit_item.tag_dator = row['tag.dator']
            fasit_item.tag_domain = row['tag.domän']
            fasit_item.tag_faktura = row['tag.faktura']
            fasit_item.tag_funktionskonto = row['tag.funktionskonto']
            fasit_item.tag_kund = row['tag.kund']
            fasit_item.tag_mobiltelefon = row['tag.mobiltelefon']
            fasit_item.tag_pekplatta = row['tag.pekplatta']
            fasit_item.tag_person = row['tag.person']
            fasit_item.tag_plats = row['tag.plats']
            fasit_item.tag_rcard = row['tag.rcard']
            fasit_item.tag_skrivare = row['tag.skrivare']
            fasit_item.tag_skarm = row['tag.skärm']
            fasit_item.tag_tv = row['tag.tv']
            fasit_item.tag_utrustning = row['tag.utrustning']
            fasit_item.tag_videoprojektor = row['tag.videoprojektor']
            fasit_item.eunomia_user_id = None
    s.commit()
    create_fasit_student_user_ids()
    update_student_examen_year()


def create_fasit_staff_user_ids() -> None:
    """ skapar eunomia koppling till användarnamn för peronsalen"""
    s = MysqlDb().session()
    fasit_staff = s.query(FasitCopy).filter(FasitCopy.tag_person == 1).all()
    for staff in fasit_staff:
        staffer = s.query(Staff_dbo).filter(Staff_dbo.user_id == staff.attribute_anvandarnamn).first()
        if staffer is not None:
            staffer
    # s.commit()


@cache
def extract_cb_student_userids_login_list(senast_inloggade: str) -> str:
    """ Drar ut bara användarnamnen från senast inloggade strängen"""
    if senast_inloggade == 0:
        return ""
    emails = senast_inloggade.split(',')
    user_ids = []
    for email in emails:
        user_ids.append(email.split('@')[0])
    return '|'.join(user_ids)


def create_fasit_student_user_ids():
    """Uppdaterar databsen för eleverna för enklare hämtning av user_id"""
    s = MysqlDb().session()
    cbs = s.query(FasitCopy).filter(and_(FasitCopy.eunomia_user_id == None,
                                         FasitCopy.attribute_elev_epost != None
                                         )).all()
    for cb in cbs:
        cb.eunomia_user_id = cb.attribute_elev_epost.split('@')[0]
    s.commit()


def add_update_cmd_line(name: str, cmd: str, new_value: str = "") -> None:
    """ Lägger till commandosträngen till fasit raden för behandling vid uppdatering av web versionen"""
    print("add_update_cmd_line", name, cmd, new_value)
    s = MysqlDb().session()
    fasit_row = s.query(FasitCopy).filter(FasitCopy.name == name).first()
    if fasit_row is not None:
        if fasit_row.eunomia_update_web_command is None or len(fasit_row.eunomia_update_web_command) < 2:
            fasit_row.eunomia_update_web_command = F"{cmd}>{new_value}"
        else:
            fasit_row.eunomia_update_web_command = fasit_row.eunomia_update_web_command + "|" + F"{cmd}>{new_value}"
    else:
        raise GearNotFoundError(f'Gear {name} not found in fasit copy db')
    s.commit()


def get_needed_web_updates() -> list[dict[str:str]]:
    """Hämtar alla rader som behöver uppdateras i web versionen"""
    s = MysqlDb().session()
    cbs = s.query(FasitCopy).filter(FasitCopy.eunomia_update_web_command != None).all()
    todo_list = []
    for cb in cbs:
        if cb.eunomia_update_web_command is None or len(cb.eunomia_update_web_command) < 2:
            continue
        for cmd_set in cb.eunomia_update_web_command.split("|"):
            cmd, new_value = cmd_set.split(">")
            todo_list.append({"name": cb.name, "cmd": cmd, "new_value": new_value})
            print(F"CB:{cb.name} commands: {cmd}, new_value: {new_value}")
    return todo_list


if __name__ == "__main__":
    # create_fasit_staff_user_ids()
    # add_update_cmd_line(name="E52076", cmd="update", new_value="test1")
    get_needed_web_updates()
