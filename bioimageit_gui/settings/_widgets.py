from qtpy.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QPushButton
import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, 
                            QGroupBox, QLabel, QLineEdit, 
                            QComboBox)

from bioimageit_gui.core.widgets import BiButton

class BiConfigWidget(QWidget):
    cancel = Signal()
    validate = Signal()

    def __init__(self, config):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
            
        # User
        user_box = QGroupBox('User')
        user_box_layout = QGridLayout()
        user_box.setLayout(user_box_layout)
        # username
        user_box_layout.addWidget(QLabel('Username'), 0, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setText(config.get('user')['name'])
        user_box_layout.addWidget(self.username_edit, 0, 1)
        # workspace
        user_box_layout.addWidget(QLabel('Workspace'), 1, 0)
        self.workspace_edit = QLineEdit()
        self.workspace_edit.setText(config.get('workspace'))
        user_box_layout.addWidget(self.workspace_edit, 1, 1)
        # installation directory
        user_box_layout.addWidget(QLabel('Installation directory'), 2, 0)
        self.install_dir_edit = QLineEdit()
        self.install_dir_edit.setText(config.get('install_dir'))
        user_box_layout.addWidget(self.install_dir_edit, 2, 1)
    
        # Data management
        data_management_box = QGroupBox('Data management')
        data_management_layout = QGridLayout()
        data_management_box.setLayout(data_management_layout)
        data_management_layout.addWidget(QLabel('Service'), 0, 0)
        self.data_management_services_combo = QComboBox() 
        self.data_management_services_combo.addItems(['LOCAL'])
        data_management_layout.addWidget(self.data_management_services_combo, 0, 1)

        # Formats
        formats_box = QGroupBox('Formats')
        formats_layout = QGridLayout()
        formats_box.setLayout(formats_layout)
        formats_layout.addWidget(QLabel('dictionary'), 0, 0)
        self.formats_dict_edit = QLineEdit()
        self.formats_dict_edit.setText(config.get('formats')['file'])
        formats_layout.addWidget(self.formats_dict_edit, 0, 1)

        # Tools
        tools_box = QGroupBox('Tools')
        tools_layout = QGridLayout()
        tools_box.setLayout(tools_layout)
        # service
        tools_layout.addWidget(QLabel('Service'), 0, 0)
        self.tools_services_combo = QComboBox() 
        self.tools_services_combo.addItems(['LOCAL'])
        tools_layout.addWidget(self.tools_services_combo, 0, 1)
        # wrappers dir
        tools_layout.addWidget(QLabel('Wrappers directory'), 1, 0)
        self.wrappers_dir_edit = QLineEdit()
        self.wrappers_dir_edit.setText(config.get('process')['xml_dirs'][0])
        tools_layout.addWidget(self.wrappers_dir_edit, 1, 1)
        # categories
        tools_layout.addWidget(QLabel('Categories'), 2, 0)
        self.categories_edit = QLineEdit()
        self.categories_edit.setText(config.get('process')['categories'])
        tools_layout.addWidget(self.categories_edit, 2, 1)
        # tools
        tools_layout.addWidget(QLabel('Tools'), 3, 0)
        self.tools_edit = QLineEdit()
        self.tools_edit.setText(config.get('process')['tools'])
        tools_layout.addWidget(self.tools_edit, 3, 1)
        # Fiji
        tools_layout.addWidget(QLabel('Fiji'), 4, 0)
        self.fiji_edit = QLineEdit()
        self.fiji_edit.setText(config.get('fiji'))
        tools_layout.addWidget(self.fiji_edit, 4, 1)

        # Runner
        runner_box = QGroupBox('Runner')
        runner_layout = QGridLayout()
        runner_box.setLayout(runner_layout)
        # service
        self.runner_combo = QComboBox() 
        self.runner_combo.addItems(['CONDA'])
        runner_layout.addWidget(QLabel('Service'), 0, 0)
        runner_layout.addWidget(self.runner_combo, 0, 1)
        # conda dir
        runner_layout.addWidget(QLabel('Conda directory'), 1, 0)
        self.conda_dir_edit = QLineEdit()
        self.conda_dir_edit.setText(config.get('runner')['conda_dir'])
        runner_layout.addWidget(self.conda_dir_edit, 1, 1)

        # buttons
        btns_widget = QWidget()
        btns_layout = QHBoxLayout()
        btns_widget.setLayout(btns_layout)
        btn_validate = QPushButton('Save')
        btn_validate.setObjectName('btnPrimary')
        btn_validate.released.connect(self.emit_validate)
        btn_cancel = QPushButton('Cancel')
        btn_cancel.setObjectName('btnDefault')
        btn_cancel.released.connect(self.emit_cancel)
        btns_layout.addWidget(btn_cancel, 1, qtpy.QtCore.Qt.AlignRight)
        btns_layout.addWidget(btn_validate, 0, qtpy.QtCore.Qt.AlignRight)

        layout.addWidget(user_box)
        layout.addWidget(data_management_box)
        layout.addWidget(formats_box)
        layout.addWidget(tools_box)
        layout.addWidget(runner_box)
        layout.addWidget(btns_widget)

    def emit_validate(self):
        self.validate.emit()

    def emit_cancel(self):
        self.cancel.emit()    

    def reload(self, config):
        self.username_edit.setText(config.get('user')['name'])
        self.workspace_edit.setText(config.get('workspace'))
        self.install_dir_edit.setText(config.get('install_dir'))
        self.formats_dict_edit.setText(config.get('formats')['file'])
        self.wrappers_dir_edit.setText(config.get('process')['xml_dirs'][0])
        self.categories_edit.setText(config.get('process')['categories'])
        self.tools_edit.setText(config.get('process')['tools'])
        self.fiji_edit.setText(config.get('fiji'))
        self.conda_dir_edit.setText(config.get('runner')['conda_dir'])

    def get_config(self):
        config = {}
        config['user'] = {'name': self.username_edit.text()}
        config['workspace'] = self.workspace_edit.text()
        config['install_dir'] = self.install_dir_edit.text()
        config['metadata'] = {'service': self.data_management_services_combo.currentText()}
        config['formats'] = {'file': self.formats_dict_edit.text()}
        config['process'] = {'service': self.tools_services_combo.currentText(),
                              'xml_dirs': [self.wrappers_dir_edit.text()],
                              'categories': self.categories_edit.text(),
                              'tools': self.tools_edit.text()
                            }
        config['fiji'] = self.fiji_edit.text()
        config['runner'] = {'service': self.runner_combo.currentText(),
                            'conda_dir': self.conda_dir_edit.text()
                           }                  
        return config                   


class BiSettingsToolBar(QWidget):
    open = Signal(int)

    def __init__(self, items=[]):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(2, 7, 2, 7)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)
        self.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        self.setObjectName('BiVerticalBar')
        self.layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop)
        self.buttons = []

        self.id_count = -1
        for item in items:    
            self.add_item(item)

    def add_item(self, title: str):
        btn_item = BiButton(title)
        self.id_count += 1
        btn_item.setCheckable(True)
        btn_item.setAutoExclusive(True)
        btn_item.id = self.id_count
        btn_item.clickedId.connect(self.emit_clicked)
        btn_item.setObjectName('BiVerticalBarButton')
        self.buttons.append(btn_item)
        self.layout.insertWidget(self.layout.count()-1, btn_item, 0, qtpy.QtCore.Qt.AlignTop)

    def set_checked(self, id):
        for btn in self.buttons:
            if btn.id == id:
                btn.setChecked(True)

    def emit_clicked(self, id: int):
        self.open.emit(id)        
