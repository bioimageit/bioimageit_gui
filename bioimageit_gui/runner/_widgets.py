import os
import qtpy.QtCore
from qtpy.QtCore import Signal
from qtpy.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QComboBox, 
                               QPushButton, QVBoxLayout, QGridLayout, QLabel,
                               QCheckBox, QFileDialog, QTabWidget, QProgressBar,
                               QTextEdit, QSpinBox)
from bioimageit_core import ConfigAccess

from bioimageit_core.containers import Tool
from bioimageit_core.api import APIAccess

from bioimageit_framework.widgets import BiButtonPrimary
from bioimageit_framework.widgets.qtwidgets import QtFileSelectWidget
from bioimageit_gui.browser import get_experiment_selector_widget
from ._containers import BiRunnerContainer


class BiRunnerInputSingleWidget(QWidget):
    openViewSignal = Signal(str, str)

    def __init__(self, process_info: Tool, parent: QWidget = None):
        super().__init__(parent)
        self.info = process_info
        # create widget
        self.layout = QGridLayout()
        row = -1
        self.view_btns = []
        for inp in self.info.inputs:
            if inp.io == "input":
                row += 1
                nameLabel = QLabel(inp.name)
                descLabel = QLabel(inp.description)
                descLabel.setObjectName("bi-label")
                selectorWidget = QtFileSelectWidget(False, self)
                selectorWidget.id = row
                selectorWidget.TextChangedIdSignal.connect(self.showViewButton)
                viewButton = BiButtonPrimary('View')
                viewButton.connect('clicked', self.open_view)
                viewButton.content = inp.name
                viewButton.set_visible(False)
                self.view_btns.append(viewButton)
                self.layout.addWidget(nameLabel, row, 0)
                self.layout.addWidget(descLabel, row, 1)
                self.layout.addWidget(selectorWidget, row, 2)
                self.layout.addWidget(viewButton.widget, row, 3)
                nameLabel.setVisible(False)
        self.setLayout(self.layout)     

    def inputs(self) -> list:
        inps = []
        for row in range(self.layout.rowCount()):
            if self.layout.itemAtPosition(row, 0):
                nameLabel = self.layout.itemAtPosition(row, 0).widget()
                selectorWidget = self.layout.itemAtPosition(row, 2).widget()
                inps.append({"name": nameLabel.text(),
                             "uri": selectorWidget.text()})
        return inps 

    def showViewButton(self, id: int):
        button = self.layout.itemAtPosition(id, 3).widget()
        if button:
            button.setVisible(True)

    def open_view(self, emitter):   
        for row in range(self.layout.rowCount()):
            selectorWidget = self.layout.itemAtPosition(row, 2).widget()
            if selectorWidget:
                format_ = self.info.inputs[selectorWidget.id].type
                print("emit open view with", format_, ", ", selectorWidget.text())
                self.openViewSignal.emit(selectorWidget.text(), format_)


class BiRunnerInputDatasetFilterWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        filterButton = QPushButton(self.tr("Filter"))
        filterButton.setObjectName('btn-default-left')
        self.statusLabel = QLabel('OFF')
        self.statusLabel.setObjectName('bi-tool-filter-status')
        layout.addWidget(filterButton)
        layout.addWidget(self.statusLabel)
        self.setLayout(layout)
        filterButton.released.connect(self.showFilter)

        self.createFilterWidget()

    def createFilterWidget(self):
        self.filterWidget = QWidget()
        self.filterWidget.setVisible(False)
        filterLayout = QGridLayout()
        self.filterWidget.setLayout(filterLayout)
        
        tagLabel = QLabel(self.tr('Key'))
        operatorLabel = QLabel(self.tr('Operator'))
        valueLabel = QLabel(self.tr('Value'))

        self.tagWidget = QComboBox()    
        self.operatorWidget = QComboBox()
        self.operatorWidget.addItem("=")
        self.operatorWidget.addItem("<")
        self.operatorWidget.addItem(">")
        self.lineEdit = QLineEdit()
        
        cancelButton = QPushButton(self.tr("Cancel"))
        cancelButton.setObjectName('btn-default')
        validateButton = QPushButton(self.tr("Validate"))
        validateButton.setObjectName('btn-primary')

        cancelButton.released.connect(self.cancel)
        validateButton.released.connect(self.hideFilter)

        filterLayout.addWidget(tagLabel, 0, 0)
        filterLayout.addWidget(operatorLabel, 0, 1)
        filterLayout.addWidget(valueLabel, 0, 2)
        filterLayout.addWidget(self.tagWidget, 1, 0)
        filterLayout.addWidget(self.operatorWidget, 1, 1)
        filterLayout.addWidget(self.lineEdit, 1, 2)
        filterLayout.addWidget(cancelButton, 2, 1)
        filterLayout.addWidget(validateButton, 2, 2)

    def cancel(self):
        self.lineEdit.setText('')
        self.hideFilter()

    def hideFilter(self):
        self.filterWidget.setVisible(False)  
        if self.lineEdit.text() != '':
            self.statusLabel.setText("ON")
        else:
            self.statusLabel.setText("OFF")   

    def showFilter(self):
        self.filterWidget.setVisible(True)

    def filter(self):
        if self.lineEdit.text() == '':
            return ''
        else:    
            return self.tagWidget.currentText() + \
                   self.operatorWidget.currentText() + self.lineEdit.text()
 
    def setTags(self, tags: list):
        for i in range(self.tagWidget.count()):
            self.tagWidget.removeItem(0)
        self.tagWidget.addItems(tags)


