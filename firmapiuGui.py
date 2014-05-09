#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.appName = 'FirmaPiu - Digital Signer Software'
        self.resize(350, 250)
        self.setWindowTitle(self.appName)
        self.statusBar().showMessage('Messaggio')

        # creo il widget astratto che conterra' tutti gli altri
        cWidget = QtGui.QWidget(self)
        # creo un layout verticale
        vBox = QtGui.QVBoxLayout()
        # setto il layout del widget
        grid = QtGui.QGridLayout()

        # creo i bottoni
        button1 = QtGui.QPushButton('Quit')
        button1.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button1, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button2 = QtGui.QPushButton('Quit')
        button2.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button2, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button3 = QtGui.QPushButton('Quit')
        button3.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button3, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button4 = QtGui.QPushButton('Quit')
        button4.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button4, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button5 = QtGui.QPushButton('Quit')
        button5.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button5, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button6 = QtGui.QPushButton('Quit')
        button6.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button6, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button7 = QtGui.QPushButton('Quit')
        button7.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button7, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button8 = QtGui.QPushButton('Quit')
        button8.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button8, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        button9 = QtGui.QPushButton('Quit')
        button9.setFont(QtGui.QFont("Sans", 10, QtGui.QFont.Bold))
        self.connect(button9, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))

        logTxt = QtGui.QTextEdit()

        grid.addWidget(button1, 0, 0)
        grid.addWidget(button2, 0, 1)
        grid.addWidget(button3, 0, 2)
        grid.addWidget(button4, 1, 0)
        grid.addWidget(button5, 1, 1)
        grid.addWidget(button6, 1, 2)
        grid.addWidget(button7, 2, 0)
        grid.addWidget(button8, 2, 1)
        grid.addWidget(button9, 2, 2)

        vBox.addLayout(grid)
        vBox.addWidget(logTxt)

        # creo le azioni del menu
        quitAction = QtGui.QAction('Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit Application')
        self.connect(quitAction, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        self.connect(quitAction, QtCore.SIGNAL('hovered()'), self.mySlot)

        # aggiungo un menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(quitAction)

        settingMenu = menuBar.addMenu('&Impostazioni')

        cWidget.setLayout(vBox)
        self.setCentralWidget(cWidget)

    def mySlot(self):
        print 'Menu voice hovered'


app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
