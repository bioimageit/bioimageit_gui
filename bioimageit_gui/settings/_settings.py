import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QHBoxLayout, QLabel)

from bioimageit_framework.framework import BiComponent

from ._components import (BiAboutComponent, BiUpdateComponent, 
                          BiConfigComponent)
from ._containers import BiUpdateContainer, BiConfigContainer
from ._models import BiUpdateModel, BiConfigModel
from ._widgets import BiSettingsToolBar


class BiSettingsComponent(BiComponent):
    def __init__(self):
        super().__init__()
        self._object_name = 'BiSettingsComponent'

        # containers
        self.update_container = BiUpdateContainer()
        self.config_container = BiConfigContainer()

        # components
        self.about_compnent = BiAboutComponent()
        self.update_component = BiUpdateComponent(self.update_container)
        self.config_component = BiConfigComponent(self.config_container)
        self.cleaner_compnent = QLabel('Cleaner page is not yet implemented')
        
        # models
        self.config_model = BiConfigModel(self.config_container)
        self.update_model = BiUpdateModel(self.update_container)

        # Widget
        self.widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.widget.setLayout(layout)

        #toolbar = BiSettingsToolBar(['About', 'Update', 'Configuration', 'Cleaner'])
        toolbar = BiSettingsToolBar(['About', 'Update', 'Configuration'])
        toolbar.open.connect(self.update_view)
        toolbar.setFixedWidth(300)

        self.update_component.get_widget().setFixedWidth(500)

        layout.addWidget(toolbar, 0, qtpy.QtCore.Qt.AlignLeft)
        layout.addWidget(self.about_compnent.get_widget(), 1)
        layout.addWidget(self.update_component.get_widget(), 1, qtpy.QtCore.Qt.AlignHCenter)
        layout.addWidget(self.config_component.get_widget(), 1)
        layout.addWidget(self.cleaner_compnent, 1)
        self.update_view(0)
        toolbar.set_checked(0)

    def update_view(self, id: int):
        if id == 0:
            self.about_compnent.get_widget().setVisible(True)  
            self.update_component.get_widget().setVisible(False) 
            self.config_component.get_widget().setVisible(False) 
            self.cleaner_compnent.setVisible(False)
        elif id == 1:
            self.about_compnent.get_widget().setVisible(False)  
            self.update_component.get_widget().setVisible(True)
            self.config_component.get_widget().setVisible(False) 
            self.cleaner_compnent.setVisible(False)    
        elif id == 2:
            self.about_compnent.get_widget().setVisible(False) 
            self.update_component.get_widget().setVisible(False)  
            self.config_component.get_widget().setVisible(True) 
            self.cleaner_compnent.setVisible(False)    
        elif id == 3:
            self.about_compnent.get_widget().setVisible(False)  
            self.update_component.get_widget().setVisible(False) 
            self.config_component.get_widget().setVisible(False) 
            self.cleaner_compnent.setVisible(True)  
