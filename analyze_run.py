import argparse
import json
import os
from support.directoryManager import cd
from res.conf_file_str import internal_flag_worked, internal_literature_value
import matplotlib.pyplot as pl
import numpy as np
from shutil import copytree, rmtree
from scipy.optimize import curve_fit
from fitter.fit_functions import quadraticPolynomial
import sys
import time
from uncertainties import ufloat_fromstr


def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        rmtree(to_path)
    copytree(from_path, to_path)


parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to be analyzed", type=str)
parser.add_argument("input_list", help="The input list containing the literature values", type=str)
parser.add_argument("-uf", "--use_failed", help="Use the failures for analysis", action='store_true')
parser.add_argument("-wf", "--write_files", help="Copy directories?", action='store_true')
parser.add_argument("-sp", "--show_plot", help="Show plots?", action='store_true')
parser.add_argument("-rf", "--refresh", help="Show plots?", action='store_true')

args = parser.parse_args()

input = np.loadtxt(args.input_list).T

working_list = []
failed_list = []

nu_max_guess = []
nu_max_literature = []
copy_list_good = []
copy_list_bad = []
copy_list_unkown = []
running_list = []
determined_params = {}
lookup_dict = {}
bayes_values = []
snr = []

nu_max_determination = []

priorAnalysis = {}

total_priors = 0
for res_path in os.listdir(args.path):
    found = False
    for result in os.listdir(args.path + res_path):
        if "results.json" == result:
            found = True
            with cd(args.path + res_path):
                id = res_path.split("_")[1]
                with open("results.json", 'r') as f:
                    data = json.load(f)
                if internal_flag_worked in data.keys():
                    if data[internal_flag_worked] != args.use_failed:
                        working_list.append(
                            (res_path, int(id), float("%.2f" % data["Nu max guess"]), data[internal_literature_value]))
                        nu_max_guess.append(float("%.2f" % data["Nu max guess"]))
                        nu_max_literature.append(data[internal_literature_value])
                        copy_list_good.append((args.path + res_path, res_path))
                        running_list.append((int(id), data[internal_literature_value]))
                        lookup_dict[data[internal_literature_value]] = res_path
                        if "Determined params" in data.keys():
                            for name, value in data["Determined params"].items():
                                if name in determined_params:
                                    determined_params[name].append(value)
                                else:
                                    determined_params[name] = [value]

                        if "Full Background result" in data.keys() and "priors" in data.keys():
                            # data["Determined params"]["H_osc"],data["Determined params"]["nu_max"] = data["Determined params"]["nu_max"],data["Determined params"]["H_osc"]

                            nu_max_determination.append(
                                [ufloat_fromstr(data["Full Background result"]["$f_\\mathrm{max}$ "]).nominal_value,
                                 data[internal_literature_value]])
                            bayes_values.append(
                                [data[internal_literature_value], ufloat_fromstr(data["Bayes factor"]).nominal_value])

                            snr_value = ufloat_fromstr(data["Full Background result"]["$H_\\mathrm{osc}$"])/ufloat_fromstr(data["Full Background result"]["w"])
                            snr.append((snr_value.nominal_value,ufloat_fromstr(data["Bayes factor"]).nominal_value))

                            for (val_name, value), (priorName, (lowerPrior, upperPrior)) in zip(
                                    data["Full Background result"].items(), data["priors"].items()):
                                total_priors += 1
                                if val_name in priorAnalysis:
                                    priorAnalysis[val_name][0] += lowerPrior / ufloat_fromstr(value).nominal_value
                                    priorAnalysis[val_name][0] /= 2
                                    priorAnalysis[val_name][1] += upperPrior / ufloat_fromstr(value).nominal_value
                                    priorAnalysis[val_name][1] /= 2
                                else:
                                    priorAnalysis[val_name] = [lowerPrior / ufloat_fromstr(value).nominal_value,
                                                               ufloat_fromstr(value).nominal_value]

                    elif data[internal_flag_worked] == args.use_failed:
                        failed_list.append(id)
                        copy_list_bad.append((args.path + res_path, res_path))

    if not found:
        copy_list_unkown.append((args.path + res_path, res_path))

