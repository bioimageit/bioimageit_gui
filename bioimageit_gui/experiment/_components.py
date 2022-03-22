from pathlib import Path
from datetime import date

import qtpy.QtCore
from qtpy.QtGui import QIcon 
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QGridLayout, QHBoxLayout, QToolButton, 
                               QLineEdit, QPushButton, QMessageBox, 
                               QFileDialog, QTabWidget, QSpinBox, QCheckBox, 
                               QComboBox, QProgressBar, QHeaderView)

from bioimageit_core import ConfigAccess
from bioimageit_core.api import APIAccess
from bioimageit_formats import FormatsAccess
from bioimageit_viewer.viewer import BiMultiViewer

from bioimageit_framework.theme import BiThemeAccess
from bioimageit_framework.framework import BiComponent, BiConnectome
from bioimageit_framework.widgets import BiTagWidget, BiButtonDefault, BiButtonPrimary

from bioimageit_gui.metadata import (BiRawDataContainer,
                                     BiProcessedDataViewerContainer,
                                     BiRunContainer,
                                     BiMetadataExperimentContainer,
                                     BiRawDataComponent,
                                     BiProcessedDataViewerComponent,
                                     BiMetadataRunComponent,
                                     BiMetadataExperimentComponent,
                                     BiRawDataModel,
                                     BiProcessedDataViewerModel,
                                     BiRunModel,
                                     BiMetadataExperimentModel)
from ._containers import (BiExperimentContainer,
                          BiExperimentCreateContainer
                         )
from ._models import BiExperimentModel


class BiExperimentViewerComponent(BiComponent):
    def __init__(self, experiment_uri: str, viewer: BiMultiViewer):
        super().__init__()

        self.show_viewer = True    
        self.viewer = viewer
        self.viewer.set_visible(False)

        # instantiate the experiment component
        self.experimentContainer = BiExperimentContainer()
        self.experimentComponent = BiExperimentComponent(self.experimentContainer)
        self.experimentModel = BiExperimentModel(self.experimentContainer)

        BiConnectome.connect(self.experimentContainer, self.experimentModel)
        BiConnectome.connect(self.experimentContainer, self)
        self.experimentContainer.init(experiment_uri)

        # Widget
        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        layout.addWidget(self.experimentComponent.widget)

    def callback_ask_view_data(self, emitter):
        local_uri = APIAccess.instance().download_data(emitter.selected_data_info.md_uri)
        self.viewer.add_data(local_uri,
                             emitter.selected_data_info.name,
                             emitter.selected_data_info.format)
        self.viewer.set_visible(True)


