import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np
import os
from shutil import rmtree, copytree

from scripts.helper_functions import load_results, get_val, recreate_dir, touch
from scripts.helper_functions import f_max, full_background
from res.conf_file_str import general_kic, internal_literature_value
from pandas import DataFrame

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)

args = parser.parse_args()

res_list = load_results(args.input_path, ["checked.txt"])


class b:
    button_pressed = None


def press(event):
    print('press', event.key)
    b.button_pressed = event.key


path_list = []

print(len(res_list))
sigma = 0.05

redo_list = []

for path, result, conf in res_list:
    f_max_f = get_val(result[full_background], f_max)
    f_lit = result[internal_literature_value]
    f_guess = result["Nu max guess"]
    kic_id = conf[general_kic]

    if np.abs(f_max_f - f_lit) / f_lit < sigma:
        continue

    app = conf[general_kic]

    if "Noise value" in conf.keys():
        noise = str(conf["Noise value"])
        app = f"{app}_n_{noise}"

    image_guess = mpimg.imread(f"{path}/images/PSD_guess_full_fit_{app}_.png")
    image_fit = mpimg.imread(f"{path}/images/PSD_full_fit_{app}_.png")

    fig : Figure = pl.figure(figsize=(16, 6))
    #fig.subplots_adjust(wspace=0.05)
    fig.suptitle(path)
    ax_guess : Axes = fig.add_subplot(121)
    ax_guess.imshow(image_guess,aspect='auto')
    ax_guess.axis('off')
    ax_guess.text(0.5, -0.1, rf"$\nu_{{max,literature}}$={f_lit},$\nu_{{max,guess}}$={f_guess}",
            size=14, ha='center', transform=pl.gca().transAxes)

    ax_guess.set_title("Guess")

    ax_fit: Axes = fig.add_subplot(122)
    ax_fit.imshow(image_fit,aspect='auto')
    ax_fit.axis('off')
    ax_fit.text(0.5, -0.1,
                  rf"$\nu_{{max,literature}}$={f_lit},$\nu_{{max,fit}}$={f_max_f}",
                  size=14, ha='center', transform=pl.gca().transAxes)

    ax_fit.set_title("Fit")

    fig.canvas.mpl_connect('key_press_event', press)
    pl.draw()
    pl.pause(1)
    while b.button_pressed != "y" and b.button_pressed != "n":
        pl.waitforbuttonpress()
        print()

    pl.close(fig)

    redo_list.append((kic_id,f_lit))

    if b.button_pressed == "n":
        touch(f"{path}/ignore.txt")
    else:
        touch(f"{path}/checked.txt")

    b.button_pressed = None

print(redo_list)

#with open("redo.txt",'w') as f:
#    for kic_id, f_lit in redo_list:
#        f.write(f"{kic_id} {f_lit}\n")
#np.savetxt('redo.txt',np.array(redo_list))