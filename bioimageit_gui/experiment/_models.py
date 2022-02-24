from qtpy.QtCore import QThread
from bioimageit_core.api import APIAccess

from bioimageit_gui.core.framework import BiModel, BiAction
from ._states import (BiExperimentCreateStates,
                      BiExperimentStates)
from ._containers import (BiExperimentCreateContainer,
                          BiExperimentContainer)


class BiExperimentModel(BiModel):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentModel'
        self.container = container
        self.container.register(self)
        self.thread = BiImportThread(container)
        self.thread.finished.connect(self.import_finished)

    def import_finished(self):
        self.container.emit(BiExperimentStates.DataImported)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Load or action.state == \
                BiExperimentStates.RefreshClicked:
            self.container.experiment = APIAccess.instance().get_experiment(
                self.container.experiment_uri)
            self.container.emit(BiExperimentStates.Loaded)

        if action.state == BiExperimentStates.DataSetClicked:
            self.container.current_dataset = APIAccess.instance().get_dataset(self.container.experiment, self.container.current_dataset_name)
            self.container.emit(BiExperimentStates.DataSetLoaded)

        if action.state == BiExperimentStates.NewImportFile:
            self.thread.mode = 'file'
            self.thread.data_path=self.container.import_info.file_data_path
            self.thread.name=self.container.import_info.file_name
            self.thread.author=self.container.import_info.author
            self.thread.format_=self.container.import_info.format
            self.thread.date=self.container.import_info.createddate
            self.thread.tags={}
            self.thread.start()

        if action.state == BiExperimentStates.NewImportDir:
            filter_regexp = ''
            if self.container.import_info.dir_filter == 0:
                filter_regexp = '.*\\' + self.container.import_info.dir_filter_value + '$'
            elif self.container.import_info.dir_filter == 1:
                filter_regexp = self.container.import_info.dir_filter_value
            elif self.container.import_info.dir_filter == 2:
                filter_regexp = '^' + self.container.import_info.dir_filter_value

            self.thread.mode = 'folder'
            self.thread.dir_uri = self.container.import_info.dir_data_path
            self.thread.filter_ = filter_regexp
            self.thread.author = self.container.import_info.author
            self.thread.format_ = self.container.import_info.format
            self.thread.date = self.container.import_info.createddate
            self.thread.dir_tag_key = self.container.import_info.dir_tag_key
            self.thread.start()

        if action.state == BiExperimentStates.TagsModified:
            APIAccess.instance().set_keys(self.container.experiment, self.container.tag_info.tags)
            self.container.emit(BiExperimentStates.TagsSaved)

        if action.state == BiExperimentStates.TagUsingSeparators:
            for i in range(len(self.container.tag_info.usingseparator_tags)):
                APIAccess.instance().annotate_using_seperator(
                    self.container.experiment,
                    key=self.container.tag_info.usingseparator_tags[i],
                    separator=self.container.tag_info.usingseparator_separator[
                        i],
                    value_position=
                    self.container.tag_info.usingseparator_position[i]
                )
            self.container.emit(BiExperimentStates.DataTagged)

        if action.state == BiExperimentStates.TagUsingName:
            self.container.experiment.tag_from_name(
                self.container.tag_info.usingname_tag,
                self.container.tag_info.usingname_search
            )
            self.container.emit(BiExperimentStates.DataTagged)    


class BiImportThread(QThread):
    def __init__(self, container) -> None:
        super().__init__()
        self.container = container
        self.mode = ''
        self.data_path = '',
        self.dir_uri = '',
        self.filter_ = ''
        self.name = '',
        self.author = '',
        self.format_ = '',
        self.date = '',
        self.tags = {},
        self.dir_tag_key = ''

    def run(self):
        if self.mode == 'file':
            APIAccess.instance().import_data(self.container.experiment,
                                             data_path=self.data_path,
                                             name=self.name,
                                             author=self.author,
                                             format_=self.format_,
                                             date=self.date,
                                             key_value_pairs=self.tags
                                            )
        elif self.mode == 'folder':
            APIAccess.instance().import_data(
                self.container.experiment,
                dir_uri=self.dir_uri,
                filter_ = self.filter_,
                author = self.author,
                format_ = self.format_,
                date = self.date,
                directory_tag_key = self.dir_tag_key)  


class BiExperimentCreateModel(BiModel):

    def __init__(self, container: BiExperimentCreateContainer):
        super().__init__()
        self._object_name = 'BiExperimentCreateModel'
        self.container = container
        self.container.register(self)

    def update(self, action: BiAction):

        if action.state == BiExperimentCreateStates.CreateClicked:
            try:
                experiment = APIAccess.instance().create_experiment(
                                  self.container.experiment_name,
                                  self.container.experiment_author,
                                  'now',
                                  self.container.experiment_destination_dir)

                self.container.experiment_dir = experiment.md_uri
                self.container.emit(BiExperimentCreateStates.ExperimentCreated)
            except FileNotFoundError as err:
                self.container.errorMessage = err
                self.container.emit(
                    BiExperimentCreateStates.ExperimentCreationError)
