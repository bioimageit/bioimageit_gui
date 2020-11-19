from bioimageit_gui.core.framework import BiAction, BiComponent
from bioimageit_gui.runner.states import BiRunnerStates
from bioimageit_gui.runner.containers import BiRunnerContainer
from bioimageit_gui.runner.models import BiRunnerModel
from bioimageit_gui.runner.components import BiRunnerComponent
from bioimageit_gui.runner.observer import BiGuiProgressObserver


class BiRunnerApp(BiComponent):
    def __init__(self, xml_file: str):
        super().__init__()

        # components
        self.runnerContainer = BiRunnerContainer()
        self.runnerModel = BiRunnerModel(self.runnerContainer)
        self.runnerComponent = BiRunnerComponent(self.runnerContainer)

        # connect observer
        progressObserver = BiGuiProgressObserver()
        self.runnerModel.observer = progressObserver
        progressObserver.progressSignal.connect(
            self.runnerComponent.progressValue)
        progressObserver.messageSignal.connect(
            self.runnerComponent.progressMessage)

        # initialization
        self.runnerContainer.process_uri = xml_file
        self.runnerContainer.emit(BiRunnerStates.ProcessUriChanged)

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.runnerComponent.get_widget()
