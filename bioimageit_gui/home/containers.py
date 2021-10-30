from bioimageit_gui.core.framework import BiContainer


class BiHomeContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiHomeContainer'

        # data
        self.experiments = []
        self.clicked_experiment = ''
