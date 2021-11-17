from pathlib import Path
import subprocess
from PySide2.QtWidgets import (QVBoxLayout, QWidget, QLabel, QHBoxLayout)

from bioimageit_core.config import ConfigAccess

from bioimageit_gui.core.theme import BiThemeAccess

from bioimageit_gui.core.widgets import BiAppBar, BiStaticStackedWidget
from bioimageit_gui.core.framework import (BiAction, BiComponent)
from bioimageit_gui.home import BiHomeComponent, BiHomeContainer, BiHomeStates

from bioimageit_gui.finder.states import BiFinderStates
from bioimageit_gui.finder.containers import BiFinderContainer
from bioimageit_gui.finder.models import BiFinderModel
from bioimageit_gui.finder.components import BiFinderComponent

from bioimageit_gui.browser2 import (BiBrowser2Component, BiBrowser2States,
                                     BiBrowser2Container, BiBrowser2Model)

from bioimageit_gui.experiment2.containers import BiExperimentCreateContainer                                     
from bioimageit_gui.experiment2.components import (BiExperimentViewerComponent, BiExperimentCreateComponent) 
from bioimageit_gui.experiment2.models import BiExperimentCreateModel
from bioimageit_gui.experiment2.states import (BiExperimentStates, BiExperimentCreateStates)

from bioimageit_gui.runnerapp import BiRunnerViewApp

from bioimageit_gui.settings import BiSettingsComponent, BiSettingsContainer
from bioimageit_gui.designer import BiDesignerComponent

