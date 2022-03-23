import os
import getpass
from pathlib import Path

import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon, QPixmap, QImage
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout,
                            QTableWidget, QTableWidgetItem,
                            QAbstractItemView, QHBoxLayout,
                            QToolButton, QSplitter, QLineEdit,
                            QPushButton, QMessageBox, QScrollArea)

from bioimageit_core import ConfigAccess
from bioimageit_core.api import APIAccess

from bioimageit_framework.framework import BiComponent, BiConnectome
from bioimageit_framework.widgets import BiWidget, QtContentButton
from bioimageit_framework.theme import BiThemeAccess

from ._containers import BiBrowserContainer
from ._widgets import BiShortcutButton
from ._models import BiBrowserModel


def get_experiment_selector_widget():
    if ConfigAccess.instance().config['metadata']['service'] == 'LOCAL':
        return BiExperimentLocalSelectorWidget()
    else:
        return BiExperimentSelectorWidget()


class BiExperimentSelectorWidget(BiWidget):
    SELECTED_EXP = "selected_experiment"

    def __init__(self) -> None:
        super().__init__()
        self.container = BiBrowserContainer()
        self.selected_path = ''
        self.selected_name = ''

        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)

        widget = QWidget()
        self.widget.setWidget(widget)
        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)
        self.refresh()

    def refresh(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        experiments = APIAccess.instance().get_workspace_experiments()
        for experiment in experiments:
            experiment_btn = QtContentButton(experiment['info'].name)
            experiment_btn.id = str(experiment['md_uri'])
            experiment_btn.content = str(experiment['info'].name)
            experiment_btn.clickedInfo.connect(self.selected)
            self.layout.addWidget(experiment_btn)

    def selected(self, id, content):
        self.selected_path = id
        self.selected_name = content
        self.emit(BiExperimentSelectorWidget.SELECTED_EXP)        


class BiExperimentLocalSelectorWidget(BiWidget):
    SELECTED_EXP = "selected_experiment"

    def __init__(self):
        super().__init__()
        self.container = BiBrowserContainer()
        self.selected_path = ''
        self.selected_name = ''
        # components
        browser_component = BiBrowserComponent(self.container)

        # model
        self.browser_model = BiBrowserModel()

        # connect
        #BiConnectome.connect(self.container, browser_component)
        BiConnectome.connect(self.container, self.browser_model)

        # init
        workspace_path = ConfigAccess.instance().get('workspace')
        self.container.init(workspace_path)

        # validation bar
        validation_bar = QWidget()
        validation_bar.setObjectName("bi-toolbar")
        validation_bar.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        bar_layout = QHBoxLayout()
        validation_bar.setLayout(bar_layout)

        validation_button = QPushButton('Open')
        validation_button.setObjectName('btn-primary')
        validation_button.released.connect(self.validate_clicked)
        bar_layout.addWidget(validation_button, 1, qtpy.QtCore.Qt.AlignRight)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget = QWidget()
        self.widget.setLayout(layout)
        layout.addWidget(browser_component.get_widget(), 1)
        layout.addWidget(validation_bar, 0, qtpy.QtCore.Qt.AlignBottom)

    def validate_clicked(self):
        path = os.path.join(self.container.currentPath, self.container.files[self.container.clickedRow].name)
        experiment_uri = os.path.join(path, 'experiment.md.json')
        if os.path.isfile(experiment_uri):
            self.selected_path = path
            self.selected_name = path
            self.emit(BiExperimentSelectorWidget.SELECTED_EXP)
            #self.selected_experiment.emit(path)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setInformativeText(f"The directory {path} is not an experiment")
            msg.setWindowTitle("Browser error")
            msg.exec_()


class BiBrowserComponent(BiComponent):
    def __init__(self, container: BiBrowserContainer):
        super().__init__()
        self._object_name = 'BiBrowserComponent'

        self.toolBarComponent = BiBrowserToolBarComponent()
        self.shortCutComponent = BiBrowserShortCutsComponent()
        self.tableComponent = BiBrowserTableComponent()

        BiConnectome.connect(container, self.toolBarComponent)
        BiConnectome.connect(container, self.shortCutComponent)
        BiConnectome.connect(container, self.tableComponent)

        self.widget = QWidget()
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


class BiBrowserToolBarComponent(BiComponent):
    PREVIOUS = 'previous'
    NEXT = 'next'
    UP = 'up'
    CHANGE_DIR = 'change_dir'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiBrowserToolBarComponent'

        # build widget
        self.widget = QWidget()
        self.widget.setObjectName("bi-toolbar")
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # previous
        previousButton = QToolButton()
        previousButton.setIcon(QIcon(BiThemeAccess.instance().icon('arrow-left')))
        previousButton.setObjectName("BiBrowserToolBarPreviousButton")
        previousButton.setToolTip(self.widget.tr("Previous"))
        previousButton.released.connect(self.previousButtonClicked)
        layout.addWidget(previousButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # next
        nextButton = QToolButton()
        nextButton.setIcon(QIcon(BiThemeAccess.instance().icon('arrow-right')))
        nextButton.setToolTip(self.widget.tr("Next"))
        nextButton.released.connect(self.nextButtonClicked)
        layout.addWidget(nextButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # up
        upButton = QToolButton()
        upButton.setIcon(QIcon(BiThemeAccess.instance().icon('arrow-up')))
        upButton.setToolTip(self.widget.tr("Up"))
        upButton.released.connect(self.upButtonClicked)
        layout.addWidget(upButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # up
        refreshButton = QToolButton()
        refreshButton.setIcon(QIcon(BiThemeAccess.instance().icon('arrow-refresh')))
        refreshButton.setToolTip(self.widget.tr("Refresh"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # data selector
        self.pathLineEdit = QLineEdit(self.widget)
        self.pathLineEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.pathLineEdit.returnPressed.connect(self.pathEditReturnPressed)
        layout.addWidget(self.pathLineEdit, 1)

    def callback_reloaded(self, emitter):
        self.pathLineEdit.setText(emitter.currentPath)            

    def previousButtonClicked(self):
        self._emit(BiBrowserToolBarComponent.PREVIOUS)

    def nextButtonClicked(self):
        self._emit(BiBrowserToolBarComponent.NEXT)

    def upButtonClicked(self):
        self._emit(BiBrowserToolBarComponent.UP)

    def pathEditReturnPressed(self):
        self._emit(BiBrowserToolBarComponent.CHANGE_DIR, self.pathLineEdit.text())

    def refreshButtonClicked(self):
        self._emit(BiBrowserToolBarComponent.CHANGE_DIR, self.pathLineEdit.text())         
       

class BiBrowserShortCutsComponent(BiComponent):
    CHANGE_DIR = 'change_dir'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiBrowserShortCutsComponent'

        self.widget = QWidget()
        
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(mainLayout)

        self.wwidget = QWidget()
        mainLayout.addWidget(self.wwidget)
        self.wwidget.setObjectName("bi-left-bar")
        self.wwidget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        self.wwidget.setLayout(layout)

        home_dir = Path.home() 
        username = getpass.getuser()

        homeButton = BiShortcutButton(username, BiThemeAccess.instance().icon('home'))
        homeButton.content = os.path.join(home_dir)
        homeButton.setCursor(qtpy.QtCore.Qt.PointingHandCursor)
        homeButton.clickedContent.connect(self.buttonClicked)

        desktopButton = BiShortcutButton('Desktop', BiThemeAccess.instance().icon('desktop'))
        desktopButton.content = os.path.join(home_dir, 'Desktop')
        desktopButton.setCursor(qtpy.QtCore.Qt.PointingHandCursor)
        desktopButton.clickedContent.connect(self.buttonClicked)

        documentsButton = BiShortcutButton('Documents', BiThemeAccess.instance().icon('open-folder-dark'))
        documentsButton.content = os.path.join(home_dir, 'Documents')
        documentsButton.setCursor(qtpy.QtCore.Qt.PointingHandCursor)
        documentsButton.clickedContent.connect(self.buttonClicked)

        downloadsButton = BiShortcutButton('Downloads', BiThemeAccess.instance().icon('download'))
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

    def buttonClicked(self, path: str):
        self._emit(BiBrowserShortCutsComponent.CHANGE_DIR, path)

    def get_widget(self): 
        return self.widget


class BiBrowserTableComponent(BiComponent):
    DOUBLE_CLICKED_ROW = 'double_clicked_row'
    CLICKED_ROW = 'clicked_row'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiBrowserTableComponent'
        self.buildWidget()

    def buildWidget(self):
        self.widget = QWidget()

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

    def callback_reloaded(self, emitter):
        i = -1
        self.tableWidget.setRowCount(len(emitter.files))
        for fileInfo in emitter.files:
            i += 1
            # icon depends on type
            iconLabel = QLabel(self.tableWidget)
            icon_file = ''
            if fileInfo.type == "dir":
                icon_file = BiThemeAccess.instance().icon('folder-dark')
            elif fileInfo.type == "experiment":
                icon_file = BiThemeAccess.instance().icon('database')
            img = QImage(icon_file)
            iconLabel.setPixmap(QPixmap.fromImage(img.scaled(15, 15, qtpy.QtCore.Qt.KeepAspectRatio)))
            # icon
            self.tableWidget.setCellWidget(i, 0, iconLabel)
            # name
            self.tableWidget.setItem(i, 1, QTableWidgetItem(fileInfo.name))
            # date
            self.tableWidget.setItem(i, 2, QTableWidgetItem(fileInfo.date))
            # type
            self.tableWidget.setItem(i, 3, QTableWidgetItem(fileInfo.type))
        #self.container.emit(BiBrowserStates.TableLoaded)    
            
    def cellDoubleClicked(self, row: int, col: int):
        self._emit(BiBrowserTableComponent.DOUBLE_CLICKED_ROW, row)
        self.highlightLine(row)

    def cellClicked(self, row : int, col : int):
        self._emit(BiBrowserTableComponent.CLICKED_ROW, row)
        self.highlightLine(row)

    def highlightLine(self, row: int):
        for col in range(0, self.tableWidget.columnCount()):
            self.tableWidget.setCurrentCell(row, col, qtpy.QtCore.QItemSelectionModel.Select)     
