import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
from data_handler.signal_features import compute_periodogram

delta_t = 0.04089778825

x = np.linspace(0,80,num=80/delta_t)
y_rand = np.random.rand(len(x))
y_normal = np.random.normal(len(x))
y_chi = np.random.chisquare(1,len(x))

fig : Figure = pl.figure(figsize=(12,6))

for y,i in zip([y_rand,y_normal,y_chi],range(0,3)):
    ax :Axes = fig.add_subplot(2,3,1+i)
    #ax.set_title("Random distribution")
    ax.plot(x,y_rand,'x',color='k',markersize=3)
    ax.set_ylabel("Flux")
    ax.set_xlabel("Time")
    ax.set_ylim(-0.2,1.2)

    ax :Axes = fig.add_subplot(2,3,4+i)
    f_data = compute_periodogram(np.array((x*3600*24,y_rand)))
    ax.loglog(f_data[0],f_data[1],color='k',linewidth=3)
    ax.set_ylabel("Power")
    ax.set_xlabel("Frequency")

pl.show()
