from bioimageapp.core.framework import BiContainer

class BiRawDataContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiRawDataContainer'

        # data
        self.md_uri = '' 
        self.rawdata = None       
        