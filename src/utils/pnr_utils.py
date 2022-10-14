""" funktioner som jobbar med personnummer"""


def is_valid_pnr12(pnr12: str) -> bool:
    """Kontrollerar att personnumret är giltigt"""
    pnr12 = pnr12.strip()
    if len(pnr12) != 12:
        return False
    if not pnr12.isdigit():
        return False
    if pnr12[0:2] not in ["19", "20"]:
        return False
    if int(pnr12[2:4]) > 12:
        return False
    if int(pnr12[4:6]) > 31:
        return False
    return True


if __name__ == "__main__":
    pass
