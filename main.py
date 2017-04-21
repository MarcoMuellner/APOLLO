from loghandler import loghandler
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *


loghandler.setup_logging()

kicList =   [
            '002436458',
            '008196817',
            '008263801',
            '008264006',
            '008264079',
            '008329894',
            '008366239',
            '008264074'
            ]

#kicList = ['008264074']
resultList = []

for i in kicList:
    result = Results(i,'00')
    plotPSD(result,True,result.getPSDOnly())
    #plotMarginalDistributions(result)
    if result.getPSDOnly() is False:
        result.calculateDeltaNu()
        calc = result.getDeltaNuCalculator()
        resultList.append(result)
        plotDeltaNuFit(calc,result.getKicID())

        print('--------------Result KIC' + result.getKicID() + '------------')
        print('nuMax = ' + str(result.getNuMax()) + '(' + str(result.getSigma()) + ')')
        print('DeltaNu = ' + str(result.getDeltaNuCalculator().getCen()[0]) + '(' + str(
            result.getDeltaNuCalculator().getCen()[1]) + ')')
        print('----------------------------------------------------------------')


for i in resultList:
    print('--------------Result KIC'+i.getKicID()+'------------')
    print('nuMax = '+str(i.getNuMax())+'('+str(i.getSigma())+')')
    print('DeltaNu = '+str(i.getDeltaNuCalculator().getCen()[0])+'('+str(i.getDeltaNuCalculator().getCen()[1])+')')
    print('----------------------------------------------------------------')

show()




