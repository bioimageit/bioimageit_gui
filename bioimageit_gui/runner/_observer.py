from bioimageit_core.core.observer import Observer
from qtpy.QtCore import QObject, Signal


class BiGuiProgressObserver(QObject, Observer):
    progressSignal = Signal(int)
    messageSignal = Signal(str)

    def __init__(self):
        super().__init__()

    def notify(self, message: str, job_id: int = 0):
        if job_id > 0:
            self.messageSignal.emit(f"job{job_id}: {message}")
        else:
            self.messageSignal.emit(message)   

    def notify_warning(self, message: str, job_id: int = 0):
        if job_id > 0:
            self.messageSignal.emit(f"job{job_id} WARNING: {message}")
        else:
            self.messageSignal.emit(f"WARNING: {message}")         

    def notify_error(self, message: str, job_id: int = 0):
        if job_id > 0:
            self.messageSignal.emit(f"job{job_id} ERROR: {message}")
        else:
            self.messageSignal.emit(f"ERROR: {message}") 
            
    def notify_progress(self, progress: int, message: int = '', job_id: int = 0):
        self.progressSignal.emit(progress) 
        self.messageSignal.emit(message)                
