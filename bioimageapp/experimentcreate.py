from framework import BiContainer, BiModel, BiComponent
import bioimagepy.experiment as experimentpy

import PySide2.QtCore
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QFileDialog

class BiExperimentCreateContainer(BiContainer):
    CreateClicked = "BiExperimentCreateContainer::CreateClicked"
    CancelClicked = "BiExperimentCreateContainer::CancelClicked"
    ExperimentCreated = "BiExperimentCreateContainer::ExperimentCreated"
    ExperimentCreationError = "BiExperimentCreateContainer::ExperimentCreationError"

    def __init__(self):
        super(BiExperimentCreateContainer, self).__init__()
        self._object_name = 'BiExperimentCreateContainer'
        self.experiment_destination_dir = ''
        self.experiment_name = ''
        self.experiment_author = ''
        self.errorMessage = ''


class BiExperimentCreateModel(BiModel):    

    def __init__(self, container: BiExperimentCreateContainer):
        super(BiExperimentCreateModel, self).__init__()
        self._object_name = 'BiExperimentCreateModel'
        self.container = container
        self.container.addObserver(self)

    def update(self, container: BiContainer):
        if container.action == BiExperimentCreateContainer.CreateClicked:
            try:
                experimentpy.create(name=self.container.experiment_name, 
                                  author=self.container.experiment_author, 
                                  path=self.container.experiment_destination_dir) 
                self.container.notify(BiExperimentCreateContainer.ExperimentCreated)                   
            except FileNotFoundError as err:
                self.container.errorMessage = err
                self.container.notify(BiExperimentCreateContainer.ExperimentCreationError)


class BiExperimentCreateComponent(BiComponent):
    def __init__(self, container: BiExperimentCreateContainer):
        super(BiExperimentCreateComponent, self).__init__()
        self._object_name = 'BiExperimentCreateComponent'
        self.container = container
        self.container.addObserver(self)

        self.widget = QWidget()
        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Create experiment"))
        title.setObjectName("BiLabelFormHeader1")

        destinationLabel = QLabel(self.widget.tr("Destination"))
        self.destinationEdit = QLineEdit()
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
        self.container.notify(BiExperimentCreateContainer.CreateClicked)

    def reset(self):
        self.destinationEdit.setText('')
        self.nameEdit.setText('')
        self.authorEdit.setText('')    

    def setDestination(self, path: str):
        self.destinationEdit.setText(path)

    def update(self, contaier: BiContainer):
        pass

    def get_widget(self):
        return self.widget            
