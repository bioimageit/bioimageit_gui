import os
import subprocess
from bioimageit_framework.framework.framework import BiConnectome
from qtpy.QtCore import QThread
from bioimageit_core.core.toolboxes import Toolboxes
from bioimageit_core import Config, ConfigAccess

from bioimageit_framework.framework import BiActuator

from ._containers import BiUpdateContainer, BiConfigContainer


class BiUpdateModel(BiActuator):  
    def __init__(self, container: BiUpdateContainer):
        super().__init__()
        self._object_name = 'BiUpdateModel'
        self.container = container
        BiConnectome.connect(container, self)

        self.thread = BiUpdateThread()
        self.thread.finished.connect(self.update_finished)

    def update_finished(self):
        self.container.action_update_finished()

    def callback_update_clicked(self, emitter):
        print('Run here the update code')
        self.thread.update_bioimageit = self.container.update_bioimageit
        self.thread.update_toolboxes = self.container.update_toolboxes
        self.thread.start()


class BiUpdateThread(QThread):
    def __init__(self):
        super().__init__() 
        self.update_bioimageit = False
        self.update_toolboxes = False   

    def run(self):  
        if self.update_bioimageit:
            self.update_app()
        if self.update_toolboxes:
            self.update_tools()    

    def update_app(self):    
        install_dir = ConfigAccess.instance().get('install_dir')
        conda_dir = ConfigAccess.instance().get('runner')['conda_dir']

        if os.name == 'nt' :
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update.bat')
            p = subprocess.run(f'{script} {install_dir} {conda_dir}', shell=True, capture_output=True)           
            print( 'exit status:', p.returncode )
            print( 'stdout:', p.stdout.decode() )
            print( 'stderr:', p.stderr.decode() )
        else:    
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update.sh')
            p1 = subprocess.run(f'chmod +x {script}', shell=True, capture_output=True)
            print( 'exit status:', p1.returncode )
            print( 'stdout:', p1.stdout.decode() )
            print( 'stderr:', p1.stderr.decode() )
            p = subprocess.run(f'{script} {install_dir} {conda_dir}', shell=True, capture_output=True)           
            print( 'exit status:', p.returncode )
            print( 'stdout:', p.stdout.decode() )
            print( 'stderr:', p.stderr.decode() )

    def update_tools(self):
        install_dir = ConfigAccess.instance().get('install_dir')
        conda_dir = ConfigAccess.instance().get('runner')['conda_dir']
        if os.name == 'nt' :
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update_tools.bat')
            p = subprocess.run(f'{script} {install_dir} {conda_dir}', shell=True, capture_output=True)           
            print( 'exit status:', p.returncode )
            print( 'stdout:', p.stdout.decode() )
            print( 'stderr:', p.stderr.decode() )
        else:
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update_tools.sh')
            p1 = subprocess.run(f'chmod +x {script}', shell=True, capture_output=True)
            print( 'exit status:', p1.returncode )
            print( 'stdout:', p1.stdout.decode() )
            print( 'stderr:', p1.stderr.decode() )
            p = subprocess.run(f'{script} {install_dir}', shell=True, capture_output=True)           
            print( 'exit status:', p.returncode )
            print( 'stdout:', p.stdout.decode() )
            print( 'stderr:', p.stderr.decode() )   
        # run toolboxes build
        builder = Toolboxes()
        builder.build()             

class BiConfigModel(BiActuator):  
    def __init__(self, container: BiConfigContainer):
        super().__init__()
        self._object_name = 'BiConfigModel'
        self.container = container
        BiConnectome.connect(container, self)

    def callback_config_edited(self, emitter):
        # save the config    
        config_obj = Config(ConfigAccess.instance().config_file)
        config_obj.config = self.container.config
        config_obj.save()
        # change the access pointer
        ConfigAccess.instance().config = config_obj
        self.container.action_config_saved(None)
        return
