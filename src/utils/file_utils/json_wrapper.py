import json


def load_dict_from_json_path(filepath: str, verbose: bool = False) -> dict:  # DONE
    if verbose:
        print(F"loading{filepath}                                          2022-08-26 09:45:00")
    with open(filepath, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    fp.close()
    return data


if __name__ == '__main__':
    pass
