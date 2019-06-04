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
                    BiExperimentToolBarComponent)
from processbrowser import BiProcessesContainer, BiProcessesModel, BiProcessesComponent, BiProcessesToolBarComponent
from processrunner import BiProcessMultiEditorContainer, BiProcessMultiEditorModel, BiProcessMultiEditorComponent, BiProcessMultiEditorToolBarComponent
from settings import BiSettingsAccess

class BiExperimentAppContainer(BiContainer):
    DataButtonClicked = "BiExperimentAppContainer::DataButtonClicked"
    ProcessButtonClicked = "BiExperimentAppContainer::ProcessButtonClicked"
    ExecButtonClicked = "BiExperimentAppContainer::ExecButtonClicked"

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
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)

        self.dataButton = QPushButton(self.widget.tr("Data"), self.widget)
        self.processesButton = QPushButton(self.widget.tr("Processes"), self.widget)
        self.execButton = QPushButton(self.widget.tr("Exec"), self.widget)

        self.dataButton.setCheckable(True)
        self.processesButton.setCheckable(True)
        self.execButton.setCheckable(True)

        self.dataButton.setObjectName("btnDefault")
        self.processesButton.setObjectName("btnDefault")
        self.execButton.setObjectName("btnDefault")

        layout.addWidget(self.dataButton)
        layout.addWidget(self.processesButton)
        layout.addWidget(self.execButton)

        self.dataButton.setChecked(True)
        self.execButton.setEnabled(False)

        self.dataButton.released.connect(self.dataButtonClicked)
        self.processesButton.released.connect(self.processesButtonClicked)
        self.execButton.released.connect(self.execButtonClicked)

    def update(self, container: BiContainer):
        if container.action == BiExperimentAppContainer.DataButtonClicked:
            self.dataButton.setChecked(True)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(False)
        elif container.action == BiExperimentAppContainer.ProcessButtonClicked:
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(True)
            self.execButton.setChecked(False)
        elif container.action == BiExperimentAppContainer.ExecButtonClicked:
            self.execButton.setEnabled(True)
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(True)

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
 
        # Models
        self.experimentModel = BiExperimentModel(self.experimentContainer)
        self.processesModel = BiProcessesModel(self.processesContainer)
        self.processMultiEditorModel = BiProcessMultiEditorModel(self.processMultiEditorContainer)
        self.experimentImportDataModel = BiExperimentImportDataModel(self.experimentImportDataContainer)

        # Components
        # main components
        self.experimentComponent = BiExperimentComponent(self.experimentContainer)
        self.processsesComponent = BiProcessesComponent(self.processesContainer)
        self.processMultiEditorComponent = BiProcessMultiEditorComponent(self.processMultiEditorContainer, self.experimentContainer)

        # popup components
        self.experimentInfoEditorComponent = BiExperimentInfoEditorComponent(self.experimentContainer)
        self.experimentTagsComponent = BiExperimentTagsComponent(self.experimentContainer)
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

        # initialization
        self.experimentContainer.projectFile = projectFile
        self.experimentContainer.notify(BiExperimentContainer.OriginModified)

        processesDir = BiSettingsAccess().instance.value("Processes", "processesdir")
        self.processesContainer.processesDir = processesDir
        self.processesContainer.notify(BiProcessesContainer.DirChanged)

        self.buildWidget()

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
        centralLayout.addWidget(self.experimentComponent.get_widget())
        centralLayout.addWidget(self.processsesComponent.get_widget())
        centralLayout.addWidget(self.processMultiEditorComponent.get_widget())
        self.experimentComponent.get_widget().setVisible(True)
        self.processsesComponent.get_widget().setVisible(False)
        self.processMultiEditorComponent.get_widget().setVisible(False)

        layout.addWidget(toolBar)
        layout.addWidget(centralArea)
        self.widget.setLayout(layout)
        self.widget.setObjectName("BiWidget")    

    def update(self, container: BiContainer):

        if container.action == BiExperimentAppContainer.DataButtonClicked:
            self.experimentComponent.get_widget().setVisible(True)
            self.processsesComponent.get_widget().setVisible(False)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponent.get_widget().setVisible(True)
            self.processesToolBarComponent.get_widget().setVisible(False)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)
            return
        if container.action == BiExperimentAppContainer.ProcessButtonClicked:
            self.experimentComponent.get_widget().setVisible(False)
            self.processsesComponent.get_widget().setVisible(True)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponen.get_widget().setVisible(False)
            self.processesToolBarComponent.get_widget().setVisible(True)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)
            return
        if container.action == BiExperimentAppContainer.ExecButtonClicked:
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

    def get_widget(self):
        return self.widget        

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    projectFileUrl = '/Users/sprigent/Documents/code/bioimageit/data/explorer/project1/experiment.md.json'
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