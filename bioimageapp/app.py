import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from framework import BiComponent, BiContainer

class bioImageApp(BiComponent):
    def __init__(self):
        super(bioImageApp, self).__init__()
        self._object_name = 'bioImageApp'

        # container

        # model

        # components

        # connections

        # crete the widget
        self.widget = QWidget()
        self.widget.setObjectName('bioImageApp')
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        layout.addWidget(QLabel('Hello world!'))
        

    def update(self, container: BiContainer):
        pass   
   
    def get_widget(self):
        return self.widget 

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = bioImageApp()
    form.get_widget().show()
    # Run the main Qt loop
    app.setStyleSheet("file:///" + "bioimageapp/theme/stylesheet.css")
    sys.exit(app.exec_())