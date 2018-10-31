from logging import getLogger
import os
import re

from settings.settings import Settings
from res.strings import *
from support.directoryManager import cd
import subprocess
from multiprocessing import Process


class _dummyProcessObject:
    def __init__(self):
        self._dummyPollCounter = 0
        self.stderr = self.out()
        self.stderr.testErrorMode = "NoError"

    def poll(self):
        if self._dummyPollCounter == 10:
            return "Finished"
        self.stderr._dummyPollCounter = self._dummyPollCounter
        self._dummyPollCounter += 1
        return None

    class out:
        def __init__(self):
            self._dummyPollCounter = 0
            self.testErrorMode = "NoError"

        def readline(self):
            if self._dummyPollCounter == 5 and self.testErrorMode != "NoError":
                return self.testErrorMode
            return "NoError"

        def read(self):
            return ("DUMMY OBJECT DONE")

class BackgroundProcess:

    def __init__(self,kicID):
        self.logger = getLogger(__name__)
        self.kicID = kicID
        self.binaryPath = Settings.ins().getSetting(strDiamondsSettings, strSectDiamondsBinaryPath).value
        self.model = Settings.ins().getSetting(strDiamondsSettings, strSectFittingMode).value

        self.resultsPath = Settings.ins().getSetting(strDiamondsSettings, strSectBackgroundResPath).value

        self.modes = {strRunIDFull: (strDiModeFull, strDiIntModeFull)
            , strRunIDNoise: (strDiModeNoise, strDiIntModeFull)}

        self._status = {}
        self._dummyObject = self._dummyProcessObject()

    def _getFullPath(self,path):
        '''
        This method will create an absolute path if the path it inputs wasn't that already
        :param path: The path you want to have the absolute of
        :type path: str
        :return: Absolute path
        :rtype: str
        '''
        if path[0] not in ["~", "/", "\\"]:
            path = os.getcwd() + "/" + path

        return path

    def _getCommandStrings(self):
        cmdStrings = {}
        for runID,(diMode,diIntMode) in self.modes.values():
            if self.model not in [runID, strRunIDBoth]:
                self.logger.info(f"Skipping {runID}")
                continue

            binPath = self._getFullPath(self.binaryPath + strDiBinary)
            runResPath = f"{self.resultsPath}KIC{self.kicID}/{runID}/"
            if not os.path.exists(runResPath):
                self.logger.debug(f"Directory {runResPath} does not exist. Creating ...")
                os.makedirs(runResPath)

            self.logger.info(f"{runID}: Results path {runResPath}")
            cmdStrings[runID] = [binPath,self.kicID,runID,diIntMode]
            self.logger.info(f"{runID}: Command --> {cmdStrings[runID]}")

        return cmdStrings

    def run(self):
        cmdStrings = self._getCommandStrings()
        pList = []
        for runID,cmd in cmdStrings.values():
            p = Process(target=self._runCmd,args =(runID,cmd,))
            p.start()
            pList.append(p)

        for i in pList:
            i.join()



    def _runBinary(self,cmd):
        if Settings.ins().getSetting(strMiscSettings,strSectRunBinaries).value == "True":
            self.logger.debug("Running binaries is true")
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            self._dummyObject._dummyPollCounter = 0
            self._dummyObject.stderr._dummyPollCounter = 0
            p = self._dummyObject
            self.logger.debug("Running binaries is false")
        return p

    def _runCmd(self,runID, cmd):
        finished = False
        runCounter = 1
        while not finished:
            with cd(self.binaryPath):
                self._status[runID] = strDiStatRunning
                p = self._runBinary(cmd)

                counter = 0
                r = re.compile(r"Ratio:\s\d+\.\d+")
                while p.poll() is None:
                    line = p.stderr.readline()
                    counter = self._logRatio(line,counter,r)
                    self._status[runID] = self._checkDiamondsStdOut(self._status[runID], line)

                line = p.stderr.read()
                self._logRatio(line,10,r)
                self._status[runID] = self._checkDiamondsStdOut(self._status[runID], line)
                if self._status[runID] == strDiStatRunning:
                    finished = True
                    self._status[runID] = strDiamondsStatusGood
                    self.logger.info(f"{runID}: Finished!")
                    return True
                elif runCounter > 5:
                    self.logger.error(f"{runID}: FAILED! Tried 5 runs, failed to find result")
                    return False
                else:
                    self.logger.warning(f"{runID}: Run {runCounter} --> Repeating run, due to failure {self._status[runID]}")
                    runCounter +=1

                #TODO change boundaries depending on result --> do short analysis here



    def _logRatio(self,line,counter,r):
        ratio = r.findall(line)
        if len(ratio) > 0 and counter >= 10:
            for i in ratio:
                self.logger.info(f"{runID} --> {i}")

            counter = 0
        elif len(ratio) == 0:
            self.logger.info(line)
        return counter

    def _checkDiamondsStdOut(self,oldStatus,text):
        """
        Checks the stdout of DIAMONDS and returns the status, that DIAMONDS has.
        :param text: stderr/stdout of diamonds that is analyzed.
        :type text: str
        :return: Statusflag
        :rtype: str
        """
        status = oldStatus
        if strDiamondsErrBetterLikelihood in str(text):
            self.logger.warning("Diamonds cannot find point with better likelihood. Repeat!")
            status = strDiamondsStatusLikelihood

        elif strDiamondsErrCovarianceFailed in str(text):
            self.logger.warning("Diamonds cannot decompose covariance. Repeat!")
            status = strDiamondsStatusCovariance

        elif strDiamondsErrAssertionFailed in str(text):
            self.logger.warning("Diamonds assertion failed. Repeat!")
            status = strDiamondsStatusAssertion
        return status
