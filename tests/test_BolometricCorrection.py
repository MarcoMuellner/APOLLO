import pytest
from calculations.bolometricCorrectionCalculations import BCCalculator
from uncertainties import ufloat

valueTestCases = {
    200:-1012.3831518705101,
    6000:-0.04488705990661401,
    ufloat(6000,200):ufloat(-0.04488705990661401,0.027592869344328363)
}

failureTestCases = [0,"string"]

@pytest.fixture(params=valueTestCases.keys())
def valueCalculator(request):
    return (BCCalculator(request.param),request.param)

def testValueBCCalc(valueCalculator):
    assert abs(valueCalculator[0].BC - valueTestCases[valueCalculator[1]]) < 10**-6

@pytest.mark.parametrize('value',[0,"string"])
def testFailureBCCalc(value):
    with pytest.raises(ValueError):
        BCCalculator(value)
