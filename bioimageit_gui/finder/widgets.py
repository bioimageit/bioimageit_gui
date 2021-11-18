import os
import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtGui import QPixmap, QImage
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem,
                               QAbstractItemView, QHBoxLayout, QToolButton)

from bioimageit_core.processes.containers import ProcessCategoryContainer


class BiProcessCategoryTile(QWidget):
    clickedSignal = Signal(ProcessCategoryContainer)

    def __init__(self, category: ProcessCategoryContainer,
                 parent: QWidget = None):
        super().__init__(parent)
        self.category = category

        self.setCursor(qtpy.QtGui.QCursor(
            qtpy.QtCore.Qt.PointingHandCursor))

        glayout = QVBoxLayout()
        self.setLayout(glayout)

        widget = QWidget()
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("BiProcessCategoryTile")
        glayout.addWidget(widget)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)

        titleLabel = QLabel()
        titleLabel.setObjectName("BiProcessCategoryTileTitle")
        titleLabel.setAlignment(qtpy.QtCore.Qt.AlignCenter)
        titleLabel.setText(category.name)
        layout.addWidget(titleLabel, 0, qtpy.QtCore.Qt.AlignTop)

        thumbnailLabel = QLabel()

        img = QImage(os.path.join(category.thumbnail))
        #print(os.path.join(category.thumbnail))
        thumbnailLabel.setPixmap(QPixmap.fromImage(img.scaled(200, 200, qtpy.QtCore.Qt.KeepAspectRatio)))
        layout.addWidget(thumbnailLabel, 0, qtpy.QtCore.Qt.AlignTop | qtpy.QtCore.Qt.AlignHCenter)

        layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop)
        widget.setObjectName("BiProcessCategoryTile")

    def mousePressEvent(self, event):
        self.clickedSignal.emit(self.category)
