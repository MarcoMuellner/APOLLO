import subprocess

from settings.settings import Settings
from support.strings import *
from support.directoryManager import cd
import logging


class DiamondsProcess:
    def __init__(self,model,kicID,runID,kernels):
        self.logger = logging.getLogger(__name__)
        self.diamondsBinaryPath = Settings.Instance().getSetting(strDiamondsSettings, strSectDiamondsBinaryPath).value
        self.diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self.binaryListToExecute = []

        if self.diamondsModel in [strFitModeFullBackground,strFitModeBayesianComparison]:
            self.binaryListToExecute.append(strDiamondsGaussian)

        if self.diamondsModel in [strFitModeNoiseBackground,strFitModeBayesianComparison]:
            self.binaryListToExecute.append(strDiamondsNoGaussian)

        self.kicID = kicID
        self.runID = runID
        self.kernels = kernels
        return

    def start(self):
        self.logger.debug("Starting diamonds process(es).")
        for i in self.binaryListToExecute:
            self.logger.debug("Binary path: '"+self.diamondsBinaryPath+"'")
            self.logger.debug("Binary used: '"+i+"'")
            self.logger.debug("KicID: '"+self.kicID+"'")
            self.logger.debug("RunID: '"+self.runID+"'")
            self.logger.debug("Kernels: '"+self.kernels+"'")
            cmd = [(self.diamondsBinaryPath + i),self.kicID,self.runID,self.kernels]
            self.logger.debug("Full Command: '"+str(cmd)+"'")

            with cd(self.diamondsBinaryPath):
                p = subprocess.Popen(cmd,stdout=subprocess.PIPE)
                p.wait()
                for line in p.stdout:
                    self.logger.debug(line)
                    self.logger.debug("Command '"+str(cmd)+"' done")
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
