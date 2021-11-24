from bioimageit_gui.core.framework import BiStates


class BiUpdateStates(BiStates):
    UpdateClicked = "BiUpdateStates::UpdateClicked"
    UpdateFinished = "BiUpdateStates::UpdateFinished"

class BiConfigStates(BiStates):
    ConfigEdited = "BiConfigStates::ConfigChanged"
    ConfigSaved = "BiConfigStates::ConfigSaved"    