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
        titleLabel.setObjectName("bi-home-tile-title")
        titleLabel.setAlignment(qtpy.QtCore.Qt.AlignCenter)
        titleLabel.setText(title)
        titleLabel.setStyleSheet('QLabel{background-color: transparent;}')
        
        # Image
        thumbnailLabel = QLabel()
        img = QImage(icon)
        thumbnailLabel.setPixmap(QPixmap.fromImage(img.scaled(40, 40, qtpy.QtCore.Qt.KeepAspectRatio)))
        thumbnailLabel.setStyleSheet('QLabel{background-color: transparent;}')
        
        # Fill layout
        layout.addWidget(thumbnailLabel, 0, qtpy.QtCore.Qt.AlignHCenter)
        layout.addWidget(titleLabel)
        widget.setObjectName("bi-home-tile")

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
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.widget.setLayout(self.layout)
        self.layout.addWidget(QWidget(), 1)
        self.layout.addWidget(QWidget(), 1)

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
        self.layout.insertWidget(self.layout.count()-1, tile)
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
        experimentsTitle.setObjectName('bi-label-form-header1')

        self.shortcutsWidget = QTableWidget()
        self.shortcutsWidget.setAlternatingRowColors(True)
        self.shortcutsWidget.setColumnCount(3)
        self.shortcutsWidget.verticalHeader().setVisible(False)
        self.shortcutsWidget.horizontalHeader().setStretchLastSection(True)
        self.shortcutsWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shortcutsWidget.cellDoubleClicked.connect(self.cell_double_clicked)
        self.shortcutsWidget.cellClicked.connect(self.cell_clicked)
        self.shortcutsWidget.setHorizontalHeaderLabels(['Name', 'Date', 'Author'])
        self.shortcutsWidget.verticalHeader().setDefaultSectionSize(12)
        
        self.emptyshortcutsWidget = QLabel("Your workspace is empty. \n Start creating a new experiment !")
        self.emptyshortcutsWidget.setObjectName('bi-home-empty')
        
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
        self.shortcutsWidget.setItem(row, 0, QTableWidgetItem(experiment['info'].name))  
        self.shortcutsWidget.setItem(row, 1, QTableWidgetItem(experiment['info'].date))  
        self.shortcutsWidget.setItem(row, 2, QTableWidgetItem(experiment['info'].author))
        self.shortcutsWidget.setVisible(True)
        self.emptyshortcutsWidget.setVisible(False)           

    def cell_clicked(self, row: int, col: int):
        for col in range(0, self.shortcutsWidget.columnCount()):
            self.shortcutsWidget.setCurrentCell(row, col, qtpy.QtCore.QItemSelectionModel.Select) 

    def cell_double_clicked(self, row: int, col: int):
        self.clicked_experiment = row
        self.emit(BiWorkspaceWidget.CLICKED_EXP)    