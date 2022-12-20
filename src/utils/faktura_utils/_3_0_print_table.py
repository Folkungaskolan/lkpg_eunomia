""" Fixa en fin tabell """
from colorama import init, Fore, Style

from database.models import FakturaRad_dbo
from utils.EunomiaEnums import FakturaRadState

init(autoreset=True)
COL_WIDTHS = {"ID": 6,
              "Period": 7,  # how wide a col is
              "Tjänst": 20,
              "Avser": 20,
              "Summa": 12,
              "Funktion försök": 30,
              # "Fasit ägare": 12,
              # "Fasit kontering": 20,
              # "Tot Tjf": 12,
              # "Elevantal": 12,
              "Summary": 12,
              "Aktivitet":15,
              "Status":40,
              "metod": 90}


def print_headers() -> None:
    """ Print header for the table. """
    header_D = {}
    h1 = ""
    tbl_h = ""
    for h in COL_WIDTHS.keys():
        header = h.ljust(COL_WIDTHS[h])
        h1 += header + "|"
        tbl_h += "-" * (len(header)) + "|"
    print(h1)
    print(tbl_h)
    return


def print_start(row_values: dict[str:str]):
    """
    Print a row for the table.
    colors by : https://pypi.org/project/colorama/
    """

    row = ""
    for r in row_values.keys():
        print(Style.BRIGHT + str(row_values[r]).ljust(COL_WIDTHS[r]), end="")
        print("|", end="")


def print_result(row_values: dict[str:str]):
    """
    Print a row for the table.
    colors by : https://pypi.org/project/colorama/
    """

    row = ""
    for r in row_values.keys():
        if row_values[r] == "Fail":
            # str(row_values[r]).ljust(COL_WIDTHS[r])
            print(Fore.RED + str(row_values[r]).ljust(COL_WIDTHS[r]) + '\033[0;0m', end="")
            print("|", end="")
        else:
            print(Style.BRIGHT + str(row_values[r]).ljust(COL_WIDTHS[r]), end="")
            print("|", end="")
    print()


def print_faktura_start(*, faktura_rad: FakturaRad_dbo) -> None:
    """ Skriver ut start delen av raden för fakturan"""
    print_start(row_values={"ID": faktura_rad.id,
                            "Period": F"{faktura_rad.faktura_year}-{faktura_rad.faktura_month}",
                            "Tjänst": faktura_rad.tjanst[:COL_WIDTHS["Tjänst"]],
                            "Avser": faktura_rad.avser[:COL_WIDTHS["Avser"]],
                            "Summa": faktura_rad.summa
                            })



def print_faktura_tail(faktura_rad: FakturaRad_dbo, function_name:str) -> None:
    """ Skriver ut resultat delen av raden för fakturan"""
    if faktura_rad.success():
        summary = "Success"
    else:
        summary = "Fail"
    print_result(row_values={"Funktion försök": function_name,
                             "Summary": summary,
                             "Aktivitet": faktura_rad.user_aktivitet_char,
                             "Status": faktura_rad.split_status,
                             "metod": faktura_rad.split_method_used})


def printfakturainfo(func):
    def wrapper(faktura_rad: FakturaRad_dbo) -> None:
        print_faktura_start(faktura_rad=faktura_rad)
        func(faktura_rad=faktura_rad)
        print_faktura_tail(faktura_rad=faktura_rad, function_name=func.__name__)
        return

    return wrapper


if __name__ == "__main__":
    print_headers()
    print_start(row_values={"ID": 1, "Period": "2022-9", "Tjänst": "Chromebooks", "Avser": "C12345", "Summa": 1012})
    print_result(row_values={"Fasit ägare": False, "Fasit kontering": True, "Tot Tjf": False, "Elevantal": False, "Summary": "Success", "split_string": "bla bla bla bla bla bla 123"})

    # print(colored('hello', 'red'), colored('world', 'green'))
    # print('\033[2;31;43m CHEESY')
