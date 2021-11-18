import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtGui import QPixmap, QImage
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout)


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
