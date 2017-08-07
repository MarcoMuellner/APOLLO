from loghandler import loghandler
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *
from settings.settings import Settings
from support.directoryManager import cd
from math import sqrt,pi

resultList = []
dataFolder = Settings.Instance().getSetting(strDataSettings, strSectBackgroundResPath).value
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
    #plotPSD(result,True,result.getPSDOnly())
    #plotMarginalDistributions(result)
    if result.getPSDOnly() is False:
        result.calculateDeltaNu()
        calc = result.getDeltaNuCalculator()
        resultList.append(result)
        #plotDeltaNuFit(calc,result.getKicID())

        print('--------------Result KIC' + result.getKicID() + '------------')
        print('nuMax = ' + str(result.getNuMax()) + '(' + str(result.getSigma()) + ')')
        print('DeltaNu = ' + str(result.getDeltaNuCalculator().getCen()[0]) + '(' + str(
            result.getDeltaNuCalculator().getCen()[1]) + ')')
        print(float(result.getKicID()))
        print('----------------------------------------------------------------')

        position = np.where(arrTemperatures[0] == float(result.getKicID()))[0]
        print(position)

        if len(position>0):
            temp = arrTemperatures[1][position[0]]
            tempSun = arrSun[2]
            print('--------------Calculations KIC' + result.getKicID() + '------------')
            print("Temperature is '"+str(temp))
            print("Temperature of the sun '"+str(tempSun)+"'")
            R = (arrSun[1] / result.getDeltaNuCalculator().getCen()[0]) ** 2 * (result.getNuMax()[0] / arrSun[0]) * \
                sqrt(temp / tempSun)

            L = R**2*(temp/tempSun)**4

            print("Radius for KicID '" + str(result.getKicID()) + "'is '" + str(R) + "'R_sun")
            print("Luminosity for KicID '" + str(result.getKicID()) + "'is '" + str(L) + "'L_sun")
            print('----------------------------------------------------------------')

for i in resultList:
    print('--------------Result KIC'+i.getKicID()[0]+'------------')
    print('nuMax = '+str(i.getNuMax()[0])+'('+str(i.getNuMax()[1])+')')
    print('Amplitude = '+str(i.getHg()[0])+"'")
    print('Sigma = '+str(i.getSigma()[0])+"'")
    print('DeltaNu = '+str(i.getDeltaNuCalculator().getCen()[0])+'('+str(i.getDeltaNuCalculator().getCen()[1])+')')
    print('----------------------------------------------------------------')


file = open("Amplitude.csv","w")
file.write("NuMax;Error;Amplitude;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getHg()[0])+";"+str(i.getHg()[1])+"\n")
file.close()

file = open("Sigma.csv","w")
file.write("NuMax;Error;Sigma;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getSigma()[0])+";"+str(i.getSigma()[1])+"\n")
file.close()

file = open("BackgroundNoise.csv","w")
file.write("NuMax;Error;Whitenoise;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getBackgroundNoise()[0])+";"+str(i.getBackgroundNoise()[1])+"\n")
file.close()

file = open("HarveyF1.csv","w")
file.write("NuMax;Error;HarveyF1;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getFirstHarveyFrequency()[0])+";"+str(i.getFirstHarveyFrequency()[1])+"\n")
file.close()

file = open("HarveyA1.csv","w")
file.write("NuMax;Error;HarveyA1;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getFirstHarveyAmplitude()[0])+";"+str(i.getFirstHarveyAmplitude()[1])+"\n")
file.close()

file = open("HarveyF2.csv","w")
file.write("NuMax;Error;HarveyF2;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getSecondHarveyFrequency()[0])+";"+str(i.getSecondHarveyFrequency()[1])+"\n")
file.close()

file = open("HarveyA2.csv","w")
file.write("NuMax;Error;HarveyA2;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getSecondHarveyAmplitude()[0])+";"+str(i.getSecondHarveyAmplitude()[1])+"\n")
file.close()

file = open("HarveyF3.csv","w")
file.write("NuMax;Error;HarveyF3;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getThirdHarveyFrequency()[0])+";"+str(i.getThirdHarveyFrequency()[1])+"\n")
file.close()

file = open("HarveyA3.csv","w")
file.write("NuMax;Error;HarveyA3;Error\n")
for i in resultList:
    file.write(str(i.getNuMax()[0])+";"+str(i.getNuMax()[1])+";"+str(i.getThirdHarveyAmplitude()[0])+";"+str(i.getThirdHarveyAmplitude()[1])+"\n")
file.close()