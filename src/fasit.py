"""FASIT casher"""

import pandas as pd

from settings.folders import FASIT_CSV_FILEPATH


class Fasit():
    """agearar cashe for fasit"""

    def __init__(self):
        self.__df = pd.read_csv(FASIT_CSV_FILEPATH, sheet_name="FASIT", dtype=str)
        # TODO Load Fasit csv fil

    def get_owner_for_gear(self, gear: str) -> str:
        """Return owner for gear"""
        return "owner"


if __name__ == "__main__":
    f = Fasit()
