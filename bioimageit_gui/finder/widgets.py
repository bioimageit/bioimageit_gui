import os
import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtGui import QPixmap, QImage
from qtpy.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                            QTableWidget, QTableWidgetItem,
                            QAbstractItemView, QPushButton)

from bioimageit_framework.widgets.qtwidgets import QtFlowLayout, QtContentButton
from bioimageit_framework.widgets import BiWidget
from bioimageit_core.containers.tools_containers import ToolsCategoryContainer


class BiProcessCategoryTile(QWidget):
    clickedSignal = Signal(ToolsCategoryContainer)

    def __init__(self, category: ToolsCategoryContainer,
                 parent: QWidget = None):
        super().__init__(parent)
        self.category = category

        self.setCursor(qtpy.QtGui.QCursor(
            qtpy.QtCore.Qt.PointingHandCursor))

        glayout = QVBoxLayout()
        self.setLayout(glayout)

        widget = QWidget()
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("bi-finder-category-tile")
        glayout.addWidget(widget)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)

        titleLabel = QLabel()
        titleLabel.setObjectName("bi-finder-category-tile-title")
        titleLabel.setAlignment(qtpy.QtCore.Qt.AlignCenter)
        titleLabel.setText(category.name)
        layout.addWidget(titleLabel, 0, qtpy.QtCore.Qt.AlignTop)

        thumbnailLabel = QLabel()

        img = QImage(os.path.join(category.thumbnail))
        #print(os.path.join(category.thumbnail))
        thumbnailLabel.setPixmap(QPixmap.fromImage(img.scaled(200, 200, qtpy.QtCore.Qt.KeepAspectRatio)))
        thumbnailLabel.setObjectName("bi-finder-category-tile-thumb")
        layout.addWidget(thumbnailLabel, 0, qtpy.QtCore.Qt.AlignTop | qtpy.QtCore.Qt.AlignHCenter)

        layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop)
        widget.setObjectName("bi-finder-category-tile")

    def mousePressEvent(self, event):
        self.clickedSignal.emit(self.category)


class BiCategoriesBrowser(BiWidget):
    OPEN = 'OPEN'

    def __init__(self):
        super().__init__()
        self.clicked_info = None
        browseWidget = QWidget()
        browseWidget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        #browseWidget.setObjectName("BiWidget")
        self.scrollWidget = QScrollArea()
        self.scrollWidget.setWidgetResizable(True)
        self.scrollWidget.setWidget(browseWidget)

        layout = QVBoxLayout()
        layout.addWidget(self.scrollWidget, 1)
        self.widget.setLayout(layout)
        
        self.layout = QtFlowLayout()
        browseWidget.setLayout(self.layout)

    def browse(self, categories):
        # free layout
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().deleteLater()
        # browse
        for category in categories:
            widget = BiProcessCategoryTile(category, self.widget)
            widget.clickedSignal.connect(self.open_tile)
            self.layout.addWidget(widget)    

    def open_tile(self, info):
        self.clicked_info = info
        self.emit(BiCategoriesBrowser.OPEN)

class BiToolsBrowser(BiWidget):
    OPEN = 'open'

    def __init__(self):
        super().__init__()
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        #self.widget.setObjectName("BiWidget")
        toolsLayout = QVBoxLayout()
        self.widget.setLayout(toolsLayout)
         
        # table
        toolsListWidget = QWidget()
        toolsLayout.addWidget(toolsListWidget)  
        toolsListLayout = QVBoxLayout()
        toolsListLayout.setContentsMargins(0, 0, 7, 0)
        toolsListWidget.setLayout(toolsListLayout)

        tutorialButton = QPushButton("Tutorial")
        toolsListLayout.addWidget(tutorialButton)
        tutorialButton.setObjectName("btnDefault")
        tutorialButton.released.connect(self.show_toolbox_doc)

        self.tableWidget = QTableWidget()
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSizeAdjustPolicy(qtpy.QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setColumnCount(4)
        labels = ["", "Name", "Version", "Documentation"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        toolsListLayout.addWidget(self.tableWidget)

    def browse(self, tools):
        self.tableWidget.setRowCount(0)
        i = -1
        for info in tools:   
            i += 1
            open_ = QtContentButton(self.widget.tr("Open"))
            open_.content = info.uri
            open_.setObjectName("btnTableDefault")
            open_.clickedContent.connect(self.open_clicked)

            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.setCellWidget(i, 0, open_)

            self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(info.version))  
            link = info.help

            docLabel = QLabel()
            docLabel.setOpenExternalLinks(True)
            docLabel.setText(f'<span><p><a style="color: #f0f1f2" href="{link}">{link}</a></p></span>')
            self.tableWidget.setCellWidget(i, 3, docLabel)
   
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setCurrentCell(0, 1)    

    def open_clicked(self, id):
        self.clicked_id = id
        self.emit(BiToolsBrowser.OPEN)

    def show_toolbox_doc(self):
        print('doc clicked not yet implemented')    
