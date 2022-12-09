""" helper for class information """
from typing import Protocol


class ClassInformation(Protocol):
    """ Samla klass information """
    def __init__(self, klass: str, skola: str):
        self.klass = klass
        self.skola = skola


if __name__ == '__main__':
    pass