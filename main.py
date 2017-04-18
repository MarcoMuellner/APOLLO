#Library Includes
from PyQt5.QtWidgets import QApplication
import sys
#
#a = QApplication(sys.argv)

#import qt5reactor
#try:
#    qt5reactor.install()
#except:
#    print("Allready Installed")

#from twisted.internet import reactor
#
#Application Includes
#from gui.gui import MainWindow
from loghandler import loghandler
from runner import StandardRunner


loghandler.setup_logging()

run = StandardRunner()


#Use this when you want to start GUI stuff!
#w = MainWindow(reactor)
#w.show()
#reactor.run(
