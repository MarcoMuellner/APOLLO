import subprocess

from settings.settings import Settings
from support.strings import *
from support.directoryManager import cd
from plotter.fileAnimator import FileAnimator
import logging
import pylab as pl


class DiamondsProcess:
    def __init__(self,kicID):
        self.status = {}
        self.logger = logging.getLogger(__name__)
        self.diamondsBinaryPath = Settings.Instance().getSetting(strDiamondsSettings, strSectDiamondsBinaryPath).value
        self.diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self.diamondsResultsPath = Settings.Instance().getSetting(strDiamondsSettings,strSectBackgroundResPath).value
        self.binaryListToExecute = {}

        if self.diamondsModel in [strFitModeFullBackground,strFitModeBayesianComparison]:
            self.binaryListToExecute[strDiamondsModeFull]=(strDiamondsExecFull)

        if self.diamondsModel in [strFitModeNoiseBackground,strFitModeBayesianComparison]:
            self.binaryListToExecute[strDiamondsModeNoise]=(strDiamondsExecNoise)

        self.kicID = kicID
        return

    def start(self):
        self.logger.debug("Starting diamonds process(es).")
        for i in self.binaryListToExecute.keys():
            resultsPath = self.diamondsResultsPath+"KIC"+self.kicID+"/"+i+"/"
            self.logger.debug("Mode is : '"+i+"'")
            self.logger.debug("Binary path: '"+self.diamondsBinaryPath+"'")
            self.logger.debug("Binary used: '"+self.binaryListToExecute[i]+"'")
            self.logger.debug("KicID: '"+self.kicID+"'")

            cmd = [(self.diamondsBinaryPath + self.binaryListToExecute[i]),self.kicID,i]
            self.logger.debug("Full Command: '"+str(cmd)+"'")
            self.logger.debug("Results directory '"+resultsPath+"'")


            if not os.path.exists(resultsPath):
                self.logger.debug("Directory "+resultsPath+" doesn't exist. Creating...")
                os.makedirs(resultsPath)

            finished = False
            errorCount = 0

            mode = strDiamondsModeNoise if i == strDiamondsModeNoise else strDiamondsModeFull

            while finished == False:
                errorCount +=1
                self.status[mode] = strDiamondsStatusRunning
                with cd(self.diamondsBinaryPath):
                    fileDict = self.getParameterDict(mode)
                    anim = FileAnimator(fileDict)

                    animStart = False

                    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    while p.poll() is None:
                        line = p.stderr.readline()
                        self.logger.debug(line)
                        if "Nit" in str(line) and animStart == False:
                            animStart = True
                            anim.start()
                        if strDiamondsErrBetterLikelihood in str(line):
                            self.logger.warning("Diamonds cannot find point with better likelihood. Repeat!")
                            self.status[mode] = strDiamondsStatusLikelihood
                        elif strDiamondsErrCovarianceFailed in str(line):
                            self.logger.warning("Diamonds cannot decompose covariance. Repeat!")
                            self.status[mode] = strDiamondsStatusCovariance
                        elif strDiamondsErrAssertionFailed in str(line):
                            self.logger.warning("Diamonds assertion failed. Repeat!")
                            self.status[mode] = strDiamondsStatusAssertion

                    self.logger.debug(p.stdout.read())
                    self.logger.debug("Command '"+str(cmd)+"' done")
                    if self.status[mode] == strDiamondsStatusRunning:
                        finished = True
                        self.status[mode] = strDiamondsStatusGood
                    elif errorCount >3:
                        self.logger.error("Diamonds failed to find good values!")
                        break

                #Some error handling needs to take place here!
        return

    def stop(self):
        self.logger.debug("Yet to implement!")
        return

    def getLog(self):
        self.logger.debug("Yet to implement!")
        return

    def stillRunning(self):
        self.logger.debug("Yet to implement!")
        return

    def finished(self):
        self.logger.debug("Yet to implement!")
        return

    def getStatus(self):
        return self.status

    def getParameterDict(self,runID):
        dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
        file = dataFolder + 'KIC' + self.kicID + "/" + runID + "/background_parameter_live00";

        fileDict = {}

        names = ['w', '$\sigma_\mathrm{long}$', '$b_\mathrm{long}$', '$\sigma_\mathrm{gran,1}$',
                      '$b_\mathrm{gran,1}$', '$\sigma_\mathrm{gran,2}$', '$b_\mathrm{gran,2}$']
        units = ['ppm$^2$/$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm', '$\mu$Hz']

        if runID == strDiamondsModeNoise:
            names.append['$H_\mathrm{osc}$', '$f_\mathrm{max}$ ', '$\sigma_\mathrm{env}$']
            units.append['ppm$^2$/$\mu$Hz','$\mu$Hz', '$\mu$Hz']
            counter = 9
        else:
            counter = 6

        for i in range(0,counter):
            try:
                self.logger.info("Deleting file "+file+str(i)+".txt")
                os.remove(file+str(i)+".txt")
            except OSError:
                self.logger.debug("File " + file+str(i) + " doesnt exist")

            fileDict[names[i]] = (units[i],file+str(i)+".txt")

        return fileDict


