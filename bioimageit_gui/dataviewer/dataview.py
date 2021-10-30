import os
import subprocess
from pathlib import Path
import json

from bioimageit_core.config import ConfigAccess
from bioimageit_formats import FormatsAccess


class BiDataView:
    def __init__(self, uri: str, format_: str):
        self.uri = uri
        self.format_ = format_

    def show(self):
        format_info = FormatsAccess.instance().get(self.format_)

        if format_info.viewer != "":
            install_dir = ConfigAccess.instance().get('install_dir')
            plan = dict()
            plan0 = dict()
            plan0['position'] = [0, 0, 1, 1]
            plan0['widget'] = format_info.viewer
            plan0['data'] = [{'uri': self.uri, 'format': self.format_}]
            plan['plan'] = [plan0]
            with open(os.path.join(install_dir,'.plan.json'), 'w') as outfile:
                json.dump(plan, outfile, indent=4)

            viewer_app = ConfigAccess.instance().get('apps')['viewer'] 
            subprocess.Popen([viewer_app, os.path.join(install_dir, '.plan.json')])
                           #   'bioimageit_viewer'+os.path.sep+'biviewerapp.py',
                           #   '.plan.json'])
        else:
            print('Cannot find viewer for format ' + self.format_)

        #plan = BiDisplayPlan()
        #region = BiDisplayRegion()
        #region.position = [0, 0, 1, 1]
        #format_info = FormatsAccess.instance().get(self.format_)
        #if 'viewer' in format_info:
        #    region.widget = format_info['viewer']
        #    region.data_list.append(BiDisplayData(self.uri, self.format_))
        #    plan.regions.append(region)
        #    display = BiDisplay(plan)
        #    display.get_widget().show()
        #else:
        #    print('Cannot find viewer for format ' + self.format_)

