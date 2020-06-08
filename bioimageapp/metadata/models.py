import os

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.metadata.states import BiMetadataEditorStates
from bioimageapp.metadata.containers import BiMetadataEditorContainer


class BiMetadataEditorModel(BiModel):  
    def __init__(self, container: BiMetadataEditorContainer):
        super(BiMetadataEditorModel, self).__init__()
        self._object_name = 'BiMetadataEditorModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiMetadataEditorStates.FileModified:
            self.read(self.container.file)
            self.container.emit(BiMetadataEditorStates.JsonRead)
            return

        if action.state == BiMetadataEditorStates.JsonModified:
            self.write(self.container.file, self.container.content)
            self.container.emit(BiMetadataEditorStates.JsonWrote)
    
    def read(self, file : str):
        """Read the metadata from the a json file"""
        if os.path.getsize(file) > 0:
            f = open(file, "r")
            self.container.content = f.read()
            f.close()

    def write(self, file : str, content : str ):
        """Write the metadata to the a json file"""
        f = open(file, "w") 
        f.write(self.container.content)
        f.close()        
