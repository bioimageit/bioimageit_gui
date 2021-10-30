import os
import PySide2.QtCore
from PySide2.QtWidgets import (QHBoxLayout, QWidget, QVBoxLayout, QPushButton,
                               QLabel)
                               
from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.core.widgets import BiFlowLayout
from bioimageit_gui.home.containers import BiHomeContainer
from bioimageit_gui.home.states import BiHomeStates
from bioimageit_gui.home.widgets import BiHomeTile
from bioimageit_gui.core.theme import BiThemeAccess
from bioimageit_core.config import ConfigAccess


class BiHomeComponent(BiComponent):
    def __init__(self, container: BiHomeContainer):
        super().__init__()
        self._object_name = 'BiHomeComponent'
        self.container = container
        self.container.register(self)  

        # Widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        # main tiles
        btnsWidget = QWidget()
        btnsLayout = QHBoxLayout()
        btnsWidget.setLayout(btnsLayout)
        openNewExperimentTile = BiHomeTile('New \n experiment', BiThemeAccess.instance().icon('plus-black-symbol'), 'openNewExperiment')
        openToolboxesTile = BiHomeTile('Toolboxes', BiThemeAccess.instance().icon('tools'), 'openToolboxes')
        openBrowserTile = BiHomeTile('Browse', BiThemeAccess.instance().icon('open-folder_negative'), 'openBrowser')
        openSettingsTile = BiHomeTile('Settings', BiThemeAccess.instance().icon('cog-wheel-silhouette'), 'openSettings')
        btnsLayout.addWidget(openNewExperimentTile, 1, PySide2.QtCore.Qt.AlignRight)
        btnsLayout.addWidget(openToolboxesTile,  0, PySide2.QtCore.Qt.AlignCenter)
        btnsLayout.addWidget(openBrowserTile,  0, PySide2.QtCore.Qt.AlignCenter)
        btnsLayout.addWidget(openSettingsTile,  1, PySide2.QtCore.Qt.AlignLeft)

        experimentsTitle = QLabel('Experiments')
        experimentsTitle.setObjectName('BiLabelFormHeader1')

        self.shortcutsWidget = QWidget()
        self.shortcutsLayout = BiFlowLayout()
        self.shortcutsWidget.setLayout(self.shortcutsLayout)

        self.emptyshortcutsWidget = QLabel("Your workspace is empty. \n Start creating a new experiment")
        self.emptyshortcutsWidget.setObjectName('BiHomeEmpty')
        
        layout.addWidget(btnsWidget, 0)
        layout.addWidget(experimentsTitle, 0)
        layout.addWidget(self.shortcutsWidget, 1)
        layout.addWidget(self.emptyshortcutsWidget, 1, PySide2.QtCore.Qt.AlignCenter)

        self.fill_experiments()
    
    def fill_experiments(self):

        workspace_dir = ConfigAccess.instance().get("workspace")
        dirs = os.listdir(workspace_dir)
        if len(dirs) == 0:
            self.shortcutsWidget.setVisible(False)
            self.emptyshortcutsWidget.setVisible(True)
        else:
            for dir in dirs:
                if os.path.exists(os.path.join(workspace_dir, dir, 'experiment.md.json')):
                    tile = BiHomeTile(os.path.basename(dir), BiThemeAccess.instance().icon('database'), dir)
                    self.shortcutsLayout.addWidget(tile)
            self.shortcutsWidget.setVisible(True)
            self.emptyshortcutsWidget.setVisible(False)    


        
        
    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget
