import os
from collections import deque
from pathlib import Path

import pandas as pd

from CustomErrors import VariableNotFoundError
from settings.folders import BASE_OBSIDIAN_PATH
from settings.folders import OBSIDIAN_LINX_SEPARATOR
from utils.path_utils import split_filename_from_filepath

# Pandas Options
pd.set_option('display.max_columns', 50)
pd.set_option('display.expand_frame_repr', False)


def get_folder_files(path: str, file_extension: str = None) -> list:  # TODO rewrite to use pathlib
    """
    Returns a list of files in a folder
    :param path:
    :param file_extension:
    :return:
    """
    if file_extension is None:
        return os.listdir(path)
    else:
        return [f for f in os.listdir(path) if f.endswith('. ' + file_extension)]


def get_file_lines_as_list(filepath: str) -> list:
    """ Returns a list of lines in a file """
    f = open(filepath, "r")
    lines = f.read().splitlines()
    f.close()
    # print(lines)
    return lines


def order_variables(lines) -> list:
    """ Orders the variables in a file """
    header_lines = []
    body_lines = []
    link_lines = []
    for line in lines:
        if "---" in line:
            continue
        elif ": " in line:
            header_lines.append(line)
        elif OBSIDIAN_LINX_SEPARATOR in line:
            link_lines.append(line)
        else:
            body_lines.append(line)
    ordered_list = ["---"]
    if header_lines:
        for line in header_lines:
            ordered_list.append(line)
    ordered_list.append("---")
    if link_lines:
        for line in link_lines:
            ordered_list.append(line)

    if body_lines:
        for line in body_lines:
            ordered_list.append(line)

    return ordered_list


def write_lines_to_file(filepath: str, lines: list):
    """ Writes a list of lines to a file """
    lines = order_variables(lines)
    Path(filepath).parent.mkdir(exist_ok=True, parents=True)
    with open(filepath, 'w') as f:
        for line in lines:
            f.write(str(line))
            f.write('\n')
        f.close()
    print(f"Lines Writen to file {filepath}")


def check_variable_value(path_to_file: str, variable_name: str, check_value: str) -> tuple[bool, str]:
    """
    Checks if a variable in a file has a specific value
    :param path_to_file:
    :param variable_name:
    :param check_value:
    :return:
    """

    try:
        files_current_value = extract_variable_value(path_to_file=path_to_file, variable_name=variable_name)
    except VariableNotFoundError as e:
        raise VariableNotFoundError from e
    else:
        if files_current_value == check_value:
            return True, files_current_value
        else:
            return False, files_current_value


def extract_variable_value_from_filepath(path_to_file: str, variable_name: str) -> str:
    """ given a list of lines and a variable name, returns the value of the variable """
    try:
        lines = get_file_lines_as_list(path_to_file)
    except FileNotFoundError as e:
        raise FileNotFoundError from e
    else:
        for line in lines:
            if "::" in line:
                line_parts = line.split("::")
                if line_parts[0].lower() == variable_name.lower():
                    return line_parts[1].strip()
            elif ":" in line:
                line_parts = line.split(":")
                if line_parts[0].lower() == variable_name.lower():
                    return line_parts[1].strip()
    raise VariableNotFoundError(f"Variable {variable_name} not found in file {path_to_file}")


def extract_variable_value_from_gear_name(gear_name: str, variable_name: str) -> str:
    """ given a gear name and a variable name, returns the value of the variable """
    gear_filepath = find_gear_file(gear_name=gear_name)
    return extract_variable_value_from_filepath(path_to_file=gear_filepath, variable_name=variable_name)


def create_variable_with_value(path_to_file: str, variable_name: str, variable_new_value: str) -> None:
    """ Creates a variable with a value in a file """
    print(F"create_variable_with_value started for variable : {variable_name} ")
    try:
        lines = get_file_lines_as_list(path_to_file)
    except FileNotFoundError as e:
        raise FileNotFoundError from e
    else:
        new_lines = []
        dash_counter = 0
        for line in lines:
            print(line)
            if "---" in line:
                dash_counter += 1
                if dash_counter > 1:
                    new_lines.append(variable_name + ":  " + variable_new_value)
            new_lines.append(line)
        if dash_counter == 0:
            new_lines = deque(new_lines)
            new_lines.appendleft("---")
            new_lines.appendleft(variable_name + ":  " + variable_new_value)
            new_lines.appendleft("---")
            new_lines = list(new_lines)

        write_lines_to_file(filepath=path_to_file, lines=new_lines)
        print(F"Variable {variable_name} with value {variable_new_value} in created in {path_to_file}")


