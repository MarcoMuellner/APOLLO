import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np
import os
from shutil import rmtree,copytree

from scripts.helper_functions import load_results,get_val,recreate_dir,touch
from scripts.helper_functions import f_max,full_background
from res.conf_file_str import general_kic,internal_literature_value
from pandas import DataFrame

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)

args = parser.parse_args()

res_list = load_results(args.input_path,["checked.txt"])

class b:
    button_pressed = None

def press(event):
    print('press', event.key)
    b.button_pressed = event.key

path_list = []

print(len(res_list))

for path,result,conf in res_list:
    f_max_f = get_val(result[full_background],f_max)
    f_lit = result[internal_literature_value]

    app = conf[general_kic]

    if  "Noise value" in conf.keys():
        noise = str(conf["Noise value"])
        app = f"{app}_n_{noise}"


    image = mpimg.imread(f"{path}/images/PSD_guess_full_fit_{app}_.png")
    fig = pl.figure(figsize=(10,6))
    pl.imshow(image)
    pl.axis('off')
    pl.text(0.5, -0.1,
            rf"$\nu_{{max,literature}}$={f_lit}$\nu_{{max,fit}}$={f_max_f}",
            size=14, ha='center', transform=pl.gca().transAxes)

    pl.title(path)

    fig.canvas.mpl_connect('key_press_event', press)
    pl.draw()
    pl.pause(1)
    while b.button_pressed != "y" and b.button_pressed != "n":
        pl.waitforbuttonpress()
        print()

    pl.close(fig)

    if b.button_pressed == "n":
        touch(f"{path}/ignore.txt")
    else:
        touch(f"{path}/checked.txt")

    b.button_pressed = None
