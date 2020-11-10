import sys
from PySide2 import QtCore, QtScxml


app = QtCore.QCoreApplication()
el = QtCore.QEventLoop()

sm = QtScxml.QScxmlStateMachine.fromFile('states.scxml')

sm.start()
el.processEvents()