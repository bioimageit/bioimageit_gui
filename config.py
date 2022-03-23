import os
import json
from pathlib import Path


def write_json(metadata: dict, md_uri: str):
    """Write the metadata to the a json file"""
    with open(md_uri, 'w') as outfile:
        json.dump(metadata, outfile, indent=4)  


if __name__ == '__main__':
    pass
