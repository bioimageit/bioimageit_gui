from qtpy.QtCore import QObject, Signal


class BiGuiProgressObserver(QObject):
    progressSignal = Signal(int)
    messageSignal = Signal(str)

    def __init__(self, debug=True):
        super().__init__()
        self.jobs_id = []
        self.debug = debug

    def new_job(self, job_id: int):
        """Add a new job id

        Parameters
        ----------
        job_id: int
            unique ID of the new job

        """
        self.jobs_id.append(job_id)    

    def notify(self, message: str, job_id: int = 0):
        pass 

    def notify_warning(self, message: str, job_id: int = 0):
        pass      

    def notify_error(self, message: str, job_id: int = 0):
        pass
            
    def notify_progress(self, progress: int, message: int = '', job_id: int = 0):
        self.progressSignal.emit(progress) 
        self.messageSignal.emit(message)                
