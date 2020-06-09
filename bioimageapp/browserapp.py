import sys
import os
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication
import subprocess
from pathlib import Path
import subprocess

from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSplitter, QHBoxLayout

from bioimageapp.core.framework import BiStates, BiAction, BiComponent, BiContainer
from bioimageapp.core.exceptions import CommandArgsError
from bioimageapp.browser.states import BiBrowserStates
from bioimageapp.browser.containers import BiBrowserContainer
from bioimageapp.browser.models import BiBrowserModel
from bioimageapp.browser.components import (BiBrowserToolBarComponent, BiBrowserShortCutsComponent, 
                                            BiBrowserTableComponent)

from bioimageapp.experiment.states import BiExperimentCreateStates, BiExperimentStates
from bioimageapp.experiment.containers import (BiExperimentCreateContainer, BiExperimentContainer)
from bioimageapp.experiment.models import BiExperimentCreateModel, BiExperimentModel
from bioimageapp.experiment.components import (BiExperimentCreateComponent, BiExperimentToolbarComponent, 
                                               BiExperimentImportComponent, BiExperimentTagComponent)

from bioimageapp.metadata.states import BiMetadataEditorStates, BiMetadataStates
from bioimageapp.metadata.containers import BiMetadataEditorContainer, BiMetadataContainer
from bioimageapp.metadata.models import BiMetadataEditorModel
from bioimageapp.metadata.components import BiMetadataJsonEditorComponent, BiMetadataPreviewComponent
                                            

