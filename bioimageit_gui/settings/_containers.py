from bioimageit_framework.framework import BiContainer


class BiSettingsContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiSettingsContainer'

class BiUpdateContainer(BiContainer):
    UpdateClicked = "update_clicked"
    UpdateFinished = "update_finished"
    GetNewTags = "get_new_tags"
    NewTags = 'new_tags'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiUpdateContainer'
        self.update_bioimageit = False
        self.update_toolboxes = False
        self.new_tags = []
        self.target_version_tag = ""

    def init(self):
        self._notify(BiUpdateContainer.GetNewTags) 

    def action_new_tags(self, action, tags):
        self.new_tags = tags
        self._notify(BiUpdateContainer.NewTags)

    def action_update_clicked(self, action):
        self._notify(BiUpdateContainer.UpdateClicked)

    def action_update_finished(self, action):
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