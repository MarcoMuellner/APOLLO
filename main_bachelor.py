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
    if result.getPSDOnly() is False:
        nuMaxSun = arrSun[0]
        deltaNuSun = arrSun[1]
        tempSun = arrSun[2]
        vmag = arrTemperatures[2][position[0]]
        kicmag = arrTemperatures[5][position[0]]
        av = (arrTemperatures[3][position[0]]*3.1,0)
        #av = (0.16*3.1,0.08*3.1)

        result.calculateDeltaNu()
        calc = result.getDeltaNuCalculator()
        resultList.append(result)
        result.calculateRadius(tempSun,nuMaxSun,deltaNuSun)
        result.calculateLuminosity(tempSun)
        result.calculateDistanceModulus(vmag,kicmag,arrTemperatures[4][position[0]],av,nuMaxSun,deltaNuSun,tempSun)

        print('--------------Result KIC' + result.getKicID() + '------------')
        print('nuMax = ' + str(result.getNuMax()) + '(' + str(result.getSigma()) + ')')
        print('DeltaNu = ' + str(result.getDeltaNuCalculator().deltaNu[0]) + '(' + str(
            result.getDeltaNuCalculator().deltaNu[1]) + ')')
        print(float(result.getKicID()))
        print('----------------------------------------------------------------')


        print('--------------Calculations KIC' + result.getKicID() + '------------')
        print("Temperature is '"+str(Teff))
        print("Temperature of the sun '"+str(tempSun)+"'")
        print("Radius for KicID '" + str(result.getKicID()) + "'is '" + str(result.getRadius()[0])
              + "'R_sun("+str(result.getRadius()[1])+")'")
        print("Luminosity for KicID '" + str(result.getKicID()) + "'is '" + str(result.getLuminosity()[0])
            + "'L_sun("+str(result.getLuminosity()[1])+")'")
        print("Bolometric Correlation for star '"+str(result.getKicID())+"' is: '"+str(result.getBC()))
        print("Apparent Magnitude :'"+str(vmag)+"("+str(arrTemperatures[4][position[0]])+")")
        print("Interstellar Extinction: '"+str(arrTemperatures[3][position[0]]))
        print("Distance is :'"+str(result.getDistanceModulus()[0])+"("+str(result.getDistanceModulus()[1])+")'")
        print("KIC Distance is: "+str(result.getKICDistanceModulus()))
        print("Robustness is: "+str(result.getRobustnessValue()))
        print("Robustness sigma is: "+str(result.getRobustnessSigma()))
        print('----------------------------------------------------------------')

        rgbstr = ''

        if lowerBound <= result.getDistanceModulus()[0] <= upperBound:
            print("KIC"+result.getKicID()+" is MEMBER of the starcluster")
            rgbstr = '75bbfd'
        elif lowerBound <=result.getDistanceModulus()[0]+result.getDistanceModulus()[1]<=upperBound:
            print("Cant tell if "+result.getKicID()+" is Member of starcluster")
            rgbstr = 'c7fdb5'

        else:
            print("KIC"+result.getKicID()+" is NO MEMBER of the starcluster")
            rgbstr = '840000'

        colorList.append(struct.unpack('BBB', bytes.fromhex(rgbstr)))
        nuMaxList.append(result.getNuMax()[0])
        errorNuMaxList.append(result.getNuMax()[1])
        deltaNuList.append(result.getDeltaNuCalculator().deltaNu[0])
        errorDeltaNuList.append(result.getDeltaNuCalculator().deltaNu[1])
        distanceModulusList.append(result.getDistanceModulus()[0])
        errorDistanceModulusList.append(result.getDistanceModulus()[1])
        radiusList.append(result.getRadius()[0])
        errorRadiusList.append(result.getRadius()[1])
        luminosityList.append(result.getLuminosity()[0])
        errorLuminosityList.append(result.getLuminosity()[1])
        kicDistanceModulusList.append(result.getKICDistanceModulus())
        robustnessDistanceModulusList.append(result.getRobustnessValue())
        nullList.append(0)

        #plotPSD(result,True,False)
        #plotDeltaNuFit(result.getDeltaNuCalculator(),result.getKicID())

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
                     r'R($R_\odot$)',r'L($L_\odot$)',r'Luminosity in relation to the radius')


plotStellarRelations(luminosityList,arrTemperatures[2],errorLuminosityList,nullList,
                     r'L($L_\odot$)',"V(mag)",'Apparent magnitude in relation to the luminosity')
'''




file = open("DistanceModulus.csv","w")
file.write("NuMax;DistanceModulus\n")

for i in range(0,len(resultList)):
    file.write(str(log10(resultList[i].getNuMax()[0]))+";"+str(resultList[i].getDistanceModulus())+"\n")
file.close()

file = open("results.csv","w")
file.write("KicID;Membership;NuMax;Error;Distance Modulus;Error;KIC Distance Modulus;Robustness;RobustnessSigma;DeltaNu;Error;Radius;Error;Luminosity\n")

for i in range(0,len(resultList)):
    M = ""
    if lowerBound <= resultList[i].getDistanceModulus()[0] <= 11:
        M="M"
    elif lowerBound <= resultList[i].getDistanceModulus()[0] + resultList[i].getDistanceModulus()[1]  <= 11:
        M = "M"
    elif lowerBound <= resultList[i].getDistanceModulus()[0] - resultList[i].getDistanceModulus()[1]  <= 11:
        M = "M"
    else:
        M='NM'
    file.write(str(resultList[i].kicID)+";"+M+";"+str(resultList[i].getNuMax()[0])+";"+str(resultList[i].getNuMax()[1])+";")
    file.write(str(resultList[i].getDistanceModulus()[0])+";"+str(resultList[i].getDistanceModulus()[1])+";")
    file.write(str(resultList[i].getKICDistanceModulus())+";")
    file.write(str(resultList[i].getRobustnessValue())+";")
    file.write(str(resultList[i].getRobustnessSigma()) + ";")
    file.write(str(resultList[i].getDeltaNuCalculator().deltaNu[0]) + ";" + str(resultList[i].getDeltaNuCalculator().deltaNu[1]) + ";")
    file.write(str(resultList[i].getRadius()[0])+";"+str(resultList[i].getRadius()[1])+";")
    file.write(str(resultList[i].getLuminosity()[0])+";"+str(resultList[i].getLuminosity()[1])+"\n")
file.close()


show()

