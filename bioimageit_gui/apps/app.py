from bioimageit_framework.theme import BiThemeAccess
from bioimageit_framework.framework import BiConnectome, BiComponent
from bioimageit_framework.widgets import BiAppMainWidget

from bioimageit_gui.home import BiHomeComponent, BiHomeContainer
from bioimageit_gui.finder import BiFinderComponent, BiFinderContainer, BiFinderModel

class BioImageITApp(BiComponent):
    def __init__(self):
        super().__init__()
        # internal params
        self.toolboxes_tab_id = None
        # widgets
        self.main_widget = BiAppMainWidget()
        self.widget = self.main_widget.widget

        # containers    
        self.homeContainer = BiHomeContainer()
        self.finderContainer = BiFinderContainer()
        # components
        self.homeComponent = BiHomeComponent()
        self.finderComponent = BiFinderComponent()
        # models
        self.finderModel = BiFinderModel() 
        # connections
        BiConnectome.connect(self.homeContainer, self.homeComponent)
        BiConnectome.connect(self.homeContainer, self)
        BiConnectome.connect(self.finderContainer, self.finderComponent)
        BiConnectome.connect(self.finderContainer, self.finderModel)
        BiConnectome.connect(self.finderContainer, self)

        # initialization
        self.finderContainer.init()

        # home tab
        self.main_widget.add(self.homeComponent, BiThemeAccess.instance().icon('home'), "Home", False)

    def callback_open_experiment(self, emitter):
        print('app open experiment:', emitter.clicked_experiment_uri)   

    def callback_open_tool(self, emitter):
        print('app open tool:', emitter.clicked_tool)       

    def callback_open_tile(self, emitter):
        if emitter.clicked_tile_action == 'OpenToolboxes':
            self._open_toolboxes()

    def _open_toolboxes(self):
        if self.toolboxes_tab_id is None:
            self.toolboxes_tab_id = self.main_widget.add(self.finderComponent, 
                                                         BiThemeAccess.instance().icon('tools'), 
                                                         "Toolboxes", 
                                                         False)    
        else:
            self.main_widget.open(self.toolboxes_tab_id)     