class BiBrowserApp(BiComponent):
    def __init__(self, bookmarks_file: str):
        super().__init__()

        # container
        self.browserContainer = BiBrowserContainer()
        self.metadataContainer = BiMetadataContainer()
        self.metadataEditorContainer = BiMetadataEditorContainer()
        self.experimentCreateContainer = BiExperimentCreateContainer()
        self.experimentContainer = BiExperimentContainer()
        
        # model
        self.browserModel = BiBrowserModel(self.browserContainer, True)
        self.metadataEditorModel = BiMetadataEditorModel(self.metadataEditorContainer)
        self.experimentCreateModel = BiExperimentCreateModel(self.experimentCreateContainer)
        self.experimentModel = BiExperimentModel(self.experimentContainer)

        # components
        self.toolBarComponent = BiBrowserToolBarComponent(self.browserContainer)
        self.experimentToolBarComponent = BiExperimentToolbarComponent(self.experimentContainer)
        self.shortCutComponent = BiBrowserShortCutsComponent(self.browserContainer)
        self.tableComponent = BiBrowserTableComponent(self.browserContainer)
        self.previewComponent = BiMetadataPreviewComponent(self.metadataContainer)

        self.metadataEditorComponent = BiMetadataJsonEditorComponent(self.metadataEditorContainer)
        self.experimentCreateComponent = BiExperimentCreateComponent(self.experimentCreateContainer)
        self.experimentImportComponent = BiExperimentImportComponent(self.experimentContainer)
        self.experimentTagComponent = BiExperimentTagComponent(self.experimentContainer)
        
        # connections
        self.browserContainer.register(self)
        self.metadataContainer.register(self)
        self.metadataEditorContainer.register(self)
        self.experimentContainer.register(self)
        self.experimentCreateContainer.register(self)

        # load settings
        self.browserContainer.currentPath = str(Path.home())
        self.browserContainer.emit(BiBrowserStates.DirectoryModified)

        self.browserModel.loadBookmarks(bookmarks_file)
        self.shortCutComponent.reloadBookmarks()

        # create the widget
        self.widget = QWidget()
        self.widget.setObjectName('bioImageApp')
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        splitters = QWidget()
        splittersLayout = QHBoxLayout()
        splittersLayout.setContentsMargins(0,0,0,0)
        splitters.setLayout(splittersLayout)

        layout.addWidget(self.toolBarComponent.get_widget())
        layout.addWidget(splitters)

        splitterLeft = QSplitter()  
        splitterRight = QSplitter()
        splittersLayout.addWidget(splitterRight)

        tableWidget = QWidget()
        tableLayout = QVBoxLayout()
        tableLayout.setContentsMargins(0,0,0,0) 
        tableLayout.setSpacing(0)
        tableWidget.setLayout(tableLayout)
        tableLayout.addWidget(self.experimentToolBarComponent.get_widget())
        tableLayout.addWidget(self.tableComponent.get_widget())


        self.shortCutComponent.get_widget().setMaximumWidth(300)
        splitterLeft.addWidget(self.shortCutComponent.get_widget())
        splitterLeft.addWidget(tableWidget)

        splitterRight.addWidget(splitterLeft)
        splitterRight.addWidget(self.previewComponent.get_widget())
        self.previewComponent.get_widget().setVisible(False)

        splitterRight.setObjectName('BiBrowserAppSplitterRight')
        splitterLeft.setObjectName('BiBrowserAppSplitterLeft')

    def setPath(self, path: str):
        self.browserContainer.currentPath = path
        self.browserContainer.emit(BiBrowserStates.DirectoryModified)

    def update(self, action: BiAction):
        if action.state == BiBrowserStates.ItemDoubleClicked:
            self.metadataEditorContainer.file = self.browserContainer.doubleClickedFile()
            if (self.metadataEditorContainer.file.endswith('.md.json')):
                self.metadataEditorContainer.emit( BiMetadataEditorStates.FileModified )
                self.metadataEditorComponent.get_widget().show()
            return

        if action.state == BiMetadataEditorStates.JsonWrote:
            self.browserContainer.emit(BiBrowserStates.RefreshClicked)
            return

        if action.state == BiMetadataStates.OpenClicked:
            self.metadataEditorContainer.file = self.metadataContainer.md_uri
            self.metadataEditorContainer.emit( BiMetadataEditorStates.FileModified )
            self.metadataEditorComponent.get_widget().show()
            return    

        if action.state == BiBrowserStates.ItemClicked:
            fileInfo = self.browserContainer.files[self.browserContainer.clickedRow]
            md_uri = os.path.join(fileInfo.path, fileInfo.fileName)
            if md_uri.endswith('.md.json'):
                self.metadataContainer.md_uri = md_uri
                self.metadataContainer.emit(BiMetadataStates.URIChanged)
                self.previewComponent.get_widget().setVisible(True)

            else:
                self.previewComponent.get_widget().setVisible(False)
            return

        if action.state == BiBrowserStates.NewExperimentClicked:
            self.experimentCreateComponent.reset()
            self.experimentCreateComponent.setDestination(self.browserContainer.currentPath)
            self.experimentCreateComponent.get_widget().setVisible(True)
            return

        if action.state == BiExperimentCreateStates.ExperimentCreated:
            self.experimentCreateComponent.get_widget().setVisible(False)
            return

        if action.state == BiBrowserStates.TableLoaded:
            experiment_uri = self.isExperimentDir()
            if experiment_uri != '':
                self.experimentToolBarComponent.get_widget().setVisible(True)
                if experiment_uri != self.experimentContainer.experiment_uri:
                    self.experimentContainer.experiment_uri = experiment_uri
                    self.experimentContainer.emit(BiExperimentStates.Load)
            else:
                self.experimentToolBarComponent.get_widget().setVisible(False)
            return   

        if action.state == BiExperimentStates.ProcessClicked:
            subprocess.call(['python3', 'finderapp.py'])
            return    

        if action.state == BiExperimentStates.ImportClicked:
            self.experimentImportComponent.get_widget().setVisible(True)
            return

        if action.state == BiExperimentStates.TagClicked:
            self.experimentTagComponent.get_widget().setVisible(True) 
            return       


    def get_widget(self):
        return self.widget 

    def isExperimentDir(self):
        if os.path.isfile( os.path.join(self.browserContainer.currentPath, 'experiment.md.json') ):
            return os.path.join(self.browserContainer.currentPath, 'experiment.md.json')
        parent_dir = os.path.abspath(os.path.join(self.browserContainer.currentPath, os.pardir))    
        if os.path.isfile( os.path.join(parent_dir, 'experiment.md.json') ):
            return os.path.join(parent_dir, 'experiment.md.json')
        return ''       


