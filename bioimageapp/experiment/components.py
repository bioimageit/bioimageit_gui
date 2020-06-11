import ntpath

import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import QFileInfo, QDir, Signal
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QGridLayout, QHBoxLayout, QToolButton, QSplitter, 
                               QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                               QFileDialog, QTabWidget, QSpinBox, QCheckBox, 
                               QComboBox, QProgressBar)

from bioimageapp.core.framework import BiComponent, BiAction
from bioimageapp.core.widgets import BiTagWidget, BiButton
from bioimageapp.experiment.states import BiExperimentStates, BiExperimentCreateStates
from bioimageapp.experiment.containers import BiExperimentContainer, BiExperimentCreateContainer  
from bioimageapp.experiment.models import BiExperimentModel

from bioimageapp.metadata.states import BiRawDataStates, BiMetadataExperimentStates
from bioimageapp.metadata.containers import BiRawDataContainer, BiMetadataExperimentContainer
from bioimageapp.metadata.components import BiRawDataComponent, BiMetadataExperimentComponent
from bioimageapp.metadata.models import BiRawDataModel, BiMetadataExperimentModel

class BiExperimentComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiBrowserExperimentToolbar'
        # containers
        self.container = container
        self.container.register(self)
        self.rawDataContainer = BiRawDataContainer()
        self.rawDataContainer.register(self)
        self.experimentContainer = BiMetadataExperimentContainer()
        self.experimentContainer.register(self)

        # models
        self.experimentModel = BiExperimentModel(self.container)
        self.rawDataModel = BiRawDataModel(self.rawDataContainer)
        self.metadataExperimentModel = BiMetadataExperimentModel(self.experimentContainer)

        # components
        self.toolbarComponent = BiExperimentToolbarComponent(self.container)
        self.datasetListComponent = BiExperimentDataSetListComponent(self.container)
        self.datasetViewComponent = BiExperimentDataSetViewComponent(self.container)
        self.rawDataComponent = BiRawDataComponent(self.rawDataContainer)
        self.metadataExperimentComponent = BiMetadataExperimentComponent(self.experimentContainer)

        # widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)
        splitter = QSplitter()

        self.rawDataComponent.get_widget().setVisible(False)    

        layout.addWidget(self.toolbarComponent.get_widget())
        layout.addWidget(splitter)
        splitter.addWidget(self.datasetListComponent.get_widget())
        splitter.addWidget(self.datasetViewComponent.get_widget())
        splitter.addWidget(self.rawDataComponent.get_widget())

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            self.datasetListComponent.datasetClicked('data')
            self.experimentContainer.experiment = self.container.experiment
            self.experimentContainer.emit(BiMetadataExperimentStates.Loaded)
            return

        if action.state == BiExperimentStates.RawDataClicked:
            self.rawDataContainer.md_uri = self.container.current_dataset.get(self.container.clickedRow).md_uri
            self.rawDataContainer.emit(BiRawDataStates.URIChanged)
            self.rawDataComponent.get_widget().setVisible(True)
            return

        if action.state == BiRawDataStates.Saved:
            self.datasetListComponent.datasetClicked('data')
            return

        if action.state == BiExperimentStates.EditInfoClicked:
            self.metadataExperimentComponent.get_widget().setVisible(True)    
            return

        if action.state == BiMetadataExperimentStates.Saved:
            self.metadataExperimentComponent.get_widget().setVisible(False)   
            self.toolbarComponent.updateTitle() 
            return


    def get_widget(self): 
        return self.widget


class BiExperimentToolbarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiBrowserExperimentToolbar'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName('BiToolBar')
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)

        layout = QHBoxLayout()
        layout.setSpacing(1)
        self.widget.setLayout(layout)

        # info
        infoButton = QToolButton()
        infoButton.setObjectName("BiBrowserExperimentToolbarInfoButton")
        infoButton.setToolTip(self.widget.tr("Import data"))
        infoButton.released.connect(self.infoButtonClicked)
        layout.addWidget(infoButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # import
        importButton = QToolButton()
        importButton.setObjectName("BiBrowserExperimentToolbarImportButton")
        importButton.setToolTip(self.widget.tr("Import data"))
        importButton.released.connect(self.importButtonClicked)
        layout.addWidget(importButton, 0, PySide2.QtCore.Qt.AlignLeft)
        
        # tags
        tagButton = QToolButton()
        tagButton.setObjectName("BiBrowserExperimentToolbarTagButton")
        tagButton.setToolTip(self.widget.tr("Tag data"))
        tagButton.released.connect(self.tagButtonClicked)
        layout.addWidget(tagButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # process
        processButton = QToolButton()
        processButton.setObjectName("BiBrowserExperimentToolbarProcessButton")
        processButton.setToolTip(self.widget.tr("Process data"))
        processButton.released.connect(self.processButtonClicked)
        layout.addWidget(processButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # experiment name
        self.nameLabel = QLabel()
        self.nameLabel.setObjectName('BiLabel')
        self.nameLabel.setAlignment(PySide2.QtCore.Qt.AlignRight | PySide2.QtCore.Qt.AlignVCenter)
        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignRight)
        layout.addWidget(self.nameLabel, 0, PySide2.QtCore.Qt.AlignRight)

    def updateTitle(self):
        self.nameLabel.setText(self.container.experiment.metadata.name)

    def infoButtonClicked(self):
        self.container.emit(BiExperimentStates.EditInfoClicked)

    def importButtonClicked(self):
        self.container.emit(BiExperimentStates.ImportClicked)

    def tagButtonClicked(self):
        self.container.emit(BiExperimentStates.TagClicked)    

    def processButtonClicked(self):
        self.container.emit(BiExperimentStates.ProcessClicked)  

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            self.nameLabel.setText(self.container.experiment.metadata.name)     

    def get_widget(self): 
        return self.widget


class BiExperimentDataSetListComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentDataSetListComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName('BiLeftBar')
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)

        self.buttons = []

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        rawLabel = QLabel('Raw dataset')
        rawLabel.setObjectName("BiBrowserShortCutsTitle")
        rawLabel.setMaximumHeight(50)

        ProcessedLabel = QLabel('Processed dataset')
        ProcessedLabel.setObjectName("BiBrowserShortCutsTitle")
        ProcessedLabel.setMaximumHeight(50)
        

        dataButton = BiButton('data')
        dataButton.content = 'data'
        dataButton.setObjectName('BiBrowserShortCutsButton')
        dataButton.setCheckable(True)
        dataButton.setChecked(True)
        dataButton.clickedContent.connect(self.datasetClicked)
        self.buttons.append(dataButton)

        layout.addWidget(rawLabel, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(dataButton, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(ProcessedLabel, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop)

    def datasetClicked(self, name: str):
        for button in self.buttons:
            if button.content != name:
                button.setChecked(True)
   
        self.container.current_dataset_name = name
        self.container.emit(BiExperimentStates.DataSetClicked)

    def update(self, action: BiAction):
        pass    

    def updateList(self):
        pass

    def get_widget(self): 
        return self.widget 

class BiExperimentDataSetViewComponent(BiComponent):
    def __init__(self, container: BiExperimentCreateContainer, default_destination: str = ""):
        super().__init__()
        self._object_name = 'BiExperimentDataSetComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(3,3,3,3)
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)

        labels = ["", "Name", "Author", "Date"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.tableWidget.cellClicked.connect(self.cellClicked)

        layout.addWidget(self.tableWidget) 

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.DataSetLoaded:
            if self.container.current_dataset_name == "data":
                self.drawRawDataset()
            else:
                self.drawProcessedDataSet()        
                 
    def drawRawDataset(self):

        # headers
        tags = self.container.experiment.metadata.tags
        self.tableWidget.setColumnCount(4 + len(tags))
        labels = ["Name"]
        for tag in tags:
            labels.append(tag)
        labels.append("Format")
        labels.append("Author")
        labels.append("Date")
        self.tableWidget.setHorizontalHeaderLabels(labels)

        exp_size = self.container.current_dataset.size()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(exp_size)
        if exp_size < 10:
            self.tableWidget.verticalHeader().setFixedWidth(20)
        elif exp_size >= 10 and exp_size < 100  :
            self.tableWidget.verticalHeader().setFixedWidth(40)  
        elif exp_size >= 100 and exp_size < 1000  :    
            self.tableWidget.verticalHeader().setFixedWidth(60) 

        data_list = self.container.current_dataset.get_data_list()
        
        for i in range(len(data_list)):
            raw_metadata = data_list[i].metadata

            # name
            col_idx  = 0
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.name))
            # tags
            for tag in tags:
                col_idx += 1
                if tag in raw_metadata.tags:
                    self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.tags[tag])) 
            # format
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.format))                
            # author
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.author))
            # created date
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.date))

    def cellClicked(self, row : int, col : int):
        self.container.clickedRow = row
        self.container.emit(BiExperimentStates.RawDataClicked)
        self.highlightLine(row)

    def highlightLine(self, row: int):
        for col in range(self.tableWidget.columnCount()):
            if self.tableWidget.item(row, col):
                self.tableWidget.item(row, col).setSelected(True) 

    def drawProcessedDataSet(self):
        pass             

    def get_widget(self): 
        return self.widget    


