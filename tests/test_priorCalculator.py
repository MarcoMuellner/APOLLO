import pytest
from calculations.priorCalculations import PriorCalculator
from calculations.powerspectraCalculations import PowerspectraCalculator
from uncertainties import ufloat
import numpy as np

typeErrorTestCases = [
    "hello",
    (1,2),
    [1,2,3],
    {1:2,"drei":"vier"}
]

typeWorkingCases = [
    55,
    55.6,
    ufloat(55.6,10)
]

@pytest.fixture()
def psdCalc():
    lc  = np.loadtxt("tests/testFiles/Lightcurve.txt")
    return PowerspectraCalculator(lightCurve= lc)


@pytest.mark.parametrize("value",typeErrorTestCases)
def testTypeFailure(psdCalc,value):
    with pytest.raises(TypeError):
        PriorCalculator(value,value,psdCalc)

@pytest.mark.parametrize("value",typeWorkingCases)
def testTypeOk(psdCalc,value):
    assert PriorCalculator(value,value/10,psdCalc).nuMax == value
