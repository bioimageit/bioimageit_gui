from qtpy.QtCore import Signal
import qtpy.QtCore
from qtpy.QtGui import QPixmap, QImage
from qtpy.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, QPushButton, QMessageBox)


class BiShortcutButton(QWidget):

    clickedId = Signal(int)
    clickedContent = Signal(str)

    def __init__(self, title: str, icon: str):
        super().__init__()

        widget = QWidget()  
        widget.setObjectName('BiShortcutButton') 
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # icon
        label = QLabel()
        img = QImage(icon)
        label.setPixmap(QPixmap.fromImage(img.scaled(15, 15, qtpy.QtCore.Qt.KeepAspectRatio)))
        layout.addWidget(label, 0, qtpy.QtCore.Qt.AlignHCenter)

        # button
        btn = QPushButton(title)
        btn.setObjectName('BiShortcutButton')
        layout.addWidget(btn, 1, qtpy.QtCore.Qt.AlignLeft)

        btn.released.connect(self.emitClicked)
        self.id = 0
        self.content = ''

        glayout = QHBoxLayout()
        glayout.setContentsMargins(0, 0, 0, 0)
        glayout.addWidget(widget)
        self.setLayout(glayout)

    def emitClicked(self):
        self.clickedId.emit(self.id)
        self.clickedContent.emit(self.content)
