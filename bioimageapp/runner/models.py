from PySide2.QtCore import Signal, QObject, QThread

from bioimagepy.process import Process
from bioimagepy.runner import Runner

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.runner.states import BiRunnerStates
from bioimageapp.runner.containers import BiRunnerContainer


class BiRunnerModel(BiModel):
    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self._object_name = 'BiProcessEditorModel'
        self.container = container
        self.container.register(self)  

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
        runner = Runner(self.container.process_info)
        for input in self.container.inputs:
            runner.add_input(input['name'], input['uri'])
        runner.set_parameters(*self.container.parameters)
        # todo set to tmp/
        runner.set_output(self.container.output_uri)
        runner.exec() 

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