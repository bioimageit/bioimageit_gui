import sys
import os

from qtpy import QtCore
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication, QMessageBox

from bioimageit_core.api import APIAccess
from bioimageit_core import ConfigAccess
from bioimageit_formats import FormatsAccess

from bioimageit_framework.framework import BiGuiObserver
from bioimageit_framework.theme import BiThemeAccess, BiThemeSheets
from bioimageit_gui.apps.app import BioImageITApp

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(['BioImageIT'])

    # Create and show the component
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_parent = os.path.abspath(os.path.join(dir_path, os.pardir))
    try:
        APIAccess.instance(os.path.join(dir_path_parent, 'config.json'), False).connect()     
        #ConfigAccess(os.path.join(dir_path_parent, 'config.json'))
        FormatsAccess(ConfigAccess.instance().get('formats')['file'])

        # add gui observer
        APIAccess.instance().add_observer(BiGuiObserver())

        # load and set the theme
        BiThemeAccess(os.path.join(dir_path, 'theme', 'dark'))
        BiThemeAccess.instance().set_stylesheet(app, BiThemeSheets.sheets())

        bookmark_file = os.path.join(dir_path_parent, 'bookmarks.json')
        component = BioImageITApp()

        component.get_widget().setWindowTitle("BioImageIT")
        component.get_widget().resize(800, 600)
        component.get_widget().showMaximized()
        component.get_widget().show()
    
        # Run the main Qt loop
        icon_path = os.path.join(dir_path, "theme", "dark", "icon.png")
        app.setWindowIcon(QIcon(icon_path))
        sys.exit(app.exec_())
        
    except Exception as ex:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("BioImageIT Connection Error")
        msg.setInformativeText(f'{str(ex)}.\nPlease update the configuration file')
        msg.setWindowTitle("BioImageIT Error")
        msg.exec_()  
        sys.exit()      

   