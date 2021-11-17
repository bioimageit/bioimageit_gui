from PySide2.QtCore import Signal
import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, )


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
        label.setPixmap(QPixmap.fromImage(img.scaled(15, 15, PySide2.QtCore.Qt.KeepAspectRatio)))
        layout.addWidget(label, 0, PySide2.QtCore.Qt.AlignHCenter)

        # button
        btn = QPushButton(title)
        btn.setObjectName('BiShortcutButton')
        layout.addWidget(btn, 1, PySide2.QtCore.Qt.AlignLeft)

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
