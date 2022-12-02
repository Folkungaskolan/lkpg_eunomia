""" Fixa en fin tabell """
from colorama import init, Fore, Back, Style

init(autoreset=True)
COL_WIDTHS = {"ID": 6,
              "Period": 7,  # how wide a col is
              "Tjänst": 20,
              "Avser": 20,
              "Summa": 12,
              "Fasit ägare": 12,
              "Fasit kontering": 20,
              "Tot Tjf": 12,
              "Elevantal": 12,
              "Summary": 12}


def print_headers():
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
    return h1


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
        if row_values[r] == "False" or row_values[r] is False:
            # str(row_values[r]).ljust(COL_WIDTHS[r])
            print(Fore.LIGHTBLACK_EX + str(row_values[r]).ljust(COL_WIDTHS[r]), end="")
            print("|", end="")
        elif row_values[r] == "Success" or row_values[r] is True:
            # str(row_values[r]).ljust(COL_WIDTHS[r])
            print(Fore.GREEN + str(row_values[r]).ljust(COL_WIDTHS[r]), end="")
            print("|", end="")
        elif row_values[r] == "Fail":
            # str(row_values[r]).ljust(COL_WIDTHS[r])
            print(Fore.RED + str(row_values[r]).ljust(COL_WIDTHS[r]) + '\033[0;0m', end="")
            print("|")
        else:
            print(Style.BRIGHT + str(row_values[r]).ljust(COL_WIDTHS[r]), end="")
            print("|", end="")
    print()


if __name__ == "__main__":
    print_headers()
    print_start(row_values={"ID": 1, "Period": "2022-9", "Tjänst": "Chromebooks", "Avser": "C12345", "Summa": 1012})
    print_result(row_values={"Fasit ägare": False, "Fasit kontering": True, "Tot Tjf": False, "Elevantal": False, "Summary": "Success"})

    # print(colored('hello', 'red'), colored('world', 'green'))
    # print('\033[2;31;43m CHEESY')
