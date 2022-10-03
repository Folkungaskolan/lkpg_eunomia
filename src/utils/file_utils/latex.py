import os

import dask
import pandas as pd
from dask import delayed

os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'


def process_tex(filename: str, dir_path: str) -> str:
    # dir_path = "H:/Min enhet/LatexGen2/"
    os.system(f"pdflatex -quiet {filename}")
    os.remove(dir_path + filename)
    print(filename.split(".")[0])
    os.remove(dir_path + filename.split(".")[0] + ".log")
    os.remove(dir_path + filename.split(".")[0] + ".aux")
    return filename


def process_tex_to_pdf_in_folder(dir_path: str) -> None:
    os.chdir(dir_path)
    process_que = []
    for file in os.listdir(dir_path):
        if file.endswith(".tex"):
            print(os.path.join(dir_path, file))
            process_que.append(delayed(process_tex)(file, dir_path))
    # dask.visualize(process_que)
    files_run = dask.compute(process_que)
    print(files_run)


def generate_tex_for_class_from_csv(run_only_class: list[str] = None) -> None:
    # Pandas Options
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.expand_frame_repr', False)

    filepath = "H:/Min enhet/Python temp/u1_klass_user_info_pickles/Elever.csv"
    df = pd.read_csv(filepath, sep=";")  # first row is headers
    df["Klass"] = df["klass"].apply(lambda s: s.replace("_", "-"))
    print(df)
    # # print(elev_df.describe())

    # # print(elev_df.columns)
    # # print(elev_df.shape)
    # # print(elev_df)

    # # print(elev_df["Klass"])
    klasser_to_process = list(df["klass"].unique())
    klasser_to_process = [s for s in klasser_to_process if len(s) > 0]
    print("klasser_to_process")
    print(klasser_to_process)
    # print("Columns")
    # print(df.columns)
    # # print(df[df["Klass" == "7A_FOL14"]])
    latex_path = "H:/Min enhet/LatexGen/"
    for klass in klasser_to_process:
        # print(klass)
        if run_only_class is not None:
            if klass not in run_only_class:
                continue
        elever_i_klass_df = df[df["klass"] == klass].sort_values(by="anv_namn")
        row_in_page = 1
        with open(latex_path + F"{klass}_pw_epw_user_info_4_page.tex", "w") as f:
            # Preamble
            print(f"Creating klass:{klass} file")
            f.write(r"\documentclass{article}" + "\n")
            f.write(r"\usepackage{qrcode}" + "\n")
            f.write(r"\usepackage{multirow}" + "\n")
            f.write(r"\usepackage{fancyhdr}" + "\n")

            f.write("\n")
            f.write(r"\pagestyle{fancy}" + "\n")
            f.write(r"\fancyhf{}" + "\n")
            f.write(r"\fancyhfoffset[L]{1cm} " + "\n")
            f.write(r"\fancyhfoffset[R]{1cm} " + "\n")
            f.write(r"\lhead{\bfseries Klass " + klass + r"}" + "\n")
            f.write(r"\rfoot{\thepage}" + "\n")
            f.write(r"\begin{document}" + "\n")
            # end of Preamble
            for label, row_df in elever_i_klass_df.iterrows():
                # print(F' F: {row_df["Förnamn"]},  E:{row_df["Efternamn"]} ')
                f.write(r"\begin{tabular}{lr}" + "\n")
                f.write(r"&\multirow{4}{*}{\qrcode[height=1in]{" + row_df["anv_namn"] + r"}} \\" + "\n")
                f.write(f'Förnamn 	                       : {row_df["first_name"]}' + r"&  \\" + "\n")
                f.write(f'Efternamn 	                     : {row_df["last_name"]}' + r"&  \\" + "\n")
                f.write(f'------------------------------------------------------------------------------------' + r"&  \\" + "\n")
                f.write(f'Wifi användarnamn (obs UTAN edu) : {row_df["anv_namn"]}@linkoping.se' + r"&  \\" + "\n")
                f.write(f'Wifi/Eduroam  lösenord           : {row_df["edu_pw"]}' + r"&  \\" + "\n")
                f.write(f'------------------------------------------------------------------------------------' + r"&  \\" + "\n")
                f.write(f'Chromebook användarnamn (obs MED edu)         : {row_df["anv_namn"]}@edu.linkoping.se' + r"&  \\" + "\n")
                f.write(f'Chromebook lösenord:             : {row_df["pw"]}' + r"&  \\" + "\n")
                f.write(f'Klass     	                     : {klass} ' + r"&  \\" + "\n")
                f.write(r"\end{tabular}" + "\n\n\n")
                f.write(r"\bigskip \bigskip \bigskip" + "\n\n\n")
                if row_in_page % 4 == 0:
                    f.write(r"\pagebreak" + "\n")
                row_in_page += 1
            # end of doc
            f.write(r"\end{document}" + "\n")
            f.write("\n")
            f.close()


if __name__ == "__main__":
    pass
    # TODO: Complete rework needed

    # sum_subfolders(folder_path="H:/Min enhet/Python temp/u1_klass_user_info_pickles/")
    # generate_tex_for_class_from_csv(run_only_class=["7A_FOL15", "7B_FOL15", "7C_FOL15", "7D_FOL15", "7K_FOL15", "7M1_FOL15", "7M2_FOL15"])
    # process_tex_to_pdf_in_folder(r"H:/Min enhet/LatexGen/")
