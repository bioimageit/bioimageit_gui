import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon, QPainter
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QToolButton, QGraphicsView

from bioimageit_framework.theme import BiThemeAccess
from bioimageit_core.api import APIAccess

from ._scene import BiDesignerGraphicScene, BiDesignerGraphicView, BiDesignerViewNodesEditor
from ._scene_items import BiDesignerViewNodeSave, BiDesignerViewNodeData, BiDesignerViewNodeTool


class BiDesignerEditorWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.toolbar = BiDesignerEditorBar()
        self.view = BiDesignerEditorView()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.view)
        self.setLayout(layout)


class BiDesignerEditorBar(QWidget):
    play = Signal()
    stop = Signal()
    save = Signal()

    def __init__(self):
        super().__init__()   

        run_btn = QToolButton()
        run_btn.setIcon(QIcon(BiThemeAccess.instance().icon('play')))
        run_btn.released.connect(self.emit_play)
        stop_btn = QToolButton()
        stop_btn.setIcon(QIcon(BiThemeAccess.instance().icon('stop')))
        stop_btn.released.connect(self.emit_stop)
        save_btn = QToolButton()
        save_btn.setIcon(QIcon(BiThemeAccess.instance().icon('save')))
        save_btn.released.connect(self.emit_save)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        spacer1 = QWidget()
        spacer1.setObjectName('bi-toolbar')
        layout.addWidget(spacer1, 1)
        layout.addWidget(run_btn, 0, qtpy.QtCore.Qt.AlignCenter)
        layout.addWidget(stop_btn, 0, qtpy.QtCore.Qt.AlignCenter)
        spacer2 = QWidget()
        spacer2.setObjectName('bi-toolbar')
        layout.addWidget(spacer2, 1)
        layout.addWidget(save_btn, 0, qtpy.QtCore.Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        tlayout = QVBoxLayout()
        tlayout.setContentsMargins(0, 0, 0, 0)
        tlayout.addWidget(widget)

        self.setLayout(tlayout)
        widget.setObjectName('bi-toolbar')

    def emit_play(self):
        self.play.emit()

    def emit_stop(self):
        self.stop.emit()    

    def emit_save(self):
        self.save.emit()     


class BiDesignerEditorView(QWidget):
    added_node = Signal(str, QWidget)
    show_node_widget = Signal(str)

    def __init__(self):
        super().__init__()

        self.req = APIAccess.instance()
        self.count = 0
        self.scene = BiDesignerGraphicScene()
        self.scene.ask_new_node.connect(self.add_node)

        self.view = BiDesignerGraphicView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.nodes_editor = BiDesignerViewNodesEditor(True, self)
        self.nodes_editor.install(self.scene)
        self.nodes_editor.setView(self.view)
        self.nodes_editor.show_parameters.connect(self._emit_show_node_widget)
    
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)        

    def _emit_show_node_widget(self, id):
        print('BiDesignerEditorView: _emit_show_node_widget id=', id)
        self.show_node_widget.emit(id)    

    def add_node(self, id, pos_x, pos_y):
        print('add note:', type(id), ', ', id, ' at (', pos_x, ', ', pos_y, ')')
        self.count += 1
        if id == 'Save':
            b = BiDesignerViewNodeSave(self.count, None, self.scene)
            b.set_pos(pos_x, pos_y)  
            self.added_node.emit(b.id, b.widget)
        elif id == 'Data':
            b = BiDesignerViewNodeData(self.count, None, self.scene)
            b.set_pos(pos_x, pos_y)  
            self.added_node.emit(b.id, b.widget)
        else:
            tool = self.req.get_tool_from_uri(id)
            b = BiDesignerViewNodeTool(tool, self.count, None, self.scene)
            b.set_pos(pos_x, pos_y)  
            self.added_node.emit(b.id, b.widget)         
