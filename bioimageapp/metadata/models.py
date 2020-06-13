import os

from bioimagepy.data import RawData, ProcessedData

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.metadata.states import (BiRawDataStates, BiProcessedDataStates, 
                                         BiMetadataExperimentStates)
from bioimageapp.metadata.containers import (BiRawDataContainer, BiProcessedDataContainer, 
                                            BiMetadataExperimentContainer)


class BiRawDataModel(BiModel):  
    def __init__(self, container: BiRawDataContainer):
        super().__init__()
        self._object_name = 'BiRawDataModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiRawDataStates.URIChanged:
            self.container.rawdata = RawData(self.container.md_uri)
            self.container.emit(BiRawDataStates.Loaded)
            return

        if action.state == BiRawDataStates.SaveClicked:
            self.container.rawdata.write()
            self.container.emit(BiRawDataStates.Saved)
            return

class BiProcessedDataModel(BiModel):  
    def __init__(self, container: BiProcessedDataContainer):
        super().__init__()
        self._object_name = 'BiProcessedDataModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiProcessedDataStates.URIChanged:
            self.container.processeddata = ProcessedData(self.container.md_uri)
            self.container.emit(BiProcessedDataStates.Loaded)
            return    

class BiMetadataExperimentModel(BiModel):  
    def __init__(self, container: BiMetadataExperimentContainer):
        super().__init__()
        self._object_name = 'BiMetadataExperimentModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiMetadataExperimentStates.SaveClicked:
            self.container.experiment.write()
            self.container.emit(BiMetadataExperimentStates.Saved)
            return