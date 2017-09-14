import sys
from PyQt5.QtWidgets import QApplication
from gui.interface import MainWindow

app = QApplication(sys.argv)

mainWindow = MainWindow()
mainWindow.go()

sys.exit(app.exec_())
