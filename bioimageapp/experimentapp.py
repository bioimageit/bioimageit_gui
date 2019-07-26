import sys
import os

# add bioimagepy to path for dev
sys.path.append("../../bioimagepy/")

import PySide2.QtCore
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PySide2.QtGui import QIcon

from framework import BiComponent, BiContainer, BiModel, BiStates
from experiment import (BiExperimentContainer, BiExperimentModel, BiExperimentComponent, 
                    BiExperimentImportDataContainer, BiExperimentImportDataModel,
                    BiExperimentInfoEditorComponent, BiExperimentTagsComponent,
                    BiExperimentImportDataComponent, BiExperimentTitleToolBarComponent,
                    BiExperimentToolBarComponent, BiExperimentAddTagsContainer,
                    BiExperimentAddTagsModel, BiExperimentStates, BiExperimentImportDataStates)
from processbrowser import (BiProcessesBrowserContainer, BiProcessesBrowserModel, 
                            BiProcessesBrowserComponent, BiProcessesBrowserToolBarComponent,
                            BiProcessesBrowserStates)
from processrunner import (BiProcessMultiEditorContainer, BiProcessMultiEditorModel, 
                            BiProcessMultiEditorComponent, BiProcessMultiEditorToolBarComponent,
                            BiProcessMultiEditorStates)
from settings import BiSettingsAccess, BiSettingsComponent
from docviewer import BiDocViewerStates, BiDocViewerContainer, BiDocViewerModel, BiDocViewerComponent
from framework import BiAction

class BiExperimentAppStates(BiStates):
    DataButtonClicked = "BiExperimentAppContainer::DataButtonClicked"
    ProcessButtonClicked = "BiExperimentAppContainer::ProcessButtonClicked"
    ExecButtonClicked = "BiExperimentAppContainer::ExecButtonClicked"
    HelpButtonClicked = "BiExperimentAppContainer::HelpButtonClicked"


class BiExperimentAppContainer(BiContainer):
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._object_name = 'BiExperimentAppContainer'

        # states
        self.states = BiExperimentAppStates()


class BiExperimentAppToolBarComponent(BiComponent):
    def __init__(self, container: BiExperimentAppContainer):
        super(BiExperimentAppToolBarComponent, self).__init__()
        self._object_name = 'BiExperimentAppToolBarComponent'
        self.container = container
        self.container.register(self)
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

    def update(self, action: BiAction):
        if action.state == BiExperimentAppStates.HelpButtonClicked:
            self.helpButton.setChecked(True)
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(False)
        elif action.state == BiExperimentAppStates.DataButtonClicked:
            self.helpButton.setChecked(False)
            self.dataButton.setChecked(True)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(False)
        elif action.state == BiExperimentAppStates.ProcessButtonClicked:
            self.helpButton.setChecked(False)
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(True)
            self.execButton.setChecked(False)
        elif action.state == BiExperimentAppStates.ExecButtonClicked:
            self.helpButton.setChecked(False)
            self.execButton.setEnabled(True)
            self.dataButton.setChecked(False)
            self.processesButton.setChecked(False)
            self.execButton.setChecked(True)


    def helpButtonClicked(self):
        self.container.emit(BiExperimentAppStates.HelpButtonClicked)

    def dataButtonClicked(self):
        self.container.emit(BiExperimentAppStates.DataButtonClicked)

    def processesButtonClicked(self):
        self.container.emit(BiExperimentAppStates.ProcessButtonClicked)

    def execButtonClicked(self):
        self.container.emit(BiExperimentAppStates.ExecButtonClicked)

    def get_widget(self):
        return self.widget

