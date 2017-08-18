from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.priorCalculations import PriorCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
from plotter.plotFunctions import *
from filehandler.Diamonds.diamondsFileCreating import FileCreater
from diamonds.diamondsProcesses import DiamondsProcess
from loghandler.loghandler import *
import logging

setup_logging()
logger = logging.getLogger(__name__)

powerSpectrum = False


input = "004770846_1435"
filename = "../Sterndaten/RG_ENRICO/kplr" + input + "_COR_" + ("PSD_" if powerSpectrum else "") + "filt_inp.fits"
file = FitsReader(filename)
powerCalc = PowerspectraCalculator(file.getLightCurve())
powerCalc.setKicID(input)

nuMaxCalc = NuMaxCalculator(file.getLightCurve())

nuMax = 57 
photonNoise = 0.03
nyquist = nuMaxCalc.getNyquistFrequency()

priorCalculator = PriorCalculator(nuMax,photonNoise)

logger.info("Priors")
logger.info("PhotonNoise: '" + str(priorCalculator.getPhotonNoiseBoundary()) + "'")
logger.info("First Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
logger.info("First Harvey Frequency: '" + str(priorCalculator.getFirstHarveyFrequencyBoundary()) + "'")
logger.info("Second Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
logger.info("Second Harvey Frequency: '" + str(priorCalculator.getSecondHarveyFrequencyBoundary()) + "'")
logger.info("Third Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
logger.info("Third Harvey Frequency: '" + str(priorCalculator.getThirdHarveyFrequencyBoundary()) + "'")
logger.info("Amplitude: '" + str(priorCalculator.getAmplitudeBounday()) + "'")
logger.info("nuMax: '" + str(priorCalculator.getNuMaxBoundary()) + "'")
logger.info("Sigma: '" + str(priorCalculator.getSigmaBoundary()) + "'")

logger.info("Priors")
logger.info("PhotonNoise: '" + str(priorCalculator.getPhotonNoise()) + "'")
logger.info("First Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitude()) + "'")
logger.info("First Harvey Frequency: '" + str(priorCalculator.getHarveyFrequency1()) + "'")
logger.info("Second Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitude()) + "'")
logger.info("Second Harvey Frequency: '" + str(priorCalculator.getHarveyFrequency2()) + "'")
logger.info("Third Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitude()) + "'")
logger.info("Third Harvey Frequency: '" + str(priorCalculator.getHarveyFrequency3()) + "'")
logger.info("Amplitude: '" + str(priorCalculator.getAmplitude()) + "'")
logger.info("nuMax: '" + str(nuMax) + "'")
logger.info("Sigma: '" + str(priorCalculator.getSigma()) + "'")

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

median = []
median.append(priorCalculator.getPhotonNoise())
median.append(priorCalculator.getHarveyAmplitude())
median.append(priorCalculator.getHarveyFrequency1())
median.append(priorCalculator.getHarveyAmplitude())
median.append(priorCalculator.getHarveyFrequency2())
median.append(priorCalculator.getHarveyAmplitude())
median.append(priorCalculator.getHarveyFrequency3())
median.append(priorCalculator.getAmplitude())
median.append(nuMax)
median.append(priorCalculator.getSigma())

proc = DiamondsProcess(strDiamondsGaussian,input,"0","1")
proc.start()