class BioImageITApp(BiComponent):
    def __init__(self):
        super().__init__()

        self.browser_tab_id = -1
        self.toolboxes_tab_id = -1
        self.settings_tab_id = -1

        # containers    
        self.homeContainer = BiHomeContainer()
        self.finderContainer = BiFinderContainer()
        self.browserContainer = BiBrowser2Container()
        self.experimentCreateContainer = BiExperimentCreateContainer()
        self.settingsContainer = BiSettingsContainer()

        # components
        self.homeComponent = BiHomeComponent(self.homeContainer)
        self.finderComponent = BiFinderComponent(self.finderContainer)
        self.BrowserComponent = BiBrowser2Component(self.browserContainer)
        self.experimentCreateComponent =  BiExperimentCreateComponent(self.experimentCreateContainer)
        self.settingsComponent = BiSettingsComponent(self.settingsContainer)

        # models
        self.finderModel = BiFinderModel(self.finderContainer)
        self.browserModel = BiBrowser2Model(self.browserContainer)
        self.experimentCreateModel = BiExperimentCreateModel(self.experimentCreateContainer)

        # register
        self.homeContainer.register(self)
        self.finderContainer.emit(BiFinderStates.Reload)
        self.finderContainer.register(self)
        self.browserContainer.register(self)
        self.experimentCreateContainer.register(self)

        # init
        self.browserContainer.currentPath = str(Path.home())
        self.browserContainer.emit(BiBrowser2States.DirectoryModified)

        # widgets
        self.widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)
        
        self.mainBar = BiAppBar()
        self.mainBar.setStyleSheet('QLabel{background-color:#414851;}')
        self.mainBar.close.connect(self.remove_tab)
        self.stackedWidget = BiStaticStackedWidget(self.widget)
        layout.addWidget(self.mainBar)
        layout.addWidget(self.stackedWidget)

        self.mainBar.open.connect(self.slide_to)

        # home component
        self.mainBar.addButton(BiThemeAccess.instance().icon('home'), "Home", 0, False)
        self.stackedWidget.addWidget(self.homeComponent.get_widget())
        self.mainBar.setChecked(0, True)


    def update(self, action: BiAction):
        if action.state == BiHomeStates.OpenNewExperiment:
            self.experimentCreateComponent.get_widget().setVisible(True)
        elif action.state == BiExperimentCreateStates.CancelClicked:
            self.experimentCreateComponent.get_widget().setVisible(False)   
        if action.state == BiExperimentCreateStates.ExperimentCreated:
            uri = self.experimentCreateContainer.experiment_dir
            print('open new experiment from:', uri)
            self.open_experiment(uri)
            self.experimentCreateComponent.get_widget().setVisible(False) 
        elif action.state == BiHomeStates.OpenBrowser:
            self.open_browser()
        elif action.state == BiHomeStates.OpenDesigner:
            print('open deigner')
            self.open_designer()     
        elif action.state == BiHomeStates.OpenToolboxes:
            self.open_toolboxes()
        elif action.state == BiHomeStates.OpenSettings:
            self.open_settings()    
        elif action.state == BiBrowser2States.OpenExperiment:
            self.open_experiment(self.browserContainer.openExperimentPath)   
        elif action.state == BiHomeStates.OpenExperiment:
            self.open_experiment(self.homeContainer.clicked_experiment) 
        elif action.state == BiFinderStates.OpenProcess:
            tool_uri = self.finderContainer.clicked_tool
            self.open_process(tool_uri)  
        elif action.state == BiExperimentStates.ProcessClicked:
            self.open_toolboxes()                                  

    def open_experiment(self, uri):
        # instantiate
        experimentComponent = BiExperimentViewerComponent(uri, 1)
        experimentComponent.experimentContainer.register(self)
        tab_id = self.add_tab(experimentComponent.get_widget(), 
                              BiThemeAccess.instance().icon('database'), 
                              "Experiment", True)
        experimentComponent.experimentComponent.parent_id = tab_id    

    def open_designer(self):
        # instantiate
        designerComponent = BiDesignerComponent()
        self.add_tab(designerComponent.get_widget(), 
                     BiThemeAccess.instance().icon('workflow'), 
                     "Designer", True)                      

    def open_process(self, uri):
        runner = BiRunnerViewApp(uri)
        self.add_tab(runner.get_widget(), BiThemeAccess.instance().icon('play'), 'Runner', True) 

    def add_tab(self, widget, icon, name, closable=False):
        # fill tab and widget
        self.stackedWidget.addWidget(widget)
        tab_idx = self.stackedWidget.count()-1
        self.mainBar.addButton(icon,  name, tab_idx, closable)
        # slide to it
        self.stackedWidget.slideInIdx(tab_idx)
        self.mainBar.setChecked(tab_idx, True)
        return tab_idx

    def remove_tab(self, idx):
        self.mainBar.removeButton(idx)
        self.stackedWidget.remove(idx)
        self.stackedWidget.slideInIdx(0)
        self.mainBar.setChecked(0, True)

    def slide_to(self, id: int):
        self.stackedWidget.slideInIdx(id)
        self.mainBar.setChecked(id, False)

    def open_browser(self):
        if self.browser_tab_id < 0:
            self.stackedWidget.addWidget(self.BrowserComponent.get_widget())
            self.browser_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('folder-gray'), 
                                   "Browser", 
                                   self.browser_tab_id, False)

        self.stackedWidget.slideInIdx(self.browser_tab_id)
        self.mainBar.setChecked(self.browser_tab_id, True)

    def open_toolboxes(self):
        print("open toolboxes:", self.toolboxes_tab_id)
        if self.toolboxes_tab_id < 0:
            self.stackedWidget.addWidget(self.finderComponent.get_widget())
            self.toolboxes_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('tools'), 
                                   "Toolboxes", 
                                   self.toolboxes_tab_id, False)

        self.stackedWidget.slideInIdx(self.toolboxes_tab_id)
        self.mainBar.setChecked(self.toolboxes_tab_id, True)

    def open_settings(self):
        print("open settings:", self.settings_tab_id)
        if self.settings_tab_id < 0:
            self.stackedWidget.addWidget(self.settingsComponent.get_widget())
            self.settings_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('cog-wheel-silhouette'), 
                                   "Toolboxes", 
                                   self.settings_tab_id, False)

        self.stackedWidget.slideInIdx(self.settings_tab_id)
        self.mainBar.setChecked(self.settings_tab_id, True)    
    
    def get_widget(self):
        return self.widget    
