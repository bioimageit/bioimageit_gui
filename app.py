import sys
import os

from qtpy import QtCore
from qtpy.QtGui import QIcon, QGuiApplication
from qtpy.QtWidgets import QApplication, QStyle

from bioimageit_core.config import ConfigAccess
from bioimageit_formats import FormatsAccess

from bioimageit_gui.core.theme import BiThemeAccess
from bioimageit_gui.apps.app import BioImageITApp

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(['BioImageIT'])
        
    # Create and show the component
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_parent = os.path.abspath(os.path.join(dir_path, os.pardir))
    ConfigAccess(os.path.join(dir_path_parent, 'config.json'))
    FormatsAccess(ConfigAccess.instance().get('formats')['file'])
    BiThemeAccess(os.path.join(dir_path, 'theme', 'dark'))
    FormatsAccess(ConfigAccess.instance().get('formats')['file'])

    bookmark_file = os.path.join(dir_path_parent, 'bookmarks.json')
    component = BioImageITApp()

    component.get_widget().setWindowTitle("BioImageIT")
    component.get_widget().resize(800, 600)
    component.get_widget().showMaximized()
    component.get_widget().show()
    
    # Run the main Qt loop
    stylesheet_path = os.path.join(dir_path, 'theme', 'dark', 'stylesheet.css')
    print('stylesheet path=', stylesheet_path)
    app.setStyleSheet("file:///" + stylesheet_path)
    icon_path = os.path.join(dir_path, "theme", "dark", "icon.png")
    app.setWindowIcon(QIcon(icon_path))
    sys.exit(app.exec_())
