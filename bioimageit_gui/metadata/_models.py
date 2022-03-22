import os

from bioimageit_core.api import APIAccess

from bioimageit_framework.framework import BiActuator


class BiRawDataModel(BiActuator):  
    Loaded = "raw_data_loaded"
    Deleted = 'raw_data_deleted'
    Saved = 'raw_data_saved'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRawDataModel'

    def callback_raw_data_uri_changed(self, emitter):
        rawdata = APIAccess.instance().get_raw_data(emitter.md_uri)
        self._emit(BiRawDataModel.Loaded, rawdata)

    def callback_raw_data_delete(self, emitter):
        APIAccess.instance().delete_raw_data(emitter.md_uri)  
        self._emit(BiRawDataModel.Deleted)

    def callback_raw_data_save(self, emitter):
        APIAccess.instance().update_raw_data(emitter.rawdata)
        self._emit(BiRawDataModel.Saved)


class BiProcessedDataModel(BiActuator):  
    Loaded = 'processed_data_loaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiProcessedDataModel'

    def callback_processed_data_uri_changed(self, emitter):
        print('BiProcessedDataModel reload pdata from uri=', emitter.md_uri)
        processeddata = APIAccess.instance().get_processed_data(emitter.md_uri)
        self._emit(BiProcessedDataModel.Loaded, processeddata)    


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