class BiExperimentApp(BiComponent):
    def __init__(self, projectFile: str, useSettings: str = False):
        super(BiExperimentApp, self).__init__()
        self._object_name = 'BiExperimentApp'

        # containers
        self.experimentAppContainer = BiExperimentAppContainer()
        self.experimentContainer = BiExperimentContainer()
        self.processesContainer = BiProcessesBrowserContainer()
        self.processMultiEditorContainer = BiProcessMultiEditorContainer()
        self.experimentImportDataContainer = BiExperimentImportDataContainer()
        self.experimentAddTagsContainer = BiExperimentAddTagsContainer()
        self.docViewerContainer = BiDocViewerContainer()
 
        # Models
        self.experimentModel = BiExperimentModel(self.experimentContainer)
        self.processesModel = BiProcessesBrowserModel(self.processesContainer)
        self.processMultiEditorModel = BiProcessMultiEditorModel(self.processMultiEditorContainer)
        self.experimentImportDataModel = BiExperimentImportDataModel(self.experimentContainer, self.experimentImportDataContainer)
        self.experimentAddTagsModel = BiExperimentAddTagsModel(self.experimentContainer, self.experimentAddTagsContainer)
        self.docViewerModel = BiDocViewerModel(self.docViewerContainer)

        # Components
        # main components
        self.docViewerComponent = BiDocViewerComponent(self.docViewerContainer)
        self.experimentComponent = BiExperimentComponent(self.experimentContainer)
        self.processsesComponent = BiProcessesBrowserComponent(self.processesContainer)
        self.processMultiEditorComponent = BiProcessMultiEditorComponent(self.processMultiEditorContainer, self.experimentContainer)

        # popup components
        self.experimentInfoEditorComponent = BiExperimentInfoEditorComponent(self.experimentContainer)
        self.experimentTagsComponent = BiExperimentTagsComponent(self.experimentContainer, self.experimentAddTagsContainer)
        self.experimentImportDataComponent = BiExperimentImportDataComponent(self.experimentContainer, self.experimentImportDataContainer)
        self.settingsComponent = BiSettingsComponent()
        # toolbars
        self.experimentAppToolBarComponent = BiExperimentAppToolBarComponent(self.experimentAppContainer)
        self.experimentTitleToolBarComponent = BiExperimentTitleToolBarComponent(self.experimentContainer)
        self.experimentToolBarComponent = BiExperimentToolBarComponent(self.experimentContainer, useSettings)
        self.processesToolBarComponent = BiProcessesBrowserToolBarComponent(self.processesContainer)
        self.processMultiEditorToolBarComponent = BiProcessMultiEditorToolBarComponent(self.processMultiEditorContainer)

        # toolbars width
        self.experimentToolBarComponent.get_widget().setFixedWidth(350)
        self.processesToolBarComponent.get_widget().setFixedWidth(350)
        self.processesToolBarComponent.get_widget().setVisible(False)
        self.processMultiEditorToolBarComponent.get_widget().setFixedWidth(350)
        self.processMultiEditorToolBarComponent.get_widget().setVisible(False)

        # connections
        self.experimentAppContainer.register(self)
        self.processesContainer.register(self)
        self.experimentContainer.register(self)
        self.experimentImportDataContainer.register(self)

        self.buildWidget()

        # initialization
        self.experimentContainer.projectFile = projectFile
        self.experimentContainer.emit(BiExperimentStates.OriginModified)

        self.docViewerContainer.content_path = "bioimageapp/experimentdoc.json"
        self.docViewerContainer.emit(BiDocViewerStates.PathChanged)
        self.docViewerContainer.register(self)

        categoriesFile = BiSettingsAccess().instance.value("Processes", "Categories json") 
        processesDir = BiSettingsAccess().instance.value("Processes", "Processes directory")
        self.processesContainer.categoriesFile = categoriesFile
        self.processesContainer.processesDir = processesDir
        self.processesContainer.emit(BiProcessesBrowserStates.ProcessesDirChanged)

        

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
        

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            if self.experimentContainer.experiment.rawdataset().size() == 0:
                self.experimentAppContainer.emit(BiExperimentAppStates.HelpButtonClicked)
                return

        if action.state == BiExperimentAppStates.HelpButtonClicked:
            self.docViewerComponent.get_widget().setVisible(True)
            self.experimentComponent.get_widget().setVisible(False)
            self.processsesComponent.get_widget().setVisible(False)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponent.get_widget().setVisible(True)
            self.processesToolBarComponent.get_widget().setVisible(False)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)  
            return

        if action.state == BiExperimentAppStates.DataButtonClicked:
            self.docViewerComponent.get_widget().setVisible(False)
            self.experimentComponent.get_widget().setVisible(True)
            self.processsesComponent.get_widget().setVisible(False)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponent.get_widget().setVisible(True)
            self.processesToolBarComponent.get_widget().setVisible(False)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)
            return

        if action.state == BiExperimentAppStates.ProcessButtonClicked:
            self.docViewerComponent.get_widget().setVisible(False)
            self.experimentComponent.get_widget().setVisible(False)
            self.processsesComponent.get_widget().setVisible(True)
            self.processMultiEditorComponent.get_widget().setVisible(False)

            self.experimentToolBarComponent.get_widget().setVisible(False)
            self.processesToolBarComponent.get_widget().setVisible(True)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(False)
            return

        if action.state == BiExperimentAppStates.ExecButtonClicked:
            self.docViewerComponent.get_widget().setVisible(False)
            self.experimentComponent.get_widget().setVisible(False)
            self.processsesComponent.get_widget().setVisible(False)
            self.processMultiEditorComponent.get_widget().setVisible(True)

            self.experimentToolBarComponent.get_widget().setVisible(False)
            self.processesToolBarComponent.get_widget().setVisible(False)
            self.processMultiEditorToolBarComponent.get_widget().setVisible(True)
            return

        if action.state == BiExperimentStates.InfoClicked:
            self.experimentInfoEditorComponent.get_widget().show()
            return

        if action.state == BiExperimentStates.TagsClicked:
            self.experimentTagsComponent.get_widget().show()
            return

        if action.state == BiExperimentStates.ImportClicked:
            self.experimentImportDataComponent.get_widget().show()
            return

        if action.state == BiExperimentImportDataStates.DataImported:
            self.experimentImportDataComponent.get_widget().hide()
            self.experimentContainer.emit(BiExperimentStates.RawDataLoaded)
            self.experimentAppContainer.emit(BiExperimentAppStates.DataButtonClicked)
            return    

        if action.state == BiExperimentStates.RawDataLoaded:
            self.experimentImportDataComponent.get_widget().hide()
            return

        if action.state == BiProcessesBrowserStates.OpenProcess:
            self.processMultiEditorContainer.processAdd(self.processesContainer.get_clickedProcess())
            self.processMultiEditorContainer.emit(BiProcessMultiEditorStates.ProcessAdded)
            self.experimentAppContainer.emit(BiExperimentAppStates.ExecButtonClicked)
            return

        if action.state == 'BiExperimentDoc::ImportButtonClicked': 
            self.experimentImportDataComponent.get_widget().show()
            return 

        if action.state == 'BiExperimentDoc::TagButtonClicked': 
            self.experimentTagsComponent.get_widget().show()
            return   

        if action.state == BiExperimentStates.SettingsClicked:
            self.settingsComponent.get_widget().setVisible(True)
            return    

    def get_widget(self):
        return self.widget        

if __name__ == '__main__':

    # Create the Qt Application
    app = QApplication(sys.argv)
    
    projectFileUrl = '/Users/sprigent/Documents/code/bioimageit_old/data/explorer/myexperiment/experiment.md.json'
    settingsFileUrl = ''
    processesDir = ''
    if len(sys.argv) > 1 :
        projectFileUrl = sys.argv[1]

    if len(sys.argv) > 2 :
        settingsFileUrl = sys.argv[2]
    else:
        settingsFileUrl = "config/config.json"    

    access = BiSettingsAccess()
    settings = access.instance
    settings.file = settingsFileUrl
    settings.read()
    
    # Create and show the component
    component = BiExperimentApp(projectFileUrl, True)
    component.get_widget().show()
    # Run the main Qt loop
    #app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    app.setStyleSheet("file:///" + settings.value("General", "stylesheet"))
    app.setWindowIcon(QIcon("../bioimageapp/theme/default/icon.png"))
    sys.exit(app.exec_())