import PySide2.QtCore
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtCore import QFileInfo, QDir, Signal
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QTableWidget, QTableWidgetItem, QAbstractItemView,
                               QGridLayout, QHBoxLayout, QToolButton, QSplitter, 
                               QLineEdit, QPushButton, QTextEdit, QMessageBox, QFileDialog)

from bioimageapp.core.framework import BiComponent, BiAction
from bioimageapp.metadata.states import BiMetadataStates, BiMetadataEditorStates
from bioimageapp.metadata.containers import BiMetadataContainer, BiMetadataEditorContainer                               

class BiMetadataPreviewComponent(BiComponent):
    def __init__(self, container: BiMetadataContainer):
        super().__init__()
        self._object_name = 'BiBrowserPreviewComponent'
        self.container = container
        self.container.register(self)

        self.buildWidget()

    def buildWidget(self):

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        self.textEdit = QTextEdit(self.widget)
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit, 0, 0, 1, 2)

        self.name = QLabel(self.widget)
        layout.addWidget(QLabel(self.widget.tr("Name:")), 1, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.name, 1, 1, PySide2.QtCore.Qt.AlignTop)

        self.type = QLabel(self.widget)
        layout.addWidget(QLabel(self.widget.tr("Type:")), 2, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.type, 2, 1, PySide2.QtCore.Qt.AlignTop)

        self.date = QLabel(self.widget)
        layout.addWidget(QLabel(self.widget.tr("Date:")), 3, 0, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.date, 3, 1, PySide2.QtCore.Qt.AlignTop)

        openButton = QPushButton(self.widget.tr("Open"), self.widget)
        openButton.setObjectName("btnDefault")
        layout.addWidget(openButton, 4, 0, 1, 2, PySide2.QtCore.Qt.AlignTop)
        openButton.released.connect(self.openButtonClicked)

        layout.addWidget(QWidget(self.widget), 5, 0, 1, 2)

    def update(self, action: BiAction):
        if action.state == BiMetadataStates.URIChanged:
            fileInfo = QFileInfo(self.container.md_uri)
            self.textEdit.setText(self.fileContentPreview(fileInfo.filePath()))
            self.name.setText(fileInfo.fileName())
            #self.type.setText(fileInfo.type)
            self.date.setText(fileInfo.lastModified().toString("yyyy-MM-dd"))
    
    def fileContentPreview(self, filename: str) -> str:
        with open(filename, 'r') as file:
            data = file.read()
        return data

    def openButtonClicked(self):
        self.container.emit(BiMetadataStates.OpenClicked)

    def get_widget(self): 
        return self.widget                 


class BiMetadataJsonEditorComponent(BiComponent):
    def __init__(self, container: BiMetadataEditorContainer, readOnly :bool = False):
        super().__init__()
        self._object_name = 'BiMetadataEditorComponent'
        self.container = container
        self.container.register(self)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()

        self.fileNameLabel = QLabel()
        layout.addWidget(self.fileNameLabel)

        self.textEdit = QTextEdit()
        if readOnly:
            self.textEdit.setEnabled(False)
        #self.highlighter = BiHighlighterJson(self.textEdit.document())
        layout.addWidget(self.textEdit)

        if not readOnly:
            buttonWidget = QWidget()

            saveButton = QPushButton(self.widget.tr("Save"))
            saveButton.setObjectName("btnPrimary")
            cancelButton = QPushButton(self.widget.tr("Cancel"))
            cancelButton.setObjectName("btnDefault")
            buttonLayout = QHBoxLayout()
            buttonLayout.addWidget(cancelButton, 1, PySide2.QtCore.Qt.AlignRight)
            buttonLayout.addWidget(saveButton, 0, PySide2.QtCore.Qt.AlignRight)
            buttonWidget.setLayout(buttonLayout)

            layout.addWidget(buttonWidget)

            saveButton.released.connect(self.save)
            cancelButton.released.connect(self.cancel)

        self.widget.setLayout(layout)

        
    def update(self, action: BiAction):
        if action.state == BiMetadataEditorStates.JsonRead:
            self.fileNameLabel.setText(self.container.file)
            self.textEdit.setText(self.container.content)

    def save(self):
        self.container.content = self.textEdit.toPlainText()
        self.container.emit(BiMetadataEditorStates.JsonModified)

    def cancel(self):
        self.textEdit.setText(self.container.content)

    def get_widget(self):
        return self.widget