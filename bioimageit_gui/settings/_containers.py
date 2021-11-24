from bioimageit_gui.core.framework import BiContainer


class BiSettingsContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiSettingsContainer'

class BiUpdateContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiUpdateContainer'
        self.update_bioimageit = False
        self.update_toolboxes = False

class BiConfigContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiConfigContainer'
        self.config = {}
