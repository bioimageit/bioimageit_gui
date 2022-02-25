from bioimageit_core.api import APIAccess

from bioimageit_framework.framework import BiActuator


class BiFinderModel(BiActuator):
    RELOADED_CATEGORIES = "reload_categories"
    RELOADED_TOOLS = "reload_tools"

    def __init__(self):
        super().__init__()
        self._object_name = 'BiFinderModel'

    def callback_reload(self, emitter):
        categories = APIAccess.instance().get_categories(emitter.curent_category)
        if len(categories) == 0:
            tools = APIAccess.instance().get_category_tools(emitter.curent_category)   
            self._emit(BiFinderModel.RELOADED_TOOLS, tuple(tools))
        else:
            self._emit(BiFinderModel.RELOADED_CATEGORIES, tuple(categories))

