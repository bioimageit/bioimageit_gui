import os

from bioimageit_core.api import APIAccess

from bioimageit_gui.core.framework import BiModel, BiAction
from bioimageit_gui.metadata.states import (BiRawDataStates,
                                            BiProcessedDataStates,
                                            BiMetadataExperimentStates,
                                            BiRunStates)
from bioimageit_gui.metadata.containers import (BiRawDataContainer,
                                                BiProcessedDataContainer,
                                                BiMetadataExperimentContainer,
                                                BiRunContainer)


class BiRawDataModel(BiModel):  
    def __init__(self, container: BiRawDataContainer):
        super().__init__()
        self._object_name = 'BiRawDataModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiRawDataStates.URIChanged:
            self.container.rawdata = APIAccess.instance().get_raw_data(self.container.md_uri)
            self.container.emit(BiRawDataStates.Loaded)
            return

        if action.state == BiRawDataStates.DeleteRawData:
            data = APIAccess.instance().get_raw_data(self.container.md_uri)    
            data.delete()
            self.container.emit(BiRawDataStates.RawDataDeleted)   

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
            self.container.processeddata = APIAccess.instance().get_processed_data(self.container.md_uri)
            self.container.emit(BiProcessedDataStates.Loaded)
            return    


class BiRunModel(BiModel):  
    def __init__(self, container: BiRunContainer):
        super().__init__()
        self._object_name = 'BiRunModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiRunStates.URIChanged:
            self.container.run = APIAccess.instance().get_run(self.container.md_uri)
            self.container.emit(BiRunStates.Loaded)
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
