from PySide2.QtCore import Signal, QObject, QThread

from bioimagepy.core.utils import ProgressObserver
from bioimagepy.process import Process
from bioimagepy.runner import Runner

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.runner.states import BiRunnerStates
from bioimageapp.runner.containers import BiRunnerContainer

class BiRunnerModel(BiModel):
    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self.observer = None
        self._object_name = 'BiProcessEditorModel'
        self.container = container
        self.container.register(self)  
        self.thread = BiRunnerThread()

    def update(self, action: BiAction):
        if action.state == BiRunnerStates.RunProcess:
            self.runProcess()
        if action.state == BiRunnerStates.ProcessUriChanged:
            self.getProcess()    

    def runProcess(self):
        print('in model, run with:') 
        print('inputs:', self.container.inputs)
        print('parameters:', self.container.parameters)
        print('output uri', self.container.output_uri)
        if self.container.mode == BiRunnerContainer.MODE_FILE:
            self.run_file()
        elif self.container.mode == BiRunnerContainer.MODE_REP:
            self.run_rep() 

    def run_file(self):
        self.thread.observer = self.observer
        self.thread.mode = BiRunnerContainer.MODE_FILE
        self.thread.process_info = self.container.process_info
        self.thread.inputs = self.container.inputs
        self.thread.parameters = self.container.parameters
        self.thread.output_uri = self.container.output_uri
        self.thread.start()

    def run_rep(self):
        runner = Runner(self.container.process_info)
        for input in self.container.inputs:
            runner.add_inputs(input['name'], input['uri'], input['filter'])
        runner.set_parameters(*self.container.parameters)
        runner.set_output(self.container.output_uri)
        runner.exec()  

    def getProcess(self):
        process = Process(self.container.process_uri)
        self.container.process_info = process
        self.container.emit(BiRunnerStates.ProcessInfoLoaded)


class BiRunnerThread(QThread):
    def __init__(self):
        super().__init__() 
        self.observer = None
        self.process_info = None
        self.inputs = []
        self.parameters = []
        self.output_uri = ''
        self.mode = ''

    def run(self):
        if self.mode == BiRunnerContainer.MODE_FILE:
            runner = Runner(self.process_info)
            runner.addObserver(self.observer)
            for input in self.inputs:
                runner.add_input(input['name'], input['uri'])
            runner.set_parameters(*self.parameters)
            runner.set_output(self.output_uri)
            runner.exec()   
        elif self.mode == BiRunnerContainer.MODE_REP:  
            print('run dir mode')   
        elif self.mode == BiRunnerContainer.MODE_EXP:  
            print('run exp mode')                   