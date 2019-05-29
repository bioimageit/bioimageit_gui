import sys
import os
import PySide2.QtCore
from PySide2.QtWidget import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableWidget, QImage, QPixmap, QTableWidgetItem
from shutil import copyfile
import subprocess

from framework import BiComponent, BiContainer, BiModel
from widgets import BiDragLabel
from settings import BiSettingsAccess

from bioimagepy.experiment import BiExperiment 
from bioimagepy.metadata import BiRawData


class BiExperimentContainer(BiContainer):
    OriginModified = "BiExperimentContainer::OriginModified"
    Loaded = "BiExperimentContainer::Loaded"
    InfoClicked = "BiExperimentContainer::InfoClicked"
    ImportClicked = "BiExperimentContainer::ImportClicked"
    TagsClicked = "BiExperimentContainer::TagsClicked"
    InfoModified = "BiExperimentContainer::InfoModified"
    RawDataImported = "BiExperimentContainer::RawDataImported"
    TagsModified = "BiExperimentContainer::TagsModified"
    RawDataLoaded = "BiExperimentContainer::RawDataLoaded"
    DataAttributEdited = "BiExperimentContainer::DataAttributEdited"

    def __init__(self):
        super(BiExperimentContainer, self).__init__()
        self._object_name = 'BiExperimentContainer'
        self.projectFile = ''
        self.experiment = BiExperiment('')
        self.lastEditedDataIdx = 0

    def projectRootDir(self):
        return os.path.dirname(self.projectFile)

    def setTagValue(self, dataIdx: int, tag: str, value: str):
        self.dataProject.rawDataSet().dataAt(dataIdx).setTag(tag, value)

    def setDataName(self, dataIdx: int, name: str):
        self.dataProject.rawDataSet().dataAt(dataIdx).setName(name)
   
class BiExperimentImportDataContainer(BiContainer):
    NewImport = "BiExperimentImportDataContainer::NewImport"
    DataImported = "BiExperimentImportDataContainer::DataImported"

    def __init__(self):
        super(BiExperimentImportDataContainer, self).__init__()
        self._object_name = 'BiExperimentImportDataContainer'
        self.originFile = ''
        self.destinationFile = ''
        self.data = BiRawData('') 


class BiExperimentModel(BiModel):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentModel, self).__init__()
        self._object_name = 'BiExperimentModel'
        self.container = container
        self.container.addObserver(self)  

    def update(self, container: BiContainer):
        if container.action == BiExperimentContainer.OriginModified:
            experiment = BiExperiment(self.container.projectFile)
            self.container.experiment = experiment
            self.container.notify(BiExperimentContainer.Loaded)
            return

        if container.action == BiExperimentContainer.InfoModified or container.action == BiExperimentContainer.TagsModified:
            self.container.experiment.write()
            return
        
        if container.action == BiExperimentContainer.RawDataImported:
            self.container.experiment.rawDataSet().write()    
            self.containerexperiment.rawDataSet().lastData().write()
            self.container.notify(BiExperimentContainer.RawDataLoaded)
            return

        if container.action == BiExperimentContainer.DataAttributEdited:
            lastEditedIndex = self.container.lastEditedIdx
            rawData = self.containerexperiment.rawDataSet().dataAt(lastEditedIndex)
            rawData.write()
            return

class BiExperimentImportDataModel(BiModel):
    def __init__(self, container: BiExperimentImportDataContainer):
        super(BiExperimentImportDataModel, self).__init__()
        self._object_name = 'BiExperimentImportDataModel'
        self.container = container
        self.container.addObserver(self)  

    def update(self, container: BiContainer):
        if container.action == BiExperimentImportDataContainer.NewImport:
            self.importData()
            self.container.notify(BiExperimentImportDataContainer.DataImported)
            return

    def importData(self):
        self.createMetaDataFile()
        self.copyInputFile()
        self.createThumb()

    def createMetaDataFile(self):
        self.container.data.write()

    def copyInputFile(self):
        copyfile(self.container.originFile, self.container.destinationFile)

    def createThumb(self):
        destinationPath = self.container.destinationFile

        settingsGroups = BiSettingsAccess().instance
        program = settingsGroups.value("Project", "fiji") # "/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx";
        arguments = [program, "--headless", "--console", "-macro", settingsGroups.value("Project", "thumbnail macro"), destinationPath]

        print("create thumb:")
        print("program: ", program)
        print("arguments: ", arguments)
        subprocess.run(arguments)

class BiExperimentComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentComponent, self).__init__()
        self._object_name = 'BiExperimentComponent'
        self.container = container
        self.container.addObserver(self)

        self.buildWidget()

    def buildWidget(self):
        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout
        self.widget.setLayout(layout)

        self.dataComponent = BiExperimentDataComponent(self.container)
        layout.addWidget(self.dataComponent.get_widget())    

    def update(self, container: BiContainer):
        pass    

class BiExperimentDataComponent(BiComponent):        
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentDataComponent, self).__init__()
        self._object_name = 'BiExperimentDataComponent'
        self.container = container
        self.container.addObserver(self)

        self.buildWidget()

    def buildWidget(self):   
        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(5,0,5,5)
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.cellChanged.connect(self.cellChanged)

        labels = ["", "Name", "Author", "Date"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.tableWidget) 

    def update(self, container: BiContainer):
        if container.action == BiExperimentContainer.Loaded or container.action == BiExperimentContainer.TagsModified or container.action == BiExperimentContainer.RawDataLoaded:

            # headers
            self.tableWidget.setColumnCount(4 + self.containerexperiment.tagsCount())
            labels = ["", "Name"]
            for tag in self.containerexperiment.tags:
                labels.append(tag)
            labels.append("Author")
            labels.append("Date")
            self.tableWidget.setHorizontalHeaderLabels(labels)

            # data
            self.tableWidget.cellChanged.disconnect(self.cellChanged)
            self.tableWidget.setRowCount(0)
            self.tableWidget.setRowCount(self.containerexperiment.rawDataSet().count())

            self.tableWidget.setColumnWidth(0, 64)
            for i in range(self.container.experiment.rawDataSet().count()):
               
                info = self.containerexperiment.rawDataSet().dataAt(i)

                # thumbnail
                metaLabel = BiDragLabel(self.widget)

                metaLabel.setMimeData(info.url())
                thumbnail = info.thumbnail()
                if thumbnail != "":
                    image = QImage(thumbnail)
                    metaLabel.setPixmap(QPixmap.fromImage(image))
                    self.tableWidget.setRowHeight(i, 64)
                else:
                    metaLabel.setObjectName("BiExperimentDataComponentLabel")
                    self.tableWidget.setRowHeight(i, 64)

                self.tableWidget.setCellWidget(i, 0, metaLabel)

                # name
                self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name()))

                # tags
                for t in range(self.container.info().tagsCount()):
                    self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tagValue(self.containerexperiment.tagAt(t))))

                for t in range(self.container.info().tagsCount()):
                    self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tagValue(self.container.experiment.tagAt(t))))

                # author
                itemAuthor = QTableWidgetItem(info.author())
                itemAuthor.setFlags(PySide2.QtCore.Qt.ItemIsEditable)
                self.tableWidget.setItem(i, 2 + self.container.experiment.tagsCount(), itemAuthor)

                # created date
                itemCreatedDate = QTableWidgetItem(info.createddate())
                itemCreatedDate.setFlags(PySide2.QtCore.Qt.ItemIsEditable)
                self.tableWidget.setItem(i, 3 + self.container.experiment.tagsCount(), itemCreatedDate)
            
            self.tableWidget.cellChanged.connect(self.cellChanged)
        
    def cellChanged(self, row: int, col: int):
        if col == 1:
            self.container.setLastEditedDataIdx(row)
            self.container.setDataName(row, self.tableWidget.item(row, col).text())
            self.container.notify(BiExperimentContainer.DataAttributEdited)
        elif  col > 1 and col < 4 + self.container.experiment.tagsCount() :
            self.container.setLastEditedDataIdx(row)
            self.container.setTagValue(row, self.container.experiment.tagAt(col-2), self.tableWidget.item(row, col).text())
            self.container.notify(BiExperimentContainer.DataAttributEdited)
        