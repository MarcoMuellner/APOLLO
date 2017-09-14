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


input = '002437804_17'
powerSpectrum = False
#filename = "../../Sterndaten/LC_CORR/kplr" + input + "_COR_" + (
#    "PSD_" if powerSpectrum else "") + "filt_inp.fits"
filename = "../../Sterndaten/LC_CORR/kplr" + input + "_COR.fits"
file = FitsReader(filename)
powerCalc = PowerspectraCalculator(file.getLightCurve())
powerCalc.kicID = input

nuMaxCalc = NuMaxCalculator(input,powerCalc.getLightcurve(), powerCalc.powerSpectralDensity)

corr,best_fit = nuMaxCalc.calculateIterativeFilterFrequency()
initLowIndex = nuMaxCalc.getNearestIndex() + 10
corr_2,best_fit_2 = nuMaxCalc.calculateIterativeFilterFrequency()
initLowIndex_2 = nuMaxCalc.getNearestIndex() + 10

best_fit[1]*=24*60
corr[0] *=24*60
pl.figure()
pl.title("First fit")
pl.plot(corr[0],corr[1])
pl.plot(corr[0], nuMaxCalc.sinc(corr[0], *best_fit), 'r', linestyle='dotted')
print(corr[0][initLowIndex])
pl.xlim(0,corr[0][initLowIndex])
pl.xlabel("Tau_ACF (min)")
pl.ylabel("ACF^2")
pl.axhline(0)
pl.figure()
pl.title("Second fit")
pl.plot(corr_2[0],corr[1])
pl.plot(corr_2[0], nuMaxCalc.sinc(corr_2[0], *best_fit_2), 'r', linestyle='dotted')
pl.xlim(0,corr_2[0][initLowIndex_2])
pl.xlabel("Tau_ACF (min)")
pl.ylabel("ACF^2")
pl.axhline(0)
plotPSD(powerCalc,True,True)
show()