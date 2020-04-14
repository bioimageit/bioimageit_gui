import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

from bioimageapp.core.framework import BiStates, BiAction, BiComponent, BiContainer
from bioimageapp.core.exceptions import CommandArgsError
from bioimageapp.runner.states import BiRunnerStates
from bioimageapp.runner.containers import BiRunnerContainer
from bioimageapp.runner.models import BiRunnerModel
from bioimageapp.runner.components import BiRunnerComponent

class BiRunnerApp(BiComponent):
    def __init__(self, xml_file: str):
        super().__init__()

        # components
        self.runnerContainer = BiRunnerContainer()
        self.runnerModel = BiRunnerModel(self.runnerContainer)
        self.runnerComponent = BiRunnerComponent(self.runnerContainer)

        # initialization
        self.runnerContainer.process_uri = xml_file
        self.runnerContainer.emit(BiRunnerStates.ProcessUriChanged)


    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.runnerComponent.get_widget()
        