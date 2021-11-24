import os
import subprocess
from qtpy.QtCore import QThread
from bioimageit_core.config import Config, ConfigAccess

from bioimageit_gui.core.framework import BiModel, BiAction

from ._containers import BiUpdateContainer, BiConfigContainer
from ._states import BiUpdateStates, BiConfigStates


class BiUpdateModel(BiModel):  
    def __init__(self, container: BiUpdateContainer):
        super().__init__()
        self._object_name = 'BiUpdateModel'
        self.container = container
        self.container.register(self)

        self.thread = BiUpdateThread()
        self.thread.finished.connect(self.update_finished)

    def update_finished(self):
        self.container.emit(BiUpdateStates.UpdateFinished)

    def update(self, action: BiAction):
        if action.state == BiUpdateStates.UpdateClicked:
            print('Run here the update code')
            self.thread.update_bioimageit = self.container.update_bioimageit
            self.thread.update_toolboxes = self.container.update_toolboxes
            self.thread.start()
            return   


class BiUpdateThread(QThread):
    def __init__(self):
        super().__init__() 
        self.update_bioimageit = False
        self.update_toolboxes = False   

    def run(self):  
        install_dir = ConfigAccess.instance().get('install_dir')
        conda_dir = ConfigAccess.instance().get('runner')['conda_dir']

        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update.sh')
        p1 = subprocess.run(f'chmod +x {script}', shell=True, capture_output=True)
        print( 'exit status:', p1.returncode )
        print( 'stdout:', p1.stdout.decode() )
        print( 'stderr:', p1.stderr.decode() )
        p = subprocess.run([script, install_dir, conda_dir], shell=True, capture_output=True)           
        print( 'exit status:', p.returncode )
        print( 'stdout:', p.stdout.decode() )
        print( 'stderr:', p.stderr.decode() )

class BiConfigModel(BiModel):  
    def __init__(self, container: BiConfigContainer):
        super().__init__()
        self._object_name = 'BiConfigModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiConfigStates.ConfigEdited:
            # save the config    
            config_obj = Config()
            config_obj.config = self.container.config
            config_obj.config_file = ConfigAccess.instance().config_file
            config_obj.save()
            # change the access pointer
            ConfigAccess.instance().config = config_obj
            self.container.emit(BiConfigStates.ConfigSaved)
            return
