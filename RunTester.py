from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
from calculations.priorCalculations import PriorCalculator
from plotter.plotFunctions import *
from filehandler.Diamonds.diamondsFileCreating import FileCreater

input = '004346201_18'
powerSpectrum = False
filename = "../../Sterndaten/KeplerData/kplr" + input + "_COR_" + (
    "PSD_" if powerSpectrum else "") + "filt_inp.fits"
file = FitsReader(filename)
powerCalc = PowerspectraCalculator(file.getLightCurve())
powerCalc.setKicID(input)

nuMaxCalc = NuMaxCalculator(powerCalc.getLightcurve(),powerCalc.getPSD())

corr,best_fit = nuMaxCalc.calculateIterativeFilterFrequency()
corr_2,best_fit_2 = nuMaxCalc.calculateIterativeFilterFrequency()


initNuFilter = nuMaxCalc.getInitNuFilter()
nuMax = nuMaxCalc.getNuFilterFitted()
photonNoise = nuMaxCalc.getPhotonNoise()
nyquist = nuMaxCalc.getNyquistFrequency()

priorCalculator = PriorCalculator(initNuFilter, nuMax,photonNoise)

print("Priors")
print("PhotonNoise: '" + str(priorCalculator.getPhotonNoiseBoundary()) + "'")
print("First Harvey Frequency: '" + str(priorCalculator.getFirstHarveyFrequencyBoundary()) + "'")
print("First Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
print("Second Harvey Frequency: '" + str(priorCalculator.getSecondHarveyFrequencyBoundary()) + "'")
print("Second Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
print("Third Harvey Frequency: '" + str(priorCalculator.getThirdHarveyFrequencyBoundary()) + "'")
print("Third Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
print("Amplitude: '" + str(priorCalculator.getAmplitudeBounday()) + "'")
print("nuMax: '" + str(priorCalculator.getNuMaxBoundary()) + "'")
print("Sigma: '" + str(priorCalculator.getSigmaBoundary()) + "'")

priors = []
priors.append(priorCalculator.getPhotonNoiseBoundary())
priors.append(priorCalculator.getHarveyAmplitudesBoundary())
priors.append(priorCalculator.getFirstHarveyFrequencyBoundary())
priors.append(priorCalculator.getHarveyAmplitudesBoundary())
priors.append(priorCalculator.getSecondHarveyFrequencyBoundary())
priors.append(priorCalculator.getHarveyAmplitudesBoundary())
priors.append(priorCalculator.getThirdHarveyFrequencyBoundary())
priors.append(priorCalculator.getAmplitudeBounday())
priors.append(priorCalculator.getNuMaxBoundary())
priors.append(priorCalculator.getSigmaBoundary())

lowerBounds = np.zeros(len(priors))
upperBounds = np.zeros(len(priors))

for i in range(0,len(priors) ):
    lowerBounds[i] = priors[i][0]
    upperBounds[i] = priors[i][1]

priors = np.array((lowerBounds,upperBounds)).transpose()


files = FileCreater(input,powerCalc.getPSD(),nyquist,priors)


#plotPSD(powerCalc,True,True)
#show()