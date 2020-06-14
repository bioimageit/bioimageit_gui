import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage, QPalette
from PySide2.QtCore import QFileInfo, QDir, Signal
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QGridLayout, QHBoxLayout, QToolButton, QSplitter, 
                               QLineEdit, QPushButton, QTextEdit, QMessageBox, QFileDialog)

from bioimageapp.core.framework import BiComponent, BiAction
from bioimageapp.metadata.states import BiRawDataStates, BiProcessedDataStates, BiMetadataExperimentStates
from bioimageapp.metadata.containers import BiRawDataContainer, BiProcessedDataContainer, BiMetadataExperimentContainer                               


class BiRawDataComponent(BiComponent):
    def __init__(self, container: BiRawDataContainer):
        super().__init__()
        self._object_name = 'BiMetadataRawDataComponent'
        self.container = container
        self.container.register(self)

        self.widget = QScrollArea()
        self.widget.setObjectName('BiWidget')
        #self.widget.setBackgroundRole(QPalette.Dark)
        self.widget.setWidgetResizable(True)
        self.widget.setMinimumWidth(150)

        widget = QWidget()
        widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("BiSideBar")
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
        descLabel.setObjectName('BiMetadataTitle')
        tagsLabel = QLabel('Tags')
        tagsLabel.setObjectName('BiMetadataTitle')

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
        layout.addWidget(saveButton, 8, 0, 1, 2)
        layout.addWidget(QWidget(), 9, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        layout.setAlignment(PySide2.QtCore.Qt.AlignTop)

        
    def saveButtonClicked(self):
        self.container.rawdata.metadata.name = self.nameEdit.text()
        self.container.rawdata.metadata.format = self.formatEdit.text()
        self.container.rawdata.metadata.date = self.dateEdit.text()
        self.container.rawdata.metadata.author = self.authorEdit.text()

        for key in self.tagWidgets:
            self.container.rawdata.metadata.tags[key] = self.tagWidgets[key].text()

        self.container.emit(BiRawDataStates.SaveClicked)

    def update(self, action: BiAction):
        if action.state == BiRawDataStates.Loaded:
            self.nameEdit.setText(self.container.rawdata.metadata.name)
            self.formatEdit.setText(self.container.rawdata.metadata.format)
            self.dateEdit.setText(self.container.rawdata.metadata.date)
            self.authorEdit.setText(self.container.rawdata.metadata.author)
            self.uriEdit.setText(self.container.rawdata.metadata.uri)

            # tags
            for i in reversed(range(self.tagsLayout.count())): 
                self.tagsLayout.itemAt(i).widget().deleteLater()
            self.tagWidgets = {}
            row_idx = -1    
            for key in self.container.rawdata.metadata.tags:
                label = QLabel(key)
                edit = QLineEdit(self.container.rawdata.metadata.tags[key])
                row_idx += 1
                self.tagsLayout.addWidget(label, row_idx, 0) 
                self.tagsLayout.addWidget(edit, row_idx, 1)
                self.tagWidgets[key] = edit

        if action.state == BiRawDataStates.Saved:
            msgBox = QMessageBox()
            msgBox.setText("Metadata have been saved")
            msgBox.exec()            

    def get_widget(self): 
        return self.widget  

class BiProcessedDataComponent(BiComponent):
    def __init__(self, container: BiProcessedDataContainer):
        super().__init__()
        self._object_name = 'BiMetadataProcessedDataComponent'
        self.container = container
        self.container.register(self)

        self.widget = QScrollArea()
        self.widget.setObjectName('BiWidget')
        #self.widget.setBackgroundRole(QPalette.Dark)
        self.widget.setWidgetResizable(True)
        self.widget.setMinimumWidth(150)

        widget = QWidget()
        widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("BiSideBar")
        layout = QGridLayout()
        widget.setLayout(layout)
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
        runButton.released.connect(self.emitRun)

        descLabel = QLabel('Description')
        descLabel.setObjectName('BiMetadataTitle')
        tagsLabel = QLabel('Tags')
        tagsLabel.setObjectName('BiMetadataTitle')
        originTitleLabel = QLabel('Origin')
        originTitleLabel.setObjectName('BiMetadataTitle')

        tagsWidget = QWidget()
        self.tagsLayout = QGridLayout()
        self.tagsLayout.setContentsMargins(0,0,0,0)
        tagsWidget.setLayout(self.tagsLayout)

        layout.addWidget(descLabel, 0, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(uriLabel, 1, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.uriEdit, 1, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(nameLabel, 2, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.nameEdit, 2, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(formatLabel, 3, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.formatEdit, 3, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(dateLabel, 4, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.dateEdit, 4, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(authorLabel, 5, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.authorEdit, 5, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(tagsLabel, 6, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(outlabelLabel, 7, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.outlabelEdit, 7, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(tagsWidget, 8, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(originTitleLabel, 9, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(originLabel, 10, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.originEdit, 10, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(runLabel, 11, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(runButton, 11, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(QWidget(), 12, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        layout.setAlignment(PySide2.QtCore.Qt.AlignTop)


    def emitRun(self):
        self.container.emit(BiProcessedDataStates.RunOpenClicked)

    def update(self, action: BiAction):
        if action.state == BiProcessedDataStates.Loaded:
            metadata = self.container.processeddata.metadata

            self.uriEdit.setText(metadata.uri)
            self.nameEdit.setText(metadata.name)
            self.authorEdit.setText(metadata.author)
            self.dateEdit.setText(metadata.date)
            self.formatEdit.setText(metadata.format)
            self.outlabelEdit.setText(metadata.output['label'])

            # tags
            orig = self.container.processeddata.get_origin()
            if orig:
                origin = orig.metadata
                for i in reversed(range(self.tagsLayout.count())): 
                    self.tagsLayout.itemAt(i).widget().deleteLater()
                self.tagWidgets = {}
                row_idx = -1    
                for key in origin.tags:
                    label = QLabel(key)
                    edit = QLineEdit(origin.tags[key])
                    edit.setReadOnly(True)
                    row_idx += 1
                    self.tagsLayout.addWidget(label, row_idx, 0) 
                    self.tagsLayout.addWidget(edit, row_idx, 1)
                    self.tagWidgets[key] = edit

            parent = self.container.processeddata.get_parent()
            if parent:
                self.originEdit.setText(parent.metadata.name)
            else:
                self.originEdit.setText("")    

    def get_widget(self): 
        return self.widget  

class BiMetadataExperimentComponent(BiComponent):
    def __init__(self, container: BiMetadataExperimentContainer):
        super().__init__()
        self._object_name = 'BiMetadataExperimentComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)

        layout = QGridLayout()
        self.widget.setLayout(layout)

        title = QLabel(self.widget.tr("Experiment informations"))
        title.setObjectName("BiLabelFormHeader1")
        title.setMaximumHeight(50)

        nameLabel = QLabel('Name')
        nameLabel.setObjectName('BiLabel')
        self.nameEdit = QLineEdit()

        authorLabel = QLabel('Author')
        authorLabel.setObjectName('BiLabel')
        self.authorEdit = QLineEdit()

        createddateLabel = QLabel('Created date')
        createddateLabel.setObjectName('BiLabel')
        self.createddateEdit = QLineEdit()

        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        saveButton.released.connect(self.saveButtonClicked)

        layout.addWidget(title, 0, 0, 1, 2)
        layout.addWidget(nameLabel, 1, 0)
        layout.addWidget(self.nameEdit, 1, 1)
        layout.addWidget(authorLabel, 2, 0)
        layout.addWidget(self.authorEdit, 2, 1)
        layout.addWidget(createddateLabel, 3, 0)
        layout.addWidget(self.createddateEdit, 3, 1)
        layout.addWidget(saveButton, 4, 0, 1, 2)
        layout.addWidget(QWidget(), 5, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)

    def saveButtonClicked(self):
        self.container.experiment.metadata.name = self.nameEdit.text()
        self.container.experiment.metadata.author = self.authorEdit.text()
        self.container.experiment.metadata.date = self.createddateEdit.text()
        self.container.emit(BiMetadataExperimentStates.SaveClicked)

    def update(self, action: BiAction):
        if action.state == BiMetadataExperimentStates.Loaded:
            self.nameEdit.setText(self.container.experiment.metadata.name)
            self.authorEdit.setText(self.container.experiment.metadata.author)
            self.createddateEdit.setText(self.container.experiment.metadata.date)

        if action.state == BiMetadataExperimentStates.Saved:
            msgBox = QMessageBox()
            msgBox.setText("Information have been saved")
            msgBox.exec()  

    def get_widget(self): 
        return self.widget    


class BiMetadataRunComponent(BiComponent):
    def __init__(self, container: BiRawDataContainer):
        super().__init__()
        self._object_name = 'BiMetadataRunComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()

    def update(self, action: BiAction):
        pass

    def get_widget(self): 
        return self.widget                        
