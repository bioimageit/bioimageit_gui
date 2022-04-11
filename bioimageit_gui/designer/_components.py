from qtpy.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSplitter)

from bioimageit_framework.framework import BiComponent

from ._tools_widget import BiDesignerToolsArea, BiDesignerTools
from ._editor_widget import BiDesignerEditorWidget
from ._scene import BiDesignerView


class BiDesigner(BiComponent):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiDesignerComponent'
        self.widget = BiDesignerWidget()


class BiDesignerWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.toolbar_widget = BiDesignerToolsArea() 
        self.toolbar_widget.add_widget('Tools', BiDesignerTools())
        self.toolbar_widget.show_widget('Tools')
        self.editor_widget = BiDesignerEditorWidget() 
        self.editor_widget.view.added_node.connect(self._add_node_widget)
        self.editor_widget.view.show_node_widget.connect(self._show_node_widget)

        self.widget = QSplitter()
        self.widget.addWidget(self.toolbar_widget)
        self.widget.addWidget(self.editor_widget)
        self.widget.setStretchFactor(0, 1)
        self.widget.setStretchFactor(1, 7)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def _add_node_widget(self, id, widget):
        self.toolbar_widget.add_widget(id, widget)

    def _show_node_widget(self, id):
        print('BiDesignerWidget: _show_node_widget: ', id)
        self.toolbar_widget.show_widget(id)    
