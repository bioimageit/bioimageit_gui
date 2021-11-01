import os
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QSplitter)

from bioimageit_gui.core.framework import BiAction, BiComponent
from bioimageit_gui.runner.states import BiRunnerStates
from bioimageit_gui.runner.containers import BiRunnerContainer
from bioimageit_gui.runner.models import BiRunnerModel
from bioimageit_gui.runner.components import BiRunnerComponent
from bioimageit_gui.runner.observer import BiGuiProgressObserver

from bioimageit_gui.dataviewer.dataview import BiDataView
from bioimageit_viewer.viewer2 import BiMultiViewer


class BiRunnerViewApp(BiComponent):
    def __init__(self, xml_file: str):
        super().__init__()

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

        # viewer widget
        self.viewerComponent = BiMultiViewer()
        self.viewerComponent.setMinimumWidth(400)

        # Widget
        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        splitter = QSplitter()
        splitter.addWidget(self.runnerComponent.get_widget())
        splitter.addWidget(self.viewerComponent)
        layout.addWidget(splitter)

        #self.viewerComponent.setVisible(False)

    def update(self, action: BiAction):
        if action.state == BiRunnerStates.RunFinished:
            for out in self.runnerContainer.genarated_outputs:
                for fileinfo in out:
                    print('open output', fileinfo)
                    name = os.path.basename(fileinfo['uri'])
                    self.viewerComponent.add_data(fileinfo['uri'], name, fileinfo['format'])
        if action.state == BiRunnerStates.ClickedView:
            name = os.path.basename(self.runnerContainer.clicked_view_uri)

            print("view data with info:")
            print("name:", name)
            print("uri:", self.runnerContainer.clicked_view_uri)
            print("format:", self.runnerContainer.clicked_view_format)
            self.viewerComponent.add_data(self.runnerContainer.clicked_view_uri, 
                                          name, 
                                          self.runnerContainer.clicked_view_format)  

    def get_widget(self):
        return self.widget


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
        if action.state == BiRunnerStates.RunFinished:
            for out in self.container.genarated_outputs:
                for fileinfo in out:
                    print('open output', fileinfo)
                    viewer = BiDataView(fileinfo['uri'], fileinfo['format'])
                    viewer.show()
        if action.state == BiRunnerContainer.ClickedView:
            viewer = BiDataView(self.clicked_view_uri, self.clicked_view_format)
            viewer.show()          

    def get_widget(self):
        return self.runnerComponent.get_widget()
