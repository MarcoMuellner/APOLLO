import subprocess

from settings.settings import Settings
from support.strings import *
from support.directoryManager import cd

class DiamondsProcess:
    def __init__(self,model,kicID,runID,kernels):
        self.__diamondsBinaryPath = Settings.Instance().getSetting(strDiamondsSettings, strSectDiamondsBinaryPath).value
        if model == strDiamondsNoGaussian or model == strDiamondsGaussian:
            self.__diamondsModelBinary = model
        else:
            print("No binary with name '"+model+"' exists!")
            raise ValueError

        self.__binary = self.__diamondsBinaryPath +self.__diamondsModelBinary
        self.__kicID = kicID
        self.__runID = runID
        self.__kernels = kernels
        return

    def start(self):
        print("Starting diamonds process.")
        print("Binary path: '"+self.__diamondsBinaryPath+"'")
        print("Binary used: '"+self.__diamondsModelBinary+"'")
        print("KicID: '"+self.__kicID+"'")
        print("RunID: '"+self.__runID+"'")
        print("Kernels: '"+self.__kernels+"'")
        cmd = [self.__binary,self.__kicID,self.__runID,self.__kernels]
        print("Full Command: '"+str(cmd)+"'")

        with cd(self.__diamondsBinaryPath):
            p = subprocess.Popen(cmd,stdout=subprocess.PIPE)
            for line in p.stdout:
                print(line)
            p.wait()
            print("Command '"+str(cmd)+"' done")
        return

    def stop(self):
        print("Yet to implement!")
        return

    def getLog(self):
        print("Yet to implement!")
        return

    def stillRunning(self):
        print("Yet to implement!")
        return

    def finished(self):
        print("Yet to implement!")
        return