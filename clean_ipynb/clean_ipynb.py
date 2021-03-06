from json import dump, load
from shutil import copyfile

from .clean_julia_code import clean_julia_code
from .clean_python_code import clean_python_code
from .has_julia_and_juliaformatter import has_julia_and_juliaformatter


def clean_ipynb(ipynb_file_path, overwrite):
    if not overwrite:
        ipynb_file_path = copyfile(
            ipynb_file_path, ipynb_file_path.replace(".ipynb", ".cleaned.ipynb")
        )

    with open(ipynb_file_path) as io:

        ipynb_dict = load(io)

    language = ipynb_dict["metadata"].get('language_info', {}).get('name', None)
    isColabNotebook = ipynb_dict["metadata"].get("colab") 

    if language == "python" or language == "ipython" or  isColabNotebook is not None:

        clean_code = clean_python_code

    elif language == "julia" and has_julia_and_juliaformatter():

        clean_code = clean_julia_code
        
    else:

        return

    cells = []

    for cell_dict in ipynb_dict["cells"]:

        if "execution_count" in cell_dict:
            cell_dict["execution_count"] = None
       
        if "outputs" in cell_dict:
            cell_dict["outputs"] = []

        if "metadata" in cell_dict:
            if "jupyter" in cell_dict["metadata"] and "source_hidden" in cell_dict["metadata"]["jupyter"]:
                cell_dict["metadata"]["jupyter"].pop("source_hidden")

            if cell_dict["metadata"].get("solution2", "hidden") == "shown":
                cell_dict["metadata"]["solution2"] = "hidden"

        if cell_dict["cell_type"] == "code":
            cell_content = "".join(cell_dict["source"])
            if not any(sql_m in cell_content for sql_m in ['%%sql', '%sql']):

                source_join_clean_split = clean_code(
                    cell_content
                ).splitlines()

                if len(source_join_clean_split) == 1 and source_join_clean_split[0] == "":
                    continue

                source_join_clean_split[:-1] = [
                    "{}\n".format(line) for line in source_join_clean_split[:-1]
                ]

                cell_dict["source"] = source_join_clean_split

        cells.append(cell_dict)

    ipynb_dict["cells"] = cells

    with open(ipynb_file_path, mode="w") as io:

        dump(ipynb_dict, io, indent=1)

        io.write("\n")
