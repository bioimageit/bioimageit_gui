from bioimageit_framework.framework import BiContainer


class BiExperimentContainer(BiContainer):
    Load = 'load'
    ExperimentLoaded = 'experiment_loaded'
    EditInfoClicked = 'edit_info_clicked'
    ImportClicked = 'import_clicked'
    TagClicked = 'tag_clicked'
    ProcessClicked = 'process_clicked'
    RefreshClicked = 'refresh_clicked'
    DataSetClicked = 'dataset_clicked'
    CloseClicked = 'close_clicked'
    ViewData = 'ask_view_data'
    ViewRawMetaDataClicked = 'view_raw_metadata_clicked'
    ViewProcessedMetaDataClicked = 'view_processed_metadata_clicked'
    DeleteRawData = 'delete_raw_data'
    ImportFile = 'import_file'
    ImportDir = 'import_dir'
    AnnotateUsingSeparator = 'annotate_using_separator'
    AnnotateUsingName = 'annotate_using_name'
    MainPage = 'main_page_clicked'
    DataImported = 'data_imported'
    DataTagged = 'data_tagged'
    TagsModified = 'tags_modified'
    TagsSaved = 'tags_saved'
    DatasetLoaded = 'dataset_loaded'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiExperimentContainer'

        # data
        self.experiment_uri = ''
        self.experiment = None
        self.import_info = BiExperimentImportContainer()
        self.tag_info = BiExperimentTagContainer()
        self.current_dataset_name = 'data'
        self.current_dataset = None
        self.clickedRow = -1
        self.selected_data_info = None

    def init(self, uri):
        self.experiment_uri = uri
        self._notify(BiExperimentContainer.Load)

    def action_tags_modified(self, action, keys):
        self.tag_info.tags = keys
        self._notify(BiExperimentContainer.TagsModified)

    def action_tags_saved(self, action):
        self._notify(BiExperimentContainer.DataTagged)

    def action_experiment_loaded(self, action, experiment, dataset_name, dataset):
        self.experiment = experiment
        self.current_dataset_name = dataset_name
        self.current_dataset = dataset
        self._notify(BiExperimentContainer.ExperimentLoaded)      

    def action_ask_refresh(self, action):
        print('container emit ask refresh')
        self._notify(BiExperimentContainer.Load) 

    def action_view_data_clicked(self, action, data_info):
        print('container emit veiw data')
        self.selected_data_info = data_info
        self._notify(BiExperimentContainer.ViewData)

    def action_uri_change(self, action, uri):
        self.init(uri)  

    def action_edit_info_clicked(self, action):
        self._notify(BiExperimentContainer.EditInfoClicked)

    def action_import_clicked(self, action):
         self._notify(BiExperimentContainer.ImportClicked)

    def action_tag_clicked(self, action):
        self._notify(BiExperimentContainer.TagClicked)    

    def action_process_clicked(self, action):
        self._notify(BiExperimentContainer.ProcessClicked) 

    def action_refresh_clicked(self, action):
        self._notify(BiExperimentContainer.RefreshClicked)  

    def action_main_page_clicked(self, action):
        self._notify(BiExperimentContainer.MainPage)    

    def action_dataset_clicked(self, action, dataset_name):
        print('the toolbar list change the dataset name to:', dataset_name)
        self.current_dataset_name = dataset_name
        self._notify(BiExperimentContainer.DataSetClicked)

    def action_dataset_loaded(self, action, dataset):
        self.current_dataset = dataset
        self.current_dataset_name = dataset.name
        self._notify(BiExperimentContainer.DatasetLoaded)

    def action_close_clicked(self, action):
        self._notify(BiExperimentContainer.CloseClicked) 

    def action_view_raw_metadata_clicked(self, action):
        self._notify(BiExperimentContainer.ViewRawMetaDataClicked)       

    def action_view_processed_metadata_clicked(self, action):
        self._notify(BiExperimentContainer.ViewProcessedMetaDataClicked)

    def action_delete_raw_data(self, action, row, selected_data_info):    
        self.clickedRow = row
        self.selected_data_info = selected_data_info
        self._notify(BiExperimentContainer.DeleteRawData)

    def action_import_file(self, action, file_data_path, file_name, format, author, createddate):
        self.import_info.file_data_path = file_data_path
        self.import_info.file_name = file_name
        self.import_info.format = format
        self.import_info.author = author
        self.import_info.createddate = createddate
        self._notify(BiExperimentContainer.ImportFile)  

    def action_import_dir(self, action, dir_data_path, dir_tag_key, dir_filter, dir_filter_value, author, format, createddate):
        self.import_info.dir_data_path = dir_data_path
        self.import_info.dir_tag_key = dir_tag_key
        self.import_info.dir_filter = dir_filter
        self.import_info.dir_filter_value = dir_filter_value
        self.import_info.author = author
        self.import_info.format = format
        self.import_info.createddate = createddate
        self._notify(BiExperimentContainer.ImportDir)  

    def action_annotate_using_separator(self, action, keys, separator, position):
        self.tag_info.usingseparator_tags = keys
        self.tag_info.usingseparator_separator = separator
        self.tag_info.usingseparator_position = position  
        self._notify(BiExperimentContainer.AnnotateUsingSeparator)                

    def action_annotate_using_name(self, action, tag, search):
        self.tag_info.usingname_tag = tag
        self.tag_info.usingname_search = search
        self._notify(BiExperimentContainer.AnnotateUsingName) 

    def action_data_imported(self, action):
        print('action data imported')
        self._notify(BiExperimentContainer.DataImported)  

    def action_data_tagged(self, action):
        print('action data imported')
        self._notify(BiExperimentContainer.DataTagged)           


class BiExperimentImportContainer():
    def __init__(self):
        super().__init__()
        self.dir_data_path = ''
        self.dir_tag_key = ''
        self.dir_filter = ''
        self.dir_filter_value = ''
        self.file_data_path = ''
        self.file_name = ''
        self.format = ''
        self.author = ''
        self.createddate = ''    


class BiExperimentTagContainer():
    def __init__(self):
        super().__init__()
        self.tags = []
        self.usingname_tag = ''
        self.usingname_search = []
        self.usingseparator_tags = []
        self.usingseparator_separator = []
        self.usingseparator_position = []    
        self.usingname_tag = ''
        self.usingname_search = []      


class BiExperimentCreateContainer(BiContainer):
    CreateExp = 'create_experiment'
    ExpCreated = 'experiment_created'

    def __init__(self):
        super().__init__()
        self._object_name = 'BiExperimentCreateContainer'

        # data
        self.experiment_destination_dir = ''
        self.experiment_name = ''
        self.experiment_author = ''
        self.errorMessage = ''
        self.experiment_uri = ''
        
    def action_experiment_created(self, action, experiment_uri):
        self.experiment_uri = experiment_uri
        self._notify(BiExperimentCreateContainer.ExpCreated)

    def action_create(self, action, destination, name, author):
        self.experiment_destination_dir = destination
        self.experiment_name = name
        self.experiment_author = author
        self._notify(BiExperimentCreateContainer.CreateExp)