class BiExperimentCreateComponent(BiComponent):
    def __init__(self, container: BiExperimentCreateContainer, default_destination: str = ""):
        super().__init__()
        self._object_name = 'BiExperimentCreateComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Create experiment"))
        title.setObjectName("BiLabelFormHeader1")
        title.setMaximumHeight(50)

        destinationLabel = QLabel(self.widget.tr("Destination"))
        destinationLabel.setObjectName("BiLabel")
        self.destinationEdit = QLineEdit()
        self.destinationEdit.setText(default_destination)
        browseButton = QPushButton(self.widget.tr("..."))
        browseButton.setObjectName("BiBrowseButton")
        browseButton.released.connect(self.browseButtonClicked)

        nameLabel = QLabel(self.widget.tr("Experiment name"))
        nameLabel.setObjectName("BiLabel")
        self.nameEdit = QLineEdit()

        authorLabel = QLabel(self.widget.tr("Author"))
        authorLabel.setObjectName("BiLabel")
        self.authorEdit = QLineEdit()

        createButton = QPushButton(self.widget.tr("Create"))
        createButton.setObjectName("btnPrimary")
        createButton.released.connect(self.createButtonClicked)

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(destinationLabel, 1, 0)
        layout.addWidget(self.destinationEdit, 1, 1)
        layout.addWidget(browseButton, 1, 2)
        layout.addWidget(nameLabel, 2, 0)
        layout.addWidget(self.nameEdit, 2, 1, 1, 2)
        layout.addWidget(authorLabel, 3, 0)
        layout.addWidget(self.authorEdit, 3, 1, 1, 2)
        layout.addWidget(createButton, 4, 2, 1, 1, PySide2.QtCore.Qt.AlignRight)
        layout.addWidget(QWidget(), 5, 0, 1, 1, PySide2.QtCore.Qt.AlignTop)

    def browseButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.widget, self.widget.tr("Select Directory"),
                                       "",
                                       QFileDialog.ShowDirsOnly
                                       | QFileDialog.DontResolveSymlinks)
        self.destinationEdit.setText(directory)

    def createButtonClicked(self):
        self.container.experiment_destination_dir = self.destinationEdit.text()
        self.container.experiment_name = self.nameEdit.text()
        self.container.experiment_author = self.authorEdit.text()
        self.container.emit(BiExperimentCreateStates.CreateClicked)

    def reset(self):
        self.destinationEdit.setText('')
        self.nameEdit.setText('')
        self.authorEdit.setText('')    

    def setDestination(self, path: str):
        self.destinationEdit.setText(path)

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget

class BiExperimentImportComponent(BiComponent):        
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentImportComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)

        importSingleComponent = BiExperimentImportSingleDataComponent(container)
        tabWidget.addTab(importSingleComponent.get_widget(), self.widget.tr("Single Data"))

        importDirectoryComponent = BiExperimentImportDirectoryDataComponent(container)
        tabWidget.addTab(importDirectoryComponent.get_widget(), self.widget.tr("Multiple Data"))

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget


class BiExperimentImportSingleDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentImportSingleDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportSingleDataComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Import single data"))
        title.setObjectName("BiLabelFormHeader1")

        dataLabel = QLabel(self.widget.tr("Data"))
        dataLabel.setObjectName("BiWidget")
        self.dataPath = QLineEdit()
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("BiBrowseButton")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        copyDataLabel = QLabel(self.widget.tr("Copy data"))
        copyDataLabel.setObjectName("BiWidget")
        self.copyDataBox = QCheckBox()
        self.copyDataBox.setChecked(True)

        nameLabel = QLabel(self.widget.tr("Name"))
        nameLabel.setObjectName("BiWidget")
        self.nameEdit = QLineEdit()

        formatLabel = QLabel(self.widget.tr("Format"))
        formatLabel.setObjectName("BiWidget")
        self.formatEdit = QLineEdit()

        authorLabel = QLabel(self.widget.tr("Author"))
        authorLabel.setObjectName("BiWidget")
        self.authorEdit = QLineEdit()

        createddateLabel = QLabel(self.widget.tr("Created date"))
        createddateLabel.setObjectName("BiWidget")
        self.createddateEdit = QLineEdit()

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btnPrimary")
        importButton.released.connect(self.importButtonClicked)

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(dataLabel, 1, 0)
        layout.addWidget(self.dataPath, 1, 1)
        layout.addWidget(browseDataButton, 1, 2)
        layout.addWidget(copyDataLabel, 2, 0)
        layout.addWidget(self.copyDataBox, 2, 1, 1, 2)
        layout.addWidget(nameLabel, 3, 0)
        layout.addWidget(self.nameEdit, 3, 1, 1, 2)
        layout.addWidget(formatLabel, 4, 0)
        layout.addWidget(self.formatEdit, 4, 1, 1, 2)
        layout.addWidget(authorLabel, 5, 0)
        layout.addWidget(self.authorEdit, 5, 1, 1, 2)
        layout.addWidget(createddateLabel, 6, 0)
        layout.addWidget(self.createddateEdit, 6, 1, 1, 2)
        layout.addWidget(importButton, 7, 2, PySide2.QtCore.Qt.AlignRight)

    def update(self, action: BiAction):
        pass

    def importButtonClicked(self):

        self.container.import_info.file_data_path = self.dataPath.text()
        self.container.import_info.file_copy_data = self.copyDataBox.isChecked()
        self.container.import_info.file_name = self.nameEdit.text()
        self.container.import_info.fotmat = self.formatEdit.text()
        self.container.import_info.author = self.authorEdit.text()
        self.container.import_info.createddate = self.createddateEdit.text()
        self.container.emit(BiExperimentStates.NewImportFile)

    def browseDataButtonClicked(self):
        fileName = QFileDialog.getOpenFileName(self.widget, self.widget.tr("Import file"), 'Data (*.*)')
        self.dataPath.setText(fileName[0])

    def get_widget(self):
        return self.widget  


class BiExperimentImportDirectoryDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentImportDirectoryDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportDirectoryDataComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Import from folder"))
        title.setObjectName("BiLabelFormHeader1")

        dataLabel = QLabel(self.widget.tr("Folder"))
        dataLabel.setObjectName("BiWidget")
        self.dataPath = QLineEdit()
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("BiBrowseButton")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        recursiveLabel = QLabel(self.widget.tr("Recursive"))
        recursiveLabel.setObjectName("BiWidget")
        self.recursiveBox = QCheckBox()
        self.recursiveBox.setChecked(True)

        filterLabel = QLabel(self.widget.tr("Filter"))
        filterLabel.setObjectName("BiWidget")
        self.filterComboBox = QComboBox()
        self.filterComboBox.addItem(self.widget.tr('Ends With'))
        self.filterComboBox.addItem(self.widget.tr('Start With'))
        self.filterComboBox.addItem(self.widget.tr('Contains'))
        self.filterEdit = QLineEdit()
        self.filterEdit.setText('.tif')

        copyDataLabel = QLabel(self.widget.tr("Copy data"))
        copyDataLabel.setObjectName("BiWidget")
        self.copyDataBox = QCheckBox()
        self.copyDataBox.setChecked(True)

        formatLabel = QLabel(self.widget.tr("Format"))
        formatLabel.setObjectName("BiWidget")
        self.formatEdit = QLineEdit()

        authorLabel = QLabel(self.widget.tr("Author"))
        authorLabel.setObjectName("BiWidget")
        self.authorEdit = QLineEdit()

        createddateLabel = QLabel(self.widget.tr("Created date"))
        createddateLabel.setObjectName("BiWidget")
        self.createddateEdit = QLineEdit()

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btnPrimary")
        importButton.released.connect(self.importButtonClicked)

        layout.addWidget(title, 0, 0, 1, 4)
        layout.addWidget(dataLabel, 1, 0)
        layout.addWidget(self.dataPath, 1, 1, 1, 2)
        layout.addWidget(browseDataButton, 1, 3)
        layout.addWidget(recursiveLabel, 2, 0)
        layout.addWidget(self.recursiveBox, 2, 1, 1, 2)
        layout.addWidget(filterLabel, 3, 0)
        layout.addWidget(self.filterComboBox, 3, 1, 1, 1)
        layout.addWidget(self.filterEdit, 3, 2, 1, 2)
        layout.addWidget(copyDataLabel, 4, 0)
        layout.addWidget(self.copyDataBox, 4, 1, 1, 2)
        layout.addWidget(formatLabel, 5, 0)
        layout.addWidget(self.formatEdit, 5, 1, 1, 2)
        layout.addWidget(authorLabel, 6, 0)
        layout.addWidget(self.authorEdit, 6, 1, 1, 2)
        layout.addWidget(createddateLabel, 7, 0)
        layout.addWidget(self.createddateEdit, 7, 1, 1, 2)
        layout.addWidget(importButton, 8, 3, PySide2.QtCore.Qt.AlignRight)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar, 8, 1, 1, 3)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Progress:
            if 'progress' in self.container.progress:
                self.progressBar.setVisible(True)
                self.progressBar.setValue(self.container.progress)
                if self.container.progress == 100:
                    self.progressBar.setVisible(False)
                 

    def importButtonClicked(self):

        self.container.import_info.dir_data_path = self.dataPath.text()
        self.container.import_info.dir_recursive = self.recursiveBox.isChecked()
        self.container.import_info.dir_filter = self.filterComboBox.currentIndex()
        self.container.import_info.dir_filter_value = self.filterEdit.text()
        self.container.import_info.dir_copy_data = self.copyDataBox.isChecked()
        self.container.import_info.author = self.authorEdit.text()
        self.container.import_info.format = self.formatEdit.text()
        self.container.import_info.createddate = self.createddateEdit.text()
        self.container.emit(BiExperimentStates.NewImportDir)

    def browseDataButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.widget, self.widget.tr("Select Directory"),
                                       "",
                                       QFileDialog.ShowDirsOnly
                                       | QFileDialog.DontResolveSymlinks)
        self.dataPath.setText(directory)

    def get_widget(self):
        return self.widget  

