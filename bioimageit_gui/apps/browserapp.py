import os
import subprocess
from pathlib import Path

import qtpy.QtCore
from qtpy.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                               QLabel, QTabWidget, QHBoxLayout)

from bioimageit_core.config import ConfigAccess
from bioimageit_gui.core.framework import BiAction, BiComponent
from bioimageit_gui.browser.states import BiBrowserStates
from bioimageit_gui.browser.containers import BiBrowserContainer
from bioimageit_gui.browser.components import BiBrowserComponent

from bioimageit_gui.experiment.states import (BiExperimentStates,
                                              BiExperimentCreateStates)
from bioimageit_gui.experiment.containers import (BiExperimentContainer,
                                                  BiExperimentCreateContainer)
from bioimageit_gui.experiment.components import (BiExperimentComponent,
                                                  BiExperimentCreateComponent)
from bioimageit_gui.experiment.models import (BiExperimentCreateModel)
                                            

class BiBrowserApp(BiComponent):
    def __init__(self, bookmarks_file: str):
        super().__init__()

        # container
        self.browserContainer = BiBrowserContainer()
        self.experimentCreateContainer = BiExperimentCreateContainer()
        
        # components
        self.browserComponent = BiBrowserComponent(self.browserContainer)
        self.experimentCreateComponent = \
            BiExperimentCreateComponent(self.experimentCreateContainer)

        # models
        self.expreimentCreateModel = \
            BiExperimentCreateModel(self.experimentCreateContainer)

        # connections
        self.browserContainer.register(self)
        self.experimentCreateContainer.register(self)

        # load settings
        self.browserContainer.currentPath = str(Path.home())
        self.browserContainer.emit(BiBrowserStates.DirectoryModified)

        self.browserComponent.browserModel.loadBookmarks(bookmarks_file)
        self.browserComponent.shortCutComponent.reloadBookmarks()

        # create the widget
        self.widget = QWidget()
        self.widget.setObjectName('bioImageApp')
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        self.tabWidget = QTabWidget()
        layout.addWidget(self.tabWidget)
        self.tabWidget.addTab(self.browserComponent.get_widget(), "Browser")

    def update(self, action: BiAction):
        if action.state == BiBrowserStates.OpenExperiment:
            exp_path = self.browserContainer.openExperimentPath
            if not self.browserContainer.openExperimentPath.\
                    endswith("experiment.md.json"):
                exp_path = os.path.join(exp_path, "experiment.md.json")
            experimentContainer = BiExperimentContainer()
            experimentContainer.experiment_uri = exp_path
            experimentContainer.register(self)
            experimentComponent = BiExperimentComponent(experimentContainer)
            
            self.tabWidget.addTab(
                experimentComponent.get_widget(), "Experiment name")
            self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
            experimentContainer.emit(BiExperimentStates.Load)

        if action.state == BiExperimentStates.CloseClicked:
            self.tabWidget.removeTab(self.tabWidget.currentIndex())
            self.tabWidget.setCurrentIndex(0)

        if action.state == BiExperimentStates.Loaded:
            self.tabWidget.setTabText(self.tabWidget.currentIndex(),
                                      action.parent_container.
                                      experiment.metadata.name)

        if action.state == BiBrowserStates.NewExperimentClicked:
            self.experimentCreateComponent.get_widget().setVisible(True)

        if action.state == BiBrowserStates.OpenFinderClicked:
            finder_app = ConfigAccess.instance().get('apps')['processing']     
            subprocess.Popen([finder_app])

        if action.state == BiExperimentCreateStates.CancelClicked:
            self.experimentCreateComponent.get_widget().setVisible(False)  

        if action.state == BiExperimentCreateStates.ExperimentCreated:
            self.browserContainer.openExperimentPath = \
                self.experimentCreateContainer.experiment_dir
            self.browserContainer.emit(BiBrowserStates.OpenExperiment)
            self.experimentCreateComponent.get_widget().setVisible(False)     

    def get_widget(self):
        return self.widget 
