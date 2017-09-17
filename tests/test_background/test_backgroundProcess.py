import pytest
from background.backgroundProcess import BackgroundProcess
import os
from res.strings import *

@pytest.fixture(scope='function')
def defaultObject():
    """
    :return:Returns a default object of the BackgroundProcess class.
    :rtype: BackgroundProcess
    """
    object = BackgroundProcess("testKIC")
    return object


@pytest.mark.parametrize("paths",[os.getcwd()+"/test/","test/"])
def testAbsolutePathCreation(defaultObject,paths):
    '''
    This function tests the absolute path handling. It applies one relative path and one absolute path to the method
    and checks if both equal the same path (which they should)
    :type defaultObject: BackgroundProcess
    '''
    assert defaultObject._getFullPath(paths) == os.getcwd()+"/test/"

@pytest.mark.parametrize("errorModes",[("NoError",strDiamondsStatusGood),
                                        (strDiamondsErrBetterLikelihood,strDiamondsStatusLikelihood),
                                        (strDiamondsErrCovarianceFailed,strDiamondsStatusCovariance),
                                        (strDiamondsErrAssertionFailed,strDiamondsStatusAssertion)])
def testStart(defaultObject,errorModes):
    """
    This function tests the starting capability of the processhandler and its errorhandling. At first it will
    apply "NoError" to simulate a run, which is fine. Next it will provide all different errors DIAMONDS can
    throw and checks if the status is correct.
    :type defaultObject: BackgroundProcess
    """
    defaultObject.testErrorMode = errorModes[0]
    try:
        defaultObject.start()
    except ValueError:
        print("No problem")
    assert defaultObject.status[strDiamondsModeFull] == errorModes[1]
    assert defaultObject.status[strDiamondsModeNoise] == errorModes[1]

