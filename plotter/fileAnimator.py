import multiprocessing as mp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.style.use('ggplot')

class FileAnimator:

    def __init__(self,fileNames):
        self.fileName = fileNames
        self.oldData = np.zeros(2000)

    def run(self):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.grid()
        self.xdata, self.ydata = [], []
        plt.ion()
        self.ani = animation.FuncAnimation(self.fig, self.run_animation, blit=False, interval=0.0001,
                                      repeat=False, init_func=self.init)

    def init(self):
        self.ax.set_xlim(0, 10)
        del self.xdata[:]
        del self.ydata[:]
        self.line.set_data(self.xdata, self.ydata)
        return self.line,

    def run_animation(self,i):
        # update the data
        data = np.loadtxt(self.fileName).T
        self.ydata = data
        try:
            self.xdata = np.arange(0,len(data))
        except:
            self.xdata = np.array([0])

        xmin, xmax = self.ax.get_xlim()

        if np.amax(self.xdata) >= xmax:
            self.ax.set_xlim(xmin, 2 * xmax)
            self.ax.figure.canvas.draw()
        self.ax.set_ylim(np.amin(self.ydata)/1.5,np.amax(self.ydata)*1.5)
        self.line.set_data(self.xdata, self.ydata)

        return self.line,
