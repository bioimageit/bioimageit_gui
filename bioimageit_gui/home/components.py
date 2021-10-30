import os
import PySide2.QtCore
from PySide2.QtWidgets import (QHBoxLayout, QWidget, QVBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QAbstractItemView)
                               
from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.core.widgets import BiFlowLayout
from bioimageit_gui.home.containers import BiHomeContainer
from bioimageit_gui.home.states import BiHomeStates
from bioimageit_gui.home.widgets import BiHomeTile
from bioimageit_gui.core.theme import BiThemeAccess
from bioimageit_core.config import ConfigAccess
from bioimageit_core.experiment import Workspace


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
        openNewExperimentTile = BiHomeTile('New \n experiment', BiThemeAccess.instance().icon('plus-black-symbol'), 'OpenNewExperiment')
        openToolboxesTile = BiHomeTile('Toolboxes', BiThemeAccess.instance().icon('tools'), 'OpenToolboxes')
        openBrowserTile = BiHomeTile('Browse', BiThemeAccess.instance().icon('open-folder_negative'), 'OpenBrowser')
        openSettingsTile = BiHomeTile('Settings', BiThemeAccess.instance().icon('cog-wheel-silhouette'), 'OpenSettings')
        openNewExperimentTile.clickedSignal.connect(self.tileClicked)
        openToolboxesTile.clickedSignal.connect(self.tileClicked)
        openBrowserTile.clickedSignal.connect(self.tileClicked)
        openSettingsTile.clickedSignal.connect(self.tileClicked)
        btnsLayout.addWidget(openNewExperimentTile, 1, PySide2.QtCore.Qt.AlignRight)
        btnsLayout.addWidget(openToolboxesTile,  0, PySide2.QtCore.Qt.AlignCenter)
        btnsLayout.addWidget(openBrowserTile,  0, PySide2.QtCore.Qt.AlignCenter)
        btnsLayout.addWidget(openSettingsTile,  1, PySide2.QtCore.Qt.AlignLeft)

        experimentsTitle = QLabel('Experiments')
        experimentsTitle.setObjectName('BiLabelFormHeader1')

        self.shortcutsWidget = QTableWidget()
        self.shortcutsWidget.setAlternatingRowColors(True)
        self.shortcutsWidget.setColumnCount(4)
        self.shortcutsWidget.verticalHeader().setVisible(False)
        self.shortcutsWidget.horizontalHeader().setStretchLastSection(True)
        self.shortcutsWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shortcutsWidget.cellDoubleClicked.connect(self.cellDoubleClicked)
        self.shortcutsWidget.setHorizontalHeaderLabels(['', 'Name', 'Date', 'Author'])
        
        self.emptyshortcutsWidget = QLabel("Your workspace is empty. \n Start creating a new experiment !")
        self.emptyshortcutsWidget.setObjectName('BiHomeEmpty')
        
        layout.addWidget(btnsWidget, 0)
        layout.addWidget(experimentsTitle, 0)
        layout.addWidget(self.shortcutsWidget, 1)
        layout.addWidget(self.emptyshortcutsWidget, 1, PySide2.QtCore.Qt.AlignCenter)

        self.fill_experiments()
    
    def fill_experiments(self):
        workspace = Workspace()  
        self.container.experiments = workspace.experiments()
        if len(self.container.experiments) == 0:
            self.shortcutsWidget.setVisible(False)
            self.emptyshortcutsWidget.setVisible(True)
        else:
            self.shortcutsWidget.setRowCount(len(self.container.experiments))
            i = -1
            for exp in self.container.experiments:
                i += 1
                iconLabel = QLabel(self.shortcutsWidget)
                iconLabel.setObjectName("BiBrowserExperimentIcon")
                self.shortcutsWidget.setCellWidget(i, 0, iconLabel)  
                self.shortcutsWidget.setItem(i, 1, QTableWidgetItem(exp.name))  
                self.shortcutsWidget.setItem(i, 2, QTableWidgetItem(exp.date))  
                self.shortcutsWidget.setItem(i, 3, QTableWidgetItem(exp.author))  
            self.shortcutsWidget.setVisible(True)
            self.emptyshortcutsWidget.setVisible(False)    
        
    def tileClicked(self, action: str):
        if action == 'OpenNewExperiment':
            self.container.emit(BiHomeStates.OpenNewExperiment)
        elif action == 'OpenToolboxes':
            self.container.emit(BiHomeStates.OpenToolboxes)    
        elif action == 'OpenBrowser':
            self.container.emit(BiHomeStates.OpenBrowser) 
        elif action == 'OpenSettings':
            self.container.emit(BiHomeStates.OpenSettings)
        print('emit ', action)                 

    def cellDoubleClicked(self, row: int, col: int):
        self.container.clicked_experiment = row
        self.container.emit(BiHomeStates.OpenExperiment)
        print('emit open experiment:', self.container.experiments[row].name)

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget
