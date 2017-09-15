#Library Imports
import logging

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

# Application Imports
from res.strings import *


class Connector(QObject):

    sigLocalSettingChanged =  pyqtSignal(str,str)
    def __init__(self,name,guiType,sectionName,widget,signal):
        QObject.__init__(self)
        self.__logger =logging.getLogger(__name__)
        self.__logger.debug("Creating Connector with name '"+name+"' and guiType '"+guiType+"'")
        self.__name = name
        self.__section = sectionName
        self.__widget = widget
        if guiType == strGUITypeTextEdit:
            self.__logger.debug("Creating textEdit connector")
            signal.connect(self.__textEditChanged)
        elif guiType == strGUITypeCheckBox:
            self.__logger.debug("Creating checkBox connector")
            signal.connect(self.__checkBoxChanged)
        else:
            self.__logger.error("No gui added with type '"+guiType+"'")
            raise

    def getString(self):
        return self.__value

    @pyqtSlot()
    def __textEditChanged(self):
        self.__value = self.__widget.text()
        self.__logger.debug("Value is '"+self.__value+"'")
        self.sigLocalSettingChanged.emit(self.__section,self.__name)

    def __checkBoxChanged(self):
        self.__value = str(self.__widget.isChecked())
        self.__logger.debug("Value is '"+self.__value+"'")
        self.sigLocalSettingChanged.emit(self.__section,self.__name)
