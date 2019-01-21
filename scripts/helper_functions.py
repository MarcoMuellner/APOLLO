import os
from json import load
from typing import Dict,List,Tuple
from uncertainties import ufloat_fromstr
from shutil import rmtree

f_max = "$f_\\mathrm{max}$ "

full_background = "Full Background result"


def load_results(path : str,ignore_list : List[str] = None) -> List[Tuple[str,Dict,Dict]]:
    """
    Loads result files and conf files for a given path
    :param path: input path
    :return: List containing this values
    """
    res_list = []
    cnt = 0
    for path,sub_path,files in  os.walk(path):
        if 'results.json' not in files or 'conf.json' not in files:
            continue

        cnt +=1

        if "ignore.txt" in files:
            continue

        try:
            if len([i for i in ignore_list if i in files]) != 0:
                continue
        except:
            pass

        with open(f"{path}/results.json") as f:
            result = load(f)

        with open(f"{path}/conf.json") as f:
            conf = load(f)

        res_list.append((path,result,conf))

    print(f"Total: {cnt}")
    return res_list

def get_val(dictionary: dict, key: str, default_value=None):
    if key in dictionary.keys():
        try:
            return ufloat_fromstr(dictionary[key])
        except (ValueError, AttributeError) as e:
            return dictionary[key]
    else:
        return default_value

def recreate_dir(dir : str):
    try:
        rmtree(dir)
    except:
        pass

    try:
        os.makedirs(dir)
    except:
        pass

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)
