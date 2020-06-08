from bioimageapp.core.framework import BiContainer

class BiExperimentContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiExperimentContainer'

        # data
        self.experiment = None

class BiExperimentCreateContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiExperimentCreateContainer'

        # data
        self.experiment_destination_dir = ''
        self.experiment_name = ''
        self.experiment_author = ''
        self.errorMessage = ''
        self.experiment_dir = ""  