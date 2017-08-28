from support.singleton import Singleton
from settings.settings import Settings
from support.strings import *
from filehandler.Diamonds.diamondsResultsFile import Results
from support.directoryManager import cd
import logging
import numpy as np


@Singleton
class AnalyserResults:
    def __init__(self):
        self.powerSpectraCalculator = None
        self.diamondsResults = {}
        self.nuMaxCalculator = None
        self.diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self.kicID = None
        self.images = {}
        self.logger = logging.getLogger(__name__)

    def addImage(self,name,figure):
        self.images[name]=figure
        pass

    def setKicID(self,kicID):
        self.kicID = kicID

    def collectDiamondsResult(self):
        if self.kicID is None:
            self.logger.error("You need to set the KicID before you can access the results!")
            raise ValueError

        self.diamondsResultsPath = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value

        if self.diamondsModel in [strFitModeFullBackground,strFitModeBayesianComparison]:
            resultsPath = self.diamondsResultsPath + "KIC" + self.kicID + "/" + strDiamondsModeFull + "/"

            if not os.path.exists(resultsPath):
                self.logger.error("There are no results yet for mode "+strDiamondsModeFull)
                self.diamondsResults[strDiamondsModeFull] = None
                return

            self.diamondsResults[strDiamondsModeFull] = Results(kicID=self.kicID, runID=strDiamondsModeFull)

        if self.diamondsModel in [strFitModeNoiseBackground,strFitModeBayesianComparison]:
            resultsPath = self.diamondsResultsPath + "KIC" + self.kicID + "/" + strDiamondsModeNoise + "/"

            if not os.path.exists(resultsPath):
                self.logger.error("There are no results yet for mode "+strDiamondsModeNoise)
                self.diamondsResults[strDiamondsModeNoise] = None
                return

            self.diamondsResults[strDiamondsModeNoise] = Results(kicID=self.kicID, runID=strDiamondsModeNoise)
        pass

    def setNuMaxCalculator(self,calc):
        self.nuMaxCalculator = calc
        pass

    def setPowerSpectraCalculator(self,calc):
        self.powerSpectraCalculator = calc
        pass

    def performAnalysis(self):
        analyserResultsPath = Settings.Instance().getSetting(strMiscSettings, strSectAnalyzerResults).value
        analyserResultsPath += self.kicID +"/"
        resultDict = {}

        if not os.path.exists(analyserResultsPath):
            os.makedirs(analyserResultsPath)

        with cd(analyserResultsPath):
            if self.powerSpectraCalculator is not None:
                np.savetxt("Lightcurve.txt",self.powerSpectraCalculator.getLightCurve(),header="Time(days) Flux")
                np.savetxt("PSD.txt",self.powerSpectraCalculator.getPSD(),header="Frequency(uHz) PSD(ppm^2/uHz)")

            if self.nuMaxCalculator is not None:
                resultDict["NuMaxCalc"]=""
                for key,value in self.nuMaxCalculator.marker:
                    resultDict["NuMaxCalc/"+key] = value

                resultDict["NuMaxCalc/Nyquist"] = self.nuMaxCalculator.getNyquistFrequency()

            if len(self.diamondsResults.keys()) != 0:
                resultDict["Diamonds"] = ""
                for key,value in self.diamondsResults:
                    for priorKey,priorValue in value.getPrior().getData():
                        resultDict["Diamonds/"+key+"/"+priorKey]=priorValue
                    for evidenceKey,evidenceValue in value.getEvidence().getData():
                        resultDict["Diamonds/"+key+"/"+evidenceKey]=evidenceValue

            if len(self.images.keys()) != 0:
                for imageName,figure in self.images:
                    figure.savefig(imageName)

        self.logger.debug(resultDict)
