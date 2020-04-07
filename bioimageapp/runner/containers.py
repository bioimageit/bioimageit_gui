
from bioimageapp.core.framework import BiContainer
from bioimageapp.runner.states import BiRunnerStates


class BiRunnerContainer(BiContainer):
    MODE_FILE = 'file'
    MODE_REP = 'rep'
    MODE_EXP = 'exp'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRunnerContainer'

        # states
        self.states = BiRunnerStates()

        # data
        self.process_uri = ''
        self.mode = BiRunnerContainer.MODE_FILE # file, rep, exp 
        self.process_info = None
        self.inputs_list = []
        self.input_exp = None
        self.parameters = []
        self.output_dataset = ''
        self.progress = 0
        self.progress_message = '' 

    def set_progress(self, progress: int, message: str):
        self.progress = progress
        self.progress_message = message