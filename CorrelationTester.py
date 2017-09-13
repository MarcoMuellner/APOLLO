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
import traceback

starList = []

#RG_ENRICO
starList.append("004770846_1435") #works
starList.append("003744681_983") #works
starList.append("004448777_771") #works
starList.append("004659821_1181") #okayish
starList.append("004770846_1435") #okayish
starList.append("005184199_539") #works
starList.append("005356201_979") #failed
starList.append("005858947_2366") #not perfect, nuMax is a bit off
starList.append("006144777_350") #works
starList.append("007467630_1088") #perfect
starList.append("007581399_1298") #nuMax and Hosc to high
starList.append("008366239_1241") #okayish
starList.append("008962923_2846")
starList.append("009267654_634")
starList.append("009332840_813")
starList.append("009346602_873")
starList.append("009574650_1445")
starList.append("009882316_2399")
starList.append("010777816_1965")
starList.append("010866415_2167")
starList.append("011550492_1262")
starList.append("012008916_19")

yStarList = []
yStarList.append("224321303")
yStarList.append("224399118")
yStarList.append("0223976028")
yStarList.append("002437103_10")

powerSpectrum = False

setup_logging()
logger = logging.getLogger(__name__)

for i in starList:
    try:
        logger.info("************************************")
        logger.info("STARTING STAR "+i)
        logger.info("************************************")


        filename = "../Sterndaten/RG_ENRICO/kplr" + i + "_COR_" + ("PSD_" if powerSpectrum else "") + "filt_inp.fits"
        #filename = "../Sterndaten/k2data/g_like/EPIC_" + i + "_xy_ap1.0_2.0_3.0_4.0_fixbox_detrend.dat.txt"
        AnalyserResults.Instance().kicID = i

        if not AnalyserResults.Instance().diamondsRunNeeded:
            logger.info("Star "+i+" allready done, reading next star")
            continue


        #read and convert
        file = FitsReader(filename)

        powerCalc = PowerspectraCalculator(np.conjugate(file.getLightCurve()))
        powerCalc.kicID = i
        AnalyserResults.Instance().powerSpectracalculator = powerCalc

        plotLightCurve(powerCalc,2,fileName="Lightcurve.png")
        plotPSD(powerCalc,True,True,visibilityLevel=2,fileName="PSD.png")
        #
        #compute nuMax
        nuMaxCalc = NuMaxCalculator(file.getLightCurve())
        AnalyserResults.Instance().nuMaxCalculator = nuMaxCalc

        nuMax = nuMaxCalc.computeNuMax()
        marker = nuMaxCalc.marker
        photonNoise = powerCalc.photonNoise
        nyquist = nuMaxCalc.nyqFreq
        #
        #compute Priors
        priorCalculator = PriorCalculator(nuMax,photonNoise,powerCalc)
        plotPSD(powerCalc,True,True,marker,visibilityLevel=1,fileName="PSD_filterfrequencies.png")

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

        for x in range(0, len(priors)):
            lowerBounds[x] = priors[x][0]
            upperBounds[x] = priors[x][1]

        priors = np.array((lowerBounds, upperBounds)).transpose()

        #create Files and start process
        files = FileCreater(i, powerCalc.powerSpectralDensity, nyquist, priors)

        proc = DiamondsProcess(i)
        proc.start()
        AnalyserResults.Instance().diamondsRunner = proc
        #
        #Create results
        diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value

        if diamondsModel in [strFitModeNoiseBackground, strFitModeBayesianComparison]:
            result = Results(kicID=i, runID=strDiamondsModeNoise)
            p = plotPSD(result, False, False, visibilityLevel=1,fileName="PSD_Noise_fit.png")
            p = plotParameterTrend(result,fileName="Noise_Parametertrend.png")
            show(2)

        if diamondsModel in [strFitModeFullBackground, strFitModeBayesianComparison]:
            result = Results(kicID=i, runID=strDiamondsModeFull)
            p = plotPSD(result, True, False, visibilityLevel=1,fileName="PSD_Full_Background_fit.png")
            p = plotParameterTrend(result,fileName="Full_Background_Parametertrend.png")
            show(2)

        AnalyserResults.Instance().collectDiamondsResult()
        AnalyserResults.Instance().performAnalysis()
        #
    except Exception as e:
        logger.error("Failed to run Correlation Test for "+i)
        logger.error(e)
        logger.error(traceback.format_exc())
        try:
            AnalyserResults.Instance().performAnalysis()
        except Exception as d:
            logger.error("Cannot proceed with analysis!")
            logger.error(d)
            logger.error(traceback.format_exc())
            raise ValueError
        continue

