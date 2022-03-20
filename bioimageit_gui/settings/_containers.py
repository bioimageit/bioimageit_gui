from bioimageit_framework.framework import BiContainer


class BiSettingsContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiSettingsContainer'

class BiUpdateContainer(BiContainer):
    UpdateClicked = "update_clicked"
    UpdateFinished = "update_finished"

    def __init__(self):
        super().__init__()
        self._object_name = 'BiUpdateContainer'
        self.update_bioimageit = False
        self.update_toolboxes = False

    def action_update_clicked(self):
        self._notify(BiUpdateContainer.UpdateClicked)

    def action_update_finished(self):
        self._notify(BiUpdateContainer.UpdateFinished)

class BiConfigContainer(BiContainer):
    ConfigEdited = "config_edited"
    ConfigSaved = "config_saved" 

    def __init__(self):
        super().__init__()
        self._object_name = 'BiConfigContainer'
        self.config = {}

    def action_config_edited(self, action, config):
        self.config = config
        self._notify(BiConfigContainer.ConfigEdited)

    def action_config_saved(self, action):
        self._notify(BiConfigContainer.ConfigSaved)         