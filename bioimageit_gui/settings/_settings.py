from qtpy.QtWidgets import (QWidget, QVBoxLayout, QLabel)

from bioimageit_gui.core.framework import BiComponent, BiAction

from ._components import BiConfigComponent
from ._containers import BiConfigContainer
from ._models import BiConfigModel


class BiSettingsComponent(BiComponent):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiSettingsComponent'

        # containers
        self.config_container = BiConfigContainer()

        # components
        self.config_component = BiConfigComponent(self.config_container)

        # models
        self.config_model = BiConfigModel(self.config_container)

        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        layout.addWidget(self.config_component.get_widget())

    def update(self, action: BiAction):
        pass 

    def get_widget(self): 
        return self.widget