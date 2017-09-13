import multiprocessing
import os
from uncertainties import ufloat
from uncertainties.core import Variable
from filehandler.fitsReading import FitsReader

from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
from calculations.priorCalculations import PriorCalculator
from filehandler.analyzerResults import AnalyserResults
from filehandler.Diamonds.diamondsFileCreating import FileCreater
from diamonds.diamondsProcesses import DiamondsProcess
from plotter.plotFunctions import *

import numpy as np

class StandardRunner(multiprocessing.Process):
    """
    The Standard Runner class represents a full run for one star. It contains all the results and information about the
    star and includes various subclasses that are accessible within this class, especially in the analyzerResult class.
    """
    def __init__(self,kicID, filePath,fileName = None):
        """
        The constructor of the class. According to the kicID and filePath, the constructor will look within filePath
        for the proper file that represents the kicID.

        It will use the most probable file available within the directory. If there are two or morefiles using the same
        KIC Id it will look at the file Ending and various Key Words like "PSD". Behaviour can be overwritten when
        using the fileName parameter.

        After looking for the file and performing some checks on it, the class will not continue. To start the process
        you need to call the run() method.
        :param kicID:KicID of the star
        :type kicID:basestring
        :param filePath:Path where to look for the file
        :type filePath:basestring
        :param fileName:FileName, optional. Will overwrite the standard behaviour of looking for the file
        :type fileName:basestring
        """
        multiprocessing.Process.__init__(self)

    def run(self):
        pass

    def _lookForFile(self,kicID,filePath):
        """
        This method looks for a lightCurve file within filePath at files with extensions *.txt and *.fits and containing
        kicID. If there is more than one match, it will look if the filename contains certain Keywords (i.e. if it
        contains PSD it will ignore the file).
        :param kicID: KicID of the star
        :type kicID:basestring
        :param filePath:FilePath where to look at
        :type filePath:basestring
        :return:filePath + filename
        :rtype:basestring
        """
        pass

    def listAvailableFilesInPath(self,filePath,filter=[".txt",".fits"]):
        """
        Using the filter, this class lists all possible files within the filePath
        :param filePath: The path where to look for the file
        :type filePath: basestring
        :param filter: List of extensions that should be looked at
        :type filter: list
        :return: A list of all available files within the path. Filename only
        :rtype: list
        """
        pass

    def _readAndConvertLightCurve(self,filename):
        """
        This method will take the fileName, check if it exists and than read it using the FitsReader class. The read
        file will than be pushed into the PowerSpectraCalculator class, where it will be converted into a PSD
        :param filename: Complete filename of the lightCurve
        :type filename: basestring
        :return: The Powerspectraobject containing the lightcurve and psd
        :rtype: PowerspectraCalculator
        """
        file = FitsReader(filename)

        powerCalc = PowerspectraCalculator(np.conjugate(file.getLightCurve()))
        powerCalc.kicID = self.kicID

        AnalyserResults.Instance().powerSpectracalculator = powerCalc

        plotLightCurve(powerCalc,2,fileName="Lightcurve.png")
        plotPSD(powerCalc,True,True,visibilityLevel=2,fileName="PSD.png")
        return powerCalc


    def _computeNuMax(self, psdCalc):
        """
        This method uses the nuMax Calculator and computes it.
        :param psdCalc: The PSD calculator object from which the lightCurve will be extracted
        :type psdCalc: PowerspectraCalculator
        :return: Tuple containing nuMax in first spot and the nuMax Calculator in second spot
        :rtype: tuple
        """
        nuMaxCalc = NuMaxCalculator(psdCalc.lightCurve)
        AnalyserResults.Instance().nuMaxCalculator = nuMaxCalc

        return (nuMaxCalc.computeNuMax(),nuMaxCalc)

    def _computePriors(self, nuMax, photonNoise, nuMaxCalc):
        """
        This method uses the PriorCalculator to compute the priors which will be used for the DIAMONDS run
        :param nuMax: Frequency of maximum Oscillation
        :type nuMax: float
        :param photonNoise: PhotonNoise as computed by the PowerSpectraCalculator
        :type photonNoise: float
        :param nuMaxCalc: the nuMax Calculator object used
        :type nuMaxCalc: NuMaxCalculator
        :return: A list containing the priors used for the run
        :rtype: list
        """
        priorCalculator = PriorCalculator(nuMax, photonNoise, nuMaxCalc)
        plotPSD(nuMaxCalc, True, True, visibilityLevel= 1, fileName= "PSD_filterfrequencies.png")

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

    def _createFiles(self,powerCalc,priors):
        """
        This method creates the necessary files for the DIAMONDS run and
        afterwards runs it
        :param powerCalc: The powerspectra calculator
        :type powerCalc: PowerspectraCalculator
        :param priors: The priors used for the run
        :type priors: list
        """
        FileCreater(self.kicID, powerCalc.powerSpectralDensity, powerCalc.nyqFreq, priors)

        proc = DiamondsProcess(self.kicID)
        proc.start()
        AnalyserResults.Instance().diamondsRunner = proc

    def _computeResults(self):
        """
        This method finally gatheres all results and computes it using the AnalyzeResult class
        :return: The imageMap and resultMap contained in a tuple
        :rtype: tuple
        """
        pass

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

