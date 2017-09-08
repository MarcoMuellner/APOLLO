import os

from loghandler import loghandler
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *
from settings.settings import Settings
from support.directoryManager import cd
from math import sqrt,pi,log10
import struct
from fitter.fitFunctions import *


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

#kicList = ['002436458']
resultList = []

nuMaxList = []
errorNuMaxList = []
deltaNuList = []
errorDeltaNuList = []
distanceModulusList = []
errorDistanceModulusList = []
radiusList = []
errorRadiusList =[]
luminosityList = []
errorLuminosityList =[]
kicDistanceModulusList = []
robustnessDistanceModulusList = []
colorList = []
nullList = []

dataFolder = Settings.Instance().getSetting(strDiamondsSettingsstrDiamondsSettings, strSectBackgroundResPath).value
print(dataFolder)
arrSun = np.loadtxt("/Users/Marco/Google Drive/Astroseismology/Sterndaten/Bachelor_Cluster/KICSun.txt")
arrTemperatures = np.loadtxt("/Users/Marco/Google Drive/Astroseismology/Sterndaten/Bachelor_Cluster/KICID_Temperature.txt")
arrTemperatures = arrTemperatures.transpose()
print("arrtemp = '"+str(arrTemperatures[0]))
print(arrSun)
lowerBound = 10
upperBound = 11

for i in kicList:
    position = np.where(arrTemperatures[0] == float(i))[0]
    Teff = None
    if len(position > 0):
        Teff = arrTemperatures[1][position[0]]
    result = Results(i,'00',Teff)
    if result.psdOnlyFlag is False:
        nuMaxSun = arrSun[0]
        deltaNuSun = arrSun[1]
        tempSun = arrSun[2]
        vmag = arrTemperatures[2][position[0]]
        kicmag = arrTemperatures[5][position[0]]
        av = (arrTemperatures[3][position[0]]*3.1,0)
        #av = (0.16*3.1,0.08*3.1)

        result.calculateDeltaNu()
        calc = result.deltaNuCalculator
        resultList.append(result)
        result.calculateRadius(tempSun,nuMaxSun,deltaNuSun)
        result.calculateLuminosity(tempSun)
        result.calculateDistanceModulus(vmag,kicmag,arrTemperatures[4][position[0]],av,nuMaxSun,deltaNuSun,tempSun)

        print('--------------Result KIC' + result._kicID + '------------')
        print('nuMax = ' + str(result.nuMax) + '(' + str(result._sigma) + ')')
        print('DeltaNu = ' + str(result.deltaNuCalculator.deltaNu[0]) + '(' + str(
            result.deltaNuCalculator.deltaNu[1]) + ')')
        print(float(result._kicID))
        print('----------------------------------------------------------------')


        print('--------------Calculations KIC' + result._kicID + '------------')
        print("Temperature is '"+str(Teff))
        print("Temperature of the sun '"+str(tempSun)+"'")
        print("Radius for KicID '" + str(result._kicID) + "'is '" + str(result.radiusStar[0])
              + "'R_sun(" + str(result.radiusStar[1]) + ")'")
        print("Luminosity for KicID '" + str(result._kicID) + "'is '" + str(result.luminosity[0])
              + "'L_sun(" + str(result.luminosity[1]) +")'")
        print("Bolometric Correlation for star '" + str(result._kicID) + "' is: '" + str(result.bolometricCorrection))
        print("Apparent Magnitude :'"+str(vmag)+"("+str(arrTemperatures[4][position[0]])+")")
        print("Interstellar Extinction: '"+str(arrTemperatures[3][position[0]]))
        print("Distance is :'"+str(result.distanceModulus[0])+"("+str(result.distanceModulus[1])+")'")
        print("KIC Distance is: "+str(result.kicDistanceModulus))
        print("Robustness is: "+str(result.robustnessValue))
        print("Robustness sigma is: "+str(result.robustnessSigma))
        print('----------------------------------------------------------------')

        rgbstr = ''

        if lowerBound <= result.distanceModulus[0] <= upperBound:
            print("KIC" + result._kicID + " is MEMBER of the starcluster")
            rgbstr = '75bbfd'
        elif lowerBound <=result.distanceModulus[0]+result.distanceModulus[1]<=upperBound:
            print("Cant tell if " + result._kicID + " is Member of starcluster")
            rgbstr = 'c7fdb5'

        else:
            print("KIC" + result._kicID + " is NO MEMBER of the starcluster")
            rgbstr = '840000'

        colorList.append(struct.unpack('BBB', bytes.fromhex(rgbstr)))
        nuMaxList.append(result.nuMax[0])
        errorNuMaxList.append(result.nuMax[1])
        deltaNuList.append(result.deltaNuCalculator.deltaNu[0])
        errorDeltaNuList.append(result.deltaNuCalculator.deltaNu[1])
        distanceModulusList.append(result.distanceModulus[0])
        errorDistanceModulusList.append(result.distanceModulus[1])
        radiusList.append(result.radiusStar[0])
        errorRadiusList.append(result.radiusStar[1])
        luminosityList.append(result.luminosity[0])
        errorLuminosityList.append(result.luminosity[1])
        kicDistanceModulusList.append(result.kicDistanceModulus)
        robustnessDistanceModulusList.append(result.robustnessValue)
        nullList.append(0)

        #plotPSD(result,True,False)
        #plotDeltaNuFit(result.deltaNuCalculator,result.kicID)

