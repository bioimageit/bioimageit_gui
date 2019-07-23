import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

# add bioimagepy to path for dev
sys.path.append("/Users/sprigent/Documents/code/bioimagepy")

from framework import BiStates, BiAction, BiComponent, BiContainer
from processbrowser import (BiProcessesBrowserStates, BiProcessesBrowserComponent, 
                            BiProcessesBrowserContainer, BiProcessesBrowserModel)



class BiProcessesBrowserApp(BiComponent):
    def __init__(self, processesDir: str):
        super().__init__()

        # components
        self.processesBrowserContainer = BiProcessesBrowserContainer()
        self.processesBrowserModel = BiProcessesBrowserModel(self.processesBrowserContainer)
        self.processesBrowserComponent = BiProcessesBrowserComponent(self.processesBrowserContainer)

        # initialization
        self.processesBrowserContainer.processesDir = processesDir
        self.processesBrowserContainer.emit(BiProcessesBrowserStates.ProcessesDirChanged)


    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.processesBrowserComponent.get_widget()


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # load the settings
    processesDir = ""
    if len(sys.argv) > 1:
        processesDir = sys.argv[1]
    if processesDir == "":
        processesDir = "../bioimageit/data/processes"

    
    # Create and show the component
    component = BiProcessesBrowserApp(processesDir)
    component.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../bioimageapp/theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("../bioimageapp/theme/default/icon.png"))
    sys.exit(app.exec_())