import numpy as np
import pytest

from filehandler.Diamonds.diamondsFileCreating import FileCreater
from settings.settings import Settings
from support.strings import *


@pytest.fixture()
def settings(request):
    Settings.Instance().customPath = "tests/testFiles/lightCurveAnalyzer.json"
    resultPath = Settings.Instance().getSetting(strDiamondsSettings,strSectBackgroundResPath).value
    def cleanup():
        print("Performing cleanup")
        for i in os.listdir(resultPath+"KICtestKIC"):
            if "runID" not in i:
                os.remove(resultPath + "KICtestKIC/"+i)
    request.addfinalizer(cleanup)
    return Settings.Instance()

@pytest.mark.skip("Yet to implement for dataFile.py")
def testDataFile(settings):
    print(settings.customPath)

def testFileCreater(settings):
    print(settings.customPath)
    resultPath = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    priors = np.loadtxt(resultPath+"KICtestKIC/runID/background_hyperParametersUniform.txt",skiprows=4)
    FileCreater("testKIC",psd,283.5425,priors)
    assert len(os.listdir(resultPath+"KICtestKIC")) == 6