plotStellarRelations(kicList,nuMaxList,distanceModulusList,errorNuMaxList,errorDistanceModulusList,
                     r'$\nu_{max}$($\mu$Hz)',r'$\mu_0$(mag)',r'Distance modulus in relation to $\nu_{max}$',fitDegree=0,fill=True)

plotStellarRelations(kicList,deltaNuList,distanceModulusList,errorDeltaNuList,errorDistanceModulusList,
                     r'$\Delta \nu$($\mu$Hz)',r'$\mu_0$(mag)',r'Distance modulus in relation to $\Delta \nu$',fitDegree=0)


plotStellarRelations(kicList,nuMaxList,radiusList,errorNuMaxList,errorRadiusList,
                     r'$\nu_{max}$($\mu$Hz)',r'$\log(R/R_\odot)$',r'Radius in relation to $\nu_{max}$',scaley='log',fill=False)

plotStellarRelations(kicList,nuMaxList,luminosityList,errorNuMaxList,errorLuminosityList,
                     r'$\nu_{max}$($\mu$Hz)',r'$\log(L/L_\odot)$',r'Luminosity in relation to $\nu_{max}$',scaley='log',fill=False)

plotStellarRelations(kicList,arrTemperatures[1],luminosityList,nullList,errorLuminosityList,
                     r'$\log (T_{eff})$',r'$\log(L(L_\odot)$',r'HR Diagramm',scalex='log',scaley='log')
'''
plotStellarRelations(radiusList,luminosityList,errorRadiusList,errorLuminosityList,
                     r'R($R_\odot$)',r'L($L_\odot$)',r'Luminosity in relation to the radiusStar')


plotStellarRelations(luminosityList,arrTemperatures[2],errorLuminosityList,nullList,
                     r'L($L_\odot$)',"V(mag)",'Apparent magnitude in relation to the luminosity')
'''




file = open("DistanceModulus.csv","w")
file.write("NuMax;DistanceModulus\n")

for i in range(0,len(resultList)):
    file.write(str(log10(resultList[i].getNuMax()[0]))+";"+str(resultList[i].distanceModulus)+"\n")
file.close()

file = open("results.csv","w")
file.write("KicID;Membership;NuMax;Error;Distance Modulus;Error;KIC Distance Modulus;Robustness;RobustnessSigma;DeltaNu;Error;Radius;Error;Luminosity\n")

for i in range(0,len(resultList)):
    M = ""
    if lowerBound <= resultList[i].distanceModulus[0] <= 11:
        M="M"
    elif lowerBound <= resultList[i].distanceModulus[0] + resultList[i].distanceModulus[1]  <= 11:
        M = "M"
    elif lowerBound <= resultList[i].distanceModulus[0] - resultList[i].distanceModulus[1]  <= 11:
        M = "M"
    else:
        M='NM'
    file.write(str(resultList[i].kicID)+";"+M+";"+str(resultList[i].getNuMax()[0])+";"+str(resultList[i].getNuMax()[1])+";")
    file.write(str(resultList[i].distanceModulus[0])+";"+str(resultList[i].distanceModulus[1])+";")
    file.write(str(resultList[i].kicDistanceModulus)+";")
    file.write(str(resultList[i].robustnessValue)+";")
    file.write(str(resultList[i].robustnessSigma) + ";")
    file.write(str(resultList[i].deltaNuCalculator.deltaNu[0]) + ";" + str(resultList[i].deltaNuCalculator.deltaNu[1]) + ";")
    file.write(str(resultList[i].radiusStar[0]) + ";" + str(resultList[i].radiusStar[1]) + ";")
    file.write(str(resultList[i].luminosity[0])+";"+str(resultList[i].luminosity[1])+"\n")
file.close()


show()

