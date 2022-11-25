""" allt som har med fasit hanteringen i databasen att göra"""
from functools import cache

from CustomErrors import GearNotFoundError, NoUserFoundError
from database.models import FasitCopy, Staff_dbo
from database.mysql_db import MysqlDb
from sqlalchemy import and_, or_

from utils.dbutil.student_db import update_student_examen_year
from utils.file_utils.fasit_file import load_fasit_csv
from utils.flatten import flatten_list, flatten_row
from utils.my_now import now_date


def get_fasit_row(name: str) -> FasitCopy:
    """ Hämta fasit rad från databasen"""
    s = MysqlDb().session()
    return s.query(FasitCopy).filter(FasitCopy.name == name).first()


def load_fasit_to_db() -> None:
    """ Ladda in fasit informationen till databasen"""
    df = load_fasit_csv()
    # print(df)
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
                attribute_senast_inloggade=extract_cb_student_user_ids_login_list(row['attribute.senast_inloggade']),
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
            fasit_item.attribute_senast_inloggade = extract_cb_student_user_ids_login_list(row['attribute.senast_inloggade'])
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
    translate_fasit_name_to_eunomia_name()
    update_staff_from_fasit_file()


def create_fasit_staff_user_ids() -> None:
    """ Skapar eunomia koppling till användarnamn för personalen"""
    s = MysqlDb().session()
    fasit_staff = s.query(FasitCopy).filter(FasitCopy.tag_person == 1).all()
    for staff in fasit_staff:
        staffer = s.query(Staff_dbo).filter(Staff_dbo.user_id == staff.attribute_anvandarnamn).first()
        if staffer is not None:
            staffer
    # s.commit()


@cache
def extract_cb_student_user_ids_login_list(senast_inloggade: str) -> str:
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


def get_user_id_for_fasit_user(attribute_anvandare: str) -> str:
    """ Hämta user_id för fasit användare
    Dolk Lyam -> lyadol
    """
    s = MysqlDb().session()
    user = s.query(FasitCopy).filter(FasitCopy.name == attribute_anvandare).first()
    if user is not None:
        return user.attribute_anvandarnamn  # user_id i FASIT
    else:
        raise NoUserFoundError(f"Kunde inte hitta användare med attribute_anvandare: {attribute_anvandare}")


def update_staff_from_fasit_file() -> None:
    """ Uppdateriar personal tabellen utifrån fasit filen"""
    s = MysqlDb().session()
    old_staff = flatten_row(list(s.query(Staff_dbo.user_id).all()))
    print("old_staff", old_staff)
    fasit_staff = s.query(FasitCopy).filter(FasitCopy.tag_person == 1).all()
    for f_staff in fasit_staff:
        if f_staff.attribute_anvandarnamn in old_staff:
            old_staff.remove(f_staff.attribute_anvandarnamn)
        staffer = s.query(Staff_dbo).filter(Staff_dbo.user_id == f_staff.attribute_anvandarnamn).first()
        if staffer is not None:  # hittades
            staffer.full_name = f_staff.name
            staffer.email = f_staff.attribute_epost
            staffer.title = f_staff.attribute_jobbtitel
            staffer.domain = "linkom"
            if f_staff.attribute_faktura.startswith("Folkunga"):
                staffer.skola = "Folkungaskolan"
            elif f_staff.attribute_faktura.startswith("St"):
                staffer.skola = "St:Lars"
            else:
                staffer.skola = "okänd"
        else:  # hittades inte så skapa ny
            if f_staff.attribute_faktura.startswith("Folkunga"):
                skola = "Folkungaskolan"
            elif f_staff.attribute_faktura.startswith("St"):
                skola = "St:Lars"
            else:
                skola = "okänd"
            s.add(Staff_dbo(user_id=f_staff.attribute_anvandarnamn,
                            full_name=f_staff.name,
                            domain="linkom",
                            email=f_staff.attribute_epost,
                            titel=f_staff.attribute_jobbtitel
                            ))
    s.commit()
    if len(old_staff) > 0:
        print(f"Följande användare finns {old_staff}")
        mark_staffer_as_old(old_staff)


def mark_staffer_as_old(old_staff: list[str]) -> None:
    """ Markera en lista med personer som gamla
    old_staff lista med user_id
    exv ["lyadol"]
    """
    s = MysqlDb().session()
    for old_user_id in old_staff:
        old_staffer = s.query(Staff_dbo).filter(Staff_dbo.user_id == old_user_id).first()
        if not old_staffer.domain.startswith("old"):  # sabba inte om det redan är old markerat
            old_staffer.domain = f"old|" + now_date()
            print(F"Markera {old_user_id} som gammal")
    s.commit()


def translate_fasit_name_to_eunomia_name() -> str:
    """ Skriv in användarnamn istället för attribut användare för kända användare"""
    s = MysqlDb().session(echo=True)
    utdelad_utrustning = s.query(FasitCopy).filter(FasitCopy.attribute_anvandare != None).all()
    for named_gear in utdelad_utrustning:
        print(F"named_gear: {named_gear.name} attribute_anvandare: {named_gear.attribute_anvandare}")
    # s.commit()


def delete_stupid_info_in_fasit() -> None:
    """ Tar bort onödig info i fasit kopieringen"""
    s = MysqlDb().session(echo=False)
    found = s.query(FasitCopy).filter(or_(FasitCopy.tag_plats == 1
                                          # ,FasitCopy.tag_rcard == 1
                                          )
                                      ).all()
    for f in found:
        print(F"named_gear: {f.name} attribute_anvandare: {f.attribute_anvandare}")
        f.delete()
    f.commit()


if __name__ == "__main__":
    # delete_stupid_info_in_fasit()
    print(get_user_id_for_fasit_user("Dolk Lyam"))
    update_staff_from_fasit_file()
    # translate_fasit_name_to_eunomia_name()
    # create_fasit_staff_user_ids()
    # add_update_cmd_line(name="E52076", cmd="update", new_value="test1") # lägg på något som behöver uppdateras
    # get_needed_web_updates() # lista allt som behöver uppdateras i web versionen
