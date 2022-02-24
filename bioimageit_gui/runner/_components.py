from PySide2.QtWidgets import QGroupBox
import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QHBoxLayout, 
                            QLabel, QPushButton, 
                            QVBoxLayout, QScrollArea)

from bioimageit_core import ConfigAccess
from bioimageit_gui.core.framework import BiComponent, BiAction

from ._containers import BiRunnerContainer
from ._states import BiRunnerStates
from ._widgets import (BiRunnerInputSingleWidget,
                       BiRunnerInputExperimentWidget,
                       BiRunnerParamWidget,
                       BiRunnerExecWidget,
                       BiRunnerProgressWidget)


class BiRunnerComponent(BiComponent):    
    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self._object_name = 'BiRunnerComponent'
        self.container = container
        self.container.register(self)

        # components    
        toolbar_component = BiRunnerToolbarCommponent(self.container)
        self.editor_component = BiRunnerEditorComponent(self.container)

        # widget
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        layout.addWidget(toolbar_component.get_widget(), 0, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(self.editor_component.get_widget(), 1)

    def progressValue(self, progress: int):
        self.editor_component.progressValue(progress)

    def progressMessage(self, message: str):
        self.editor_component.progressMessage(message)

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget  


class BiRunnerToolbarCommponent(BiComponent):    
    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self._object_name = 'BiRunnerToolbarCommponent'
        self.container = container
        self.container.register(self)

        # widget
        self.widget = QWidget()
        self.widget.setObjectName('BiToolBar')

        layout = QHBoxLayout()
        layout.setContentsMargins(7, 0, 7, 0)
        self.widget.setLayout(layout)

        self.title_label = QLabel()

        btn_widget = QWidget()
        btn_widget.setMaximumWidth(200)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)
        btn_widget.setLayout(btn_layout)
        self.btn_file = QPushButton('File')
        self.btn_file.setCheckable(True)
        self.btn_file.setObjectName('btnDefaultLeft')
        self.btn_file.released.connect(self.switch_to_file_mode)
        self.btn_experiment = QPushButton('Experiment')
        self.btn_experiment.setCheckable(True)
        self.btn_experiment.setObjectName('btnDefaultRight')
        self.btn_experiment.released.connect(self.switch_to_exp_mode)
        btn_layout.addWidget(self.btn_file)
        btn_layout.addWidget(self.btn_experiment)

        layout.addWidget(self.title_label)
        layout.addWidget(btn_widget)

        self.switch_to_exp_mode()

    def switch_to_file_mode(self):
        self.btn_file.setChecked(True)
        self.btn_experiment.setChecked(False)
        self.container.mode = BiRunnerContainer.MODE_FILE
        self.container.emit(BiRunnerStates.ModeChanged)

    def switch_to_exp_mode(self):
        self.btn_file.setChecked(False)
        self.btn_experiment.setChecked(True)
        self.container.mode = BiRunnerContainer.MODE_EXP
        self.container.emit(BiRunnerStates.ModeChanged)        

    def update(self, action: BiAction):
        if action.state == BiRunnerStates.ProcessInfoLoaded:
            self.title_label.setText(self.container.process_info.name)

    def get_widget(self):
        return self.widget          


