from loghandler import loghandler
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *
from settings.settings import Settings
from support.directoryManager import cd
from math import sqrt,pi

resultList = []
dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
print(dataFolder)

kicList = []
with cd(dataFolder):
    for x in os.walk("."):
        if "KIC" in x[0] and "/00" not in x[0] and "/01" not in x[0]:
            kicList.append(x[0][5:])

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

print(kicList)

arrSun = np.loadtxt("/Users/Marco/Google Drive/Astroseismology/Sterndaten/Bachelor_Cluster/KICSun.txt")
arrTemperatures = np.loadtxt("/Users/Marco/Google Drive/Astroseismology/Sterndaten/Bachelor_Cluster/KICID_Temperature.txt")
arrTemperatures = arrTemperatures.transpose()
print("arrtemp = '"+str(arrTemperatures[0]))
print(arrSun)

for i in kicList:
    print(i)
    result = Results(i,'00')
    #plotPSD(result,True,result.psdOnlyFlag)
    #plotMarginalDistributions(result)
    if result.psdOnlyFlag  is False:
        result.calculateDeltaNu()
        calc = result.deltaNuCalculator
        resultList.append(result)
        #plotDeltaNuFit(calc,result.kicID)

        print('--------------Result KIC' + result.kicID + '------------')
        print('nuMax = ' + str(result.nuMax) + '(' + str(result.sigma) + ')')
        print('DeltaNu = ' + str(result.deltaNuCalculator.deltaNu[0]) + '(' + str(
            result.deltaNuCalculator.deltaNu[1]) + ')')
        print(float(result.kicID))
        print('----------------------------------------------------------------')

        position = np.where(arrTemperatures[0] == float(result.kicID))[0]
        print(position)

        if len(position>0):
            temp = arrTemperatures[1][position[0]]
            tempSun = arrSun[2]
            print('--------------Calculations KIC' + result.kicID + '------------')
            print("Temperature is '"+str(temp))
            print("Temperature of the sun '"+str(tempSun)+"'")
            R = (arrSun[1] / result.deltaNuCalculator.deltaNu[0]) ** 2 * (result.nuMax[0] / arrSun[0]) * \
                sqrt(temp / tempSun)

            L = R**2*(temp/tempSun)**4

            print("Radius for KicID '" + str(result.kicID) + "'is '" + str(R) + "'R_sun")
            print("Luminosity for KicID '" + str(result.kicID) + "'is '" + str(L) + "'L_sun")
            print('----------------------------------------------------------------')

for i in resultList:
    print('--------------Result KIC'+i.kicID[0]+'------------')
    print('nuMax = '+str(i.nuMax[0])+'('+str(i.nuMax[1])+')')
    print('Amplitude = '+str(i.oscillationAmplitude()[0])+"'")
    print('Sigma = '+str(i.sigma[0])+"'")
    print('DeltaNu = ' + str(i.deltaNuCalculator.deltaNu[0]) + '(' + str(i.deltaNuCalculator.deltaNu[1]) + ')')
    print('----------------------------------------------------------------')


file = open("Amplitude.csv","w")
file.write("NuMax;Error;Amplitude;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.oscillationAmplitude()[0])+";"+str(i.oscillationAmplitude()[1])+"\n")
file.close()

file = open("Sigma.csv","w")
file.write("NuMax;Error;Sigma;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.sigma[0])+";"+str(i.sigma[1])+"\n")
file.close()

file = open("BackgroundNoise.csv","w")
file.write("NuMax;Error;Whitenoise;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.backgroundNoise[0])+";"+str(i.backgroundNoise[1])+"\n")
file.close()

file = open("HarveyF1.csv","w")
file.write("NuMax;Error;HarveyF1;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.firstHarveyFrequency[0])+";"+str(i.firstHarveyFrequency[1])+"\n")
file.close()

file = open("HarveyA1.csv","w")
file.write("NuMax;Error;HarveyA1;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.firstHarveyAmplitude[0])+";"+str(i.firstHarveyAmplitude[1])+"\n")
file.close()

file = open("HarveyF2.csv","w")
file.write("NuMax;Error;HarveyF2;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.secondHarveyFrequency[0])+";"+str(i.secondHarveyFrequency[1])+"\n")
file.close()

file = open("HarveyA2.csv","w")
file.write("NuMax;Error;HarveyA2;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.secondHarveyAmplitude[0])+";"+str(i.secondHarveyAmplitude[1])+"\n")
file.close()

file = open("HarveyF3.csv","w")
file.write("NuMax;Error;HarveyF3;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.thirdHarveyFrequency[0])+";"+str(i.thirdHarveyFrequency[1])+"\n")
file.close()

file = open("HarveyA3.csv","w")
file.write("NuMax;Error;HarveyA3;Error\n")
for i in resultList:
    file.write(str(i.nuMax[0])+";"+str(i.nuMax[1])+";"+str(i.thirdHarveyAmplitude[0])+";"+str(i.thirdHarveyAmplitude[1])+"\n")
file.close()