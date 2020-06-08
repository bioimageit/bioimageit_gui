import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import QFileInfo, QDir, Signal
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QGridLayout, QHBoxLayout, QToolButton, QSplitter, 
                               QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                               QFileDialog, QTabWidget)

from bioimageapp.core.framework import BiComponent, BiAction
from bioimageapp.experiment.states import BiExperimentStates, BiExperimentCreateStates
from bioimageapp.experiment.containers import BiExperimentContainer, BiExperimentCreateContainer                             

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

        # fill widget
        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignLeft)

    def importButtonClicked(self):
        self.container.emit(BiExperimentStates.ImportClicked)

    def tagButtonClicked(self):
        self.container.emit(BiExperimentStates.TagClicked)    

    def processButtonClicked(self):
        self.container.emit(BiExperimentStates.ProcessClicked)  

    def update(self, action: BiAction):
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
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)

        tabWidget.addTab(QLabel("Import file"), 'Import file')
        tabWidget.addTab(QLabel("Import dir"), 'Import directory')


    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget


class BiExperimentTagComponent(BiComponent):        
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentTagComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)

        tabWidget.addTab(QLabel("add tag"), 'Manual tags')
        tabWidget.addTab(QLabel("From name"), 'Tag extracting words from filename')
        tabWidget.addTab(QLabel("From separators"), 'Tag using separator from filename')


    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget    