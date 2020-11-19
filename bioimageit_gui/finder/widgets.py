import os
import PySide2.QtCore
from PySide2.QtCore import Signal
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem,
                               QAbstractItemView, QHBoxLayout, QToolButton)

from bioimageit_core.processes.containers import ProcessCategoryContainer


class BiProcessCategoryTile(QWidget):
    clickedSignal = Signal(ProcessCategoryContainer)

    def __init__(self, category: ProcessCategoryContainer,
                 parent: QWidget = None):
        super().__init__(parent)
        self.category = category

        self.setCursor(PySide2.QtGui.QCursor(
            PySide2.QtCore.Qt.PointingHandCursor))

        glayout = QVBoxLayout()
        self.setLayout(glayout)

        widget = QWidget()
        widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("BiProcessCategoryTile")
        glayout.addWidget(widget)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)

        titleLabel = QLabel()
        titleLabel.setObjectName("BiProcessCategoryTileTitle")
        titleLabel.setAlignment(PySide2.QtCore.Qt.AlignCenter)
        titleLabel.setText(category.name)
        layout.addWidget(titleLabel, 0, PySide2.QtCore.Qt.AlignTop)

        thumbnailLabel = QLabel()

        img = QImage(os.path.join(category.thumbnail))
        thumbnailLabel.setPixmap(QPixmap.fromImage(img.scaled(200, 200, PySide2.QtCore.Qt.KeepAspectRatio)))
        layout.addWidget(thumbnailLabel, 0, PySide2.QtCore.Qt.AlignTop | PySide2.QtCore.Qt.AlignHCenter)

        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop)
        widget.setObjectName("BiProcessCategoryTile")

    def mousePressEvent(self, event):
        self.clickedSignal.emit(self.category)
