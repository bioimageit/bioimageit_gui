import os
import json
import PySide2.QtCore
from PySide2.QtCore import QObject, QDir
from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, 
                            QTextEdit, QGridLayout, QVBoxLayout,
                            QToolButton, QLineEdit, QMessageBox,
                            QHBoxLayout, QTableWidgetItem, QTableWidget,
                            QAbstractItemView)
from framework import BiObject, BiContainer, BiModel, BiComponent
from widgets import BiButton
from bioimagepy.metadata import BiData, BiRawDataSet, BiProcessedDataSet, BiRun
from bioimagepy.experiment import BiExperiment

class BiBrowserBookmarks(BiObject):
    def __init__(self, filename = ''):
        super(BiBrowserBookmarks, self).__init__()
        self._object_name = 'BiBrowserBookmarks'
        self.filename = filename
        self.bookmarks = dict()
        if filename != '':
            self.read() 

    def read(self):
        """Read the bookmarks to the file in json format"""
        if os.path.getsize(self.filename) > 0:
            with open(self.filename) as json_file:  
                self.bookmarks = json.load(json_file)

    def write(self):
        """Write the bookmarks to the json file at filename"""
        with open(self.filename, 'w') as outfile:
            json.dump(self.bookmarks, outfile, indent=4)  

    def clear(self):
        self.bookmarks = dict()

    def set(self, name: str, url: str):
        data = dict()
        data['name'] = name
        data['url'] = url
        self.bookmarks['bookmarks'].append(data)

class BiBrowserContainer(BiContainer):
    DirectoryModified = "BiBrowserContainer::DirectoryModified"
    PreviousClicked = "BiBrowserContainer::PreviousClicked"
    NextClicked = "BiBrowserContainer::NextClicked"
    UpClicked = "BiBrowserContainer::UpClicked"
    RefreshClicked = "BiBrowserContainer::RefreshClicked"
    BookmarkClicked = "BiBrowserContainer::BookmarkClicked"
    FilesInfoLoaded = "BiBrowserContainer::FilesInfoLoaded"
    ItemDoubleClicked = "BiBrowserContainer::ItemDoubleClicked"
    ItemClicked = "BiBrowserContainer::ItemClicked"
    OpenJson = "BiBrowserContainer::OpenJson"
    BookmarksLoaded = "BiBrowserContainer::BookmarksLoaded"
    BookmarksModified = "BiBrowserContainer::BookmarksModified"
    NewExperimentClicked = "BiBrowserContainer::NewExperimentClicked"

    def __init__(self):
        super(BiBrowserContainer, self).__init__()
        self._object_name = 'BiBrowserContainer'
        self.currentPath = ''
        self.files = list()
        self.doubleClickedRow = -1
        self.clickedRow = -1
        self.historyPaths = list()
        self.posHistory = 0
        self.bookmarks = BiBrowserBookmarks()

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


class BiBrowserFileInfo(BiObject):     
    def __init__(self, fileName: str = '', path: str = '', name: str = '', dtype: str = '', date: str = ''):
        super(BiBrowserFileInfo, self).__init__()
        self.fileName = fileName
        self.path = path # without file name 
        self.name = name
        self.type = dtype
        self.date = date

    def filePath(self) -> str:
        return os.path.join(self.path, self.fileName)    


