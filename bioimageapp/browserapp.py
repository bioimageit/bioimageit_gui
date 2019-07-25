import sys

# add bioimagepy to path for dev
sys.path.append("../../bioimagepy/")

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSplitter, QHBoxLayout
from framework import (BiAction, BiComponent, BiContainer)
from browser import (BiBrowserStates, BiBrowserContainer, BiBrowserModel, BiBrowserToolBarComponent, BiBrowserShortCutsComponent, BiBrowserTableComponent, BiBrowserPreviewComponent)
from metadataeditor import BiMetadataEditorStates, BiMetadataEditorComponent, BiMetadataEditorContainer, BiMetadataEditorModel                   
from settings import BiSettingsAccess
from experimentcreate import BiExperimentCreateStates, BiExperimentCreateContainer, BiExperimentCreateModel, BiExperimentCreateComponent


class BiBrowserApp(BiComponent):
    def __init__(self, useExperimentProcess = True):
        super().__init__()
        self._object_name = 'BiBrowserApp'

        # container
        self.browserContainer = BiBrowserContainer()
        self.metadataEditorContainer = BiMetadataEditorContainer()
        self.experimentCreateContainer = BiExperimentCreateContainer()
        
        # model
        self.browserModel = BiBrowserModel(self.browserContainer, useExperimentProcess)
        self.metadataEditorModel = BiMetadataEditorModel(self.metadataEditorContainer)
        self.experimentCreateModel = BiExperimentCreateModel(self.experimentCreateContainer)

        # components
        self.toolBarComponent = BiBrowserToolBarComponent(self.browserContainer)
        self.shortCutComponent = BiBrowserShortCutsComponent(self.browserContainer)
        self.tableComponent = BiBrowserTableComponent(self.browserContainer)
        self.previewComponent = BiBrowserPreviewComponent(self.browserContainer)

        self.metadataEditorComponent = BiMetadataEditorComponent(self.metadataEditorContainer)
        self.experimentCreateComponent = BiExperimentCreateComponent(self.experimentCreateContainer)
        
        # connections
        self.browserContainer.register(self)
        self.metadataEditorContainer.register(self)
        self.experimentCreateContainer.register(self)

        # load settings
        settingsAccess = BiSettingsAccess().instance
        homeDir = settingsAccess.value("Browser", "Home")
        self.browserContainer.currentPath = homeDir
        self.browserContainer.emit(BiBrowserStates.DirectoryModified)

        self.browserModel.loadBookmarks(settingsAccess.value("Browser", "bookmarks"))
        self.shortCutComponent.reloadBookmarks()

        # create the widget
        self.widget = QWidget()
        self.widget.setObjectName('bioImageApp')
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        splitters = QWidget()
        splittersLayout = QHBoxLayout()
        splittersLayout.setContentsMargins(0,0,0,0)
        splitters.setLayout(splittersLayout)

        layout.addWidget(self.toolBarComponent.get_widget())
        layout.addWidget(splitters)

        splitterLeft = QSplitter()  
        splitterRight = QSplitter()
        splittersLayout.addWidget(splitterRight)

        self.shortCutComponent.get_widget().setMaximumWidth(300)
        splitterLeft.addWidget(self.shortCutComponent.get_widget())
        splitterLeft.addWidget(self.tableComponent.get_widget())

        splitterRight.addWidget(splitterLeft)
        splitterRight.addWidget(self.previewComponent.get_widget())
        self.previewComponent.get_widget().setVisible(False)

        splitterRight.setObjectName('BiBrowserAppSplitterRight')
        splitterLeft.setObjectName('BiBrowserAppSplitterLeft')
        
    def update(self, action: BiAction):
        if action.state == BiBrowserStates.OpenJson:
            self.metadataEditorContainer.file = self.browserContainer.doubleClickedFile()
            self.metadataEditorContainer.emit( BiMetadataEditorStates.FileModified )
            self.metadataEditorComponent.get_widget().show()
            return

        if action.state == BiMetadataEditorStates.JsonWrote:
            self.browserContainer.emit(BiBrowserStates.RefreshClicked)
            return

        if action.state == BiBrowserStates.NewExperimentClicked:
            self.experimentCreateComponent.reset()
            self.experimentCreateComponent.setDestination(self.browserContainer.currentPath)
            self.experimentCreateComponent.get_widget().setVisible(True)
            return

        if action.state == BiExperimentCreateStates.ExperimentCreated:
            self.experimentCreateComponent.get_widget().setVisible(False)

        
        #    QProcess *openProcess = new QProcess(this);
        #    connect(openProcess, SIGNAL(errorOccurred(QProcess::ProcessError)), this, SLOT(errorOccurred(QProcess::ProcessError)));
        #    QString program = biSettingsAccess::instance()->settings()->value("Browser", "experiment editor");

        #    QString mdfileUrl = m_experimentCreateContainer->experiment()->mdFileUrl();
        #    program += " " + mdfileUrl;
        #    openProcess->startDetached(program);
        #    return
   
    def get_widget(self):
        return self.widget 

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    settingsFileUrl = ''
    if len(sys.argv) > 1 :
        settingsFileUrl = sys.argv[2]
    else:
        settingsFileUrl = "config/config.json" 

    access = BiSettingsAccess()
    settings = access.instance
    settings.file = settingsFileUrl
    settings.read()
    
    # Create and show the component
    component = BiBrowserApp()
    component.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("../bioimageapp/theme/default/icon.png"))
    sys.exit(app.exec_())