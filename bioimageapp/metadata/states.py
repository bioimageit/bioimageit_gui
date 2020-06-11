from bioimageapp.core.framework import BiStates

class BiRawDataStates(BiStates):
    URIChanged = "BiRawDataStates.URIChanged"
    Loaded = "BiRawDataStates.Loaded"
    SaveClicked = "BiRawDataStates.SaveClicked"
    Saved = "BiRawDataStates.Saved"

class BiMetadataExperimentStates(BiStates):
    Loaded = "BiMetadataExperimentStates.Loaded"
    SaveClicked = "BiMetadataExperimentStates.SaveClicked"
    Saved = "BiMetadataExperimentStates.Saved"    