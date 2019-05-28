import os
import json
import PySide2.QtCore
from PySide2.QtCore import QObject, QDir
from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, 
                            QTextEdit, QGridLayout, QVBoxLayout,
                            QToolButton, QLineEdit, QMessageBox,
                            QHBoxLayout)
from framework import BiObject, BiContainer, BiModel, BiComponent


class BiMetadataEditorContainer(BiContainer):
    FileModified = "BiMetadataEditorContainer::FileModified"
    JsonRead = "BiMetadataEditorContainer::JsonRead"
    JsonWrote = "BiMetadataEditorContainer::JsonWrote"
    JsonModified = "BiMetadataEditorContainer::JsonModified"

    def __init__(self):
        super(BiMetadataEditorContainer, self).__init__()
        self._object_name = 'BiMetadataEditorContainer'
        self.file = ''
        self.content = ''

class BiMetadataEditorModel(BiModel):  
    def __init__(self, container: BiMetadataEditorContainer):
        super(BiMetadataEditorModel, self).__init__()
        self._object_name = 'BiMetadataEditorModel'
        self.container = container
        self.container.addObserver(self)

    def update(self, container: BiContainer):
        if container.action == BiMetadataEditorContainer.FileModified:
            self.read(self.container.file)
            self.container.notify(BiMetadataEditorContainer.JsonRead)
            return

        if container.action == BiMetadataEditorContainer.JsonModified:
            self.write(self.container.file, self.container.content)
            self.container.notify(BiMetadataEditorContainer.JsonWrote)
    
    def read(self, file : str):
        """Read the metadata from the a json file"""
        if os.path.getsize(file) > 0:
            f = open(file, "r")
            self.container.content = f.read()
            f.close()

    def write(self, file : str, content : str ):
        """Write the metadata to the a json file"""
        f = open(file, "w") 
        f.write(self.container.content)
        f.close()        

#class HighlightingRule:
#    def __init__(self):
#        self.pattern = QRegularExpression()
#        self.format = QTextCharFormat()

#class BiHighlighterJson(QSyntaxHighlighter):
#    def __init__(self, parent: QTextDocument):
#        super(BiHighlighterJson, self).__init__(parent)

#        rule = HighlightingRule()

#        self.keywordFormat.setForeground(PySide2.QtCore.Qt.darkBlue)
#        self.keywordFormat.setFontWeight(PySide2.QtCore.QFont.Bold)
#        keywordPatterns = []
#        keywordPatterns.append("common")

#        for pattern in keywordPatterns:
#            rule.pattern = QRegularExpression("\\b"+pattern+"\\b")
#            rule.format = self.keywordFormat
#            self.highlightingRules.append(rule)

#        self.quotationFormat.setForeground(PySide2.QtCore.Qt.darkRed)
#        rule.pattern = QRegularExpression("\".*\"")
#        rule.format = self.quotationFormat
#        self.highlightingRules.append(rule)

#        self.quotationColonFormat.setForeground(PySide2.QtCore.Qt.darkBlue)
#        rule.pattern = QRegularExpression("\".*\":")
#        rule.format = self.quotationColonFormat
#        self.highlightingRules.append(rule)

#        self.colonFormat.setForeground(PySide2.QtCore.Qt.black)
#        rule.pattern = QRegularExpression(":")
#        rule.format = self.colonFormat
#        self.highlightingRules.append(rule)

#        self.extraCommaFormat.setBackground(PySide2.QtCore.Qt.red)
#        rule.pattern = QRegularExpression(",\\s+}")
#        rule.format = self.extraCommaFormat
#        self.highlightingRules.append(rule)

#        self.missingCommaFormat.setBackground(PySide2.QtCore.Qt.red)
#        rule.pattern = QRegularExpression("\"^}")
#        rule.format = self.missingCommaFormat
#        self.highlightingRules.append(rule)

#    def highlightBlock(self, text: str):
#        for rule in self.highlightingRules:
#            matchIterator = rule.pattern.globalMatch(text)
#            while matchIterator.hasNext():
#                match = matchIterator.next()
#                self.setFormat(match.capturedStart(), match.capturedLength(), rule.format)
#        self.setCurrentBlockState(0)


class BiMetadataEditorComponent(BiComponent):
    def __init__(self, container: BiComponent):
        super(BiMetadataEditorComponent, self).__init__()
        self._object_name = 'BiMetadataEditorComponent'
        self.container = container
        self.container.addObserver(self)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()

        self.fileNameLabel = QLabel()
        layout.addWidget(self.fileNameLabel)

        self.textEdit = QTextEdit()
        #self.highlighter = BiHighlighterJson(self.textEdit.document())
        layout.addWidget(self.textEdit)

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

        self.widget.setLayout(layout)

        saveButton.released.connect(self.save)
        cancelButton.released.connect(self.cancel)

    def update(self, container: BiContainer):
        if container.action == BiMetadataEditorContainer.JsonRead:
            print('fill editor with file=', self.container.file)
            self.fileNameLabel.setText(self.container.file)
            self.textEdit.setText(self.container.content)

    def save(self):
        self.container.content = self.textEdit.toPlainText()
        self.container.notify(BiMetadataEditorContainer.JsonModified)

    def cancel(self):
        self.textEdit.setText(self.container.content)

    def get_widget(self):
        return self.widget    
