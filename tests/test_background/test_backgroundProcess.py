import pytest
from background.backgroundProcess import BackgroundProcess
import os
from res.strings import *

@pytest.fixture()
def defaultObject():
    return BackgroundProcess("testKIC")


@pytest.mark.parametrize("paths",[os.getcwd()+"/test/","test/"])
def testAbsolutePathCreation(defaultObject,paths):
    '''

    :type defaultObject: BackgroundProcess
    '''
    assert defaultObject._getFullPath(paths) == os.getcwd()+"/test/"

@pytest.mark.parametrize("errorModes",[("NoError",strDiamondsStatusGood),
                                        (strDiamondsErrBetterLikelihood,strDiamondsStatusLikelihood),
                                        (strDiamondsErrCovarianceFailed,strDiamondsStatusCovariance),
                                        (strDiamondsErrCovarianceFailed,strDiamondsStatusAssertion)])
def testStart(defaultObject,errorModes):
    """

    :type defaultObject: BackgroundProcess
    """
    defaultObject.testErrorMode = errorModes[0]
    try:
        assert defaultObject.status == errorModes[1]
    except ValueError:
        print("No problem")

