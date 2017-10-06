#Library Imports
import logging

# Application Imports
from res.strings import *
from support.observers import obsDict
from support.observers import obsSetting
from support.singleton import Singleton


@Singleton
class Settings:
    """
    This class represents the possibility to create Settings on a machine. It will automatically reread the file if it
    changed and write it to the file if a setting in the program changed. Assumes the settings file at the head of
    your user dir.
    To access settings:
    Settings.Instance().getSetting(strSect,strOpt).value
    To write settings:
    Settings.Instance().setSetting(setting). See method for docu
    """
    def __init__(self,*args):
        """
        Constructor of the object
        """
        self.__logger = logging.getLogger(__name__)
        self.__defSettingMap = obsDict(strPathDefSettings,True)
        self.__custSettingMap = obsDict(strPathSettings,False)
        self._adjustCustMapWithDefMap()

    def _adjustCustMapWithDefMap(self):
        """
        This method reads the current settings file and checks if all the settings from the default one are
        available. If not it will create them with the default value provided in the default settings.
        :return:
        :rtype:
        """
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
        """
        Returns a settings observer dict. To get the value you have to call .value
        """
        return obsSetting(self.__custSettingMap,innerSection,option)

    def setSetting(self,setting):
        """
        Sets a setting with setting. This has to be a dictionary, similar to the setting you want to set. Its easiest
        to get the setting by calling getSetting, which will return the settings observer dict and change the value in
        there
        """
        for key in setting:
            self.__logger.info("Setting section '"+setting[key][0]+"', option '"+key+"', value '"+setting[key][1]+"'")
            obsSet = obsSetting(self.__custSettingMap,setting[key][0],key)
            obsSet.value = setting[key][1]

    @property
    def customPath(self):
        """
        Property of the custom path
        """
        return self._customPath

    @customPath.setter
    def customPath(self,value):
        """
        Custom path setter. Sets the path to the settings file by assigning a different path. If the setting
        doesn't exist there, it will be created. From now on, the Settings class will only use these settings
        """
        self._customPath = value
        self.__custSettingMap = obsDict(self._customPath,False)
        self._adjustCustMapWithDefMap()

    def getAllSettings(self):
        """
        Returns a full obs dict of all settings
        """
        return self.__custSettingMap.map

