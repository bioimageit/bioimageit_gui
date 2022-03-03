import os

from bioimageit_core.api import APIAccess

from bioimageit_framework.framework import BiActuator


class BiRawDataModel(BiActuator):  
    Loaded = "loaded"
    Deleted = 'deleted'
    Saved = 'saved'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRawDataModel'

    def callback_uri_changed(self, emitter):
        rawdata = APIAccess.instance().get_raw_data(emitter.md_uri)
        self._emit(BiRawDataModel.Loaded, rawdata)

    def callback_delete(self, emitter):
        APIAccess.instance().delete_raw_data(emitter.md_uri)  
        self._emit(BiRawDataModel.Deleted)

    def callback_save(self, emitter):
        APIAccess.instance().update_raw_data(emitter.rawdata)
        self._emit(BiRawDataModel.Saved)


class BiProcessedDataModel(BiActuator):  
    Loaded = 'loaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiProcessedDataModel'

    def callback_uri_changed(self, emitter):
        processeddata = APIAccess.instance().get_processed_data(emitter.md_uri)
        self.e_mit(BiProcessedDataModel.Loaded, processeddata)    


class BiRunModel(BiActuator): 
    Loaded = 'loaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRunModel'

    def callback_uri_changed(self, emitter):
        run = APIAccess.instance().get_run(emitter.md_uri)
        self._emit(BiRunModel.Loaded, run)    


class BiMetadataExperimentModel(BiActuator): 
    Saved = 'metadata_saved'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataExperimentModel'

    def callback_metadata_save(self, emitter):
        APIAccess.instance().update_experiment(emitter.experiment)
        self._emit(BiMetadataExperimentModel.Saved)
