from bioimageit_core.experiment import Experiment

from bioimageit_gui.core.framework import BiModel, BiAction
from bioimageit_gui.experiment.states import (BiExperimentCreateStates,
                                              BiExperimentStates)
from bioimageit_gui.experiment.containers import (BiExperimentCreateContainer,
                                                  BiExperimentContainer)


class BiExperimentModel(BiModel):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Load or action.state == BiExperimentStates.RefreshClicked:
            self.container.experiment = Experiment(self.container.experiment_uri)
            self.container.emit(BiExperimentStates.Loaded)  

        if action.state == BiExperimentStates.DataSetClicked:
            self.container.current_dataset = self.container.experiment.get_dataset(self.container.current_dataset_name)
            self.container.emit(BiExperimentStates.DataSetLoaded)                  

        if action.state == BiExperimentStates.NewImportFile:
            self.container.experiment.import_data(
                data_path=self.container.import_info.file_data_path, 
                name=self.container.import_info.file_name,
                author=self.container.import_info.author, 
                format=self.container.import_info.format, 
                date = self.container.import_info.createddate, 
                tags = {}, 
                copy = self.container.import_info.file_copy_data
                )    
            self.container.emit(BiExperimentStates.DataImported)    

        if action.state == BiExperimentStates.NewImportDir:
            filter_regexp = ''
            if self.container.import_info.dir_filter == 0:
                filter_regexp = '\\' + self.container.import_info.dir_filter_value + '$'
            elif self.container.import_info.dir_filter == 1:
                filter_regexp = self.container.import_info.dir_filter_value    
            elif self.container.import_info.dir_filter == 2:
                filter_regexp = '^' + self.container.import_info.dir_filter_value 

            self.container.experiment.import_dir(dir_uri=self.container.import_info.dir_data_path,
                         filter=filter_regexp,
                         author=self.container.import_info.author, 
                         format=self.container.import_info.format, 
                         date=self.container.import_info.createddate, 
                         copy_data=self.container.import_info.dir_copy_data)

            self.container.emit(BiExperimentStates.DataImported)

        if action.state == BiExperimentStates.TagsModified:
            for tag in self.container.tag_info.tags:
                self.container.experiment.set_tag(tag)
            self.container.emit(BiExperimentStates.TagsSaved) 

        if action.state == BiExperimentStates.TagUsingSeparators:
            for i in range(len(self.container.tag_info.usingseparator_tags)):
                self.container.experiment.tag_using_seperator(
                    tag=self.container.tag_info.usingseparator_tags[i], 
                    separator=self.container.tag_info.usingseparator_separator[i], 
                    value_position=self.container.tag_info.usingseparator_position[i]
                )  
            self.container.emit(BiExperimentStates.DataTagged)     

        if action.state == BiExperimentStates.TagUsingName:  
            self.container.experiment.tag_from_name(
                self.container.tag_info.usingname_tag, 
                self.container.tag_info.usingname_search
                )   
            self.container.emit(BiExperimentStates.DataTagged)       


class BiExperimentCreateModel(BiModel):  
      
    def __init__(self, container: BiExperimentCreateContainer):
        super().__init__()
        self._object_name = 'BiExperimentCreateModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):

        if action.state == BiExperimentCreateStates.CreateClicked:
            try:
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
