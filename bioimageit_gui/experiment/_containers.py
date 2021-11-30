from bioimageit_gui.core.framework import BiContainer


class BiExperimentContainer(BiContainer):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiExperimentContainer'

        # data
        self.experiment_uri = ''
        self.experiment = None
        self.import_info = BiExperimentImportContainer()
        self.tag_info = BiExperimentTagContainer()
        self.current_dataset_name = ''
        self.current_dataset = None
        self.clickedRow = -1
        self.selected_data_info = None


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

    def __init__(self):
        super().__init__()
        self._object_name = 'BiExperimentCreateContainer'

        # data
        self.experiment_destination_dir = ''
        self.experiment_name = ''
        self.experiment_author = ''
        self.errorMessage = ''
        self.experiment_dir = ''
