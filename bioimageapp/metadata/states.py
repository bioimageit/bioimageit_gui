from bioimageapp.core.framework import BiStates

class BiMetadataStates(BiStates):
    URIChanged = "BiMetadataStates.URIChanged"
    OpenClicked = "BiMetadataStates.OpenClicked"

class BiMetadataEditorStates(BiStates):
    FileModified = "BiMetadataEditorStates.FileModified"
    JsonRead = "BiMetadataEditorStates.JsonRead"
    JsonWrote = "BiMetadataEditorStates.JsonWrote"
    JsonModified = "BiMetadataEditorStates.JsonModified" 