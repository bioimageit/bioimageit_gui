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

from bioimageit_gui.experiment2.containers import BiExperimentContainer                                     
from bioimageit_gui.experiment2.components import BiExperimentComponent 
from bioimageit_gui.experiment2.states import BiExperimentStates

class BioImageITApp(BiComponent):
    def __init__(self):
        super().__init__()

        self.browser_tab_id = -1
        self.toolboxes_tab_id = -1

        # containers    
        self.homeContainer = BiHomeContainer()
        self.finderContainer = BiFinderContainer()
        self.browserContainer = BiBrowser2Container()

        # components
        self.homeComponent = BiHomeComponent(self.homeContainer)
        self.finderComponent = BiFinderComponent(self.finderContainer)
        self.BrowserComponent = BiBrowser2Component(self.browserContainer)

        # models
        self.finderModel = BiFinderModel(self.finderContainer)
        self.browserModel = BiBrowser2Model(self.browserContainer)

        # register
        self.homeContainer.register(self)
        self.finderContainer.emit(BiFinderStates.Reload)
        self.finderContainer.register(self)
        self.browserContainer.register(self)

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
        self.stackedWidget = BiStaticStackedWidget(self.widget)
        layout.addWidget(self.mainBar)
        layout.addWidget(self.stackedWidget)

        self.mainBar.open.connect(self.slide_to)


        # home component
        self.mainBar.addButton(BiThemeAccess.instance().icon('home'), "Home", 0, False)
        self.stackedWidget.addWidget(self.homeComponent.get_widget())
        self.mainBar.setChecked(0, True)


    def update(self, action: BiAction):
        if action.state == BiHomeStates.OpenBrowser:
            self.open_browser()
        elif action.state == BiHomeStates.OpenToolboxes:
            self.open_toolboxes()
        elif action.state == BiBrowser2States.OpenExperiment:
            self.open_experiment(self.browserContainer.openExperimentPath)   
        elif action.state == BiHomeStates.OpenExperiment:
            self.open_experiment(self.homeContainer.clicked_experiment) 
        elif action.state == BiFinderStates.OpenProcess:
            tool_uri = self.finderContainer.clicked_tool
            self.open_process(tool_uri)              

    def open_experiment(self, uri):
        print('app is opening experiment: ', uri)
        # instantiate
        experimentContainer = BiExperimentContainer()
        experimentContainer.experiment_uri = uri
        experimentContainer.register(self)
        experimentComponent = BiExperimentComponent(experimentContainer)
        experimentContainer.emit(BiExperimentStates.Load)
        # add to tag
        self.stackedWidget.addWidget(experimentComponent.get_widget())
        tab_idx = self.stackedWidget.count()-1
        self.mainBar.addButton(BiThemeAccess.instance().icon('database'), 
                               "Experiment", 
                               tab_idx, False)
        # slide to it
        self.stackedWidget.slideInIdx(tab_idx)
        self.mainBar.setChecked(tab_idx, True)

    def open_process(self, uri):
        runner_script = ConfigAccess.instance().get('apps')['runner']  
        print('run open process:', runner_script, self.finderContainer.clicked_tool)   
        subprocess.Popen([runner_script, uri])   

    def slide_to(self, id: int):
        self.stackedWidget.slideInIdx(id)
        self.mainBar.setChecked(id, False)

    def open_browser(self):
        if self.browser_tab_id < 0:
            widget = QLabel('Hello Browser')
            widget.setObjectName('BiWidget')
            self.stackedWidget.addWidget(self.BrowserComponent.get_widget())
            self.browser_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('open-folder_negative'), 
                                   "Browser", 
                                   self.browser_tab_id, False)

        self.stackedWidget.slideInIdx(self.browser_tab_id)
        self.mainBar.setChecked(self.browser_tab_id, True)

    def open_toolboxes(self):
        if self.toolboxes_tab_id < 0:
            self.stackedWidget.addWidget(self.finderComponent.get_widget())
            self.toolboxes_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('tools'), 
                                   "Browser", 
                                   self.toolboxes_tab_id, False)

        self.stackedWidget.slideInIdx(self.toolboxes_tab_id)
        self.mainBar.setChecked(self.toolboxes_tab_id, True)
    
    def get_widget(self):
        return self.widget    
