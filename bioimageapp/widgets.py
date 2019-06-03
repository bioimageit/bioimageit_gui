import PySide2.QtCore
from PySide2.QtCore import QMimeData
from PySide2.QtGui import QMouseEvent, QDrag
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QWidget, QPushButton, QFileDialog, QHBoxLayout, QLineEdit, QVBoxLayout
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
        

class BiTagWidget(QWidget):
    def __init__(self, parent: QWidget):
        super(BiTagWidget, self).__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.tagName = QLineEdit()
        self.tagName.setReadOnly(True)
        layout.addWidget(self.tagName)

        removeButton = QPushButton(self.tr("Remove"))
        removeButton.setObjectName("btnDanger")
        layout.addWidget(removeButton, 0, PySide2.QtCore.Qt.AlignRight)
        removeButton.released.connect(self.emitClicked)

        self.setLayout(layout)

    def setContent(self, content: str):
        self.tagName.setText(content)

    def content(self) -> str:
        return self.tagName.text()

    def emitRemove(self): 
        self.remove(self.tagName.text())

class BiWebBrowser(QWidget):
    def __init__(self, parent: QWidget):
        super(BiWebBrowser, self).__init__(parent)

        thisLayout = QVBoxLayout
        thisLayout.setContentsMargins(0,0,0,0)
        thisLayout.setSpacing(0)

        toolBar = self.createToolBar()
        toolBar.setMaximumHeight(48)
        self.webView = QWebEngineView(self)

        thisLayout.addWidget(toolBar)
        thisLayout.addWidget(self.webView)

        totalWidget = QWidget()
        totalLayout = QVBoxLayout()
        totalLayout.setContentsMargins(0,0,0,0)
        totalWidget.setLayout(thisLayout)
        self.setLayout(totalLayout)
        totalLayout.addWidget(totalWidget)
        totalWidget.setObjectName("BiWebBrowser")

    def createToolBar(self) -> QWidget:
        toolbar = QWidget()
        toolbar.setObjectName("BiSubToolBar")

        backButton = QPushButton()
        backButton.setFixedSize(32,32)
        backButton.pressed.connect(self.back)
        backButton.setObjectName("BiWebBrowserBack")

        forwardButton = QPushButton()
        forwardButton.setFixedSize(32,32)
        forwardButton.pressed.connect(self.forward)
        forwardButton.setObjectName("BiWebBrowserForward")

        homeButton = QPushButton()
        homeButton.setFixedSize(32,32)
        homeButton.pressed.connect(self.home)
        homeButton.setObjectName("BiWebBrowserHome")

        barLayout = QHBoxLayout
        barLayout.setSpacing(1)
        barLayout.setContentsMargins(2,2,2,2)
        barLayout.addWidget(backButton)
        barLayout.addWidget(forwardButton)
        barLayout.addWidget(homeButton)
        barLayout.addWidget(QWidget())

        toolbar.setLayout(barLayout)
        return toolbar

    def forward(self):
        self.webView.forward()

    def back(self):
        self.webView.back()

    def home(self):
        self.setHomePage(self.homeURL, self.isWebURL)

    def setHomePage(self, pageURL: str, isWebURL: bool):
        self.homeURL = pageURL
        self.isWebURL = isWebURL
        if self.isWebURL:
            self.webView.load(pageURL)
        else:
            self.homeURL = self.homeURL.replace("\\", "/")
            self.webView.load( "file:///" + self.homeURL)

