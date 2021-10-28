import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import QFileInfo, QDir, Signal
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem,
                               QAbstractItemView, QGridLayout, QHBoxLayout,
                               QToolButton, QSplitter, QLineEdit, QPushButton,
                               QTextEdit, QMessageBox, QFileDialog)

from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.core.widgets import BiButton
from bioimageit_gui.browser.states import BiBrowserStates
from bioimageit_gui.browser.containers import BiBrowserContainer
from bioimageit_gui.browser.models import BiBrowserModel


class BiBrowserComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super().__init__()
        self._object_name = 'BiBrowserComponent'
        self.container = container
        self.container.register(self)  

        self.browserModel = BiBrowserModel(self.container, True)
        self.toolBarComponent = BiBrowserToolBarComponent(self.container)
        self.shortCutComponent = BiBrowserShortCutsComponent(self.container)
        self.tableComponent = BiBrowserTableComponent(self.container)

        self.widget = QWidget()
        self.widget.setObjectName("BiSideBar")
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        splitter = QSplitter()
        splitter.addWidget(self.shortCutComponent.get_widget())
        splitter.addWidget(self.tableComponent.get_widget())

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(self.toolBarComponent.get_widget())
        layout.addWidget(splitter)

    def update(self, action: BiAction):
        pass 

    def get_widget(self): 
        return self.widget  


class BiBrowserToolBarComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super().__init__()
        self._object_name = 'BiBrowserToolBarComponent'
        self.container = container
        self.container.register(self)

        # build widget
        self.widget = QWidget()
        self.widget.setObjectName("BiToolBar")
        self.widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # previous
        previousButton = QToolButton()
        previousButton.setObjectName("BiBrowserToolBarPreviousButton")
        previousButton.setToolTip(self.widget.tr("Previous"))
        previousButton.released.connect(self.previousButtonClicked)
        layout.addWidget(previousButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # next
        nextButton = QToolButton()
        nextButton.setObjectName("BiBrowserToolBarNextButton")
        nextButton.setToolTip(self.widget.tr("Next"))
        nextButton.released.connect(self.nextButtonClicked)
        layout.addWidget(nextButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # up
        upButton = QToolButton()
        upButton.setObjectName("BiExperimentToolBarUpButton")
        upButton.setToolTip(self.widget.tr("Tags"))
        upButton.released.connect(self.upButtonClicked)
        layout.addWidget(upButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # up
        refreshButton = QToolButton()
        refreshButton.setObjectName("BiExperimentToolBarRefreshButton")
        refreshButton.setToolTip(self.widget.tr("Tags"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # data selector
        self.pathLineEdit = QLineEdit(self.widget)
        self.pathLineEdit.setAttribute(PySide2.QtCore.Qt.WA_MacShowFocusRect, False)
        self.pathLineEdit.returnPressed.connect(self.pathEditReturnPressed)
        layout.addWidget(self.pathLineEdit, 1)

        # bookmark
        bookmarkButton = QToolButton()
        bookmarkButton.setObjectName("BiExperimentToolBarBookmarkButton")
        bookmarkButton.setToolTip(self.widget.tr("Bookmark"))
        bookmarkButton.released.connect(self.bookmarkButtonClicked)
        layout.addWidget(bookmarkButton, 0, PySide2.QtCore.Qt.AlignLeft)

    def update(self, action: BiAction):
        if action.state == BiBrowserStates.FilesInfoLoaded:
            self.pathLineEdit.setText(self.container.currentPath)

    def previousButtonClicked(self):
        self.container.emit(BiBrowserStates.PreviousClicked)

    def nextButtonClicked(self):
        self.container.emit(BiBrowserStates.NextClicked)

    def upButtonClicked(self):
        self.container.emit(BiBrowserStates.UpClicked)

    def pathEditReturnPressed(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.emit(BiBrowserStates.DirectoryModified)

    def refreshButtonClicked(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.emit(BiBrowserStates.RefreshClicked)

    def bookmarkButtonClicked(self):
        msgBox = QMessageBox()
        msgBox.setText("Want to bookmark this directory ?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        ret = msgBox.exec_()
        if ret:
            self.container.emit(BiBrowserStates.BookmarkClicked)

    def get_widget(self): 
        return self.widget            
       

class BiBrowserShortCutsComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super(BiBrowserShortCutsComponent, self).__init__()
        self._object_name = 'BiBrowserPreviewComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(mainLayout)

        self.wwidget = QWidget()
        mainLayout.addWidget(self.wwidget)
        self.wwidget.setObjectName("BiLeftBar")
        self.wwidget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        self.wwidget.setLayout(layout)

        addExpermentbutton = QPushButton(self.wwidget.tr("New Experiment"))
        addExpermentbutton.setObjectName("BiBrowserShortCutsNewButton")
        addExpermentbutton.released.connect(self.newExperimentClicked)
        layout.addWidget(addExpermentbutton, 0, PySide2.QtCore.Qt.AlignTop)

        openFinderButton = QPushButton(self.widget.tr("Toolboxes"))
        openFinderButton.setObjectName("BiBrowserShortCutsFinderButton")
        openFinderButton.released.connect(self.openFinderClicked)
        layout.addWidget(openFinderButton, 0, PySide2.QtCore.Qt.AlignTop)

        separatorLabel = QLabel(self.wwidget.tr("Bookmarks"), self.wwidget)
        layout.addWidget(separatorLabel, 0, PySide2.QtCore.Qt.AlignTop)
        separatorLabel.setObjectName("BiBrowserShortCutsTitle")

        bookmarkWidget = QWidget(self.wwidget)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        bookmarkWidget.setLayout(self.layout)

        layout.addWidget(bookmarkWidget, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop) 

    def reloadBookmarks(self):

        # free layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()

        # load
        for entry in self.container.bookmarks.bookmarks["bookmarks"]:

            button = BiButton(entry['name'], self.widget)
            button.setObjectName("BiBrowserShortCutsButton")
            button.content = entry['url']
            button.setCursor(PySide2.QtCore.Qt.PointingHandCursor)
            button.clickedContent.connect(self.buttonClicked)
            self.layout.insertWidget(self.layout.count()-1, button, 0,
                                     PySide2.QtCore.Qt.AlignTop)

    def update(self, action: BiAction):
        if action.state == BiBrowserStates.BookmarksModified:
            self.reloadBookmarks()

    def openFinderClicked(self):
        self.container.emit(BiBrowserStates.OpenFinderClicked)

    def newExperimentClicked(self):
        self.container.emit(BiBrowserStates.NewExperimentClicked)

    def buttonClicked(self, path: str):
        self.container.bookmarkPath = path
        self.container.emit(BiBrowserStates.BookmarkOpenClicked)

    def get_widget(self): 
        return self.widget


class BiBrowserTableComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super(BiBrowserTableComponent, self).__init__()
        self._object_name = 'BiBrowserTableComponent'
        self.container = container
        self.container.register(self)
        self.buildWidget()

    def buildWidget(self):

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.cellDoubleClicked.connect(self.cellDoubleClicked)
        self.tableWidget.cellClicked.connect(self.cellClicked)

        labels = ['', 'Name', 'Date', 'Type']
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)

    def update(self, action : BiAction):
        if action.state == BiBrowserStates.FilesInfoLoaded:
            i = -1
            self.tableWidget.setRowCount(len(self.container.files))
            for fileInfo in self.container.files:
                i += 1
                # icon depends on type
                iconLabel = QLabel(self.tableWidget)
                if fileInfo.type == "dir":
                    iconLabel.setObjectName("BiBrowserDirIcon")
                elif fileInfo.type == "run":
                    iconLabel.setObjectName("BiBrowserRunIcon")
                elif fileInfo.type == "experiment":
                    iconLabel.setObjectName("BiBrowserExperimentIcon")
                elif fileInfo.type == "rawdataset":
                    iconLabel.setObjectName("BiBrowserRawDatSetIcon")
                elif fileInfo.type == "processeddataset":
                    iconLabel.setObjectName("BiBrowserProcessedDataSetIcon")
                elif fileInfo.type == "rawdata":
                    iconLabel.setObjectName("BiBrowserRawDatIcon")
                elif fileInfo.type == "processeddata":
                    iconLabel.setObjectName("BiBrowserProcessedDataIcon")

                # icon
                self.tableWidget.setCellWidget(i, 0, iconLabel)
                # name
                self.tableWidget.setItem(i, 1, QTableWidgetItem(fileInfo.name))
                # date
                self.tableWidget.setItem(i, 2, QTableWidgetItem(fileInfo.date))
                # type
                self.tableWidget.setItem(i, 3, QTableWidgetItem(fileInfo.type))
            self.container.emit(BiBrowserStates.TableLoaded)    
            
    def cellDoubleClicked(self, row: int, col: int):
        self.container.doubleClickedRow = row
        self.container.emit(BiBrowserStates.ItemDoubleClicked)
        self.highlightLine(row)

    def cellClicked(self, row : int, col : int):
        self.container.clickedRow = row
        self.container.emit(BiBrowserStates.ItemClicked)
        self.highlightLine(row)

    def highlightLine(self, row: int):
        for col in range(4):
            if self.tableWidget.item(row, col):
                self.tableWidget.item(row, col).setSelected(True)    

    def get_widget(self): 
        return self.widget   
