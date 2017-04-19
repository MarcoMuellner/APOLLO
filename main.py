from loghandler import loghandler
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *


loghandler.setup_logging()

'''
kicList =   [
            '002436458',
            '008196817',
            '008263801',
            '008264006',
            '008264079',
            '008329894',
            '008366239'
            ]
'''
kicList = ['008264074']

for i in kicList:
    result = Results(i,'00')
    plotPSD(result,True,result.getPSDOnly())
    #plotMarginalDistributions(result)
    #plotParameterTrend(result)
    if result.getPSDOnly() is False:
        result.calculateDeltaNu()
        calc = result.getDeltaNuCalculator()
        plotDeltaNuFit(calc)

        print("------------FINAL RESULTS-------------------")
        nuMax = result.getNuMax()
        sigma = result.getSigma()
        deltaNu = calc.getCen()
        print("NuMax = '"+str(nuMax)+"', Sigma = '"+str(sigma)+"'")
        print("DeltaNu = '"+str(deltaNu[0])+"', Sigma = '"+str(deltaNu[1])+"'")
        print("--------------------------------------------")

    show()




