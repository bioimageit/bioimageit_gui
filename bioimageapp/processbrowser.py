import sys
import os
import json
import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import QFileInfo, QDir, Signal
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QHBoxLayout, QToolButton)

from framework import BiContainer, BiModel, BiComponent
from widgets import BiButton, BiFlowLayout, BiNavigationBar
from bioimagepy.process import BiProcessInfo, BiProcessParser


class BiProcessesBrowserContainer(BiContainer):
    ProcessesDirChanged = "BiProcessesContainer::ProcessedDirChanged"
    ProcessesLoaded = "BiProcessesContainer::ProcessesLoaded"
    PathChanged = "BiProcessesContainer::PathChanged"
    OpenProcess = "BiProcessesContainer::OpenProcess"

    def __init__(self):
        super().__init__()
        self._object_name = 'BiExperimentContainer'
        self.processesDir = ''
        self.processes = []
        self.categories = None
        self.historyPaths = ["root"]
        self.historyPathsNames = ["Home"]
        self.currentPath = "root"
        self.currentPathName = "Home"
        self.posHistory = 0
        self.clickedProcess = -1

    def set_path(self, path: str, name: str):
        self.currentPath = path
        self.currentPathName = name
        if self.posHistory <= len(self.historyPaths):
            for i in range(len(self.historyPaths), self.posHistory):
                self.historyPaths.pop(i)
                self.historyPathsNames.pop(i)
        self.historyPaths.append(path)
        self.historyPathsNames.append(name)
        self.posHistory = len(self.historyPaths) - 1 

    def moveToPrevious(self):
        self.posHistory -= 1
        if self.posHistory < 0 :
            self.posHistory = 0
        self.currentPath = self.historyPaths[self.posHistory]
        self.currentPathName = self.historyPathsNames[self.posHistory]

    def moveToNext(self):
        self.posHistory += 1
        if self.posHistory >= len(self.historyPaths):
            self.posHistory = len(self.historyPaths) - 1
        self.currentPath = self.historyPaths[self.posHistory] 
        self.currentPathName = self.historyPathsNames[self.posHistory] 

    def moveToHome(self):
        self.set_path("root", "Home")  

    def get_clickedProcess(self):
        for process in self.processes:
            if process.id == self.clickedProcess:
                return process
        return None           


class BiProcessesBrowserModel(BiModel):
    def __init__(self, container: BiProcessesBrowserContainer):
        super().__init__()
        self._object_name = 'BiProcessesBrowserContainer'
        self.container = container
        self.container.addObserver(self)  

    def update(self, container: BiContainer):
        if container.action == BiProcessesBrowserContainer.ProcessesDirChanged:
            if self.load():
                self.container.notify(BiProcessesBrowserContainer.ProcessesLoaded)
    
    def load(self) -> bool:
        if not self.loadProcesses():
            return False
        if not self.loadCategories():
            return False    
        return True   

    def loadCategories(self):
        categories_file = os.path.join(self.container.processesDir, "categories.json")
        if os.path.getsize(categories_file) > 0:
            with open(categories_file) as json_file:  
                self.container.categories = json.load(json_file) 
                return True
        else:
            return False             

    def loadProcesses(self) -> bool:
        processesDirInfo = QFileInfo(self.container.processesDir)

        if processesDirInfo.exists() and processesDirInfo.isDir():
            dir = QDir(self.container.processesDir)
            files = dir.entryList()
            for file in files:
                if file.endswith(".xml"):
                    parser = BiProcessParser(self.container.processesDir + QDir.separator() + file)
                    self.container.processes.append(parser.parse())
            return True
        else:
            print("WARNING: biProcessesModel::load: the processed dir ", self.container.processesDir, " does not exists")
            return False
        

class BiProcessesBrowserToolBarComponent(BiComponent):
    def __init__(self, container: BiProcessesBrowserContainer):
        super().__init__()
        self._object_name = 'BiProcessesBrowserToolBarComponent'
        self.container = container
        self.container.addObserver(self)  

        self.widget = QWidget()

    def update(self, container: BiContainer):
        pass

    def get_widget(self):
        return self.widget


