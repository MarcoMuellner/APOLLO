import pytest
from support.strings import *
from filehandler.Diamonds.InternalStructure.backgroundEvidenceInformationFile import Evidence
from filehandler.Diamonds.InternalStructure.backgroundMarginalDistributionFile import MarginalDistribution
from filehandler.Diamonds.InternalStructure.backgroundParameterFile import BackgroundParameter
from filehandler.Diamonds.InternalStructure.backgroundParameterSummaryFile import ParameterSummary
from settings.settings import Settings
import numpy as np

@pytest.fixture()
def settings():
    return Settings.Instance()


def testEvidenceFile(settings):
    print(settings.customPath)
    e = Evidence("testKIC","runID")
    assert len(e.getData()) == 3
    assert isinstance(e.getData(strEvidenceSkillLog),float)
    assert isinstance(e.getData(strEvidenceSkillErrLog), float)
    assert isinstance(e.getData(strEvidenceSkillInfLog), float)

    e = Evidence("empty","empty")
    assert len(e.getData()) == 0


@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testMarginalDistributionFile(settings,id):
    print(settings.customPath)
    e = MarginalDistribution(str(id),str(id),"testKIC","runID",id)
    assert isinstance(e.getData(),np.ndarray)

@pytest.mark.skip("This test needs to be yet implementd")
@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testCreateMarginalDistributions(settings,id):
    print(settings.customPath)
    e = MarginalDistribution(str(id),str(id),"testKIC","runID",id)
    assert isinstance(e.createMarginalDistribution(),np.ndarray) #change this

@pytest.mark.parametrize("id",[0,1,2,3,4,5,6,7,8,9])
def testParameterFile(settings,id):
    print(settings.customPath)
    p = BackgroundParameter(str(id),str(id),"testKIC","runID",id)
    assert isinstance(p.getData(),np.ndarray)

    p = BackgroundParameter(str(id),str(id),"thiswill","fail",id)
    assert p.getData() == None

def testParameterSummary(settings):
    print(settings.customPath)
    p = ParameterSummary("testKIC","runID")
    assert p.dataLength() == 10
    assert len(p.getRawData()) == 7
    assert len(p.getData()) == p.dataLength()
    assert p.getData(strPriorFlatNoise) > 0
    assert p.getData(strPriorFreqHarvey3) > 0
    assert p.getData(strPriorNuMax) > 0

    p = ParameterSummary("thiswill","fail")
    assert p._rawValues == {}
    assert p._priorValues == {}