class BiExperimentTagComponent(BiComponent):        
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)

        tagsListComponent = BiExperimentTagsListComponent(self.container)
        tagUsingSeparatorComponent = BiExperimentTagsUsingSeparatorsComponent(self.container)
        tagUsingNameComponent = BiExperimentTagsUsingNameComponent(self.container)

        tabWidget.addTab(tagsListComponent.get_widget(), self.widget.tr("Tags"))
        tabWidget.addTab(tagUsingSeparatorComponent.get_widget(), self.widget.tr("Tag using separator"))
        tabWidget.addTab(tagUsingNameComponent.get_widget(), self.widget.tr("Tag using name"))

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget    


class BiExperimentTagsListComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagsListComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
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

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            self.reload()
            return

    def reload(self):
        # free layout
        for i in reversed(range(self.tagListLayout.count())): 
            self.tagListLayout.itemAt(i).widget().deleteLater()

        # add tags
        for tag in self.container.experiment.metadata.tags:
            tagWidget = BiTagWidget() 
            tagWidget.setContent(tag)
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
        tags = []
        for i in range(self.tagListLayout.count()):
            item = self.tagListLayout.itemAt(i)
            widget = item.widget()
            if widget:
                tags.append(widget.content())
        self.container.tag_info.tags = tags        
        self.container.emit(BiExperimentStates.TagsModified)

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


class BiExperimentTagsUsingSeparatorsComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagsUsingSeparatorsComponent'
        self.container = container
        self.container.register(self)  
        self._tagsEdit = []
        self._separatorEdit = []
        self._positionSpinBox = []

        self.widget = QWidget()
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Tag using separator"))
        title.setObjectName("BiLabelFormHeader1")

        gridWidget = QWidget()
        self.gridLayout = QGridLayout()
        gridWidget.setLayout(self.gridLayout)

        tagLabel = QLabel(self.widget.tr("Tag"))
        tagLabel.setObjectName("BiWidget")
        separatorLabel = QLabel(self.widget.tr("Separator"))
        separatorLabel.setObjectName("BiWidget")
        positionLabel = QLabel(self.widget.tr("Position"))
        positionLabel.setObjectName("BiWidget")

        tagsEdit = QLineEdit()
        self._tagsEdit.append(tagsEdit)
        separatorEdit = QLineEdit()
        self._separatorEdit.append(separatorEdit)
        positionSpinBox = QSpinBox()
        self._positionSpinBox.append(positionSpinBox)

        addLineButton = QPushButton(self.widget.tr("Add line"))
        addLineButton.setObjectName('btnDefault')
        addLineButton.released.connect(self.addLine)

        validateButton = QPushButton(self.widget.tr("Validate"))
        validateButton.setObjectName('btnPrimary')
        validateButton.released.connect(self.validated)

        layout.addWidget(title, 0, 0, 1, 3)
        
        self.gridLayout.addWidget(tagLabel, 0, 0)
        self.gridLayout.addWidget(separatorLabel, 0, 1)
        self.gridLayout.addWidget(positionLabel, 0, 2)

        self.gridLayout.addWidget(tagsEdit, 1, 0)
        self.gridLayout.addWidget(separatorEdit, 1, 1)
        self.gridLayout.addWidget(positionSpinBox, 1, 2)

        layout.addWidget(gridWidget, 1, 0, 1, 3)
        layout.addWidget(addLineButton, 2, 0)
        layout.addWidget(validateButton, 3, 2)

    def validated(self):
        tags = []
        separator = []
        position = []
        for tag in self._tagsEdit:
            tags.append(tag.text())    
        for sep in self._separatorEdit:
            separator.append(sep.text())
        for pos in self._positionSpinBox:
            position.append(pos.value())    

        self.container.tag_info.usingseparator_tags = tags
        self.container.tag_info.usingseparator_separator = separator
        self.container.tag_info.usingseparator_position = position
        self.container.emit(BiExperimentStates.TagUsingSeparators)

    def addLine(self):
        tagsEdit = QLineEdit()
        self._tagsEdit.append(tagsEdit)
        separatorEdit = QLineEdit()
        self._separatorEdit.append(separatorEdit)
        positionSpinBox = QSpinBox()
        self._positionSpinBox.append(positionSpinBox)

        rowIdx = self.gridLayout.count()
        self.gridLayout.addWidget(tagsEdit, rowIdx, 0)
        self.gridLayout.addWidget(separatorEdit, rowIdx, 1)
        self.gridLayout.addWidget(positionSpinBox, rowIdx, 2)

    def update(self, action: BiAction):
        pass    

    def get_widget(self):
        return self.widget  


class BiExperimentTagsUsingNameComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagsUsingNameComponent'
        self.container = container
        self.container.register(self)  

        self._namesEdit = []

        self.widget = QWidget()
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Tag using name"))
        title.setObjectName("BiLabelFormHeader1")

        tagLabel = QLabel(self.widget.tr("Tag:"))
        tagLabel.setObjectName("BiWidget")
        self.tagEdit = QLineEdit()

        searchLabel = QLabel(self.widget.tr("Search names:"))
        searchLabel.setObjectName("BiWidget")
        searchWidget = QWidget()
        self.searchLayout = QVBoxLayout()
        self.searchLayout.setContentsMargins(0,0,0,0)
        searchWidget.setLayout(self.searchLayout)

        nameEdit = QLineEdit()
        self._namesEdit.append(nameEdit)
        self.searchLayout.addWidget(nameEdit)

        addLineButton = QPushButton(self.widget.tr("Add name"))
        addLineButton.setObjectName('btnDefault')
        addLineButton.released.connect(self.addLine)

        validateButton = QPushButton(self.widget.tr("Validate"))
        validateButton.setObjectName('btnPrimary')
        validateButton.released.connect(self.validated)

        layout.addWidget(title, 0, 0)
        layout.addWidget(tagLabel, 1, 0, 1, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.tagEdit, 1, 1)
        layout.addWidget(searchLabel, 2, 0, 1, 1, PySide2.QtCore.Qt.AlignTop )
        layout.addWidget(searchWidget, 2, 1)
        layout.addWidget(addLineButton, 3, 1)
        layout.addWidget(validateButton, 4, 2)

    def validated(self):
        names = []
        for name in self._namesEdit:
            names.append(name.text())
        self.container.tag_info.usingname_tag = self.tagEdit.text()
        self.container.tag_info.usingname_search = names
        self.container.emit(BiExperimentStates.TagUsingName)

    def addLine(self):
        nameEdit = QLineEdit()
        self._namesEdit.append(nameEdit)
        self.searchLayout.addWidget(nameEdit)

    def update(self, action: BiAction):
        pass    

    def get_widget(self):
        return self.widget                        