class BiExperimentComponent(BiComponent):
    AskRefresh = 'ask_refresh'

    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentComponent'
        self.show_viewer = True
        BiConnectome.connect(container, self)

        # containers
        self.container = container
        self.rawDataContainer = BiRawDataContainer()
        self.processedDataContainer = BiProcessedDataViewerContainer()
        self.metadataExperimentContainer = BiMetadataExperimentContainer()

        BiConnectome.connect(self.rawDataContainer, self)
        BiConnectome.connect(self.processedDataContainer, self)
        BiConnectome.connect(self.metadataExperimentContainer, self)

        # models
        self.rawDataModel = BiRawDataModel()
        self.processedDataModel = BiProcessedDataViewerModel()
        self.metadataExperimentModel = BiMetadataExperimentModel()

        BiConnectome.connect(self.rawDataContainer, self.rawDataModel)
        BiConnectome.connect(self.processedDataContainer, self.processedDataModel)
        BiConnectome.connect(self.metadataExperimentContainer, self.metadataExperimentModel)

        # components
        self.toolbarComponent = BiExperimentToolbarComponent(self.container)
        self.metaToolbarComponent = BiExperimentMetaToolbarComponent(self.container)
        self.datasetViewComponent = BiExperimentDataSetViewComponent(self.container)
        self.rawDataComponent = BiRawDataComponent()
        self.processedDataComponent = BiProcessedDataViewerComponent()
        self.runComponent = BiMetadataRunComponent()
        self.metadataExperimentComponent = BiMetadataExperimentComponent()
        self.importComponent = BiExperimentImportComponent(self.container)
        self.tagComponent = BiExperimentTagComponent(self.container)

        BiConnectome.connect(self.rawDataContainer, self.rawDataComponent)
        BiConnectome.connect(self.processedDataContainer, self.processedDataComponent)
        BiConnectome.connect(self.metadataExperimentContainer, self.metadataExperimentComponent)

        # widget
        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.widget.setLayout(layout)

        layout.addWidget(self.toolbarComponent.get_widget())
        layout.addWidget(self.metaToolbarComponent.get_widget())
        layout.addWidget(self.datasetViewComponent.get_widget())
        layout.addWidget(self.metadataExperimentComponent.get_widget())
        layout.addWidget(self.importComponent.get_widget())
        layout.addWidget(self.tagComponent.get_widget())
        layout.addWidget(self.rawDataComponent.get_widget())
        layout.addWidget(self.processedDataComponent.get_widget())

        # widget init
        self.metaToolbarComponent.get_widget().setVisible(False)
        self.metadataExperimentComponent.get_widget().setVisible(False)
        self.importComponent.get_widget().setVisible(False)
        self.tagComponent.get_widget().setVisible(False)
        self.rawDataComponent.get_widget().setVisible(False)
        self.processedDataComponent.get_widget().setVisible(False)

    def hideDataComponents(self):
        self.rawDataComponent.get_widget().setVisible(False)  
        self.processedDataComponent.get_widget().setVisible(False)

    def callback_experiment_loaded(self, emitter):
        self.metadataExperimentContainer.action_metadata_loaded(None, emitter.experiment)

    def callback_view_raw_metadata_clicked(self, emitter):
        data_uri = emitter.current_dataset.uris[emitter.clickedRow].md_uri
        print('experiment component open:', data_uri)
        self.rawDataContainer.action_update_uri(None, data_uri)
        self.toolbarComponent.get_widget().setVisible(False)
        self.metaToolbarComponent.get_widget().setVisible(True) 
        self.datasetViewComponent.get_widget().setVisible(False)  
        self.rawDataComponent.get_widget().setVisible(True)
        self.processedDataComponent.get_widget().setVisible(False)

    def callback_view_processed_metadata_clicked(self, emitter):
        self.processedDataContainer.action_update_uri(None, emitter.current_dataset.uris[self.container.clickedRow].md_uri)   

        self.toolbarComponent.get_widget().setVisible(False)
        self.metaToolbarComponent.get_widget().setVisible(True) 
        self.datasetViewComponent.get_widget().setVisible(False) 
        self.rawDataComponent.get_widget().setVisible(False)
        self.processedDataComponent.get_widget().setVisible(True)

    def callback_saved(self, emitter):
        self.toolbarComponent.get_widget().setVisible(True)
        self.metaToolbarComponent.get_widget().setVisible(False) 
        self.datasetViewComponent.get_widget().setVisible(True)  
        self.rawDataComponent.get_widget().setVisible(False)
        self._emit(BiExperimentComponent.AskRefresh)

    def callback_edit_info_clicked(self, emitter):
        self.toolbarComponent.get_widget().setVisible(False)
        self.metaToolbarComponent.get_widget().setVisible(True)
        self.metadataExperimentComponent.get_widget().setVisible(True)  
        self.datasetViewComponent.get_widget().setVisible(False) 

    def callback_metadata_saved(self, emitter):
        self.toolbarComponent.get_widget().setVisible(True)
        self.metaToolbarComponent.get_widget().setVisible(False)
        self.metadataExperimentComponent.get_widget().setVisible(False)  
        self.datasetViewComponent.get_widget().setVisible(True)   
        self.toolbarComponent.updateTitle() 

    def callback_import_clicked(self, emitter):
        self.toolbarComponent.get_widget().setVisible(False)
        self.metaToolbarComponent.get_widget().setVisible(True)
        self.importComponent.get_widget().setVisible(True)  
        self.datasetViewComponent.get_widget().setVisible(False) 

    def callback_data_imported(self, emitter):
        self.toolbarComponent.get_widget().setVisible(True)
        self.metaToolbarComponent.get_widget().setVisible(False)
        self.importComponent.get_widget().setVisible(False)  
        self.datasetViewComponent.get_widget().setVisible(True) 
        msgBox = QMessageBox()
        msgBox.setText("Data imported")
        msgBox.exec() 
        self._emit(BiExperimentComponent.AskRefresh)

    def callback_tag_clicked(self, emitter):
        self.toolbarComponent.get_widget().setVisible(False)
        self.metaToolbarComponent.get_widget().setVisible(True)
        self.tagComponent.get_widget().setVisible(True)  
        self.datasetViewComponent.get_widget().setVisible(False) 

    def callback_tag_saved(self, emitter):
        self._toggle_tag()    

    def callback_data_tagged(self, emitter):
        self._toggle_tag() 

    def _toggle_tag(self):
        self.toolbarComponent.get_widget().setVisible(True)
        self.metaToolbarComponent.get_widget().setVisible(False)
        self.tagComponent.get_widget().setVisible(False)  
        self.datasetViewComponent.get_widget().setVisible(True) 
        msgBox = QMessageBox()
        msgBox.setText("Tags saved")
        msgBox.exec() 
        self._emit(BiExperimentComponent.AskRefresh)

    def callback_dataset_clicked(self, emitter):
        self.hideDataComponents()    

    def callback_run_open_clicked(self, emitter):
        self.runContainer.action_uri_changed(None, self.processedDataContainer.processeddata.run_uri)

    def callback_run_loaded(self, emitter):
        self.runComponent.widget.setVisible(True)

    def callback_delete_raw_clicked(self, emitter):
        print('catch delete rawdata:', self.container.selected_data_info.md_uri)
        msgbox = QMessageBox(QMessageBox.Question, "Confirm delete", f"Are you sure you want to delete: {self.container.selected_data_info.name}?")
        msgbox.addButton(QMessageBox.Yes)
        msgbox.addButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.No)

        reply = msgbox.exec()
        if reply == QMessageBox.Yes:
            self.rawDataContainer.action_delete(None, self.container.selected_data_info.md_uri)

    def callback_raw_data_deleted(self, emitter):
        self._emit(BiExperimentComponent.AskRefresh)

    def callback_main_page_clicked(self, emitter):
        self.metaToolbarComponent.get_widget().setVisible(False)
        self.tagComponent.get_widget().setVisible(False)
        self.importComponent.get_widget().setVisible(False)
        self.metadataExperimentComponent.get_widget().setVisible(False)
        self.rawDataComponent.get_widget().setVisible(False)
        self.processedDataComponent.get_widget().setVisible(False)
        self.toolbarComponent.get_widget().setVisible(True)
        self.datasetViewComponent.get_widget().setVisible(True) 
    

class BiExperimentToolbarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiBrowserExperimentToolbar'
        self.container = container
        BiConnectome.connect(container, self)

        self.widget = QWidget()
        self.widget.setObjectName('bi-toolbar')
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QHBoxLayout()
        layout.setSpacing(1)
        self.widget.setLayout(layout)

        # info
        infoButton = QToolButton()
        infoButton.setIcon(QIcon(BiThemeAccess.instance().icon('info')))
        infoButton.setToolTip(self.widget.tr("Information"))
        infoButton.released.connect(self.infoButtonClicked)
        layout.addWidget(infoButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # import
        importButton = QToolButton()
        importButton.setIcon(QIcon(BiThemeAccess.instance().icon('upload')))
        importButton.setToolTip(self.widget.tr("Import data"))
        importButton.released.connect(self.importButtonClicked)
        layout.addWidget(importButton, 0, qtpy.QtCore.Qt.AlignLeft)
        
        # tags
        tagButton = QToolButton()
        tagButton.setIcon(QIcon(BiThemeAccess.instance().icon('tags')))
        tagButton.setToolTip(self.widget.tr("Annotate data"))
        tagButton.released.connect(self.tagButtonClicked)
        layout.addWidget(tagButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # refresh
        refreshButton = QToolButton()
        refreshButton.setIcon(QIcon(BiThemeAccess.instance().icon('refresh')))
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
        self.nameLabel.setObjectName('bi-label')
        self.nameLabel.setAlignment(qtpy.QtCore.Qt.AlignRight | qtpy.QtCore.Qt.AlignVCenter)
        layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignRight)
        layout.addWidget(self.nameLabel, 0, qtpy.QtCore.Qt.AlignRight)

    def updateTitle(self):
        self.nameLabel.setText(self.container.experiment.name)

    def infoButtonClicked(self):
        self.container.action_edit_info_clicked(None)

    def importButtonClicked(self):
        self.container.action_import_clicked(None)

    def tagButtonClicked(self):
        self.container.action_tag_clicked(None)

    def processButtonClicked(self):
        self.container.action_process_clicked(None)

    def refreshButtonClicked(self):
        self.container.action_refresh_clicked(None)

    def datasetBoxChanged(self):
        self.container.action_dataset_clicked(None, self.dataset_box.currentText())

    def closeButtonClicked(self):
        self.container.action_close_clicked(None) 

    def callback_experiment_loaded(self, emitter):
        print('toolbar callback_experiment_loaded')
        self.nameLabel.setText(emitter.experiment.name)  
        # update the list of datasets in the combobox
        current_text = self.dataset_box.currentText
        self.dataset_box.clear()
        self.dataset_box.addItem('data')
        self.dataset_box.currentIndexChanged.disconnect(
            self.datasetBoxChanged)
        for pdataset_uri in emitter.experiment.processed_datasets:
            print('pdataset_uri=', pdataset_uri.url)
            pdataset = APIAccess.instance().get_dataset_from_uri(pdataset_uri.url)
            dataset_name = pdataset.name
            self.dataset_box.addItem(dataset_name)
            if dataset_name == current_text:
                self.dataset_box.setCurrentText(dataset_name)
        self.dataset_box.currentIndexChanged.connect(
            self.datasetBoxChanged) 


class BiExperimentMetaToolbarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentMetaToolbarComponent'
        self.container = container
        BiConnectome.connect(self.container, self)

        self.widget = QWidget()
        self.widget.setObjectName('bi-toolbar')
        layout = QHBoxLayout()
        self.widget.setLayout(layout)
        returnButton = QToolButton()
        returnButton.setIcon(QIcon(BiThemeAccess.instance().icon('arrow-left')))
        returnButton.released.connect(self.emitReturn)
        layout.addWidget(returnButton, 0, qtpy.QtCore.Qt.AlignLeft)

    def emitReturn(self):
        self.container.action_main_page_clicked(None)


class BiExperimentDataSetListComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentDataSetListComponent'
        self.container = container
        BiConnectome.connect(self.container, self)

        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)
        self.widget.setMinimumWidth(150)

        widget = QWidget()
        widget.setObjectName('bi-side-bar')
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setWidget(widget)

        self.buttons = []

        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)

    def datasetClicked(self, name: str):  
        self.container.action_dataset_clicked(None, name)

    def callback_experiment_loaded(self, emitter):
        self.createDataSetsButton()

    def callback_refresh_clicked(self, emitter):
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
        
        dataButton = BiButtonDefault('data')
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

        for pdataset_uri in self.container.experiment.processed_datasets:
            pdataset = APIAccess.instance().get_dataset(pdataset_uri)
            datasetButton = BiButtonDefault(pdataset.name)
            datasetButton.content = pdataset.name
            datasetButton.setObjectName('BiBrowserShortCutsButton')
            datasetButton.setCheckable(True)
            datasetButton.setAutoExclusive(True)
            if self.container.current_dataset_name == pdataset.name:
                datasetButton.setChecked(True)
            datasetButton.clickedContent.connect(self.datasetClicked)
            self.layout.addWidget(datasetButton, 0, qtpy.QtCore.Qt.AlignTop)
            self.buttons.append(datasetButton)
        self.layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop)

    def updateList(self):
        pass


class BiExperimentDataSetViewComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()

        self.btns = []
        self._object_name = 'BiExperimentDataSetViewComponent'
        self.container = container
        BiConnectome.connect(self.container, self)

        self.widget = QWidget()
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


    def callback_dataset_loaded(self, emitter):
        print('table view reload dataset: ', emitter.current_dataset_name)
        if emitter.current_dataset_name == "data":
            self.drawRawDataset()
        else:
            if emitter.current_dataset:
                self.drawProcessedDataSet()  

    def callback_experiment_loaded(self, emitter):
        print('table view reload dataset: ', emitter.current_dataset_name)
        if emitter.current_dataset_name == "data":
            self.drawRawDataset()
        else:
            if emitter.current_dataset:
                self.drawProcessedDataSet()    

    def callback_dataset_loaded(self, emitter):
        print('show dataset ', emitter.current_dataset_name)
        if emitter.current_dataset_name == "data":
            self.drawRawDataset()
        else:
            if emitter.current_dataset:
                self.drawProcessedDataSet()
                    
    def drawRawDataset(self):
        # headers
        tags = self.container.experiment.keys
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

        data_list = APIAccess.instance().get_data(self.container.current_dataset)
        
        self.btns.clear()
        for i in range(len(data_list)):
            raw_metadata = data_list[i]

            # view button
            col_idx = 0
            view_btn = BiButtonPrimary("View")
            view_btn.widget.setObjectName('bi-table-btn-primary')
            view_btn.id = i
            view_btn.connect('clicked', self.viewDataClicked)
            self.btns.append(view_btn)
            self.tableWidget.setCellWidget(i, col_idx, view_btn.widget)

            # metadata button
            col_idx += 1
            edit_btn = BiButtonDefault("Metadata")
            edit_btn.widget.setObjectName('bi-table-btn-default')
            edit_btn.id = i
            edit_btn.connect('clicked', self.viewMetaDataClicked)
            self.btns.append(edit_btn)
            self.tableWidget.setCellWidget(i, col_idx, edit_btn.widget)

            # delete button
            col_idx += 1
            del_btn = BiButtonDefault("X")
            del_btn.widget.setObjectName('bi-table-btn-default')
            del_btn.widget.setMaximumWidth(20)
            del_btn.id = i
            del_btn.connect('clicked', self.deleteRawDataClicked)
            self.btns.append(del_btn)
            self.tableWidget.setCellWidget(i, col_idx, del_btn.widget)

            # name
            col_idx +=1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.name))
            # tags
            for tag in tags:
                col_idx += 1
                if tag in raw_metadata.key_value_pairs:
                    self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.key_value_pairs[tag])) 
            # format
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.format))                
            # author
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(raw_metadata.author))
            # created date
            col_idx += 1
            self.tableWidget.setItem(i, col_idx, QTableWidgetItem(str(raw_metadata.date)))

        #self.tableWidget.resizeColumnsToContents()    

    def cellClicked(self, row : int, col : int):
        self.container.clickedRow = row
        self.highlightLine(row)

    def viewDataClicked(self, emitter):
        data_uri = self.container.current_dataset.uris[emitter.id].md_uri
        selected_data_info = APIAccess.instance().get_raw_data(data_uri)
        print('emit view data:', selected_data_info.uri)
        self.container.action_view_data_clicked(None, selected_data_info)

    def viewMetaDataClicked(self, emitter):
        data_uri = self.container.current_dataset.uris[emitter.id].md_uri
        self.container.selected_data_info = APIAccess.instance().get_raw_data(data_uri)
        self.container.clickedRow = emitter.id
        print('emit view metadata:', self.container.selected_data_info.uri)
        if self.container.current_dataset_name == 'data':
            self.container.action_view_raw_metadata_clicked(None)
        else:
            self.container.action_view_processed_metadata_clicked(None)

    def deleteRawDataClicked(self, emitter):
        data_uri = self.container.current_dataset.uris[emitter.id].md_uri
        self.container.selected_data_info = APIAccess.instance().get_raw_data(data_uri)
        print('emit delete rawdata:', self.container.selected_data_info.uri)
        if self.container.current_dataset_name == 'data':
            self.container.action_delete_raw_data(None, emitter.id, self.container.selected_data_info)

    def highlightLine(self, row: int):
        for col in range(0, self.tableWidget.columnCount()):
            self.tableWidget.setCurrentCell(row, col, qtpy.QtCore.QItemSelectionModel.Select)  

    def drawProcessedDataSet(self):
        # headers
        tags = self.container.experiment.keys
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

        data_list = APIAccess.instance().get_data(self.container.current_dataset)
        
        self.btns.clear()
        for i in range(len(data_list)):
            raw_metadata = data_list[i]
            parent_metadata = APIAccess.instance().get_parent(data_list[i])
            origin_metadata = APIAccess.instance().get_origin(data_list[i])

            # view button
            col_idx = 0
            view_btn = BiButtonDefault("View")
            view_btn.id = i
            view_btn.widget.setObjectName("bi-table-btn-primary")
            view_btn.connect('clicked', self.viewDataClicked)
            self.btns.append(view_btn)
            self.tableWidget.setCellWidget(i, col_idx, view_btn.widget)

            # metadata button
            col_idx += 1
            edit_btn = BiButtonDefault("Metadata")
            edit_btn.id = i
            edit_btn.widget.setObjectName("bi-table-btn-default")
            self.btns.append(edit_btn)
            edit_btn.connect('clicked', self.viewMetaDataClicked)
            self.tableWidget.setCellWidget(i, col_idx, edit_btn.widget)

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
                    if tag in origin_metadata.key_value_pairs:
                        self.tableWidget.setItem(i, col_idx, QTableWidgetItem(origin_metadata.key_value_pairs[tag])) 
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


