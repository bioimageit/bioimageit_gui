import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import QFileInfo, QDir, Signal
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QHBoxLayout, QToolButton, QSplitter)

from bioimageapp.core.widgets import BiButton, BiFlowLayout, BiNavigationBar, BiWebBrowser

from bioimageapp.core.framework import BiComponent, BiAction
from bioimageapp.finder.states import BiFinderStates
from bioimageapp.finder.containers import BiFinderContainer
from bioimageapp.finder.widgets import BiProcessCategoryTile

class BiFinderComponent(BiComponent):
    def __init__(self, container: BiFinderContainer):
        super().__init__()
        self._object_name = 'BiFinderComponent'
        self.container = container
        self.container.register(self)  
        self.historyPaths = []
        self.posHistory = 0
        self.currentPath = ''

        # Widget
        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)
        
        # NavBar
        self.navBar = BiNavigationBar(self.widget)
        self.navBar.previousSignal.connect(self.moveToPrevious)
        self.navBar.nextSignal.connect(self.moveToNext)
        self.navBar.homeSignal.connect(self.moveToHome)
        layout.addWidget(self.navBar, 0, PySide2.QtCore.Qt.AlignTop)

        # Browse area
        browseWidget = QWidget()
        browseWidget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        browseWidget.setObjectName("BiWidget")
        self.scrollWidget = QScrollArea()
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setWidget(browseWidget)
        layout.addWidget(self.scrollWidget, 1)
        
        self.layout = BiFlowLayout()
        browseWidget.setLayout(self.layout)

        # tools table
        self.toolsWidget = QWidget()
        self.toolsWidget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        self.toolsWidget.setObjectName("BiWidget")
        toolsLayout = QVBoxLayout()
        self.toolsWidget.setLayout(toolsLayout)
        layout.addWidget(self.toolsWidget, 1)

        toolsSplitter = QSplitter() 
        toolsLayout.addWidget(toolsSplitter)   

        # table
        self.tableWidget = QTableWidget()
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.cellClicked.connect(self.showClickedDoc)
        labels = ["Open", "Name", "Version"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        toolsSplitter.addWidget(self.tableWidget)

        # doc viewer
        self.docViewer = BiWebBrowser(self.toolsWidget)
        self.docViewer.setToolBarVisible(False)
        toolsSplitter.addWidget(self.docViewer)
    
        self.toolsWidget.setVisible(False)

    def moveToPrevious(self):
        self.container.movePrevious()
        self.container.emit(BiFinderStates.Reload)

    def moveToNext(self):
        self.container.moveNext()
        self.container.emit(BiFinderStates.Reload)

    def moveToHome(self):
        self.container.moveHome()  
        self.container.emit(BiFinderStates.Reload)      

    def browse(self):
        if len(self.container.categories) > 0:
            self.browseCategories()
            self.toolsWidget.setVisible(False)
            self.scrollWidget.setVisible(True)
        else:
            self.browseTools()  
            self.toolsWidget.setVisible(True)
            self.scrollWidget.setVisible(False)      

    def browseTools(self):
        self.tableWidget.setRowCount(0)
        i= -1    
        for info in self.container.tools:   
            i += 1
            open = BiButton(self.widget.tr("Open"))
            #open.id = i
            open.content = info.uri
            open.setObjectName("btnDefault")
            open.clickedContent.connect(self.openClicked)

            self.tableWidget.insertRow( self.tableWidget.rowCount() )
            self.tableWidget.setCellWidget(i, 0, open)    

            self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(info.version))  
   
        self.tableWidget.setCurrentCell(0,1)   
        self.showClickedDoc(0, 1)

    def browseCategories(self):

        # free layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
 
        # browse
        for category in self.container.categories:
            widget = BiProcessCategoryTile(category, self.widget)
            widget.clickedSignal.connect(self.clickedTile)
            self.layout.addWidget(widget)

    def clickedTile(self, info: dict):
        self.container.setCurrentCategory(info.id, info.name)
        self.container.emit(BiFinderStates.Reload)  

    def openClicked(self, id: str):
        self.container.clicked_tool = id
        self.container.emit(BiFinderStates.OpenProcess)   

    def showClickedDoc(self, row, column):
        if row >= len(self.container.tools):
             self.docViewer.setHomePageHtml("No tool available")
             return
        tool = self.container.tools[row]  
        if tool.help.startswith('http') or tool.help.startswith('www'):
            self.docViewer.setHomePage(tool.help, True)
        elif tool.help.endswith('.html'):    
            self.docViewer.setHomePage(tool.help, False)
        else:
            self.docViewer.setHomePageHtml("<span>This tool documentation is not available</span>")           


    def update(self, action: BiAction):
        if (action.state == BiFinderStates.Reloaded):
            self.navBar.set_path(self.container.curent_category_name)
            self.browse()
            return

    def get_widget(self):
        return self.widget 