from bioimageit_core.core.utils import ProgressObserver
from qtpy.QtCore import QObject, Signal


class BiGuiProgressObserver(QObject, ProgressObserver):
    progressSignal = Signal(int)
    messageSignal = Signal(str)

    def __init__(self):
        super().__init__()

    def notify(self, data: dict):

        if 'progress' in data:
            self.progressSignal.emit(data['progress'])
            #print('progress:', data['progress'])
        if 'message' in data:
            self.messageSignal.emit(data['message'])
            #print('message:', data['message'])   
        if 'warning' in data:
            self.messageSignal.emit('warning:' + data['warning'])
            #print('warning:', data['warning']) 
        if 'error' in data:
            self.messageSignal.emit('error:' + data['warning'])
            #print('error:', data['error'])          