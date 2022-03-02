from bioimageit_framework.framework import BiContainer


class BiRawDataContainer(BiContainer):
    URIChanged = 'uri_changed'
    Loaded = 'loaded'
    Deleted = 'deleted'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRawDataContainer'

        # data
        self.md_uri = '' 
        self.rawdata = None   

    def action_update_uri(self, action, uri):
        self.md_uri = uri
        self._notify(BiRawDataContainer.URIChanged)

    def action_loaded(self, action, rawdata):
        self.rawdata = rawdata   
        self._notify(BiRawDataContainer.Loaded)  

    def action_delete(self, action, uri):
        self.md_uri = uri
        self._notify(BiRawDataContainer.Delete)  

    def action_deleted(self, action):
        self.md_uri = '' 
        self.rawdata = None   
        self._notify(BiRawDataContainer.Deleted)         


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
    Save = 'save'
    Saved = 'saved'
    UriChanged = 'uri_changed'
    Loaded = 'loaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataExperimentContainer'

        # data
        self.md_uri = '' 
        self.experiment = None           

    def action_uri_changed(self, action, uri):
        self.md_uri = uri
        self._notify(BiMetadataExperimentContainer.UriChanged)

    def action_loaded(self, action, experiment):
        self.experiment = experiment
        self._notify(BiMetadataExperimentContainer.Loaded)    

    def action_saved(self, action):
        self._notify(BiMetadataExperimentContainer.Saved)

    def action_save_clicked(self, action, name, author, createddate):
        self.experiment.name = name
        self.experiment.author = author
        self.experiment.created_date = createddate
        self._notify(BiMetadataExperimentContainer.Save)    