class BiRunnerEditorComponent(BiComponent):
    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self._object_name = 'BiRunnerEditorComponent'
        self.container = container
        self.container.register(self)

        # widget
        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")
        self.widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        execWidget = QWidget()
        execWidget.setObjectName("BiWidget")
        execWidget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        
        
        execScrollArea = QScrollArea()
        execScrollArea.setObjectName("BiWidget")
        execScrollArea.setMinimumWidth(300)
        execScrollArea.setWidgetResizable(True)
        execScrollArea.setWidget(execWidget)
        layout.addWidget(execScrollArea)
        self.execLayout = QVBoxLayout()
        execWidget.setLayout(self.execLayout)

    def update(self, action: BiAction):
        if action.state == BiRunnerStates.ProcessInfoLoaded:
            self.buildExecWidget() 
        if action.state == BiRunnerStates.ModeChanged:
            self.swithMode(self.container.mode)    

    def buildExecWidget(self):
        process_info = self.container.process_info
        
        # inputs
        inputs_group = QGroupBox('Inputs')
        inputs_layout = QVBoxLayout()
        inputs_group.setLayout(inputs_layout)

        self.inputSingleWidget = BiRunnerInputSingleWidget(process_info)
        self.inputSingleWidget.openViewSignal.connect(self.showData)
        self.inputExperimentWidget = BiRunnerInputExperimentWidget(
            self.container)

        inputs_layout.addWidget(self.inputSingleWidget, 0, qtpy.QtCore.Qt.AlignTop)
        inputs_layout.addWidget(self.inputExperimentWidget, 0, qtpy.QtCore.Qt.AlignTop)

        self.execLayout.addWidget(inputs_group, 0, qtpy.QtCore.Qt.AlignTop)

        # parameters
        parameters_group = QGroupBox('Parameters')
        parameters_layout = QVBoxLayout()
        parameters_group.setLayout(parameters_layout)
 
        self.paramWidget = BiRunnerParamWidget(process_info)
        parameters_layout.addWidget(self.paramWidget)

        self.execLayout.addWidget(parameters_group, 0, qtpy.QtCore.Qt.AlignTop)

        # exec
        exec_group = QGroupBox('Exec')
        exec_layout = QVBoxLayout()
        exec_group.setLayout(exec_layout)

        self.execWidget = BiRunnerExecWidget()

        exec_layout.addWidget(self.execWidget)
        self.execLayout.addWidget(exec_group, 0, qtpy.QtCore.Qt.AlignTop)
        self.execWidget.runSignal.connect(self.run)

        # progess
        progress_group = QGroupBox('Progress')
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)

        self.progressWidget = BiRunnerProgressWidget()
        progress_layout.addWidget(self.progressWidget)
        self.execLayout.addWidget(progress_group, 0, qtpy.QtCore.Qt.AlignTop)

        # fill
        fillWidget = QWidget()
        self.execLayout.addWidget(fillWidget, 1, qtpy.QtCore.Qt.AlignTop)

        # hide parameters if there are no parameter
        if process_info.param_size() < 1:
            self.paramWidget.setVisible(False)      

        self.swithMode(self.container.mode)     
        
    def showData(self, uri: str, format_: str):
        print("open data", uri)
        print("format", format_)

        self.container.clicked_view_uri = uri
        self.container.clicked_view_format = format_
        self.container.emit(BiRunnerStates.ClickedView)

    def swithMode(self, mode: str):
        self.container.mode = mode
        if mode == BiRunnerContainer.MODE_FILE:
            self.inputSingleWidget.setVisible(True)
            self.inputExperimentWidget.setVisible(False)
        elif mode == BiRunnerContainer.MODE_EXP:
            self.inputSingleWidget.setVisible(False)
            self.inputExperimentWidget.setVisible(True)
                
    def run(self):
        # create the input datalist
        if self.container.mode == BiRunnerContainer.MODE_FILE:
            self.container.inputs = self.inputSingleWidget.inputs()
            config = ConfigAccess.instance().config
            self.container.output_uri = ''
            if 'workspace' in config:
                self.container.output_uri = config['workspace']
            self.progressWidget.set_range(0, 0)    
        elif self.container.mode == BiRunnerContainer.MODE_EXP:
            self.container.inputs = self.inputExperimentWidget.inputs() 
            self.container.output_uri = self.inputExperimentWidget.output() 
            self.progressWidget.set_range(0, 100)
    
        self.container.parameters = self.paramWidget.parameters()

        print('run clicked with data:')
        print('inputs:', self.container.inputs)
        print('parameters:', self.container.parameters)
        print('output:', self.container.output_uri)
        
        self.container.emit(BiRunnerStates.RunProcess) 

    def progressValue(self, progress: int):
        self.progressWidget.setProgress(progress)
        if (progress > 0):
            self.progressWidget.set_range(0, 100)

    def progressMessage(self, message: str):
        self.progressWidget.setMessage(message)

    def get_widget(self):
        return self.widget                
