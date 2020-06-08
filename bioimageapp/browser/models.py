import os
import json

from PySide2.QtCore import QObject, QDir

from bioimagepy.process import ProcessAccess
from bioimagepy.experiment import Experiment
from bioimagepy.metadata.run import Run
from bioimagepy.dataset import RawDataSet, ProcessedDataSet, RawData

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.browser.states import BiBrowserStates
from bioimageapp.browser.settings import BiBookmarks
from bioimageapp.browser.containers import BiBrowserContainer, BiBrowserFileInfo


class BiBrowserModel(BiModel):
    def __init__(self, container: BiBrowserContainer, useExperimentProcess: bool = False):
        super().__init__()
        self._object_name = 'BiBrowserModel'
        self._useExperimentProcess = useExperimentProcess
        self.container = container
        self.container.register(self)
        self.files = list

    def update(self, action: BiAction):
        if action.state == BiBrowserStates.DirectoryModified or action.state == BiBrowserStates.RefreshClicked:
            self.loadFiles()
            return
    
        if action.state == BiBrowserStates.ItemDoubleClicked:
            
            row = self.container.doubleClickedRow
            dcFile = self.container.files[row]
            
            if dcFile.type == "dir":
                self.container.setCurrentPath(os.path.join(dcFile.path,dcFile.fileName))
                self.container.emit(BiBrowserStates.DirectoryModified)
            elif dcFile.type == "experiment":
                self.container.openExperimentPath = os.path.join(dcFile.path,dcFile.fileName)
                self.container.emit(BiBrowserStates.OpenExperiment)
            else:
                self.container.emit(BiBrowserStates.OpenJson) 

        if action.state == BiBrowserStates.PreviousClicked:
            self.container.moveToPrevious()
            self.container.emit(BiBrowserStates.DirectoryModified)
            return

        if action.state == BiBrowserStates.NextClicked:
            self.container.moveToNext()
            self.container.emit(BiBrowserStates.DirectoryModified)
            return

        if action.state == BiBrowserStates.UpClicked:
            dir = QDir(self.container.currentPath)
            dir.cdUp()
            upPath = dir.absolutePath()
            self.container.setCurrentPath(upPath)
            self.container.emit(BiBrowserStates.DirectoryModified)
            return

        if action.state == BiBrowserStates.BookmarkClicked:
            dir = QDir(self.container.currentPath)
            self.container.bookmarks.set(dir.dirName(), self.container.currentPath)
            self.container.bookmarks.write()
            self.container.emit(BiBrowserStates.BookmarksModified)
            return

    def loadFiles(self):
        dir = QDir(self.container.currentPath)
        files = dir.entryInfoList()
        self.files = []

        for i in range(len(files)):
            if files[i].fileName() != "." and files[i].fileName() != "..":
                if files[i].isDir():
                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                           files[i].path(),
                                           files[i].fileName(),
                                           "dir",
                                           files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)

                elif files[i].fileName().endswith("experiment.md.json"):
                    experiment = Experiment(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            experiment.metadata.name,
                                            "experiment",
                                            experiment.metadata.date)
                    self.files.append(fileInfo)
                    del experiment
        
                elif files[i].fileName().endswith("run.md.json"):
                    run = Run(files[i].absoluteFilePath())
    
                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            run.metadata.process_name,
                                            "run",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del run
                
                elif files[i].fileName().endswith("rawdataset.md.json"):
                    rawDataSet = RawDataSet(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            rawDataSet.metadata.name,
                                            "rawdataset",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del rawDataSet
        
                elif files[i].fileName().endswith("processeddataset.md.json"):
                    processedDataSet = ProcessedDataSet(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            processedDataSet.metadata.name,
                                            "processeddataset",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del processedDataSet
        
                elif files[i].fileName().endswith(".md.json"):
                    # test type of file raw/processed
                    metadata = None 
                    if os.path.getsize(files[i].absoluteFilePath()) > 0:
                        with open(files[i].absoluteFilePath()) as json_file:  
                            metadata = json.load(json_file)

                    name = ''
                    if 'common' in metadata:
                        if 'name' in metadata['common']:
                            name = metadata['common']['name'] 

                    type = ''
                    if 'origin' in metadata:
                        if 'type' in metadata['origin']:
                            type = metadata['origin']['type']               

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            name,
                                            type + "data",
                                            files[i].lastModified().toString("yyyy-MM-dd"))
                    self.files.append(fileInfo)

        self.container.files = self.files
        self.container.emit(BiBrowserStates.FilesInfoLoaded)


    def loadBookmarks(self, file: str):
        self.container.bookmarks = BiBookmarks(file)
