""" Hjälp funktioner för elev hantering"""
from database.models import Student_dbo
from database.mysql_db import MysqlDb


def get_klass_for_student(*, user_id: str) -> str:
    """ Returnerar klass för eleven """
    s = MysqlDb().session()
    student = s.query(Student_dbo).filter(Student_dbo.user_id == user_id).first()
    return student.klass


def get_id_komplement_pa_for_student(*, user_id: str) -> list[str]:
    """ Returnerar enheten som eleven är kopplad till """
    klass = get_klass_for_student(user_id=user_id)
    return decode_klass_to_id_komplement_pa(klass_namn=klass)


def decode_klass_to_id_komplement_pa(klass_namn: str) -> list[str]:
    """ Returnerar enheten som klass är kopplad till
    :type klass_namn: str
    """
    klass_namn: str = klass_namn.lower()
    if "fol" in klass_namn.lower():
        if klass_namn.startswith("ek"):
            return ["655119"]  #: GY_AKTIVITER,  # GY EK
        elif klass_namn.startswith("es"):
            return ["655123"]  # : GY_AKTIVITER,  # GY ES
        elif klass_namn.startswith("sa"):
            return ["655122"]  # : GY_AKTIVITER,  # GY SA
        elif klass_namn.startswith(("4", "5", "6")):
            if klass_namn.endswith("fol1"):  # hanterar 4_fol1 -> EK ES rektorns år fyra grupp
                return ["655119", "655123"]
            if klass_namn.endswith("fol2"):  # hanterar 4_fol2 -> SA rektorns år fyra grupp
                return ["655122"]
            return ["656510"]  #: GRU_AKTIVITER,  # GRU 4-6
        elif klass_namn.startswith(("7", "8", "9")):
            return ["656520"]  # : GRU_AKTIVITER,  # GRU 7-9
        else:
            raise ValueError(f"Klass {klass_namn} är inte kopplad till någon enhet")
    elif "stl" in klass_namn.lower():
        if klass_namn == "4_stl":               return ["654100", "654200", "654300", "654400"]
        elif klass_namn.startswith("es"):       return ["654100", "654200"]
        elif klass_namn.startswith("na"):       return ["654300"]
        elif klass_namn.startswith("ima"):      return ["654400"]
        else: raise ValueError(f"Klass {klass_namn} är inte kopplad till någon enhet")


def get_klasser_for_all_students():
    """ Returnerar klasser för alla elever """
    s = MysqlDb().session()
    klasser = s.query(Student_dbo.klass).distinct().all()
    return [klass[0] for klass in klasser]


if __name__ == '__main__':
    # print(get_id_komplement_pa_for_student(user_id="malmos795"))
    klasslist = get_klasser_for_all_students()
    for klass in klasslist:
        print(F"Klass {klass} är kopplad till enhet {decode_klass_to_id_komplement_pa(klass_namn=klass)}")
