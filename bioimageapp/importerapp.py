import sys

# add bioimagepy to path for dev
sys.path.append("../bioimagepy/")

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSplitter, QHBoxLayout
from framework import (BiAction, BiComponent, BiContainer)                 
from settings import BiSettingsAccess
from importer import (BiImporterStates, BiImporterContainer, BiImporterModel, 
                      BiImporterSideBarComponent, BiImporterToolBarComponent,
                      BiImporterTableComponent, BiImportFormContainer, BiImportFormModel,
                      BiImportFormComponent
                      )
from experimentcreate import BiExperimentCreateStates, BiExperimentCreateContainer, BiExperimentCreateModel, BiExperimentCreateComponent


class BiImporterApp(BiComponent):
    def __init__(self, fields_file):
        super().__init__()
        self._object_name = 'BiImportApp'

        # container
        self.importerContainer = BiImporterContainer()
        self.importFormContainer = BiImportFormContainer()
        self.experimentCreateContainer = BiExperimentCreateContainer()
        
        # model
        self.importerModel = BiImporterModel(self.importerContainer)
        self.importFormModel = BiImportFormModel(self.importFormContainer)
        self.experimentCreateModel = BiExperimentCreateModel(self.experimentCreateContainer)

        # components
        self.toolBarComponent = BiImporterToolBarComponent(self.importerContainer)
        self.sideBarComponent = BiImporterSideBarComponent(self.importerContainer)
        self.tableComponent = BiImporterTableComponent(self.importerContainer)

        self.importFormComponent = BiImportFormComponent(self.importerContainer, fields_file)
        self.experimentCreateComponent = BiExperimentCreateComponent(self.experimentCreateContainer)
        
        # connections
        self.importerContainer.register(self)
        self.importFormContainer.register(self)
        self.experimentCreateContainer.register(self)

        # load settings
        settingsAccess = BiSettingsAccess().instance
        homeDir = settingsAccess.value("Browser", "Home")
        self.importerContainer.rootPath = homeDir
        self.importerContainer.currentPath = homeDir
        self.importerContainer.emit(BiImporterStates.DirectoryModified)

        # create the widget
        self.widget = QWidget()
        self.widget.setObjectName('bioImageApp')
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        layout.addWidget(self.toolBarComponent.get_widget())
        
        splitter = QSplitter()  
        layout.addWidget(splitter)

        self.sideBarComponent.get_widget().setMaximumWidth(200)
        splitter.addWidget(self.sideBarComponent.get_widget())
        splitter.addWidget(self.tableComponent.get_widget())

        splitter.setObjectName('BiImporterAppSplitter')


    def update(self, action : BiAction):
        if action.state == BiImporterStates.NewExperimentClicked:
            self.experimentCreateComponent.reset()
            self.experimentCreateComponent.setDestination(self.importerContainer.currentPath)
            self.experimentCreateComponent.get_widget().setVisible(True)
            return

        if action.state == BiImporterStates.ImportClicked:
            self.importFormComponent.get_widget().setVisible(True)
            return    

        if action.state == BiImporterStates.ImportDone:
            self.importFormComponent.get_widget().setVisible(False)
            self.importerContainer.emit(BiImporterStates.DirectoryModified)
            return

        if action.state == BiExperimentCreateStates.ExperimentCreated:
            self.experimentCreateComponent.get_widget().setVisible(False)
            self.importerContainer.emit(BiImporterStates.DirectoryModified)
            return


    def get_widget(self):
        return self.widget 


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    settingsFileUrl = ''
    if len(sys.argv) > 1 :
        settingsFileUrl = sys.argv[1]
    else:
        settingsFileUrl = "config/config.json" 

    access = BiSettingsAccess()
    settings = access.instance
    settings.file = settingsFileUrl
    settings.read()
    
    # Create and show the component
    component = BiImporterApp('config/import_fields.json')
    component.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("../bioimageapp/theme/default/icon.png"))
    sys.exit(app.exec_())
