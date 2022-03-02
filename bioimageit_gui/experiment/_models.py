from qtpy.QtCore import QThread
from bioimageit_core.api import APIAccess

from bioimageit_framework.framework import BiActuator, BiConnectome
from ._containers import (BiExperimentCreateContainer,
                          BiExperimentContainer)


class BiExperimentModel(BiActuator):
    LOADED = 'loaded'
    DataSetLoaded = 'dataset_loaded'
    ImportFile = 'import_file'
    TagsSaved = 'tags_saved'
    DataTagged = 'data_tagged'
    DataImported = 'data_imported'

    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentModel'
        self.thread = BiImportThread(container)
        self.thread.finished.connect(self.import_finished)

    def import_finished(self):
        self._emit(BiExperimentModel.DataImported)

    def callback_load(self, emitter):
        experiment = APIAccess.instance().get_experiment(emitter.experiment_uri)
        self._emit(BiExperimentModel.LOADED, experiment)

    def callback_refresh_clicked(self, emitter):
        experiment = APIAccess.instance().get_experiment(emitter.experiment_uri)
        self._emit(BiExperimentModel.LOADED, experiment)

    def callback_dataset_clicked(self, emitter):
        current_dataset = APIAccess.instance().get_dataset(emitter.experiment, emitter.current_dataset_name)
        self._emit(BiExperimentModel.DataSetLoaded, current_dataset)

    def callback_import_file(self, emitter):
        self.thread.mode = 'file'
        self.thread.data_path=emitter.import_info.file_data_path
        self.thread.name=emitter.import_info.file_name
        self.thread.author=emitter.import_info.author
        self.thread.format_=emitter.import_info.format
        self.thread.date=emitter.import_info.createddate
        self.thread.tags={}
        self.thread.start()

    def callback_import_dir(self, emitter):
        filter_regexp = ''
        if emitter.import_info.dir_filter == 0:
            filter_regexp = '.*\\' + emitter.import_info.dir_filter_value + '$'
        elif emitter.import_info.dir_filter == 1:
            filter_regexp = emitter.import_info.dir_filter_value
        elif emitter.import_info.dir_filter == 2:
            filter_regexp = '^' + emitter.import_info.dir_filter_value

        self.thread.mode = 'folder'
        self.thread.dir_uri = emitter.import_info.dir_data_path
        self.thread.filter_ = filter_regexp
        self.thread.author = emitter.import_info.author
        self.thread.format_ = emitter.import_info.format
        self.thread.date =emitter.import_info.createddate
        self.thread.dir_tag_key = emitter.import_info.dir_tag_key
        self.thread.start()   

    def callback_tags_modified(self, emitter):
        APIAccess.instance().set_keys(emitter.experiment, emitter.tag_info.tags)
        self._emit(BiExperimentModel.TagsSaved)       

    def callback_tag_using_separators(self, emitter):
        for i in range(len(emitter.tag_info.usingseparator_tags)):
            APIAccess.instance().annotate_using_seperator(
                emitter.experiment,
                key=emitter.tag_info.usingseparator_tags[i],
                separator=emitter.tag_info.usingseparator_separator[i],
                value_position=emitter.tag_info.usingseparator_position[i]
                )
        self._emit(BiExperimentModel.DataTagged)    

    def callback_tag_using_names(self, emitter):
        emitter.experiment.tag_from_name(
                emitter.tag_info.usingname_tag,
                emitter.tag_info.usingname_search
            )
        self._emit(BiExperimentModel.DataTagged)

                


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


class BiExperimentCreateModel(BiActuator):
    ExperimentCreationError = 'experiment_creation_error'
    ExperimentCreated = 'experiment_created'

    def __init__(self, container: BiExperimentCreateContainer):
        super().__init__()
        self._object_name = 'BiExperimentCreateModel'
        self.container = container
        BiConnectome.connect( self.container, self)

    def callback_create_experiment(self, emitter):
        try:
            print('create experiment to: ', emitter.experiment_destination_dir)
            experiment = APIAccess.instance().create_experiment(
                              emitter.experiment_name,
                              emitter.experiment_author,
                              'now',
                              keys=None,
                              destination=emitter.experiment_destination_dir)

            self._emit(BiExperimentCreateModel.ExperimentCreated, experiment.md_uri)
        except FileNotFoundError as err:
            self._emit(BiExperimentCreateModel.ExperimentCreationError, err)
