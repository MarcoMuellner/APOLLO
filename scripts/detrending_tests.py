import numpy as np
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import os
from data_handler.signal_features import compute_periodogram
from astropy.convolution import convolve, Box1DKernel

def fit_lower_frequencies(data : np.ndarray):
    pass

files = [f for f in os.listdir("test_data") if os.path.isfile(os.path.join("test_data", f))]

for file in files:
    data = np.loadtxt(f"test_data/{file}").T
    x = data[0]
    y = data[1]

    fit_lower_frequencies(data)

    kernel = int(100/np.log(np.std(y)))
    print(kernel)
    smoothed_signal = convolve(y,  Box1DKernel(kernel))

    fig: Figure = pl.figure(figsize=(20, 10))
    ax: Axes = fig.add_subplot(221)
    ax.plot(x, y, 'o', markersize=2, color='k')
    ax.plot(x, smoothed_signal, linewidth=2, color='red')
    ax.set_ylim(min(y) * 0.99, max(y) * 1.01)
    ax.set_xlabel("Time")
    ax.set_ylabel("Flux")
    ax.set_title(file)

    f_data = compute_periodogram(data)
    ax: Axes = fig.add_subplot(222)
    ax.loglog(f_data[0], f_data[1], linewidth=2, color='k')
    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')

    y_new = y - smoothed_signal + np.mean(y)
    y_new = y_new[np.logical_and(x > min(x)*1.001,x<max(x)*0.999)]
    x = x[np.logical_and(x > min(x)*1.001,x<max(x)*0.999)]

    ax: Axes = fig.add_subplot(223)
    ax.plot(x, y_new, 'o', markersize=2, color='k')
    ax.set_ylim(min(y_new) * 0.99, max(y_new) * 1.01)
    ax.set_xlabel("Time")
    ax.set_ylabel("Flux")
    ax.set_title(file+ " smoothed")

    y_new -= np.mean(y)

    f_data_new = compute_periodogram(np.array((x,y_new)))
    ax: Axes = fig.add_subplot(224)
    ax.loglog(f_data_new[0], f_data_new[1], linewidth=2, color='k')
    ax.loglog(f_data[0], f_data[1], linewidth=2, color='red',alpha=0.1)
    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')

    #pl.draw()
    #pl.pause(5)

    print("")

    #pl.waitforbuttonpress()

    np.savetxt(f"reduced_k2/{file}",np.array((x,y_new)).T)
    fig.savefig(f"reduced_k2/{file}.png")
    pl.close(fig)
