import PySide2.QtCore
from PySide2.QtWidgets import QWidget, QPushButton, QFileDialog, QHBoxLayout, QLineEdit, QMouseEvent, QDrag, QMimeData
from PySide2.QtCore import QObject, Signal, Slot, QUrl 

class BiButton(QPushButton):
    clickedId = Signal(int)
    clickedContent = Signal(str)

    def __init__(self, title: str, parent: QWidget):
        super(BiButton, self).__init__(title, parent)
        self.pressed.connect(self.emitClicked)
        self.id = 0
        self.content = ''

    def emitClicked(self):
        self.clickedId.emit(self.id)
        self.clickedContent.emit(self.content)

class BiFileSelectWidget(QWidget):

    def __init__(self, isDir: str, parent: QWidget):
        super(BiFileSelectWidget, self).__init__(isDir, parent)

        self.isDir = isDir

        layout = QHBoxLayout
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.lineEdit = QLineEdit()
        layout.addWidget(self.lineEdit)

        browseButton = QPushButton("...")
        browseButton.setObjectName("BiBrowseButton")
        layout.addWidget(browseButton, 0, PySide2.QtCore.Qt.AlignRight)
        browseButton.released.connect(self.browseClicked)

    def setText(self, text: str):
        self.lineEdit.setText(text)

    def text(self):
        return self.lineEdit.text()

    def browseClicked(self):

        if self.isDir:
            dir = QFileDialog.getExistingDirectory(self, "Open a directory")
            if dir != "":
                self.lineEdit.setText(dir)
            
        else:
            file = QFileDialog.getOpenFileName(self, "Open a file", '', "*.*")
            if file != "":
                self.lineEdit.setText(file)

class BiDragLabel(QWidget):
    def __init__(self, parent: QWidget):
        super(BiDragLabel, self).__init__(parent)

    def setMimeData(self, data: str):
        self.mimeData = data

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == PySide2.QtCore.Qt.LeftButton:
            drag = QDrag(self)
            mimeData = QMimeData()
            urlList = [QUrl(self.mimeData)]

            mimeData.setUrls(urlList)
            drag.setMimeData(mimeData)

            if self.pixmap():
                drag.setPixmap(self.pixmap())
            
            drag.exec()
        