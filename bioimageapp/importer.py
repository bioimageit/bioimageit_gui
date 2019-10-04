import os
import datetime

import PySide2.QtCore
from PySide2.QtCore import QObject, QDir
from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, 
                            QTextEdit, QGridLayout, QVBoxLayout,
                            QToolButton, QLineEdit, QMessageBox,
                            QHBoxLayout, QTableWidgetItem, QTableWidget,
                            QAbstractItemView)
from settings import BiSettingsAccess
from framework import BiObject, BiStates, BiContainer, BiModel, BiComponent, BiAction

from bioimagepy import experiment as experimentapi
from bioimagepy.metadata import BiMetaData, BiData, BiRawDataSet, BiProcessedDataSet, BiRun
from bioimagepy.experiment import BiExperiment

from formeditor import BiFormFields, BiFormContent, BiFormWidget
from widgets import BiFileSelectWidget

class BiImporterStates(BiStates):
    DirectoryModified = "BiImporterStates.DirectoryModified"
    PreviousClicked = "BiImporterStates.PreviousClicked"
    NextClicked = "BiImporterStates.NextClicked"
    UpClicked = "BiImporterStates.UpClicked"
    HomeClicked = "BiImporterStates.HomeClicked"
    RefreshClicked = "BiImporterStates.RefreshClicked"
    SettingsClicked = "BiImporterStates.SettingsClicked"
    FilesInfoLoaded = "BiImporterStates.FilesInfoLoaded"
    ItemDoubleClicked = "BiImporterStates.ItemDoubleClicked"
    ItemClicked = "BiImporterStates.ItemClicked"
    NewExperimentClicked = "BiImporterStates.NewExperimentClicked"
    ImportClicked = "BiImporterStates.ImportClicked"
    importValidated = "BiImporterStates.importValidated"
    ImportDone = "BiImporterStates.ImportDone"


class BiImporterContainer(BiContainer):

    def __init__(self):
        super(BiImporterContainer, self).__init__()
        self._object_name = 'BiBrowserContainer'

        # state
        self.states = BiImporterStates()

        # data
        self.rootPath = ''
        self.currentPath = ''
        self.files = list()
        self.doubleClickedRow = -1
        self.clickedRow = -1
        self.historyPaths = list()
        self.posHistory = 0  
        self.in_experiment = False  
        self.importDataUrl = ''
        self.importDataMeta = dict()

    def clickedFileInfo(self):
        return self.files[self.clickedRow]  

    def doubleClickedFile(self):
        return self.files[self.doubleClickedRow].filePath()

    def addHistory(self, path: str):
        self.historyPaths.append(path)

    def moveToPrevious(self):
        self.posHistory -= 1
        if self.posHistory < 0 :
            self.posHistory = 0
        self.currentPath = self.historyPaths[self.posHistory]

    def moveToNext(self):
        self.posHistory += 1
        if self.posHistory >= len(self.historyPaths):
            self.posHistory = len(self.historyPaths) - 1
        self.currentPath = self.historyPaths[self.posHistory]

    def setCurrentPath(self, path: str):
        self.currentPath = path
        if self.posHistory <= len(self.historyPaths):
            for i in range(len(self.historyPaths), self.posHistory):
                self.historyPaths.pop(i)
        self.addHistory(path)
        self.posHistory = len(self.historyPaths) - 1     


class BiImportFormContainer(BiContainer):
    def __init__(self):
        super(BiImportFormContainer, self).__init__()
        self._object_name = 'BiImportFormContainer'

        # state
        self.states = BiImporterStates()

        # data


class BiImporterFileInfo(BiObject):     
    def __init__(self, fileName: str = '', path: str = '', name: str = '', dtype: str = '', date: str = ''):
        super(BiImporterFileInfo, self).__init__()
        self.fileName = fileName
        self.path = path # without file name 
        self.name = name
        self.type = dtype
        self.date = date

    def filePath(self) -> str:
        return os.path.join(self.path, self.fileName)           