def create_barebones_file(path_to_file: str) -> None:
    """ Skapar en tom fil med bara --- i början och slutet """
    lines = ["---", "---"]
    write_lines_to_file(filepath=path_to_file, lines=lines)
    print(F"Barebones file created {path_to_file}")


def set_variable_value(path_to_file: str, variable_name: str, variable_new_value: str) -> None:
    """ given a file, sets the value of the variable to a value in that file"""
    print(
        F"START set_variable_value| path: {path_to_file} | variable_name : {variable_name} | variable value: {variable_new_value} ")
    try:
        change_needed = check_variable_value(path_to_file, variable_name=variable_name,
                                             check_value=variable_new_value)
    except VariableNotFoundError:
        print("VariableNotFoundError")
        create_variable_with_value(path_to_file=path_to_file, variable_name=variable_name,
                                   variable_new_value=variable_new_value)
        return
    except FileNotFoundError as e:
        print("FileNotFoundError")
        print(e)

        create_barebones_file(path_to_file)
        create_variable_with_value(path_to_file=path_to_file, variable_name=variable_name,
                                   variable_new_value=variable_new_value)
        return
    else:
        if change_needed:
            try:
                lines = get_file_lines_as_list(path_to_file)
            except FileNotFoundError:
                print("FileNotFoundError")
            else:
                # print(lines)
                new_lines = []
                for line in lines:
                    if "::" in line:
                        line_parts = line.split("::")
                        if line_parts[0].lower() == variable_name.lower():
                            line_parts[1] = variable_new_value
                            line = line_parts[0] + line_parts[1]
                            new_lines.append(line)
                    elif ":" in line:
                        line_parts = line.split(":")
                        if line_parts[0].lower() == variable_name.lower():
                            line_parts[1] = variable_new_value
                            line = line_parts[0] + ": " + line_parts[1]
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                # print(new_lines)
                write_lines_to_file(filepath=path_to_file, lines=new_lines)


def download_fasit_csv_file():
    """ Downloads the Fasit csv file and saves it to the fasit folder """
    # print(fasit_path)
    # driver = init_chrome_webdriver(headless_bool=False, enable_file_download_redirect=True)
    # driver.get("https://onify.linkoping.se/workspace/fasit/export?term=*&export=csv")
    # print("testing")
    pass


def parse_fasit_csv_to_df(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath, skiprows=1, encoding="latin-1", sep="\t")


def add_link_to_file(path_to_file: str, new_link_name: str) -> None:
    pass


def numeric_to_str_fixer(value: str) -> str:
    value = value.split(".")[0]
    return value


def parse_anknytningar_from_df(df: pd.DataFrame) -> None:
    subfolder = "Anknytningar/"
    # Användbara columner
    df = df[["name", "attribute.mobilnummer", "attribute.användare", "attribute.kundnummer", "attribute.plats",
             "tag.anknytning"]]
    # Användbara rader
    df = df[df["tag.anknytning"] == 1]
    # Konvertera columner till korrekt typ ?
    print("......")
    print(df.head())
    print(df.dtypes)
    df = df.astype({"attribute.kundnummer": str, "tag.anknytning": str})

    df["attribute.kundnummer"] = df["attribute.kundnummer"].apply(numeric_to_str_fixer)
    df["tag.anknytning"] = df["tag.anknytning"].apply(numeric_to_str_fixer)
    print(df.dtypes)
    print(df.head())
    print("......")
    for label, row_df in df.iterrows():
        print(label, row_df)
        print(F"{row_df['attribute.mobilnummer']} is type {type(row_df['attribute.mobilnummer'])}'")
        if isinstance(row_df['attribute.mobilnummer'], float):
            # print("row is nan")
            set_variable_value(path_to_file=os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"),
                               variable_name="Stationary_phone", variable_new_value="True")
            add_link_in_category(path_to_file=os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"),
                                 link_category="categori_länkar", new_link_name="Stationary_phone")
        if isinstance(row_df['attribute.mobilnummer'], str):
            # print("row is mobilnummer")
            set_variable_value(os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"),
                               "kuntet_mobilnummer", row_df['attribute.mobilnummer'])
            add_link_in_category(path_to_file=os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"),
                                 link_category="categori_länkar", new_link_name="Mobil_anknytning")
        set_variable_value(os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"), "kundnummer",
                           row_df['attribute.kundnummer'])
        set_variable_value(os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"), "plats",
                           row_df['attribute.plats'])
    print(df.columns)
    print(df)


