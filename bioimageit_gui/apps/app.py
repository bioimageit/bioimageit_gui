from bioimageit_framework.theme import BiThemeAccess
from bioimageit_framework.framework import BiComponent
from bioimageit_framework.widgets import BiAppMainWidget

from bioimageit_gui.home import BiHomeComponent, BiHomeContainer


class BioImageITApp(BiComponent):
    def __init__(self):
        super().__init__()

        self.main_widget = BiAppMainWidget()
        self.widget = self.main_widget.widget

        # containers    
        self.homeContainer = BiHomeContainer()

        # components
        self.homeComponent = BiHomeComponent(self.homeContainer)

        self.main_widget.add(self.homeComponent, BiThemeAccess.instance().icon('home'), "Home", False)
