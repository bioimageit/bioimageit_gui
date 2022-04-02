from qtpy.QtWidgets import (QWidget, QVBoxLayout, QLabel)

from bioimageit_framework.framework import BiComponent

from ._containers import BiDesignerContainer
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
        
        #self.container = container
        #self.container.register(self)  

        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        self.view = BiDesignerView()
        layout.addWidget(self.view)

        #label = QLabel('The pipeline designer is not yet implemented')
        #label.setObjectName("BiWidget")
        #layout.addWidget(label)
