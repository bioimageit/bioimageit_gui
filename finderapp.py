import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication


sys.path.append("../bioimagepy")
from bioimagepy.config import ConfigAccess
from bioimageapp.finderapp import BiFinderApp

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
        
    # Create and show the component
    ConfigAccess('config.sample.json') 
    component = BiFinderApp()
    component.get_widget().show()
    
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "theme/dark/stylesheet.css")
    app.setWindowIcon(QIcon("theme/default/icon.png"))
    sys.exit(app.exec_())