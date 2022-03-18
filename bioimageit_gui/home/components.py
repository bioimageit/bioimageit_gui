from bioimageit_core.api import APIAccess
from bioimageit_core import ConfigAccess

from bioimageit_framework.framework import BiComponent
from bioimageit_framework.widgets import BiVComposer
from bioimageit_framework.theme import BiThemeAccess

from bioimageit_gui.home.widgets import BiHomeTilesWidget, BiWorkspaceWidget


class BiHomeComponent(BiComponent):
    CLICKED_EXP = 'open_experiment'
    CLICKED_TILE = 'open_tile'
    LOADED_EXP = 'load_experiments'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiHomeComponent' 

        self.home_widget = BiHomeTilesWidget()

        use_browse = False
        if ConfigAccess.instance().config['metadata']['service'] == 'LOCAL':
            use_browse = True
        self.workspace_widget = BiWorkspaceWidget(use_browse)

        self.composer = BiVComposer()
        self.widget = self.composer.widget
        self.composer.add(self.home_widget)
        self.composer.add(self.workspace_widget)

        self.home_widget.add_tile('New \n experiment', BiThemeAccess.instance().icon('plus-dark'), 'OpenNewExperiment')
        #self.home_widget.add_tile('Browse \n experiments', BiThemeAccess.instance().icon('folder-dark'), 'OpenBrowser')
        self.home_widget.add_tile('Toolboxes', BiThemeAccess.instance().icon('tools-dark'), 'OpenToolboxes')
        #self.home_widget.add_tile('Settings', BiThemeAccess.instance().icon('settings-dark'), 'OpenSettings')
        self.home_widget.connect(BiHomeTilesWidget.CLICKED_TILE, self.open_tile)

        self.workspace_widget.connect(BiWorkspaceWidget.CLICKED_EXP, self.open_experiment)
        self.workspace_widget.connect(BiWorkspaceWidget.BROWSE, self.browse)
        self.fill_experiments()
    
    def fill_experiments(self):
        experiments = APIAccess.instance().get_workspace_experiments()
        if len(experiments) == 0:
            self.workspace_widget.free()
        else:
            self.workspace_widget.set_row_count(len(experiments))
            for i, exp in enumerate(experiments):
                self.workspace_widget.set_item(i, exp) 
        self._emit(BiHomeComponent.LOADED_EXP, experiments)        
               
        
    def open_tile(self, origin: str):
        print('clicked til=', origin.clicked_tile)
        self._emit(BiHomeComponent.CLICKED_TILE, [origin.clicked_tile])

    def browse(self, origin):
        self._emit(BiHomeComponent.CLICKED_TILE, ['OpenBrowser'])

    def open_experiment(self, origin):
        experiment_uri = origin.experiments[origin.clicked_experiment]['md_uri']
        self._emit(BiHomeComponent.CLICKED_EXP, experiment_uri)
