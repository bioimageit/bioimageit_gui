import sys
import os
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication


sys.path.append("../bioimagepy")
from bioimagepy.config import ConfigAccess
from bioimageapp.finderapp import BiFinderApp

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
        
    # Create and show the component
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_parent = os.path.abspath(os.path.join(dir_path, os.pardir))
    ConfigAccess(os.path.join(dir_path_parent,'config.json')) 
    component = BiFinderApp()
    component.get_widget().show()
    
    # Run the main Qt loop
    stylesheet_path = os.path.join(dir_path, 'theme', 'dark', 'stylesheet.css')
    app.setStyleSheet("file:///" + stylesheet_path)
    icon_path = os.path.join(dir_path,"theme", "default", "icon.png" )
    app.setWindowIcon(QIcon(icon_path))
    sys.exit(app.exec_())