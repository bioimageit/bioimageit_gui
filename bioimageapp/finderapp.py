import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication
import subprocess

from bioimageapp.core.framework import BiStates, BiAction, BiComponent, BiContainer
from bioimageapp.core.exceptions import CommandArgsError
from bioimageapp.finder.states import BiFinderStates
from bioimageapp.finder.containers import BiFinderContainer
from bioimageapp.finder.models import BiFinderModel
from bioimageapp.finder.components import BiFinderComponent

class BiFinderApp(BiComponent):
    def __init__(self):
        super().__init__()

        # components
        self.finderContainer = BiFinderContainer()
        self.finderModel = BiFinderModel(self.finderContainer)
        self.finderComponent = BiFinderComponent(self.finderContainer)

        # initialization
        self.finderContainer.emit(BiFinderStates.Reload)
        self.finderContainer.register(self) 


    def update(self, action: BiAction):
        if action.state == BiFinderStates.OpenProcess:
            subprocess.call(['python3', 'runnerapp.py', self.finderContainer.clicked_tool])

    def get_widget(self):
        return self.finderComponent.get_widget()


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create and show the component
    component = BiFinderApp()
    component.get_widget().show()
    
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "../theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("../theme/default/icon.png"))
    sys.exit(app.exec_())