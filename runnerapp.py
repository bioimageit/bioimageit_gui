import os
import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

from bioimageit_core.config import ConfigAccess
from bioimageit_core.formats import FormatsAccess

from bioimageit_gui.runnerapp import BiRunnerApp
from bioimageit_gui.core.exceptions import CommandArgsError

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # load the settings
    process_xml = ""
    if len(sys.argv) > 1:
        process_xml = sys.argv[1]
    if process_xml == "":
        raise CommandArgsError("No processs XML file")

    # Create and show the component
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_parent = os.path.abspath(os.path.join(dir_path, os.pardir))
    ConfigAccess(os.path.join(dir_path_parent,'config.json'))
    FormatsAccess(ConfigAccess.instance().get('formats')['file'])

    component = BiRunnerApp(process_xml)
    # rec = QApplication.desktop().screenGeometry()
    # component.get_widget().resize(rec.width()/2, rec.height()/2)
    component.get_widget().show()
    
    # Run the main Qt loop
    stylesheet_path = os.path.join(dir_path, 'theme', 'dark', 'stylesheet.css')
    app.setStyleSheet("file:///" + stylesheet_path)
    icon_path = os.path.join(dir_path, "theme", "default", "icon.png")
    app.setWindowIcon(QIcon(icon_path))
    sys.exit(app.exec_())
