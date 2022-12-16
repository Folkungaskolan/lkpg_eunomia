""" Enum för Någon kombination av enheter som har eget namn"""

from enum import Enum


class EnhetsAggregering(Enum):
    """Enum for enheter to split over"""
    ALLA = "ALLA"
    CB = "CB"  # Alla som har Chromebooks
    F_GY = "F_GY"
    GRU = "GRU"
    GRU4_6 = "GRU4_6"
    GRU7_9 = "GRU7_9"
    STL = "STL"


class FakturaRadState(Enum):
    """Enum for faktura rad state"""
    # Keep going
    SPLIT_INCOMPLETE = "SPLIT_INCOMPLETE"
    # Outcomes
    SPLIT_BY_FASIT_KONTERING_SUCCESSFUL = "SPLIT_BY_FASIT_KONTERING_SUCCESSFUL"
    SPLIT_BY_FASIT_USER_SUCCESSFUL = "SPLIT_BY_FASIT_USER_SUCCESSFUL"
    SPLIT_BY_ELEVANTAL_SUCCESSFUL = "SPLIT_BY_ELEVANTAL_SUCCESSFUL"
    SPLIT_BY_GENERELL_TFJ_SUCCESSFUL = "SPLIT_BY_GENERELL_TFJ_SUCCESSFUL"
    SPLIT_BY_FAILSAFE_METHOD_SUCCESSFUL = "SPLIT_BY_FAILSAFE_METHOD_SUCCESSFUL"


class Skola(Enum):
    """Enum for skola"""
    FOLKUNGA = "FOLKUNGA"
    ST_LARS = "ST_LARS"


class Months(Enum):
    """Enum for months"""
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12


if __name__ == '__main__':
    print(EnhetsAggregering.ALLA)
    print(EnhetsAggregering.ALLA.value)
    print(EnhetsAggregering("ALLA"))
    var = "ALLA"
    print(EnhetsAggregering(var))
