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
    assert defaultObject.status[strDiModeFull] == errorModes[1]
    assert defaultObject.status[strDiModeNoise] == errorModes[1]


@pytest.mark.parametrize("texts",[("Fine text", strDiStatRunning),
                                  (strDiamondsErrBetterLikelihood,strDiamondsStatusLikelihood),
                                  (strDiamondsErrCovarianceFailed,strDiamondsStatusCovariance),
                                  (strDiamondsErrAssertionFailed,strDiamondsStatusAssertion)])
def testCheckDiamondsStdOut(defaultObject,texts):
    """
    Checks the Std Out parser of the Process object. Inputs various possible texts and checks if the status is set
    accordingly to the proper state
    :type defaultObject: BackgroundProcess
    :param texts: Texts that are checked
    :type texts: tuple
    """
    defaultStatus = strDiStatRunning
    assert texts [1] == defaultObject._checkDiamondsStdOut(defaultStatus,texts[0])

@pytest.mark.parametrize("testDicts",[({strDiModeFull:("", True), strDiModeNoise:("", False)}, False),
                                      ({strDiModeFull:("", False), strDiModeNoise:("", True)}, False),
                                      ({strDiModeFull:("", False), strDiModeNoise:("", False)}, False),
                                      ({strDiModeFull:("", True), strDiModeNoise:("", True)}, True),
                                      ({strDiModeFull:("", False)}, False),
                                      ({strDiModeNoise:("", False)}, False),
                                      ({strDiModeNoise: ("", True)}, True),
                                      ({strDiModeFull: ("", True)}, True),
                                      ])
def testEvaluateRun(defaultObject,testDicts):
    """
    Tests the evaluator of the run. Testdicts provides test Dictionaries with valid results from a run and checks against
    the second component of the tuple
    :type defaultObject: BackgroundProcess
    :param testDicts: Test Dictionaries
    :type testDicts: tuple
    """
    if not testDicts[1]:
        with pytest.raises(ValueError):
            defaultObject.evaluateRun(testDicts[0])
    else:
        assert testDicts[1] == defaultObject.evaluateRun(testDicts[0])

