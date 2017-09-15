import pytest
from background.backgroundProcess import BackgroundProcess
import os

@pytest.fixture()
def defaultObject():
    return BackgroundProcess("testKIC")


@pytest.mark.parametrize("paths",[os.getcwd()+"/test/","test/"])
def testAbsolutePathCreation(defaultObject,paths):
    '''

    :type defaultObject: BackgroundProcess
    '''
    assert defaultObject._getFullPath(paths) == os.getcwd()+"/test/"

