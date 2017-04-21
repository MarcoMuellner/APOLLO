from calculations.deltaNuCalculations import DeltaNuCalculator
from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
from plotter.plotFunctions import *
import pylab as pl
import numpy as np

def smoothTriangle(data, degree, dropVals=False):
    print(len(data))
    triangle=np.array(list(range(degree)) + [degree] + list(range(degree)[::-1])) + 1
    smoothed=[]
    print(degree)
    print(len(data) - degree * 2)
    for i in range(degree, len(data) - degree * 2):
        point=data[i:i + len(triangle)] * triangle
        smoothed.append(sum(point)/sum(triangle))
    if dropVals:
        return smoothed

    print(smoothed[0])
    print([smoothed[0]])
    smoothed=np.array(smoothed[0])*((degree + degree/2)) + smoothed
    print(len(smoothed))
    print(len(data))
    while len(smoothed) < len(data):
        smoothed = np.append(smoothed,smoothed[-1])
        print(len(smoothed))
        print(len(data))
    return smoothed


input = '004346201_18'
powerSpectrum = False
filename = "../../Sterndaten/KeplerData/kplr" + input + "_COR_" + (
    "PSD_" if powerSpectrum else "") + "filt_inp.fits"
file = FitsReader(filename)
powerCalc = PowerspectraCalculator(file.getLightCurve())
powerCalc.setKicID(input)
'''
smoothing = smoothTriangle(powerCalc.getLightcurve()[1],1500)
smoothing = powerCalc.getLightcurve()[1]-smoothing

powerCalc1 = PowerspectraCalculator(np.array((file.getLightCurve()[0],smoothing)))

plotPSD(powerCalc,True,True)
plotPSD(powerCalc1,True,True)
show()
'''

#pl.plot(file.getLightCurve()[0],file.getLightCurve()[1])
#plotPSD(powerCalc,True,True)

nuMaxCalc = NuMaxCalculator(powerCalc.getLightcurve(),powerCalc.getPSD())

corr,best_fit = nuMaxCalc.calculateIterativeFilterFrequency()

best_fit[1]*=24*60
corr[0] *=24*60
pl.figure()
pl.plot(corr[0][1:],corr[1][1:])
pl.plot(corr[0], nuMaxCalc.sinc(corr[0], *best_fit), 'r', linestyle='dotted')
pl.xlim(0,10)
pl.xlabel("Tau_ACF (min)")
pl.ylabel("ACF^2")
pl.axhline(0)
#pl.ylim(0,max(corr[1])+0.1)
#pl.axhline(y=0,linestyle='dotted')
#pl.axvline(x=best_fit[1],linestyle='dotted')
plotPSD(powerCalc,True,True)
#plotPSD(nuMaxCalc.getFirstFilteredPSD(),True,True)
show()