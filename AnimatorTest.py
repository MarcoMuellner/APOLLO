from plotter.fileAnimator import FileAnimator
from filehandler.Diamonds.InternalStructure.backgroundParameterFile import BackgroundParameter
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

parameter = BackgroundParameter("Background","ppm",kickId="224321303",runID="NoiseOnly",id=1,readData=False,readLiveData=True)
parameter2 = BackgroundParameter("Background","ppm",kickId="224321303",runID="NoiseOnly",id=2,readData=False,readLiveData=True)

data = parameter.getLiveData()
data2 = parameter2.getLiveData()
np.savetxt("testFile.txt",data[:0])
np.savetxt("testFile2.txt",data2[:0])

Files  ={"test1":("Unit","testFile.txt"),
         "test2":("Unit","testFile2.txt")}


p = FileAnimator(Files)
p.start()

for i in range(1,len(data)):
    np.savetxt("testFile.txt",data[:i])
    np.savetxt("testFile2.txt", data2[:i])
p.join()