if args.write_files:
    for i in copy_list_good:
        copy_and_overwrite(i[0], f"working_apokasc/{i[1]}")

    for i in copy_list_bad:
        copy_and_overwrite(i[0], f"failed_apokasc/{i[1]}")

    for i in copy_list_unkown:
        copy_and_overwrite(i[0], f"unknown_apokasc/{i[1]}")

n_working = len(working_list)
n_failed = len(failed_list)
n_total = len(os.listdir(args.path))
batch_yield = "%.1f" % (100 * len(working_list) / len(os.listdir(args.path))) + "%"
batch_failed = "%.1f" % (100 * n_failed / n_total) + "%"
batch_rest = "%.1f" % (100 *(1 - n_failed / n_total - len(working_list) / len(os.listdir(args.path)))) + "%"

print(f"Total available: {n_total}")
print(f"Total working: {n_working}")
print(f"Total failed: {n_failed}")
print(f"Total rest: {n_total - n_working - n_failed}")
print(f"Total unknown: {n_total - n_working - n_failed - 32}")
print(f"Yield working: {batch_yield}")
print(f"Yield failed: {batch_failed}")
print(f"Yield rest: {batch_rest}")

if args.write_files:
    with open("apokasc_running_list.txt", 'w') as f:
        for i in running_list:
            f.writelines(f"{i[0]} {i[1]}\n")

if not args.show_plot:
    sys.exit(0)

nu_max_guess = np.array(nu_max_guess)
nu_max_literature = np.array(nu_max_literature)

try:
    boundary = -(53/61)*nu_max_literature + 56
    y = nu_max_guess - nu_max_literature
    x = nu_max_literature[y<boundary]
    y = y[y<boundary]
    popt, _ = curve_fit(quadraticPolynomial, x,y)
    nu_max_new = nu_max_guess - quadraticPolynomial(nu_max_literature, *popt)
    nofit = False
except:
    nofit = True

try:
    popt2, _ = curve_fit(quadraticPolynomial, nu_max_literature, nu_max_new)
    nofit = False
except:
    nofit = True

if not nofit:
    print(f"Fitvalues: {popt}")
    print(f"Standarddeviation: {(nu_max_new - nu_max_literature).std()}")

fig1 = pl.figure(figsize=(20, 20))
fig1.suptitle(f"Failed: {args.use_failed}")
ax1 = fig1.add_subplot(3, 3, 1)
ax1.set_title("Histogram of values")
weights = np.ones_like(input[1]) / float(len(input[1]))
ax1.hist(input[1], color='k', alpha=0.8, weights=weights, label='Theory')
weights = np.ones_like(nu_max_literature) / float(len(nu_max_literature))
ax1.hist(nu_max_literature, alpha=0.5, color='green', weights=weights, label='Result')
ax1.set_ylabel("Number of values")
ax1.set_xlabel(fr"$\nu_{{maxliterature}}$")
ax1.legend()

ax2 = fig1.add_subplot(3, 3, 2, sharex=ax1)
ax2.set_title("Residuals")
ax2.plot(nu_max_literature, nu_max_guess - nu_max_literature, 'x', label='Residual', color='k', markersize=3)
if not nofit:
    ax2.plot(nu_max_literature, quadraticPolynomial(nu_max_literature, *popt), 'o', markersize=3, label='Fit')
ax2.set_ylabel(r"$\mu_{maxliterature}-\mu_{maxguess}$")
ax2.set_xlabel(r"$\mu_{maxliterature}$")
ax2.axhline(y=0, linestyle='dashed')
pl.legend()

ax3 = fig1.add_subplot(3, 3, 3, sharex=ax1)
ax3.set_title("Residuals after fit")
if not nofit:
    ax3.plot(nu_max_literature, nu_max_new - nu_max_literature, 'x', label='Residual', color='k', markersize=3)
ax3.set_ylabel(r"$\mu_{maxliterature}-\mu_{maxguess}$")
ax3.set_xlabel(r"$\mu_{maxliterature}$")
ax3.axhline(y=0, linestyle='dashed')
ax3.legend()

