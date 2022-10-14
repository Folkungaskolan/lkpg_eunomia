""" funktioner som jobbar med personnummer"""
import datetime


def only_numerics(seq):
    """ Returnerar enbart numeriska värden """
    seq_type = type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))


def is_valid_pnr12(pnr12: str) -> bool:
    """Kontrollerar att personnumret med 12 siffor är giltigt"""
    pnr12 = pnr12.strip()
    pnr12 = only_numerics(seq=pnr12)
    if pnr12[0:2] not in ["19", "20"]:
        return False
    return is_valid_pnr10(pnr12[2:])


def is_valid_pnr10(pnr10):
    """Kontrollerar att personnumret med 10 siffor är giltigt"""
    pnr10 = pnr10.strip()
    pnr10 = only_numerics(seq=pnr10)
    if len(pnr10) != 12:
        return False
    if not pnr10.isdigit():
        return False
    if pnr10[0:2] not in ["19", "20"]:
        return False
    if int(pnr10[2:4]) > 12:
        return False
    if int(pnr10[4:6]) > 31:
        return False
    return check_pnr_control_digit(pnr10)


def check_pnr_control_digit(pnr10: str) -> bool:
    """Kontrollerar kontrollsiffran i ett 10-siffrigt personnummer"""
    return True


def calc_pnr12(pnr10: str) -> str:
    """Beräknar ett 12-siffrigt personnummer från ett 10-siffrigt"""
    # if not is_valid_pnr10(pnr10):
    #     raise ValueError("Felaktigt personnummer")
    min_age = 17
    this_year = datetime.date.today().year
    rolloveryear = str(this_year - min_age)  # year to roll over to next century
    pnr12 = ""
    if int(pnr10[:2]) < int(rolloveryear[2:4]):
        pnr12 += "20"
    else:
        pnr12 += "19"
    pnr12 += pnr10[0:2]
    pnr12 += pnr10[2:4]
    pnr12 += pnr10[4:6]
    pnr12 += pnr10[6:8]
    pnr12 += pnr10[8:10]
    return pnr12


if __name__ == "__main__":
    print(calc_pnr12("0109269034"))
    print(calc_pnr12("0209269034"))
    print(calc_pnr12("0309269034"))
    print(calc_pnr12("0409269034"))
    print(calc_pnr12("0509269034"))
    print(calc_pnr12("0609269034"))
    print(calc_pnr12("7709269034"))

    pass
