from PySide2.QtWidgets import (QVBoxLayout, QWidget, QLabel, QHBoxLayout)

from bioimageit_gui.core.theme import BiThemeAccess

from bioimageit_gui.core.widgets import BiAppBar, BiStaticStackedWidget
from bioimageit_gui.core.framework import (BiAction, BiComponent)
from bioimageit_gui.home import BiHomeComponent, BiHomeContainer, BiHomeStates

from bioimageit_gui.finder.states import BiFinderStates
from bioimageit_gui.finder.containers import BiFinderContainer
from bioimageit_gui.finder.models import BiFinderModel
from bioimageit_gui.finder.components import BiFinderComponent


class BioImageITApp(BiComponent):
    def __init__(self):
        super().__init__()

        self.browser_tab_id = -1
        self.toolboxes_tab_id = -1

        # containers    
        self.homeContainer = BiHomeContainer()
        self.finderContainer = BiFinderContainer()

        # components
        self.homeComponent = BiHomeComponent(self.homeContainer)
        self.finderComponent = BiFinderComponent(self.finderContainer)

        # models
        self.finderModel = BiFinderModel(self.finderContainer)

        # register
        self.homeContainer.register(self)
        self.finderContainer.emit(BiFinderStates.Reload)
        self.finderContainer.register(self)

        self.widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)
        
        self.mainBar = BiAppBar()
        self.mainBar.setStyleSheet('QLabel{background-color:#414851;}')
        self.stackedWidget = BiStaticStackedWidget(self.widget)
        layout.addWidget(self.mainBar)
        layout.addWidget(self.stackedWidget)

        self.mainBar.open.connect(self.slide_to)


        # home component
        self.mainBar.addButton(BiThemeAccess.instance().icon('home'), "Home", 0, False)
        self.stackedWidget.addWidget(self.homeComponent.get_widget())
        self.mainBar.setChecked(0, True)


    def update(self, action: BiAction):
        if action.state == BiHomeStates.OpenBrowser:
            self.open_browser()
        elif action.state == BiHomeStates.OpenToolboxes:
            self.open_toolboxes()    

    def slide_to(self, id: int):
        self.stackedWidget.slideInIdx(id)
        self.mainBar.setChecked(id, False)

    def open_browser(self):
        if self.browser_tab_id < 0:
            widget = QLabel('Hello Browser')
            widget.setObjectName('BiWidget')
            self.stackedWidget.addWidget(widget)
            self.browser_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('open-folder_negative'), 
                                   "Browser", 
                                   self.browser_tab_id, False)

        self.stackedWidget.slideInIdx(self.browser_tab_id)
        self.mainBar.setChecked(self.browser_tab_id, True)

    def open_toolboxes(self):
        if self.toolboxes_tab_id < 0:
            self.stackedWidget.addWidget(self.finderComponent.get_widget())
            self.toolboxes_tab_id = self.stackedWidget.count()-1
            self.mainBar.addButton(BiThemeAccess.instance().icon('tools'), 
                                   "Browser", 
                                   self.toolboxes_tab_id, False)

        self.stackedWidget.slideInIdx(self.toolboxes_tab_id)
        self.mainBar.setChecked(self.toolboxes_tab_id, True)
    
    def get_widget(self):
        return self.widget    
