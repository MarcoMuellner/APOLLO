import shutil

import numpy as np
import pytest

from evaluators.inputDataEvaluator import InputDataEvaluator
from evaluators.nuMaxEvaluator import NuMaxEvaluator
from res.strings import *
from runner.StandardRunner import StandardRunner
from settings.settings import Settings
from support.directoryManager import cd
from shutil import rmtree


@pytest.fixture(params=[".fits",".txt"],scope="function")
def defaultSetup(request):
    if "playground" not in os.listdir("tests/testFiles"):
        os.makedirs("tests/testFiles/playground/")

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


@pytest.fixture(scope='function')
def fullRunner(request):
    shutil.copy2("tests/testFiles/fitsLightcurve.fits", "tests/testFiles/playground/fits_123456789.fits")
    resultPath = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
    dataPath = resultPath = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundDataPath).value
    def cleanup():
        try:
            os.remove(resultPath+"KIC123456789/")
        except:
            print("cannot remove data dir")

        for i in os.listdir("tests/testFiles/playground/"):
            os.remove("tests/testFiles/playground/" + i)

        rmtree("tests/testFiles/results/")
    request.addfinalizer(cleanup)
    return StandardRunner("123456789", "tests/testFiles/playground/")


@pytest.mark.parametrize("value",[92345443,"92345443"])
def testLookForFile(defaultSetup,value):
    '''

    :type defaultSetup: StandardRunner
    '''
    defaultSetup._lookForFile(value,defaultSetup.filePath)

@pytest.mark.parametrize("value",[9254342345443,"9234543443","923435444"])
def testFileNotFound(defaultSetup,value):
    with pytest.raises(IOError):
        defaultSetup._lookForFile(value,defaultSetup.filePath)

def testListAvailableFiles(defaultSetup):
    '''

    :type defaultSetup: StandardRunner
    '''
    fileList = defaultSetup.listAvailableFilesInPath(defaultSetup.filePath)
    extensionList = []
    for i in fileList:
        extensionList.append(os.path.splitext(i)[1])
    assert isinstance(fileList,list)
    assert len(fileList) > 0
    assert all( i in [".txt",".fits"]  for i in extensionList)

def testReadAndConvertLightCurve(defaultSetup):
    '''

    :type defaultSetup: StandardRunner
    '''
    result = defaultSetup._readAndConvertLightCurve("tests/testFiles/fitsLightcurve.fits")
    assert isinstance(result, InputDataEvaluator)
    assert result.powerSpectralDensity is not None
    assert result.lightCurve is not None
    assert result.smoothedData is not None
    assert abs(result.photonNoise -19.305658352604116) < 10**-1
    assert abs(result.nyqFreq - 283.20699116753133) < 10**-1

def testComputeNuMax(defaultSetup):
    '''

    :type defaultSetup: StandardRunner
    '''
    lightCurve = np.loadtxt("tests/testFiles/Lightcurve.txt")
    psdCalc = InputDataEvaluator(lightCurve)
    result = defaultSetup._computeNuMax(psdCalc)
    assert isinstance(result,tuple)
    assert isinstance(result[0],float)
    assert result[0] > 0
    assert isinstance(result[1], NuMaxEvaluator)
    assert len(result[1].marker) == 3

@pytest.mark.skip("Need to think about how to test this properly!")
def testComputePriors(defaultSetup):
    '''

    :type defaultSetup: StandardRunner
    '''
    pass

@pytest.mark.skip("Need to think about how to test this properly!")
def testComputeResults(defaultSetup):
    '''

    :type defaultSetup: StandardRunner
    '''
    pass

def testFullRun(fullRunner):
    print(os.getcwd())
    try:
        fullRunner._internalRun()
    except IOError:
        print("OK")

    




