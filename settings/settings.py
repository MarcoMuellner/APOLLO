#Library Imports
import logging

# Application Imports
from res.strings import *
from support.observers import obsDict
from support.observers import obsSetting
from support.singleton import Singleton


@Singleton
class Settings:
    def __init__(self,customPath = None):
        self.__logger = logging.getLogger(__name__)
        self.__defSettingMap = obsDict(strPathDefSettings)
        self.__custSettingMap = obsDict(strPathSettings)
        self.__adjustCustMapWithDefMap()

    def __adjustCustMapWithDefMap(self):
        self.__logger.log(9,"Syncing default map with custMap")
        defMap = self.__defSettingMap.map
        custMap = self.__custSettingMap.map
        self.__logger.log(9,"Content of def Map is '"+str(defMap)+"'")
        for mainSect in defMap:
            self.__logger.log(9,"Entering Main Section '"+mainSect+"' with data '"+str(defMap[mainSect]))
            if mainSect not in custMap:
                self.__logger.info("Main Section '"+mainSect+"' is not part of CustMap. Adding '"+str(defMap[mainSect])+"'")
                custMap[mainSect] = defMap[mainSect]
            else:
                for innerSect  in defMap[mainSect]:
                    self.__logger.log(9,"Entering Inner Section '"+innerSect+"' with data '"+str(defMap[mainSect][innerSect])+"'")
                    if innerSect not in custMap[mainSect]:
                        self.__logger.info("Inner Section '"+innerSect+"' is not part of CustMap. Adding '"+str(defMap[mainSect][innerSect])+"'")
                        custMap[mainSect][innerSect] = defMap[mainSect][innerSect]
                    else:
                        for option in defMap[mainSect][innerSect]:
                            self.__logger.log(9,"Entering Option '"+option+"' with data '"+str(defMap[mainSect][innerSect][option])+"'")
                            if option not in custMap[mainSect][innerSect]:
                                self.__logger.info("Option '"+option+"' is not part of CustMap. Adding '"+str(defMap[mainSect][innerSect][option])+"'")
                                custMap[mainSect][innerSect][option] = defMap[mainSect][innerSect][option]
                            else:
                                for innerOption in defMap[mainSect][innerSect][option]:
                                    self.__logger.log(9,"Entering innerOption '"+innerOption+"' with data '"+str(defMap[mainSect][innerSect][option][innerOption])+"'")
                                    if innerOption not in custMap[mainSect][innerSect][option]:
                                        self.__logger.info("InnerOption '"+innerOption+"' is not part of CustMap. Adding '"+str(defMap[mainSect][innerSect][option][innerOption])+"'")
                                        custMap[mainSect][innerSect][option][innerOption] = defMap[mainSect][innerSect][option][innerOption]
        self.__custSettingMap.map = custMap
        self.__defSettingMap.map = defMap

    def getSetting(self,innerSection,option):
        return obsSetting(self.__custSettingMap,innerSection,option)

    def setSetting(self,setting):
        for key in setting:
            self.__logger.info("Setting section '"+setting[key][0]+"', option '"+key+"', value '"+setting[key][1]+"'")
            obsSet = obsSetting(self.__custSettingMap,setting[key][0],key)
            obsSet.value = setting[key][1]

    @property
    def customPath(self):
        return self._customPath

    @customPath.setter
    def customPath(self,value):
        self._customPath = value
        self.__custSettingMap = obsDict(self._customPath)
        self.__adjustCustMapWithDefMap()

    def getAllSettings(self):
        return self.__custSettingMap.map

