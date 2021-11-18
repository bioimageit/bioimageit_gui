import os
import getpass
from pathlib import Path

import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout,
                               QTableWidget, QTableWidgetItem,
                               QAbstractItemView, QHBoxLayout,
                               QToolButton, QSplitter, QLineEdit)

from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.core.theme import BiThemeAccess
from ._states import BiBrowserStates
from ._containers import BiBrowserContainer
from ._widgets import BiShortcutButton


class BiBrowserComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super().__init__()
        self._object_name = 'BiBrowserComponent'
        self.container = container
        self.container.register(self)  

        self.toolBarComponent = BiBrowserToolBarComponent(self.container)
        self.shortCutComponent = BiBrowserShortCutsComponent(self.container)
        self.tableComponent = BiBrowserTableComponent(self.container)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

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
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # previous
        previousButton = QToolButton()
        previousButton.setObjectName("BiBrowserToolBarPreviousButton")
        previousButton.setToolTip(self.widget.tr("Previous"))
        previousButton.released.connect(self.previousButtonClicked)
        layout.addWidget(previousButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # next
        nextButton = QToolButton()
        nextButton.setObjectName("BiBrowserToolBarNextButton")
        nextButton.setToolTip(self.widget.tr("Next"))
        nextButton.released.connect(self.nextButtonClicked)
        layout.addWidget(nextButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # up
        upButton = QToolButton()
        upButton.setObjectName("BiBrowserToolBarUpButton")
        upButton.setToolTip(self.widget.tr("Tags"))
        upButton.released.connect(self.upButtonClicked)
        layout.addWidget(upButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # up
        refreshButton = QToolButton()
        refreshButton.setObjectName("BiBrowserToolBarRefreshButton")
        refreshButton.setToolTip(self.widget.tr("Tags"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # data selector
        self.pathLineEdit = QLineEdit(self.widget)
        self.pathLineEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.pathLineEdit.returnPressed.connect(self.pathEditReturnPressed)
        layout.addWidget(self.pathLineEdit, 1)

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

    def get_widget(self): 
        return self.widget            
       

class BiBrowserShortCutsComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super(BiBrowserShortCutsComponent, self).__init__()
        self._object_name = 'BiBrowserShortCutsComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(mainLayout)

        self.wwidget = QWidget()
        mainLayout.addWidget(self.wwidget)
        self.wwidget.setObjectName("BiLeftBar")
        self.wwidget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        self.wwidget.setLayout(layout)

        home_dir = Path.home() 
        username = getpass.getuser()

        homeButton = BiShortcutButton(username, BiThemeAccess.instance().icon('home'))
        homeButton.setObjectName("BiBrowserHomeButton")
        homeButton.content = os.path.join(home_dir)
        homeButton.setCursor(qtpy.QtCore.Qt.PointingHandCursor)
        homeButton.clickedContent.connect(self.buttonClicked)

        desktopButton = BiShortcutButton('Desktop', BiThemeAccess.instance().icon('desktop'))
        desktopButton.setObjectName("BiBrowserDesktopButton")
        desktopButton.content = os.path.join(home_dir, 'Desktop')
        desktopButton.setCursor(qtpy.QtCore.Qt.PointingHandCursor)
        desktopButton.clickedContent.connect(self.buttonClicked)

        documentsButton = BiShortcutButton('Documents', BiThemeAccess.instance().icon('open-folder_negative'))
        documentsButton.setObjectName("BiBrowserDocumentsButton")
        documentsButton.content = os.path.join(home_dir, 'Documents')
        documentsButton.setCursor(qtpy.QtCore.Qt.PointingHandCursor)
        documentsButton.clickedContent.connect(self.buttonClicked)

        downloadsButton = BiShortcutButton('Downloads', BiThemeAccess.instance().icon('download'))
        downloadsButton.setObjectName("BiBrowserDownloadsButton")
        downloadsButton.content = os.path.join(home_dir, 'Downloads')
        downloadsButton.setCursor(qtpy.QtCore.Qt.PointingHandCursor)
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

        layout.addWidget(bookmarkWidget, 0, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop) 


    def update(self, action: BiAction):
        pass

    def buttonClicked(self, path: str):
        self.container.currentPath = path
        self.container.emit(BiBrowserStates.DirectoryModified)

    def get_widget(self): 
        return self.widget


class BiBrowserTableComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super().__init__()
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
        self.tableWidget.verticalHeader().setDefaultSectionSize(12)

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
                elif fileInfo.type == "experiment":
                    iconLabel.setObjectName("BiBrowserExperimentIcon")

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
        for col in range(0, self.tableWidget.columnCount()):
            self.tableWidget.setCurrentCell(row, col, qtpy.QtCore.QItemSelectionModel.Select)    

    def get_widget(self): 
        return self.widget   
