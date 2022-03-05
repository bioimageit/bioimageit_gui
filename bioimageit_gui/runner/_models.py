import os

from bioimageit_formats import FormatsAccess
from qtpy.QtCore import QThread

from bioimageit_core.api import APIAccess
from bioimageit_core.containers import Job

from bioimageit_framework.framework import BiActuator, BiConnectome
from ._containers import BiRunnerContainer


class BiRunnerModel(BiActuator):
    def __init__(self, container: BiRunnerContainer):
        super().__init__()
        self.observer = None
        self._object_name = 'BiRunnerModel'
        self.container = container
        BiConnectome.connect(self.container, self)
        self.thread = BiRunnerThread()
        self.thread.finished.connect(self.copyOutputs)

    def callback_run_process(self, emitter):
        self.runProcess()

    def callback_process_uri_changed(self, emitter):
        self.getProcess()                

    def copyOutputs(self):
        self.container.action_run_finished(None, [self.thread.output_uris])

    def runProcess(self):
        print('in model, run with:') 
        print('inputs:', self.container.inputs)
        print('parameters:', self.container.parameters)
        print('output uri', self.container.output_uri)
        if self.container.mode == BiRunnerContainer.MODE_FILE:
            self.run_file()
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
        process = APIAccess.instance().get_tool_from_uri(self.container.process_uri)
        self.container.action_process_info_loaded(None, process)


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
            params = {}
            for input_ in self.inputs:
                params[input_['name']] = input_['uri']
            print('outputs info:', self.process_info.outputs)    
            for output in self.process_info.outputs:
                params[output.name] = os.path.join(self.output_uri, output.name + '.' + FormatsAccess.instance().get(output.type).extension)    
            for i in range(0, len(self.parameters), 2):
                params[self.parameters[i]] = self.parameters[i+1]
            APIAccess.instance().exec(self.process_info, **params)
        elif self.mode == BiRunnerContainer.MODE_EXP:  
            job = Job()
            job.experiment = self.experiment
            job.tool = self.process_info
            for input_ in self.inputs:
                job.set_input(input_['name'], input_['dataset'],
                              input_['filter'], input_['origin_output_name'])
            for i in range(0, len(self.parameters), 2):
                job.set_param(self.parameters[i], self.parameters[i+1] )               
            job.set_output_dataset_name(self.output_uri)
            APIAccess.instance().run(job)
