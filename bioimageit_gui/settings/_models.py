from bioimageit_core.config import Config, ConfigAccess

from bioimageit_gui.core.framework import BiModel, BiAction

from ._containers import BiConfigContainer
from ._states import BiConfigStates


class BiConfigModel(BiModel):  
    def __init__(self, container: BiConfigContainer):
        super().__init__()
        self._object_name = 'BiRawDataModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiConfigStates.ConfigEdited:
            # save the config    
            config_obj = Config()
            config_obj.config = self.container.config
            config_obj.config_file = ConfigAccess.instance().config_file
            config_obj.save()
            # change the access pointer
            ConfigAccess.instance().config = config_obj
            self.container.emit(BiConfigStates.ConfigSaved)
            return