class BiBrowserModel(BiModel):
    def __init__(self, container: BiBrowserContainer, useExperimentProcess: bool = False):
        super(BiBrowserModel, self).__init__()
        self._object_name = 'BiBrowserModel'
        self._useExperimentProcess = useExperimentProcess
        self.container = container
        self.container.addObserver(self)
        self.files = list

    def update(self, container: BiContainer):
        if container.action == BiBrowserContainer.DirectoryModified or container.action == BiBrowserContainer.RefreshClicked:
            self.loadFiles()
            return
    
        if container.action == BiBrowserContainer.ItemDoubleClicked:
            row = self.container.doubleClickedRow
            dcFile = self.container.files[row]
            if dcFile.type == "dir":
                self.container.setCurrentPath(os.path.join(dcFile.path,dcFile.fileName))
                self.container.notify(BiBrowserContainer.DirectoryModified)
            elif dcFile.type == "experiment":
                if self._useExperimentProcess:
                    pass
                    ## TODO: Open the experiment as exernal process
                    #QProcess *openProcess = new QProcess(this)
                    #connect(openProcess, SIGNAL(errorOccurred(QProcess::ProcessError)), this, SLOT(errorOccurred(QProcess::ProcessError)))
                    #QString program = biSettingsAccess::instance().settings().value("Browser", "experiment editor")
                    #program += " " + dcFile.path() + QDir::separator() + dcFile.fileName()
                    #openProcess.startDetached(program)
            else:
                self.container.notify(BiBrowserContainer.OpenJson)

        if container.action == BiBrowserContainer.PreviousClicked:
            self.container.moveToPrevious()
            self.container.notify(BiBrowserContainer.DirectoryModified)
            return

        if container.action == BiBrowserContainer.NextClicked:
            self.container.moveToNext()
            self.container.notify(BiBrowserContainer.DirectoryModified)
            return

        if container.action == BiBrowserContainer.UpClicked:
            dir = QDir(self.container.currentPath)
            dir.cdUp()
            upPath = dir.absolutePath()
            self.container.setCurrentPath(upPath)
            self.container.notify(BiBrowserContainer.DirectoryModified)
            return

        if container.action == BiBrowserContainer.BookmarkClicked:
            dir = QDir(self.container.currentPath)
            self.container.bookmarks.set(dir.dirName(), self.container.currentPath)
            print('bookmarks:', self.container.bookmarks.bookmarks)
            self.container.bookmarks.write()
            self.container.notify(BiBrowserContainer.BookmarksModified)
            return

    def loadFiles(self):
        dir = QDir(self.container.currentPath)
        files = dir.entryInfoList()
        self.files = []

        for i in range(len(files)):
            if files[i].fileName() != "." and files[i].fileName() != "..":
                if files[i].isDir():
                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                           files[i].path(),
                                           files[i].fileName(),
                                           "dir",
                                           files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)

                elif files[i].fileName().endswith("experiment.md.json"):
                    experiment = BiExperiment(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            experiment.name(),
                                            "experiment",
                                            experiment.createddate())
                    self.files.append(fileInfo)
                    del experiment
        
                elif files[i].fileName().endswith("run.md.json"):
                    run = BiRun(files[i].absoluteFilePath())
    
                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            run.process_name(),
                                            "run",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del run
                
                elif files[i].fileName().endswith("rawdataset.md.json"):
                    rawDataSet = BiRawDataSet(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            rawDataSet.name(),
                                            "rawdataset",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del rawDataSet
        
                elif files[i].fileName().endswith("processeddataset.md.json"):
                    processedDataSet = BiProcessedDataSet(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            processedDataSet.name(),
                                            "processeddataset",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del processedDataSet
        
                elif files[i].fileName().endswith(".md.json"):
                    data = BiData(files[i].absoluteFilePath())
                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            data.name(),
                                            data.origin_type() + "data",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del data

        self.container.files = self.files
        self.container.notify(BiBrowserContainer.FilesInfoLoaded)


    def loadBookmarks(self, file: str):
        self.container.bookmarks = BiBrowserBookmarks(file)


class BiBrowserPreviewComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super(BiBrowserPreviewComponent, self).__init__()
        self._object_name = 'BiBrowserPreviewComponent'
        self.container = container
        self.container.addObserver(self)

        self.buildWidget()

    def buildWidget(self):

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        self.textEdit = QTextEdit(self.widget)
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit, 0, 0, 1, 2)

        self.name = QLabel(self.widget)
        layout.addWidget(QLabel(self.widget.tr("Name:")), 1, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.name, 1, 1, PySide2.QtCore.Qt.AlignTop)

        self.type = QLabel(self.widget)
        layout.addWidget(QLabel(self.widget.tr("Type:")), 2, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.type, 2, 1, PySide2.QtCore.Qt.AlignTop)

        self.date = QLabel(self.widget)
        layout.addWidget(QLabel(self.widget.tr("Date:")), 3, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.date, 3, 1, PySide2.QtCore.Qt.AlignTop)

        openButton = QPushButton(self.widget.tr("Open"), self.widget)
        openButton.setObjectName("btnDefault")
        layout.addWidget(openButton, 4, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        openButton.released.connect(self.openButtonClicked)

        layout.addWidget(QWidget(self.widget), 5, 0, 1, 2)

    def update(self, container: BiContainer):

        if container.action == BiBrowserContainer.ItemClicked:
        
            fileInfo = self.container.clickedFileInfo()

            if fileInfo.type == "dir":
                self.widget.setVisible(False)
            else:
                self.textEdit.setText(self.fileContentPreview(fileInfo.filePath()))
                self.widget.setVisible(True)

            self.name.setText(fileInfo.name)
            self.type.setText(fileInfo.type)
            self.date.setText(fileInfo.date)
    
    def fileContentPreview(self, filename: str) -> str:
        with open(filename, 'r') as file:
            data = file.read()
        return data

    def openButtonClicked(self):
        self.container.doubleClickedRow = self.container.clickedRow
        self.container.notify(BiBrowserContainer.ItemDoubleClicked)

    def get_widget(self): 
        return self.widget     


class BiBrowserShortCutsComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super(BiBrowserShortCutsComponent, self).__init__()
        self._object_name = 'BiBrowserPreviewComponent'
        self.container = container
        self.container.addObserver(self)

        self.widget = QWidget()
        
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(mainLayout)

        self.wwidget = QWidget()
        mainLayout.addWidget(self.wwidget)
        self.wwidget.setObjectName("BiBrowserShortCutsBar")

        layout = QVBoxLayout()
        self.wwidget.setLayout(layout)

        addExpermentbutton = QPushButton(self.wwidget.tr("New Experiment"))
        addExpermentbutton.setObjectName("BiBrowserShortCutsNewButton")
        addExpermentbutton.released.connect(self.newExperimentClicked)
        layout.addWidget(addExpermentbutton, 0, PySide2.QtCore.Qt.AlignTop)

        separatorLabel = QLabel(self.wwidget.tr("Bookmarks"), self.wwidget)
        layout.addWidget(separatorLabel, 0, PySide2.QtCore.Qt.AlignTop)
        separatorLabel.setObjectName("BiBrowserShortCutsTitle")

        bookmarkWidget = QWidget(self.wwidget)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        bookmarkWidget.setLayout(self.layout)

        layout.addWidget(bookmarkWidget, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop) 

    def reloadBookmarks(self):

        # free layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()

        # load
        for entry in self.container.bookmarks.bookmarks["bookmarks"]:
            button = BiButton(entry['name'], self.widget)
            button.setObjectName("BiBrowserShortCutsButton")
            button.content = entry['url']
            button.setCursor(PySide2.QtCore.Qt.PointingHandCursor)
            button.clickedContent.connect(self.buttonClicked)
            self.layout.insertWidget(self.layout.count()-1, button, 0, PySide2.QtCore.Qt.AlignTop)

    def update(self, container: BiContainer):
        if container.action == BiBrowserContainer.BookmarksModified:
            self.reloadBookmarks()


    def newExperimentClicked(self):
        self.container.notify(BiBrowserContainer.NewExperimentClicked)

    def buttonClicked(self, path: str):
        self.container.setCurrentPath(path)
        self.container.notify(BiBrowserContainer.DirectoryModified)

    def get_widget(self): 
        return self.widget     

class BiBrowserTableComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super(BiBrowserTableComponent, self).__init__()
        self._object_name = 'BiBrowserTableComponent'
        self.container = container
        self.container.addObserver(self)
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

    def update(self, container : BiContainer):
        if container.action == BiBrowserContainer.FilesInfoLoaded:
            i = -1
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
        self.container.notify(BiBrowserContainer.ItemDoubleClicked)

    def cellClicked(self, row : int, col : int):
        self.container.clickedRow = row
        self.container.notify(BiBrowserContainer.ItemClicked)

    def get_widget(self): 
        return self.widget     

class BiBrowserToolBarComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super(BiBrowserToolBarComponent, self).__init__()
        self._object_name = 'BiBrowserToolBarComponent'
        self.container = container
        self.container.addObserver(self)

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
        upButton.setToolTip(self.widget.tr("Tags"))
        upButton.released.connect(self.upButtonClicked)
        layout.addWidget(upButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # up
        refreshButton = QToolButton()
        refreshButton.setObjectName("BiExperimentToolBarRefreshButton")
        refreshButton.setToolTip(self.widget.tr("Tags"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # data selector
        self.pathLineEdit = QLineEdit(self.widget)
        self.pathLineEdit.returnPressed.connect(self.pathEditReturnPressed)
        layout.addWidget(self.pathLineEdit, 1)

        # bookmark
        bookmarkButton = QToolButton()
        bookmarkButton.setObjectName("BiExperimentToolBarBookmarkButton")
        bookmarkButton.setToolTip(self.widget.tr("Bookmark"))
        bookmarkButton.released.connect(self.bookmarkButtonClicked)
        layout.addWidget(bookmarkButton, 0, PySide2.QtCore.Qt.AlignLeft)

    def update(self, container: BiContainer):
        if container.action == BiBrowserContainer.FilesInfoLoaded:
            self.pathLineEdit.setText(self.container.currentPath)

    def previousButtonClicked(self):
        self.container.notify(BiBrowserContainer.PreviousClicked)

    def nextButtonClicked(self):
        self.container.notify(BiBrowserContainer.NextClicked)

    def upButtonClicked(self):
        self.container.notify(BiBrowserContainer.UpClicked)

    def pathEditReturnPressed(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.notify(BiBrowserContainer.DirectoryModified)

    def refreshButtonClicked(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.notify(BiBrowserContainer.RefreshClicked)

    def bookmarkButtonClicked(self):
        msgBox = QMessageBox()
        msgBox.setText("Want to bookmark this directory ?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        ret = msgBox.exec_()
        if ret:
            self.container.notify(BiBrowserContainer.BookmarkClicked)

    def get_widget(self): 
        return self.widget        