class BiExperimentCreateComponent(BiComponent):
    def __init__(self, container: BiExperimentCreateContainer):
        super().__init__()
        self._object_name = 'BiExperimentCreateComponent'
        self.container = container
        BiConnectome.connect(self.container, self)

        self.widget = QWidget()
        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Create experiment"))
        title.setObjectName("bi-label-form-header1")
        title.setMaximumHeight(50)

        destinationLabel = QLabel(self.widget.tr("Destination"))
        destinationLabel.setObjectName("bi-label")
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
        createButton.setObjectName("btn-primary")
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
        self.container.action_create(None, self.destinationEdit.text(),
                                     self.nameEdit.text(),
                                     self.authorEdit.text())

    def reset(self):
        self.destinationEdit.setText('')
        self.nameEdit.setText('')
        self.authorEdit.setText('')    

    def setDestination(self, path: str):
        self.destinationEdit.setText(path)


class BiExperimentImportComponent(BiComponent):        
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentImportComponent'
        self.container = container

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)

        importSingleComponent = BiExperimentImportSingleDataComponent(container)
        tabWidget.addTab(importSingleComponent.get_widget(), self.widget.tr("Single Data"))

        importDirectoryComponent = BiExperimentImportDirectoryDataComponent(container)
        tabWidget.addTab(importDirectoryComponent.get_widget(), self.widget.tr("Multiple Data"))


class BiExperimentImportSingleDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentImportSingleDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportSingleDataComponent'
        self.container = container
        BiConnectome.connect(self.container, self)

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QGridLayout()

        # title
        title = QLabel(self.widget.tr("Import single data"))
        title.setObjectName("bi-label-form-header1")

        dataLabel = QLabel(self.widget.tr("Data"))
        self.dataPath = QLineEdit()
        self.dataPath.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("bi-browse-button")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        nameLabel = QLabel(self.widget.tr("Name"))
        self.nameEdit = QLineEdit()
        self.nameEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)

        formatLabel = QLabel(self.widget.tr("Format"))
        self.formatCombox = QComboBox()
        self.formatCombox.addItems(FormatsAccess.instance().names())
        self.formatCombox.setCurrentText('bioformat')

        authorLabel = QLabel(self.widget.tr("Author"))
        self.authorEdit = QLineEdit()
        self.authorEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.authorEdit.setText(ConfigAccess.instance().get('user')['name'])

        createddateLabel = QLabel(self.widget.tr("Created date"))
        self.createddateEdit = QLineEdit()
        self.createddateEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.createddateEdit.setText(date.today().strftime("%Y-%m-%d"))

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btn-primary")
        importButton.released.connect(self.import_button_clicked)

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

    def callback_data_imported(self, emitter):
        self.progressBar.setRange(0, 100)
        self.progressBar.setVisible(False)            

    def import_button_clicked(self):
        self.container.action_import_file(None, self.dataPath.text(), 
                                          self.nameEdit.text(), self.formatCombox.currentText(), 
                                          self.authorEdit.text(), self.createddateEdit.text())
        self.progressBar.setRange(0, 0)
        self.progressBar.setVisible(True)

    def browseDataButtonClicked(self):
        fileName = QFileDialog.getOpenFileName(self.widget, self.widget.tr("Import file"), '*.*')
        self.dataPath.setText(fileName[0])
        self.nameEdit.setText(Path(fileName[0]).stem)


class BiExperimentImportDirectoryDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentImportDirectoryDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportDirectoryDataComponent'
        self.container = container
        BiConnectome.connect(self.container, self) 

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()

        # title
        title = QLabel(self.widget.tr("Import from folder"))
        title.setObjectName("bi-label-form-header1")

        dataLabel = QLabel(self.widget.tr("Folder"))
        self.dataPath = QLineEdit()
        self.dataPath.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.released.connect(self.browseDataButtonClicked)

        key_value_label = QLabel(self.widget.tr("Key-Value pair"))
        self.key_value_box = QCheckBox("use folder name as value")
        self.key_value_box.setChecked(False)
        self.key_value_box.setObjectName("BiCheckBoxNegative")
        self.key_value_box.stateChanged.connect(self.update_key_value_box)

        self.key_value_title = QLabel('key')
        self.key_folder_edit = QLineEdit()
        self.key_folder_edit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)

        filterLabel = QLabel(self.widget.tr("Filter"))
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

    def callback_progress(self, emitter):
        if 'progress' in self.container.progress:
            self.progressBar.setVisible(True)
            self.progressBar.setValue(self.container.progress)
            if self.container.progress == 100:
                self.progressBar.setVisible(False)

    def callback_data_imported(self, emitter):
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
        dir_tag_key = ''
        if self.key_value_box.isChecked():
            dir_tag_key = self.key_folder_edit.text()
        self.container.action_import_dir(None, self.dataPath.text(), dir_tag_key, self.filterComboBox.currentIndex(), self.filterEdit.text(), self.authorEdit.text(), self.formatCombox.currentText(), self.createddateEdit.text())
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0, 0)

    def browseDataButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.widget, self.widget.tr("Select Directory"),
                                       "",
                                       QFileDialog.ShowDirsOnly
                                       | QFileDialog.DontResolveSymlinks)
        self.dataPath.setText(directory)


class BiExperimentTagComponent(BiComponent):        
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagComponent'
        self.container = container
        BiConnectome.connect(self.container, self)

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

        tabWidget.addTab(tagsListComponent.get_widget(), self.widget.tr("Keys"))
        tabWidget.addTab(tagUsingSeparatorComponent.get_widget(), self.widget.tr("Annotate using separator"))
        tabWidget.addTab(tagUsingNameComponent.get_widget(), self.widget.tr("Annotate using name"))


