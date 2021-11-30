from pathlib import Path
from datetime import date

import qtpy.QtCore
from qtpy.QtGui import QPixmap, QImage, QPalette
from qtpy.QtCore import QFileInfo, QDir, Signal
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QGridLayout, QHBoxLayout, QToolButton, QSplitter, 
                               QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                               QFileDialog, QTabWidget, QSpinBox, QCheckBox, 
                               QComboBox, QProgressBar, QHeaderView)

from bioimageit_core.config import ConfigAccess
from bioimageit_core.dataset import ProcessedDataSet
from bioimageit_formats import FormatsAccess

from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.core.widgets import BiTagWidget, BiButton
from ._states import (BiExperimentStates, BiExperimentCreateStates)
from ._containers import (BiExperimentContainer,
                          BiExperimentCreateContainer
                         )
from ._models import BiExperimentModel

from bioimageit_gui.metadata.states import (BiRawDataStates,
                                            BiProcessedDataStates,
                                            BiRunStates,
                                            BiMetadataExperimentStates)
from bioimageit_gui.metadata.containers import (BiRawDataContainer,
                                                BiProcessedDataContainer,
                                                BiRunContainer,
                                                BiMetadataExperimentContainer)
from bioimageit_gui.metadata.components import (BiRawDataComponent,
                                                BiProcessedDataComponent,
                                                BiMetadataRunComponent,
                                                BiMetadataExperimentComponent)
from bioimageit_gui.metadata.models import (BiRawDataModel,
                                            BiProcessedDataModel,
                                            BiRunModel,
                                            BiMetadataExperimentModel)

from bioimageit_viewer.viewer import BiMultiViewer


class BiExperimentViewerComponent(BiComponent):
    def __init__(self, experiment_uri: str, viewer: BiMultiViewer):
        super().__init__()

        self.show_viewer = True    
        self.viewer = viewer
        self.viewer.setVisible(False)

        # instantiate the expeirment component
        self.experimentContainer = BiExperimentContainer()
        self.experimentContainer.experiment_uri = experiment_uri
        self.experimentContainer.register(self)
        self.experimentComponent = BiExperimentComponent(self.experimentContainer)
        self.experimentContainer.emit(BiExperimentStates.Load)

        # Widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        layout.addWidget(self.experimentComponent.get_widget())

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.ViewDataClicked:
            self.viewer.add_data(self.experimentContainer.selected_data_info.metadata.uri,
                                          self.experimentContainer.selected_data_info.metadata.name,
                                          self.experimentContainer.selected_data_info.metadata.format)
            self.viewer.setVisible(True)

    def get_widget(self):
        return self.widget


class BiExperimentComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentComponent'
        self.show_viewer = True

        # containers
        self.container = container
        self.container.register(self)
        self.rawDataContainer = BiRawDataContainer()
        self.rawDataContainer.register(self)
        self.processedDataContainer = BiProcessedDataContainer()
        self.processedDataContainer.register(self)
        self.runContainer = BiRunContainer()
        self.runContainer.register(self)
        self.metadataExperimentContainer = BiMetadataExperimentContainer()
        self.metadataExperimentContainer.register(self)

        # models
        self.experimentModel = BiExperimentModel(self.container)
        self.rawDataModel = BiRawDataModel(self.rawDataContainer)
        self.processedDataModel = BiProcessedDataModel(
            self.processedDataContainer)
        self.runModel = BiRunModel(self.runContainer)
        self.metadataExperimentModel = BiMetadataExperimentModel(
            self.metadataExperimentContainer)

        # components
        self.toolbarComponent = BiExperimentToolbarComponent(self.container)
        self.metaToolbarComponent = SgExperimentMetaToolbarComponent(self.container)
        self.datasetViewComponent = BiExperimentDataSetViewComponent(self.container)
        self.rawDataComponent = BiRawDataComponent(self.rawDataContainer)
        self.processedDataComponent = BiProcessedDataComponent(self.processedDataContainer)
        self.runComponent = BiMetadataRunComponent(self.runContainer)
        self.metadataExperimentComponent = BiMetadataExperimentComponent(self.metadataExperimentContainer)
        self.importComponent = BiExperimentImportComponent(self.container)
        self.tagComponent = BiExperimentTagComponent(self.container)

        # widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.widget.setLayout(layout)

        self.processedDataWidget = QWidget()
        processedDataLayout = QVBoxLayout()
        title1 = QLabel('Processed data metadata')
        title1.setObjectName('SgLabelFormHeader1')
        processedDataLayout.addWidget(title1)
        processedDataLayout.addWidget(self.processedDataComponent.get_widget())
        title2 = QLabel('Run information')
        title2.setObjectName('SgLabelFormHeader1')
        processedDataLayout.addWidget(title2)
        processedDataLayout.addWidget(self.runComponent.get_widget())
        self.processedDataWidget.setLayout(processedDataLayout)

        layout.addWidget(self.toolbarComponent.get_widget())
        layout.addWidget(self.metaToolbarComponent.get_widget())
        layout.addWidget(self.datasetViewComponent.get_widget())
        layout.addWidget(self.metadataExperimentComponent.get_widget())
        layout.addWidget(self.importComponent.get_widget())
        layout.addWidget(self.tagComponent.get_widget())
        layout.addWidget(self.rawDataComponent.get_widget())
        layout.addWidget(self.processedDataWidget)

        # widget init
        self.metaToolbarComponent.get_widget().setVisible(False)
        self.metadataExperimentComponent.get_widget().setVisible(False)
        self.importComponent.get_widget().setVisible(False)
        self.tagComponent.get_widget().setVisible(False)
        self.rawDataComponent.get_widget().setVisible(False)
        self.processedDataWidget.setVisible(False)


    def hideDataComponents(self):
        self.rawDataComponent.get_widget().setVisible(False)  
        self.processedDataComponent.get_widget().setVisible(False)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            self.metadataExperimentContainer.experiment = self.container.experiment
            self.metadataExperimentContainer.emit(BiMetadataExperimentStates.Loaded)
            return

        if action.state == BiExperimentStates.ViewRawMetaDataClicked:
            self.rawDataContainer.md_uri = self.container.current_dataset.get(self.container.clickedRow).md_uri
            self.rawDataContainer.emit(BiRawDataStates.URIChanged)

            self.toolbarComponent.get_widget().setVisible(False)
            self.metaToolbarComponent.get_widget().setVisible(True) 
            self.datasetViewComponent.get_widget().setVisible(False)  
            self.rawDataComponent.get_widget().setVisible(True)
            self.processedDataComponent.get_widget().setVisible(False)
            return

        if action.state == BiExperimentStates.ViewProcessedMetaDataClicked:
            self.processedDataContainer.md_uri = self.container.current_dataset.get(self.container.clickedRow).md_uri   
            self.processedDataContainer.emit(BiProcessedDataStates.URIChanged)

            self.toolbarComponent.get_widget().setVisible(False)
            self.metaToolbarComponent.get_widget().setVisible(True) 
            self.datasetViewComponent.get_widget().setVisible(False) 
            self.rawDataComponent.get_widget().setVisible(False)
            self.processedDataWidget.setVisible(True)
            return 

        if action.state == BiRawDataStates.Saved:
            self.toolbarComponent.get_widget().setVisible(True)
            self.metaToolbarComponent.get_widget().setVisible(False) 
            self.datasetViewComponent.get_widget().setVisible(True)  
            self.rawDataComponent.get_widget().setVisible(False)

            self.container.emit(BiExperimentStates.RefreshClicked)
            return

        if action.state == BiExperimentStates.EditInfoClicked:
            self.toolbarComponent.get_widget().setVisible(False)
            self.metaToolbarComponent.get_widget().setVisible(True)
            self.metadataExperimentComponent.get_widget().setVisible(True)  
            self.datasetViewComponent.get_widget().setVisible(False)  
            return

        if action.state == BiMetadataExperimentStates.Saved:
            self.toolbarComponent.get_widget().setVisible(True)
            self.metaToolbarComponent.get_widget().setVisible(False)
            self.metadataExperimentComponent.get_widget().setVisible(False)  
            self.datasetViewComponent.get_widget().setVisible(True)   
            self.toolbarComponent.updateTitle() 
            return

        if action.state == BiExperimentStates.ImportClicked:
            self.toolbarComponent.get_widget().setVisible(False)
            self.metaToolbarComponent.get_widget().setVisible(True)
            self.importComponent.get_widget().setVisible(True)  
            self.datasetViewComponent.get_widget().setVisible(False) 
            return

        if action.state == BiExperimentStates.DataImported:
            self.toolbarComponent.get_widget().setVisible(True)
            self.metaToolbarComponent.get_widget().setVisible(False)
            self.importComponent.get_widget().setVisible(False)  
            self.datasetViewComponent.get_widget().setVisible(True) 
            msgBox = QMessageBox()
            msgBox.setText("Data imported")
            msgBox.exec() 
            self.container.emit(BiExperimentStates.RefreshClicked)
            return

        if action.state == BiExperimentStates.TagClicked:
            self.toolbarComponent.get_widget().setVisible(False)
            self.metaToolbarComponent.get_widget().setVisible(True)
            self.tagComponent.get_widget().setVisible(True)  
            self.datasetViewComponent.get_widget().setVisible(False) 
            return

        if action.state == BiExperimentStates.TagsSaved or action.state == BiExperimentStates.DataTagged:
            self.toolbarComponent.get_widget().setVisible(True)
            self.metaToolbarComponent.get_widget().setVisible(False)
            self.tagComponent.get_widget().setVisible(False)  
            self.datasetViewComponent.get_widget().setVisible(True) 
            msgBox = QMessageBox()
            msgBox.setText("Tags saved")
            msgBox.exec() 
            self.container.emit(BiExperimentStates.RefreshClicked)
            return    

        if action.state == BiExperimentStates.DataSetClicked:
            self.hideDataComponents()     

        if action.state == BiProcessedDataStates.RunOpenClicked:
            self.runContainer.md_uri = self.processedDataContainer.processeddata.metadata.run_uri   
            self.runContainer.emit(BiRunStates.URIChanged) 

        if action.state == BiRunStates.Loaded:    
            self.runComponent.get_widget().setVisible(True)   

        if action.state == BiExperimentStates.DeleteRawClicked:
            print('catch delete rawdata:', self.container.selected_data_info.md_uri)
            msgbox = QMessageBox(QMessageBox.Question, "Confirm delete", f"Are you sure you want to delete: {self.container.selected_data_info.metadata.name}?")
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)

            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                self.rawDataContainer.md_uri = self.container.selected_data_info.md_uri
                self.rawDataContainer.emit(BiRawDataStates.DeleteRawData)

        if action.state == BiRawDataStates.RawDataDeleted:
            self.container.emit(BiExperimentStates.RefreshClicked)            

        if action.state == BiExperimentStates.MainPageClicked:
            self.metaToolbarComponent.get_widget().setVisible(False)
            self.tagComponent.get_widget().setVisible(False)
            self.importComponent.get_widget().setVisible(False)
            self.metadataExperimentComponent.get_widget().setVisible(False)
            self.rawDataComponent.get_widget().setVisible(False)
            self.processedDataWidget.setVisible(False)
            self.toolbarComponent.get_widget().setVisible(True)
            self.datasetViewComponent.get_widget().setVisible(True)     

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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QHBoxLayout()
        layout.setSpacing(1)
        self.widget.setLayout(layout)

        # info
        infoButton = QToolButton()
        infoButton.setObjectName("BiExperimentToolbarInfoButton")
        infoButton.setToolTip(self.widget.tr("Information"))
        infoButton.released.connect(self.infoButtonClicked)
        layout.addWidget(infoButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # import
        importButton = QToolButton()
        importButton.setObjectName("BiExperimentToolbarImportButton")
        importButton.setToolTip(self.widget.tr("Import data"))
        importButton.released.connect(self.importButtonClicked)
        layout.addWidget(importButton, 0, qtpy.QtCore.Qt.AlignLeft)
        
        # tags
        tagButton = QToolButton()
        tagButton.setObjectName("BiExperimentToolbarTagButton")
        tagButton.setToolTip(self.widget.tr("Tag data"))
        tagButton.released.connect(self.tagButtonClicked)
        layout.addWidget(tagButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # refresh
        refreshButton = QToolButton()
        refreshButton.setObjectName("BiExperimentToolbarRefreshButton")
        refreshButton.setToolTip(self.widget.tr("Refresh"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # datasets
        self.dataset_box = QComboBox()
        self.dataset_box.currentIndexChanged.connect(self.datasetBoxChanged)
        layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignRight)
        layout.addWidget(self.dataset_box, 0, qtpy.QtCore.Qt.AlignHCenter)

        # experiment name
        self.nameLabel = QLabel()
        self.nameLabel.setObjectName('BiLabel')
        self.nameLabel.setAlignment(qtpy.QtCore.Qt.AlignRight | qtpy.QtCore.Qt.AlignVCenter)
        layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignRight)
        layout.addWidget(self.nameLabel, 0, qtpy.QtCore.Qt.AlignRight)

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

    def refreshButtonClicked(self):
        self.container.emit(BiExperimentStates.RefreshClicked)  

    def datasetBoxChanged(self):
        self.container.current_dataset_name = self.dataset_box.currentText()
        self.container.emit(BiExperimentStates.DataSetClicked)

    def closeButtonClicked(self):
        self.container.emit(BiExperimentStates.CloseClicked)  

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            self.nameLabel.setText(self.container.experiment.metadata.name)  

            # update the list of datasets in the combobox
            current_text = self.dataset_box.currentText
            self.dataset_box.clear()
            self.dataset_box.addItem('data')
            self.dataset_box.currentIndexChanged.disconnect(
                self.datasetBoxChanged)
            for pdataset_uri in self.container.experiment.metadata.processeddatasets:
                pdataset = ProcessedDataSet(pdataset_uri)
                dataset_name = pdataset.metadata.name
                self.dataset_box.addItem(dataset_name)
                if dataset_name == current_text:
                    self.dataset_box.setCurrentText(dataset_name)
            self.dataset_box.currentIndexChanged.connect(
                self.datasetBoxChanged)              

    def get_widget(self): 
        return self.widget


class SgExperimentMetaToolbarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentMetaToolbarComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName('BiToolBar')
        layout = QHBoxLayout()
        self.widget.setLayout(layout)
        returnButton = QToolButton()
        returnButton.setObjectName('BiReturnToolButton')
        returnButton.released.connect(self.emitReturn)
        layout.addWidget(returnButton, 0, qtpy.QtCore.Qt.AlignLeft)

    def emitReturn(self):
        self.container.emit(BiExperimentStates.MainPageClicked)

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget


class BiExperimentDataSetListComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentDataSetListComponent'
        self.container = container
        self.container.register(self)

        self.widget = QScrollArea()
        self.widget.setObjectName('BiWidget')
        self.widget.setWidgetResizable(True)
        self.widget.setMinimumWidth(150)

        widget = QWidget()
        widget.setObjectName('BiSideBar')
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setWidget(widget)

        self.buttons = []

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

    def datasetClicked(self, name: str):   
        self.container.current_dataset_name = name
        self.container.emit(BiExperimentStates.DataSetClicked)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded or action.state == BiExperimentStates.RefreshClicked: 
            self.createDataSetsButton()
            
    def createDataSetsButton(self):
        # free layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()

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
        dataButton.setAutoExclusive(True)
        if self.container.current_dataset_name == 'data':
            dataButton.setChecked(True)
        dataButton.clickedContent.connect(self.datasetClicked)
        self.buttons.append(dataButton)

        self.layout.addWidget(rawLabel, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(dataButton, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(ProcessedLabel, 0, qtpy.QtCore.Qt.AlignTop)

        for pdataset_uri in self.container.experiment.metadata.processeddatasets:
            pdataset = ProcessedDataSet(pdataset_uri)
            datasetButton = BiButton(pdataset.metadata.name)
            datasetButton.content = pdataset.metadata.name
            datasetButton.setObjectName('BiBrowserShortCutsButton')
            datasetButton.setCheckable(True)
            datasetButton.setAutoExclusive(True)
            if self.container.current_dataset_name == pdataset.metadata.name:
                datasetButton.setChecked(True)
            datasetButton.clickedContent.connect(self.datasetClicked)
            self.layout.addWidget(datasetButton, 0, qtpy.QtCore.Qt.AlignTop)
            self.buttons.append(datasetButton)
        self.layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop)

    def updateList(self):
        pass

    def get_widget(self): 
        return self.widget 


class BiExperimentDataSetViewComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentDataSetViewComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(3,3,3,3)
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(4)

        labels = ["", "Name", "Author", "Date"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableWidget.verticalHeader().setDefaultSectionSize(24)
        self.tableWidget.setSizeAdjustPolicy(qtpy.QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.tableWidget.cellClicked.connect(self.cellClicked)

        layout.addWidget(self.tableWidget) 

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.DataSetLoaded:
            if self.container.current_dataset_name == "data":
                self.drawRawDataset()
            else:
                if self.container.current_dataset:
                    self.drawProcessedDataSet()        
                 
    def drawRawDataset(self):
        # headers
        tags = self.container.experiment.metadata.tags
        self.tableWidget.setColumnCount(7 + len(tags))
        labels = ["", "", "", "Name"]
        for tag in tags:
            labels.append(tag)
        labels.append("Format")
        labels.append("Author")
        labels.append("Date")
        self.tableWidget.setHorizontalHeaderLabels(labels)

        exp_size = self.container.current_dataset.size()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(exp_size)
        self.tableWidget.verticalHeader().setVisible(False)

        data_list = self.container.current_dataset.get_data_list()
        
        for i in range(len(data_list)):
            raw_metadata = data_list[i].metadata

            # view button
            col_idx = 0
            view_btn = BiButton("View")
            view_btn.id = i
            view_btn.setObjectName("btnTablePrimary")
            view_btn.clickedId.connect(self.viewDataClicked)
            self.tableWidget.setCellWidget(i, col_idx, view_btn)

            # metadata button
            col_idx += 1
            edit_btn = BiButton("Metadata")
            edit_btn.id = i
            edit_btn.setObjectName("btnTableDefault")
            edit_btn.clickedId.connect(self.viewMetaDataClicked)
            self.tableWidget.setCellWidget(i, col_idx, edit_btn)

            # delete button
            col_idx += 1
            del_btn = BiButton("X")
            del_btn.setMaximumWidth(20)
            del_btn.id = i
            del_btn.setObjectName("btnTableDefault")
            del_btn.clickedId.connect(self.deleteRawDataClicked)
            self.tableWidget.setCellWidget(i, col_idx, del_btn)

            # name
            col_idx +=1
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

        #self.tableWidget.resizeColumnsToContents()    

    def cellClicked(self, row : int, col : int):
        self.container.clickedRow = row
        self.highlightLine(row)

    def viewDataClicked(self, row: int):
        self.container.selected_data_info = self.container.current_dataset.get(row)
        print('emit view data:', self.container.selected_data_info.metadata.uri)
        self.container.emit(BiExperimentStates.ViewDataClicked)

    def viewMetaDataClicked(self, row: int):
        self.container.selected_data_info = self.container.current_dataset.get(row)
        self.container.clickedRow = row
        print('emit view metadata:', self.container.selected_data_info.metadata.uri)
        if self.container.current_dataset_name == 'data':
            self.container.emit(BiExperimentStates.ViewRawMetaDataClicked)
        else:
            self.container.emit(BiExperimentStates.ViewProcessedMetaDataClicked)

    def deleteRawDataClicked(self, row: int):
        self.container.selected_data_info = self.container.current_dataset.get(row)
        self.container.clickedRow = row
        print('emit delete rawdata:', self.container.selected_data_info.metadata.uri)
        if self.container.current_dataset_name == 'data':
            self.container.emit(BiExperimentStates.DeleteRawClicked)

    def highlightLine(self, row: int):
        for col in range(0, self.tableWidget.columnCount()):
            self.tableWidget.setCurrentCell(row, col, qtpy.QtCore.QItemSelectionModel.Select)  

    def drawProcessedDataSet(self):
        # headers
        tags = self.container.experiment.metadata.tags
        self.tableWidget.setColumnCount(6 + len(tags))
        labels = ["", "", "Name"]
        labels.append("Parent")
        labels.append("Label")
        for tag in tags:
            labels.append(tag)
        labels.append("Format")
        labels.append("Author")
        labels.append("Date")
        self.tableWidget.setHorizontalHeaderLabels(labels)

        exp_size = self.container.current_dataset.size()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(exp_size)

        data_list = self.container.current_dataset.get_data_list()
        
        for i in range(len(data_list)):
            raw_metadata = data_list[i].metadata
            parent_metadata = data_list[i].get_parent().metadata
            origin_metadata = None
            if data_list[i].get_origin():
                origin_metadata = data_list[i].get_origin().metadata

            # view button
            col_idx = 0
            view_btn = BiButton("View")
            view_btn.id = i
            view_btn.setObjectName("btnTablePrimary")
            view_btn.clickedId.connect(self.viewDataClicked)
            self.tableWidget.setCellWidget(i, col_idx, view_btn)

            # metadata button
            col_idx += 1
            edit_btn = BiButton("Metadata")
            edit_btn.id = i
            edit_btn.setObjectName("btnTableDefault")
            edit_btn.clickedId.connect(self.viewMetaDataClicked)
            self.tableWidget.setCellWidget(i, col_idx, edit_btn)

            # name
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.name))
            # origin
            col_idx  += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(parent_metadata.name))
            # label
            col_idx  += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.output['label']))
            # tags
            if origin_metadata:
                # tags
                for tag in tags:
                    col_idx += 1
                    if tag in origin_metadata.tags:
                        self.tableWidget.setItem(i, col_idx, QTableWidgetItem(origin_metadata.tags[tag])) 
            else:
                for tag in tags:
                    col_idx += 1
                    self.tableWidget.setItem(i, col_idx, QTableWidgetItem(""))                 
            # format
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.format))                
            # author
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.author))
            # created date
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.date))             

    def get_widget(self): 
        return self.widget    


class BiExperimentCreateComponent(BiComponent):
    def __init__(self, container: BiExperimentCreateContainer):
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
        self.destinationEdit.setText(ConfigAccess.instance().get('workspace'))
        browseButton = QPushButton(self.widget.tr("..."))
        browseButton.setObjectName("BiBrowseButton")
        browseButton.released.connect(self.browseButtonClicked)

        nameLabel = QLabel(self.widget.tr("Experiment name"))
        nameLabel.setObjectName("BiLabel")
        self.nameEdit = QLineEdit()

        authorLabel = QLabel(self.widget.tr("Author"))
        authorLabel.setObjectName("BiLabel")
        self.authorEdit = QLineEdit()
        self.authorEdit.setText(ConfigAccess.instance().get('user')['name']) 

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
        layout.addWidget(createButton, 4, 2, 1, 1, qtpy.QtCore.Qt.AlignRight)
        layout.addWidget(QWidget(), 5, 0, 1, 1, qtpy.QtCore.Qt.AlignTop)

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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()

        # title
        title = QLabel(self.widget.tr("Import single data"))
        title.setObjectName("BiLabelFormHeader1")

        dataLabel = QLabel(self.widget.tr("Data"))
        dataLabel.setObjectName("BiWidget")
        self.dataPath = QLineEdit()
        self.dataPath.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("BiBrowseButton")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        nameLabel = QLabel(self.widget.tr("Name"))
        nameLabel.setObjectName("BiWidget")
        self.nameEdit = QLineEdit()
        self.nameEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)

        formatLabel = QLabel(self.widget.tr("Format"))
        formatLabel.setObjectName("BiWidget")
        self.formatCombox = QComboBox()
        self.formatCombox.addItems(FormatsAccess.instance().names())
        self.formatCombox.setCurrentText('bioformat')

        authorLabel = QLabel(self.widget.tr("Author"))
        authorLabel.setObjectName("BiWidget")
        self.authorEdit = QLineEdit()
        self.authorEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.authorEdit.setText(ConfigAccess.instance().get('user')['name'])

        createddateLabel = QLabel(self.widget.tr("Created date"))
        createddateLabel.setObjectName("BiWidget")
        self.createddateEdit = QLineEdit()
        self.createddateEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.createddateEdit.setText(date.today().strftime("%Y-%m-%d"))

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btnPrimary")
        importButton.released.connect(self.importButtonClicked)

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(dataLabel, 1, 0)
        layout.addWidget(self.dataPath, 1, 1)
        layout.addWidget(browseDataButton, 1, 2)
        layout.addWidget(nameLabel, 2, 0)
        layout.addWidget(self.nameEdit, 2, 1, 1, 2)
        layout.addWidget(formatLabel, 3, 0)
        layout.addWidget(self.formatCombox, 3, 1, 1, 2)
        layout.addWidget(authorLabel, 4, 0)
        layout.addWidget(self.authorEdit, 4, 1, 1, 2)
        layout.addWidget(createddateLabel, 5, 0)
        layout.addWidget(self.createddateEdit, 5, 1, 1, 2)
        layout.addWidget(importButton, 6, 2, qtpy.QtCore.Qt.AlignRight)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)

        totalLayout = QVBoxLayout()
        self.widget.setLayout(totalLayout)
        thisWidget = QWidget()
        thisWidget.setLayout(layout)
        totalLayout.addWidget(thisWidget, 0)
        totalLayout.addWidget(QWidget(), 1)
        totalLayout.addWidget(self.progressBar, 0)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.DataImported:
            self.progressBar.setRange(0, 100)
            self.progressBar.setVisible(False)

    def importButtonClicked(self):
        self.container.import_info.file_data_path = self.dataPath.text()
        self.container.import_info.file_name = self.nameEdit.text()
        self.container.import_info.format = self.formatCombox.currentText()
        self.container.import_info.author = self.authorEdit.text()
        self.container.import_info.createddate = self.createddateEdit.text()
        self.container.emit(BiExperimentStates.NewImportFile)
        self.progressBar.setRange(0, 0)
        self.progressBar.setVisible(True)

    def browseDataButtonClicked(self):
        fileName = QFileDialog.getOpenFileName(self.widget, self.widget.tr("Import file"), '*.*')
        self.dataPath.setText(fileName[0])
        self.nameEdit.setText(Path(fileName[0]).stem)

    def get_widget(self):
        return self.widget  


class BiExperimentImportDirectoryDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentImportDirectoryDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportDirectoryDataComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        #self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Import from folder"))
        title.setObjectName("BiLabelFormHeader1")

        dataLabel = QLabel(self.widget.tr("Folder"))
        dataLabel.setObjectName("BiWidget")
        self.dataPath = QLineEdit()
        self.dataPath.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("BiBrowseButton")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        key_value_label = QLabel(self.widget.tr("Key-Value pair"))
        key_value_label.setObjectName("BiWidget")
        self.key_value_box = QCheckBox("use folder name as value")
        self.key_value_box.setChecked(False)
        self.key_value_box.setObjectName("BiCheckBoxNegative")
        self.key_value_box.stateChanged.connect(self.update_key_value_box)

        self.key_value_title = QLabel('key')
        self.key_value_title.setObjectName("BiWidget")
        self.key_folder_edit = QLineEdit()
        self.key_folder_edit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)

        filterLabel = QLabel(self.widget.tr("Filter"))
        filterLabel.setObjectName("BiWidget")
        self.filterComboBox = QComboBox()
        self.filterComboBox.addItem(self.widget.tr('Ends With'))
        self.filterComboBox.addItem(self.widget.tr('Start With'))
        self.filterComboBox.addItem(self.widget.tr('Contains'))
        self.filterEdit = QLineEdit()
        self.filterEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.filterEdit.setText('.tif')

        formatLabel = QLabel(self.widget.tr("Format"))
        formatLabel.setObjectName("BiWidget")
        self.formatCombox = QComboBox()
        self.formatCombox.addItems(FormatsAccess.instance().names())
        self.formatCombox.setCurrentText('bioformat')

        authorLabel = QLabel(self.widget.tr("Author"))
        authorLabel.setObjectName("BiWidget")
        self.authorEdit = QLineEdit()
        self.authorEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.authorEdit.setText(ConfigAccess.instance().get('user')['name'])

        createddateLabel = QLabel(self.widget.tr("Created date"))
        createddateLabel.setObjectName("BiWidget")
        self.createddateEdit = QLineEdit()
        self.createddateEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.createddateEdit.setText(date.today().strftime("%Y-%m-%d"))

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btnPrimary")
        importButton.released.connect(self.importButtonClicked)

        layout.addWidget(title, 0, 0, 1, 4)
        layout.addWidget(dataLabel, 1, 0)
        layout.addWidget(self.dataPath, 1, 1, 1, 2)
        layout.addWidget(browseDataButton, 1, 3)
        layout.addWidget(key_value_label, 2, 0)
        layout.addWidget(self.key_value_box, 2, 1, 1, 2)
        layout.addWidget(self.key_value_title, 3, 1)
        layout.addWidget(self.key_folder_edit, 3, 2, 1, 1)

        layout.addWidget(filterLabel, 4, 0)
        layout.addWidget(self.filterComboBox, 4, 1, 1, 1)
        layout.addWidget(self.filterEdit, 4, 2, 1, 1)
        layout.addWidget(formatLabel, 5, 0)
        layout.addWidget(self.formatCombox, 5, 1, 1, 2)
        layout.addWidget(authorLabel, 6, 0)
        layout.addWidget(self.authorEdit, 6, 1, 1, 2)
        layout.addWidget(createddateLabel, 7, 0)
        layout.addWidget(self.createddateEdit, 7, 1, 1, 2)
        layout.addWidget(importButton, 8, 3, qtpy.QtCore.Qt.AlignRight)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)

        totalLayout = QVBoxLayout()
        self.widget.setLayout(totalLayout)
        thisWidget = QWidget()
        thisWidget.setLayout(layout)
        totalLayout.addWidget(thisWidget, 0)
        totalLayout.addWidget(QWidget(), 1)
        totalLayout.addWidget(self.progressBar, 0)
        self.update_key_value_box(False)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Progress:
            if 'progress' in self.container.progress:
                self.progressBar.setVisible(True)
                self.progressBar.setValue(self.container.progress)
                if self.container.progress == 100:
                    self.progressBar.setVisible(False)
        elif action.state == BiExperimentStates.DataImported:
            self.progressBar.setRange(0, 100)
            self.progressBar.setVisible(False)

    def update_key_value_box(self, status):
        if status:
            self.key_value_title.setVisible(True)
            self.key_folder_edit.setVisible(True)
        else:  
            self.key_value_title.setVisible(False)
            self.key_folder_edit.setVisible(False)  

    def importButtonClicked(self):
        self.container.import_info.dir_data_path = self.dataPath.text()
        if self.key_value_box.isChecked():
            self.container.import_info.dir_tag_key = self.key_folder_edit.text()
        else:
            self.container.import_info.dir_tag_key = ''
        self.container.import_info.dir_filter = self.filterComboBox.currentIndex()
        self.container.import_info.dir_filter_value = self.filterEdit.text()
        self.container.import_info.author = self.authorEdit.text()
        self.container.import_info.format = self.formatCombox.currentText()
        self.container.import_info.createddate = self.createddateEdit.text()
        self.container.emit(BiExperimentStates.NewImportDir)
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0, 0)

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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
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
        buttonsLayout.setSpacing(15)
        buttonsWidget.setLayout(buttonsLayout)
        cancelButton = QPushButton(self.widget.tr("Cancel"))
        cancelButton.setObjectName("btnDefault")
        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        buttonsLayout.addWidget(cancelButton, 1, qtpy.QtCore.Qt.AlignRight)
        buttonsLayout.addWidget(saveButton, 0)

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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        #self.widget.setLayout(layout)

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

        mainWidget = QWidget()
        mainWidget.setLayout(layout)

        globalLayout = QVBoxLayout()
        self.widget.setLayout(globalLayout)

        globalLayout.addWidget(mainWidget, 0)
        globalLayout.addWidget(QWidget(), 1)

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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        #self.widget.setLayout(layout)

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

        layout.addWidget(title, 0, 0, 1, 2)
        layout.addWidget(tagLabel, 1, 0, 1, 1, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(self.tagEdit, 1, 1)
        layout.addWidget(searchLabel, 2, 0, 1, 1, qtpy.QtCore.Qt.AlignTop )
        layout.addWidget(searchWidget, 2, 1)
        layout.addWidget(addLineButton, 3, 1)
        layout.addWidget(validateButton, 4, 2)

        mainWidget = QWidget()
        mainWidget.setLayout(layout)

        globalLayout = QVBoxLayout()
        self.widget.setLayout(globalLayout)

        globalLayout.addWidget(mainWidget, 0)
        globalLayout.addWidget(QWidget(), 1)

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
