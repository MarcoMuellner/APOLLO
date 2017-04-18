#Library Imports
import os
import logging
from configparser import ConfigParser
#Application Imports
from support.strings import *
from support.singleton import Singleton

@Singleton
class Settings:
    def __init__(self):
        self.__logger =logging.getLogger(__name__)
        self.__logger.debug("Checking file")
        self.__checkFile()
        self.__logger.debug("Creating lock")
        self.__rwLock = Lock()

    def __checkFile(self):
        config = ConfigParser()
        config.optionxform = str
        if not self.__fileExists():
            self.__logger.warning("File does not exist, creating in path '"+strPathSettings+"'")
            config_file = open(strPathSettings,'w')
            config_file.close()
        else:
            self.__logger.debug("File does exist continue")

    def __fileExists(self):
        return os.path.isfile(strPathSettings)

    def getAllSettings(self):
        config = ConfigParser()
        config.optionxform = str
        config.read(strPathSettings)
        returnDict = {}
        for s in config.sections():
            returnDict[s] = self.getOption(s)[s]

        return returnDict

    def getOption(self,optionName):
        self.__logger.debug("Option name is '"+optionName+"', acquiring lock")
        self.__rwLock.acquire()
        try:
            config = ConfigParser()
            config.optionxform = str
            self.__logger.debug("Reading settings from path '"+strPathSettings+"'")
            config.read(strPathSettings)
            self.__logger.debug("Checking if setting has option '"+optionName+"'")
            if config.has_section(optionName):
                self.__logger.debug("Settings has Section '"+optionName+"', reading values")
                optionList = []
                for o in config.options(optionName):
                    optionList.append((o,config.get(optionName,o)))

                self.__logger.info("Reading values for section '"+optionName+"'")
                self.__logger.info("Values are '"+str(optionList)+"'")

                return {optionName:optionList}
            else:
                self.__logger.warning("No section with '"+optionName+"', creating dummy object")
                return {optionName:None}
        finally:
            self.__logger.debug("Releasing lock")
            self.__rwLock.release()

    def setOption(self,optionName,values):
        self.__logger.info("Setting Section '"+optionName+"' with the following values:")
        self.__logger.info(values)
        self.__logger.debug("Option name is '"+optionName+"', acquiring lock, send Notification is '"+str(sendNotification)+"'")
        self.__rwLock.acquire()

        try:
            if type(optionName) is not str or type(values) is not list:
                self.__log.critical("OptionName and Values are not of the correct type. OptionName is '"+str(type(optionName))+"' values is '"+str(type(values))+"'")
                raise
            config = ConfigParser()
            config.optionxform = str
            self.__logger.debug("Reading from settings path '"+strPathSettings+"'")
            config.read(strPathSettings)

            if not config.has_section(optionName):
                self.__logger.info("Creating section with name '"+optionName+"'")
                config.add_section(optionName)

            self.__logger.debug("Setting options")
            for o in values:
                self.__logger.debug("Setting options")
                config.set(optionName,o[0],o[1])

            self.__logger.debug("Writing to settings file")
            with open(strPathSettings,'w') as write_file:
                config.write(write_file)

            return {optionName:values}
        finally:
            self.__logger.debug("Releasing lock")
            self.__rwLock.release()