class BiExperimentTagsListComponent(BiComponent):
    TagsModified = 'tags_modified'

    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagsListComponent'
        self.container = container
        BiConnectome.connect(self.container, self)

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        self.tags_widgets = []

        # title
        title = QLabel(self.widget.tr("Keys"))
        title.setObjectName("bi-label-form-header1")

        # add widget
        addWidget = QWidget()
        addLayout = QHBoxLayout()
        addWidget.setLayout(addLayout)

        self.addEdit = QLineEdit(self.widget)
        addButton = QPushButton(self.widget.tr("Add"))
        addButton.setObjectName("bt-default")
        addLayout.addWidget(self.addEdit)
        addLayout.addWidget(addButton)

        self.tagListWidget = QWidget()
        self.tagListLayout = QVBoxLayout()
        self.tagListWidget.setLayout(self.tagListLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.tagListWidget)

        # button area
        buttonsWidget = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setContentsMargins(0,0,0,0)
        buttonsLayout.setSpacing(15)
        buttonsWidget.setLayout(buttonsLayout)
        cancelButton = QPushButton(self.widget.tr("Cancel"))
        cancelButton.setObjectName("btn-default")
        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btn-primary")
        buttonsLayout.addWidget(cancelButton, 1, qtpy.QtCore.Qt.AlignRight)
        buttonsLayout.addWidget(saveButton, 0)

        layout.addWidget(title)
        layout.addWidget(addWidget)
        layout.addWidget(scrollArea)
        layout.addWidget(buttonsWidget)

        addButton.released.connect(self.addButtonClicked)
        cancelButton.released.connect(self.cancelButtonClicked)
        saveButton.released.connect(self.saveButtonClicked)

    def callback_experiment_loaded(self, emitter):
        self.reload()

    def reload(self):
        # free layout
        for i in reversed(range(self.tagListLayout.count())): 
            self.tagListLayout.itemAt(i).widget().deleteLater()

        # add tags
        self.tags_widgets.clear()
        for tag in self.container.experiment.keys:
            tagWidget = BiTagWidget() 
            self.tags_widgets.append(tagWidget)
            tagWidget.set_tag_name(tag)
            tagWidget.connect('remove', self.remove_clicked)
            self.tagListLayout.addWidget(tagWidget.widget)
        self.tagListWidget.adjustSize()

    def addButtonClicked(self):
        if self.addEdit.text() != "":
            tagWidget = BiTagWidget()
            self.tags_widgets.append(tagWidget)
            tagWidget.set_tag_name(self.addEdit.text())
            tagWidget.connect('remove', self.remove_clicked)
            self.tagListLayout.addWidget(tagWidget.widget)
            self.addEdit.setText("")
            self.tagListLayout.update()

    def cancelButtonClicked(self):
        self.reload()

    def saveButtonClicked(self):
        tags = []
        for tag_widget in self.tags_widgets:
            tags.append(tag_widget.tag_name())           
        self._emit(BiExperimentTagsListComponent.TagsModified, [tags])

    def remove_clicked(self, tag: str):
        for i in range(self.tagListLayout.count()):
            item = self.tagListLayout.itemAt( i )
            widget = item.widget()
            if widget:
                if widget.content() == tag:
                    itemd = self.tagListLayout.takeAt( i )
                    itemd.widget().deleteLater()
        self.tagListWidget.adjustSize()   


class BiExperimentTagsUsingSeparatorsComponent(BiComponent):
    TagUsingSeparators = 'tag_using_separators'

    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagsUsingSeparatorsComponent'
        self.container = container
        BiConnectome.connect(self.container, self)
        self._tagsEdit = []
        self._separatorEdit = []
        self._positionSpinBox = []

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QGridLayout()
        #self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Annotate using separator"))
        title.setObjectName("bi-label-form-header1")

        gridWidget = QWidget()
        self.gridLayout = QGridLayout()
        gridWidget.setLayout(self.gridLayout)

        tagLabel = QLabel(self.widget.tr("Key"))
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
        addLineButton.setObjectName('btn-default')
        addLineButton.released.connect(self.addLine)

        validateButton = QPushButton(self.widget.tr("Validate"))
        validateButton.setObjectName('btn-primary')
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

        self.container.action_annotate_using_separator(None, tags, separator, position)

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


class BiExperimentTagsUsingNameComponent(BiComponent):
    TagUsingName = 'tag_using_name'

    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagsUsingNameComponent'
        self.container = container
        BiConnectome.connect(self.container, self)  

        self._namesEdit = []

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QGridLayout()

        # title
        title = QLabel(self.widget.tr("Annotate using name"))
        title.setObjectName("bi-label-form-header1")

        tagLabel = QLabel(self.widget.tr("Key:"))
        tagLabel.setObjectName("BiWidget")
        self.tagEdit = QLineEdit()

        searchLabel = QLabel(self.widget.tr("Searched values:"))
        searchLabel.setObjectName("BiWidget")
        searchWidget = QWidget()
        self.searchLayout = QVBoxLayout()
        self.searchLayout.setContentsMargins(0,0,0,0)
        searchWidget.setLayout(self.searchLayout)

        nameEdit = QLineEdit()
        self._namesEdit.append(nameEdit)
        self.searchLayout.addWidget(nameEdit)

        addLineButton = QPushButton(self.widget.tr("Add value"))
        addLineButton.setObjectName('btn-default')
        addLineButton.released.connect(self.addLine)

        validateButton = QPushButton(self.widget.tr("Validate"))
        validateButton.setObjectName('btn-primary')
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
        self.container.action_annotate_using_name(None, self.tagEdit.text(), (names))    

    def addLine(self):
        nameEdit = QLineEdit()
        self._namesEdit.append(nameEdit)
        self.searchLayout.addWidget(nameEdit)
