from bioimageapp.core.framework import BiStates

class BiExperimentStates(BiStates):
    ImportClicked = "BiExperimentStates.ImportClicked" 
    TagClicked = "BiExperimentStates.TagClicked"  
    ProcessClicked = "BiExperimentStates.ProcessClicked" 


class BiExperimentCreateStates(BiStates):
    CreateClicked = "BiExperimentCreateStates.CreateClicked"
    CancelClicked = "BiExperimentCreateStates.CancelClicked"
    ExperimentCreated = "BiExperimentCreateStates.ExperimentCreated"
    ExperimentCreationError = "BiExperimentCreateStates.ExperimentCreationError"  