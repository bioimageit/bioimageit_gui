import os
import json
import sys

import PySide2.QtCore
from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout, 
                               QLabel, QComboBox, QSpinBox, QLineEdit,
                               QMessageBox) 

from widgets import BiFileSelectWidget                               


class BiFormFields():
    TypeString = "string"
    TypeNumber = "number"
    TypeBool = "bool"
    TypeSelect = "select"
    TypeFile = "file"
    TypeDir = "dir"

    def __init__(self, file: str = ''):
        self.file = file
        self.data = dict()
        if os.path.isfile(file):
            self.read()
        
    def read(self):
        """Read the settings from the a json file at file"""
        if os.path.getsize(self.file) > 0:
            with open(self.file) as json_file:  
                self.data = json.load(json_file)

    def write(self):
        """Write the settings to the a json file at file"""
        with open(self.file, 'w') as outfile:
            json.dump(self.data, outfile, indent=4)  

    def sections(self):
        keys = []
        for key in self.data:
            keys.append(key)
        return keys  

    def set(self, section: str, key: str, type: type, value: str) -> bool:
        found = False
        for entry in self.data[section]:
            if entry["key"] == key:
                found = True
                entry["type"] = type
                entry["value"] = value

        return found 

    def add(self, section: str, key: str, type: type, value: str):
        if section not in self.data:
            self.data[section] = list()

        self.data[section].append({"key": key, "type": type, "value": value})
       
    def get(self, section: str) -> dict:
        return self.data[section]

    def value(self, section: str, key: str) -> str:
        if self.data[section][key]:
            return self.data[section][key]
        return ''


class BiFormContent():
    def __init__(self, file: str = ''):
        self.file = file
        self.data = dict()
        if os.path.isfile(file):
            self.read()
        
    def read(self):
        """Read the settings from the a json file at file"""
        if os.path.getsize(self.file) > 0:
            with open(self.file) as json_file:  
                self.data = json.load(json_file)

    def write(self):
        """Write the settings to the a json file at file"""
        with open(self.file, 'w') as outfile:
            json.dump(self.data, outfile, indent=4) 

    def get(self, section: str, key: str):
        if section in self.data:
            if key in self.data[section]:
                return self.data[section][key]
        return ''

    def set(self, section: str, key: str, value: str):
        if section not in self.data:
            self.data[section] = dict()        
        
        self.data[section][key] = value                


class BiFormWidget(QWidget):
    saveClickedSignal = Signal()
    cancelClickedSignal = Signal()

    def __init__(self, fields : BiFormFields, content : BiFormContent, useButtons: bool = True):
        super(BiFormWidget, self).__init__()
        self.fields = fields
        self.content = content

        self.setObjectName("BiWidget")
        layout = QGridLayout()
        self.setLayout(layout)
        self.widgets = {}
        

        sections = fields.sections()
        line = 0
        for section in sections:

            line += 1
            titleLabel = QLabel(section)
            titleLabel.setObjectName("BiLabelFormHeader1")
            layout.addWidget(titleLabel, line, 0, 1, 3)

            for i in range(0,len(fields.data[section])):
                line += 1

                setting = fields.data[section][i]
                key = setting['key']
                ttype = setting['type']

                value = self.content.get(section, key)
                if value == '':
                    value = setting['value']

                title = QLabel(key)
                title.setObjectName("BiWidget")
                layout.addWidget(title, line, 0)

                settingId = section + "::" + key

                if ttype == BiFormFields.TypeString:
                    edit = QLineEdit()
                    edit.setText(value)
                    layout.addWidget(edit, line, 1, 1, 2)
                    self.widgets[settingId] = edit
                elif ttype == BiFormFields.TypeNumber:
                    spinBox = QSpinBox()
                    if "maximum" in setting:
                        spinBox.setMaximum(setting["maximum"])
                    if "minimum" in setting:
                        spinBox.setMinimum(setting["minimum"])    
                    spinBox.setValue(int(value))
                    layout.addWidget(spinBox, line, 1, 1, 2)
                    self.widgets[settingId] = spinBox
                elif ttype == BiFormFields.TypeBool:
                    comboBox = QComboBox()
                    comboBox.addItem("true")
                    comboBox.addItem("false")
                    comboBox.setCurrentText(value)
                    layout.addWidget(comboBox, line, 1, 1, 2)
                    self.widgets[settingId] = comboBox
                elif ttype == BiFormFields.TypeSelect:
                    comboBox = QComboBox()
                    if "choices" in setting:
                        comboBox.addItems(setting['choices'])
                    comboBox.setCurrentText(value)
                    layout.addWidget(comboBox, line, 1, 1, 2)
                    self.widgets[settingId] = comboBox
                elif ttype == BiFormFields.TypeFile:
                    fileWidget = BiFileSelectWidget(False, None)
                    fileWidget.setText(value)
                    layout.addWidget(fileWidget, line, 1, 1, 2)
                    self.widgets[settingId] = fileWidget
                elif ttype == BiFormFields.TypeDir:
                    fileWidget = BiFileSelectWidget(True, None)
                    fileWidget.setText(value)
                    layout.addWidget(fileWidget, line, 1, 1, 2)
                    self.widgets[settingId] = fileWidget
                else:
                    print(ttype, " is not a known settings type")
                line += 1

        if useButtons:
            saveButton = QPushButton(self.tr("Save"))
            cancelButton = QPushButton(self.tr("Cancel")) 

            saveButton.released.connect(self.saveClicked)
            cancelButton.released.connect(self.cancelClicked)

            layout.addWidget(saveButton, line, 1, 1, 1) 
            layout.addWidget(cancelButton, line, 2, 1, 1)       

    def extractContent(self):
        for key, widget in self.widgets.items():

            settingId = key.split("::")
            settingSection = settingId[0]
            settingKey = settingId[1]

            if widget:
                if type(widget).__name__ == 'QLineEdit':
                    self.content.set(settingSection, settingKey, widget.text())

                if type(widget).__name__ == 'QSpinBox':
                    self.content.set(settingSection, settingKey, widget.value())

                if type(widget).__name__ == 'QComboBox':
                    self.content.set(settingSection, settingKey, widget.currentText())
                
                if type(widget).__name__ == 'BiFileSelectWidget':
                    self.content.set(settingSection, settingKey, widget.text()) 

    def saveClicked(self):
        self.extractContent()
        self.saveClickedSignal.emit()            

    def cancelClicked(self):
        self.cancelClickedSignal.emit()

    def getContent(self):
        self.extractContent()
        return self.content                  



if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    fields = BiFormFields("config/import_fields.json")
    #fields.add("Informations", "FirstName", BiFormFields.TypeString, "FirstName")
    #fields.add("Informations", "Name", BiFormFields.TypeString, "Name")

    content = BiFormContent("config/import_example.json")
    #content.set("FirstName", "Sylvain")
    #content.set("Name", "Prigent")
    
    widget = BiFormWidget(fields, content)
    widget.show()

    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("../bioimageapp/theme/default/icon.png"))
    sys.exit(app.exec_())