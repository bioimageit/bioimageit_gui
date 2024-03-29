import qtpy.QtCore
from qtpy.QtCore import Signal, QMimeData, QUrl, QByteArray
from qtpy.QtGui import QPixmap, QDrag, QIcon
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QScrollArea, QComboBox

from bioimageit_framework.theme import BiThemeAccess
from bioimageit_core.api import APIAccess


class BiDesignerToolsArea(QWidget):
    def __init__(self):
        super().__init__()

        self._widgets = {}

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        widget_area = QWidget()
        widget_area.setLayout(self.layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._toolbar = BiDesignerToolsAreaBar()
        self._toolbar.back.connect(self._show_tools)
        layout.addWidget(self._toolbar, 0, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(widget_area, 1)
        self.setLayout(layout)

    def add_widget(self, id, widget):
        self._widgets[id] = widget
        self.layout.addWidget(widget)
        self.show_widget(id)

    def remove_widget(self, id):
        self.layout.removeWidget(self._widgets[id])

    def show_widget(self, id):
        print('show widget:', id)
        self._toolbar.change_text(id)
        if id == 'Tools':
            self._toolbar.set_back_button_visible(False)
        else:
            self._toolbar.set_back_button_visible(True)    
        for key, widget in self._widgets.items():
            if key == id:
                widget.setVisible(True)
            else:
                widget.setVisible(False)      

    def _show_tools(self):
        self.show_widget('Tools')                  


class BiDesignerToolsAreaBar(QWidget):
    back = Signal()

    def __init__(self):
        super().__init__()  

        self.back_button = QToolButton()
        self.back_button.setIcon(QIcon(BiThemeAccess.instance().icon('arrow-left')))
        self.back_button.clicked.connect(self._emit_back)
        self.label = QLabel()

        layout = QHBoxLayout()
        layout.setContentsMargins(7, 0, 0, 0)
        layout.addWidget(self.back_button)
        layout.addWidget(self.label)
        
        widget = QWidget()
        tlayout = QVBoxLayout()
        tlayout.setContentsMargins(0, 0, 0, 0)
        tlayout.addWidget(widget)

        widget.setLayout(layout)
        widget.setObjectName('bi-toolbar')
        self.setLayout(tlayout)

    def _emit_back(self):
        self.back.emit()    

    def change_text(self, text):
        self.label.setText(text)

    def set_back_button_visible(self, visible):
        self.back_button.setVisible(visible) 




class BiDesignerTools(QWidget):
    def __init__(self):
        super().__init__()
        self.req = APIAccess.instance()

        categories_names = []
        categories = self.req.get_categories('root')
        for category in categories:
            categories_names.append(category.id)
        #print('categories=', categories_names)
        self.tools_bar = BiDesignerToolsBar(categories_names)
        self.tools_list = BiDesignerToolsList()
        self.tools_footer = BiDesignerToolsFooter()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tools_bar)
        layout.addWidget(self.tools_list)
        layout.addWidget(self.tools_footer)
        self.setLayout(layout)

        self.tools_bar.changed_toolbox.connect(self.browse)

    def browse(self, category):   
        tools = self.req.get_category_tools(category)
        self.tools_list.load_tools(tools)


class BiDesignerToolsBar(QWidget):
    changed_toolbox = Signal(str)

    def __init__(self, categories):
        super().__init__()

        self.categories_box = QComboBox()
        self.categories_box.addItems(categories)
        self.categories_box.currentTextChanged.connect(self.show_toolbox)

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 0, 4, 0)
        layout.addWidget(self.categories_box)
        
        widget = QWidget()
        tlayout = QVBoxLayout()
        tlayout.setContentsMargins(0, 0, 0, 0)
        tlayout.addWidget(widget)

        widget.setLayout(layout)
        self.setLayout(tlayout)

    def show_toolbox(self, toolbox_name):
        self.changed_toolbox.emit(toolbox_name)


class BiDesignerTool(QWidget):
    def __init__(self, tool):
        super().__init__()
        self.tool = tool

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(tool.name)
        label.setStyleSheet('background-color:#0071C3; border-radius: 5px; min-height:40px; qproperty-alignment: AlignCenter;')
        layout.addWidget(label)
        self.setLayout(layout)

    def id(self):
        return self.tool.uri


class BiDesignerToolIO(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(name)
        label.setStyleSheet('background-color:#007100; border-radius: 5px; min-height:40px; qproperty-alignment: AlignCenter;')
        layout.addWidget(label)
        self.setLayout(layout)

    def id(self):
        return self.name            
        

class BiDropWidget(QWidget):
    def __init__(self):
        super().__init__()

    def dragEnterEvent(self, event): # QDragEnterEvent
        if event.mimeData().hasFormat("application/x-dnditemdata"):
            if event.source() == self:
                event.setDropAction(qtpy.QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event): # QDragMoveEvent
        if event.mimeData().hasFormat("application/x-dnditemdata"):
            if event.source() == self:
                event.setDropAction(qtpy.QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        pass

    def mousePressEvent(self, event): # QMouseEvent
        #print('mouse press event')
        child = self.childAt(event.pos()).parent()
        #print('child type=', type(child))
        if child is not None and (isinstance(child, BiDesignerTool) or isinstance(child, BiDesignerToolIO)) :
            hotSpot = event.pos() - child.pos()
            mimeData = QMimeData()
            #print("tool id = ", child.id())
            urls = [QUrl(child.id())]
            mimeData.setUrls(urls)
            #mimeData.setText(child.text())
            mimeData.setData("application/x-hotspot",
                             QByteArray.number(hotSpot.x())
                             + " " + QByteArray.number(hotSpot.y()))

            pixmap = QPixmap(child.size())
            child.render(pixmap)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(hotSpot)

            dropAction = drag.exec_(qtpy.QtCore.Qt.CopyAction | qtpy.QtCore.Qt.MoveAction, qtpy.QtCore.Qt.CopyAction)

            #if dropAction == qtpy.QtCore.Qt.MoveAction:
            #    child.close()


class BiDesignerToolsList(BiDropWidget):
    def __init__(self):
        super().__init__()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        scroll_area.setWidget(self.widget)

    def load_tools(self, tools_list):
        """Load the tools in the list

        Parameters
        ----------
        tools_list: list
            List of Tools objects

        """    
        # free layout
        if self.layout.count() > 0:
            for i in reversed(range(self.layout.count())): 
                self.layout.itemAt(i).widget().deleteLater()
        # add tools    
        for tool in tools_list:
            self.layout.addWidget(BiDesignerTool(tool), 0, qtpy.QtCore.Qt.AlignTop)
        self.layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignBottom)


class BiDesignerToolsFooter(BiDropWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(BiDesignerToolIO('Data'))
        layout.addWidget(BiDesignerToolIO('Save'))
        self.setLayout(layout)
