from bioimageit_gui.core.framework import BiStates


class BiRunnerStates(BiStates):
    ProcessUriChanged = "BiRunnerStates::ProcessUriChanged"
    ProcessInfoLoaded = "BiRunnerStates::ProcessInfoLoaded"
    RunProcess = "BiRunnerStates::RunProcess"
    RunFinished = "BiRunnerStates::RunFinished"