""" hanterar funktioner som gör något mot för studenter"""
import math
from datetime import datetime
from functools import cache

from sqlalchemy import func, and_


from database.models import Student_dbo, StudentCount_dbo
from database.mysql_db import init_db, MysqlDb
from settings.enhetsinfo import ID_AKTIVITET, FOLKUNGA_GY_ENHETER, FOLKUNGA_GRU_ENHETER, ENHETER_SOM_HAR_CBS, STLARS_ENHETER
from utils.decorators import function_timer


@function_timer
@cache
def count_student(endast_id_komplement_pa: set[str] = None, month: int = None) -> tuple[dict[str, int], dict[str, float]]:
    """ Räknar elever i respektive klass i databasen och sparar dessa siffror samt returnerar dem
    return raw_total, relative_distribution
    """
    s = MysqlDb().session()
    raw_total = {}
    relative_distribution = {}
    if month == datetime.now().month or month is None:
        slask = []
        klass_sum = s.query(Student_dbo.klass,
                                        Student_dbo.skola,
                                        func.count(Student_dbo.klass).label("sum")
                                        ).group_by(Student_dbo.klass
                                                   ).all()
        for klass_obj in klass_sum:
            # print(klass)
            if "_FOL" in klass_obj.klass:  # FOLKUNGASKOLAN
                if klass_obj.klass.startswith("EK"):  # EK
                    raw_total["655119"] = raw_total.get("655119", 0) + klass_obj.sum
                elif klass_obj.klass.startswith("ES"):  # ES
                    raw_total["655123"] = raw_total.get("655123", 0) + klass_obj.sum
                elif klass_obj.klass.startswith("SA"):  # SA
                    raw_total["655122"] = raw_total.get("655122", 0) + klass_obj.sum
                elif klass_obj.skola in {"Folkungaskolan 5", "Folkungaskolan 6"}:  # 7-9
                    raw_total["656520"] = raw_total.get("656520", 0) + klass_obj.sum
                elif klass_obj.skola in {"Folkungaskolan 4"}:  # 4-6
                    raw_total["656510"] = raw_total.get("656510", 0) + klass_obj.sum
                continue
            elif "_STL" in klass_obj.klass:  # S:t Lars
                if klass_obj.klass.startswith("NA"):  # NA
                    raw_total["654300"] = raw_total.get("654300", 0) + klass_obj.sum
                elif klass_obj.klass.startswith("ES"):  # ES
                    raw_total["654100"] = raw_total.get("654100", 0) + math.ceil(klass_obj.sum / 2)  # TODO Fråga Maria H om detta är ok
                    raw_total["654200"] = raw_total.get("654200", 0) + math.ceil(klass_obj.sum / 2)
                elif klass_obj.klass.startswith("IMA"):  # IMA
                    raw_total["654400"] = raw_total.get("654400", 0) + klass_obj.sum
                continue
            slask.append(klass_obj.klass)  # om ingen tagit hand om klassen så lägger vi den i slasken
        print(F"slask klasser: {slask}")
        for key in raw_total.keys():
            id_count = s.query(StudentCount_dbo).filter(StudentCount_dbo.id_komplement_pa == key,
                                                                    StudentCount_dbo.month == datetime.now().month,
                                                                    StudentCount_dbo.year == datetime.now().year,
                                                                    ).first()
            if id_count is None:
                s.add(StudentCount_dbo(id_komplement_pa=key,
                                                   count=raw_total[key],
                                                   month=datetime.now().month,
                                                   year=datetime.now().year)
                                  )
            else:
                id_count.count = raw_total[key]
                id_count.month = datetime.now().month
                id_count.year = datetime.now().year
            s.commit()
    else:
        old_month_counts = s.query(StudentCount_dbo).filter(StudentCount_dbo.month == month).all()
        print(old_month_counts)
        for id_komplement_pa in old_month_counts:
            raw_total[id_komplement_pa.id_komplement_pa] = id_komplement_pa.count

    if endast_id_komplement_pa is not None:
        for k in list(raw_total.keys()):
            if k not in endast_id_komplement_pa:
                del raw_total[k]

    total = sum(raw_total.values())
    for key in raw_total.keys():
        relative_distribution[key] = raw_total[key] / total

    return raw_total, relative_distribution


def generate_split_on_student_count(year: int, month: int, enheter_to_split_over: set) -> list[str:float]:
    """ Generera split på antal elever """
    s = MysqlDb().session()

    alla_enheter = ID_AKTIVITET.keys()
    if enheter_to_split_over is None:
        enheter_to_split_over = alla_enheter
    elif enheter_to_split_over == {"CB"}:
        enheter_to_split_over = ENHETER_SOM_HAR_CBS
    elif enheter_to_split_over == {"F_GY"}:
        enheter_to_split_over = FOLKUNGA_GY_ENHETER
    elif enheter_to_split_over == {"GRU"}:
        enheter_to_split_over = FOLKUNGA_GRU_ENHETER
    elif enheter_to_split_over == {"STL"}:
        enheter_to_split_over = STLARS_ENHETER
    if any([True for enhet in enheter_to_split_over if enhet not in alla_enheter]):  # Kollar att enheterna vi fick finns i alla enheter
        raise ValueError("Enhet finns inte i alla enheter")

    abs_distribution = {}  # Variabel initiering
    rel_distribution = {}  # Variabel initiering

    # hämta antal elever
    for enhet in enheter_to_split_over:
        enhet_student_count = s.query(StudentCount_dbo.count).filter(StudentCount_dbo.id_komplement_pa == enhet,
                                                                                 StudentCount_dbo.month == month,
                                                                                 StudentCount_dbo.year == year,
                                                                                 ).first()
        if enhet_student_count is None:
            raise ValueError(f"Kunde inte hitta antal elever för enhet: {enhet}")
        abs_distribution[enhet] = enhet_student_count[0]
    total = sum(abs_distribution.values())
    for key in abs_distribution.keys():
        rel_distribution[key] = abs_distribution[key] / total

    return rel_distribution


if __name__ == "__main__":
    split, x = generate_split_on_student_count(year=2022, month=11, enheter_to_split_over={"GY"})
    print(split)
