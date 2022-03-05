from bioimageit_framework.framework import BiContainer


class BiRawDataContainer(BiContainer):
    URIChanged = 'raw_data_uri_changed'
    Loaded = 'raw_data_loaded'
    Deleted = 'raw_data_deleted'
    ASK_SAVE = 'raw_data_save'
    SAVED = 'raw_data_saved'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRawDataContainer'

        # data
        self.md_uri = '' 
        self.rawdata = None   

    def action_update_uri(self, action, uri):
        self.md_uri = uri
        self._notify(BiRawDataContainer.URIChanged)

    def action_raw_data_loaded(self, action, rawdata):
        self.rawdata = rawdata   
        self._notify(BiRawDataContainer.Loaded)  

    def action_raw_data_delete(self, action, uri):
        self.md_uri = uri
        self._notify(BiRawDataContainer.Delete)  

    def action_raw_data_deleted(self, action):
        self.md_uri = '' 
        self.rawdata = None   
        self._notify(BiRawDataContainer.Deleted)   

    def action_raw_data_save(self, action, name, format, date, author, key_value_pairs):
        self.rawdata.name = name
        self.rawdata.format = format
        self.rawdata.date = date
        self.rawdata.author = author
        self.rawdata.key_value_pairs = key_value_pairs
        self._notify(BiRawDataContainer.ASK_SAVE) 

    def action_raw_data_saved(self, action):
        self._notify(BiRawDataContainer.SAVED)     



class BiProcessedDataContainer(BiContainer):
    Loaded = 'loaded'
    UriChanged = 'uri_changed'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiProcessedDataContainer'
        # data
        self.md_uri = '' 
        self.processeddata = None  

    def action_update_uri(self, action, uri):
        self.md_uri = uri
        self._notify(BiProcessedDataContainer.UriChanged)

    def action_loaded(self, action, processeddata):
        self.processeddata = processeddata
        self._notify(BiProcessedDataContainer.Loaded)


class BiRunContainer(BiContainer):
    Loaded = 'loaded'
    UriChanged = 'uri_changed'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRunContainer'

        # data
        self.md_uri = '' 
        self.run = None   

    def uri_changed(self, action, uri):
        self.md_uri = uri
        self._notify(BiRunContainer.UriChanged)     

    def action_loaded(self, action, run):
        self.run = run
        self._notify(BiRunContainer.Loaded)                


class BiMetadataExperimentContainer(BiContainer):
    Save = 'metadata_save'
    Saved = 'metadata_saved'
    UriChanged = 'metadata_uri_changed'
    MetadataLoaded = 'metadata_loaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataExperimentContainer'

        # data
        self.md_uri = '' 
        self.experiment = None           

    def action_metadata_uri_changed(self, action, uri):
        self.md_uri = uri
        self._notify(BiMetadataExperimentContainer.UriChanged)

    def action_metadata_loaded(self, action, experiment):
        self.experiment = experiment
        self._notify(BiMetadataExperimentContainer.MetadataLoaded)    

    def action_metadata_saved(self, action):
        self._notify(BiMetadataExperimentContainer.Saved)

    def action_metadata_save_clicked(self, action, name, author, createddate):
        self.experiment.name = name
        self.experiment.author = author
        self.experiment.created_date = createddate
        self._notify(BiMetadataExperimentContainer.Save)    