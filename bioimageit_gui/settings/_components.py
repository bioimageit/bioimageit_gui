import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QMessageBox)

from bioimageit_core.config import ConfigAccess

from bioimageit_gui.core.framework import BiComponent, BiAction

from ._containers import BiConfigContainer
from ._widgets import BiConfigWidget
from ._states import BiConfigStates

  
class BiConfigComponent(BiComponent):
    def __init__(self, container: BiConfigContainer):
        self._object_name = 'BiConfigComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)

        self.config_widget = BiConfigWidget(ConfigAccess.instance().config)
        self.config_widget.cancel.connect(self.reload)
        self.config_widget.validate.connect(self.save)
        self.config_widget.setMinimumWidth(500)
        layout.addWidget(self.config_widget, 0, qtpy.QtCore.Qt.AlignHCenter)

    def reload(self):
        self.config_widget.reload(ConfigAccess.instance().config)

    def save(self):
        self.container.config = self.config_widget.get_config()
        self.container.emit(BiConfigStates.ConfigEdited)        

    def update(self, action: BiAction):
        if action.state == BiConfigStates.ConfigSaved:
            msgBox = QMessageBox()
            msgBox.setText("The new configuration has been saved. You may need to restart the application.")
            msgBox.exec() 

    def get_widget(self):
        return self.widget       
