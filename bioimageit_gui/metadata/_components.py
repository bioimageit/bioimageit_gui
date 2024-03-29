from bioimageit_core.api.request import APIAccess
import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QLabel, QScrollArea,
                            QTableWidget, QTableWidgetItem,
                            QGridLayout, QLineEdit, QPushButton,
                            QMessageBox)
from bioimageit_core.containers import RawData

from bioimageit_framework.framework import BiComponent

from bioimageit_framework.widgets import BiDictViewer


class BiRawDataComponent(BiComponent):
    SaveClicked = 'raw_data_save'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRawDataComponent'

        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)
        self.widget.setMinimumWidth(150)

        widget = QWidget()
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QGridLayout()
        widget.setLayout(layout)
        self.tagWidgets = {}
        self.widget.setWidget(widget)

        uriLabel = QLabel('URI')
        self.uriEdit = QLineEdit()
        self.uriEdit.setEnabled(False)

        nameLabel = QLabel('Name')
        self.nameEdit = QLineEdit()

        formatLabel = QLabel('Format')
        self.formatEdit = QLineEdit()

        dateLabel = QLabel('Date')
        self.dateEdit = QLineEdit()

        authorLabel = QLabel('Author')
        self.authorEdit = QLineEdit()

        tagsWidget = QWidget()
        self.tagsLayout = QGridLayout()
        self.tagsLayout.setContentsMargins(0,0,0,0)
        tagsWidget.setLayout(self.tagsLayout)

        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        saveButton.released.connect(self.saveButtonClicked)

        descLabel = QLabel('Description')
        descLabel.setObjectName('bi-metadata-title')
        tagsLabel = QLabel('Tags')
        tagsLabel.setObjectName('bi-metadata-title')

        metadataLabel = QLabel('Metadata')
        metadataLabel.setObjectName('bi-metadata-title')
        self.metadataWidget = BiDictViewer()

        layout.addWidget(descLabel, 0, 0, 1, 2)
        layout.addWidget(uriLabel, 1, 0)
        layout.addWidget(self.uriEdit, 1, 1)
        layout.addWidget(nameLabel, 2, 0)
        layout.addWidget(self.nameEdit, 2, 1)
        layout.addWidget(formatLabel, 3, 0)
        layout.addWidget(self.formatEdit, 3, 1)
        layout.addWidget(dateLabel, 4, 0)
        layout.addWidget(self.dateEdit, 4, 1)
        layout.addWidget(authorLabel, 5, 0)
        layout.addWidget(self.authorEdit, 5, 1)
        layout.addWidget(tagsLabel, 6, 0, 1, 2)
        layout.addWidget(tagsWidget, 7, 0, 1, 2)
        layout.addWidget(metadataLabel, 8, 0, 1, 2)
        layout.addWidget(self.metadataWidget.widget, 9, 0, 1, 2)
        layout.addWidget(saveButton, 10, 0, 1, 2)
        layout.addWidget(QWidget(), 11, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)
        layout.setAlignment(qtpy.QtCore.Qt.AlignTop)

    def saveButtonClicked(self):
        key_value_pairs = {}
        for key in self.tagWidgets:
            key_value_pairs[key] = self.tagWidgets[key].text()
        self._emit(BiRawDataComponent.SaveClicked,
                   [self.nameEdit.text(),
                    self.formatEdit.text(),
                    self.dateEdit.text(),
                    self.authorEdit.text(),
                    key_value_pairs])

    def callback_raw_data_loaded(self, emitter):
        self.nameEdit.setText(emitter.rawdata.name)
        self.formatEdit.setText(emitter.rawdata.format)
        self.dateEdit.setText(str(emitter.rawdata.date))
        self.authorEdit.setText(emitter.rawdata.author)
        self.uriEdit.setText(str(emitter.rawdata.uri))
        # metadata
        self.metadataWidget.import_data(emitter.rawdata.metadata)
        # tags
        for i in reversed(range(self.tagsLayout.count())): 
            self.tagsLayout.itemAt(i).widget().deleteLater()
        self.tagWidgets = {}
        row_idx = -1    
        for key in emitter.rawdata.key_value_pairs:
            label = QLabel(key)
            edit = QLineEdit(emitter.rawdata.key_value_pairs[key])
            row_idx += 1
            self.tagsLayout.addWidget(label, row_idx, 0) 
            self.tagsLayout.addWidget(edit, row_idx, 1)
            self.tagWidgets[key] = edit

    def callback_raw_data_saved(self, emitter):
        msgBox = QMessageBox()
        msgBox.setText("Metadata have been saved")
        msgBox.exec()  


