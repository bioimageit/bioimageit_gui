import os
from qtpy.QtCore import QDir

from bioimageit_framework.framework import BiContainer


class BiBrowserFileInfo:     
    def __init__(self, fileName: str = '', path: str = '', name: str = '',
                 dtype: str = '', date: str = ''):
        super().__init__()
        self.fileName = fileName
        self.path = path # without file name 
        self.name = name
        self.type = dtype
        self.date = date

    def filePath(self) -> str:
        return os.path.join(self.path, self.fileName)  


class BiBrowserContainer(BiContainer):
    REFRESH = 'refresh'
    OPEN_EXP = 'open_experiment'
    CLICKED_ROW = 'clicked_row'
    DOUBLE_CLICKED_ROW = 'double_clicked_row'
    RELOADED = 'reloaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiBrowserContainer'

        # data
        self.currentPath = ''
        self.files = list()
        self.doubleClickedRow = -1
        self.clickedRow = -1
        self.historyPaths = list()
        self.posHistory = 0
        self.experiment_uri = ''
        self.bookmarkPath = ''

    def clickedFileInfo(self):
        return self.files[self.clickedRow]  

    def doubleClickedFile(self):
        return self.files[self.doubleClickedRow].filePath()

    def addHistory(self, path: str):
        self.historyPaths.append(path)

    def moveToPrevious(self):
        self.posHistory -= 1
        if self.posHistory < 0 :
            self.posHistory = 0
        self.currentPath = self.historyPaths[self.posHistory]

    def moveToNext(self):
        self.posHistory += 1
        if self.posHistory >= len(self.historyPaths):
            self.posHistory = len(self.historyPaths) - 1
        self.currentPath = self.historyPaths[self.posHistory]

    def setCurrentPath(self, path: str):
        self.currentPath = path
        if self.posHistory <= len(self.historyPaths):
            for i in range(len(self.historyPaths), self.posHistory):
                self.historyPaths.pop(i)
        self.addHistory(path)
        self.posHistory = len(self.historyPaths) - 1   

    def action_previous(self, action):
        self.moveToPrevious()
        self._notify(BiBrowserContainer.REFRESH)

    def action_next(self, action):
        self.moveToNext()
        self._notify(BiBrowserContainer.REFRESH)

    def action_up(self, action):
        dir = QDir(self.currentPath)
        dir.cdUp()
        upPath = dir.absolutePath()
        self.setCurrentPath(upPath)
        self._notify(BiBrowserContainer.REFRESH)

    def action_change_dir(self, action, path):
        self.setCurrentPath(path)
        self._notify(BiBrowserContainer.REFRESH)

    def action_open_experiment(self, action, experiment_uri):
        self.experiment_uri = experiment_uri
        self._notify(BiBrowserContainer.OPEN_EXP)
        
    def action_clicked_row(self, action, row):
        self.clickedRow = row
        self._notify(BiBrowserContainer.CLICKED_ROW)   

    def action_double_clicked_row(self, action, row):
        self.doubleClickedRow = row
        if self.files[row].type == 'experiment':
            self.experiment_uri = os.path.join(self.files[row].filePath(), 'experiment.md.json')
            self._notify(BiBrowserContainer.OPEN_EXP)
        elif self.files[row].type == 'dir':   
            self.setCurrentPath(self.files[row].filePath())
            self._notify(BiBrowserContainer.REFRESH)       

    def action_reload(self, action, files):
        self.files = files
        self._notify(BiBrowserContainer.RELOADED)

    def init(self, workspace_path):
        self.currentPath = workspace_path
        self._notify(BiBrowserContainer.REFRESH)    
   