import PySide2.QtCore
from PySide2.QtGui import QImage, QPixmap, QIcon, QCursor
from PySide2.QtCore import QFileInfo, QDir, Signal, Slot
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel)

from framework import BiStates, BiAction, BiContainer, BiComponent
from widgets import BiClosableButton, BiHideableWidget, BiSlidingStackedWidget

class BiTile():
    def __init__(self):
        self.action = ""
        self.name = ""
        self.tooltip = ""
        self.iconeUrl = ""

class BiTileWidget(QWidget):
    clicked = Signal()
    clickedInfo = Signal(BiTile)

    def __init__(self, info: BiTile, parent: QWidget = None):
        super().__init__(parent)

        self.info = info
        self.buildButton()
        self.setText(self.info.name)
        self.setIcon(self.info.iconeUrl)
        self.etToolTip(self.info.tooltip)


    def buildButton(self):

        wt = QWidget(self)
        tlayout = QVBoxLayout()
        self.setLayout(tlayout)
        tlayout.addWidget(wt)
        wt.setObjectName("BiTileWidgetTile")


        layout = QVBoxLayout()
        layout.setContentsMargins(2,3,2,3)
        layout.setSpacing(0)
        wt.setLayout(layout)

        self.label = QLabel()
        self.label.setObjectName("BiTileButtonLabel")

        self.button = QPushButton()
        self.button.setObjectName("BiTileButton")
        self.button.clicked.connect(self.emitClicked)

        layout.addWidget(self.button, 0, PySide2.QtCore.Qt.AlignBottom )
        layout.addWidget(self.label, 0, PySide2.QtCore.Qt.AlignTop )

        self.setCursor(QCursor(PySide2.QtCore.Qt.PointingHandCursor))
    

    def setText(self, text: str):
        self.label.setText(text)

    def setIcon(self, iconFile: str):
        layout = QVBoxLayout()
        iconLabel = QLabel()

        iconLabel.setPixmap(QPixmap.fromImage(QImage(iconFile)).scaledToHeight(56,PySide2.QtCore.Qt.SmoothTransformation))
        layout.addWidget(iconLabel, 0, PySide2.QtCore.Qt.AlignCenter)
        self.button.setLayout(layout)

    def emitClicked(self):
        self.clicked.emit()
        self.clickedInfo.emit(self.info)


class BiTilesBarWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(QWidget(self), 1, PySide2.QtCore.Qt.AlignTop)

        # global
        layout = QHBoxLayout()
        w = QWidget(self)
        layout.addWidget(w, 1, PySide2.QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(2,2,2,2)
        w.setLayout(self.layout)

        # total
        tlayout = QHBoxLayout()
        wt = QWidget(self)
        tlayout.addWidget(wt, 1, PySide2.QtCore.Qt.AlignHCenter)
        tlayout.setContentsMargins(0,0,0,0)
        wt.setLayout(layout)
        wt.setObjectName("BiTileBar")
        self.setLayout(tlayout)


    def addButton(self, icon: str, toolTip: str, id: int, closable: bool):
        button = BiClosableButton(closable, self)
        button.setCheckable(True)
        button.setIcon(QIcon(icon))
        if toolTip != "":
            button.setToolTip(toolTip)
        button.setId(id)
        self.layout.insertWidget(self.layout.count() -1, button)

        button.clicked.connect(self.open)
        button.closed.connect(self.close)


    def removeButton(self, id: int):
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            button = item.widget()
            if button:
                if button.id() == id:
                    del button
                    return
                    
                # decrease here the id if button after
                elif button.id() > id:
                    button.setId( button.id() -1 )


    def setButtonChecked(self, id: int, clicked: bool = True):
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            button = item.widget()
            if button:
                if button.id() == id:
                    #qDebug() << "set checked id = " << id;
                    if clicked == False:
                        button.setChecked(True)
                else:
                    # qDebug() << "set unchecked id = " << button.id();
                    button.setChecked(False)


class BiTilesBoardWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(QWidget(self), 1, PySide2.QtCore.Qt.AlignTop)
        self.setLayout(self.layout)


    def addSection(self, name: str, strech: int = 0, useFlowLayout: bool = True):
        sectionWidget = BiHideableWidget(name, 2, self, useFlowLayout)
        self.layout.insertWidget(self.layout.count() - 1, sectionWidget, strech, PySide2.QtCore.Qt.AlignTop)
        self.sectionsNames.append(name)
        self.sectionsWidgets.append(sectionWidget)


    def addTile(self, section: str, info: BiTile):
        for i in range(self.sectionsNames.count()):
            if self.sectionsNames[i] == section:
                tile = BiTileWidget(info, self)
                self.sectionsWidgets[i].addWidget(tile)
                tile.clicked.connect(self.action)
                break
            
        
    def addWidget(self, section: str, widget: QWidget):
        for i in range(self.sectionsNames.count()):
            if self.sectionsNames[i] == section:
                self.sectionsWidgets[i].addWidget(widget)
                break


class BiTilesStates(BiStates):
    BarTileClicked = "BiTilesStates.BarTileClicked"
    BarTileCloseClicked = "BiTilesStates.BarTileClicked"
    OpenAppClicked = "BiTilesStates.BarTileClicked"


class BiTilesContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self.tiles = [] #  QList<biTile*>
        self.barClickedIndex = -1
        self.openApp = None # BiTile

    def tilesCount(self):
        return len(self.tiles)

    def tile(self, i: int) -> BiTile:
        return self.tiles[i]

    def addTile(self, tile: BiTile):
        self.tiles.append(tile)

    def clearTiles(self):
        self.tiles = []

    def setBarClickedIndex(self, index: int):
        self.barClickedIndex = index

    def setOpenApp(self, tileInfo: BiTile):
        self.openApp = tileInfo


class BiTilesComponents(BiComponent):
    def __init__(self, container: BiTilesContainer):
        super().__init__()
        self.container = container
        container.register(self)

        # internal 
        self.projectsIndex = -1

        # widget
        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        # global layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        # bar
        self.bar = BiTilesBarWidget(self.widget)
        self.bar.setFixedWidth(44)
        self.centralWidget = BiSlidingStackedWidget(self.widget)

        layout.addWidget(self.bar)
        layout.addWidget(self.centralWidget)

        self.settingIndex = -1
        self.newProjectIndex = -1
        self.m_projectsIndex = -1

        # connections
        self.bar.open.connect(self.showTab)
        self.bar.close.connect(self.closeTab)


    def addSection(self, name: str):
        self.tilesBoard.addSection(name)


    def addTile(self, section: str, info: BiTile):
        self.tilesBoard.addTile(section, info)


    def addTilesBoard(self, icon: str):
        self.bar.addButton(icon, "Home", 0, False)

        self.tilesBoard = BiTilesBoardWidget(self.widget)
        self.centralWidget.addWidget(self.tilesBoard)
        self.bar.setButtonChecked(0, False)

        self.tilesBoard.action.connect(self.openAppEmit)


    def update(self, action: BiAction):
        pass


    def openApp(self, tileInfo: BiTile, widget: QWidget):
        self.settingIndex = self.centralWidget.count()
        self.centralWidget.addWidget(widget)
        self.bar.addButton(tileInfo.iconeUrl, tileInfo.name, self.centralWidget.count()-1, True)

        self.centralWidget.slideInIdx(self.centralWidget.count()-1)
        self.bar.setButtonChecked(self.centralWidget.count()-1, False)


    def openAppEmit(self, tileInfo: BiTile):
        self.container.setOpenApp(tileInfo)
        self.container.emit(BiTilesStates.OpenAppClicked)


    def showTab(self, id: int):
        self.entralWidget.slideInIdx(id)
        self.bar.setButtonChecked(id)


    def closeTab(self, id: int):
        
        if self.centralWidget.currentIndex() == id:
            self.bar.setButtonChecked(id-1, False)
            self.centralWidget.setCurrentIndex(id-1)
        
        if self.settingIndex == id:
            self.settingIndex = -1
        
        if self.projectsIndex == id:
            self.projectsIndex = -1

        self.bar.removeButton(id)
    