class BiImporterModel(BiModel):
    def __init__(self, container: BiImporterContainer):
        super(BiImporterModel, self).__init__()
        self._object_name = 'BiImporterModel'
        self.container = container
        self.container.register(self)
        self.files = list

    def update(self, action: BiAction):
        if action.state == BiImporterStates.DirectoryModified or action.state == BiImporterStates.RefreshClicked:
            self.loadFiles()
            return
    
        if action.state == BiImporterStates.ItemDoubleClicked:
            
            row = self.container.doubleClickedRow
            dcFile = self.container.files[row]
            
            if dcFile.type == "dir":
                self.container.setCurrentPath(os.path.join(dcFile.path,dcFile.fileName))
                self.container.emit(BiImporterStates.DirectoryModified)
            elif dcFile.type == "experiment":
                self.container.openExperimentPath = os.path.join(dcFile.path,dcFile.fileName)
                self.container.emit(BiImporterStates.OpenExperiment)
            else:
                self.container.emit(BiImporterStates.OpenJson)

        if action.state == BiImporterStates.PreviousClicked:
            self.container.moveToPrevious()
            self.container.emit(BiImporterStates.DirectoryModified)
            return

        if action.state == BiImporterStates.NextClicked:
            self.container.moveToNext()
            self.container.emit(BiImporterStates.DirectoryModified)
            return

        if action.state == BiImporterStates.UpClicked:
            dir = QDir(self.container.currentPath)
            dir.cdUp()
            upPath = dir.absolutePath()
            self.container.setCurrentPath(upPath)
            self.container.emit(BiImporterStates.DirectoryModified)
            return

        if action.state == BiImporterStates.HomeClicked:
            dir = QDir(self.container.rootPath)
            path = dir.absolutePath()
            self.container.setCurrentPath(path)
            self.container.emit(BiImporterStates.DirectoryModified)
            return

        if action.state == BiImporterStates.SettingsClicked:
            dir = QDir(self.container.currentPath)
            self.container.bookmarks.set(dir.dirName(), self.container.currentPath)
            self.container.bookmarks.write()
            self.container.emit(BiImporterStates.BookmarksModified)
            return

        if action.state == BiImporterStates.importValidated:

            # import data with bioimagepy
            experiment = BiExperiment( os.path.join(self.container.currentPath, "experiment.md.json"))
            filename = os.path.basename(self.container.importDataUrl)
            md_file_url = experimentapi.import_data(experiment, self.container.importDataUrl, filename, "", "", 'now', True)

            # add metadata
            metadata = BiMetaData(md_file_url)
            metadata.merge(self.container.importDataMeta.data)
            metadata.write()

            self.container.emit(BiImporterStates.ImportDone)
            

    def loadFiles(self):
        experiment_file = os.path.join( self.container.currentPath, 'experiment.md.json' )
        if os.path.isfile(experiment_file):
            self.container.in_experiment = True
            self.loadFilesList(os.path.join( self.container.currentPath, 'data' ))    
        else:  
            self.container.in_experiment = False
            self.loadFilesList(self.container.currentPath)

    def loadFilesList(self, currentPath):
        dir = QDir(currentPath)
        files = dir.entryInfoList()
        self.files = []

        for i in range(len(files)):
            if files[i].fileName() != "." and files[i].fileName() != "..":
                if files[i].isDir():
                    fileInfo = BiImporterFileInfo(files[i].fileName(),
                                           files[i].path(),
                                           files[i].fileName(),
                                           "dir",
                                           files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)


                elif files[i].fileName().endswith("experiment.md.json"):
                    experiment = BiExperiment(files[i].absoluteFilePath())

                    fileInfo = BiImporterFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            experiment.name(),
                                            "experiment",
                                            experiment.createddate())
                    self.files.append(fileInfo)
                    del experiment
         

                elif files[i].fileName().endswith("rawdataset.md.json"):
                    pass
        

                elif files[i].fileName().endswith("processeddataset.md.json"):
                    processedDataSet = BiProcessedDataSet(files[i].absoluteFilePath())

                    fileInfo = BiImporterFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            processedDataSet.name(),
                                            "processeddataset",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del processedDataSet
        

                elif files[i].fileName().endswith(".md.json"):
                    data = BiData(files[i].absoluteFilePath())
                    fileInfo = BiImporterFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            data.name(),
                                            data.origin_type() + "data",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del data

        self.container.files = self.files
        self.container.emit(BiImporterStates.FilesInfoLoaded)


class BiImportFormModel(BiModel):
    def __init__(self, container: BiImporterContainer):
        super(BiImportFormModel, self).__init__()
        self._object_name = 'BiImportFormModel'
        self.container = container
        self.container.register(self)

    def update(self, container: BiContainer):
        pass    


