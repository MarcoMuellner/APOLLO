from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from plotter.plotFunctions import *

input = '003656476_12'
powerSpectrum = False
filename = "../../Sterndaten/KeplerData/kplr" + input + "_COR_" + (
    "PSD_" if powerSpectrum else "") + "filt_inp.fits"
file = FitsReader(filename)
#powerCalc = PowerspectraCalculator(file.getLightCurve())
#powerCalc.setKicID(input)

pl.plot(file.getLightCurve()[0],file.getLightCurve()[1])
pl.show()