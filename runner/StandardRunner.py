from background.backgroundResults import BackgroundResults

from evaluators.nuMaxEvaluator import NuMaxEvaluator
from evaluators.inputDataEvaluator import InputDataEvaluator
from evaluators.priorEvaluator import PriorEvaluator
from background.backgroundProcess import BackgroundProcess
from background.fileModels.backgroundFileCreator import BackgroundFileCreator
from readerWriter.inputFileReader import InputFileReader
from plotter.plotFunctions import *
from support.directoryManager import cd
from fitter.fitFunctions import *
import signal
import sys
import traceback


class StandardRunner():
    '''
    The Standard Runner class represents a full run for one star. It contains all the results and information about the
    star and includes various subclasses that are accessible within this class, especially in the analyzerResult class.
    '''
    def __init__(self,kicID, filePath,fileName = None):
        '''
        The constructor of the class. According to the kicID and filePath, the constructor will look within filePath
        for the proper file that represents the kicID.

        It will use the most probable file available within the directory. If there are two or morefiles using the same
        KIC Id it will look at the file Ending and various Key Words like "PSD". Behaviour can be overwritten when
        using the fileName parameter.

        After looking for the file and performing some checks on it, the class will not continue. To start the process
        you need to call the run() method.
        :param kicID:KicID of the star
        :type kicID:str
        :param filePath:Path where to look for the file
        :type filePath:str
        :param fileName:FileName, optional. Will overwrite the standard behaviour of looking for the file
        :type fileName:str
        '''
        self.logger = logging.getLogger(__name__)
        self.kicID = kicID
        self.filePath =filePath
        self.fileName = fileName
        self.resInst : ResultsWriter = None

    def run(self):
        self._internalRun()
    def _internalRun(self):
        '''
        Runs the Standardrunner. The sequence is:

        - look for file
        - read file and compute PSD
        - compute nuMax
        - compute Priors
        - write files
        - run Diamonds
        - create Results

        will run in its own process. So after calling you need to call join() to wait for it to be finished
        '''

        signal.signal(signal.SIGINT,self.sigInterrupt)
        try:
            self.resInst = ResultsWriter.getInstance(self.kicID)
            if not self.resInst.diamondsRunNeeded:
                self.logger.info("Star "+self.kicID+" is already done, skipping")
                return

            self.fileName = self._lookForFile(self.kicID,self.filePath)
            self.logger.info("Lightcurve file is "+self.fileName)

            self._psdCalc = self._readAndConvertLightCurve(self.fileName)
            self.logger.info("Nyquist frequency according to psdCalc is "+str(self._psdCalc.nyqFreq))
            self.logger.info("Photon noise according to psdCalc is " + str(self._psdCalc.photonNoise))

            self._nuMaxResult = self._computeNuMax(self._psdCalc)
            self.logger.info("NuMax is "+str(self._nuMaxResult[0]))
            self.logger.info(self._nuMaxResult)
            self.logger.info(self._nuMaxResult[1].marker)
            plotPSD(self._psdCalc,True,self._nuMaxResult[1].marker,False,1,"Nu Max values")

            self._priors = self._computePriors(self._nuMaxResult[0],self._psdCalc)
            self.logger.info("Priors are:")
            self.logger.info(self._priors)

            self._createFilesAndRunDiamonds(self._psdCalc, self._priors)
            self.logger.info("Files created,diamondsRun")
        except Exception as e:
            self.logger.warning("run failed, saving data")
            trace = traceback.format_exc()
            self.logger.warning(str(e.__class__.__name__) + ":" + str(e))
            self.logger.warning(trace)
        finally:
            if self.resInst.diamondsRunNeeded:
                try:
                    self._computeResults()
                except Exception as e:
                    self.logger.warning(f"Failed to write results for {self.kicID}")
            ResultsWriter.removeInstance(self.kicID)
            self.logger.info("Result created")



    def sigInterrupt(self,sig,frame):
        self.logger.info("Run interrrupted, saving data")
        try:
            if self.resInst.diamondsRunNeeded:
                self._computeResults()
        except:
            pass
        sys.exit()

    def _lookForFile(self,kicID,filePath):
        '''
        This method looks for a lightCurve file within filePath at files with extensions *.txt and *.fits and containing
        kicID. If there is more than one match, it will look if the filename contains certain Keywords (i.e. if it
        contains PSD it will ignore the file).
        :param kicID: KicID of the star
        :type kicID:str
        :param filePath:FilePath where to look at
        :type filePath:str
        :return:filePath + filename
        :rtype:str
        '''
        files = self.listAvailableFilesInPath(filePath)
        self.logger.debug("Files available is "+str(files))
        for file in files:
            if str(kicID) in file:
                try:
                    lightCurveCandidates.append(file)
                except UnboundLocalError:
                    lightCurveCandidates = [file]

        try:
            if len(lightCurveCandidates) > 1:
                for candidate in lightCurveCandidates:
                    if "PSD" in candidate:
                        lightCurveCandidates.remove(candidate)
        except UnboundLocalError:
            self.logger.error("No valid files found!")
            raise IOError("No valid files found")

        if len(lightCurveCandidates) != 1:
            self.logger.error("Failed to find a lightCurve for KIC "+str(kicID))
            self.logger.error("Available files: "+str(lightCurveCandidates))
            raise IOError("Too many files found")

        return filePath+lightCurveCandidates[0]


    def listAvailableFilesInPath(self,filePath,filter=[".txt",".fits"]):
        '''
        Using the filter, this class lists all possible files within the filePath
        :param filePath: The path where to look for the file
        :type filePath: str
        :param filter: List of extensions that should be looked at
        :type filter: list
        :return: A list of all available files within the path. Filename only
        :rtype: list
        '''
        resultList = []
        self.logger.debug("Filepath where we will search: "+filePath)
        with cd(filePath):
            for file in os.listdir("."):
                _,file_extension = os.path.splitext(file)
                if file_extension in filter:
                    resultList.append(file)

        if resultList == []:
            self.logger.error("Failed to find files")
            self.logger.error("Extension filter: "+str(filter))
            self.logger.error("Path: "+filePath)
            raise IOError("No files found")

        return resultList

    def _readAndConvertLightCurve(self,filename):
        '''
        This method will take the fileName, check if it exists and than read it using the FitsReader class. The read
        file will than be pushed into the PowerSpectraCalculator class, where it will be converted into a PSD
        :param filename: Complete filename of the lightCurve
        :type filename: str
        :return: The Powerspectraobject containing the lightcurve and psd
        :rtype: InputDataEvaluator
        '''
        file = InputFileReader(filename,self.kicID)
        powerCalc = InputDataEvaluator(np.conjugate(file.lightCurve))
        powerCalc.kicID = self.kicID

        self.resInst.powerSpectraCalculator = powerCalc

        plotLightCurve(powerCalc,2,fileName="Lightcurve.png")
        plotPSD(powerCalc, True,visibilityLevel=2,fileName="PSD.png")

        return powerCalc


    def _computeNuMax(self, psdCalc):
        '''
        This method uses the nuMax Calculator and computes it.
        :param psdCalc: The PSD calculator object from which the lightCurve will be extracted
        :type psdCalc: InputDataEvaluator
        :return: Tuple containing nuMax in first spot and the nuMax Calculator in second spot
        :rtype: tuple
        '''
        nuMaxCalc = NuMaxEvaluator(self.kicID, psdCalc.lightCurve)
        self.resInst.nuMaxCalculator = nuMaxCalc

        return (nuMaxCalc.computeNuMax(),nuMaxCalc)

    def _computePriors(self, nuMax, powerCalc):
        '''
        This method uses the PriorCalculator to compute the priors which will be used for the DIAMONDS run
        :param nuMax: Frequency of maximum Oscillation
        :type nuMax: float
        :param powerCalc: the psd Calculator object used
        :type powerCalc: InputDataEvaluator
        :return: A list containing the priors used for the run
        :rtype: list
        '''
        priorCalculator = PriorEvaluator(nuMax, powerCalc)
        plotPSD(powerCalc, True, visibilityLevel= 1, fileName="PSD_filterfrequencies.png")

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

        return priors

    def _createFilesAndRunDiamonds(self, powerCalc, priors):
        '''
        This method creates the necessary files for the DIAMONDS run and
        afterwards runs it
        :param powerCalc: The powerspectra calculator
        :type powerCalc: InputDataEvaluator
        :param priors: The priors used for the run
        :type priors: list
        '''
        BackgroundFileCreator(self.kicID, powerCalc.powerSpectralDensity, powerCalc.nyqFreq, priors)

        proc = BackgroundProcess(self.kicID)
        try:
            proc.start()
        except ValueError:
            self.logger.error("Background Process failed for kicID "+self.kicID)
        self.resInst.diamondsRunner = proc

    def _computeResults(self):
        '''
        This method finally gatheres all results and computes it using the AnalyzeResult class
        :return: The imageMap and resultMap contained in a tuple
        :rtype: tuple
        '''
        diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        models = {strFitModeFullBackground:strDiamondsModeFull,strFitModeNoiseBackground:strDiamondsModeNoise}

        for fitMode,binary in models.items():
            if diamondsModel in [strFitModeBayesianComparison,fitMode]:
                result = BackgroundResults(kicID=self.kicID,runID=binary)
                plotPSD(result, False, visibilityLevel=1, fileName="PSD_"+binary+"_fit.png")
                plotParameterTrend(result, fileName=binary+"_Parametertrend.png")
                show(2)

        self.resInst.collectDiamondsResult()
        self.resInst.performAnalysis()

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self,value):
        self._result = value

    @property
    def imageMap(self):
        return self._imageMap

    @imageMap.setter
    def imageMap(self,value):
        self._imageMap = value

    @property
    def kicID(self):
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        self._kicID = value

    @property
    def fileName(self):
        return self._fileName

    @fileName.setter
    def fileName(self,value):
        self._fileName = value

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self,value):
        self._filePath  = value
