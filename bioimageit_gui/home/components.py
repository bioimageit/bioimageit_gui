from bioimageit_core.api import APIAccess

from bioimageit_framework.framework import BiComponent, BiAction
from bioimageit_framework.widgets import BiVComposer
from bioimageit_framework.theme import BiThemeAccess

from bioimageit_gui.home.containers import BiHomeContainer
#from bioimageit_gui.home.states import BiHomeStates
from bioimageit_gui.home.widgets import BiHomeTilesWidget, BiWorkspaceWidget


class BiHomeComponent(BiComponent):
    def __init__(self, container: BiHomeContainer):
        super().__init__()
        self._object_name = 'BiHomeComponent'
        self.container = container
        #self.container.register(self)  

        self.home_widget = BiHomeTilesWidget()
        self.workspace_widget = BiWorkspaceWidget()

        self.composer = BiVComposer()
        self.widget = self.composer.widget
        self.composer.add(self.home_widget)
        self.composer.add(self.workspace_widget)

        self.home_widget.add_tile('New \n experiment', BiThemeAccess.instance().icon('plus-dark'), 'OpenNewExperiment')
        self.home_widget.add_tile('Browse \n experiments', BiThemeAccess.instance().icon('folder-dark'), 'OpenBrowser')
        self.home_widget.add_tile('Toolboxes', BiThemeAccess.instance().icon('tools-dark'), 'OpenToolboxes')
        self.home_widget.add_tile('Settings', BiThemeAccess.instance().icon('settings-dark'), 'OpenSettings')
        self.home_widget.connect(BiHomeTilesWidget.CLICKED_TILE, self.open_tile)

        self.workspace_widget.connect(BiWorkspaceWidget.CLICKED_EXP, self.open_eperiment)
        self.fill_experiments()
    
    def fill_experiments(self):
        self.container.experiments = APIAccess.instance().get_workspace_experiments()
        if len(self.container.experiments) == 0:
            self.workspace_widget.free()
        else:
            self.workspace_widget.set_row_count(len(self.container.experiments))
            for i, exp in enumerate(self.container.experiments):
                self.workspace_widget.set_item(i, exp) 
               
        
    def open_tile(self, origin: str):
        if origin.clicked_tile == 'OpenNewExperiment':
            self.container.emit(BiHomeStates.OpenNewExperiment)
        elif origin.clicked_tile == 'OpenBrowser':
            self.container.emit(BiHomeStates.OpenBrowser) 
        elif origin.clicked_tile == 'OpenDesigner':
            self.container.emit(BiHomeStates.OpenDesigner) 
        elif origin.clicked_tile == 'OpenToolboxes':
            self.container.emit(BiHomeStates.OpenToolboxes)    
        elif origin.clicked_tile == 'OpenSettings':
            self.container.emit(BiHomeStates.OpenSettings)

    def open_experiment(self, origin):
        self.container.clicked_experiment = origin.clicked_experiment
        self.container.emit(BiHomeStates.OpenExperiment)
