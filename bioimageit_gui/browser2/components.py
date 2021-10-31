import os
import getpass
from pathlib import Path

import PySide2.QtCore
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout,
                               QTableWidget, QTableWidgetItem,
                               QAbstractItemView, QHBoxLayout,
                               QToolButton, QSplitter, QLineEdit)

from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.core.theme import BiThemeAccess
from bioimageit_gui.browser2.states import BiBrowser2States
from bioimageit_gui.browser2.containers import BiBrowser2Container
from bioimageit_gui.browser2.widgets import BiShortcutButton


class BiBrowser2Component(BiComponent):
    def __init__(self, container: BiBrowser2Container):
        super().__init__()
        self._object_name = 'BiBrowserComponent'
        self.container = container
        self.container.register(self)  

        self.toolBarComponent = BiBrowser2ToolBarComponent(self.container)
        self.shortCutComponent = BiBrowser2ShortCutsComponent(self.container)
        self.tableComponent = BiBrowser2TableComponent(self.container)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
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


class BiBrowser2ToolBarComponent(BiComponent):
    def __init__(self, container: BiBrowser2Container):
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
        previousButton.setObjectName("BiBrowser2ToolBarPreviousButton")
        previousButton.setToolTip(self.widget.tr("Previous"))
        previousButton.released.connect(self.previousButtonClicked)
        layout.addWidget(previousButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # next
        nextButton = QToolButton()
        nextButton.setObjectName("BiBrowser2ToolBarNextButton")
        nextButton.setToolTip(self.widget.tr("Next"))
        nextButton.released.connect(self.nextButtonClicked)
        layout.addWidget(nextButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # up
        upButton = QToolButton()
        upButton.setObjectName("BiBrowser2ToolBarUpButton")
        upButton.setToolTip(self.widget.tr("Tags"))
        upButton.released.connect(self.upButtonClicked)
        layout.addWidget(upButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # up
        refreshButton = QToolButton()
        refreshButton.setObjectName("BiBrowser2ToolBarRefreshButton")
        refreshButton.setToolTip(self.widget.tr("Tags"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # data selector
        self.pathLineEdit = QLineEdit(self.widget)
        self.pathLineEdit.setAttribute(PySide2.QtCore.Qt.WA_MacShowFocusRect, False)
        self.pathLineEdit.returnPressed.connect(self.pathEditReturnPressed)
        layout.addWidget(self.pathLineEdit, 1)

    def update(self, action: BiAction):
        if action.state == BiBrowser2States.FilesInfoLoaded:
            self.pathLineEdit.setText(self.container.currentPath)

    def previousButtonClicked(self):
        self.container.emit(BiBrowser2States.PreviousClicked)

    def nextButtonClicked(self):
        self.container.emit(BiBrowser2States.NextClicked)

    def upButtonClicked(self):
        self.container.emit(BiBrowser2States.UpClicked)

    def pathEditReturnPressed(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.emit(BiBrowser2States.DirectoryModified)

    def refreshButtonClicked(self):
        self.container.setCurrentPath(self.pathLineEdit.text())
        self.container.emit(BiBrowser2States.RefreshClicked)

    def get_widget(self): 
        return self.widget            
       

class BiBrowser2ShortCutsComponent(BiComponent):
    def __init__(self, container: BiBrowser2Container):
        super(BiBrowser2ShortCutsComponent, self).__init__()
        self._object_name = 'BiBrowser2ShortCutsComponent'
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

        home_dir = Path.home() 
        username = getpass.getuser()

        homeButton = BiShortcutButton(username, BiThemeAccess.instance().icon('home'))
        homeButton.setObjectName("BiBrowser2HomeButton")
        homeButton.content = os.path.join(home_dir)
        homeButton.setCursor(PySide2.QtCore.Qt.PointingHandCursor)
        homeButton.clickedContent.connect(self.buttonClicked)

        desktopButton = BiShortcutButton('Desktop', BiThemeAccess.instance().icon('desktop'))
        desktopButton.setObjectName("BiBrowser2DesktopButton")
        desktopButton.content = os.path.join(home_dir, 'Desktop')
        desktopButton.setCursor(PySide2.QtCore.Qt.PointingHandCursor)
        desktopButton.clickedContent.connect(self.buttonClicked)

        documentsButton = BiShortcutButton('Documents', BiThemeAccess.instance().icon('open-folder_negative'))
        documentsButton.setObjectName("BiBrowser2DocumentsButton")
        documentsButton.content = os.path.join(home_dir, 'Documents')
        documentsButton.setCursor(PySide2.QtCore.Qt.PointingHandCursor)
        documentsButton.clickedContent.connect(self.buttonClicked)

        downloadsButton = BiShortcutButton('Downloads', BiThemeAccess.instance().icon('download'))
        downloadsButton.setObjectName("BiBrowser2DownloadsButton")
        downloadsButton.content = os.path.join(home_dir, 'Downloads')
        downloadsButton.setCursor(PySide2.QtCore.Qt.PointingHandCursor)
        downloadsButton.clickedContent.connect(self.buttonClicked)

        layout.addWidget(homeButton)
        layout.addWidget(desktopButton)
        layout.addWidget(documentsButton)
        layout.addWidget(downloadsButton)
        layout.setSpacing(2)

        bookmarkWidget = QWidget(self.wwidget)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        bookmarkWidget.setLayout(self.layout)

        layout.addWidget(bookmarkWidget, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop) 


    def update(self, action: BiAction):
        pass

    def buttonClicked(self, path: str):
        self.container.currentPath = path
        self.container.emit(BiBrowser2States.DirectoryModified)

    def get_widget(self): 
        return self.widget


class BiBrowser2TableComponent(BiComponent):
    def __init__(self, container: BiBrowser2Container):
        super().__init__()
        self._object_name = 'BiBrowser2TableComponent'
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
        self.tableWidget.verticalHeader().setDefaultSectionSize(12)

        labels = ['', 'Name', 'Date', 'Type']
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)

    def update(self, action : BiAction):
        if action.state == BiBrowser2States.FilesInfoLoaded:
            i = -1
            self.tableWidget.setRowCount(len(self.container.files))
            for fileInfo in self.container.files:
                i += 1
                # icon depends on type
                iconLabel = QLabel(self.tableWidget)
                if fileInfo.type == "dir":
                    iconLabel.setObjectName("BiBrowser2DirIcon")
                elif fileInfo.type == "experiment":
                    iconLabel.setObjectName("BiBrowser2ExperimentIcon")

                # icon
                self.tableWidget.setCellWidget(i, 0, iconLabel)
                # name
                self.tableWidget.setItem(i, 1, QTableWidgetItem(fileInfo.name))
                # date
                self.tableWidget.setItem(i, 2, QTableWidgetItem(fileInfo.date))
                # type
                self.tableWidget.setItem(i, 3, QTableWidgetItem(fileInfo.type))
            self.container.emit(BiBrowser2States.TableLoaded)    
            
    def cellDoubleClicked(self, row: int, col: int):
        print('double cliked catched')
        self.container.doubleClickedRow = row
        self.container.emit(BiBrowser2States.ItemDoubleClicked)
        self.highlightLine(row)

    def cellClicked(self, row : int, col : int):
        self.container.clickedRow = row
        self.container.emit(BiBrowser2States.ItemClicked)
        self.highlightLine(row)

    def highlightLine(self, row: int):
        for col in range(0, self.tableWidget.columnCount()):
            self.tableWidget.setCurrentCell(row, col, PySide2.QtCore.QItemSelectionModel.Select)    

    def get_widget(self): 
        return self.widget   
