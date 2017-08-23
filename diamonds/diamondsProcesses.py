import subprocess

from settings.settings import Settings
from support.strings import *
from support.directoryManager import cd
import logging


class DiamondsProcess:
    def __init__(self,model,kicID,runID,kernels):
        self.logger = logging.getLogger(__name__)
        self.__diamondsBinaryPath = Settings.Instance().getSetting(strDiamondsSettings, strSectDiamondsBinaryPath).value
        if model == strDiamondsNoGaussian or model == strDiamondsGaussian:
            self.__diamondsModelBinary = model
        else:
            self.logger.debug("No binary with name '"+model+"' exists!")
            raise ValueError

        self.__binary = self.__diamondsBinaryPath +self.__diamondsModelBinary
        self.__kicID = kicID
        self.__runID = runID
        self.__kernels = kernels
        return

    def start(self):
        self.logger.debug("Starting diamonds process.")
        self.logger.debug("Binary path: '"+self.__diamondsBinaryPath+"'")
        self.logger.debug("Binary used: '"+self.__diamondsModelBinary+"'")
        self.logger.debug("KicID: '"+self.__kicID+"'")
        self.logger.debug("RunID: '"+self.__runID+"'")
        self.logger.debug("Kernels: '"+self.__kernels+"'")
        cmd = [self.__binary,self.__kicID,self.__runID,self.__kernels]
        self.logger.debug("Full Command: '"+str(cmd)+"'")

        with cd(self.__diamondsBinaryPath):
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
