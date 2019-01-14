import argparse
import os
from json import load
import re
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from collections import OrderedDict
import numpy as np
from uncertainties import ufloat_fromstr,unumpy as unp
from pdf2image import convert_from_path
from scipy.optimize import curve_fit
from scipy import odr
from fitter.fit_functions import quadraticPolynomial
from matplotlib.ticker import FuncFormatter
import matplotlib
import matplotlib.image as mpimg
from support.directoryManager import cd
import shutil

from res.conf_file_str import *

def get_val(dictionary: dict, key: str, default_value=None):
    if key in dictionary.keys():
        try:
            return ufloat_fromstr(dictionary[key]).nominal_value
        except (ValueError, AttributeError) as e:
            return dictionary[key]
    else:
        return default_value

parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to be analyzed", type=str)

args = parser.parse_args()

path = f"{args.path}"

tar_list = []

reg_id = re.compile(r"APO_(\d+)")
for path, sub_path, files in os.walk(path):
    if "results.json" in files:

        kic_id = reg_id.findall(path)[0]

        with open(f"{path}/results.json", 'r') as f:
            data_dict = load(f)

        f_fit = get_val(data_dict["Full Background result"], "$f_\\mathrm{max}$ ")
        evidence = get_val(data_dict, "Conclusion")

        if evidence != "Strong evidence":
            continue

        im_path = f"{path}/images/PSD_full_fit_{kic_id}_.png"

        tmp_dict = {}
        tmp_dict["id"] = kic_id
        tmp_dict["f_fit"] = f_fit
        tmp_dict["evidence"] = evidence
        tmp_dict["im_path"] = im_path
        tar_list.append(tmp_dict)

try:
    os.mkdir("filtered_result")
except:
    shutil.rmtree("filtered_result")
    os.mkdir("filtered_result")

with cd("filtered_result"):
    os.mkdir("30-40")
    os.mkdir("40-50")
    os.mkdir("50-60")
    os.mkdir("60-70")
    os.mkdir("70-80")

for i in tar_list:
    if 30 < i["f_fit"] < 40:
        tar_dir = "30-40"
    elif 40 < i["f_fit"] < 50:
        tar_dir = "40-50"
    elif 50 < i["f_fit"] < 60:
        tar_dir = "50-60"
    elif 60 < i["f_fit"] <70:
        tar_dir = "60-70"
    elif 70 < i["f_fit"] < 80:
        tar_dir = "70-80"
    else:
        continue

    with cd(f"filtered_result/{tar_dir}"):
        fig = pl.figure(figsize=(10,6))
        pl.axis('off')
        img = mpimg.imread(i["im_path"])
        pl.imshow(img)
        pl.title(i["id"])
        pl.text(0.5,-0.1,f"nu_max = {i['f_fit']}, evidence = {i['evidence']}")
        pl.savefig(f"{i['id']}.png")
        pl.close(fig)




