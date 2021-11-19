import webbrowser
import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem,
                               QAbstractItemView,
                               QSplitter, QPushButton)

from bioimageit_gui.core.widgets import (BiButton, BiFlowLayout,
                                         BiNavigationBar)

from bioimageit_gui.core.framework import BiComponent, BiAction
from bioimageit_gui.finder.states import BiFinderStates
from bioimageit_gui.finder.containers import BiFinderContainer
from bioimageit_gui.finder.widgets import BiProcessCategoryTile


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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)
        
        # NavBar
        self.navBar = BiNavigationBar(self.widget)
        self.navBar.previousSignal.connect(self.moveToPrevious)
        self.navBar.nextSignal.connect(self.moveToNext)
        self.navBar.homeSignal.connect(self.moveToHome)
        layout.addWidget(self.navBar, 0, qtpy.QtCore.Qt.AlignTop)

        # Browse area
        browseWidget = QWidget()
        browseWidget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        browseWidget.setObjectName("BiWidget")
        self.scrollWidget = QScrollArea()
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setWidget(browseWidget)
        layout.addWidget(self.scrollWidget, 1)
        
        self.layout = BiFlowLayout()
        browseWidget.setLayout(self.layout)

        # tools table
        self.toolsWidget = QWidget()
        self.toolsWidget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground,
                                      True)
        self.toolsWidget.setObjectName("BiWidget")
        toolsLayout = QVBoxLayout()
        self.toolsWidget.setLayout(toolsLayout)
        layout.addWidget(self.toolsWidget, 1)
         
        # table
        toolsListWidget = QWidget()
        toolsLayout.addWidget(toolsListWidget)  
        toolsListLayout = QVBoxLayout()
        toolsListLayout.setContentsMargins(0, 0, 7, 0)
        toolsListWidget.setLayout(toolsListLayout)

        tutorialButton = QPushButton("Tutorial")
        toolsListLayout.addWidget(tutorialButton)
        tutorialButton.setObjectName("btnDefault")
        tutorialButton.released.connect(self.showToolboxDoc)

        self.tableWidget = QTableWidget()
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSizeAdjustPolicy(qtpy.QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setColumnCount(4)
        labels = ["", "Name", "Version", "Documentation"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        toolsListLayout.addWidget(self.tableWidget)

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
        i = -1
        for info in self.container.tools:   
            i += 1
            open_ = BiButton(self.widget.tr("Open"))
            # open.id = i
            open_.content = info.uri
            open_.setObjectName("btnTableDefault")
            open_.clickedContent.connect(self.openClicked)

            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.setCellWidget(i, 0, open_)

            self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(info.version))  
            link = info.help

            docLabel = QLabel()
            docLabel.setOpenExternalLinks(True)
            docLabel.setText(f'<span><p><a href="{link}">{link}</a></p></span>')
            self.tableWidget.setCellWidget(i, 3, docLabel)
   
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setCurrentCell(0, 1)

    def browseCategories(self):
        # free layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
 
        # browse
        for category in self.container.categories:
            widget = BiProcessCategoryTile(category, self.widget)
            widget.clickedSignal.connect(self.clickedTile)
            self.layout.addWidget(widget)

    def showToolboxDoc(self):
        webbrowser.open(self.container.current_category_doc)
        print("TODO, open the doc:", self.container.current_category_doc)

    def clickedTile(self, info):
        self.container.setCurrentCategory(info.id, info.name, info.doc)
        self.container.emit(BiFinderStates.Reload)  

    def openClicked(self, id_: str):
        self.container.clicked_tool = id_
        self.container.emit(BiFinderStates.OpenProcess)   

    def update(self, action: BiAction):
        if action.state == BiFinderStates.Reloaded:
            self.navBar.set_path(self.container.curent_category_name)
            self.browse()
            return

    def get_widget(self):
        return self.widget