def set_cb_senaste_elev_lista(path_to_file: str, senaste_elev_lista: list) -> None:
    """ Sets the variable 'senaste_elev_lista' in the file 'path_to_file' to the value 'senaste_elev_lista' """
    student_linx = []
    for email in senaste_elev_lista.split(","):
        student_linx.append(F"[[{email.split('@')[0]}]]")
    print(student_linx)
    for elev in student_linx:
        add_link_in_category(path_to_file=path_to_file,
                             link_category="Senaste_inloggade_elever",
                             new_link_name=elev,
                             sort=False)


def parse_chromebooks_from_df(df):
    subfolder = "Chromebooks/"
    # Användbara columner
    use_cols = ["name", "color", "status", "attribute.byggnad", "attribute.elev", "attribute.hyresperiodens_slut",
                "attribute.kundnummer", "attribute.modell", "attribute.plats", "attribute.senast_inloggade",
                "attribute.senast_online",
                "attribute.serienummer", "attribute.servicestatus", "attribute.servicestatus_full", "attribute.skola",
                "attribute.tillverkare", "tag.chromebook"]
    col_variablename = {"color": "color",
                        "status": "CBA_status",
                        "attribute.byggnad": "byggnad",
                        "attribute.elev": "hos_elev",
                        "attribute.hyresperiodens_slut": "hyresperiodens_slut",
                        "attribute.kundnummer": "kundnummer",
                        "attribute.modell": "modell",
                        "attribute.plats": "plats",
                        "attribute.senast_online": "senast_online",
                        "attribute.serienummer": "serienummer",
                        "attribute.servicestatus": "servicestatus",
                        "attribute.servicestatus_full": "servicestatus_full",
                        "attribute.skola": "skola",
                        "attribute.tillverkare": "tillverkare"}

    df = df[use_cols]
    # Användbara rader
    df = df[df["tag.chromebook"] == 1]
    df = df[df["name"].isin(["C09791", "C10188"])]
    # Konvertera columner till korrekt typ ?
    print("......")
    print(df.head())
    print(df.dtypes)
    df = df.astype({"attribute.kundnummer": str})
    df["attribute.kundnummer"] = df["attribute.kundnummer"].apply(numeric_to_str_fixer)
    print(df.dtypes)
    print(df.head())
    print("......")
    print(col_variablename.keys())
    print("**************")
    for label, row_df in df.iterrows():
        print(label, list(row_df))
        # set_variable_value(os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"), "kuntet_mobilnummer", row_df['attribute.mobilnummer'])
        add_link_in_category(path_to_file=os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"),
                             link_category="categori_länkar", new_link_name="Chromebook")
        for col_var in col_variablename.keys():
            print(f"key: {col_var}")
            print(f"name: {col_variablename[col_var]}")
            save_variable_based_on_nan(df=row_df, df_column_name=col_var, subfolder=subfolder,
                                       filename=F"{row_df['name']}.md", variable_name=col_variablename[col_var])
        set_cb_senaste_elev_lista(path_to_file=os.path.join(BASE_OBSIDIAN_PATH, subfolder, F"{row_df['name']}.md"),
                                  senaste_elev_lista=row_df["attribute.senast_inloggade"])