class BiProcessesBrowserComponent(BiComponent):
    def __init__(self, container: BiProcessesBrowserContainer):
        super().__init__()
        self._object_name = 'BiProcessesComponent'
        self.container = container
        self.container.addObserver(self)  
        self.historyPaths = []
        self.posHistory = 0
        self.currentPath = ''

        # Widget
        self.widget = QWidget()
        #self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)
        
        # NavBar
        self.navBar = BiNavigationBar()
        self.navBar.previousSignal.connect(self.moveToPrevious)
        self.navBar.nextSignal.connect(self.moveToNext)
        self.navBar.homeSignal.connect(self.moveToHome)
        layout.addWidget(self.navBar)

        # Browse area
        browseWidget = QWidget()
        browseWidget.setObjectName("BiWidget")
        self.scrollWidget = QScrollArea()
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setWidget(browseWidget)
        layout.addWidget(self.scrollWidget)
        
        self.layout = BiFlowLayout()
        browseWidget.setLayout(self.layout)

        # tools table
        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(4)

        labels = ["Open", "Name", "Version", "Description"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tableWidget)
        self.tableWidget.setVisible(False)


    def moveToPrevious(self):
        self.container.moveToPrevious()
        self.container.notify(BiProcessesBrowserContainer.PathChanged)

    def moveToNext(self):
        self.container.moveToNext()
        self.container.notify(BiProcessesBrowserContainer.PathChanged)

    def moveToHome(self):
        self.container.moveToHome()  
        self.container.notify(BiProcessesBrowserContainer.PathChanged)      

    def browse(self, categories: dict, processesDir: str, parent: str):
        if self.hasChildCategory(parent):
            self.browseCategories(categories, processesDir, parent)
            self.tableWidget.setVisible(False)
            self.scrollWidget.setVisible(True)
        else:
            self.browseTools(categories, processesDir, parent)  
            self.tableWidget.setVisible(True)
            self.scrollWidget.setVisible(False)  

    def hasChildCategory(self, parent: str):
        for category in self.container.categories["categories"]:
            if category["parent"] == parent: 
                return True
        return False      

    def browseTools(self, categories: dict, processesDir: str, parent: str):
        self.tableWidget.setRowCount(0)
        #self.tableWidget.setRowCount(len(self.container.processes))

        i= -1    
        for info in self.container.processes:
            if parent in info.categories:    
                i += 1
                open = BiButton(self.widget.tr("Open"))
                #open.id = i
                open.content = info.id
                open.setObjectName("btnPrimary")
                open.clickedContent.connect(self.openClicked)

                self.tableWidget.insertRow( self.tableWidget.rowCount() )
                self.tableWidget.setCellWidget(i, 0, open)

                description = info.description.replace('\n','')
                description = description.replace('\t','')      

                self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(info.version))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(description))     

    def browseCategories(self, categories: dict, processesDir: str, parent: str):

        # free layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()

        # browse
        for category in categories:
            if category["parent"] == parent:    
                widget = BiProcessCategoryTile(category, processesDir, self.widget)
                widget.clickedSignal.connect(self.clickedTile)
                self.layout.addWidget(widget)

    def clickedTile(self, info: dict):
        self.container.set_path(info["id"], info["name"])
        self.container.notify(BiProcessesBrowserContainer.PathChanged)  

    def openClicked(self, id: str):
        self.container.clickedProcess = id
        self.container.notify(BiProcessesBrowserContainer.OpenProcess)              

    def update(self, container: BiContainer):
        if (container.action == BiProcessesBrowserContainer.ProcessesLoaded or
            container.action == BiProcessesBrowserContainer.PathChanged ):
            self.navBar.set_path(self.container.currentPathName)
            self.browse(self.container.categories["categories"], self.container.processesDir, self.container.currentPath)
            return

    def get_widget(self):
        return self.widget        


class BiProcessCategoryTile(QWidget):
    clickedSignal = Signal(dict)

    def __init__(self, info: dict, processesDir: str, parent: QWidget = None):
        super().__init__(parent)
        self.info = info

        self.setCursor(PySide2.QtGui.QCursor(PySide2.QtCore.Qt.PointingHandCursor))

        glayout = QVBoxLayout()
        widget = QWidget()
        glayout.addWidget(widget)
        self.setLayout(glayout)

        widget.setObjectName("BiProcessCategoryTile")
        layout = QVBoxLayout()
        widget.setLayout(layout)

        titleLabel = QLabel()
        titleLabel.setObjectName("BiProcessCategoryTileTitle")
        titleLabel.setText(info["name"])
        layout.addWidget(titleLabel, 0, PySide2.QtCore.Qt.AlignTop)

        thumbnailLabel = QLabel()
        img = QImage(os.path.join(processesDir, info["thumbnail"]))
        thumbnailLabel.setPixmap(QPixmap.fromImage(img.scaled(200, 200, PySide2.QtCore.Qt.KeepAspectRatio)))
        layout.addWidget(thumbnailLabel, 0, PySide2.QtCore.Qt.AlignTop | PySide2.QtCore.Qt.AlignHCenter)

        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop)

    def mousePressEvent(self, event):
        self.clickedSignal.emit(self.info)
