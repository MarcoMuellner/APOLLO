from PyQt5.QtWidgets import QWidget

class MainWindow:
    def __init__(self):
        self.__createWindow()
    def go(self):
        self.mainWidget.show()
    def __createWindow(self):
        self.mainWidget = QWidget()