def save_variable_based_on_nan(df: pd.DataFrame, df_column_name: str, subfolder: str, filename: str, variable_name: str,
                               value_when_nan: str = "") -> None:
    df = df.apply(str)
    print(
        F"df_column_name: {df_column_name} | subfolder: {subfolder} | filename: {filename} | variable_name: {variable_name} | value_when_nan:{value_when_nan}")
    print(F"actual value:  {df[[df_column_name]]}")
    is_nan: bool = isinstance(df[df_column_name], float)
    is_str: bool = isinstance(df[df_column_name], str)
    print(F"is nan: {is_nan}")
    print(F"is str: {is_str}")
    print(F"type of {df_column_name} = {type(df[df_column_name])} ")
    if is_nan:
        print("nan")
        set_variable_value(os.path.join(BASE_OBSIDIAN_PATH, subfolder, filename), variable_name, value_when_nan)
    if is_str:
        print("str")
        set_variable_value(os.path.join(BASE_OBSIDIAN_PATH, subfolder, filename), variable_name, df[df_column_name])
    print(F"------ finished : df_column_name: {df_column_name}")


def add_link_in_category(path_to_file: str,
                         link_category: str,
                         new_link_name: str,
                         sort: bool = True,
                         only_one_value_in_category: bool = False) -> None:
    """
    sort: bool default = False:
            Sortera länkar i kategorin?
            False För exv senaste användarna, där ordning spelar roll
            True för kategori länkar där ordning inte spelar roll
    only_one_value_in_category: bool default = False:
            Spara bara en länk i kategorin -> Current User
    """
    try:
        lines = get_file_lines_as_list(path_to_file)
    except FileNotFoundError as e:
        create_barebones_file(path_to_file)
        add_link_in_category(path_to_file=path_to_file, link_category=link_category, new_link_name=new_link_name)
    else:
        new_lines = []
        link_category_found = False
        for line in lines:
            if link_category + OBSIDIAN_LINX_SEPARATOR in line and not link_category_found:
                link_category_found = True
                if only_one_value_in_category:  # spara bara en länk i kategorin -> Current User
                    new_lines.append(F"{link_category + OBSIDIAN_LINX_SEPARATOR} [[{new_link_name}]]")
                else:
                    line_parts = line.split(OBSIDIAN_LINX_SEPARATOR)
                    links = line_parts[1].strip().split(";")
                    links = [l.strip() for l in links if len(l) > 0]
                    for link in links:
                        if new_link_name == link.replace("[", "").replace("]", ""):
                            return  # lin finns redan -> inget behöver göras
                    links.append(F"[[{new_link_name}]]")
                    if sort:
                        links = sorted(links)
                    new_lines.append(f"{link_category + OBSIDIAN_LINX_SEPARATOR} " + ";".join(links))
                continue
            new_lines.append(line)
        if not link_category_found:
            new_lines.append(F"{link_category + OBSIDIAN_LINX_SEPARATOR} [[{new_link_name}]]")

        write_lines_to_file(filepath=path_to_file, lines=new_lines)


def update_obsidian_gear_from_fasit() -> None:
    download_fasit_csv_file()
    df = parse_fasit_csv_to_df("/downloads/fasit.csv")
    # parse_anknytningar_from_df(df=df)
    parse_chromebooks_from_df(df)


def find_gear_file(gear_name: str) -> str:
    """ Returnerar sökväg till filen som innehåller gear_name """
    filelist = list(Path(BASE_OBSIDIAN_PATH).rglob('**/*.md'))
    for filepath in filelist:
        # print(f"filename = {split_filename_from_filepath(filepath)}")
        if gear_name in split_filename_from_filepath(filepath):
            return str(filepath)
    raise FileNotFoundError(f"Could not find file for {gear_name} in Obsidian")


def find_gear_kontering_file(gear_name: str) -> str:
    """ Returnerar sökväg till filen som innehåller gear_name """
    filepath: str = find_gear_file(gear_name=gear_name)
    return extract_variable_value(filepath, "kontering")


if __name__ == "__main__":
    print(extract_variable_value_from_gear_name(gear_name="5629", variable_name="kontering"))
    # update_obsidian_gear_from_fasit()
#     TODO complete rework needed
