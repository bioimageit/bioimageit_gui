from bioimageit_framework.framework.framework import BiConnectome
import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                            QMessageBox, QLabel, QCheckBox, QProgressBar)

from bioimageit_core import ConfigAccess

from bioimageit_framework.framework import BiComponent, BiConnectome

from ._containers import BiUpdateContainer, BiConfigContainer
from ._widgets import BiConfigWidget


class BiAboutComponent(BiComponent):
    def __init__(self):

        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)

        label = QLabel()
        label.setObjectName('bi-about')
        label.setWordWrap(True)
        layout.addWidget(label, 0, qtpy.QtCore.Qt.AlignHCenter)
        label.setText('<span><p>BioImageIT v0.1.0</p></span><p>BioImageIT is an open source software funded by France-BioImaging : <a href="https://bioimageit.github.io">https://bioimageit.github.io</a></p>')


class BiUpdateComponent(BiComponent):
    def __init__(self, container: BiUpdateContainer):
        super().__init__()
        self._object_name = 'BiConfigComponent'
        self.container = container
        BiConnectome.connect(container, self)

        self.widget = QWidget()
        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        self.checkbox_bioimageit = QCheckBox("Update BioImageIT")
        self.checkbox_bioimageit.setObjectName("BiCheckBoxNegative")
        self.checkbox_bioimageit.setChecked(True)
        self.checkbox_toolboxes = QCheckBox("Update Toolboxes")
        self.checkbox_toolboxes.setObjectName("BiCheckBoxNegative")
        self.checkbox_toolboxes.setChecked(True)

        update_btn = QPushButton('Update')
        update_btn.setObjectName('btn-primary')
        update_btn.released.connect(self.update_clicked)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        layout.addWidget(self.checkbox_bioimageit, 0, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(self.checkbox_toolboxes, 0, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(update_btn, 0, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(self.progress_bar, 0, qtpy.QtCore.Qt.AlignTop)
        layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop)
        
    def update_clicked(self):
        self.container.update_bioimageit = self.checkbox_bioimageit.isChecked()
        self.container.update_toolboxes = self.checkbox_toolboxes.isChecked()
        self.container.action_update_clicked()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)

    def callback_update_finished(self, emitter):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        msgBox = QMessageBox()
        msgBox.setText("BioImageIT is up to date. Please restart BioImageIT to use the new version.")
        msgBox.exec()             
  

class BiConfigComponent(BiComponent):
    def __init__(self, container: BiConfigContainer):
        super().__init__()
        self._object_name = 'BiConfigComponent'
        self.container = container
        BiConnectome.connect(container, self) 

        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)

        self.config_widget = BiConfigWidget(ConfigAccess.instance().config)
        self.config_widget.cancel.connect(self.reload)
        self.config_widget.validate.connect(self.save)
        self.config_widget.setMinimumWidth(500)
        layout.addWidget(self.config_widget, 0, qtpy.QtCore.Qt.AlignHCenter)

    def reload(self):
        self.config_widget.reload(ConfigAccess.instance().config)

    def save(self):
        self.container.action_config_edited(None, self.config_widget.get_config())        

    def callback_config_saved(self, emitter):
        msgBox = QMessageBox()
        msgBox.setText("The new configuration has been saved. You may need to restart the application.")
        msgBox.exec()
