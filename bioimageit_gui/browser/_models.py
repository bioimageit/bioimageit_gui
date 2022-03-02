import os
import json

from qtpy.QtCore import QDir

from bioimageit_core.api import APIAccess
from bioimageit_framework.framework import BiActuator

from ._containers import BiBrowserFileInfo


class BiBrowserModel(BiActuator):
    OPEN_EXP = 'open_experiment'
    CHANGE_DIR = 'change_dir'
    RELOAD = 'reload'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiBrowserModel'
        self.files = list

    def callback_browse(self, emitter):
        row = emitter.doubleClickedRow
        dcFile = emitter.files[row]
        self.browse(dcFile)

    def browse(self, fileInfo: BiBrowserFileInfo):
        experiment_file = os.path.join(fileInfo.path, fileInfo.fileName,
                                      'experiment.md.json')
        if os.path.isfile(experiment_file):
            self._emit(BiBrowserModel.OPEN_EXP, os.path.join(fileInfo.path,
                                                             fileInfo.fileName,
                                                             "experiment.md.json"))
        elif fileInfo.type == "dir":  
            self._emit(BiBrowserModel.CHANGE_DIR, os.path.join(fileInfo.path,
                                                       fileInfo.fileName))  
            
    def callback_refresh(self, emitter):
        dir = QDir(emitter.currentPath)
        files = dir.entryInfoList()
        self.files = []

        for i in range(len(files)):
            if files[i].fileName() != "." and files[i].fileName() != "..":
                if files[i].isDir():
                    experiment_file = os.path.join(files[i].absoluteFilePath(),
                                                   'experiment.md.json')
                    if os.path.isfile(experiment_file):
                        fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                           files[i].path(),
                                           files[i].fileName(),
                                           'experiment',
                                           files[i].lastModified().toString(
                                               "yyyy-MM-dd"))
                    else:    
                        fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                           files[i].path(),
                                           files[i].fileName(),
                                           'dir',
                                           files[i].lastModified().toString(
                                               "yyyy-MM-dd"))

                    self.files.append(fileInfo)

                elif files[i].fileName().endswith("experiment.md.json"):
                    experiment = APIAccess.instance().get_experiment(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            experiment.name,
                                            "experiment",
                                            experiment.date)
                    self.files.append(fileInfo)
                    del experiment
        
                elif files[i].fileName().endswith("run.md.json"):
                    run = APIAccess.instance().get_run(files[i].absoluteFilePath())
    
                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            run.process_name,
                                            "run",
                                            files[i].lastModified().toString(
                                                "yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del run
                
                elif files[i].fileName().endswith("raw_dataset.md.json"):
                    rawDataSet = APIAccess.instance().get_dataset(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            rawDataSet.name,
                                            "rawdataset",
                                            files[i].lastModified().toString(
                                                "yyyy-MM-dd"))
                    self.files.append(fileInfo)
                    del rawDataSet
        
                elif files[i].fileName().endswith("processeddataset.md.json"):
                    processedDataSet = APIAccess.instance().get_dataset(files[i].absoluteFilePath())

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
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

                    fileInfo = BiBrowserFileInfo(files[i].fileName(),
                                            files[i].path(),
                                            name,
                                            type + "data",
                                            files[i].lastModified().toString(
                                                "yyyy-MM-dd"))
                    self.files.append(fileInfo)
        self._emit(BiBrowserModel.RELOAD, tuple(self.files))
