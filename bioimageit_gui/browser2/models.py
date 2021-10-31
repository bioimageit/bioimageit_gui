import os
import json

from PySide2.QtCore import QDir

from bioimageit_core.experiment import Experiment
from bioimageit_core.metadata.run import Run
from bioimageit_core.dataset import RawDataSet, ProcessedDataSet, RawData

from bioimageit_gui.core.framework import BiModel, BiAction
from bioimageit_gui.browser2.states import BiBrowser2States
from bioimageit_gui.browser2.containers import (BiBrowser2Container,
                                               BiBrowser2FileInfo)


class BiBrowser2Model(BiModel):
    def __init__(self, container: BiBrowser2Container):
        super().__init__()
        self._object_name = 'BiBrowser2Model'
        self.container = container
        self.container.register(self)
        self.files = list

    def update(self, action: BiAction):
        if action.state == BiBrowser2States.DirectoryModified or \
                action.state == BiBrowser2States.RefreshClicked:
            self.loadFiles()
            return
    
        if action.state == BiBrowser2States.ItemDoubleClicked:
            print('model in double cliekd update')
            row = self.container.doubleClickedRow
            dcFile = self.container.files[row]
            self.browse(dcFile)
            return   

        if action.state == BiBrowser2States.PreviousClicked:
            self.container.moveToPrevious()
            self.container.emit(BiBrowser2States.DirectoryModified)
            return

        if action.state == BiBrowser2States.NextClicked:
            self.container.moveToNext()
            self.container.emit(BiBrowser2States.DirectoryModified)
            return

        if action.state == BiBrowser2States.UpClicked:
            dir = QDir(self.container.currentPath)
            dir.cdUp()
            upPath = dir.absolutePath()
            self.container.setCurrentPath(upPath)
            self.container.emit(BiBrowser2States.DirectoryModified)
            return


    def browse(self, fileInfo: BiBrowser2FileInfo):
        experiment_file = os.path.join(fileInfo.path, fileInfo.fileName,
                                      'experiment.md.json')
        if os.path.isfile(experiment_file):
            self.container.openExperimentPath = os.path.join(fileInfo.path,
                                                             fileInfo.fileName)
            self.container.emit(BiBrowser2States.OpenExperiment)
        elif fileInfo.type == "dir":    
            self.container.setCurrentPath(os.path.join(fileInfo.path,
                                                       fileInfo.fileName))
            self.container.emit(BiBrowser2States.DirectoryModified)

    def loadFiles(self):
        dir = QDir(self.container.currentPath)
        files = dir.entryInfoList()
        self.files = []

        for i in range(len(files)):
            if files[i].fileName() != "." and files[i].fileName() != "..":
                if files[i].isDir():
                    experiment_file = os.path.join(files[i].absoluteFilePath(),
                                                   'experiment.md.json')
                    if os.path.isfile(experiment_file):
                        fileInfo = BiBrowser2FileInfo(files[i].fileName(),
                                           files[i].path(),
                                           files[i].fileName(),
                                           'experiment',
                                           files[i].lastModified().toString(
                                               "yyyy-MM-dd"))
                    else:    
                        fileInfo = BiBrowser2FileInfo(files[i].fileName(),
                                           files[i].path(),
                                           files[i].fileName(),
                                           'dir',
                                           files[i].lastModified().toString(
                                               "yyyy-MM-dd"))

                    self.files.append(fileInfo)

                elif files[i].fileName().endswith("experiment.md.json"):
                    experiment = Experiment(files[i].absoluteFilePath())

                    fileInfo = BiBrowser2FileInfo(files[i].fileName(),
                                            files[i].path(),
                                            experiment.metadata.name,
                                            "experiment",
                                            experiment.metadata.date)
                    self.files.append(fileInfo)
                    del experiment
        
                elif files[i].fileName().endswith("run.md.json"):
                    run = Run(files[i].absoluteFilePath())
    
                    fileInfo = BiBrowser2FileInfo(files[i].fileName(),
                                            files[i].path(),
                                            run.metadata.process_name,
                                            "run",
                                            files[i].lastModified().toString(
                                                "yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del run
                
                elif files[i].fileName().endswith("rawdataset.md.json"):
                    rawDataSet = RawDataSet(files[i].absoluteFilePath())

                    fileInfo = BiBrowser2FileInfo(files[i].fileName(),
                                            files[i].path(),
                                            rawDataSet.metadata.name,
                                            "rawdataset",
                                            files[i].lastModified().toString(
                                                "yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del rawDataSet
        
                elif files[i].fileName().endswith("processeddataset.md.json"):
                    processedDataSet = ProcessedDataSet(
                        files[i].absoluteFilePath())

                    fileInfo = BiBrowser2FileInfo(files[i].fileName(),
                                            files[i].path(),
                                            processedDataSet.metadata.name,
                                            "processeddataset",
                                            files[i].lastModified().toString(
                                                "yyyy-MM-dd"))
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

                    fileInfo = BiBrowser2FileInfo(files[i].fileName(),
                                            files[i].path(),
                                            name,
                                            type + "data",
                                            files[i].lastModified().toString(
                                                "yyyy-MM-dd"))
                    self.files.append(fileInfo)

        self.container.files = self.files
        self.container.emit(BiBrowser2States.FilesInfoLoaded)
