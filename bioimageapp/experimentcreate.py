from framework import BiStates, BiAction, BiContainer, BiModel, BiComponent
import bioimagepy.experiment as experimentpy

import PySide2.QtGui
import PySide2.QtCore
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QFileDialog, QSizePolicy

class BiExperimentCreateStates(BiStates):
    CreateClicked = "BiExperimentCreateStates.CreateClicked"
    CancelClicked = "BiExperimentCreateStates.CancelClicked"
    ExperimentCreated = "BiExperimentCreateStates.ExperimentCreated"
    ExperimentCreationError = "BiExperimentCreateStates.ExperimentCreationError"

class BiExperimentCreateContainer(BiContainer):


    def __init__(self):
        super(BiExperimentCreateContainer, self).__init__()
        self._object_name = 'BiExperimentCreateContainer'

        # states
        self.states = BiExperimentCreateStates()

        # data
        self.experiment_destination_dir = ''
        self.experiment_name = ''
        self.experiment_author = ''
        self.errorMessage = ''
        self.experiment_dir = ""


class BiExperimentCreateModel(BiModel):    

    def __init__(self, container: BiExperimentCreateContainer):
        super(BiExperimentCreateModel, self).__init__()
        self._object_name = 'BiExperimentCreateModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):

        if action.state == BiExperimentCreateStates.CreateClicked:
            try:
                experiment = experimentpy.create(name=self.container.experiment_name, 
                                                          author=self.container.experiment_author, 
                                                          path=self.container.experiment_destination_dir) 

                self.container.experiment_dir = experiment.md_file_path()
                self.container.emit(BiExperimentCreateStates.ExperimentCreated)                   
            except FileNotFoundError as err:
                self.container.errorMessage = err
                self.container.emit(BiExperimentCreateStates.ExperimentCreationError)


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
        self.destinationEdit = QLineEdit()
        self.destinationEdit.setText(default_destination)
        browseButton = QPushButton(self.widget.tr("..."))
        browseButton.setObjectName("BiBrowseButton")
        browseButton.released.connect(self.browseButtonClicked)

        nameLabel = QLabel(self.widget.tr("Experiment name"))
        self.nameEdit = QLineEdit()

        authorLabel = QLabel(self.widget.tr("Author"))
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
