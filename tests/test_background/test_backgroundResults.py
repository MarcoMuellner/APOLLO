import numpy as np
import pytest
from uncertainties.core import Variable

from background.backgroundResults import BackgroundResults
from background.fileModels.backgroundEvidenceFileModel import BackgroundEvidenceFileModel
from background.fileModels.backgroundMarginalDistrFileModel import BackgroundMarginalDistrFileModel
from background.fileModels.backgroundParamSummaryModel import BackgroundParamSummaryModel
from background.fileModels.backgroundParameterFileModel import BackgroundParameterFileModel
from background.fileModels.backgroundPriorFileModel import BackgroundPriorFileModel
from res.strings import *


@pytest.fixture(params=[strDiModeFull, strDiModeNoise], scope="module")
def fullObject(request):
    return (BackgroundResults("123456789",request.param),request.param)

@pytest.fixture(scope='module')
def fullBackgroundObject():
    return BackgroundResults("123456789", strDiModeFull)

@pytest.fixture(scope='module')
def noiseOnlyObject():
    return BackgroundResults("123456789", strDiModeNoise)


testNoiseOnlyNames = [strPriorFlatNoise,
               strPriorAmpHarvey1,
               strPriorFreqHarvey1,
               strPriorAmpHarvey2,
               strPriorFreqHarvey2,
               strPriorAmpHarvey3,
               strPriorFreqHarvey3]

testFullBackgroundNames = testNoiseOnlyNames + [
               strPriorHeight,
               strPriorNuMax,
               strPriorSigma]


def testFullParameters(fullObject: (BackgroundResults,str)):
    params = fullObject[0].getBackgroundParameters()
    if fullObject[1] == strDiModeFull:
        assert len(params) == 10
        for i in params:
            assert i.name in testFullBackgroundNames
    else:
        assert len(params) == 7
        for i in params:
            assert i.name in testNoiseOnlyNames

    assert isinstance(params,list)

@pytest.mark.parametrize("names",testNoiseOnlyNames)
def testNoiseOnlyOnlyParameters(noiseOnlyObject:BackgroundResults,names):
    param = noiseOnlyObject.getBackgroundParameters(names)

    assert isinstance(param,BackgroundParameterFileModel)

@pytest.mark.parametrize("names",testFullBackgroundNames)
def testFullBackOnlyParameters(fullBackgroundObject:BackgroundResults, names):
    param = fullBackgroundObject.getBackgroundParameters(names)

    assert isinstance(param,BackgroundParameterFileModel)

def testHasPrior(fullObject:(BackgroundResults,str)):
    assert isinstance(fullObject[0].prior,BackgroundPriorFileModel)

def testHasEvidence(fullObject:(BackgroundResults,str)):
    assert isinstance(fullObject[0].evidence,BackgroundEvidenceFileModel)

def testHasSummary(fullObject:(BackgroundResults,str)):
    assert isinstance(fullObject[0].summary,BackgroundParamSummaryModel)

def testFullSummaryParameter(fullObject:(BackgroundResults,str)):
    summaryValues = fullObject[0]._getSummaryParameter()
    if fullObject[1] == strDiModeFull:
        assert len(summaryValues) == 10
        assert strPriorNuMax in summaryValues.keys()
    else:
        assert len(summaryValues) == 7

    assert isinstance(summaryValues,dict)

@pytest.mark.parametrize("names",testNoiseOnlyNames)
def testNoiseOnlyOnlySummaryParameters(noiseOnlyObject:BackgroundResults,names):
    summaryParam = noiseOnlyObject._getSummaryParameter(names)
    assert isinstance(summaryParam,Variable)

@pytest.mark.parametrize("names",testFullBackgroundNames)
def testNoiseOnlyOnlySummaryParameters(fullBackgroundObject:BackgroundResults,names):
    summaryParam = fullBackgroundObject._getSummaryParameter(names)
    assert isinstance(summaryParam,Variable)
    
def testCreateBackgroundModel(fullObject:(BackgroundResults,str)):
    val = fullObject[0].createBackgroundModel()
    assert len(val) > 0
    assert not isinstance(val,bool)
    assert not isinstance(val, int)
    assert not isinstance(val, float)
    
def testFullMarginalDistribution(fullObject:(BackgroundResults,str)):
    margDistrValues = fullObject[0].getMarginalDistribution()
    if fullObject[1] == strDiModeFull:
        assert len(margDistrValues) == 10
        for i in margDistrValues:
            assert i.name in testFullBackgroundNames
    else:
        assert len(margDistrValues) == 7
        for i in margDistrValues:
            assert i.name in testNoiseOnlyNames

    assert isinstance(margDistrValues,list)

@pytest.mark.parametrize("names",testNoiseOnlyNames)
def testNoiseOnlyOnlyMarginalDistribution(noiseOnlyObject:BackgroundResults,names):
    summaryParam = noiseOnlyObject.getMarginalDistribution(names)
    assert isinstance(summaryParam,BackgroundMarginalDistrFileModel)

@pytest.mark.parametrize("names",testFullBackgroundNames)
def testNoiseOnlyOnlyMarginalDistribution(fullBackgroundObject:BackgroundResults,names):
    summaryParam = fullBackgroundObject.getMarginalDistribution(names)
    assert isinstance(summaryParam,BackgroundMarginalDistrFileModel)
    

