import numpy as np
import pytest

from background.fileModels.backgroundEvidenceFileModel import BackgroundEvidenceFileModel
from background.fileModels.backgroundFileCreator import BackgroundFileCreator
from background.fileModels.backgroundMarginalDistrFileModel import BackgroundMarginalDistrFileModel
from background.fileModels.backgroundParamSummaryModel import BackgroundParamSummaryModel
from background.fileModels.backgroundParameterFileModel import BackgroundParameterFileModel
from res.strings import *
from settings.settings import Settings


@pytest.fixture()
def settings(request):
    resultPath = Settings.Instance().getSetting(strDiamondsSettings,strSectBackgroundResPath).value
    def cleanup():
        print("Performing cleanup")
        for i in os.listdir(resultPath+"KICtestKIC"):
            if "runID" not in i and "FullBackground" not in i and "NoiseOnly" not in i:
                os.remove(resultPath + "KICtestKIC/"+i)
    request.addfinalizer(cleanup)
    return Settings.Instance()

@pytest.mark.skip("Yet to implement for backgroundDataFile.py")
def testDataFile(settings):
    print(settings.customPath)

def testFileCreater(settings):
    print(settings.customPath)
    resultPath = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    priors = np.loadtxt(resultPath+"KICtestKIC/runID/background_hyperParametersUniform.txt",skiprows=4)
    BackgroundFileCreator("testKIC", psd, 283.5425, priors)
    assert len(os.listdir(resultPath+"KICtestKIC")) == 8


def testEvidenceFile(settings):
    print(settings.customPath)
    e = BackgroundEvidenceFileModel("testKIC","runID")
    assert len(e.getData()) == 3
    assert isinstance(e.getData(strEvidenceSkillLog),float)
    assert isinstance(e.getData(strEvidenceSkillErrLog), float)
    assert isinstance(e.getData(strEvidenceSkillInfLog), float)

    e = BackgroundEvidenceFileModel("empty","empty")
    assert len(e.getData()) == 0


@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testMarginalDistributionFile(settings,id):
    print(settings.customPath)
    e = BackgroundMarginalDistrFileModel(str(id),str(id),"testKIC","runID",id)
    assert isinstance(e.getData(),np.ndarray)

@pytest.mark.skip("This test needs to be yet implementd")
@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testCreateMarginalDistributions(settings,id):
    print(settings.customPath)
    e = BackgroundMarginalDistrFileModel(str(id),str(id),"testKIC","runID",id)
    assert isinstance(e.createMarginalDistribution(),np.ndarray) #change this

@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testParameterFile(settings,id):
    print(settings.customPath)
    p = BackgroundParameterFileModel(str(id), str(id), "testKIC", "runID", id)
    assert isinstance(p.getData(),np.ndarray)

    p = BackgroundParameterFileModel(str(id), str(id), "thiswill", "fail", id)
    assert p.getData() == None

def testParameterSummary(settings):
    print(settings.customPath)
    p = BackgroundParamSummaryModel("testKIC","runID")
    assert p.dataLength() == 10
    assert len(p.getRawData()) == 7
    assert len(p.getData()) == p.dataLength()
    assert p.getData(strPriorFlatNoise) > 0
    assert p.getData(strPriorFreqHarvey3) > 0
    assert p.getData(strPriorNuMax) > 0

    p = BackgroundParamSummaryModel("thiswill","fail")
    assert p._rawValues == {}
    assert p._priorValues == {}