class BiImporterSideBarComponent(BiComponent):
    def __init__(self, container: BiImporterContainer):
        super(BiImporterSideBarComponent, self).__init__()
        self._object_name = 'BiImporterSideBarComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(mainLayout)

        self.wwidget = QWidget()
        mainLayout.addWidget(self.wwidget)
        self.wwidget.setObjectName("BiImporterSideBar")

        layout = QVBoxLayout()
        self.wwidget.setLayout(layout)

        self.addExpermentbutton = QPushButton(self.wwidget.tr("New Experiment"))
        self.addExpermentbutton.setObjectName("BiImporterSideBarNewButton")
        self.addExpermentbutton.released.connect(self.newExperimentClicked)
        layout.addWidget(self.addExpermentbutton, 0, PySide2.QtCore.Qt.AlignTop)

        self.importDatabutton = QPushButton(self.wwidget.tr("Import Data"))
        self.importDatabutton.setObjectName("BiImporterSideBarNewButton")
        self.importDatabutton.released.connect(self.importDataClicked)
        layout.addWidget(self.importDatabutton, 0, PySide2.QtCore.Qt.AlignTop)

        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop) 

    def update(self, action: BiAction):
        if action.state == BiImporterStates.DirectoryModified:
            if self.container.in_experiment:
                self.addExpermentbutton.setVisible(False)
                self.importDatabutton.setVisible(True)
            else:
                self.addExpermentbutton.setVisible(True) 
                self.importDatabutton.setVisible(False)   


    def newExperimentClicked(self):
        self.container.emit(BiImporterStates.NewExperimentClicked)

    def importDataClicked(self):
        self.container.emit(BiImporterStates.ImportClicked)    

    def get_widget(self): 
        return self.widget     


