import sys
import os

import PySide2.QtCore
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PySide2.QtGui import QIcon

from framework import BiComponent, BiContainer, BiModel
from experiment import (BiExperimentContainer, BiExperimentModel, BiExperimentComponent, 
                    BiExperimentImportDataContainer, BiExperimentImportDataModel,
                    BiExperimentInfoEditorComponent, BiExperimentTagsComponent,
                    BiExperimentImportDataComponent, BiExperimentTitleToolBarComponent,
                    BiExperimentToolBarComponent, BiExperimentAddTagsContainer,
                    BiExperimentAddTagsModel)
from processbrowser import BiProcessesContainer, BiProcessesModel, BiProcessesComponent, BiProcessesToolBarComponent
from processrunner import BiProcessMultiEditorContainer, BiProcessMultiEditorModel, BiProcessMultiEditorComponent, BiProcessMultiEditorToolBarComponent
from settings import BiSettingsAccess
from docviewer import BiDocViewerContainer, BiDocViewerModel, BiDocViewerComponent


class BiExperimentAppContainer(BiContainer):
    DataButtonClicked = "BiExperimentAppContainer::DataButtonClicked"
    ProcessButtonClicked = "BiExperimentAppContainer::ProcessButtonClicked"
    ExecButtonClicked = "BiExperimentAppContainer::ExecButtonClicked"
    HelpButtonClicked = "BiExperimentAppContainer::HelpButtonClicked"

    def __init__(self):
        super(BiExperimentAppContainer, self).__init__()
        self._object_name = 'BiExperimentAppContainer'


class BiExperimentAppToolBarComponent(BiComponent):
    def __init__(self, container: BiExperimentAppContainer):
        super(BiExperimentAppToolBarComponent, self).__init__()
        self._object_name = 'BiExperimentAppToolBarComponent'
        self.container = container
        self.container.addObserver(self)
        self.buildWidget()

    def buildWidget(self):
        self.widget = QWidget()
        self.widget.setObjectName("BiToolBar")
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)

        self.helpButton = QPushButton(self.widget.tr("Help"), self.widget)
        self.dataButton = QPushButton(self.widget.tr("Data"), self.widget)
        self.processesButton = QPushButton(self.widget.tr("Processes"), self.widget)
        self.execButton = QPushButton(self.widget.tr("Exec"), self.widget)

        self.helpButton.setCheckable(True)
        self.dataButton.setCheckable(True)
        self.processesButton.setCheckable(True)
        self.execButton.setCheckable(True)

        self.helpButton.setObjectName("btnDefaultLeft")
        self.dataButton.setObjectName("btnDefaultCentral")
        self.processesButton.setObjectName("btnDefaultCentral")
        self.execButton.setObjectName("btnDefaultRight")

        layout.addWidget(self.helpButton)
        layout.addWidget(self.dataButton)
        layout.addWidget(self.processesButton)
        layout.addWidget(self.execButton)

        self.dataButton.setChecked(True)
        self.execButton.setEnabled(False)

        self.helpButton.released.connect(self.helpButtonClicked)
        self.dataButton.released.connect(self.dataButtonClicked)
        self.processesButton.released.connect(self.processesButtonClicked)
        self.execButton.released.connect(self.execButtonClicked)

    def update(self, container: BiContainer):
        if container.action == BiExperimentAppContainer.HelpButtonClicked:
            self.helpButton.setChecked(True)
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(False)
        elif container.action == BiExperimentAppContainer.DataButtonClicked:
            self.helpButton.setChecked(False)
            self.dataButton.setChecked(True)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(False)
        elif container.action == BiExperimentAppContainer.ProcessButtonClicked:
            self.helpButton.setChecked(False)
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(True)
            self.execButton.setChecked(False)
        elif container.action == BiExperimentAppContainer.ExecButtonClicked:
            self.helpButton.setChecked(False)
            self.execButton.setEnabled(True)
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(True)


    def helpButtonClicked(self):
        self.container.notify(BiExperimentAppContainer.HelpButtonClicked)

    def dataButtonClicked(self):
        self.container.notify(BiExperimentAppContainer.DataButtonClicked)

    def processesButtonClicked(self):
        self.container.notify(BiExperimentAppContainer.ProcessButtonClicked)

    def execButtonClicked(self):
        self.container.notify(BiExperimentAppContainer.ExecButtonClicked)

    def get_widget(self):
        return self.widget

