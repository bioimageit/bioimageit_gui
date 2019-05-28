import os
import json

import PySide2.QtCore
from PySide2.QtWidgets import (QWidget, QPushButton, QGridLayout, QLabel, QComboBox, QSpinBox, QLineEdit) 

from framework import BiContainer, BiComponent
from widgets import BiFileSelectWidget

class BiSettings():
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

    def groups(self):
        keys = []
        for key in self.data:
            keys.append(key)
        return keys    

    def keys(self, group: str):
        keys = []
        for key in self.data[group]:
            keys.append(key)
        return keys   

    def set(self, group: str, key: str, value: str):
        self.data[group][key] = value   

    def value(self, group: str, key: str):
        data = self.data[group]
        for entry in data:
            if entry['key'] == key:
                return entry['value'] 
        return ''        

class BiSettingsAccess:
    instance = None
    def __init__(self):
        if not BiSettingsAccess.instance:
            BiSettingsAccess.instance = BiSettings()

class BiSettingsComponent(BiComponent):
    def __init__(self):
        super(BiSettingsComponent, self).__init__()
        self._object_name = 'BiSettingsComponent'

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
        layout = QGridLayout
        self.widget.setLayout(layout)
        self.widgets = []

        groups = BiSettingsAccess.instance
        titles = groups.groups()

        line = 0
        for i in range(len(titles)):
   
            titleLabel = QLabel(titles[i])
            titleLabel.setObjectName("BiLabelFormHeader1")
            layout.addWidget(titleLabel, line, 0, 1, 3)
            line += 1

            settings = groups.data[titles[i]]
            for setting in settings:
                key = setting['key']
                ttype = setting['type']
                value = setting['value']

                title = QLabel(key)
                layout.addWidget(title, line, 0)

                settingId = titles[i] + "::" + key

                if ttype == BiSettings.TypeString:
                    edit = QLineEdit()
                    edit.setText(value)
                    layout.addWidget(edit, line, 1, 1, 2)
                    self.widgets[settingId] = edit
                elif ttype == BiSettings.TypeNumber:
                    spinBox = QSpinBox()
                    spinBox.setValue(int(value))
                    layout.addWidget(spinBox, line, 1, 1, 2)
                    self.widgets[settingId] = spinBox
                elif ttype == BiSettings.TypeBool:
                    comboBox = QComboBox()
                    comboBox.addItem("true")
                    comboBox.addItem("false")
                    comboBox.setCurrentText(value)
                    layout.addWidget(comboBox, line, 1, 1, 2)
                    self.widgets[settingId] = comboBox
                elif ttype == BiSettings.TypeSelect:
                    comboBox = QComboBox()
                    comboBox.addItems(setting['choices'])
                    comboBox.setCurrentText(value)
                    layout.addWidget(comboBox, line, 1, 1, 2)
                    self.widgets[settingId] = comboBox
                elif ttype == BiSettings.TypeFile:
                    fileWidget = BiFileSelectWidget()
                    fileWidget.setText(value)
                    layout.addWidget(fileWidget, line, 1, 1, 2)
                    self.widgets[settingId] = fileWidget
                elif ttype == BiSettings.TypeDir:
                    fileWidget = BiFileSelectWidget(True)
                    fileWidget.setText(setting.value())
                    layout.addWidget(fileWidget, line, 1, 1, 2)
                    self.widgets[settingId] = fileWidget
                else:
                    print(ttype, " is not a known settings type")
                line += 1

        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        layout.addWidget(saveButton, line, 2, PySide2.QtCore.Qt.AlignRight)
        saveButton.released.connect(self.saveClicked)

        line += 1
        layout.addWidget(QWidget(), line, 0, 1, 3, PySide2.QtCore.Qt.AlignTop)

    def saveClicked(self):

        groups = BiSettingsAccess.instance
        
        for key, widget in self.widgets:

            settingId = key.split("::")
            group = settingId[0]
            settingKey = settingId[1]

            if widget:
                if type(widget).__name__ == 'QLineEdit':
                    groups.set(group, settingKey, widget.text())

                if type(widget).__name__ == 'QSpinBox':
                    groups.set(group, settingKey, str(widget.value()))

                if type(widget).__name__ == 'QComboBox':
                    groups.set(group, settingKey, widget.currentText())
                
                if type(widget).__name__ == 'BiFileSelectWidget':
                    groups.set(group, settingKey, widget.text())
                
        BiSettingsAccess.instance.save()

    def update(self, container: BiContainer):
        pass
