""" hanterar funktioner som gör något mot för studenter"""
import math
from datetime import datetime
from functools import cache

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.models import Student_dbo, StudentCount_dbo
from database.mysql_db import init_db
from utils.decorators import function_timer


@function_timer
@cache
def count_student(endast_id_komplement_pa: set[str] = None, month: int = None) -> tuple[dict[str, int], dict[str, float]]:
    """ Räknar elever i respektive klass i databasen och sparar dessa siffror samt returnerar dem
    return raw_total, relative_distribution
    """
    local_session = init_db()
    raw_total = {}
    relative_distribution = {}
    if month == datetime.now().month or month is None:
        slask = []
        klass_sum = local_session.query(Student_dbo.klass,
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
            id_count = local_session.query(StudentCount_dbo).filter(StudentCount_dbo.id_komplement_pa == key,
                                                                    StudentCount_dbo.month == datetime.now().month,
                                                                    StudentCount_dbo.year == datetime.now().year,
                                                                    ).first()
            if id_count is None:
                local_session.add(StudentCount_dbo(id_komplement_pa=key,
                                                   count=raw_total[key],
                                                   month=datetime.now().month,
                                                   year=datetime.now().year)
                                  )
            else:
                id_count.count = raw_total[key]
                id_count.month = datetime.now().month
                id_count.year = datetime.now().year
            local_session.commit()
    else:
        old_month_counts = local_session.query(StudentCount_dbo).filter(StudentCount_dbo.month == month).all()
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


def generate_split_on_student_count(year: int, month: int, enheter_to_split_over: set, session: Session = None) -> list[str:float] | tuple[list[str:float], Session]:
    """ Generera split på antal elever """
    if session is None:
        local_session = init_db()
    else:
        local_session = session

    alla_enheter = {"655119",  # Gy EK
                    "655122",  # Gy ES
                    "655123",  # Gy SA
                    "656510",  # 4-6
                    "656520",  # 7-9
                    "656310",  # Fritids

                    "654100",  # Stlars Es Musik
                    "654200",  # Stlars Es Bild
                    "654300",  # Stlars NA
                    "654400",  # Stlars IMA
                    }
    if enheter_to_split_over is None:
        enheter_to_split_over = alla_enheter
    if enheter_to_split_over == {"CB"}:
        enheter_to_split_over = {"655119",  # Gy EK
                    "655122",  # Gy ES
                    "655123",  # Gy SA
                    # "656510",  # 4-6
                    "656520",  # 7-9
                    # "656310",  # Fritids

                    "654100",  # Stlars Es Musik
                    "654200",  # Stlars Es Bild
                    "654300",  # Stlars NA
                    "654400",  # Stlars IMA
                    }
    if enheter_to_split_over == {"F_GY"}:
        enheter_to_split_over = {"655119",  # Gy EK
                                 "655122",  # Gy ES
                                 "655123",  # Gy SA
                                 }
    elif enheter_to_split_over == {"GRU"}:
        enheter_to_split_over = {"656510",  # 4-6
                                 "656520",  # 7-9
                                 "656310",  # Fritids
                                 }
    if any([True for enhet in enheter_to_split_over if enhet not in alla_enheter]):
        raise ValueError("Enhet finns inte i alla enheter")
    # hämta antal elever
    abs_distribution = {}
    rel_distribution = {}

    for enhet in enheter_to_split_over:
        enhet_student_count = local_session.query(StudentCount_dbo.count).filter(StudentCount_dbo.id_komplement_pa == enhet,
                                                                                 StudentCount_dbo.month == month,
                                                                                 StudentCount_dbo.year == year,
                                                                                 ).first()
        if enhet_student_count is None:
            raise ValueError(f"Kunde inte hitta antal elever för enhet: {enhet}")
        abs_distribution[enhet] = enhet_student_count[0]
    total = sum(abs_distribution.values())
    for key in abs_distribution.keys():
        rel_distribution[key] = abs_distribution[key] / total

    return rel_distribution, local_session


if __name__ == "__main__":
    split, x = generate_split_on_student_count(year=2022, month=11, enheter_to_split_over={"GY"})
    print(split)

