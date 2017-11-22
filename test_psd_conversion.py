from astropy.io import fits
import pylab as pl
from runner.StandardRunner import StandardRunner
import numpy as np

kic = "004448777_771"

lightcurveFileName = "kplr"+kic+"_COR_filt_inp.fits"
psdFileName = "kplr"+kic+"_COR_PSD_filt_inp.fits"

hdulist = fits.open(psdFileName)
rawData = hdulist[0].data.T

rawData[0] = rawData[0]*10**6


pl.loglog(rawData[0],rawData[1],label="direct")


runner = StandardRunner(kic,"",".")

powerCalc = runner._readAndConvertLightCurve(lightcurveFileName)

psd = powerCalc.powerSpectralDensity

pl.loglog(psd[0],psd[1],label="converted",alpha=10)

pl.legend()

print("Delta Length: "+str(len(psd[0])-len(rawData[0])))

delta = psd[1] - rawData[1][0:len(psd[1])]

print("Mean of delta: "+str(np.mean(delta)))

#pl.show()

np.savetxt("KIC"+kic+".txt",rawData.T)