import pytest
from settings.settings import Settings
from filehandler.Diamonds.diamondsFileCreating import FileCreater
import os
import numpy as np

@pytest.fixture()
def settings(request):
    Settings.Instance().customPath = "tests/testFiles/lightCurveAnalyzer.json"
    def cleanup():
        print("Performing cleanup")
        for i in os.listdir("tests/testFiles/diamondsFiles/KICtestKIC"):
            if "runID" not in i:
                os.remove("tests/testFiles/diamondsFiles/KICtestKIC/"+i)
    request.addfinalizer(cleanup)
    return Settings.Instance()

@pytest.mark.skip("Yet to implement for dataFile.py")
def testDataFile(settings):
    print(settings.customPath)

def testFileCreater(settings):
    print(settings.customPath)
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    priors = np.loadtxt("tests/testFiles/diamondsFiles/KICtestKIC/runID/background_hyperParametersUniform.txt",skiprows=4)
    FileCreater("testKIC",psd,283.5425,priors)
    assert len(os.listdir("tests/testFiles/diamondsFiles/KICtestKIC")) == 6