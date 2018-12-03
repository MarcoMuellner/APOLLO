import argparse
import json
import os
from support.directoryManager import cd
from res.conf_file_str import internal_flag_worked,internal_literature_value
import matplotlib.pyplot as pl
import numpy as np
from shutil import copytree,rmtree
from scipy.optimize import curve_fit
from fitter.fit_functions import quadraticPolynomial


def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        rmtree(to_path)
    copytree(from_path, to_path)


parser = argparse.ArgumentParser()
parser.add_argument("path",help="The path to be analyzed",type=str)

args = parser.parse_args()

working_list = []

nu_max_guess = []
nu_max_literature = []
copy_list = []
running_list = []

for res_path in os.listdir(args.path):
    for result in os.listdir(args.path +res_path):
        if "results.json" == result:
            with cd(args.path +res_path):
                with open("results.json",'r') as f:
                    data = json.load(f)
                if internal_flag_worked in data.keys() and data[internal_flag_worked]:
                    id = res_path.split("_")[1]
                    working_list.append((res_path,int(id),float("%.2f"%data["Nu max guess"]),data[internal_literature_value]))
                    nu_max_guess.append(float("%.2f" % data["Nu max guess"]))
                    nu_max_literature.append(data[internal_literature_value])
                    copy_list.append((args.path +res_path,res_path))
                    running_list.append((int(id),data[internal_literature_value]))


for i in copy_list:
    copy_and_overwrite(i[0],f"working_apokasc/{i[1]}")

n_working = len(working_list)
n_total = len(os.listdir(args.path))
batch_yield = "%.1f"%(100*len(working_list)/len(os.listdir(args.path))) + "%"

print(f"Total working: {n_working}")
print(f"Total available: {n_total}")
print(f"Yield: {batch_yield}")

nu_max_guess = np.array(nu_max_guess)
nu_max_literature = np.array(nu_max_literature)

popt, _ = curve_fit(quadraticPolynomial, nu_max_literature, (nu_max_guess-nu_max_literature))
nu_max_new = nu_max_guess - quadraticPolynomial(nu_max_literature,*popt)

popt2, _ = curve_fit(quadraticPolynomial, nu_max_literature, nu_max_new)

print(f"Fitvalues: {popt}")
print(f"Standarddeviation: {(nu_max_new - nu_max_literature).std()}")

fig = pl.figure(figsize=(20,12))
ax1 = fig.add_subplot(2,2,1)
ax1.set_title("Histogram of values")
ax1.hist(nu_max_guess,color='k')
ax1.set_ylabel("Number of values")
ax1.set_xlabel(fr"$\nu_{{maxguess}}")

ax2 = fig.add_subplot(2,2,2,sharex=ax1)
ax2.set_title("Residuals")
ax2.plot(nu_max_literature,nu_max_guess-nu_max_literature,'x',label='Residual',color='k',markersize=3)
ax2.plot(nu_max_literature,quadraticPolynomial(nu_max_literature,*popt),'o',markersize=3,label='Fit')
ax2.set_ylabel(r"$\mu_{maxliterature}-\mu_{maxguess}$")
ax2.set_xlabel(r"$\mu_{maxliterature}$")
ax2.axhline(y=0,linestyle='dashed')
pl.legend()

ax3 = fig.add_subplot(2,2,3,sharex=ax1)
ax3.set_title("Residuals after fit")
ax3.plot(nu_max_literature,nu_max_new - nu_max_literature,'x',label='Residual',color='k',markersize=3)
ax3.set_ylabel(r"$\mu_{maxliterature}-\mu_{maxguess}$")
ax3.set_xlabel(r"$\mu_{maxliterature}$")
ax3.axhline(y=0,linestyle='dashed')
ax3.legend()

ax4 = fig.add_subplot(2,2,4,sharex=ax1)
ax4.set_title("New relation")
ax4.plot(nu_max_literature,nu_max_new,'x',label='Residual',color='k',markersize=3)
ax4.plot(nu_max_literature,quadraticPolynomial(nu_max_literature,*popt2),'o',markersize=3,label='Fit')
ax4.set_ylabel(r"$\mu_{maxnew}$")
ax4.set_xlabel(r"$\mu_{maxliterature}$")
ax4.axhline(y=0,linestyle='dashed')

with open("apokasc_running_list.txt",'w') as f:
    for i in running_list:
        f.write(f"{i[0]} {i[1]}\n")

pl.show()