class BiRunnerInputExperimentWidget(QWidget):
    def __init__(self, container: BiRunnerContainer, parent: QWidget = None):
        super().__init__(parent)
        self.container = container
        self.info = container.process_info

        # experiment browser
        self.browser_widget = get_experiment_selector_widget()
        self.browser_widget.widget.setVisible(False)
        self.browser_widget.connect('selected_experiment', self.update_experiment_path)

        # create widget
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)

        experimentLabel = QLabel("Experiment")
        experimentLabel.setObjectName('bi-label')
        self.experiment_dir_edit = QLineEdit()
        self.experiment_dir_edit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.experiment_browse_btn = QPushButton('...')
        self.experiment_browse_btn.setObjectName('btn-default')
        self.experiment_browse_btn.setMaximumWidth(40)
        self.experiment_browse_btn.released.connect(self.select_experiments)

        self.layout.addWidget(experimentLabel, 0, 1)
        self.layout.addWidget(self.experiment_dir_edit, 0, 2, 1, 1)
        self.layout.addWidget(self.experiment_browse_btn, 0, 3, 1, 1)

        outputDatasetLabel = QLabel("Output dataset name")
        outputDatasetLabel.setObjectName('bi-label')
        self.outputDatasetNameEdit = QLineEdit()
        self.outputDatasetNameEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.outputDatasetNameEdit.setText(self.info.id)
        self.layout.addWidget(outputDatasetLabel, 1, 1)
        self.layout.addWidget(self.outputDatasetNameEdit, 1, 2, 1, 1)

        row = 1
        self.inputs_count = 0
        for inp in self.info.inputs:
            if inp.io == "input":
                row += 1
                self.inputs_count += 1
                nameLabel = QLabel(inp.name)
                descLabel = QLabel(inp.description)
                descLabel.setObjectName("bi-label")
                selectorWidget = QComboBox()
                filterWidget = BiRunnerInputDatasetFilterWidget()
                filterWidget.setMaximumWidth(100)
                self.layout.addWidget(nameLabel, row, 0)
                self.layout.addWidget(descLabel, row, 1)
                self.layout.addWidget(selectorWidget, row, 2)
                self.layout.addWidget(filterWidget, row, 3)
                nameLabel.setVisible(False)
 
        self.setLayout(self.layout)    

    def select_experiments(self):
        self.browser_widget.widget.setVisible(True)   

    def update_experiment_path(self, emitter):
        self.experiment_dir_edit.setText(str(emitter.selected_name))
        self.browser_widget.widget.setVisible(False)  
        self.openExperiment(emitter.selected_path)

    def openExperiment(self, experiment_uri):
        if ConfigAccess.instance().config['metadata']['service'] == 'LOCAL':
            experiment_uri = os.path.join(experiment_uri, 'experiment.md.json')  

        datasets_text = ['data']
        datasets_name = ['data']
        datasets_origin = ['']
        tags = []

        experiment = APIAccess.instance().get_experiment(experiment_uri)
        self.container.experiment = experiment
        tags = experiment.keys
        for i in range(len(experiment.processed_datasets)):
            pdataset = APIAccess.instance().get_dataset_from_uri( experiment.processed_datasets[i].url)
            # get run
            runs = APIAccess.instance().get_dataset_runs(pdataset)
            if len(runs) > 0:
                run = runs[0]
                process = APIAccess.instance().get_tool_from_uri(run.process_uri)
                for output in process.outputs:
                    datasets_text.append(pdataset.name + ":" +
                                         output.description)
                    datasets_name.append(pdataset.name)
                    datasets_origin.append(output.name)
        idx = 1
        for inp in self.info.inputs:
            idx += 1
            if (self.layout.itemAtPosition(idx, 2)):
                # add datasets list to combobox
                widget = self.layout.itemAtPosition(idx, 2).widget()
                for i in range(widget.count()):  
                    widget.removeItem(0)
                for i in range(len(datasets_text)):    
                    widget.addItem(datasets_text[i]) 
                    widget.setItemData(i, [datasets_name[i],
                                           datasets_origin[i]])
                # add tags to filter combobox
                self.layout.itemAtPosition(idx, 3).widget().setTags(tags)       

    def output(self) -> str:
        return self.outputDatasetNameEdit.text()

    def inputs(self) -> list:
        inps = []
        offset = 2
        for row in range(self.inputs_count):
            nameLabel = self.layout.itemAtPosition(row+offset, 0).widget()
            selectorWidget = self.layout.itemAtPosition(row+offset, 2).widget()
            filterWidget = self.layout.itemAtPosition(row+offset, 3).widget()
            itemdata = selectorWidget.itemData(selectorWidget.currentIndex())
            datasetname = itemdata[0]
            dataset_origin = itemdata[1]
            inps.append({"name": nameLabel.text(), "dataset": datasetname,
                         "filter": filterWidget.filter(),
                         "origin_output_name": dataset_origin})
        return inps   
    

