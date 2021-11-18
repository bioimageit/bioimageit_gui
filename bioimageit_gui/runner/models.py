from qtpy.QtCore import Signal, QObject, QThread

from bioimageit_core.process import Process
from bioimageit_core.runner import Runner
from bioimageit_core.pipeline import PipelineRunner

from bioimageit_gui.core.framework import BiModel, BiAction
from bioimageit_gui.runner.states import BiRunnerStates
from bioimageit_gui.runner.containers import BiRunnerContainer


class BiRunnerModel(BiModel):
    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self.observer = None
        self._object_name = 'BiProcessEditorModel'
        self.container = container
        self.container.register(self)  
        self.thread = BiRunnerThread()
        self.thread.finished.connect(self.copyOutputs)

    def update(self, action: BiAction):
        if action.state == BiRunnerStates.RunProcess:
            self.runProcess()
        if action.state == BiRunnerStates.ProcessUriChanged:
            self.getProcess()    

    def copyOutputs(self):
        self.container.genarated_outputs = self.thread.output_uris
        self.container.emit(BiRunnerStates.RunFinished)

    def runProcess(self):
        print('in model, run with:') 
        print('inputs:', self.container.inputs)
        print('parameters:', self.container.parameters)
        print('output uri', self.container.output_uri)
        if self.container.mode == BiRunnerContainer.MODE_FILE:
            self.run_file()
        elif self.container.mode == BiRunnerContainer.MODE_REP:
            self.run_rep() 
        elif self.container.mode == BiRunnerContainer.MODE_EXP:  
            self.run_exp()  

    def run_file(self):
        self.thread.observer = self.observer
        self.thread.mode = BiRunnerContainer.MODE_FILE
        self.thread.process_info = self.container.process_info
        self.thread.inputs = self.container.inputs
        self.thread.parameters = self.container.parameters
        self.thread.output_uri = self.container.output_uri
        self.thread.start()

    def run_rep(self):
        self.thread.observer = self.observer
        self.thread.mode = BiRunnerContainer.MODE_REP
        self.thread.process_info = self.container.process_info
        self.thread.inputs = self.container.inputs
        self.thread.parameters = self.container.parameters
        self.thread.output_uri = self.container.output_uri
        self.thread.start() 

    def run_exp(self):
        self.thread.observer = self.observer
        self.thread.experiment = self.container.experiment
        self.thread.mode = BiRunnerContainer.MODE_EXP
        self.thread.process_info = self.container.process_info
        self.thread.inputs = self.container.inputs
        print('inputs = ', self.container.inputs)
        self.thread.parameters = self.container.parameters
        self.thread.output_uri = self.container.output_uri
        self.thread.start()     

    def getProcess(self):
        process = Process(self.container.process_uri)
        self.container.process_info = process
        self.container.emit(BiRunnerStates.ProcessInfoLoaded)


class BiRunnerThread(QThread):
    def __init__(self):
        super().__init__() 
        self.observer = None
        self.experiment = None
        self.process_info = None
        self.inputs = []
        self.parameters = []
        self.output_uri = ''
        self.mode = ''
        self.output_uris = []

    def run(self):
        self.output_uris = []
        if self.mode == BiRunnerContainer.MODE_FILE:
            runner = Runner(self.process_info)
            runner.add_observer(self.observer)
            for input_ in self.inputs:
                runner.add_input(input_['name'], input_['uri'])
            runner.set_parameters(*self.parameters)
            runner.set_output(self.output_uri)
            runner.exec()   
            self.output_uris = runner.output_uris
        elif self.mode == BiRunnerContainer.MODE_REP:  
            runner = Runner(self.process_info)
            runner.add_observer(self.observer)
            for input in self.inputs: 
                runner.add_inputs(input['name'], input['uri'], input['filter'])
            runner.set_parameters(*self.parameters)
            runner.set_output(self.output_uri)
            runner.exec()  
            #self.output_uris = runner.output_uris
        elif self.mode == BiRunnerContainer.MODE_EXP:  
            process = PipelineRunner(self.experiment, self.process_info)
            process.add_observer(self.observer)
            process.set_dataset_name(self.output_uri)
            process.set_parameters(*self.parameters)
            for input_ in self.inputs:
                process.add_input(input_['name'], input_['dataset'],
                                  input_['filter'], input_['origin_output_name'])
            process.exec()                  