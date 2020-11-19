import os
import json
from pathlib import Path


def write_json(metadata: dict, md_uri: str):
    """Write the metadata to the a json file"""
    with open(md_uri, 'w') as outfile:
        json.dump(metadata, outfile, indent=4)  


if __name__ == '__main__':
    
    # create the bookmarks file at bookmarks.json
    bioimageapp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    package_dir = Path(bioimageapp_dir).parent

    config_json = dict()  
    config_json["bookmarks"] = []
    userdata = {"name": "userdata",
                "url": os.path.join(package_dir,
                                    "userdata")}
    config_json["bookmarks"].append(userdata)

    config_file = os.path.join(package_dir, 'bookmarks.json')
    write_json(config_json, config_file)
