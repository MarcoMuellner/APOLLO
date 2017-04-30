import os

from loghandler import loghandler
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *
from settings.settings import Settings
from support.directoryManager import cd
from math import sqrt,pi


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
resultList = []
dataFolder = Settings.Instance().getSetting(strDataSettings, strSectBackgroundResPath).value
print(dataFolder)
arrSun = np.loadtxt("/Users/Marco/Google Drive/Astroseismology/Sterndaten/Bachelor_Cluster/KICSun.txt")
arrTemperatures = np.loadtxt("/Users/Marco/Google Drive/Astroseismology/Sterndaten/Bachelor_Cluster/KICID_Temperature.txt")
arrTemperatures = arrTemperatures.transpose()
print("arrtemp = '"+str(arrTemperatures[0]))
print(arrSun)

for i in kicList:
    position = np.where(arrTemperatures[0] == float(i))[0]
    Teff = None
    if len(position > 0):
        Teff = arrTemperatures[1][position[0]]
    result = Results(i,'00',Teff)
    if result.getPSDOnly() is False:
        nuMaxSun = arrSun[0]
        deltaNuSun = arrSun[1]
        tempSun = arrSun[2]

        result.calculateDeltaNu()
        calc = result.getDeltaNuCalculator()
        resultList.append(result)
        result.calculateRadius(tempSun,nuMaxSun,deltaNuSun)
        result.calculateLuminosity(tempSun)

        print('--------------Result KIC' + result.getKicID() + '------------')
        print('nuMax = ' + str(result.getNuMax()) + '(' + str(result.getSigma()) + ')')
        print('DeltaNu = ' + str(result.getDeltaNuCalculator().getCen()[0]) + '(' + str(
            result.getDeltaNuCalculator().getCen()[1]) + ')')
        print(float(result.getKicID()))
        print('----------------------------------------------------------------')


        print('--------------Calculations KIC' + result.getKicID() + '------------')
        print("Temperature is '"+str(Teff))
        print("Temperature of the sun '"+str(tempSun)+"'")
        print("Radius for KicID '" + str(result.getKicID()) + "'is '" + str(result.getRadius()) + "'R_sun")
        print("Luminosity for KicID '" + str(result.getKicID()) + "'is '" + str(result.getLuminosity()) + "'L_sun")
        print("Bolometric Correlation for star '"+str(result.getKicID())+"' is: '"+str(result.getBC()))
        print('----------------------------------------------------------------')



