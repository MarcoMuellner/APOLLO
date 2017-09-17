import pytest
from background.backgroundProcess import BackgroundProcess
import os
from res.strings import *

@pytest.fixture(scope='function')
def defaultObject():
    object = BackgroundProcess("testKIC")
    return object


@pytest.mark.parametrize("paths",[os.getcwd()+"/test/","test/"])
def testAbsolutePathCreation(defaultObject,paths):
    '''

    :type defaultObject: BackgroundProcess
    '''
    assert defaultObject._getFullPath(paths) == os.getcwd()+"/test/"

@pytest.mark.parametrize("errorModes",[#("NoError",strDiamondsStatusGood),
                                        (strDiamondsErrBetterLikelihood,strDiamondsStatusLikelihood),
                                        (strDiamondsErrCovarianceFailed,strDiamondsStatusCovariance),
                                        (strDiamondsErrAssertionFailed,strDiamondsStatusAssertion)])
def testStart(defaultObject,errorModes):
    """

    :type defaultObject: BackgroundProcess
    """
    defaultObject.testErrorMode = errorModes[0]
    try:
        defaultObject.start()
    except ValueError:
        print("No problem")
    assert defaultObject.status[strDiamondsModeFull] == errorModes[1]
    assert defaultObject.status[strDiamondsModeNoise] == errorModes[1]

