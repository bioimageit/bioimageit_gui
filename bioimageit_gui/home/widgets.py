import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtGui import QPixmap, QImage
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout)

import qtpy.QtCore
from qtpy.QtWidgets import (QHBoxLayout, QWidget, QVBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QAbstractItemView)

from bioimageit_framework.widgets import BiWidget                                

class BiHomeTile(QWidget):
    clickedSignal = Signal(str)

    def __init__(self, title: str, icon: str, action: str,
                 parent: QWidget = None):
        super().__init__(parent)
        self.action = action

        self.setCursor(qtpy.QtGui.QCursor(
            qtpy.QtCore.Qt.PointingHandCursor))

        glayout = QVBoxLayout()
        self.setLayout(glayout)

        widget = QWidget()
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        glayout.addWidget(widget)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Title
        titleLabel = QLabel()
        titleLabel.setObjectName("BiHomeTileTitle")
        titleLabel.setAlignment(qtpy.QtCore.Qt.AlignCenter)
        titleLabel.setText(title)
        
        # Image
        thumbnailLabel = QLabel()
        img = QImage(icon)
        thumbnailLabel.setPixmap(QPixmap.fromImage(img.scaled(40, 40, qtpy.QtCore.Qt.KeepAspectRatio)))
        
        # Fill layout
        layout.addWidget(thumbnailLabel, 0, qtpy.QtCore.Qt.AlignHCenter)
        layout.addWidget(titleLabel)
        widget.setObjectName("BiHomeTile")

    def mousePressEvent(self, event):
        self.clickedSignal.emit(self.action)

class BiHomeTilesWidget(BiWidget):
    CLICKED_TILE = 'clicked_tile'

    """Home page widget for BioImageIT app"""
    def __init__(self):
        super().__init__()
        # actions ids
        self.clicked_tile = ''

        # Widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        # apps tiles
        btnsWidget = QWidget()
        btnsLayout = QHBoxLayout()
        btnsWidget.setLayout(btnsLayout)

        # workspace 
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

    def add_tile(self, title, icon, action):
        """Add a new tile to the home widget
        
        Parameters
        ----------
        title: str
            title of the tile
        icon: str
            Path of the icon displayed in the tile
        action: str
            Name of the action that is triggered when the tile is clicked        
        
        """    
        tile = BiHomeTile(title, icon, action)
        tile.clickedSignal.connect(self.tile_clicked)

    def tile_clicked(self, action):
        self.clicked_tile = action
        self.emit(BiHomeTilesWidget.CLICKED_TILE)


class BiWorkspaceWidget(BiWidget):
    CLICKED_EXP = 'clicked_exp'

    def __init__(self):
        super().__init__()
        self.clicked_experiment = None

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
        
        layout = QVBoxLayout()
        layout.addWidget(experimentsTitle, 0)
        layout.addWidget(self.shortcutsWidget, 1)
        layout.addWidget(self.emptyshortcutsWidget, 1, qtpy.QtCore.Qt.AlignCenter)
        self.widget.setLayout(layout)

    def free(self):
        self.shortcutsWidget.setRowCount(0)
        self.shortcutsWidget.setVisible(False)
        self.emptyshortcutsWidget.setVisible(True)

    def set_row_count(self, n):
        self.shortcutsWidget.setRowCount(n)

    def set_item(self, row, experiment):
        iconLabel = QLabel(self.shortcutsWidget)
        iconLabel.setObjectName("BiBrowserExperimentIcon")
        self.shortcutsWidget.setCellWidget(row, 0, iconLabel)  
        self.shortcutsWidget.setItem(row, 1, QTableWidgetItem(experiment['info'].name))  
        self.shortcutsWidget.setItem(row, 2, QTableWidgetItem(experiment['info'].date))  
        self.shortcutsWidget.setItem(row, 3, QTableWidgetItem(experiment['info'].author))
        self.shortcutsWidget.setVisible(True)
        self.emptyshortcutsWidget.setVisible(False)           

    def cellClicked(self, row: int, col: int):
        for col in range(0, self.shortcutsWidget.columnCount()):
            self.shortcutsWidget.setCurrentCell(row, col, qtpy.QtCore.QItemSelectionModel.Select) 

    def cellDoubleClicked(self, row: int, col: int):
        self.clicked_experiment = self.container.experiments[row]['md_uri']
        self.emit(BiWorkspaceWidget.CLICKED_EXP)    