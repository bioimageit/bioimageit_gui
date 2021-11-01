from bioimageit_gui.core.framework import BiContainer
from bioimageit_gui.runner.states import BiRunnerStates


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
        self.inputs = []
        self.parameters = []
        self.output_uri = ''
        self.progress = 0
        self.progress_message = ''
        self.genarated_outputs = [] 
        self.clicked_view_uri = ''
        self.clicked_view_format = ''

    def set_progress(self, progress: int, message: str):
        self.progress = progress
        self.progress_message = message
