import os
from pathlib import Path
from PySide2.QtWidgets import QSplitter
from qtpy.QtWidgets import (QVBoxLayout, QWidget, QLabel, QHBoxLayout)

from bioimageit_core.config import ConfigAccess

from bioimageit_gui.core.theme import BiThemeAccess

from bioimageit_gui.core.widgets import BiAppBar, BiStaticStackedWidget
from bioimageit_gui.core.framework import (BiAction, BiComponent)
from bioimageit_gui.home import BiHomeComponent, BiHomeContainer, BiHomeStates

from bioimageit_gui.finder.states import BiFinderStates
from bioimageit_gui.finder.containers import BiFinderContainer
from bioimageit_gui.finder.models import BiFinderModel
from bioimageit_gui.finder.components import BiFinderComponent

from bioimageit_gui.browser import (BiBrowserComponent, BiBrowserStates,
                                     BiBrowserContainer, BiBrowserModel)

from bioimageit_gui.experiment import (BiExperimentCreateContainer, 
                                       BiExperimentViewerComponent,
                                       BiExperimentCreateComponent, 
                                       BiExperimentCreateModel,
                                       BiExperimentStates,
                                       BiExperimentCreateStates)

from bioimageit_gui.apps.runnerapp import BiRunnerViewApp

from bioimageit_gui.settings import BiSettingsComponent, BiSettingsContainer
from bioimageit_gui.designer import BiDesignerComponent

from bioimageit_viewer.viewer import BiMultiViewer


class BioImageITApp(BiComponent):
    def __init__(self):
        super().__init__()

        self.opened_components = []
        self.browser_tab_id = -1
        self.toolboxes_tab_id = -1
        self.settings_tab_id = -1
        self.create_exp_tab_id = -1

        # containers    
        self.homeContainer = BiHomeContainer()
        self.finderContainer = BiFinderContainer()
        self.browserContainer = BiBrowserContainer()
        self.experimentCreateContainer = BiExperimentCreateContainer()
        self.settingsContainer = BiSettingsContainer()

        # components
        self.homeComponent = BiHomeComponent(self.homeContainer)
        self.finderComponent = BiFinderComponent(self.finderContainer)
        self.BrowserComponent = BiBrowserComponent(self.browserContainer)
        self.experimentCreateComponent =  BiExperimentCreateComponent(self.experimentCreateContainer)
        self.settingsComponent = BiSettingsComponent(self.settingsContainer)

        # models
        self.finderModel = BiFinderModel(self.finderContainer)
        self.browserModel = BiBrowserModel(self.browserContainer)
        self.experimentCreateModel = BiExperimentCreateModel(self.experimentCreateContainer)

        # register
        self.homeContainer.register(self)
        self.finderContainer.emit(BiFinderStates.Reload)
        self.finderContainer.register(self)
        self.browserContainer.register(self)
        self.experimentCreateContainer.register(self)

        # viewer
        self.viewer = BiMultiViewer()
        self.viewer.setVisible(False)

        # init
        self.browserContainer.currentPath = str(Path.home())
        self.browserContainer.emit(BiBrowserStates.DirectoryModified)

        # widgets
        self.widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)
        
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_widget.setLayout(central_layout)

        self.mainBar = BiAppBar()
        self.mainBar.setStyleSheet('QLabel{background-color:#414851;}')
        self.mainBar.close.connect(self.remove_tab)
        self.stackedWidget = BiStaticStackedWidget(self.widget)
        central_layout.addWidget(self.mainBar)
        central_layout.addWidget(self.stackedWidget)

        splitter = QSplitter()
        splitter.addWidget(central_widget)
        splitter.addWidget(self.viewer)

        layout.addWidget(splitter)

        self.mainBar.open.connect(self.slide_to)

        # home component
        self.mainBar.addButton(BiThemeAccess.instance().icon('home'), "Home", 0, False)
        self.stackedWidget.addWidget(self.homeComponent.get_widget())
        self.opened_components.append(self.homeComponent)
        self.mainBar.setChecked(0, True)

    def update(self, action: BiAction):
        if action.state == BiHomeStates.OpenNewExperiment:
            if self.create_exp_tab_id < 0:
                self.stackedWidget.addWidget(self.experimentCreateComponent.get_widget())
                self.create_exp_tab_id = self.stackedWidget.count()-1
                self.mainBar.addButton(BiThemeAccess.instance().icon('plus-white-symbol'), 
                                       "Create experiment", 
                                       self.create_exp_tab_id, False)
                self.opened_components.append(self.experimentCreateComponent)                       

            self.stackedWidget.slideInIdx(self.create_exp_tab_id)
            self.mainBar.setChecked(self.create_exp_tab_id, True)

        elif action.state == BiExperimentCreateStates.ExperimentCreated:
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
        elif action.state == BiBrowserStates.OpenExperiment:
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
        experimentComponent = BiExperimentViewerComponent(uri, self.viewer)
        # add to tab
        self.add_tab(experimentComponent.get_widget(), 
                     BiThemeAccess.instance().icon('database'), 
                     "Experiment", True)
        self.opened_components.append(experimentComponent)       

    def open_designer(self):
        # instantiate
        designerComponent = BiDesignerComponent()
        self.opened_components.append(designerComponent) 
        self.add_tab(designerComponent.get_widget(), 
                     BiThemeAccess.instance().icon('workflow'), 
                     "Designer", True)                      

    def open_process(self, uri):
        runner = BiRunnerViewApp(uri, self.viewer)
        self.opened_components.append(runner) 
        tab_idx = self.add_tab(runner.get_widget(), BiThemeAccess.instance().icon('play'), 'Runner', True) 

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
        self.opened_components.pop(idx) 
        self.stackedWidget.slideInIdx(0)
        self.mainBar.setChecked(0, True)
        self.viewer.setVisible(False)

    def slide_to(self, id: int):
        self.stackedWidget.slideInIdx(id)
        self.mainBar.setChecked(id, False)
        # Condition to show/hide the viewer
        print(self.opened_components)
        if self.opened_components[id].show_viewer:
            self.viewer.setVisible(True)
        else:
            self.viewer.setVisible(False)     

    def open_browser(self):
        if self.browser_tab_id < 0:
            self.stackedWidget.addWidget(self.BrowserComponent.get_widget())
            self.browser_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('folder-gray'), 
                                   "Browser", 
                                   self.browser_tab_id, False)

        self.stackedWidget.slideInIdx(self.browser_tab_id)
        self.mainBar.setChecked(self.browser_tab_id, True)
        self.opened_components.append(self.BrowserComponent)

    def open_toolboxes(self):
        if self.toolboxes_tab_id < 0:
            self.stackedWidget.addWidget(self.finderComponent.get_widget())
            self.toolboxes_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('tools'), 
                                   "Toolboxes", 
                                   self.toolboxes_tab_id, False)

        self.stackedWidget.slideInIdx(self.toolboxes_tab_id)
        self.mainBar.setChecked(self.toolboxes_tab_id, True)
        self.opened_components.append(self.finderComponent)

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
        self.opened_components.append(self.settingsComponent)   
    
    def get_widget(self):
        return self.widget    
