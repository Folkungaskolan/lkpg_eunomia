""" Hjälp funktioner för faktura hanteringen"""


def normalize(tjf: dict[str, float]) -> dict[str, float]:
    """ Normalisera fördelningar så de summerar till 1"""
    s = sum(dict.values(tjf))
    for key, value in tjf.items():
        tjf[key] = value / s
    return tjf
