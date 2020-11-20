from bioimageit_gui.core.framework import BiContainer


class BiRawDataContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRawDataContainer'

        # data
        self.md_uri = '' 
        self.rawdata = None     


class BiProcessedDataContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiProcessedDataContainer'

        # data
        self.md_uri = '' 
        self.processeddata = None     


class BiRunContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRunContainer'

        # data
        self.md_uri = '' 
        self.run = None               


class BiMetadataExperimentContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataExperimentContainer'

        # data
        self.md_uri = '' 
        self.experiment = None           
