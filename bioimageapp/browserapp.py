import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSplitter, QHBoxLayout
from framework import (BiComponent, BiContainer)
from browser import (BiBrowserContainer, BiBrowserModel, BiBrowserToolBarComponent, BiBrowserShortCutsComponent, BiBrowserTableComponent, BiBrowserPreviewComponent)
from metadataeditor import BiMetadataEditorComponent, BiMetadataEditorContainer, BiMetadataEditorModel                   
from settings import BiSettingsAccess

class BiBrowserApp(BiComponent):
    def __init__(self):
        super(BiBrowserApp, self).__init__()
        self._object_name = 'BiBrowserApp'

        # container
        self.browserContainer = BiBrowserContainer()
        self.metadataEditorContainer = BiMetadataEditorContainer()
        
        # model
        self.browserModel = BiBrowserModel(self.browserContainer)
        self.metadataEditorModel = BiMetadataEditorModel(self.metadataEditorContainer)

        # components
        self.toolBarComponent = BiBrowserToolBarComponent(self.browserContainer)
        self.shortCutComponent = BiBrowserShortCutsComponent(self.browserContainer)
        self.tableComponent = BiBrowserTableComponent(self.browserContainer)
        self.previewComponent = BiBrowserPreviewComponent(self.browserContainer)

        self.metadataEditorComponent = BiMetadataEditorComponent(self.metadataEditorContainer)
        
        # connections
        self.browserContainer.addObserver(self)
        self.metadataEditorContainer.addObserver(self)

        # load settings
        settingsAccess = BiSettingsAccess().instance
        homeDir = settingsAccess.value("Browser", "home")
        self.browserContainer.currentPath = homeDir
        self.browserContainer.notify(BiBrowserContainer.DirectoryModified)

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

        splitterLeft.addWidget(self.shortCutComponent.get_widget())
        splitterLeft.addWidget(self.tableComponent.get_widget())

        splitterRight.addWidget(splitterLeft)
        splitterRight.addWidget(self.previewComponent.get_widget())

        splitterRight.setObjectName('BiBrowserAppSplitterRight')
        splitterLeft.setObjectName('BiBrowserAppSplitterLeft')
        
    def update(self, container: BiContainer):
        if container.action == BiBrowserContainer.OpenJson:
            self.metadataEditorContainer.file = self.browserContainer.doubleClickedFile()
            self.metadataEditorContainer.notify( BiMetadataEditorContainer.FileModified )
            self.metadataEditorComponent.get_widget().show()
            return

        if container.action == BiMetadataEditorContainer.JsonWrote:
            self.browserContainer.notify(BiBrowserContainer.RefreshClicked)
            return

        if container.action == BiBrowserContainer.NewExperimentClicked:
            #self.experimentCreateComponent.reset()
            #self.experimentCreateComponent.setDestination(self.browserContainer.currentPath)
            #self.experimentCreateComponent.get_widget().setVisible(true)
            return

        #if container.action == BiExperimentCreateContainer.ExperimentCreated):
        #    self.experimentCreateComponent.get_widget().setVisible(false)

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
    
    # load the settings
    settingsFileUrl = ""
    if len(sys.argv) > 1:
        settingsFileUrl = sys.argv[1]
    if settingsFileUrl == "":
        settingsFileUrl = "../bioimageit/data/explorer/config.json"

    access = BiSettingsAccess()
    settings = access.instance
    settings.file = settingsFileUrl
    settings.read()
    
    # Create and show the component
    component = BiBrowserApp()
    component.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    sys.exit(app.exec_())