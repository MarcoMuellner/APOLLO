from plotter.fileAnimator import FileAnimator
from filehandler.Diamonds.InternalStructure.backgroundParameterFile import BackgroundParameter
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

parameter = BackgroundParameter("Background","ppm",kickId="224321303",runID="NoiseOnly",id=1,readData=False,readLiveData=True)

data = parameter.getLivedata()
np.savetxt("testFile.txt",data[:0])

p = FileAnimator("testFile.txt")
p.run()
for i in range(1,len(data)):
    np.savetxt("testFile.txt",data[:i])
    plt.pause(0.000001)
p.join()