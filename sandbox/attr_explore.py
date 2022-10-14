""" listar ut hur attr funkar"""
from dataclasses import dataclass


class A:
    id: str
    name: str
    _pnr12: str

    def __setattr__(self, key, value):
        if key == "pnr10":
            self._pnr12 = 19 + value
        if key == "pnr12":
            self._pnr12 = value

    def __getattr__(self, item):
        if item == "pnr10":
            return self._pnr12[2:]
        if item == "pnr12":
            return self._pnr12


# a = A()
# a.id = "123"
# a.name = "Kalle"
# a._pnr12 = "197709269034"
# print(a.pnr12)
# print(a.pnr10)
#
# a.pnr10 = "1234567890"
#
# print(a.pnr10)

# Dataclasses

@dataclass(frozen=False, order=True)
class ABC:
    """ dataclass ABC. """
    id: str
    name: str
    pnr12: str


b = ABC("123", "Kalle", "197709269034")
setattr(b, "id", "1234")
print(b)
