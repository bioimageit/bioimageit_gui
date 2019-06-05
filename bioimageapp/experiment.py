import sys
import os
import ntpath
import PySide2.QtCore
from PySide2.QtCore import QFileInfo, QDir
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                               QGridLayout, QScrollArea, QToolButton, QComboBox,
                               QFileDialog)
from shutil import copyfile
import subprocess

from framework import BiComponent, BiContainer, BiModel
from widgets import BiDragLabel, BiTagWidget
from settings import BiSettingsAccess

from bioimagepy.experiment import BiExperiment 
from bioimagepy.metadata import BiRawData
from  bioimagepy.metadata import create_rawdata


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
        self.experiment = None
        self.lastEditedDataIdx = 0

    def projectRootDir(self):
        return os.path.dirname(self.projectFile)

    def setTagValue(self, dataIdx: int, tag: str, value: str):
        self.experiment.rawdataset().data(dataIdx).set_tag(tag, value)

    def setDataName(self, dataIdx: int, name: str):
        self.experiment.rawdataset().data(dataIdx).set_name(name)

    def setLastEditedDataIdx(self, idx):
        self.lastEditedDataIdx = idx    
   
class BiExperimentImportDataContainer(BiContainer):
    NewImport = "BiExperimentImportDataContainer::NewImport"
    DataImported = "BiExperimentImportDataContainer::DataImported"

    def __init__(self):
        super(BiExperimentImportDataContainer, self).__init__()
        self._object_name = 'BiExperimentImportDataContainer'
        self.originFile = ''
        self.destinationFile = ''
        self.data = None


class BiExperimentModel(BiModel):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentModel, self).__init__()
        self._object_name = 'BiExperimentModel'
        self.container = container
        self.container.addObserver(self)  

    def update(self, container: BiContainer):
        if container.action == BiExperimentContainer.OriginModified:
            print('change origin to :',  self.container.projectFile)
            self.container.experiment = BiExperiment(self.container.projectFile)
            self.container.notify(BiExperimentContainer.Loaded)
            return

        if container.action == BiExperimentContainer.InfoModified or container.action == BiExperimentContainer.TagsModified:
            self.container.experiment.write()
            return
        
        if container.action == BiExperimentContainer.RawDataImported:
            self.container.experiment.rawdataset().write()    
            self.container.experiment.rawdataset().last_data().write()
            self.container.notify(BiExperimentContainer.RawDataLoaded)
            return

        if container.action == BiExperimentContainer.DataAttributEdited:
            lastEditedIndex = self.container.lastEditedDataIdx
            rawData = self.container.experiment.rawdataset().data(lastEditedIndex)
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
        program = settingsGroups.value("Experiment", "fiji") # "/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx"
        arguments = [program, "--headless", "--console", "-macro", settingsGroups.value("Experiment", "thumbnail macro"), destinationPath]

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

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        self.dataComponent = BiExperimentDataComponent(self.container)
        layout.addWidget(self.dataComponent.get_widget())    

    def update(self, container: BiContainer):
        pass    

    def get_widget(self):
        return self.widget      

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
            self.tableWidget.setColumnCount(4 + self.container.experiment.tags_size())
            labels = ["", "Name"]
            for tag in self.container.experiment.tags():
                labels.append(tag)
            labels.append("Author")
            labels.append("Date")
            self.tableWidget.setHorizontalHeaderLabels(labels)

            # data
            self.tableWidget.cellChanged.disconnect(self.cellChanged)
            self.tableWidget.setRowCount(0)
            self.tableWidget.setRowCount(self.container.experiment.rawdataset().size())

            self.tableWidget.setColumnWidth(0, 64)
            for i in range(self.container.experiment.rawdataset().size()):
               
                info = self.container.experiment.rawdataset().data(i)

                # thumbnail
                metaLabel = BiDragLabel(self.widget)

                metaLabel.setMimeData(info.url())
                thumbnail = info.thumbnail()
                if thumbnail != "":
                    print('set thumbnail: ', thumbnail)
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
                for t in range(self.container.experiment.tags_size()):
                    self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tag(self.container.experiment.tag(t))))

                for t in range(self.container.experiment.tags_size()):
                    self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tag(self.container.experiment.tag(t))))

                # author
                itemAuthor = QTableWidgetItem(info.author())
                itemAuthor.setFlags(PySide2.QtCore.Qt.ItemIsEditable)
                self.tableWidget.setItem(i, 2 + self.container.experiment.tags_size(), itemAuthor)

                # created date
                itemCreatedDate = QTableWidgetItem(info.createddate())
                itemCreatedDate.setFlags(PySide2.QtCore.Qt.ItemIsEditable)
                self.tableWidget.setItem(i, 3 + self.container.experiment.tags_size(), itemCreatedDate)
            
            self.tableWidget.cellChanged.connect(self.cellChanged)
        
    def cellChanged(self, row: int, col: int):
        if col == 1:
            self.container.setLastEditedDataIdx(row)
            self.container.setDataName(row, self.tableWidget.item(row, col).text())
            self.container.notify(BiExperimentContainer.DataAttributEdited)
        elif  col > 1 and col < 4 + self.container.experiment.tags_size() :
            self.container.setLastEditedDataIdx(row)
            self.container.setTagValue(row, self.container.experiment.tag(col-2), self.tableWidget.item(row, col).text())
            self.container.notify(BiExperimentContainer.DataAttributEdited)

    def get_widget(self):
        return self.widget  

class BiExperimentInfoEditorComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentInfoEditorComponent, self).__init__()
        self._object_name = 'BiExperimentDataComponent'
        self.container = container
        self.container.addObserver(self)   

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Informations"))
        title.setObjectName("BiLabelFormHeader1")

        self.nameEdit = QLineEdit()
        self.authorEdit = QLineEdit()
        self.createdEdit = QLineEdit()

        nameLabel = QLabel(self.widget.tr("Project Name:"))
        authorLabel = QLabel(self.widget.tr("User:"))
        createdLabel = QLabel(self.widget.tr("Created date:"))

        layout.addWidget(title, 0, 0, 1, 2)
        layout.addWidget(nameLabel, 1, 0)
        layout.addWidget(self.nameEdit, 1, 1)
        layout.addWidget(authorLabel, 2, 0)
        layout.addWidget(self.authorEdit, 2, 1)
        layout.addWidget(createdLabel, 3, 0)
        layout.addWidget(self.createdEdit, 3, 1)

        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        layout.addWidget(saveButton, 4, 1, PySide2.QtCore.Qt.AlignRight)
        saveButton.released.connect(self.saveClicked)

    def update(self, container: BiContainer):
        if container.action == BiExperimentContainer.Loaded:
            self.nameEdit.setText(self.container.experiment.name())
            self.authorEdit.setText(self.container.experiment.author())
            self.createdEdit.setText(self.container.experiment.createddate())

    def saveClicked(self):
        self.container.experiment.set_name(self.nameEdit.text())
        self.container.experiment.set_author(self.authorEdit.text())
        self.container.experiment.set_createddate(self.createdEdit.text())

        self.container.notify(BiExperimentContainer.InfoModified)

    def get_widget(self):
        return self.widget  

class BiExperimentTagsComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentTagsComponent, self).__init__()
        self._object_name = 'BiExperimentTagsComponent'
        self.container = container
        self.container.addObserver(self)   

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Tags"))
        title.setObjectName("BiLabelFormHeader1")

        # add widget
        addWidget = QWidget()
        addLayout = QHBoxLayout()
        addWidget.setLayout(addLayout)

        self.addEdit = QLineEdit(self.widget)
        addButton = QPushButton(self.widget.tr("Add"))
        addButton.setObjectName("btnDefault")
        addLayout.addWidget(self.addEdit)
        addLayout.addWidget(addButton)

        self.tagListWidget = QWidget()
        self.tagListWidget.setObjectName("BiWidget")
        self.tagListLayout = QVBoxLayout()
        self.tagListWidget.setLayout(self.tagListLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setObjectName("BiWidget")
        scrollArea.setWidget(self.tagListWidget)

        # button area
        buttonsWidget = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setContentsMargins(0,0,0,0)
        buttonsLayout.setSpacing(2)
        buttonsWidget.setLayout(buttonsLayout)
        cancelButton = QPushButton(self.widget.tr("Cancel"))
        cancelButton.setObjectName("btnDefault")
        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        buttonsLayout.addWidget(cancelButton, 1, PySide2.QtCore.Qt.AlignRight)
        buttonsLayout.addWidget(saveButton, 0, PySide2.QtCore.Qt.AlignRight)

        layout.addWidget(title)
        layout.addWidget(addWidget)
        layout.addWidget(scrollArea)
        layout.addWidget(buttonsWidget)

        addButton.released.connect(self.addButtonClicked)
        cancelButton.released.connect(self.cancelButtonClicked)
        saveButton.released.connect(self.saveButtonClicked)

    def update(self, container: BiContainer):
        if container.action == BiExperimentContainer.Loaded:
            self.reload()
            return

    def reload(self):
        # free layout
        for i in reversed(range(self.tagListLayout.count())): 
            self.tagListLayout.itemAt(i).widget().deleteLater()

        # add tags
        for t in range(self.container.experiment.tags_size()):
            tagWidget = BiTagWidget() 
            tagWidget.setContent(self.container.experiment.tag(t))
            tagWidget.remove.connect(self.removeClicked)
            self.tagListLayout.addWidget(tagWidget)
        self.tagListWidget.adjustSize()

    def addButtonClicked(self):
        if self.addEdit.text() != "":
            tagWidget = BiTagWidget()
            tagWidget.setContent(self.addEdit.text())
            tagWidget.remove.connect(self.removeClicked)
            self.tagListLayout.addWidget(tagWidget)
            self.addEdit.setText("")
            self.tagListLayout.update()

    def cancelButtonClicked(self):
        self.reload()

    def saveButtonClicked(self):
        self.container.experiment.clear_tags()
        for i in range(self.tagListLayout.count()):
            item = self.tagListLayout.itemAt(i)
            widget = item.widget()
            if widget:
                self.container.experiment.add_tag(widget.content())
        self.container.notify(BiExperimentContainer.TagsModified)

    def removeClicked(self, tag: str):
        for i in range(self.tagListLayout.count()):
            item = self.tagListLayout.itemAt( i )
            widget = item.widget()
            if widget:
                if widget.content() == tag:
                    itemd = self.tagListLayout.takeAt( i )
                    itemd.widget().deleteLater()
        self.tagListWidget.adjustSize()

    def get_widget(self):
        return self.widget      

class BiExperimentImportDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer, importContainer: BiExperimentImportDataContainer):
        super(BiExperimentImportDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportDataComponent'
        self.container = container
        self.container.addObserver(self)  
        self.importContainer = importContainer
        self.importContainer.addObserver(self) 

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Import data"))
        title.setObjectName("BiLabelFormHeader1")

        dataLabel = QLabel(self.widget.tr("Data"))
        self.dataPath = QLineEdit()
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("biBrowseButton")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        nameLabel = QLabel(self.widget.tr("Name"))
        self.nameEdit = QLineEdit()

        authorLabel = QLabel(self.widget.tr("Author"))
        self.authorEdit = QLineEdit()

        createddateLabel = QLabel(self.widget.tr("Created date"))
        self.createddateEdit = QLineEdit()

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btnPrimary")
        importButton.released.connect(self.importButtonClicked)

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(dataLabel, 1, 0)
        layout.addWidget(self.dataPath, 1, 1)
        layout.addWidget(browseDataButton, 1, 2)
        layout.addWidget(nameLabel, 2, 0)
        layout.addWidget(self.nameEdit, 2, 1, 1, 2)
        layout.addWidget(authorLabel, 3, 0)
        layout.addWidget(self.authorEdit, 3, 1, 1, 2)
        layout.addWidget(createddateLabel, 4, 0)
        layout.addWidget(self.createddateEdit, 4, 1, 1, 2)
        layout.addWidget(importButton, 5, 2, PySide2.QtCore.Qt.AlignRight)

    def update(self, container: BiContainer):
        pass

    def importButtonClicked(self):
        # origin/destination data file url
        originFile = self.dataPath.text()
        originFileInfo = QFileInfo(originFile)
        originfilename = originFileInfo.fileName()
        originBasename = originFileInfo.baseName()

        rawDataSetmdFileInfo = self.container.experiment.rawdataset().md_file_path()
        destinationFile = rawDataSetmdFileInfo + QDir.separator() + originfilename

        # meta data
        data_md_file = rawDataSetmdFileInfo + QDir.separator() + originBasename + ".md.json"

        print('import data to:', data_md_file)

        data = create_rawdata(data_md_file) 
        data.set_url(ntpath.basename(destinationFile))
        data.set_name(self.nameEdit.text())
        data.set_author(self.authorEdit.text())
        data.set_createddate(self.createddateEdit.text())
        data.set_datatype("image")
        data.set_thumbnail(originBasename + "_thumb.jpg")
        
        self.container.experiment.rawdataset().add_data(data)
        self.container.notify(BiExperimentContainer.RawDataImported)

        self.importContainer.data = data
        self.importContainer.originFile = originFile
        self.importContainer.destinationFile = destinationFile
        self.importContainer.notify(BiExperimentImportDataContainer.NewImport)

    def browseDataButtonClicked(self):
        fileName = QFileDialog.getOpenFileName(self.widget, self.widget.tr("Import file"), 'Data (*.*)')
        print('filename: ', fileName[0])
        self.dataPath.setText(fileName[0])

    def get_widget(self):
        return self.widget   

class BiExperimentTitleToolBarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentTitleToolBarComponent, self).__init__()
        self._object_name = 'BiExperimentTitleToolBarComponent'
        self.container = container
        self.container.addObserver(self)  

        self.widget = QWidget()
        self.widget.setObjectName("BiToolBar")
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # title
        layout.addWidget(QWidget(), 1)
        self.titleLabel = QLabel("default Title")
        layout.addWidget(self.titleLabel, 0, PySide2.QtCore.Qt.AlignRight)
        self.titleLabel.setObjectName("BiExperimentTitleToolBarTitle")

    def update(self, container: BiContainer):
        if container.action == BiExperimentContainer.Loaded or container.action == BiExperimentContainer.InfoModified:
            self.titleLabel.setText(self.container.experiment.name())

    def get_widget(self):
        return self.widget          


class BiExperimentToolBarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentToolBarComponent, self).__init__()
        self._object_name = 'BiExperimentToolBarComponent'
        self.container = container
        self.container.addObserver(self)  

        self.widget = QWidget()
        self.widget.setObjectName("BiToolBar")
        layout = QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # info
        openInfoButton = QToolButton()
        openInfoButton.setObjectName("BiExperimentToolBarInfoButton")
        openInfoButton.setToolTip(self.widget.tr("Project informations"))
        openInfoButton.released.connect(self.infoButtonClicked)
        layout.addWidget(openInfoButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # import
        importButton = QToolButton()
        importButton.setObjectName("BiExperimentToolBarImportButton")
        importButton.setToolTip(self.widget.tr("Import data"))
        importButton.released.connect(self.importButtonClicked)
        layout.addWidget(importButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # Tags
        tagsButton = QToolButton()
        tagsButton.setObjectName("BiExperimentToolBarTagsButton")
        tagsButton.setToolTip(self.widget.tr("Tags"))
        tagsButton.released.connect(self.tagsButtonClicked)
        layout.addWidget(tagsButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # data selector
        dataCombo = QComboBox()
        dataCombo.addItem("Data")
        dataCombo.currentTextChanged.connect(self.dataComboChanged)
        layout.addWidget(dataCombo, 0, PySide2.QtCore.Qt.AlignLeft)

    def update(self, container: BiContainer):
        pass

    def infoButtonClicked(self):
        self.container.notify(BiExperimentContainer.InfoClicked)

    def dataComboChanged(self, text: str):
        pass

    def importButtonClicked(self):
        self.container.notify(BiExperimentContainer.ImportClicked)

    def tagsButtonClicked(self):    
        self.container.notify(BiExperimentContainer.TagsClicked)

    def get_widget(self):
        return self.widget      