class BiProcessedDataViewerComponent(BiComponent):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiProcessedDataViewer'

        self.dict_viewer = BiDictViewer()
        self.widget = self.dict_viewer.widget

    def callback_processed_data_loaded(self, emitter):
        # convert metadata to dict
        metadata = emitter.processeddata
        data = {}
        data['Common'] = {}
        data['Common']['URI'] = metadata.uri
        data['Common']['Name'] = metadata.name
        data['Common']['Author'] = metadata.author
        data['Common']['Date'] = metadata.date
        data['Common']['Format'] = metadata.format

        data["Inputs"] = {}
        for input in metadata.inputs:
            dict_data = {}
            dict_data['name'] = input.name
            dict_data['uri'] = input.uri
            dict_data['uuid'] = input.uuid
            dict_data['type'] = input.type
            data['Inputs'][f'input {input.name}'] = dict_data

        data['Output'] = metadata.output   

        data['Run info'] = {}
        data['Run info']['process'] = {}    
        data['Run info']['process']['name'] = emitter.rundata.process_name
        data['Run info']['process']['uri'] = emitter.rundata.process_uri

        data['Run info']['dataset'] = {}
        data['Run info']['dataset']['uri'] = emitter.rundata.processed_dataset.md_uri
        data['Run info']['dataset']['uuid'] = emitter.rundata.processed_dataset.uuid

        data['Run info']['inputs'] = {}
        for input in emitter.rundata.inputs:
            dict_data = {}
            dict_data['name'] = input.name
            dict_data['dataset'] = input.dataset
            dict_data['query'] = input.query
            dict_data['origin_output_name'] = input.origin_output_name
            data['Run info']['inputs'][f'input {input.name}'] = dict_data

        data['Run info']['parameters'] = {}
        for parameter in emitter.rundata.parameters:
            dict_data = {}
            dict_data['name'] = parameter.name
            dict_data['value'] = parameter.value
            data['Run info']['parameters'][f'{parameter.name}'] = dict_data

        # update viewer 
        self.dict_viewer.import_data(data)
            


