import pytest
from runner.StandardRunner import StandardRunner
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
import os
import numpy as np

@pytest.fixture(scope=module)
def defaultSetup():
    #create some dummy files here
    return StandardRunner("92345443","tests/testFiles/playground")

pytest.mark.param("value",[92345443,"92345443"])
def testLookForFile(defaultSetup,value):
    """

    :type defaultSetup: StandardRunner
    """
    path = "tests/testFiles/playground/"
    assert path+"testfile_92345443.fits" == defaultSetup._lookForFile(value,path)
    with pytest.raises(FileNotFoundError):
        defaultSetup._lookForFile(value+"du",path)

def testListAvailableFiles(defaultSetup):
    """

    :type defaultSetup: StandardRunner
    """
    fileList = defaultSetup.listAvailableFilesInPath()
    assert isinstance(fileList,list)
    assert len(fileList) > 0
    assert all([".txt",".psd"] in i for i in fileList)

def testReadAndConvertLightCurve(defaultSetup):
    """

    :type defaultSetup: StandardRunner
    """
    result = defaultSetup._readAndConvertLightCurve("tests/testFiles/Lightcurve.txt")
    assert isinstance(result,PowerspectraCalculator)
    assert result.powerSpectralDensity is not None
    assert result.lightCurve is not None
    assert result.smoothedData is not None
    assert abs(result.photonNoise -4.174009048728105) < 10**-4
    assert abs(result.nyqFreq - 283.20699116753133) < 10**-4

def testComputeNuMax(defaultSetup):
    """

    :type defaultSetup: StandardRunner
    """
    lightCurve = np.loadtxt("tests/testFiles/Lightcurve.txt")
    psdCalc = PowerspectraCalculator(lightCurve)
    result = defaultSetup._computeNuMax(psdCalc)
    assert isinstance(result,tuple)
    assert isinstance(result[0],float)
    assert result[0] > 0
    assert isinstance(result[1],NuMaxCalculator)
    assert len(result[1].marker) == 3
    assert abs(result[1].nyqFreq - 283.20699116753133) < 10**-4

@pytest.mark.skip("Need to think about how to test this properly!")
def testComputePriors(defaultSetup):
    """

    :type defaultSetup: StandardRunner
    """
    pass

@pytest.mark.skip("Need to think about how to test this properly!")
def testComputeResults(defaultSetup):
    """

    :type defaultSetup: StandardRunner
    """
    pass
    




