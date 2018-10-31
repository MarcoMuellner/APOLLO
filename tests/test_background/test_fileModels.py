import numpy as np
import pytest

from background.fileModels.backgroundEvidenceFileModel import BackgroundEvidenceFileModel
from background.fileModels.backgroundFileCreator import BackgroundFileCreator
from background.fileModels.backgroundMarginalDistrFileModel import BackgroundMarginalDistrFileModel
from background.fileModels.backgroundParamSummaryModel import BackgroundParamSummaryModel
from background.fileModels.backgroundParameterFileModel import BackgroundParameterFileModel
from background.fileModels.backgroundDataFileModel import BackgroundDataFileModel
from res.strings import *
from settings.settings import Settings


@pytest.fixture()
def settings(request):
    """
    Changes the settings to the testSettings. Also provides some cleaning up of files.
    """
    resultPath = Settings.ins().getSetting(strDiamondsSettings,strSectBackgroundResPath).value
    def cleanup():
        print("Performing cleanup")
        for i in os.listdir(resultPath+"KICtestKIC"):
            if "runID" not in i and "FullBackground" not in i and "NoiseOnly" not in i:
                os.remove(resultPath + "KICtestKIC/"+i)
    request.addfinalizer(cleanup)
    return Settings.ins()

def testDataFile(settings):
    """
    This function provides some rudimentary tests to the datafile class. Checks if the PSD was correctly read and
    if the mean of it is non zero
    """
    print(settings.customPath)
    dataFile = BackgroundDataFileModel("testKIC")
    assert len(dataFile.powerSpectralDensity) == 2
    assert np.mean(dataFile.powerSpectralDensity) != 0

def testFileCreater(settings):
    """
    This function tests the capabilities of the FileCreator. It loads the PSD file and the priors and feeds it
    into the BackgroundFileCreator. It then checks if all the Files needed for a DIAMONDS run are created.
    """
    print(settings.customPath)
    resultPath = Settings.ins().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    priors = np.loadtxt(resultPath+"KICtestKIC/runID/background_hyperParametersUniform.txt",skiprows=4)
    BackgroundFileCreator("testKIC", psd, 283.5425, priors)
    assert len(os.listdir(resultPath+"KICtestKIC")) == 8


def testEvidenceFile(settings):
    """
    This function tests the evidence evidence File. It checks if the evidence file was properly read and if the
    values are correct (length and type). Also checks an empty run.
    """
    print(settings.customPath)
    e = BackgroundEvidenceFileModel("testKIC","runID")
    assert len(e.getData()) == 4
    assert isinstance(e.getData(strEvidSkillLog), float)
    assert isinstance(e.getData(strEvidSkillErrLog), float)
    assert isinstance(e.getData(strEvidSkillInfLog), float)

def testEvidenceFileFailue(settings):
    print(settings.customPath)
    with pytest.raises(IOError):
        e = BackgroundEvidenceFileModel("failureKIC", "failureRun")


@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testMarginalDistributionFile(settings,id):
    """
    This function tests the background maringal distribution files. Checks if the data is of type ndarray for all
    possible ids.
    """
    print(settings.customPath)
    e = BackgroundMarginalDistrFileModel(str(id),str(id),"testKIC","runID",id)
    assert isinstance(e.getData(),np.ndarray)

@pytest.mark.skip("Backrounddata must be created.")
@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testCreateMarginalDistributions(settings,id):
    """
    This function tests the createMarginalDistribution method. It checks if the length of the values is correct.
    """
    print(settings.customPath)
    e = BackgroundMarginalDistrFileModel(str(id),str(id),"testKIC","runID",id)
    margDistr = e.createMarginalDistribution()
    assert len(margDistr) == 5

@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testParameterFile(settings,id):
    """
    This function tests the BackgroundParameterFileModel. Simply checks if the data is of ndarray
    """
    print(settings.customPath)
    p = BackgroundParameterFileModel(str(id), str(id), "testKIC", "runID", id)
    assert isinstance(p.getData(),np.ndarray)

def testFailParameterFile(settings):
    print(settings.customPath)
    with pytest.raises(IOError):
        BackgroundParameterFileModel(str(id), str(id), "thiswill", "fail", "totally")

def testParameterSummary(settings):
    """
    This function tests the parameter summary file. It checks if the raw data is correct, and if the values
    have sanity character
    """
    print(settings.customPath)
    p = BackgroundParamSummaryModel("testKIC","runID")
    assert p.dataLength() == 10
    assert len(p.getRawData()) == 7
    assert len(p.getData()) == p.dataLength()
    assert p.getData(strPriorFlatNoise) > 0
    assert p.getData(strPriorFreqHarvey3) > 0
    assert p.getData(strPriorNuMax) > 0

def testFailParameterSummary(settings):
    print(settings.customPath)
    p = BackgroundParamSummaryModel("thiswill","fail")
    assert p.getData(strPriorFlatNoise) == 0
    assert p.getData(strPriorAmpHarvey1) == 0
    assert p.getData(strPriorFreqHarvey1) == 0
