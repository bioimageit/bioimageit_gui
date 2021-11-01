"""Set of basic widgets for BioImageIT

Classes
-------
BiWebBrowser

"""

from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import (QWidget, QPushButton,
                               QHBoxLayout, QVBoxLayout)

class BiWebBrowser(QWidget):
    def __init__(self, parent: QWidget):
        super(BiWebBrowser, self).__init__(parent)

        thisLayout = QVBoxLayout()
        thisLayout.setContentsMargins(0,0,0,0)
        thisLayout.setSpacing(0)

        self.toolBar = self.createToolBar()
        self.toolBar.setMaximumHeight(48)
        self.webView = QWebEngineView(self)

        thisLayout.addWidget(self.toolBar)
        thisLayout.addWidget(self.webView)

        totalWidget = QWidget()
        totalLayout = QVBoxLayout()
        totalLayout.setContentsMargins(0,0,0,0)
        totalWidget.setLayout(thisLayout)
        self.setLayout(totalLayout)
        totalLayout.addWidget(totalWidget)
        totalWidget.setObjectName("BiWebBrowser")

    def setToolBarVisible(self, visible:bool):
        self.toolBar.setVisible(visible)    

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

        barLayout = QHBoxLayout()
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

    def setHomePageHtml(self, html:str):
        self.webView.setHtml(html)

    def setHomePage(self, pageURL: str, isWebURL: bool):
        self.homeURL = pageURL
        self.isWebURL = isWebURL
        if self.isWebURL:
            self.webView.load(pageURL)
        else:
            self.homeURL = self.homeURL.replace("\\", "/")
            self.webView.load( "file:///" + self.homeURL)