class BiImporterToolBarComponent(BiComponent):
    def __init__(self, container: BiImporterContainer):
        super(BiImporterToolBarComponent, self).__init__()
        self._object_name = 'BiImporterToolBarComponent'
        self.container = container
        self.container.register(self)

        # build widget
        self.widget = QWidget()
        self.widget.setObjectName("BiToolBar")
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # previous
        previousButton = QToolButton()
        previousButton.setObjectName("BiBrowserToolBarPreviousButton")
        previousButton.setToolTip(self.widget.tr("Previous"))
        previousButton.released.connect(self.previousButtonClicked)
        layout.addWidget(previousButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # next
        nextButton = QToolButton()
        nextButton.setObjectName("BiBrowserToolBarNextButton")
        nextButton.setToolTip(self.widget.tr("Next"))
        nextButton.released.connect(self.nextButtonClicked)
        layout.addWidget(nextButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # up
        upButton = QToolButton()
        upButton.setObjectName("BiExperimentToolBarUpButton")
        upButton.setToolTip(self.widget.tr("Up"))
        upButton.released.connect(self.upButtonClicked)
        layout.addWidget(upButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # home
        homeButton = QToolButton()
        homeButton.setObjectName("BiExperimentToolBarHomeButton")
        homeButton.setToolTip(self.widget.tr("Home"))
        homeButton.released.connect(self.homeButtonClicked)
        layout.addWidget(homeButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # data selector
        self.pathLineEdit = QLineEdit(self.widget)
        self.pathLineEdit.returnPressed.connect(self.pathEditReturnPressed)
        layout.addWidget(self.pathLineEdit, 1)

        # refresh
        refreshButton = QToolButton()
        refreshButton.setObjectName("BiExperimentToolBarRefreshButton")
        refreshButton.setToolTip(self.widget.tr("Reload"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # settings
        settingsButton = QToolButton()
        settingsButton.setObjectName("BiExperimentToolBarSettingsButton")
        settingsButton.setToolTip(self.widget.tr("Settings"))
        settingsButton.released.connect(self.settingsButtonClicked)
        layout.addWidget(settingsButton, 0, PySide2.QtCore.Qt.AlignLeft)

    def update(self, action: BiAction):
        if action.state == BiImporterStates.FilesInfoLoaded:
            self.pathLineEdit.setText(self.container.currentPath)

    def previousButtonClicked(self):
        self.container.emit(BiImporterStates.PreviousClicked)

    def nextButtonClicked(self):
        self.container.emit(BiImporterStates.NextClicked)

    def upButtonClicked(self):
        self.container.emit(BiImporterStates.UpClicked)

    def homeButtonClicked(self):
        self.container.emit(BiImporterStates.HomeClicked)    

    def pathEditReturnPressed(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.emit(BiImporterStates.DirectoryModified)

    def refreshButtonClicked(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.emit(BiImporterStates.RefreshClicked)

    def settingsButtonClicked(self):
        msgBox = QMessageBox()
        msgBox.setText("Settings not yet implemented ?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        msgBox.exec_()

    def get_widget(self): 
        return self.widget        


class BiImporterTableComponent(BiComponent):
    def __init__(self, container: BiImporterContainer):
        super(BiImporterTableComponent, self).__init__()
        self._object_name = 'BiImporterTableComponent'
        self.container = container
        self.container.register(self)
        self.buildWidget()


    def buildWidget(self):

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.cellDoubleClicked.connect(self.cellDoubleClicked)
        self.tableWidget.cellClicked.connect(self.cellClicked)

        labels = ['', 'Name', 'Date', 'Type']
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)

    def update(self, action : BiAction):
        if action.state == BiImporterStates.FilesInfoLoaded:
            i = -1
            # check if dir is an experiment
            self.tableWidget.setRowCount(len(self.container.files))
            for fileInfo in self.container.files:
                i += 1
                # icon depends on type
                iconLabel = QLabel(self.tableWidget)
                if fileInfo.type == "dir":
                    iconLabel.setObjectName("BiBrowserDirIcon")
                elif fileInfo.type == "run":
                    iconLabel.setObjectName("BiBrowserRunIcon")
                elif fileInfo.type == "experiment":
                    iconLabel.setObjectName("BiBrowserExperimentIcon")
                elif fileInfo.type == "rawdataset":
                    iconLabel.setObjectName("BiBrowserRawDatSetIcon")
                elif fileInfo.type == "processeddataset":
                    iconLabel.setObjectName("BiBrowserProcessedDataSetIcon")
                elif fileInfo.type == "rawdata":
                    iconLabel.setObjectName("BiBrowserRawDatIcon")
                elif fileInfo.type == "processeddata":
                    iconLabel.setObjectName("BiBrowserProcessedDataIcon")

                # icon
                self.tableWidget.setCellWidget(i, 0, iconLabel)
                # name
                self.tableWidget.setItem(i, 1, QTableWidgetItem(fileInfo.name))
                # date
                self.tableWidget.setItem(i, 2, QTableWidgetItem(fileInfo.date))
                # type
                self.tableWidget.setItem(i, 3, QTableWidgetItem(fileInfo.type))
            
    def cellDoubleClicked(self, row: int, col: int):
        self.container.doubleClickedRow = row
        self.container.emit(BiImporterStates.ItemDoubleClicked)

    def cellClicked(self, row : int, col : int):
        self.container.clickedRow = row
        self.container.emit(BiImporterStates.ItemClicked)

    def get_widget(self): 
        return self.widget          


class BiImportFormComponent(BiComponent):
    def __init__(self, container: BiImporterContainer, fields_file: str):
        super(BiImportFormComponent, self).__init__()
        self._object_name = 'BiImportFormComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        layout = QVBoxLayout()
        self.widget.setLayout(layout)
        
        title = QLabel('Import Data')
        title.setObjectName('BiLabelFormHeader1')
        layout.addWidget(title)

        self.fileSelectorWidget = BiFileSelectWidget(False, self.widget)
        layout.addWidget(self.fileSelectorWidget) 

        metadataTitle = QLabel('Metadata')
        metadataTitle.setObjectName('BiLabelFormHeader1')
        layout.addWidget(metadataTitle)

        formFields = BiFormFields(fields_file)
        formContent = BiFormContent()
        self.formWidget = BiFormWidget(formFields, formContent, False)
        layout.addWidget(self.formWidget)

        # buttons
        buttonsWidget = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsWidget.setLayout(buttonsLayout)
        saveButton = QPushButton(self.widget.tr("Import"))
        saveButton.setObjectName("btnPrimary")
        cancelButton = QPushButton(self.widget.tr("Cancel"))
        cancelButton.setObjectName("btnDefault")
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(cancelButton)

        saveButton.released.connect(self.emitSave)

        layout.addWidget(buttonsWidget)

    def emitSave(self):
        self.container.importDataUrl = self.fileSelectorWidget.text()
        self.container.importDataMeta = self.formWidget.getContent()
        self.container.emit(BiImporterStates.importValidated)    

    def update(self, action : BiAction):
        pass

    def get_widget(self): 
        return self.widget       
