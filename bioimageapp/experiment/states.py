from bioimageapp.core.framework import BiStates

class BiExperimentStates(BiStates):
    ImportClicked = "BiExperimentStates.ImportClicked" 
    TagClicked = "BiExperimentStates.TagClicked"  
    ProcessClicked = "BiExperimentStates.ProcessClicked" 
    Load = "BiExperimentStates.Load"
    Loaded = "BiExperimentStates.Loaded"
    TagsModified = "BiExperimentStates.TagsModified"
    TagUsingSeparators = "BiExperimentStates.TagUsingSeparators"
    TagUsingName = "BiExperimentStates.TagUsingName"
    RawDataImported = "BiExperimentStates.RawDataImported"
    NewImport = "BiExperimentStates.NewImport"
    Progress = "BiExperimentStates.Progress"
    NewImportDir = "BiExperimentStates.NewImportDir"
    NewImportFile = "BiExperimentStates.NewImportFile"
    DataImported = "BiExperimentStates.DataImported"
    TagsSaved = "BiExperimentStates.TagsSaved"
    DataTagged = "BiExperimentStates.DataTagged"

class BiExperimentCreateStates(BiStates):
    CreateClicked = "BiExperimentCreateStates.CreateClicked"
    CancelClicked = "BiExperimentCreateStates.CancelClicked"
    ExperimentCreated = "BiExperimentCreateStates.ExperimentCreated"
    ExperimentCreationError = "BiExperimentCreateStates.ExperimentCreationError"  