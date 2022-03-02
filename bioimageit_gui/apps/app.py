from bioimageit_core import ConfigAccess

from bioimageit_framework.theme import BiThemeAccess
from bioimageit_framework.framework import BiConnectome, BiComponent
from bioimageit_framework.widgets import BiAppMainWidget
from bioimageit_viewer.viewer import BiMultiViewer

from bioimageit_gui.home import BiHomeComponent, BiHomeContainer
from bioimageit_gui.finder import BiFinderComponent, BiFinderContainer, BiFinderModel
from bioimageit_gui.browser import BiBrowserComponent, BiBrowserContainer, BiBrowserModel
from bioimageit_gui.experiment import (BiExperimentCreateContainer, 
                                       BiExperimentCreateComponent, 
                                       BiExperimentCreateModel,
                                       BiExperimentViewerComponent)

class BioImageITApp(BiComponent):
    def __init__(self):
        super().__init__()
        # internal params
        self.toolboxes_tab_id = None
        self.browser_tab_id = None
        self.create_exp_tab_id = None
        # widgets
        self.main_widget = BiAppMainWidget()
        self.widget = self.main_widget.widget

        # containers    
        self.homeContainer = BiHomeContainer()
        self.finderContainer = BiFinderContainer()
        self.browserContainer = BiBrowserContainer()
        self.experimentCreateContainer = BiExperimentCreateContainer()
        # components
        self.homeComponent = BiHomeComponent()
        self.finderComponent = BiFinderComponent()
        self.browserComponent = BiBrowserComponent(self.browserContainer)
        self.experimentCreateComponent =  BiExperimentCreateComponent(self.experimentCreateContainer)
        # models
        self.finderModel = BiFinderModel() 
        self.browserModel = BiBrowserModel()
        self.experimentCreateModel = BiExperimentCreateModel(self.experimentCreateContainer)

        # connections
        BiConnectome.connect(self.homeContainer, self.homeComponent)
        BiConnectome.connect(self.homeContainer, self)
        BiConnectome.connect(self.finderContainer, self.finderComponent)
        BiConnectome.connect(self.finderContainer, self.finderModel)
        BiConnectome.connect(self.finderContainer, self)
        BiConnectome.connect(self.browserContainer, self.browserModel)
        BiConnectome.connect(self.browserContainer, self.browserComponent)
        BiConnectome.connect(self.browserContainer, self)
        BiConnectome.connect(self.experimentCreateContainer, self)

        # initialization
        self.finderContainer.init()
        self.browserContainer.init(ConfigAccess.instance().config["workspace"])

        # home tab
        self.main_widget.add(self.homeComponent, BiThemeAccess.instance().icon('home'), "Home", False)

        # viewer
        self.viewer = BiMultiViewer()
        self.viewer.set_visible(False)

    def callback_open_experiment(self, emitter):
        self._open_experiment(emitter.experiment_uri)  

    def callback_open_tool(self, emitter):
        print('app open tool:', emitter.clicked_tool)           

    def callback_open_tile(self, emitter):
        if emitter.clicked_tile_action == 'OpenToolboxes':
            self._open_toolboxes()
        elif emitter.clicked_tile_action == 'OpenBrowser':
            self._open_browser()  
        elif emitter.clicked_tile_action == 'OpenNewExperiment':   
            self._open_new_experiment() 

    def callback_experiment_created(self, emitter):
        self._open_experiment(emitter.experiment_uri)
        self.experimentCreateComponent.get_widget().setVisible(False)

    def _open_new_experiment(self):
        if self.create_exp_tab_id is None:
            self.create_exp_tab_id = self.main_widget.add(self.experimentCreateComponent, 
                                                         BiThemeAccess.instance().icon('plus'), 
                                                         "Create experiment", 
                                                         False)     
        else:
            self.main_widget.open(self.create_exp_tab_id) 

    def _open_toolboxes(self):
        if self.toolboxes_tab_id is None:
            self.toolboxes_tab_id = self.main_widget.add(self.finderComponent, 
                                                         BiThemeAccess.instance().icon('tools'), 
                                                         "Toolboxes", 
                                                         False)    
        else:
            self.main_widget.open(self.toolboxes_tab_id)     

    def _open_browser(self):
        if self.browser_tab_id is None:
            self.browser_tab_id = self.main_widget.add(self.browserComponent, 
                                                         BiThemeAccess.instance().icon('folder-dark'), 
                                                         "Toolboxes", 
                                                         False)    
        else:
            self.main_widget.open(self.browser_tab_id) 

    def _open_experiment(self, uri):
        print('app open experiment:', uri)
        experimentComponent = BiExperimentViewerComponent(uri, self.viewer)
        self.main_widget.add(experimentComponent, 
                             BiThemeAccess.instance().icon('database'), 
                             "Experiment", 
                             True)      
