from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
from calculations.priorCalculations import PriorCalculator
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *
from filehandler.Diamonds.diamondsFileCreating import FileCreater
from filehandler.analyzerResults import AnalyserResults
from diamonds.diamondsProcesses import DiamondsProcess
from loghandler.loghandler import *
import logging

setup_logging()
logger = logging.getLogger(__name__)
#KeplerData
#input = "003656476_12"
#input = "004346201_18"
#input = "004351319_19"
#input = "004346201_18"
#input = '0603396438'
#RG_ENRICO
input = "004770846_1435" #works
input = "003744681_983" #works
input = "004448777_771" #works
input = "004659821_1181" #okayish
input = "004770846_1435" #okayish
input = "005184199_539" #works
input = "005356201_979" #failed
input = "005858947_2366" #not perfect, nuMax is a bit off
input = "006144777_350" #works
input = "007467630_1088" #perfect
input = "007581399_1298" #nuMax and Hosc to high
input = "008366239_1241" #okayish
#input = "008962923_2846"
#input = "009267654_634"
#input = "009332840_813"
#input = "009346602_873"
#input = "009574650_1445"
#input = "009882316_2399"
#input = "010777816_1965"
#input = "010866415_2167"
#input = "011550492_1262"
#input = "012008916_19"
#Corot -> Young stars
#input = "0223978308"
#Kepler -> Young stars
#input = "224321303"
#input = "224399118"
#input = "0223976028"
#input = "002437103_10"
powerSpectrum = False
#KeplerData
#filename = "../Sterndaten/KeplerData/kplr" + input + "_COR_" + ("PSD_" if powerSpectrum else "") + "filt_inp.fits"
#Young Stars
#filename = "../Sterndaten/CoRoT_lightcurves/G-type/" + input + "_LC_poly.txt"
#Kepler Young stars
filename = "../Sterndaten/k2data/g_like/EPIC_"+input+"_xy_ap1.0_2.0_3.0_4.0_fixbox_detrend.dat.txt"
#New data
#filename = "../Sterndaten/LC_CORR/kplr" + input + "_COR.fits"
#Reviewed Data by Enrico
filename = "../Sterndaten/RG_ENRICO/kplr" + input + "_COR_" + ("PSD_" if powerSpectrum else "") + "filt_inp.fits"

file = FitsReader(filename)
powerCalc = PowerspectraCalculator(np.conjugate(file.getLightCurve()))
AnalyserResults.Instance().setKicID(input)
AnalyserResults.Instance().setPowerSpectraCalculator(powerCalc)



powerCalc.kicID = input
p = plotLightCurve(powerCalc,2)
saveFigToResults("Lightcurve.png",p)
p = plotPSD(powerCalc,True,True,visibilityLevel=1)
saveFigToResults("PSD.png",p)

nuMaxCalc = NuMaxCalculator(file.getLightCurve())

nuMax = nuMaxCalc.computeNuMax()
marker = nuMaxCalc.marker
photonNoise = powerCalc.photonNoise
nyquist = nuMaxCalc.nyqFreq
AnalyserResults.Instance().setNuMaxCalculator(nuMaxCalc)

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
plotPSD(powerCalc,True,True,marker,visibilityLevel=1)

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

proc = DiamondsProcess(input)
proc.start()

diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value

if diamondsModel in [strFitModeNoiseBackground,strFitModeBayesianComparison]:
    result = Results(kicID=input,runID=strDiamondsModeNoise)
    p = plotPSD(result,False,False,visibilityLevel=1)
    saveFigToResults("PSD_Noise_fit.png",p)
    p = plotParameterTrend(result)
    saveFigToResults("Noise_Parametertrend.png",p)
    show(2)

if diamondsModel in [strFitModeFullBackground,strFitModeBayesianComparison]:
    result = Results(kicID=input,runID=strDiamondsModeFull)
    p = plotPSD(result,True,False,visibilityLevel=1)
    saveFigToResults("PSD_Full_Background_fit.png",p)
    p = plotParameterTrend(result)
    saveFigToResults("Full_Background_Parametertrend.png",p)
    show(2)

AnalyserResults.Instance().collectDiamondsResult()
AnalyserResults.Instance().performAnalysis()
