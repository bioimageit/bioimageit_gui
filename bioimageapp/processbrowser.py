import sys
import os
import PySide2.QtCore
from PySide2.QtCore import QFileInfo, QDir
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView

from framework import BiContainer, BiModel, BiComponent
from widgets import BiButton
from bioimagepy.process import BiProcessInfo, BiProcessParser


class BiProcessesContainer(BiContainer):
    DirChanged = "BiProcessesContainer::DirChanged"
    ProcessesLoaded = "BiProcessesContainer::ProcessesLoaded"
    OpenProcess = "BiProcessesContainer::OpenProcess"

    def __init__(self):
        super(BiProcessesContainer, self).__init__()
        self._object_name = 'BiExperimentContainer'
        self.processesDir = ''
        self.processes = []
        self.clickedId = -1

    def clickedProcess(self):
        return self.processes[self.clickedId]

    def processAdd(self, info: BiProcessInfo):
        self.processes.append(info)

    def processesCount(self):
        return len(self.processes)


class BiProcessesModel(BiModel):
    def __init__(self, container: BiProcessesContainer):
        super(BiProcessesModel, self).__init__()
        self._object_name = 'BiProcessesModel'
        self.container = container
        self.container.addObserver(self)  

    def update(self, container: BiContainer):
        if container.action == BiProcessesContainer.DirChanged:
            if self.load():
                self.container.notify(BiProcessesContainer.ProcessesLoaded)
    
    def load(self) -> bool:
        processesDirInfo = QFileInfo(self.container.processesDir)

        if processesDirInfo.exists() and processesDirInfo.isDir():
            dir = QDir(self.container.processesDir)
            files = dir.entryList()
            for file in files:
                if file.endswith(".xml"):
                    self.loadFile(self.container.processesDir + QDir.separator() + file)

            return True
        else:
            print("WARGNING: biProcessesModel::load: the processed dir ", self.container.processesDir, " does not exists")
            return False

    def loadFile(self, file: str):
        parser = BiProcessParser(file)
        self.container.processAdd(parser.parse())


class BiProcessesToolBarComponent(BiComponent):
    def __init__(self, container: BiProcessesContainer):
        super(BiProcessesToolBarComponent, self).__init__()
        self._object_name = 'BiProcessesToolBarComponent'
        self.container = container
        self.container.addObserver(self)  

        self.widget = QWidget()

    def update(self, container: BiContainer):
        pass

    def get_widget(self):
        return self.widget


class BiProcessesComponent(BiComponent):
    def __init__(self, container: BiProcessesContainer):
        super(BiProcessesComponent, self).__init__()
        self._object_name = 'BiProcessesComponent'
        self.container = container
        self.container.addObserver(self)  

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(4)

        labels = ["Open", "Name", "Version", "Description"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.tableWidget)

    def update(self, container: BiContainer):
        if container.action == BiProcessesContainer.ProcessesLoaded:

            self.tableWidget.setRowCount(0)
            self.tableWidget.setRowCount(container.processesCount())

            i= -1    
            for info in self.container.processes:
                i += 1
                open = BiButton(self.widget.tr("Open"))
                open.id = i
                open.setObjectName("btnPrimary")
                open.clicked.connect(self.openClicked)
                self.tableWidget.setCellWidget(i, 0, open)

                self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(info.version))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(info.description))
        
    def openClicked(self, id: int):
        self.container.setClickedProcess(id)
        self.container.notify(BiProcessesContainer.OpenProcess)

    def get_widget(self):
        return self.widget    