class BiExperimentApp(BiComponent):
    def __init__(self, projectFile: str):
        super(BiExperimentApp, self).__init__()
        self._object_name = 'BiExperimentApp'

        # containers
        self.experimentAppContainer = BiExperimentAppContainer()
        self.experimentContainer = BiExperimentContainer()
        self.processesContainer = BiProcessesContainer()
        self.processMultiEditorContainer = BiProcessMultiEditorContainer()
        self.experimentImportDataContainer = BiExperimentImportDataContainer()
        self.experimentAddTagsContainer = BiExperimentAddTagsContainer()
        self.docViewerContainer = BiDocViewerContainer()
 
        # Models
        self.experimentModel = BiExperimentModel(self.experimentContainer)
        self.processesModel = BiProcessesModel(self.processesContainer)
        self.processMultiEditorModel = BiProcessMultiEditorModel(self.processMultiEditorContainer)
        self.experimentImportDataModel = BiExperimentImportDataModel(self.experimentContainer, self.experimentImportDataContainer)
        self.experimentAddTagsModel = BiExperimentAddTagsModel(self.experimentContainer, self.experimentAddTagsContainer)
        self.docViewerModel = BiDocViewerModel(self.docViewerContainer)

        # Components
        # main components
        self.docViewerComponent = BiDocViewerComponent(self.docViewerContainer)
        self.experimentComponent = BiExperimentComponent(self.experimentContainer)
        self.processsesComponent = BiProcessesComponent(self.processesContainer)
        self.processMultiEditorComponent = BiProcessMultiEditorComponent(self.processMultiEditorContainer, self.experimentContainer)

        # popup components
        self.experimentInfoEditorComponent = BiExperimentInfoEditorComponent(self.experimentContainer)
        self.experimentTagsComponent = BiExperimentTagsComponent(self.experimentContainer, self.experimentAddTagsContainer)
        self.experimentImportDataComponent = BiExperimentImportDataComponent(self.experimentContainer, self.experimentImportDataContainer)

        # toolbars
        self.experimentAppToolBarComponent = BiExperimentAppToolBarComponent(self.experimentAppContainer)
        self.experimentTitleToolBarComponent = BiExperimentTitleToolBarComponent(self.experimentContainer)
        self.experimentToolBarComponent = BiExperimentToolBarComponent(self.experimentContainer)
        self.processesToolBarComponent = BiProcessesToolBarComponent(self.processesContainer)
        self.processMultiEditorToolBarComponent = BiProcessMultiEditorToolBarComponent(self.processMultiEditorContainer)

        # connections
        self.experimentAppContainer.addObserver(self)
        self.processesContainer.addObserver(self)
        self.experimentContainer.addObserver(self)
        self.experimentImportDataContainer.addObserver(self)

        self.buildWidget()

        # initialization
        self.experimentContainer.projectFile = projectFile
        self.experimentContainer.notify(BiExperimentContainer.OriginModified)

        self.docViewerContainer.content_path = "bioimageapp/experimentdoc.json"
        self.docViewerContainer.notify(BiDocViewerContainer.PathChanged)
        self.docViewerContainer.addObserver(self)

        processesDir = BiSettingsAccess().instance.value("Processes", "processesdir")
        self.processesContainer.processesDir = processesDir
        self.processesContainer.notify(BiProcessesContainer.DirChanged)

        

    def buildWidget(self):
        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # tool bar area
        toolBar = QWidget(self.widget)
        toolBar.setObjectName("BiToolBar")
        toolBarLayout = QHBoxLayout()
        toolBarLayout.setContentsMargins(0,0,0,0)
        toolBar.setLayout(toolBarLayout)
        toolBarLayout.setSpacing(2)
        toolBarLayout.addWidget(self.experimentToolBarComponent.get_widget())
        toolBarLayout.addWidget(self.processesToolBarComponent.get_widget())
        toolBarLayout.addWidget(self.processMultiEditorToolBarComponent.get_widget())
        toolBarLayout.addWidget(QWidget(self.widget), 1, PySide2.QtCore.Qt.AlignCenter)
        toolBarLayout.addWidget(self.experimentAppToolBarComponent.get_widget())
        toolBarLayout.addWidget(QWidget(self.widget), 1, PySide2.QtCore.Qt.AlignCenter)
        toolBarLayout.addWidget(self.experimentTitleToolBarComponent.get_widget(), 0, PySide2.QtCore.Qt.AlignRight)
        toolBar.setLayout(toolBarLayout)

        # central area
        centralArea = QWidget(self.widget)
        centralLayout = QHBoxLayout()
        centralLayout.setContentsMargins(0,0,0,0)
        centralArea.setLayout(centralLayout)
        centralLayout.addWidget(self.docViewerComponent.get_widget())
        centralLayout.addWidget(self.experimentComponent.get_widget())
        centralLayout.addWidget(self.processsesComponent.get_widget())
        centralLayout.addWidget(self.processMultiEditorComponent.get_widget())
        self.docViewerComponent.get_widget().setVisible(False)
        self.experimentComponent.get_widget().setVisible(True)
        self.processsesComponent.get_widget().setVisible(False)
        self.processMultiEditorComponent.get_widget().setVisible(False)

        layout.addWidget(toolBar)
        layout.addWidget(centralArea)
        self.widget.setLayout(layout)
        self.widget.setObjectName("BiWidget")    

    def update(self, container: BiContainer):
        if container.action == BiExperimentContainer.Loaded:
            if self.experimentContainer.experiment.rawdataset().size() == 0:
                self.experimentAppContainer.notify(BiExperimentAppContainer.HelpButtonClicked)
                return

        if container.action == BiExperimentAppContainer.HelpButtonClicked:
            self.docViewerComponent.get_widget().setVisible(True)
            self.experimentComponent.get_widget().setVisible(False)
            self.processsesComponent.get_widget().setVisible(False)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponent.get_widget().setVisible(True)
            self.processesToolBarComponent.get_widget().setVisible(False)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)  
            return

        if container.action == BiExperimentAppContainer.DataButtonClicked:
            self.docViewerComponent.get_widget().setVisible(False)
            self.experimentComponent.get_widget().setVisible(True)
            self.processsesComponent.get_widget().setVisible(False)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponent.get_widget().setVisible(True)
            self.processesToolBarComponent.get_widget().setVisible(False)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)
            return

        if container.action == BiExperimentAppContainer.ProcessButtonClicked:
            self.docViewerComponent.get_widget().setVisible(False)
            self.experimentComponent.get_widget().setVisible(False)
            self.processsesComponent.get_widget().setVisible(True)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponen.get_widget().setVisible(False)
            self.processesToolBarComponent.get_widget().setVisible(True)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)
            return

        if container.action == BiExperimentAppContainer.ExecButtonClicked:
            self.docViewerComponent.get_widget().setVisible(False)
            self.experimentComponent.get_widget().setVisible(False)
            self.processsesComponent.get_widget().setVisible(False)
            self.processMultiEditorComponent.get_widget().setVisible(True)

            self.experimentToolBarComponent.get_widget().setVisible(False)
            self.processesToolBarComponent.get_widget().setVisible(False)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(True)
            return

        if container.action == BiExperimentContainer.InfoClicked:
            self.experimentInfoEditorComponent.get_widget().show()
            return

        if container.action == BiExperimentContainer.TagsClicked:
            self.experimentTagsComponent.get_widget().show()
            return

        if container.action == BiExperimentContainer.ImportClicked:
            self.experimentImportDataComponent.get_widget().show()
            return

        if container.action == BiExperimentContainer.RawDataLoaded:
            self.experimentImportDataComponent.get_widget().hide()
            return

        if container.action == BiProcessesContainer.OpenProcess:
            self.processMultiEditorContainer.processAdd(self.processesContainer.clickedProcess())
            self.processMultiEditorContainer.notify(BiProcessMultiEditorContainer.ProcessAdded)
            self.experimentAppContainer.notify(BiExperimentAppContainer.ExecButtonClicked)
            return

        if container.action == 'BiExperimentDoc::ImportButtonClicked': 
            self.experimentImportDataComponent.get_widget().show()
            return 

        if container.action == 'BiExperimentDoc::TagButtonClicked': 
            self.experimentTagsComponent.get_widget().show()
            return       

    def get_widget(self):
        return self.widget        

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    projectFileUrl = '/Users/sprigent/Documents/code/bioimageit/data/explorer/myexperiment/experiment.md.json'
    settingsFileUrl = ''
    processesDir = ''
    if len(sys.argv) > 1 :
        projectFileUrl = sys.argv[1]

    if len(sys.argv) > 2 :
        settingsFileUrl = sys.argv[2]
    else:
        settingsFileUrl = "../bioimageit/data/explorer/config.json"    

    access = BiSettingsAccess()
    settings = access.instance
    settings.file = settingsFileUrl
    settings.read()
    
    # Create and show the component
    component = BiExperimentApp(projectFileUrl)
    component.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("../bioimageapp/theme/default/icon.png"))
    sys.exit(app.exec_())