import os
import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QSplitter)

from bioimageit_gui.core.framework import BiAction, BiComponent
from bioimageit_gui.runner import (BiRunnerStates, BiRunnerContainer, 
                                   BiRunnerModel, BiRunnerComponent, 
                                   BiGuiProgressObserver)


class BiRunnerViewApp(BiComponent):
    def __init__(self, xml_file: str, viewer):
        super().__init__()
        self.viewer = viewer

        # components
        self.runnerContainer = BiRunnerContainer()
        self.runnerModel = BiRunnerModel(self.runnerContainer)
        self.runnerComponent = BiRunnerComponent(self.runnerContainer)
        self.runnerContainer.register(self)

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

        # Widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        layout.addWidget(self.runnerComponent.get_widget())

    def update(self, action: BiAction):
        if action.state == BiRunnerStates.RunFinished:
            for out in self.runnerContainer.genarated_outputs:
                self.viewer.set_visible(True)
                for fileinfo in out:
                    print('open output', fileinfo)
                    name = os.path.basename(fileinfo['uri'])
                    self.viewer.add_data(fileinfo['uri'], name, fileinfo['format'])
        if action.state == BiRunnerStates.ClickedView:
            self.viewer.set_visible(True)
            name = os.path.basename(self.runnerContainer.clicked_view_uri)
            print("view data with info:")
            print("name:", name)
            print("uri:", self.runnerContainer.clicked_view_uri)
            print("format:", self.runnerContainer.clicked_view_format)
            self.viewer.add_data(self.runnerContainer.clicked_view_uri, 
                                          name, 
                                          self.runnerContainer.clicked_view_format)  

    def get_widget(self):
        return self.widget


class BiRunnerApp(BiComponent):
    def __init__(self, xml_file: str):
        super().__init__()
        self.show_viewer = True

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

        # Widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        layout.addWidget(self.runnerComponent.get_widget())

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget
