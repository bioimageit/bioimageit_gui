import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication


sys.path.append("../bioimagepy")
from bioimagepy.config import ConfigAccess

from bioimageapp.runnerapp import BiRunnerApp

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # load the settings
    process_xml = ""
    if len(sys.argv) > 1:
        processesDir = sys.argv[1]
    if process_xml == "":
        process_xml = "../bioimagepy/tests/test_processes_local/svdeconv/svdeconv2D.xml"
    #if process_xml == "":
    #    raise CommandArgsError("No processs XML file")

    
    # Create and show the component
    ConfigAccess('config.sample.json') 
    component = BiRunnerApp(process_xml)
    component.get_widget().show()
    
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "theme/default/stylesheet.css")
    app.setWindowIcon(QIcon("theme/default/icon.png"))
    sys.exit(app.exec_())