from support.singleton import Singleton
from settings.settings import Settings
from support.strings import *
from filehandler.Diamonds.diamondsResultsFile import Results
from support.directoryManager import cd
import logging
from uncertainties import ufloat,ufloat_fromstr
import numpy as np
import json


@Singleton
class AnalyserResults:
    """
    This class allows for a single place to create a full report on the data gathered during one DIAMONDS run.
    It gatheres different objects from which it will call the results up and sets it up in a simple json format
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.kicID = None

    def addImage(self,name,figure):
        self._images[name]=figure
        pass

    @property
    def kicID(self):
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        self._kicID = value
        self.powerSpectraCalculator = None
        self.diamondsRunner = None
        self.nuMaxCalculator = None
        self._diamondsResults = {}
        self._diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self._images = {}
        #try to read old values and set flag accordingly
        if self._kicID is not None:
            self.diamondsRunNeeded = self._checkRunNeeded()


    def _checkRunNeeded(self):
        starType = "YS" if Settings.Instance().getSetting(strDataSettings,
                                                          strSectStarType).value == strStarTypeYoungStar else "RG"
        analyserResultsPath = Settings.Instance().getSetting(strMiscSettings, strSectAnalyzerResults).value
        forceDiamondsRun = "True" in Settings.Instance().getSetting(strMiscSettings, strSectForceDiamondsRun).value

        analyserResultsPath += "/" + starType + "_" + self._kicID + "/results.json"

        if forceDiamondsRun or not os.path.exists(analyserResultsPath):
            return True

        with open(analyserResultsPath,'rt') as f:
            resultDict = json.load(f)

        try:
            priorContent = self._checkPriorContent(resultDict,strAnalyzerResSectDiamondsPriors)
        except:
            self.logger.info("Diamonds modes not in results file, full programm needed!")
            priorContent = True

        try:
            resultContent = self._checkPriorContent(resultDict,strAnalyzerResSectDiamonds,3)
        except:
            self.logger.info("Diamonds results are not yet created, full programm needed")
            resultContent = True

        resultOkay = False
        try:
            for key,newDict in resultDict[strAnalyzerResSectAnalysis].items():
                if isinstance(newDict,dict):
                    for name,okayValue in newDict.items():
                        if okayValue != "Okay":
                            self.logger.info("Diamonds results for name "+name+" is not okay, rerunning!")
                            resultOkay = True
        except:
            self.logger.info("Diamonds resultOkay doesn't have an Analyzer section, full programm needed")
            resultOkay = True

        self.logger.info("Need for DIAMONDS run is "+str(resultContent or priorContent or resultOkay))
        return (resultContent or priorContent or resultOkay)


    def _checkPriorContent(self,resultDict,sectName,numberOffset=0):
        modes = {strDiamondsModeNoise:7+numberOffset,strDiamondsModeFull:10+numberOffset}

        for mode,number in modes.items():
            if self._diamondsModel in [mode, strFitModeBayesianComparison] and len(resultDict[sectName][mode]) != number:
                self.logger.info("Sector name: " + sectName)
                self.logger.info("Mode "+mode+" not in results, run full programm")
                return True

        return False



    @property
    def powerSpectraCalculator(self):
        return self._powerSpectraCalculator

    @powerSpectraCalculator.setter
    def powerSpectraCalculator(self,value):
        self._powerSpectraCalculator = value

    @property
    def nuMaxCalculator(self):
        return self._nuMaxCalculator

    @nuMaxCalculator.setter
    def nuMaxCalculator(self,value):
        self._nuMaxCalculator = value

    @property
    def diamondsRunner(self):
        return self._diamondsRunner

    @diamondsRunner.setter
    def diamondsRunner(self,value):
        self._diamondsRunner = value

    @property
    def diamondsRunNeeded(self):
        return self._diamondsRunNeeded

    @diamondsRunNeeded.setter
    def diamondsRunNeeded(self,value):
        self._diamondsRunNeeded = value

    def collectDiamondsResult(self):
        if self._kicID is None:
            self.logger.error("You need to set the KicID before you can access the results!")
            raise ValueError

        if self._diamondsModel in [strFitModeFullBackground, strFitModeBayesianComparison]:
            self._diamondsResults[strDiamondsModeFull] = Results(kicID=self._kicID, runID=strDiamondsModeFull)
        else:
            self._diamondsResults[strDiamondsModeFull] = None

        if self._diamondsModel in [strFitModeNoiseBackground, strFitModeBayesianComparison]:
            self._diamondsResults[strDiamondsModeNoise] = Results(kicID=self._kicID, runID=strDiamondsModeNoise)
        else:
            self._diamondsResults[strDiamondsModeNoise] = None


    def performAnalysis(self):
        starType = "YS" if Settings.Instance().getSetting(strDataSettings,strSectStarType).value == strStarTypeYoungStar else "RG"
        analyserResultsPath = Settings.Instance().getSetting(strMiscSettings, strSectAnalyzerResults).value
        analyserResultsPath += "/" + starType + "_" +self._kicID + "/"
        imagePath = analyserResultsPath + "images/"
        resultDict = {}

        if not os.path.exists(analyserResultsPath):
            os.makedirs(analyserResultsPath)

        if not os.path.exists(imagePath):
            os.makedirs(imagePath)

        with cd(analyserResultsPath):
            if self._powerSpectraCalculator is not None:
                np.savetxt("Lightcurve.txt", self._powerSpectraCalculator.lightCurve, header="Time(days) Flux")
                np.savetxt("PSD.txt", self._powerSpectraCalculator.powerSpectralDensity, header="Frequency(uHz) PSD(ppm^2/uHz)")

            if self._nuMaxCalculator is not None:
                resultDict[strAnalyzerResSectNuMaxCalc]={}
                for key,(value,color) in self._nuMaxCalculator.marker.items():
                    resultDict[strAnalyzerResSectNuMaxCalc][key]=value

                resultDict[strAnalyzerResSectNuMaxCalc]["Nyquist"] = self._nuMaxCalculator.nyqFreq

            if len(self._diamondsResults.keys()) != 0:
                resultDict[strAnalyzerResSectDiamondsPriors] = {}
                resultDict[strAnalyzerResSectDiamonds] = {}
                resultDict[strAnalyzerResSectAnalysis] = {}
                for key,value in self._diamondsResults.items():
                    resultDict[strAnalyzerResSectDiamondsPriors][key] = {}
                    resultDict[strAnalyzerResSectDiamonds][key]={}
                    resultDict[strAnalyzerResSectAnalysis][key] = {}

                    for priorKey,priorValue in value.prior.getData(mode=key).items():
                        resultDict[strAnalyzerResSectDiamondsPriors][key][priorKey]=priorValue

                    resultDict[strAnalyzerResSectDiamonds][key][strEvidenceSkillLog] = \
                        format(ufloat(value.evidence.getData(strEvidenceSkillLog)
                                      ,value.evidence.getData(strEvidenceSkillErrLog)))
                    resultDict[strAnalyzerResSectDiamonds][key][strEvidenceSkillInfLog] = value.evidence.getData(strEvidenceSkillInfLog)

                    for backPriorKey,backPriorValue in value.summary.getData().items():
                        resultDict[strAnalyzerResSectDiamonds][key][backPriorKey] = format(backPriorValue)
                        if backPriorValue/resultDict[strAnalyzerResSectDiamondsPriors][key][backPriorKey][0] < 1.05:
                            resultDict[strAnalyzerResSectAnalysis][key][backPriorKey] = "Not okay (Lower Limit!)"
                        elif backPriorValue / resultDict[strAnalyzerResSectDiamondsPriors][key][backPriorKey][1] > 0.95:
                            resultDict[strAnalyzerResSectAnalysis][key][backPriorKey] = "Not okay (Upper Limit!)"
                        else:
                            resultDict[strAnalyzerResSectAnalysis][key][backPriorKey] = "Okay"

            if len(self._diamondsRunner.status.items()) != 0:
                if strAnalyzerResSectDiamonds not in resultDict.keys():
                    resultDict[strAnalyzerResSectDiamonds] = {}

                for key,value in self._diamondsRunner.status.items():
                    if key not in resultDict[strAnalyzerResSectDiamonds].keys():
                        resultDict[strAnalyzerResSectDiamonds][key]={}

                    resultDict[strAnalyzerResSectDiamonds][key]["Status"] = value

            if len(self._images.keys()) != 0:
                with cd(imagePath):
                    for imageName,figure in self._images.items():
                        try:
                            figure.save(imageName)
                        except:
                            try:
                                figure.savefig(imageName)
                            except:
                                self.logger.error("File with name "+imageName+" doesnt seem to be a ggplot or matplotlib type")
                                raise

            if self._diamondsModel == strFitModeBayesianComparison:
                backgroundEvidence = ufloat_fromstr(resultDict[strAnalyzerResSectDiamonds][strDiamondsModeFull][strEvidenceSkillLog])
                noiseBackground = ufloat_fromstr(resultDict[strAnalyzerResSectDiamonds][strDiamondsModeNoise][strEvidenceSkillLog])

                evidence = backgroundEvidence-noiseBackground
                resultDict[strAnalyzerResSectAnalysis][strAnalyzerResValBayes] = format(evidence)
                if evidence < 1:
                    resultDict[strAnalyzerResSectAnalysis][strAnalyzerResValStrength] = "Inconclusive"
                elif 1 < evidence < 2.5:
                    resultDict[strAnalyzerResSectAnalysis][strAnalyzerResValStrength] = "Weak evidence"
                elif 2.5 < evidence < 5:
                    resultDict[strAnalyzerResSectAnalysis][strAnalyzerResValStrength] = "Moderate evidence"
                else:
                    resultDict[strAnalyzerResSectAnalysis][strAnalyzerResValStrength] = "Strong evidence"

            self.logger.debug(resultDict)
            with open("results.json", 'w') as f:
                json.dump(resultDict, f)
