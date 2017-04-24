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

npArrs = file.getLightCurve()
counter = 1

print(npArrs.shape)

pl.plot(npArrs[0],npArrs[1])

'''
for i in npArrs:
    pl.title(str(counter)+" Array")
    print(npArrs)
    pl.plot(i[0],i[1])
    pl.figure()
    counter +=1
'''

pl.show()