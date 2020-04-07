import PySide2.QtCore
from PySide2.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QSplitter, 
                               QScrollArea, QLabel, QGridLayout, QComboBox,
                               QPushButton, QLineEdit, QCheckBox, QFileDialog,
                               QHBoxLayout, QProgressBar, QTextEdit)

from bioimagepy.process import Process 

from bioimageapp.core.framework import BiComponent, BiAction
from bioimageapp.runner.containers import BiRunnerContainer
from bioimageapp.runner.states import BiRunnerStates
from bioimageapp.runner.widgets import (BiRunnerInputSingleWidget, BiRunnerInputFolderWidget, 
                                        BiRunnerInputExperimentWidget, BiRunnerParamWidget,
                                        BiRunnerExecWidget, BiRunnerProgressWidget) 
from bioimageapp.core.widgets import BiFileSelectWidget


class BiRunnerComponent(BiComponent):

    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self._object_name = 'BiRunnerComponent'
        self.container = container
        self.container.register(self)

        # settings
        self.use_experiment = False

        # mode
        self.container.mode = BiRunnerContainer.MODE_FILE

        # widget
        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)
        execWidget = QWidget()
        execWidget.setObjectName("BiWidgetNegative")
        self.widget.setObjectName("BiWidgetNegative")
        
        execScrollArea = QScrollArea()
        execScrollArea.setObjectName("BiWidgetNegative")
        execScrollArea.setMinimumWidth(300)
        execScrollArea.setWidgetResizable(True)
        execScrollArea.setWidget(execWidget)
        layout.addWidget(execScrollArea)
        self.execLayout = QVBoxLayout()
        execWidget.setLayout(self.execLayout)
        #layout.addWidget(execWidget)

    def update(self, action: BiAction):
        if action.state == BiRunnerStates.ProcessInfoLoaded:
            print("build exec widget") 
            self.buildExecWidget()  

    def buildExecWidget(self):

        process_info = self.container.process_info
        
        # tab widget
        self.fileButton = QPushButton('File')
        self.fileButton.setCheckable(True)
        self.fileButton.setObjectName('btnDefaultLeft')
        self.fileButton.released.connect(self.switchFile)

        self.folderButton = QPushButton('Folder')
        self.folderButton.setCheckable(True)
        self.folderButton.setObjectName('btnDefaultCentral')
        self.folderButton.released.connect(self.switchFolder)
        
        self.experimentButton = QPushButton('Experiment')
        self.experimentButton.setCheckable(True)
        self.experimentButton.setObjectName('btnDefaultRight')
        self.experimentButton.released.connect(self.switchExp)

        tabWidget = QWidget()
        tabLayout = QHBoxLayout()
        tabLayout.setContentsMargins(0,0,0,0)
        tabLayout.setSpacing(0)
        tabLayout.addWidget(self.fileButton)
        tabLayout.addWidget(self.folderButton)
        tabLayout.addWidget(self.experimentButton)
        tabWidget.setLayout(tabLayout)
        self.execLayout.addWidget(tabWidget, 0, PySide2.QtCore.Qt.AlignTop)

        # inputs
        self.inputSingleWidget = BiRunnerInputSingleWidget(process_info)
        self.inputFolderWidget = BiRunnerInputFolderWidget(process_info)
        self.inputExperimentWidget = BiRunnerInputExperimentWidget(process_info)

        self.execLayout.addWidget(self.inputSingleWidget, 0, PySide2.QtCore.Qt.AlignTop)
        self.execLayout.addWidget(self.inputFolderWidget, 0, PySide2.QtCore.Qt.AlignTop)
        self.execLayout.addWidget(self.inputExperimentWidget, 0, PySide2.QtCore.Qt.AlignTop)

        # parameters
        self.paramWidget = BiRunnerParamWidget(process_info)
        self.execLayout.addWidget(self.paramWidget, 0, PySide2.QtCore.Qt.AlignTop)

        # exec
        self.execWidget = BiRunnerExecWidget()
        self.execLayout.addWidget(self.execWidget, 0, PySide2.QtCore.Qt.AlignTop)
        self.execWidget.runSignal.connect(self.run)

        # progess
        self.progressWidget = BiRunnerProgressWidget()
        self.execLayout.addWidget(self.progressWidget, 0, PySide2.QtCore.Qt.AlignTop)

        # fill
        fillWidget = QWidget()
        self.execLayout.addWidget(fillWidget, 1, PySide2.QtCore.Qt.AlignTop)

        # hide parameters if there are no parameter
        if process_info.metadata.param_size() < 1:
            self.paramWidget.setVisible(False)
        self.inputExperimentWidget.setVisible(self.use_experiment)  

        self.switchFile()       
        
    def switchFile(self):
        self.swithMode(BiRunnerContainer.MODE_FILE)
    
    def switchFolder(self):
        self.swithMode(BiRunnerContainer.MODE_REP)

    def switchExp(self):
        self.swithMode(BiRunnerContainer.MODE_EXP)    

    def swithMode(self, mode: str):
        self.container.mode = mode
        if mode == BiRunnerContainer.MODE_FILE:
            self.inputSingleWidget.setVisible(True)
            self.inputFolderWidget.setVisible(False)
            self.inputExperimentWidget.setVisible(False)
            self.fileButton.setChecked(True)
            self.folderButton.setChecked(False)
            self.experimentButton.setChecked(False)
        elif mode == BiRunnerContainer.MODE_REP:     
            self.inputSingleWidget.setVisible(False)
            self.inputFolderWidget.setVisible(True)
            self.inputExperimentWidget.setVisible(False)
            self.fileButton.setChecked(False)
            self.folderButton.setChecked(True)
            self.experimentButton.setChecked(False)
        elif mode == BiRunnerContainer.MODE_EXP:
            self.inputSingleWidget.setVisible(False)
            self.inputFolderWidget.setVisible(False)
            self.inputExperimentWidget.setVisible(True)
            self.fileButton.setChecked(False)
            self.folderButton.setChecked(False)
            self.experimentButton.setChecked(True)

    def run(self):
        # create the input datalist
        if self.container.mode == BiRunnerContainer.MODE_FILE:
            self.container.inputs = self.inputSingleWidget.inputs()
            self.container.output_uri = ''
        elif self.container.mode == BiRunnerContainer.MODE_REP: 
            self.container.inputs = self.inputFolderWidget.inputs()
            self.container.output_uri = self.inputFolderWidget.output()
        elif self.container.mode == BiRunnerContainer.MODE_EXP:
            self.container.inputs = self.inputExperimentWidget.inputs() 
            self.container.output_uri = self.inputFolderWidget.output()   
 
        self.container.parameters = self.paramWidget.parameters()

        print('run clicked with data:')
        print('inputs:', self.container.inputs)
        print('parameters:', self.container.parameters)
        print('output:', self.container.output_uri)
        
        #self.container.emit(BiRunnerStates.RunProcess)

    def get_widget(self):
        return self.widget      