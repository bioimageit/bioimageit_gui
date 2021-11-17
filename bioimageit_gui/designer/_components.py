from PySide2.QtWidgets import (QWidget, QVBoxLayout, QLabel)

from bioimageit_gui.core.framework import BiComponent, BiAction

from ._containers import BiDesignerContainer


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

        label = QLabel('The pipeline designer is not yet implemented')
        label.setObjectName("BiWidget")
        layout.addWidget(label)

    def update(self, action: BiAction):
        pass 

    def get_widget(self): 
        return self.widget  
