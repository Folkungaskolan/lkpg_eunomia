""" Skapa text med nuvarande datum och tid """

import datetime


def now_date():
    """ Skapa text med nuvarande datum och tid """
    return datetime.datetime.now().strftime("%Y-%m-%d")


def now_time():
    """ Skapa text med nuvarande datum och tid """
    return datetime.datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    print(now_date())
