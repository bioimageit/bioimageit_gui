import os

from bioimageit_gui.core.framework import BiContainer, BiObject


class BiBrowserFileInfo(BiObject):     
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
        self.openExperimentPath = ''
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
