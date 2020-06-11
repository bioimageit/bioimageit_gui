import os

from bioimagepy.data import RawData

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.metadata.states import BiRawDataStates
from bioimageapp.metadata.containers import BiRawDataContainer


class BiRawDataModel(BiModel):  
    def __init__(self, container: BiRawDataContainer):
        super().__init__()
        self._object_name = 'BiMetadataEditorModel'
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
       
