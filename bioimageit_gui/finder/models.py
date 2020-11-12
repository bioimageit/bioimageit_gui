from bioimagepy.process import ProcessAccess

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.finder.states import BiFinderStates
from bioimageapp.finder.containers import BiFinderContainer


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
        self.container.categories = ProcessAccess().get_categories(self.container.curent_category)
        if len(self.container.categories) == 0:
            self.container.tools = ProcessAccess().get_category_processes(self.container.curent_category)
