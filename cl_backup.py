#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

"""

import sys, os
from PyQt4 import QtCore, QtGui
from cl_download import *
import exiting 

class WorkThread(QtCore.QThread):

    def __init__(self, username, dl_palettes, dl_patterns):

        QtCore.QThread.__init__(self)
        self.username = str(username) #username was still a QString at this point 
        self.dl_palettes = dl_palettes
        self.dl_patterns = dl_patterns 
        self.downloader = Downloader()


    def __del__(self):

        exiting.exiting = True 
        self.wait()


    def run(self):
      
        exiting.exiting = False 
        try:
            username_dir = "".join(i for i in self.username if i not in "\/:*?<>|")
            if self.dl_palettes:
                dir_pal = 'palettes_' + username_dir
                if not os.path.isdir(dir_pal): 
                    try: os.mkdir(dir_pal)
                    except: dir_pal = os.getcwd()
                self.downloader.download_palettes(self.username, dir_pal)

            if exiting.exiting: return 
            if self.dl_patterns:
                dir_pat = 'patterns_' + username_dir
                if not os.path.isdir(dir_pat): 
                    try: os.mkdir(dir_pat)
                    except: dir_pat = os.getcwd()
                self.downloader.download_patterns(self.username, dir_pat)

            if not exiting.exiting:            
                self.emit(QtCore.SIGNAL('update(QString)'), "Download for %s finished!" %self.username)
            #self.terminate() #böse böse!

        except Exception as e:
            #(type, value, traceback) = sys.exc_info()
            #sys.excepthook(type, value, traceback)
            self.emit(QtCore.SIGNAL('update(QString)'), "An error has ocurred. Please restart the program.")
            return 


class CLTool(QtGui.QWidget):
    
    def __init__(self):
        super(CLTool, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.userLabel = QtGui.QLabel('Username:')
        self.userEdit = QtGui.QLineEdit('Trixxie')
        self.paletteCheckbox = QtGui.QCheckBox('Download palettes', self)
        self.patternCheckbox = QtGui.QCheckBox('Download patterns', self)
        self.downloadButton = QtGui.QPushButton("Start Download", self)
        self.stopDownloadButton = QtGui.QPushButton("Stop Download", self)
        self.loggingDisplay = QtGui.QTextBrowser()

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.userLabel, 1, 0)
        grid.addWidget(self.userEdit, 1, 1)
        grid.addWidget(self.paletteCheckbox, 2, 0)
        grid.addWidget(self.patternCheckbox, 3, 0)
        grid.addWidget(self.downloadButton, 4, 0, 1, 2)
        grid.addWidget(self.stopDownloadButton, 5, 0, 1, 2)
        grid.addWidget(self.loggingDisplay, 6, 0, 3, 2)

        self.setLayout(grid) 
        self.setGeometry(400, 400, 450, 250)
        self.setWindowTitle('CL Download Tool')    
        self.setWindowIcon(QtGui.QIcon('icon.png'))        
        self.patternCheckbox.setChecked(True)

        self.userEdit.setFocus()
        self.loggingDisplay.append("Please insert a user name. Download not yet started.") 
        self.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.stopDownloadButton.clicked.connect(self.stopDownloadButtonClicked)

        self.show()

    def log(self, message):

        self.loggingDisplay.append(message) 
        
    def reactivateButton(self):

        self.downloadButton.setEnabled(True) 
        exiting.exiting = False 

    def okToQuit(self):


        if not self.workThread.isRunning(): 
            return True 

        reply = QtGui.QMessageBox.question(self, "Download incomplete", "Do you really want to abort the download and quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)

        if reply == QtGui.QMessageBox.Cancel: return False
        elif reply == QtGui.QMessageBox.Yes: return True 
        else: return False 

    def closeEvent(self, event):

        if self.okToQuit():
            exiting.exiting = True 
            self.workThread.wait()
        else:
            event.ignore()

    def stopDownloadButtonClicked(self):

        if not self.workThread.isRunning():
            return 

        exiting.exiting = True
        self.workThread.wait()
        if self.workThread.isFinished():
            self.log("Downloading aborted.")
            exiting.exiting = False 
            self.reactivateButton()
            self.workThread.__del__()


    def downloadButtonClicked(self):

        dl_palettes = False
        dl_patterns = False 
        exiting.exiting = False 
        username = self.userEdit.text()
        if not username:
            self.log("Please insert a user name. If an invalid user name is entered, the 1000 most popular patterns of all users will be downloaded.")
            return 

        if self.paletteCheckbox.isChecked():
            dl_palettes = True
        if self.patternCheckbox.isChecked():
            dl_patterns = True
            
        if dl_palettes and dl_patterns: 
            self.log("Will download palettes and patterns of %s." %username) 
        elif dl_palettes:
            self.log("Will download palettes of %s." %username)
        elif dl_patterns:
            self.log("Will now download patterns of %s." %username)
        else:
            return
        self.downloadButton.setEnabled(False)        

        self.workThread = None 
        self.workThread = WorkThread(username, dl_palettes, dl_patterns)
        self.connect(self.workThread, QtCore.SIGNAL("update(QString)"), self.log)
        self.connect(self.workThread, QtCore.SIGNAL("terminate()"), self.reactivateButton)
        self.connect(self.workThread, QtCore.SIGNAL("finished()"), self.reactivateButton)
        self.connect(self.workThread.downloader, QtCore.SIGNAL("update(QString)"), self.log)

        self.workThread.start()
        

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = CLTool()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