class BiProcessedDataComponent(BiComponent):
    RunOpenClicked = 'run_open_clicked'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiProcessedDataComponent'

        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)
        self.widget.setMinimumHeight(150)
        self.widget.setMinimumWidth(150)

        widget = QWidget()
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("bi-side-bar")
        self.layout = QGridLayout()
        widget.setLayout(self.layout)
        self.widget.setWidget(widget)

        uriLabel = QLabel('URI')
        self.uriEdit = QLineEdit()
        self.uriEdit.setReadOnly(True)

        nameLabel = QLabel('Name')
        self.nameEdit = QLineEdit()
        self.nameEdit.setReadOnly(True)

        authorLabel = QLabel('Author')
        self.authorEdit = QLineEdit()
        self.authorEdit.setReadOnly(True)

        dateLabel = QLabel('Date')
        self.dateEdit = QLineEdit()
        self.dateEdit.setReadOnly(True)

        formatLabel = QLabel('Format')
        self.formatEdit = QLineEdit()
        self.formatEdit.setReadOnly(True)

        outlabelLabel = QLabel('Label')
        self.outlabelEdit = QLineEdit()
        self.outlabelEdit.setReadOnly(True)

        originLabel = QLabel('Parent')
        self.originEdit = QLineEdit()
        self.originEdit.setReadOnly(True)

        runLabel = QLabel('Run')
        runButton = QPushButton('Show info')
        runButton.setObjectName('btnDefault')
        runButton.released.connect(self.emit_run)

        descLabel = QLabel('Description')
        descLabel.setObjectName('bi-metadata-title')
        tagsLabel = QLabel('Key-value pairs')
        tagsLabel.setObjectName('bi-metadata-title')
        originTitleLabel = QLabel('Origin')
        originTitleLabel.setObjectName('bi-metadata-title')

        tagsWidget = QWidget()
        self.tagsLayout = QGridLayout()
        self.tagsLayout.setContentsMargins(0,0,0,0)
        tagsWidget.setLayout(self.tagsLayout)

        self.layout.addWidget(descLabel, 0, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(uriLabel, 1, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(self.uriEdit, 1, 1, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(nameLabel, 2, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(self.nameEdit, 2, 1, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(formatLabel, 3, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(self.formatEdit, 3, 1, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(dateLabel, 4, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(self.dateEdit, 4, 1, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(authorLabel, 5, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(self.authorEdit, 5, 1, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(tagsLabel, 6, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(outlabelLabel, 7, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(self.outlabelEdit, 7, 1, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(tagsWidget, 8, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(originTitleLabel, 9, 0, 1, 2,
                              qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(originLabel, 10, 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(self.originEdit, 10, 1, qtpy.QtCore.Qt.AlignTop)
        #self.layout.addWidget(runLabel, 11, 0, qtpy.QtCore.Qt.AlignTop)
        #self.layout.addWidget(runButton, 11, 1, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(QWidget(), 11, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)
        self.layout.setAlignment(qtpy.QtCore.Qt.AlignTop)

    def emit_run(self):
        self._emit(BiProcessedDataComponent.RunOpenClicked)

    def callback_processed_data_loaded(self, emitter):
        metadata = emitter.processeddata

        print('name = ', metadata.name)

        self.uriEdit.setText(metadata.uri)
        self.nameEdit.setText(metadata.name)
        self.authorEdit.setText(metadata.author)
        self.dateEdit.setText(metadata.date)
        self.formatEdit.setText(metadata.format)
        self.outlabelEdit.setText(metadata.output['label'])

        # tags
        orig = APIAccess.instance().get_origin(metadata)
        if orig:
            origin = orig
            for i in reversed(range(self.tagsLayout.count())): 
                self.tagsLayout.itemAt(i).widget().deleteLater()
            self.tagWidgets = {}
            row_idx = -1    
            for key in origin.key_value_pairs:
                label = QLabel(key)
                edit = QLineEdit(origin.key_value_pairs[key])
                edit.setReadOnly(True)
                row_idx += 1
                self.tagsLayout.addWidget(label, row_idx, 0) 
                self.tagsLayout.addWidget(edit, row_idx, 1)
                self.tagWidgets[key] = edit

        parent = APIAccess.instance().get_parent(metadata)
        if parent:
            self.originEdit.setText(parent.name)
        else:
            self.originEdit.setText("")  


class BiMetadataExperimentComponent(BiComponent):
    SaveClicked = 'metadata_save_clicked'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataExperimentComponent'

        self.widget = QWidget()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QGridLayout()
        self.widget.setLayout(layout)

        title = QLabel(self.widget.tr("Experiment informations"))
        title.setObjectName("bi-label-form-header1")
        title.setMaximumHeight(50)

        nameLabel = QLabel('Name')
        nameLabel.setObjectName('bi-label')
        self.nameEdit = QLineEdit()

        authorLabel = QLabel('Author')
        authorLabel.setObjectName('bi-label')
        self.authorEdit = QLineEdit()

        createddateLabel = QLabel('Created date')
        createddateLabel.setObjectName('bi-label')
        self.createddateEdit = QLineEdit()

        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btn-primary")
        saveButton.released.connect(self.saveButtonClicked)

        layout.addWidget(title, 0, 0, 1, 2)
        layout.addWidget(nameLabel, 1, 0)
        layout.addWidget(self.nameEdit, 1, 1)
        layout.addWidget(authorLabel, 2, 0)
        layout.addWidget(self.authorEdit, 2, 1)
        layout.addWidget(createddateLabel, 3, 0)
        layout.addWidget(self.createddateEdit, 3, 1)
        layout.addWidget(saveButton, 4, 0, 1, 2)
        layout.addWidget(QWidget(), 5, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)

    def saveButtonClicked(self):
        self._emit(BiMetadataExperimentComponent.SaveClicked,
                   [self.nameEdit.text(),
                   self.authorEdit.text(),
                   self.createddateEdit.text()]
                   )

    def callback_metadata_loaded(self, emitter):
        self.nameEdit.setText(emitter.experiment.name)
        self.authorEdit.setText(emitter.experiment.author)
        self.createddateEdit.setText(str(emitter.experiment.date))

    def callback_metadata_saved(self, emitter):
        msgBox = QMessageBox()
        msgBox.setText("Information have been saved")
        msgBox.exec()          


class BiMetadataRunComponent(BiComponent):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataRunComponent'

        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)
        self.widget.setMinimumWidth(150)

        widget = QWidget()
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("bi-side-bar")
        layout = QGridLayout()
        widget.setLayout(layout)
        self.widget.setWidget(widget)

        toolLabel = QLabel('Tool')
        self.toolEdit = QLineEdit()
        self.toolEdit.setEnabled(False)

        tooluriLabel = QLabel('Name')
        self.tooluriEdit = QLineEdit()
        self.tooluriEdit.setEnabled(False)

        parametersLabel = QLabel('Parameters')
        parametersLabel.setObjectName('bi-metadata-title')

        self.parametersTable = QTableWidget()

        inputsLabel = QLabel('Inputs')
        inputsLabel.setObjectName('bi-metadata-title')

        self.inputsTable = QTableWidget()

        tagsWidget = QWidget()
        self.tagsLayout = QGridLayout()
        self.tagsLayout.setContentsMargins(0,0,0,0)
        tagsWidget.setLayout(self.tagsLayout)

        layout.addWidget(toolLabel, 0, 0)
        layout.addWidget(self.toolEdit, 0, 1)
        layout.addWidget(tooluriLabel, 1, 0)
        layout.addWidget(self.tooluriEdit, 1, 1)
        layout.addWidget(parametersLabel, 2, 0, 1, 2)
        layout.addWidget(self.parametersTable, 3, 0, 1, 2)
        layout.addWidget(inputsLabel, 4, 0, 1, 2)
        layout.addWidget(self.inputsTable, 5, 0, 1, 2)
        layout.addWidget(QWidget(), 6, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)

    def callback_loaded(self, emitter):
        metadata = emitter.run.metadata

        self.toolEdit.setText(metadata.process_name)
        self.tooluriEdit.setText(metadata.process_uri)

        # parameters
        self.parametersTable.setColumnCount(2)
        self.parametersTable.setHorizontalHeaderLabels(["Name", "Value"])
        self.parametersTable.setRowCount(0)
        self.parametersTable.setRowCount(len(metadata.parameters))
        row_idx = 0
        for param in metadata.parameters:
            self.parametersTable.setItem(row_idx, 0, QTableWidgetItem(param.name))
            self.parametersTable.setItem(row_idx, 1, QTableWidgetItem(str(param.value)))
            row_idx += 1

        # inputs
        self.inputsTable.setColumnCount(3)
        self.inputsTable.setHorizontalHeaderLabels(["Name", "Dataset", "Query"])
        self.inputsTable.setRowCount(0)
        self.inputsTable.setRowCount(len(metadata.inputs))
        row_idx = 0
        for input in metadata.inputs:
            self.inputsTable.setItem(row_idx, 0, QTableWidgetItem(input.name))
            self.inputsTable.setItem(row_idx, 1, QTableWidgetItem(input.dataset))  
            self.inputsTable.setItem(row_idx, 2, QTableWidgetItem(input.query))  
            row_idx += 1                   
