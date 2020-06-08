from bioimagepy.experiment import Experiment

from bioimageapp.core.framework import BiModel, BiAction
from bioimageapp.experiment.states import BiExperimentCreateStates
from bioimageapp.experiment.containers import BiExperimentCreateContainer

class BiExperimentCreateModel(BiModel):    

    def __init__(self, container: BiExperimentCreateContainer):
        super(BiExperimentCreateModel, self).__init__()
        self._object_name = 'BiExperimentCreateModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):

        if action.state == BiExperimentCreateStates.CreateClicked:
            try:

                print('create experiment at ', self.container.experiment_destination_dir)
                experiment = Experiment()
                experiment.create(self.container.experiment_name, 
                                  self.container.experiment_author, 
                                  'now',
                                  self.container.experiment_destination_dir) 

                self.container.experiment_dir = experiment.md_uri
                self.container.emit(BiExperimentCreateStates.ExperimentCreated)                   
            except FileNotFoundError as err:
                self.container.errorMessage = err
                self.container.emit(BiExperimentCreateStates.ExperimentCreationError)
