import subprocess

from settings.settings import Settings
from support.strings import *
from support.directoryManager import cd
import logging


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

            mode = strDiamondsModeNoise if i == strDiamondsExecNoise else strDiamondsModeFull

            while finished is False:
                errorCount +=1
                with cd(self.diamondsBinaryPath):
                    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    while p.poll() is None:
                        line = p.stderr.readline()
                        self.logger.debug(line)
                        if strDiamondsErrBetterLikelihood in str(line) and errorCount <=3:
                            self.logger.warning("Diamonds cannot find point with better likelihood. Repeat!")
                            self.status[mode] = strDiamondsStatusLikelihood
                            continue
                        elif errorCount >3:
                            self.logger.error("Diamonds failed to find good values")
                            break

                    self.logger.debug(p.stdout.read())
                    self.logger.debug("Command '"+str(cmd)+"' done")
                    finished = True
                    self.status[mode] = strDiamondsStatusGood

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