ax4 = fig1.add_subplot(3, 3, 4, sharex=ax1)
ax4.set_title("New relation")
if not nofit:
    ax4.plot(nu_max_literature, nu_max_new, 'x', label='Residual', color='k', markersize=3)
    ax4.plot(nu_max_literature, quadraticPolynomial(nu_max_literature, *popt2), 'o', markersize=3, label='Fit')
ax4.set_ylabel(r"$\mu_{maxnew}$")
ax4.set_xlabel(r"$\mu_{maxliterature}$")
ax4.axhline(y=0, linestyle='dashed')

ax5 = fig1.add_subplot(3, 3, 5, )
ax5.set_title("Distribution of targets")
labels = 'Worked', 'Failed', 'Unknown'
pie_data = [n_working, n_failed, n_total - n_working - n_failed]
explode = [0.1, 0, 0]
colors = ['green', 'red', 'gray']
ax5.pie(pie_data, explode=explode, labels=labels, shadow=True, startangle=90, colors=colors)
ax5.axis('equal')

ax6 = fig1.add_subplot(3, 3, 6)

for (i, (name, (lower, upper))) in zip(range(0, len(priorAnalysis)), priorAnalysis.items()):
    ax6.plot([i, i], [lower, upper], color='r', linewidth=5, label=name)
    ax6.plot(i, 1, 'x', color='k', markersize=3)

ax6.set_title(f"Total priors: {total_priors / len(priorAnalysis)}")
ax6.set_xticks(range(0, len(priorAnalysis)))
ax6.set_xticklabels(priorAnalysis.keys(), rotation=40)

arr = np.array(nu_max_determination).T

ax7 = fig1.add_subplot(3, 3, 7)
ax7.plot(arr[1], arr[0], 'x', label='Residual', color='k', markersize=3)
ax7.plot(arr[1], arr[1],':', color='green', linewidth=2)
ax7.set_ylabel(r"$\mu_{maxdetermination}$")
ax7.set_xlabel(r"$\mu_{maxliterature}$")
ax7.axhline(y=0, linestyle='dashed')

ax8 = fig1.add_subplot(3, 3, 8)
ax8.plot(arr[1], arr[0]-arr[1], 'x', label='Residual', color='k', markersize=3)
ax8.set_ylabel(r"$\mu_{maxdetermination}$ - $\mu_{maxliterature}$")
ax8.set_xlabel(r"$\mu_{maxliterature}$")
ax8.axhline(y=0, linestyle='dashed')

arr = np.array(snr).T

ax9 = fig1.add_subplot(3, 3, 9)
ax9.plot(arr[0], arr[1], 'x', label='Residual', color='k', markersize=3)
ax9.set_ylabel(r"Bayes factor")
ax9.set_xlabel(r"SNR")
ax9.axhline(y=0, linestyle='dashed')



def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

    index = (np.abs(nu_max_literature - event.xdata)).argmin()
    print(lookup_dict[nu_max_literature[index]])
    id = lookup_dict[nu_max_literature[index]]

    for txt in fig1.texts:
        txt.set_visible(False)

    for i in axlist:
        i.text(event.xdata, event.ydata, id)

        fig1.canvas.draw()
        fig1.canvas.flush_events()


cid = fig1.canvas.mpl_connect('button_press_event', onclick)

fig = pl.figure(figsize=(20, 20))
fig.suptitle(f"Failed: {args.use_failed}")

for (name, values), i in zip(determined_params.items(), range(1, len(determined_params) + 1)):
    ax = fig.add_subplot(4, 4, i)
    ax.set_title(f"Histogram {name}")
    values = np.array(values)
    values = values[values < 0.9 * np.max(values)]
    weights = np.ones_like(values) / float(len(values))
    ax.hist(values, color='k', alpha=0.8, weights=weights, label='Result')
    ax.set_ylabel("Number of values")
    ax.set_xlabel(fr"{name}")
    ax.legend()

axlist = [ax2,
          ax3,
          ax4]

if not args.refresh:
    pl.show()
else:
    pl.draw()
    pl.pause(1)
    time.sleep(5)
    pl.close(fig)
