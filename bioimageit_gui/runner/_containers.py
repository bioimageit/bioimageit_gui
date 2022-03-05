from bioimageit_framework.framework import BiContainer


class BiRunnerContainer(BiContainer):
    ProcessUriChanged = "process_uri_changed"
    ProcessInfoLoaded = "process_info_loaded"
    RunProcess = "run_process"
    RunFinished = "run_finished"
    ClickedView = "clicked_view"
    ModeChanged = "mode_changed"

    MODE_FILE = 'file'
    MODE_EXP = 'exp'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRunnerContainer'

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

    def action_run_finished(self, origin, output_uris):
        self.genarated_outputs = output_uris
        self._notify(BiRunnerContainer.RunFinished)    

    def action_process_info_loaded(self, action, process):
        self.process_info = process
        self._notify(BiRunnerContainer.ProcessInfoLoaded)

    def action_mode_changed(self, action, mode):
        self.mode = mode
        self._notify(BiRunnerContainer.ModeChanged)    

    def action_clicked_view(self, action, uri, format_):
        self.clicked_view_uri = uri
        self.clicked_view_format = format_
        self._notify(BiRunnerContainer.ClickedView)    

    def action_run_process(self, action):
        self._notify(BiRunnerContainer.RunProcess)
      
    def action_process_uri_changed(self, action, xml_file):
        self.process_uri = xml_file
        self._notify(BiRunnerContainer.ProcessUriChanged)
