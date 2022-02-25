from bioimageit_framework.framework import BiComponent
from bioimageit_framework.widgets import BiVComposer, BiNavigationBar

from bioimageit_gui.finder.containers import BiFinderContainer
from bioimageit_gui.finder.widgets import BiProcessCategoryTile, BiCategoriesBrowser, BiToolsBrowser


class BiFinderComponent(BiComponent):
    PREVIOUS = 'previous'
    NEXT = 'next'
    HOME = 'home'
    OPEN_TILE = 'open_tile'
    OPEN_TOOL = 'open_tool'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiFinderComponent' 
        self.historyPaths = []
        self.posHistory = 0
        self.currentPath = ''

        self.composer = BiVComposer()
        self.widget = self.composer.widget

        # navigation bar
        self.navbar = BiNavigationBar()
        self.navbar.connect(BiNavigationBar.PREVIOUS, self.previous)
        self.navbar.connect(BiNavigationBar.NEXT, self.next)
        self.navbar.connect(BiNavigationBar.HOME, self.home)
        self.composer.add(self.navbar)

        # categories browser
        self.categories_browser = BiCategoriesBrowser()
        self.categories_browser.connect(BiCategoriesBrowser.OPEN, self.clicked_tile)
        self.composer.add(self.categories_browser)
        
        # tools browser
        self.tools_browser = BiToolsBrowser()
        self.tools_browser.connect(BiToolsBrowser.OPEN, self.open_clicked)
        self.composer.add(self.tools_browser)
        self.tools_browser.set_visible(False)

    def previous(self, _):
        self._emit(BiFinderComponent.PREVIOUS)

    def next(self, _):
        self._emit(BiFinderComponent.NEXT)

    def home(self, _):
        self._emit(BiFinderComponent.HOME)    

    def browse(self, emitter):
        if len(emitter.categories) > 0:
            self.browse_categories(emitter.categories)
            self.tools_browser.set_visible(False)
            self.categories_browser.set_visible(True)
        else:
            self.browse_tools(emitter.tools)  
            self.tools_browser.set_visible(True)
            self.categories_browser.set_visible(False)      

    def browse_tools(self, tools):
        self.tools_browser.browse(tools)

    def browse_categories(self, categories):
        self.categories_browser.browse(categories)

    def clicked_tile(self, origin):
        self._emit(BiFinderComponent.OPEN_TILE, origin.clicked_info)

    def open_clicked(self, origin):
        self._emit(BiFinderComponent.OPEN_TOOL, origin.clicked_id)  

    def callback_reloaded(self, emitter):
        self.navbar.set_path(emitter.curent_category_name)
        self.browse(emitter)
