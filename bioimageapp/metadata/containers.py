from bioimageapp.core.framework import BiContainer

class BiMetadataContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataContainer'

        # data
        self.md_uri = ''

class BiMetadataEditorContainer(BiContainer):

    def __init__(self):
        super().__init__()
        self._object_name = 'BiMetadataEditorContainer'

        # data
        self.file = ''
        self.content = ''  