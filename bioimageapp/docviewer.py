import sys
import os
import json
import PySide2.QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea, QToolButton, QPushButton 

from framework import BiContainer, BiModel, BiComponent
from widgets import BiToolButton

class BiDocViewerContainer(BiContainer):
    ContentLoaded = "BiDocViewerContainer::ContentLoaded"
    PathChanged = "BiDocViewerContainer::PathChanged"

    def __init__(self):
        super(BiDocViewerContainer, self).__init__()
        self._object_name = 'BiDocViewerContainer'
        self.content_path = ''
        self.content = ''
 

class BiDocViewerModel(BiModel):
    def __init__(self, container: BiDocViewerContainer):
        super(BiDocViewerModel, self).__init__()
        self._object_name = 'BiDocViewerModel'  
        self.container = container
        self.container.addObserver(self)

    def update(self, container: BiContainer):
        if container.action == BiDocViewerContainer.PathChanged:
            if os.path.getsize(self.container.content_path) > 0:
                with open(self.container.content_path) as json_file:  
                    self.container.content = json.load(json_file)  
                    self.container.notify(BiDocViewerContainer.ContentLoaded) 


class BiDocViewerComponent(BiComponent):

    def __init__(self, container: BiDocViewerContainer):
        super(BiDocViewerComponent, self).__init__()
        self._object_name = 'BiDocEditorComponent'
        self.container = container
        self.container.addObserver(self)

        self.widget = QScrollArea()
        
        self.widget.setWidgetResizable(True)
        self.widget.setHorizontalScrollBarPolicy(PySide2.QtCore.Qt.ScrollBarAlwaysOff)
        
        mainWidget = QWidget()
        mainWidget.setObjectName('BiWidget')
        self.widget.setWidget(mainWidget)
        self.widget.setObjectName('BiWidget')
        mainWidget.setMaximumWidth(900)

        self.layout = QVBoxLayout()
        containerWidget = QWidget()
        containerLayout = QVBoxLayout()
        containerWidget.setLayout(self.layout)
        containerLayout.addWidget(containerWidget)
        mainWidget.setLayout(containerLayout)

    def fillWidget(self):

        if 'title' in self.container.content:
            widget = QLabel("<h1>" + self.container.content["title"] + "</h1>")
            widget.setWordWrap(True)
            widget.setObjectName("BiWidget")
            self.layout.addWidget(widget, 0, PySide2.QtCore.Qt.AlignTop) 

        for cell in self.container.content["cells"]:
            if cell["celltype"] == "text":
                widget = QLabel(cell["text"])
                widget.setWordWrap(True)
                widget.setObjectName("BiWidget")
                self.layout.addWidget(widget, 0, PySide2.QtCore.Qt.AlignTop) 
            elif cell["celltype"] == "action":
                button = BiToolButton()
                button.content = cell["action"]
                button.setObjectName(cell["button"])
                button.clickedContent.connect(self.actionClicked)  
                self.layout.addWidget(button, 0, PySide2.QtCore.Qt.AlignTop | PySide2.QtCore.Qt.AlignHCenter) 
                
        self.layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop )             

    def actionClicked(self, content: str):
        print('cutton clicked with content:', content)
        self.container.notify(content)

    def update(self, container: BiContainer):
        if container.action == BiDocViewerContainer.ContentLoaded:
            self.fillWidget()      

    def get_widget(self): 
        return self.widget   


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # load the settings
    json_doc_file = ""
    if len(sys.argv) > 1:
        json_doc_file = sys.argv[1]
    else:
        json_doc_file = 'bioimageapp/experimentdoc.json'    
    
    # Create and show the component
    container = BiDocViewerContainer()
    model = BiDocViewerModel(container)
    component = BiDocViewerComponent(container)

    container.content_path = json_doc_file
    container.notify(BiDocViewerContainer.PathChanged)

    component.get_widget().show() 
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("../bioimageapp/theme/default/icon.png"))
    sys.exit(app.exec_())
