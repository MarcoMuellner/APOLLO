from logging import getLogger
import os
import re
import subprocess
from multiprocessing import Process
import numpy as np

from res.strings import *
from support.directoryManager import cd
from background.backgroundResults import BackgroundResults
import time
from res.conf_file_str import general_background_result_path,general_binary_path,general_kic



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
    """
    Background Process allows for concurrent runs of diamonds for both modes. Use run() to get it started
    """

    def __init__(self,kwargs):
        self.logger = getLogger(__name__)
        self.kicID = kwargs[general_kic]
        self.binaryPath = kwargs[general_binary_path]
        self.model = strRunIDBoth

        self.resultsPath = kwargs[general_background_result_path]

        self.modes = {strDiModeFull: strDiIntModeFull
            ,strDiModeNoise :  strDiIntModeNoise}

        self.status = {}
        self.priorChanges = {}
        self._dummyObject = _dummyProcessObject()

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
        for runID,diIntMode in self.modes.items():
            if self.model not in [runID, strRunIDBoth]:
                self.logger.info(f"Skipping {runID}")
                continue

            self.priorChanges[runID] = {}

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
        for runID,cmd in cmdStrings.items():
            p = Process(target=self._runCmd,args =(runID,cmd,))
            p.start()
            pList.append(p)

        for i in pList:
            i.join()



    def _runBinary(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p

    def _checkResults(self,runID,runNo):
        result = BackgroundResults(self.kicID,runID)
        prior = result.prior
        priorData = prior.getData(runID)
        values = result.summary.getData()
        triggerSave = False
        for name,value in values.items():
            if name not in self.priorChanges.keys():
                self.priorChanges[runID][name] = 0

            lowerBound,upperBound = priorData[name]

            lowValue = value/lowerBound < 1.05
            highValue = upperBound/value < 1.05

            if Settings.ins().getSetting(strDataSettings, strSectStarType).value == strStarTypeYoungStar:
                k = -0.1
                d = 0.6
            else:
                k = - 0.0875
                d = 0.4875

            if lowValue or highValue:
                changeValue = k*runNo + d

                if lowValue:
                    self.logger.warning(f"Prior {name} to low! Value reaches lower bound. Lower bound: {lowerBound},"
                                        f"Value: {value}, Ratio {value/lowerBound}")
                    multiplier = 1-changeValue
                    priorData[name] = (multiplier*priorData[name][0],multiplier*priorData[name][1])
                    self.priorChanges[runID][name] -= changeValue
                elif highValue:
                    self.logger.warning(f"Prior {name} to high! Value reaches upper bound. Upper bound: {upperBound}, "
                                        f"Value: {value}, Ratio {upperBound/value}")
                    multiplier = 1 + changeValue
                    priorData[name] = (multiplier * priorData[name][0], multiplier * priorData[name][1])
                    self.priorChanges[runID][name] += changeValue

                self.logger.info(f"Prior {name}: Setting to {priorData[name]}")
                triggerSave = True

        if triggerSave:
            self.logger.info(f"Rerunning {runID} due to change of priors")
            prior.rewritePriors(priorData)
            self.status[runID] = strDiamondsStatusPriorsChanged
            return False
        else:
            return True


    def _runCmd(self,runID, cmd):
        for runCounter in range(1,6):
            self.logger.info(f"Starting {runID}:no {runCounter}")
            with cd(self.binaryPath):
                self.status[runID] = strDiStatRunning
                p = self._runBinary(cmd)

                logCounter = 0
                r = re.compile(r"(Nit:\s\d+).+(Ratio: [\w\d\.\+]+)")
                time.sleep(5)
                while p.poll() is None:
                    line = p.stderr.readline().decode("utf-8")
                    logCounter = self._logRatio(runID,line,logCounter,r)
                    self.status[runID] = self._checkDiamondsStdOut(self.status[runID], line)
                    logCounter +=1
                line = p.stderr.read().decode("utf-8")
                self._logRatio(runID,line,10,r)

                self.status[runID] = self._checkDiamondsStdOut(self.status[runID], line)
                if self.status[runID] == strDiStatRunning: #and self._checkResults(runID,runCounter):
                    self.status[runID] = strDiamondsStatusGood
                    self.logger.info(f"{runID}: Finished!")
                    return True

                else:
                    self.logger.warning(f"{runID}: Run {runCounter} --> Repeating run, due to failure due to {self.status[runID]}")

        self.logger.error(f"{runID}: FAILED! Tried 5 runs, failed to find result")
        return False



    def _logRatio(self,runID,line,counter,r):
        match = r.findall(line)
        if len(match) > 0 and counter >= 10:
            for it,ratio in match:
                print(f"{runID} --> {it},{ratio}")

            counter = 0
        elif len(match) == 0 and counter >= 10:
            print(f"{line}")
            counter = 0
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
