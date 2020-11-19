import os
import json


class BiBookmarks:
    def __init__(self, filename=''):
        super().__init__()
        self._object_name = 'BiBookmarks'
        self.filename = filename
        self.bookmarks = dict()
        if filename != '':
            self.read() 

    def read(self):
        """Read the bookmarks to the file in json format"""
        if os.path.getsize(self.filename) > 0:
            with open(self.filename) as json_file:  
                self.bookmarks = json.load(json_file)

    def write(self):
        """Write the bookmarks to the json file at filename"""
        with open(self.filename, 'w') as outfile:
            json.dump(self.bookmarks, outfile, indent=4)  

    def clear(self):
        self.bookmarks = dict()

    def set(self, name: str, url: str):
        data = dict()
        data['name'] = name
        data['url'] = url
        self.bookmarks['bookmarks'].append(data)
