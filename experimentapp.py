import sys
import os

from PySide2 import QtCore
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtWidgets import QApplication, QStyle

from bioimageit_core.config import ConfigAccess
from bioimageit_formats import FormatsAccess

from bioimageit_gui.core.theme import BiThemeAccess
from bioimageit_gui.experiment2.components import BiExperimentViewerComponent

from bioimageit_gui.core.exceptions import CommandArgsError

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(['BioImageIT'])

    # load the args
    experiment_uri = ""
    if len(sys.argv) > 1:
        experiment_uri = sys.argv[1]
    if experiment_uri == "":
        raise CommandArgsError("No Experiment file")
        
    # Create and show the component
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_parent = os.path.abspath(os.path.join(dir_path, os.pardir))
    ConfigAccess(os.path.join(dir_path_parent, 'config.json'))
    FormatsAccess(ConfigAccess.instance().get('formats')['file'])
    BiThemeAccess(os.path.join(dir_path, 'theme', 'dark'))
    FormatsAccess(ConfigAccess.instance().get('formats')['file'])

    bookmark_file = os.path.join(dir_path_parent, 'bookmarks.json')
    component = BiExperimentViewerComponent(experiment_uri)

    component.get_widget().setWindowTitle("BioImageIT")
    component.get_widget().showMaximized()
    component.get_widget().show()
    
    # Run the main Qt loop
    stylesheet_path = os.path.join(dir_path, 'theme', 'dark', 'stylesheet.css')
    app.setStyleSheet("file:///" + stylesheet_path)
    icon_path = os.path.join(dir_path, "theme", "default", "icon.png")
    app.setWindowIcon(QIcon(icon_path))
    sys.exit(app.exec_())
