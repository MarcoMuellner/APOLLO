import argparse
import os
from json import load
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
from matplotlib.backend_bases import MouseEvent
from collections import OrderedDict
import numpy as np
from uncertainties import ufloat_fromstr
from pdf2image import convert_from_path


def get_val(dictionary: dict, key: str, default_value=None):
    if key in dictionary.keys():
        try:
            return ufloat_fromstr(dictionary[key]).nominal_value
        except (ValueError, AttributeError) as e:
            return dictionary[key]
    else:
        return default_value


def plot_bar_from_counter(list_item, ax: Axes):
    """"
    This function creates a bar plot from a counter.

    :param counter: This is a counter object, a dictionary with the item as the key
     and the frequency as the value
    :param ax: an axis of matplotlib
    :return: the axis wit the object in it
    """

    counter = dict((x, list_item.count(x)) for x in set(list_item))

    frequencies = []
    names = []

    for i in ["Strong evidence","Moderate evidence","Weak evidence","Inconclusive"]:
        try:
            frequencies.append(counter[i])
            names.append(counter[i])
        except:
            pass

    x_coordinates = np.arange(len(counter))
    ax.bar(x_coordinates, frequencies, align='center', color='k')

    ax.xaxis.set_major_locator(pl.FixedLocator(x_coordinates))  #
    ax.set_xticklabels(names, rotation=40)

    return ax


parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to be analyzed", type=str)

args = parser.parse_args()

path = f"{args.path}"

res_dat = OrderedDict()
res_dat["ID"] = []
res_dat["Conclusion"] = []
res_dat["Bayes factor"] = []
res_dat["White noise"] = []
res_dat["Amp oscillation"] = []
res_dat["Literature value"] = []
res_dat["SNR"] = []
res_dat["full_fit"] = []
res_dat["light_curve"] = []

for path, sub_path, files in os.walk(path):
    if "results.json" in files:
        with open(f"{path}/results.json", 'r') as f:
            data_dict = load(f)

        res_dat["ID"].append(int(path.split("_")[-1]))
        res_dat["Conclusion"].append(get_val(data_dict, "Conclusion"))
        res_dat["Bayes factor"].append(get_val(data_dict, "Bayes factor"))
        res_dat["White noise"].append(get_val(data_dict["Full Background result"], "w"))
        res_dat["Amp oscillation"].append(get_val(data_dict["Full Background result"], "$H_\\mathrm{osc}$"))
        res_dat["Literature value"].append(get_val(data_dict, "Literature value"))
        res_dat["SNR"].append(get_val(data_dict["Full Background result"], "$H_\\mathrm{osc}$") / get_val(
            data_dict["Full Background result"], "w"))
        res_dat["full_fit"].append(f"{path}/images/PSD_full_fit_{int(path.split('_')[-1])}_.png")
        res_dat["light_curve"].append(f"{path}/images/Lightcurve_sigma_clipping_{int(path.split('_')[-1])}_.png")


fig: Figure = pl.figure(figsize=(20, 10))
fig.suptitle("Bayesian analysis")

ax1: Axes = fig.add_subplot(1, 3, 1)
ax1 = plot_bar_from_counter(res_dat["Conclusion"], ax1)

ax2: Axes = fig.add_subplot(1, 3, 2)
ax2.plot(res_dat["SNR"], res_dat['Bayes factor'], 'x', markersize=3, color='k')
ax2.axhline(y=0, color='k')
ax2.axhline(y=5, linestyle='dashed', color='blue', label='Weak evidence')
ax2.set_ylim(-50, 100)
ax2.set_xlim(0, 50)
ax2.set_xlabel("SNR")
ax2.set_ylabel("Bayes factor")

ax3: Axes = fig.add_subplot(1, 3, 3)
ax3.plot(res_dat["Literature value"], res_dat["Bayes factor"], 'x', markersize=3, color='k')
ax3.axhline(y=0, color='k')
ax3.axhline(y=5, linestyle='dashed', color='blue', label='Weak evidence')
ax3.set_ylim(-50, 100)
ax3.set_xlabel(r"$\nu_{max,literature}$")

def onclick(event : MouseEvent):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

    if event.dblclick:
        if event.inaxes == ax2:
            vector_list = np.sqrt(np.array(res_dat["SNR"]) ** 2 + np.array(res_dat['Bayes factor']) ** 2)
            index = (np.abs(np.array(res_dat["Bayes factor"]) - event.ydata)).argmin()
        elif event.inaxes == ax3:
            vector_list = np.sqrt(np.array(res_dat["Literature value"]) ** 2 + np.array(res_dat['Bayes factor']) ** 2)
            index = (np.abs(np.array(res_dat["Literature value"]) - event.ydata)).argmin()
        else:
            return

        vector = np.sqrt(event.x**2 + event.y**2)
        #index = (np.abs(vector_list - vector)).argmin()

        fig_im = pl.figure(figsize=(10, 6))
        image = mpimg.imread(res_dat["full_fit"][index])
        pl.imshow(image)
        pl.axis('off')
        fig_im = pl.figure(figsize=(10, 6))
        image = mpimg.imread(res_dat["light_curve"][index])
        pl.imshow(image)
        pl.axis('off')
        pl.show()


cid = fig.canvas.mpl_connect('button_press_event', onclick)

test_id_list = np.array(res_dat["ID"])[np.logical_and(np.array(res_dat["SNR"])>45,np.array(res_dat["Bayes factor"])>30)]
test_lit_val_list = np.array(res_dat["Literature value"])[np.logical_and(np.array(res_dat["SNR"])>45,np.array(res_dat["Bayes factor"])>30)]
for id,val in zip(test_id_list,test_lit_val_list):
    print(f"{id} {val}")

pl.show(fig)
