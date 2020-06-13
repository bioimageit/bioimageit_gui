from bioimageapp.core.framework import BiStates

class BiRawDataStates(BiStates):
    URIChanged = "BiRawDataStates.URIChanged"
    Loaded = "BiRawDataStates.Loaded"
    SaveClicked = "BiRawDataStates.SaveClicked"
    Saved = "BiRawDataStates.Saved"

class BiProcessedDataStates(BiStates):
    URIChanged = "BiProcessedDataStates.URIChanged"
    Loaded = "BiProcessedDataStates.Loaded"  

class BiMetadataExperimentStates(BiStates):
    Loaded = "BiMetadataExperimentStates.Loaded"
    SaveClicked = "BiMetadataExperimentStates.SaveClicked"
    Saved = "BiMetadataExperimentStates.Saved"    