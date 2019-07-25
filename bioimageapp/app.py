import sys
import os

from shutil import copyfile

from PySide2.QtGui import QIcon
from PySide2.QtCore import QFile
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

from framework import BiComponent, BiContainer, BiStates, BiAction
from settings import BiSettings, BiSettingsAccess, BiBookmarks, BiSettingsComponent
from tiles import BiTile, BiTilesStates, BiTilesContainer, BiTilesComponents

class bioImageApp(BiComponent):
    def __init__(self):
        super(bioImageApp, self).__init__()
        self._object_name = 'bioImageApp'

        # init settings
        self.init_settings()

        # container
        self.tilesContainer = BiTilesContainer()

        # components
        self.tilesComponent = BiTilesComponents(self.tilesContainer)

        # connections
        self.tilesContainer.register(self)

        # initialize
        self.init_settings()
        self.build_widget()
        self.build_tiles()
        

    def build_widget(self):

        # create the widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        layout.addWidget(self.tilesComponent.get_widget())


    def build_tiles(self):

        iconsDir = os.path.dirname(BiSettingsAccess().instance.value("General", "stylesheet"))
        self.tilesComponent.addTilesBoard( os.path.join(iconsDir,"home_negative.svg"))

        # tiles applications
        self.tilesComponent.addSection("Applications")

        newExpTileInfo = BiTile("BiExperimentCreateGui", "New Experiment", "Create a new experiment", os.path.join(iconsDir, "plus-white-symbol.svg"))
        self.tilesComponent.addTile("Applications", newExpTileInfo) 

        browserTileInfo = BiTile("BiBrowserApp", "Browser", "File browser", os.path.join(iconsDir, "open-folder_negative.svg"))
        self.tilesComponent.addTile("Applications", browserTileInfo)

        settingsTileInfo = BiTile("BiSettingsApp", "Settings", "Application settings", os.path.join(iconsDir, "cog-wheel-silhouette_negative.svg"))
        self.tilesComponent.addTile("Applications", settingsTileInfo)

        # tiles Shortcuts
        self.tilesComponent.addSection("Bookmarks")
        bookmarksFile = BiSettingsAccess.instance.value("Browser", "bookmarks")
        bookmarks = BiBookmarks(bookmarksFile)
        bookmarks.read()

        if "bookmarks" in bookmarks.bookmarks:
            for bookmark in bookmarks.bookmarks["bookmarks"]:
                expTileInfo = BiTile("BiExperimentApp " + bookmark["url"], bookmark["name"], bookmark["name"], os.path.join(iconsDir, "folder-white-shape_negative.svg"))
                self.tilesComponent.addTile("Bookmarks", expTileInfo)


    def init_settings(self):
        data_dir = BiSettingsAccess.instance.value("Browser", "Home")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)  

        # create bookmarks if not exists
        copyfile("config/bookmarks.json.sample", os.path.join(data_dir, "bookmarks.json"))

        sys.path.append(BiSettingsAccess.instance.value("General", "BioImagePy"))
            

    def update(self, action: BiAction):
        if action.state == BiTilesStates.OpenAppClicked:
            self.openApp(self.tilesContainer.openApp)
            return

        if action.state == "BiBrowserStates.ItemDoubleClicked":
    
            print("open experiment signal clicked")
            browserContainer = action.parent
            if browserContainer:
                row = browserContainer.doubleClickedRow()
                dcFile = browserContainer.file(row)

                experimentFilePath = os.path.join(dcFile.path(), dcFile.fileName())
                from experimentapp import BiExperimentApp
                experimentComponent = BiExperimentApp(experimentFilePath)

                iconsDir = os.path.dirname(BiSettingsAccess().instance.value("General", "stylesheet"))
                info = BiTile("BiExperimentApp", "experiment", "experiment", os.path.join(iconsDir, "folder-white-shape_negative.svg"))

                self.tilesComponent.openApp(info, experimentComponent.get_widget())
    
            return


    def openApp(self, info: BiTile):

        if info.action == "BiSettingsApp":

            settingComponent = BiSettingsComponent()
            self.tilesComponent.openApp(info, settingComponent.get_widget())
    
        elif info.action == "BiBrowserApp":

            from browserapp import BiBrowserApp
            browserApp = BiBrowserApp()
            browserApp.browserContainer.register(self)
            self.tilesComponent.openApp(info, browserApp.get_widget())
        
        elif info.action().startsWith("BiExperimentApp"):
        
            ShortCutPath = info.action.replace("BiExperimentApp ", "")
            experimentFilePath = os.path.join(ShortCutPath, "experiment.md.json")

            file = QFile(experimentFilePath)
            if (file.exists()):
                from experimentapp import BiExperimentApp
                experimentComponent = BiExperimentApp(experimentFilePath)
                self.tilesComponent.openApp(info, experimentComponent.get_widget())
            else:
                from browserapp import BiBrowserApp
                browserApp = BiBrowserApp()
                browserApp.browserContainer().register(self)
                browserApp.setPath(ShortCutPath)
                self.tilesComponent.openApp(info, browserApp.get_widget())
        
        elif info.action() == "BiExperimentCreateGui":
            from experimentcreate import BiExperimentCreateContainer, BiExperimentCreateModel, BiExperimentCreateComponent
            experimentCreateContainer = BiExperimentCreateContainer()
            experimentCreateModel = BiExperimentCreateModel(experimentCreateContainer)
            experimentCreateModel.nowarning()
            experimentCreateComponent = BiExperimentCreateComponent(experimentCreateContainer)
            self.tilesComponent.openApp(info, experimentCreateComponent.get_widget())
        

    def get_widget(self):
        return self.widget 



if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Get the config file
    settingsFileUrl = ''
    if len(sys.argv) > 1 :
        settingsFileUrl = sys.argv[1]
    else:
        settingsFileUrl = "config/config.json"    

    access = BiSettingsAccess()
    settings = access.instance
    settings.file = settingsFileUrl
    settings.read()

    # Create and show the form
    form = bioImageApp()
    form.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + BiSettingsAccess.instance.value("General", "stylesheet"))
    app.setWindowIcon(QIcon("theme/default/icon.png"))
    sys.exit(app.exec_())