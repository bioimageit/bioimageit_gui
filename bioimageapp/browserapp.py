import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSplitter
from framework import (BiComponent, BiContainer)
from browser import (BiBrowserContainer, BiBrowserModel, BiBrowserToolBarComponent, BiBrowserShortCutsComponent, BiBrowserTableComponent, BiBrowserPreviewComponent)
                   
class bioImageApp(BiComponent):
    def __init__(self):
        super(bioImageApp, self).__init__()
        self._object_name = 'bioImageApp'

        # container
        self.browserContainer = BiBrowserContainer()
        
        # model
        self.browserModel = BiBrowserModel(self.browserContainer)

        # components
        self.toolBarComponent = BiBrowserToolBarComponent(self.browserContainer)
        self.shortCutComponent = BiBrowserShortCutsComponent(self.browserContainer)
        self.tableComponent = BiBrowserTableComponent(self.browserContainer)
        self.previewComponent = BiBrowserPreviewComponent(self.browserContainer)

        # connections

        # crete the widget
        self.widget = QWidget()
        self.widget.setObjectName('bioImageApp')
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)

        splitter = QSplitter()

        layout.addWidget(self.toolBarComponent.get_widget())
        layout.addWidget(splitter)

        splitter.addWidget(self.shortCutComponent.get_widget())
        splitter.addWidget(self.tableComponent.get_widget())
        splitter.addWidget(self.previewComponent.get_widget())

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        

    def update(self, container: BiContainer):
        pass   
   
    def get_widget(self):
        return self.widget 

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = bioImageApp()
    form.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    sys.exit(app.exec_())