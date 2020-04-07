
from bioimageapp.core.framework import BiStates

class BiRunnerStates(BiStates):
    ProcessUriChanged = "BiRunnerStates::ProcessUriChanged"
    ProcessInfoLoaded = "BiRunnerStates::ProcessInfoLoaded"
    RunProcess = "BiRunnerStates::RunProcess"