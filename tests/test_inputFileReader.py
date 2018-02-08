import pytest
import numpy as np

from readerWriter.inputFileReader import InputFileReader
from res.strings import *
from settings.settings import Settings
from support.directoryManager import cd


@pytest.fixture(scope="function")
def defaultSetup(request):
    defaultRefineSettting = Settings.Instance().getSetting(strDataSettings, strSectLightCurveAlgorithm).value
    def cleanup():
        sett = Settings.Instance().getSetting(strDataSettings, strSectLightCurveAlgorithm)
        sett.value = defaultRefineSettting

    request.addfinalizer(cleanup)
    return InputFileReader("tests/testFiles/YoungStar.dat.txt","123456")


@pytest.mark.parametrize("value", [strLightInterpolating,strLightCombining,strLightCutting])
def testRefineData(defaultSetup:InputFileReader,value):
    refineSetting = Settings.Instance().getSetting(strDataSettings,strSectLightCurveAlgorithm)
    refineSetting.value = value

    defaultSetup._refineData(defaultSetup._rawData)
