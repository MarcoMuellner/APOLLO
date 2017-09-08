from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.priorCalculations import PriorCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
from plotter.plotFunctions import *
from filehandler.Diamonds.diamondsFileCreating import FileCreater
from diamonds.diamondsProcesses import DiamondsProcess
from loghandler.loghandler import *
import logging

def createBackgroundModel(runGauss,median,psd,nyq):
    freq, psd = psd
    par_median = median  # median values

    zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
    r = (np.sin(np.pi / 2. * freq / nyq) / (
        np.pi / 2. * freq / nyq)) ** 2  # ; responsivity (apodization) as a sinc^2
    w = par_median[0]  # White noise component
    g = 0
    if runGauss:
        g = median[7] * np.exp(-(median[8] - freq) ** 2 / (2. * median[9] ** 2))  ## Gaussian envelope

    ## Long-trend variations
    sigma_long = par_median[1]
    freq_long = par_median[2]
    h_long = (sigma_long ** 2 / freq_long) / (1. + (freq / freq_long) ** 4)

    ## First granulation component
    sigma_gran1 = par_median[3]
    freq_gran1 = par_median[4]
    h_gran1 = (sigma_gran1 ** 2 / freq_gran1) / (1. + (freq / freq_gran1) ** 4)

    ## Second granulation component
    sigma_gran2 = par_median[5]
    freq_gran2 = par_median[6]
    h_gran2 = (sigma_gran2 ** 2 / freq_gran2) / (1. + (freq / freq_gran2) ** 4)

    ## Global background model
    logger.info(w)
    w = np.zeros_like(freq) + w
    b1 = zeta * (h_long + h_gran1 + h_gran2) * r + w
    logger.info("Whitenoise is '" + str(w) + "'")
    if runGauss:
        b2 = (zeta * (h_long + h_gran1 + h_gran2) + g) * r + w
        return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
    else:
        return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w

def plotPSDTemp(runGauss,psd,backgroundModel):
    smoothedData = None

    pl.figure(figsize=(16, 7))
    pl.loglog(psd[0], psd[1], 'k', alpha=0.5)
    if smoothedData is not None:
        pl.plot(psd[0], smoothedData)
    else:
        logger.info("Smoothingdata is None!")

    pl.plot(psd[0], backgroundModel[0], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[1], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[2], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[3], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[4], 'b', linestyle='dashed', linewidth=2)
    withoutGaussianBackground = np.sum(backgroundModel[0:4], axis=0)
    fullBackground = np.sum(backgroundModel, axis=0)
    pl.plot(psd[0], fullBackground, 'c', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], withoutGaussianBackground, 'r', linestyle='solid', linewidth=3)

    pl.xlim(0.1, max(psd[0]))
    pl.ylim(np.mean(psd[1]) / 10 ** 6, max(psd[1]) * 1.2)
    pl.xticks(fontsize=16);
    pl.yticks(fontsize=16)
    pl.xlabel(r'Frequency [$\mu$Hz]', fontsize=18)
    pl.ylabel(r'PSD [ppm$^2$/$\mu$Hz]', fontsize=18)
    title = "Standardmodel" if runGauss else "Noise Backgroundmodel"
    title += ' KIC'
    pl.title(title)
    fig = pl.gcf()
    fig.canvas.set_window_title('Powerspectrum')

setup_logging()
logger = logging.getLogger(__name__)

powerSpectrum = False


input = "003744681_983"
filename = "../Sterndaten/RG_ENRICO/kplr" + input + "_COR_" + ("PSD_" if powerSpectrum else "") + "filt_inp.fits"
file = FitsReader(filename)
powerCalc = PowerspectraCalculator(file.getLightCurve())
powerCalc.kicID = input
plotPSD(powerCalc,True,True)

nuMaxCalc = NuMaxCalculator(file.getLightCurve())

nuMax = 61
photonNoise = 0.04
nyquist = 283.2116656017908

priorCalculator = PriorCalculator(nuMax,photonNoise)

