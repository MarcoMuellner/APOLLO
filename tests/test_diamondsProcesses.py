import pytest
from diamonds.diamondsProcesses import DiamondsProcess
import os

@pytest.fixture()
def defaultObject():
    return DiamondsProcess("testKIC")


@pytest.mark.parametrize("paths",[os.getcwd()+"/test/","test/"])
def testAbsolutePathCreation(defaultObject,paths):
    '''

    :type defaultObject: DiamondsProcess
    '''
    assert defaultObject._getFullPath(paths) == os.getcwd()+"/test/"

