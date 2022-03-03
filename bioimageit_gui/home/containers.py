from bioimageit_framework.framework import BiContainer


class BiHomeContainer(BiContainer):
    OPEN_TILE = 'open_tile'
    OPEN_EXP = 'open_experiment'
    EXPERIMENTS_LOADED = 'experiments_loaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiHomeContainer'

        # data
        self.experiments = []
        self.experiment_uri = ''
        self.clicked_tile_action = ''

    def action_open_experiment(self, action, experiment_uri):
        """Action callback to open an experiment"""
        self.experiment_uri = experiment_uri
        self._notify(BiHomeContainer.OPEN_EXP)     

    def action_open_tile(self, action, tile_action):
        """Action callback to open an experiment"""
        self.clicked_tile_action = tile_action
        self._notify(BiHomeContainer.OPEN_TILE) 

    def action_load_experiments(self, action, experiments):
        self.experiments = experiments
        self._notify(BiHomeContainer.EXPERIMENTS_LOADED) 
    