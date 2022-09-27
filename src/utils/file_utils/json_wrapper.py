"""
Funktioner som hanterar json filer
"""

import json


def load_dict_from_json_path(filepath: str, verbose: bool = False) -> dict:  # DONE
    """
    load a dict from a json file    # DONE
    :param filepath:
    :param verbose:
    :return:
    """
    if verbose:
        print(F"loading{filepath}                                          2022-09-27 08:46:39")
    with open(filepath, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    fp.close()
    return data


def save_dict_to_json(data: dict, filepath: str, verbose: bool = False) -> None:
    """
    save a dict to a json file, overwriting old file
    :param data: dict med användaruppgifter
    :param filepath: var filen ska sparas
    :param verbose: visa vad som händer
    :return:
    """

    if verbose:
        print(F"saving{filepath}                                          2022-09-27 08:46:32")
    with open(filepath, 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))
    fp.close()


if __name__ == '__main__':
    print(load_dict_from_json_path(filepath=r"H:\Min enhet\Python Students\2.students\test4_test1.json", verbose=True))
