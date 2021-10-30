import PySide2.QtCore
from PySide2.QtCore import Signal
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout)


class BiHomeTile(QWidget):
    clickedSignal = Signal(str)

    def __init__(self, title: str, icon: str, action: str,
                 parent: QWidget = None):
        super().__init__(parent)
        self.action = action

        self.setCursor(PySide2.QtGui.QCursor(
            PySide2.QtCore.Qt.PointingHandCursor))

        glayout = QVBoxLayout()
        self.setLayout(glayout)

        widget = QWidget()
        widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        glayout.addWidget(widget)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Title
        titleLabel = QLabel()
        titleLabel.setObjectName("BiHomeTileTitle")
        titleLabel.setAlignment(PySide2.QtCore.Qt.AlignCenter)
        titleLabel.setText(title)
        
        # Image
        thumbnailLabel = QLabel()
        img = QImage(icon)
        thumbnailLabel.setPixmap(QPixmap.fromImage(img.scaled(40, 40, PySide2.QtCore.Qt.KeepAspectRatio)))
        
        # Fill layout
        layout.addWidget(thumbnailLabel, 0, PySide2.QtCore.Qt.AlignHCenter)
        layout.addWidget(titleLabel)
        widget.setObjectName("BiHomeTile")

    def mousePressEvent(self, event):
        self.clickedSignal.emit(self.action)
