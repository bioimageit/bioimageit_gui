import os
import subprocess
from pathlib import Path


class BiDataView:
    def __init__(self, uri: str, format: str):
        self.uri = uri
        self.format = format

    def show(self):
        print('dataview show format:', self.format)
        if self.format == 'tif' or self.format == 'tiff':
            self.openImageViewer(self.uri)
        elif self.format == 'csv':
            self.openTableViewer(self.uri)

    def openImageViewer(self, uri):
        subprocess.Popen(['napari', uri])

    def openTableViewer(self, uri):
        print('open csv from: ', uri)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = Path(dir_path).parent
        subprocess.Popen(['python3', os.path.join(path, 'dataviewer',
                                                  'csvviewer.py'), uri])

