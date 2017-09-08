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
    def __init__(self):
        self.powerSpectraCalculator = None
        self.diamondsResults = {}
        self.diamondsRunner = {}
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
        self.powerSpectraCalculator = None
        self.diamondsResults = {}
        self.nuMaxCalculator = None
        self.diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self.diamondsRunner = {}
        self.images = {}


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
        return None

    def setNuMaxCalculator(self,calc):
        self.nuMaxCalculator = calc

    def setPowerSpectraCalculator(self,calc):
        self.powerSpectraCalculator = calc

    def setDiamondsRunner(self,runner):
        self.diamondsRunner=runner

    def performAnalysis(self):
        starType = "YS" if Settings.Instance().getSetting(strDataSettings,strSectStarType).value == strStarTypeYoungStar else "RG"
        analyserResultsPath = Settings.Instance().getSetting(strMiscSettings, strSectAnalyzerResults).value
        analyserResultsPath += "/" + starType + "_" +self.kicID +"/"
        imagePath = analyserResultsPath + "images/"
        resultDict = {}

        if not os.path.exists(analyserResultsPath):
            os.makedirs(analyserResultsPath)

        if not os.path.exists(imagePath):
            os.makedirs(imagePath)

        with cd(analyserResultsPath):
            if self.powerSpectraCalculator is not None:
                np.savetxt("Lightcurve.txt",self.powerSpectraCalculator.lightCurve,header="Time(days) Flux")
                np.savetxt("PSD.txt", self.powerSpectraCalculator.powerSpectralDensity, header="Frequency(uHz) PSD(ppm^2/uHz)")

            if self.nuMaxCalculator is not None:
                resultDict["NuMaxCalc"]={}
                for key,(value,color) in self.nuMaxCalculator.marker.items():
                    resultDict["NuMaxCalc"][key]=value

                resultDict["NuMaxCalc"]["Nyquist"] = self.nuMaxCalculator.nyqFreq

            if len(self.diamondsResults.keys()) != 0:
                resultDict["Diamonds_Priors"] = {}
                resultDict["Diamonds"] = {}
                resultDict["Analysis"] = {}
                for key,value in self.diamondsResults.items():
                    resultDict["Diamonds_Priors"][key] = {}
                    resultDict["Diamonds"][key]={}
                    resultDict["Analysis"][key] = {}

                    for priorKey,priorValue in value.prior.getData().items():
                        resultDict["Diamonds_Priors"][key][priorKey]=priorValue

                    resultDict["Diamonds"][key][strEvidenceSkillLog] = \
                        format(ufloat(value.evidence.getData(strEvidenceSkillLog)
                                      ,value.evidence.getData(strEvidenceSkillErrLog)))
                    resultDict["Diamonds"][key][strEvidenceSkillInfLog] = value.evidence.getData(strEvidenceSkillInfLog)

                    for backPriorKey,backPriorValue in value.summary.getData(priorData=True).items():
                        resultDict["Diamonds"][key][backPriorKey] = format(backPriorValue)
                        if backPriorValue/resultDict["Diamonds_Priors"][key][backPriorKey][0] < 1.05:
                            resultDict["Analysis"][key][backPriorKey] = "Not okay (Lower Limit!)"
                        elif backPriorValue / resultDict["Diamonds_Priors"][key][backPriorKey][1] > 0.95:
                            resultDict["Analysis"][key][backPriorKey] = "Not okay (Upper Limit!)"
                        else:
                            resultDict["Analysis"][key][backPriorKey] = "Okay"

            if len(self.diamondsRunner.status.items()) != 0:
                if "Diamonds" not in resultDict.keys():
                    resultDict["Diamonds"] = {}

                for key,value in self.diamondsRunner.status.items():
                    if key not in resultDict["Diamonds"].keys():
                        resultDict["Diamonds"][key]={}

                    resultDict["Diamonds"][key]["Status"] = value

            if len(self.images.keys()) != 0:
                with cd(imagePath):
                    for imageName,figure in self.images.items():
                        try:
                            figure.save(imageName)
                        except:
                            try:
                                figure.savefig(imageName)
                            except:
                                self.logger.error("File with name "+imageName+" doesnt seem to be a ggplot or matplotlib type")
                                raise

            if self.diamondsModel == strFitModeBayesianComparison:
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
