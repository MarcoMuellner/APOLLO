import json
import logging

import numpy as np
from matplotlib.pyplot import Figure
from uncertainties import ufloat, ufloat_fromstr
from collections import OrderedDict

from background.backgroundResults import BackgroundResults
from res.strings import *
from settings.settings import Settings
from support.directoryManager import cd
from support.singleton import Singleton


@Singleton
class ResultsWriter:
    '''
    This class gathers all results from the DIAMONDS run and the ACF function. After calling the constructor, which is
    done by calling AnalyserResults.Instance() for the first time, you can easily set the results from everywhere in
    the code by calling the different methods (see documentation of the methods). This class is only accessible via
    Singleton pattern.

    To finish of the analysis, you need to call performAnalysis() at the end of your analysis. Be careful, this instance
    doesn't really die. This should not be a problem though, because the data saved is quite miniscule.
    '''
    def __init__(self,*args):
        '''
        Constructor of AnalyserResults. Only called by Singleton Constructor
        '''
        self.logger = logging.getLogger(__name__)
        self.defaultPath = os.getcwd()

        if len(args) == 1:
            self.kicID = args[0][0]


    def addImage(self,name,figure):
        '''
        Adds an image to the results list. Basically only called from saveFigToResults by plotFunctions
        :param name: Name of the image
        :type name: str
        :param figure: Figure object, provided by matplotlib
        :type figure: Figure
        '''
        self._images[name]=figure

    @property
    def kicID(self):
        '''
        Property for the KicID
        :return: The KicID of the star
        :rtype: str
        '''
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        '''
        Setter property for the KicID. Resets all results and calls checkRunNeeded for what results are already
        available. Use the diamondsRunNeeded flag to check if you need to check if something is not already available.
        :param value:KicID of the star
        :type value: str
        '''
        self._kicID = value
        self.powerSpectraCalculator = None
        self.diamondsRunner = None
        self.nuMaxCalculator = None
        self._diamondsResults = OrderedDict()
        self._diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self._images = OrderedDict()

        #try to read old values and set flag accordingly
        if self._kicID is not None:
            self.diamondsRunNeeded = self._checkRunNeeded()

    def _checkRunNeeded(self):
        '''
        Checks if a run is needed and returns a flag, which can be used to determine which things need to be run.
        For this it looks in the results it created beforehand at some time and checks which results are available.

        For now it only checks if Priors and DIAMONDS results are available and checks if these results are fine.
        :return: A boolean which describes if the run is needed. True --> run needs to be done.
        :rtype:bool
        '''
        starType = "YS" if Settings.Instance().getSetting(strDataSettings,
                                                          strSectStarType).value == strStarTypeYoungStar else "RG"
        analyserResultsPath = Settings.Instance().getSetting(strMiscSettings, strSectAnalyzerResults).value
        forceDiamondsRun = ("True" == Settings.Instance().getSetting(strMiscSettings, strSectForceDiamondsRun).value)

        analyserResultsPath += "/" + starType + "_" + self._kicID + "/results.json"

        if forceDiamondsRun or not os.path.exists(analyserResultsPath):
            return True

        with open(analyserResultsPath,'rt') as f:
            resultDict = json.load(f)

        try:
            priorContentFailed = self._checkPriorContent(resultDict,strAnalyzerResSectDiamondsPriors)
        except:
            self.logger.info("Diamonds modes not in results file, full programm needed!")
            priorContentFailed = True

        try:
            resultContentFailed = self._checkPriorContent(resultDict, strAnalyseSectDiamonds, 3)
        except:
            self.logger.info("Diamonds results are not yet created, full programm needed")
            resultContentFailed = True

        resultFailed = False
        try:
            for key,newDict in resultDict[strAnalyzerResSectAnalysis].items():
                if isinstance(newDict,dict):
                    for name,okayValue in newDict.items():
                        if okayValue != "Okay":
                            self.logger.info("Diamonds results for name "+name+" is not okay, rerunning!")
                            resultFailed = True
        except:
            self.logger.info("Diamonds resultOkay doesn't have an Analyzer section, full programm needed")
            resultFailed = True

        self.logger.info("Results Content is (Analyzer section) "+str(resultContentFailed))
        self.logger.info("Prior Content is "+str(priorContentFailed))
        self.logger.info("Result okay is "+str(resultFailed))
        self.logger.info("Need for DIAMONDS run is "+str(resultContentFailed or priorContentFailed or resultFailed))
        return (resultContentFailed or priorContentFailed or resultFailed)


    def _checkPriorContent(self, resultDict, sectName, numberOffset=0):
        '''
        Checks if priors are created for modes
        :param resultDict: A dictionary containing mode and number of items in dict
        :type resultDict: dict
        :param sectName: Section Name for the data --> overreaching category in resultDict (i.e. "Diamonds")
        :type sectName:str
        :param numberOffset: Offsetparameter in count. By Default it will use 7 for noise, 10 for full. This parameter
        can offset both at the same time
        :type numberOffset:int
        :return:True if content is valid, False if not
        :rtype:bool
        '''
        modes = {strDiamondsModeNoise:7+numberOffset,strDiamondsModeFull:10+numberOffset}

        for mode,number in modes.items():
            if self._diamondsModel in [mode, strFitModeBayesianComparison] and len(resultDict[sectName][mode]) not in [7,10]:
                self.logger.info("Sector name: " + sectName)
                self.logger.info("Mode "+mode+" not in results, run full programm")
                return True

        return False

    def collectDiamondsResult(self):
        '''
        This method gatheres the Results of the DIAMONDS run using the Results class.See the Results class for
        further information. Checks first if the run was even necessary using the settings
        '''
        if self._kicID is None:
            self.logger.error("You need to set the KicID before you can access the results!")
            raise ValueError

        modeDict = {strFitModeFullBackground:strDiamondsModeFull,
                    strFitModeNoiseBackground:strDiamondsModeNoise}

        for fitMode,runID in modeDict.items():
            if self._diamondsModel in [fitMode, strFitModeBayesianComparison]:
                self._diamondsResults[runID] = BackgroundResults(kicID=self._kicID, runID=runID)
            else:
                self._diamondsResults[runID] = None


    def performAnalysis(self):
        '''
        This method gatheres up all images and results set within the instance. For this it creates a dictionary, with
        overreaching categories. The dict is than saved as a json file in the results cluster. The structure of the file
        will look like this:

        -NuMaxCalc
        -- InitialFilter:
        -- First Filter:
        -- Second Filter:
        -- Nyquist:
        -Diamonds_Priors:
        --Mode
        ---Priors (count depending on mode)
        -- Second Mode (if one was run)
        ---Priors second mode
        -Diamonds
        --Mode
        ---Prior values fitted
        -- Second Mode (if one was run)
        ---Prior values fitted
        -Analysis
        --Mode
        ---Priors status
        -- Second Mode (if one was run)
        ---Priors status
        --Bayes Factor:
        --Strength of evidence:

        '''
        starType = "YS" if Settings.Instance().getSetting(strDataSettings,strSectStarType).value == strStarTypeYoungStar else "RG"
        analyserResultsPath = os.path.abspath(Settings.Instance().getSetting(strMiscSettings, strSectAnalyzerResults).value)
        analyserResultsPath += "/" + starType + "_" +self._kicID + "/"
        imagePath = os.path.abspath(analyserResultsPath) + "/images/"
        resultDict = OrderedDict()

        paths = [analyserResultsPath, imagePath]
        for i in paths:
            if not os.path.exists(i):
                os.makedirs(i)

        with cd(analyserResultsPath):
            self._saveRawData(analyserResultsPath)

            resultDict = self._createSectionsInMap(resultDict)

            resultDict = self._saveMetaFrequencies(resultDict)

            resultDict = self._savePriorStuff(resultDict)

            resultDict = self._saveStatus(resultDict)

            self._saveImages(imagePath)

            resultDict = self._saveBayesValue(resultDict)

            self.logger.debug(resultDict)
            with open("results.json", 'w') as f:
                json.dump(resultDict, f)

    @property
    def powerSpectraCalculator(self):
        return self._powerSpectraCalculator

    @powerSpectraCalculator.setter
    def powerSpectraCalculator(self, value):
        self._powerSpectraCalculator = value

    @property
    def nuMaxCalculator(self):
        return self._nuMaxCalculator

    @nuMaxCalculator.setter
    def nuMaxCalculator(self, value):
        self._nuMaxCalculator = value

    @property
    def diamondsRunner(self):
        return self._diamondsRunner

    @diamondsRunner.setter
    def diamondsRunner(self, value):
        self._diamondsRunner = value

    @property
    def diamondsRunNeeded(self):
        return self._diamondsRunNeeded

    @diamondsRunNeeded.setter
    def diamondsRunNeeded(self, value):
        self._diamondsRunNeeded = value

    def _getBayesFactorEvidence(self,resultDict):
        backgroundEvidence = ufloat_fromstr(
            resultDict[strAnalyseSectDiamonds][strDiamondsModeFull][strEvidSkillLog])
        noiseBackground = ufloat_fromstr(resultDict[strAnalyseSectDiamonds][strDiamondsModeNoise][strEvidSkillLog])

        evidence = backgroundEvidence - noiseBackground
        resultDict[strAnalyzerResSectAnalysis][strAnalyzerResValBayes] = format(evidence)
        if evidence < 1:
            conclusion = "Inconclusive"
        elif 1 < evidence < 2.5:
            conclusion = "Weak evidence"
        elif 2.5 < evidence < 5:
            conclusion = "Moderate evidence"
        else:
            conclusion = "Strong evidence"

        return conclusion

    def _saveRawData(self,path):
        """
        saves the rawData to path
        :param path: path to the results
        :type path: str
        """
        with cd(path):
            if self.powerSpectraCalculator is not None:
                np.savetxt("Lightcurve.txt", self.powerSpectraCalculator.lightCurve, header="Time(days) Flux")
                np.savetxt("PSD.txt", self.powerSpectraCalculator.powerSpectralDensity, header="Frequency(uHz) PSD(ppm^2/uHz)")

    def _saveMetaFrequencies(self,resultDict):
        """
        Saves characteristic frequencies of the analysis. This includes the three iterative filter frequencies from
        the iterative fit as well as the Nyquist frequency
        :param resultDict: resultdict on which to append to
        :return: resultdict containting the data
        """
        if self.nuMaxCalculator is not None:
            for key, (value, color) in self.nuMaxCalculator.marker.items():
                resultDict[strAnalyzerResSectNuMaxCalc][key] = value

            resultDict[strAnalyzerResSectNuMaxCalc]["Nyquist"] = self.powerSpectraCalculator.nyqFreq

        return resultDict

    def _createSectionsInMap(self,resultDict):

        resultDict[strAnalyzerResSectNuMaxCalc] = OrderedDict()

        for key, value in self._diamondsResults.items():

            #sections in resultFile
            priorKeys = [strAnalyzerResSectDiamondsPriors
                , strAnalyzerResSectDiamondsPriors
                , strAnalyseSectDiamonds
                , strAnalyzerResSectAnalysis]

            #adding the sections in the resultFile
            for i in priorKeys:

                if i not in resultDict.keys():
                    resultDict[i] = OrderedDict()

                if key not in resultDict[i].keys():
                    resultDict[i][key] = OrderedDict()

        if len(self.diamondsRunner.status.items()) != 0:
            if strAnalyseSectDiamonds not in resultDict.keys():
                resultDict[strAnalyseSectDiamonds] = OrderedDict()

            for key, value in self.diamondsRunner.status.items():
                if key not in resultDict[strAnalyseSectDiamonds].keys():
                    resultDict[strAnalyseSectDiamonds][key] = OrderedDict()

        return resultDict

    def _savePriorStuff(self,resultDict):
        for key, value in self._diamondsResults.items():
            resultDict[strAnalyzerResSectDiamondsPriors][key] = value.prior.getData(mode=key)

            resultDict[strAnalyseSectDiamonds][key][strEvidSkillLog] = format(
value.evidence.getData(strEvidSkillLogWithErr))
            resultDict[strAnalyseSectDiamonds][key][strEvidSkillInfLog] = value.evidence.getData(strEvidSkillInfLog)

            for backPriorKey, backPriorValue in value.summary.getData().items():
                try:
                    resultDict[strAnalyseSectDiamonds][key][backPriorKey] = format(backPriorValue)
                    if backPriorValue / resultDict[strAnalyzerResSectDiamondsPriors][key][backPriorKey][0] < 1.05 or \
                            backPriorValue / resultDict[strAnalyzerResSectDiamondsPriors][key][backPriorKey][1] > 0.95:
                        resultDict[strAnalyzerResSectAnalysis][key][backPriorKey] = "Not okay"
                    else:
                        resultDict[strAnalyzerResSectAnalysis][key][backPriorKey] = "Okay"
                except KeyError:
                    self.logger.error("Failed fo find value for key: " + backPriorKey)
                    self.logger.error("Failed fo find value for run: " + key)
                    self.logger.error("Failed fo find value for section: " + strAnalyzerResSectDiamondsPriors)

        return resultDict

    def _saveStatus(self,resultDict):
        if len(self.diamondsRunner.status.items()) != 0:
            for key, value in self.diamondsRunner.status.items():
                resultDict[strAnalyseSectDiamonds][key]["Status"] = value

        return resultDict

    def _saveImages(self,imagePath):
        if len(self._images.keys()) != 0:
            with cd(imagePath):
                for imageName, figure in self._images.items():
                    try:
                        figure.save(imageName)
                    except:
                        try:
                            figure.savefig(imageName)
                        except:
                            self.logger.error(
                                "File with name " + imageName + " doesnt seem to be a ggplot or matplotlib type")
                            raise IOError

    def _saveBayesValue(self,resultDict):
        if self._diamondsModel == strFitModeBayesianComparison:
            resultDict[strAnalyzerResSectAnalysis][strAnalyzerResValStrength] = self._getBayesFactorEvidence(resultDict)
        return resultDict

