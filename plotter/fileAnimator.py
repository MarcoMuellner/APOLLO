import numpy as np
import pylab as plt
import matplotlib.animation as animation
import multiprocessing as mp


class FileAnimator(mp.Process):

    def __init__(self,fileNames):
        self.files = fileNames
        self.axDict = {}
        self.lineDict = {}
        self.oldData = np.zeros(2000)
        mp.Process.__init__(self)

    def run(self):
        self.fig = plt.figure()
        counter = 1
        if len(self.files.keys()) > 5:
            counterJ = 2
            counterK = 5
        else:
            counterJ = 1
            counterK = 5
        for name,(unit,filename) in self.files.items():
            self.axDict[name] = self.fig.add_subplot(counterJ,counterK,counter)
            self.axDict[name].set_xlabel(unit)
            self.axDict[name].set_title(name)
            self.lineDict[name], = self.axDict[name].plot([],[],lw=2)
            counter +=1
            print(self.lineDict[name])
        self.fig.tight_layout()

        plt.ion()
        self.ani = animation.FuncAnimation(self.fig, self.run_animation, blit=False, interval=1,
                                      repeat=False, init_func=self.init)

        while(True):
            print("Hello")
            pass


    def init(self):
        lineList = []
        for name,line in self.lineDict.items():
            line.set_data([], [])
            lineList.append(line)
        return lineList,

    def run_animation(self,i):
        # update the data
        lineList = []
        print("HI")
        for name,(unit,filename) in self.files.items():
            try:
                data = np.loadtxt(filename).T
            except:
                data = np.array([0])
            ydata = data
            try:
                xdata = np.arange(0,len(data))
                xmin, xmax = self.axDict[name].get_xlim()

                if np.amax(xdata) >= xmax:
                    self.axDict[name].set_xlim(xmin, 2 * xmax)
                    self.axDict[name].figure.canvas.draw()
                    self.axDict[name].set_ylim(np.amin(ydata) / 1.5, np.amax(ydata) * 1.5)
            except:
                xdata = np.array([0])

            self.lineDict[name].set_data(xdata, ydata)
            lineList.append(self.lineDict[name])

        return lineList
