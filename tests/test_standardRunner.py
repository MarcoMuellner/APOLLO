import pytest
from runner.StandardRunner import StandardRunner
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
import os
import numpy as np
from support.directoryManager import cd

@pytest.fixture(params=[".fits",".txt"],scope="function")
def defaultSetup(request):
    with cd("tests/testFiles/playground"):
        open("testfile_92345443"+request.param,'a').close()
        open("testfile_92345443_PSD"+request.param, 'a').close()
        open("testfile_923435444"+request.param, 'a').close()
        open("testfile_923435443_PSD"+request.param, 'a').close()
        open("testfile_923435444_dat" + request.param, 'a').close()
        def cleanup():
            print("Performing cleanup")
            with cd("tests/testFiles/playground"):
                for i in os.listdir("."):
                    os.remove(i)

        request.addfinalizer(cleanup)
    return StandardRunner("92345443","tests/testFiles/playground/")

@pytest.mark.parametrize("value",[92345443,"92345443"])
def testLookForFile(defaultSetup,value):
    """

    :type defaultSetup: StandardRunner
    """
    defaultSetup._lookForFile(value,defaultSetup.filePath)

@pytest.mark.parametrize("value",[9254342345443,"9234543443","923435444"])
def testFileNotFound(defaultSetup,value):
    with pytest.raises(FileNotFoundError):
        defaultSetup._lookForFile(value,defaultSetup.filePath)

def testListAvailableFiles(defaultSetup):
    """

    :type defaultSetup: StandardRunner
    """
    fileList = defaultSetup.listAvailableFilesInPath(defaultSetup.filePath)
    extensionList = []
    for i in fileList:
        extensionList.append(os.path.splitext(i)[1])
    assert isinstance(fileList,list)
    assert len(fileList) > 0
    assert all( i in [".txt",".fits"]  for i in extensionList)

def testReadAndConvertLightCurve(defaultSetup):
    """

    :type defaultSetup: StandardRunner
    """
    result = defaultSetup._readAndConvertLightCurve("tests/testFiles/fitsLightcurve.fits")
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
    