class BiRunnerParamWidget(QWidget):
    def __init__(self, process_info: Tool, parent: QWidget = None):
        super().__init__(parent) 
        self.info = process_info
        self.labels = dict() # <str, QLabel>
        self.widgets = dict() # <str, BiProcessInputWidget>

        self.layout = QGridLayout()

        advancedToggleButton = QCheckBox(self.tr("Advanced"), self)
        advancedToggleButton.setObjectName("bi-checkbox")
        advancedToggleButton.stateChanged.connect(self.showHideAdvanced)
        self.advancedMode = False
        self.layout.addWidget(advancedToggleButton, 0, 0)

        row = 0
        for parameter in self.info.inputs:
            if parameter.io == "param":
                row += 1
                titleLabel = QLabel(parameter.description)
                titleLabel.setObjectName("bi-label")
                titleLabel.setWordWrap(True)
                titleLabel.setMaximumWidth(150)
                self.labels[parameter.name] = titleLabel
                self.layout.addWidget(titleLabel, row, 0)

                if parameter.type == "integer":
                    valueEdit = BiProcessInputInt(self) 
                    valueEdit.build_help(parameter.help)
                    valueEdit.setKey(parameter.name)
                    valueEdit.setValue(parameter.value)
                    valueEdit.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = valueEdit

                    self.layout.addWidget(titleLabel, row, 0)
                    self.layout.addWidget(valueEdit, row, 1)

                elif parameter.type == "number" or parameter.type == "float"  or parameter.type == "string":
                    valueEdit = BiProcessInputValue(self) 
                    valueEdit.build_help(parameter.help)
                    valueEdit.setKey(parameter.name)
                    valueEdit.setValue(parameter.value)
                    valueEdit.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = valueEdit
                    self.layout.addWidget(titleLabel, row, 0)
                    self.layout.addWidget(valueEdit, row, 1)
                
                elif parameter.type == "select":
                    w = BiProcessInputSelect(self)
                    w.build_help(parameter.help)
                    w.setKey(parameter.name)
                    w.setContent(parameter.select_info)
                    w.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = w
                    self.layout.addWidget(titleLabel, row, 0)
                    self.layout.addWidget(w, row, 1)
        
                elif parameter.type == "file":
                    w = BiProcessInputBrowser(self, False)
                    w.setKey(parameter.name)
                    w.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = w
                    self.layout.addWidget(titleLabel, row, 0)
                    self.layout.addWidget(w, row, 1)

        self.setLayout(self.layout) 
        self.showHideAdvanced(0)

    def showHideAdvanced(self, adv: int):
        if adv > 0:
            self.advancedMode = True
        else:
            self.advancedMode = False

        for key in self.labels:
            label = self.labels[key]
            widget = self.widgets[key]

            if widget.isAdvanced() and self.advancedMode:
                label.setVisible(True)
                widget.setVisible(True) 
            elif widget.isAdvanced() and not self.advancedMode:
                label.setVisible(False)
                widget.setVisible(False) 

        # TODO: add here code to show/hide conditionnal advanced

    def parameters(self) -> list:
        parameters = []
        for key in self.labels:
            parameters.append(key)
            parameters.append(self.widgets[key].value())
        return parameters     


class BiRunnerExecWidget(QWidget):
    runSignal = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)   
        layout = QVBoxLayout()

        runButton = QPushButton(self.tr("Run"), self)
        runButton.released.connect(self.run)
        runButton.setObjectName("btn-primary")

        layout.addWidget(runButton)
        self.setLayout(layout)

    def run(self):
        self.runSignal.emit()    


class BiRunnerProgressWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)  

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.progressBar = QProgressBar() 
        self.toggle_btn = QCheckBox('Show run log')
        self.toggle_btn.setObjectName("bi-checkbox")
        self.toggle_btn.released.connect(self._toggle_log)
        self.logWidget = QTextEdit()
        self.logWidget.setReadOnly(True)
        self.logWidget.setVisible(False)

        layout.addWidget(self.progressBar)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.logWidget)

    def _toggle_log(self):
        if self.toggle_btn.isChecked():
            self.logWidget.setVisible(True)
        else:
            self.logWidget.setVisible(False)   

    def set_range(self, mini, maxi):
        self.progressBar.setRange(mini, maxi)

    def setProgress(self, progress: int):
        self.progressBar.setValue(progress)

    def setMessage(self, message: str):
        self.logWidget.append(message)           


# ///////////////////////////////////////////////// //
#                BiProcessInputWidget                //
# ///////////////////////////////////////////////// //
class BiProcessInputWidget(QWidget):
    def __init__(self, parent= QWidget):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)
        self._dataType = ''
        self._key = ''
        self._value = ''
        self._advanced = False

        self.help_label = QLabel()
        self.help_label.setVisible(False)

    def build_help(self, help_text):
        help_btn = QPushButton('?')
        help_btn.setMaximumWidth(30)
        help_btn.setObjectName('btn-default')
        self.help_label.setWordWrap(True)
        self.help_label.setText(help_text) 
        help_btn.released.connect(self.toggle_help)

        self.layout.addWidget(help_btn, 0, 0) 
        self.layout.addWidget(self.help_label, 1, 0, 1, 2)

    def toggle_help(self):
        if self.help_label.isVisible():
            self.help_label.setVisible(False)
        else:
            self.help_label.setVisible(True)    

    def datatype(self) -> str:
        return self._dataType

    def key(self) -> str:
        return self._key

    def value(self) -> str:
        return self._value

    def isAdvanced(self) -> bool:
        return self._advanced

    def setAdvanced(self, adv: bool):
        self._advanced = adv

    def setKey(self, key: str):
        self._key = key

    def setValue(self, value: str):
        self._value = value

    def setDatatype(self, datatype: str):
        self._dataType = datatype


# ///////////////////////////////////////////////// //
#                BiProcessInputInt                  //
# ///////////////////////////////////////////////// //
class BiProcessInputInt(BiProcessInputWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.valueEdit = QSpinBox(self)
        self.valueEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.layout.addWidget(self.valueEdit, 0, 1)
        self.valueEdit.valueChanged.connect(self.updateValue)

    def updateValue(self, value: int):
        self._value = value

    def setValue(self, value: int):
        self._value = value
        self.valueEdit.setValue(int(self._value))

# ///////////////////////////////////////////////// //
#                BiProcessInputValue                //
# ///////////////////////////////////////////////// //
class BiProcessInputValue(BiProcessInputWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.valueEdit = QLineEdit(self)
        self.valueEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.layout.addWidget(self.valueEdit, 0, 1)
        self.valueEdit.textChanged.connect(self.updateValue)


    def updateValue(self, value: str):
        self._value = value

    def setValue(self, value: str):
        self._value = value
        self.valueEdit.setText(self._value)
    

# ///////////////////////////////////////////////// //
#                BiProcessInputSelect
# ///////////////////////////////////////////////// //
class BiProcessInputSelect(BiProcessInputWidget):
    valueChanged = Signal(str, str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.conbobox = QComboBox(self)
        self.layout.addWidget(self.conbobox, 0, 1)
        self.conbobox.currentTextChanged.connect(self.updateValue)
        self.conbobox.currentTextChanged.connect(self.emitValueChanged)

    def emitValueChanged(self, value: str):
        self.valueChanged.emit(self._key, value)

    def setContent(self, content):
        for i in range(len(content.names)):
            name = content.names[i] 
            value = content.values[i] 
            self.conbobox.addItem(name, value)

    def updateValue(self, value: str):
        self._value = self.conbobox.itemData(self.conbobox.currentIndex())
        #self._value = value


# ///////////////////////////////////////////////// //
#                BiProcessInputBrowser
# ///////////////////////////////////////////////// //
class BiProcessInputBrowser(BiProcessInputWidget):
    def __init__(self, parent: QWidget, isDir: bool):
        super().__init__(parent)
        self.isDir = isDir
        self.pathEdit = QLineEdit(self)
        self.pathEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        button = QPushButton(self.tr("..."), self)
        button.setObjectName("btn-default")
        self.layout.insertWidget(0,self.pathEdit)
        self.layout.insertWidget(1,button)

        button.released.connect(self.browse)
        self.pathEdit.textChanged.connect(self.updateValue)

    def browse(self):
        if not self.isDir:
            file = QFileDialog.getOpenFileName(self, "open data", "", "")
            self.pathEdit.setText(file)
        else:
            dir = QFileDialog.getExistingDirectory(self)
            self.pathEdit.setText(dir)

    def updateValue(self, value: str):
        self._value = value