logger.info("Priors")
logger.info("PhotonNoise: '" + str(priorCalculator.photonNoiseBoundary) + "'")
logger.info("First Harvey Amplitude: '" + str(priorCalculator.harveyAmplitudeBoundary) + "'")
logger.info("First Harvey Frequency: '" + str(priorCalculator.firstHarveyFrequencyBoundary) + "'")
logger.info("Second Harvey Amplitude: '" + str(priorCalculator.harveyAmplitudeBoundary) + "'")
logger.info("Second Harvey Frequency: '" + str(priorCalculator.secondHarveyFrequencyBoundary) + "'")
logger.info("Third Harvey Amplitude: '" + str(priorCalculator.harveyAmplitudeBoundary) + "'")
logger.info("Third Harvey Frequency: '" + str(priorCalculator.thirdHarveyFrequencyBoundary) + "'")
logger.info("Amplitude: '" + str(priorCalculator.oscillationAmplitudeBoundary) + "'")
logger.info("nuMax: '" + str(priorCalculator.nuMaxBoundary) + "'")
logger.info("Sigma: '" + str(priorCalculator.sigmaBoundary) + "'")

logger.info("Priors")
logger.info("PhotonNoise: '" + str(priorCalculator.photonNoise) + "'")
logger.info("First Harvey Amplitude: '" + str(priorCalculator.harveyAmplitude) + "'")
logger.info("First Harvey Frequency: '" + str(priorCalculator.firstHarveyFrequency) + "'")
logger.info("Second Harvey Amplitude: '" + str(priorCalculator.harveyAmplitude) + "'")
logger.info("Second Harvey Frequency: '" + str(priorCalculator.secondHarveyFrequency) + "'")
logger.info("Third Harvey Amplitude: '" + str(priorCalculator.harveyAmplitude) + "'")
logger.info("Third Harvey Frequency: '" + str(priorCalculator.thirdHarveyFrequency) + "'")
logger.info("Amplitude: '" + str(priorCalculator.oscillationAmplitude) + "'")
logger.info("nuMax: '" + str(nuMax) + "'")
logger.info("Sigma: '" + str(priorCalculator.sigma) + "'")

priors = []
priors.append(priorCalculator.photonNoiseBoundary)
priors.append(priorCalculator.harveyAmplitudeBoundary)
priors.append(priorCalculator.firstHarveyFrequencyBoundary)
priors.append(priorCalculator.harveyAmplitudeBoundary)
priors.append(priorCalculator.secondHarveyFrequencyBoundary)
priors.append(priorCalculator.harveyAmplitudeBoundary)
priors.append(priorCalculator.thirdHarveyFrequencyBoundary)
priors.append(priorCalculator.oscillationAmplitudeBoundary)
priors.append(priorCalculator.nuMaxBoundary)
priors.append(priorCalculator.sigmaBoundary)

lowerBounds = np.zeros(len(priors))
upperBounds = np.zeros(len(priors))

for i in range(0,len(priors) ):
    lowerBounds[i] = priors[i][0]
    upperBounds[i] = priors[i][1]

priors = np.array((lowerBounds,upperBounds)).transpose()

files = FileCreater(input, powerCalc.powerSpectralDensity, nyquist, priors)

median = []
median.append(priorCalculator.photonNoise)
median.append(priorCalculator.harveyAmplitude)
median.append(priorCalculator.firstHarveyFrequency)
median.append(priorCalculator.harveyAmplitude)
median.append(priorCalculator.secondHarveyFrequency)
median.append(priorCalculator.harveyAmplitude)
median.append(priorCalculator.thirdHarveyFrequency)
median.append(priorCalculator.oscillationAmplitude)
median.append(nuMax)
median.append(priorCalculator.sigma)

backgroundModel = createBackgroundModel(True, median, powerCalc.powerSpectralDensity, nyquist)
plotPSDTemp(True, powerCalc.powerSpectralDensity, backgroundModel)
#show()

proc = DiamondsProcess(strDiamondsExecFull, input, "0", "1")
proc.start()

