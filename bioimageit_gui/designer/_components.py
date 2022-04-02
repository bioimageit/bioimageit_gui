from qtpy.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSplitter)

from bioimageit_framework.framework import BiComponent

from ._tools_widget import BiDesignerTools
from ._editor_widget import BiDesignerEditorWidget
from ._scene import BiDesignerView


class BiDesigner(BiComponent):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiDesignerComponent'

        self.designer_component = BiDesignerComponent()
        self.widget = self.designer_component.widget


class BiDesignerComponent(BiComponent):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiDesignerComponent'

        self.tools_widget = BiDesignerTools() 
        self.editor_widget = BiDesignerEditorWidget() 

        self.widget = QSplitter()
        self.widget.addWidget(self.tools_widget)
        self.widget.addWidget(self.editor_widget)
        self.widget.setStretchFactor(0, 1)
        self.widget.setStretchFactor(1, 7)
