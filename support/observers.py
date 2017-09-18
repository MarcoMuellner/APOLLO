#Library Imports
import json
import logging
from multiprocessing import Lock

# Application Imports
from res.strings import *


class obsDict(object):
    def __init__(self,pathToFile,readOnly):
        self.__observers = []
        self.__path = pathToFile
        self.__lock = Lock()
        self.__readOnly = readOnly
        if self.__checkFile(self.__path):
            with open(pathToFile, 'rt') as f:
                self.__map = json.load(f)
        else:
            self.__map = {}

    def __checkFile(self,path):
        return os.path.isfile(path)

    @property
    def map(self):
        return self.__map

    @map.setter
    def map(self,value):
 #       self.__lock.acquire()
        self.__map = value


        if not self.__readOnly:
            with open(self.__path,'w') as outfile:
                json.dump(self.__map,outfile,sort_keys = True, indent = 4, separators=(',',':'))

        for callback in self.__observers:
            callback(self.__map)
 #       self.__lock.release()

    @map.getter
    def map(self):
#        self.__lock.acquire()
        try:
            return self.__map
        finally:
            pass
#            self.__lock.release()


    @map.deleter
    def map(self):
        del self.__map

    def bind_to(self,callback):
        self.__observers.append(callback)

class obsSetting(object):
        def __init__(self,settingsDictionary,innerSection,option):
            self.__logger = logging.getLogger(__name__)
            self.__dict = settingsDictionary
            self.__innerSect = innerSection
            self.__option = option
            self.__logger.log(9,"dict is '"+str(self.__dict.map)+"', innerSect is '"+self.__innerSect+"', option is '"+self.__option+"'")
            self.__dict.bind_to(self.__dictChanged)
            self.__observers =  []
            self.__lock = Lock()

            self.__value = self.__dict.map['Settings'][self.__innerSect][self.__option][strOptionValue]
            self.__logger.log(9,"Value set to '"+self.__value+"'")

        def bind_to(self,callback):
            self.__logger.log(9,"Adding callback '"+str(callback)+"'")
            self.__observers.append(callback)

        def __dictChanged(self,dictionary):
            if self.value is not self.__dict.map['Settings'][self.__innerSect][self.__option][strOptionValue]:
                self.__value = self.__dict.map['Settings'][self.__innerSect][self.__option][strOptionValue]
                self.__runCallback()

        def __runCallback(self):
            self.__logger.log(9,"Running callbacks")
            for callback in self.__observers:
                self.__logger.log(9,"Callback called is '"+str(callback)+"'")
                callback(self.__value)

        @property
        def value(self):
            return self.__value

        @value.setter
        def value(self,value):
            self.__logger.log(9,"Entering with value '"+str(value)+"'")
 #           self.__lock.acquire()
            try:
                self.__value = value
                internalDict = self.__dict.map
                internalDict['Settings'][self.__innerSect][self.__option][strOptionValue] = self.__value
                self.__dict.map = internalDict
                self.__runCallback()
            finally:
#                self.__lock.release()
                self.__logger.log(9,"Leaving")

        @value.getter
        def value(self):
            self.__logger.log(9,"Entering option '"+self.__option+"'")
#            self.__lock.acquire()
            try:
                return self.__value
            finally:
#                self.__lock.release()
                self.__logger.log(9,"Leaving '"+self.__option+"'")

        def guiName(self):
            return self.__dict.map['Settings'][self.__innerSect][self.__option][strOptionName]

        def guiType(self):
            return self.__dict.map['Settings'][self.__innerSect][self.__option][strOptionType]

        def section(self):
            return self.__innerSect

        def optionName(self):
            return self.__option
