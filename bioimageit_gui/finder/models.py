from bioimageit_core.process import ProcessAccess

from bioimageit_gui.core.framework import BiModel, BiAction
from bioimageit_gui.finder.states import BiFinderStates
from bioimageit_gui.finder.containers import BiFinderContainer


class BiFinderModel(BiModel):
    def __init__(self, container: BiFinderContainer):
        super().__init__()
        self._object_name = 'BiFinderModel'
        self.container = container
        self.container.register(self)  

    def update(self, action: BiAction):
        if action.state == BiFinderStates.Reload:
            self.reload()   
            self.container.emit(BiFinderStates.Reloaded)

    def reload(self):
        self.container.categories = ProcessAccess().get_categories(
            self.container.curent_category)
        if len(self.container.categories) == 0:
            self.container.tools = ProcessAccess().get_category_processes(
                self.container.curent_category)
