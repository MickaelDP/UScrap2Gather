import os
import sys
from pathlib import Path


# load config setting
def load_config(dictionary, file):
    path = os.path.join(Path.home(), ".scrap/" + file)
    if os.path.exists(path):
        pass
    else:
        file = open(path, "w")
        file.write("NbrProfil\t1\n")
        file.write("NbrDataSet\t1\n")
        file.close()
    try:
        with open(path, 'r') as flux:
            for line in flux.readlines():
                conf = line.replace("\n", "").split("\t")
                try:
                    dictionary[conf[0]] = conf[1]
                except IndexError:
                    print(f'{path}: Missing information for the field: {line}')
    except FileNotFoundError:
        sys.exit(3)
