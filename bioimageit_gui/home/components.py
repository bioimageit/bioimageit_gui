import os
import qtpy.QtCore
from qtpy.QtWidgets import (QHBoxLayout, QWidget, QVBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QAbstractItemView)
                               
from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.home.containers import BiHomeContainer
from bioimageit_gui.home.states import BiHomeStates
from bioimageit_gui.home.widgets import BiHomeTile
from bioimageit_gui.core.theme import BiThemeAccess
from bioimageit_core.api import APIAccess

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
        openBrowserTile = BiHomeTile('Browse \n experiments', BiThemeAccess.instance().icon('folder-gray'), 'OpenBrowser')
        #openDesignerTile = BiHomeTile('Pipeline \n designer', BiThemeAccess.instance().icon('workflow'), 'OpenDesigner')
        openToolboxesTile = BiHomeTile('Toolboxes', BiThemeAccess.instance().icon('tools'), 'OpenToolboxes')
        openSettingsTile = BiHomeTile('Settings', BiThemeAccess.instance().icon('cog-wheel-silhouette'), 'OpenSettings')

        openNewExperimentTile.clickedSignal.connect(self.tileClicked)
        #openDesignerTile.clickedSignal.connect(self.tileClicked)
        openToolboxesTile.clickedSignal.connect(self.tileClicked)
        openBrowserTile.clickedSignal.connect(self.tileClicked)
        openSettingsTile.clickedSignal.connect(self.tileClicked)
        btnsLayout.addWidget(openNewExperimentTile, 1, qtpy.QtCore.Qt.AlignRight)
        btnsLayout.addWidget(openBrowserTile,  0, qtpy.QtCore.Qt.AlignCenter)
        #btnsLayout.addWidget(openDesignerTile,  0, qtpy.QtCore.Qt.AlignCenter)
        btnsLayout.addWidget(openToolboxesTile,  0, qtpy.QtCore.Qt.AlignCenter)
        btnsLayout.addWidget(openSettingsTile,  1, qtpy.QtCore.Qt.AlignLeft)

        experimentsTitle = QLabel('Experiments')
        experimentsTitle.setObjectName('BiLabelFormHeader1')

        self.shortcutsWidget = QTableWidget()
        self.shortcutsWidget.setAlternatingRowColors(True)
        self.shortcutsWidget.setColumnCount(4)
        self.shortcutsWidget.verticalHeader().setVisible(False)
        self.shortcutsWidget.horizontalHeader().setStretchLastSection(True)
        self.shortcutsWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shortcutsWidget.cellDoubleClicked.connect(self.cellDoubleClicked)
        self.shortcutsWidget.cellClicked.connect(self.cellClicked)
        self.shortcutsWidget.setHorizontalHeaderLabels(['', 'Name', 'Date', 'Author'])
        self.shortcutsWidget.verticalHeader().setDefaultSectionSize(12)
        
        self.emptyshortcutsWidget = QLabel("Your workspace is empty. \n Start creating a new experiment !")
        self.emptyshortcutsWidget.setObjectName('BiHomeEmpty')
        
        layout.addWidget(btnsWidget, 0)
        layout.addWidget(experimentsTitle, 0)
        layout.addWidget(self.shortcutsWidget, 1)
        layout.addWidget(self.emptyshortcutsWidget, 1, qtpy.QtCore.Qt.AlignCenter)

        self.fill_experiments()
    
    def fill_experiments(self):
        self.container.experiments = APIAccess.instance().get_workspace_experiments()
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
                self.shortcutsWidget.setItem(i, 1, QTableWidgetItem(exp['info'].name))  
                self.shortcutsWidget.setItem(i, 2, QTableWidgetItem(exp['info'].date))  
                self.shortcutsWidget.setItem(i, 3, QTableWidgetItem(exp['info'].author))  
            self.shortcutsWidget.setVisible(True)
            self.emptyshortcutsWidget.setVisible(False)    
        
    def tileClicked(self, action: str):
        if action == 'OpenNewExperiment':
            self.container.emit(BiHomeStates.OpenNewExperiment)
        elif action == 'OpenBrowser':
            self.container.emit(BiHomeStates.OpenBrowser) 
        elif action == 'OpenDesigner':
            self.container.emit(BiHomeStates.OpenDesigner) 
        elif action == 'OpenToolboxes':
            self.container.emit(BiHomeStates.OpenToolboxes)    
        elif action == 'OpenSettings':
            self.container.emit(BiHomeStates.OpenSettings)

    def cellClicked(self, row: int, col: int):
        for col in range(0, self.shortcutsWidget.columnCount()):
            self.shortcutsWidget.setCurrentCell(row, col, qtpy.QtCore.QItemSelectionModel.Select) 

    def cellDoubleClicked(self, row: int, col: int):
        self.container.clicked_experiment = self.container.experiments[row]['md_uri']
        self.container.emit(BiHomeStates.OpenExperiment)

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget
