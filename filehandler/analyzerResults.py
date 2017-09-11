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
                resultDict["NuMaxCalc"]={}
                for key,(value,color) in self._nuMaxCalculator.marker.items():
                    resultDict["NuMaxCalc"][key]=value

                resultDict["NuMaxCalc"]["Nyquist"] = self._nuMaxCalculator.nyqFreq

            if len(self._diamondsResults.keys()) != 0:
                resultDict["Diamonds_Priors"] = {}
                resultDict["Diamonds"] = {}
                resultDict["Analysis"] = {}
                for key,value in self._diamondsResults.items():
                    resultDict["Diamonds_Priors"][key] = {}
                    resultDict["Diamonds"][key]={}
                    resultDict["Analysis"][key] = {}

                    for priorKey,priorValue in value.prior.getData(mode=key).items():
                        resultDict["Diamonds_Priors"][key][priorKey]=priorValue

                    resultDict["Diamonds"][key][strEvidenceSkillLog] = \
                        format(ufloat(value.evidence.getData(strEvidenceSkillLog)
                                      ,value.evidence.getData(strEvidenceSkillErrLog)))
                    resultDict["Diamonds"][key][strEvidenceSkillInfLog] = value.evidence.getData(strEvidenceSkillInfLog)

                    for backPriorKey,backPriorValue in value.summary.getData().items():
                        resultDict["Diamonds"][key][backPriorKey] = format(backPriorValue)
                        if backPriorValue/resultDict["Diamonds_Priors"][key][backPriorKey][0] < 1.05:
                            resultDict["Analysis"][key][backPriorKey] = "Not okay (Lower Limit!)"
                        elif backPriorValue / resultDict["Diamonds_Priors"][key][backPriorKey][1] > 0.95:
                            resultDict["Analysis"][key][backPriorKey] = "Not okay (Upper Limit!)"
                        else:
                            resultDict["Analysis"][key][backPriorKey] = "Okay"

            if len(self._diamondsRunner.status.items()) != 0:
                if "Diamonds" not in resultDict.keys():
                    resultDict["Diamonds"] = {}

                for key,value in self._diamondsRunner.status.items():
                    if key not in resultDict["Diamonds"].keys():
                        resultDict["Diamonds"][key]={}

                    resultDict["Diamonds"][key]["Status"] = value

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
                backgroundEvidence = ufloat_fromstr(resultDict["Diamonds"][strDiamondsModeFull][strEvidenceSkillLog])
                noiseBackground = ufloat_fromstr(resultDict["Diamonds"][strDiamondsModeNoise][strEvidenceSkillLog])

                evidence = backgroundEvidence-noiseBackground
                resultDict["Analysis"]["Bayes Factor"] = format(evidence)
                if evidence < 1:
                    resultDict["Analysis"]["Strength of evidence"] = "Inconclusive"
                elif 1 < evidence < 2.5:
                    resultDict["Analysis"]["Strength of evidence"] = "Weak evidence"
                elif 2.5 < evidence < 5:
                    resultDict["Analysis"]["Strength of evidence"] = "Moderate evidence"
                else:
                    resultDict["Analysis"]["Strength of evidence"] = "Strong evidence"

            self.logger.debug(resultDict)
            with open("results.json", 'w') as f:
                json.dump(resultDict, f)
