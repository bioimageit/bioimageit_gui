import os
import PySide2.QtCore
from PySide2.QtCore import Signal
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QComboBox, 
                               QPushButton, QVBoxLayout, QGridLayout, QLabel,
                               QCheckBox, QFileDialog, QTabWidget, QProgressBar,
                               QTextEdit)

from bioimageit_gui.core.widgets import BiButton, BiFileSelectWidget
from bioimageit_gui.runner.containers import BiRunnerContainer

from bioimageit_core.process import Process
from bioimageit_core.experiment import Experiment
from bioimageit_core.metadata.run import Run


class BiRunnerInputSingleWidget(QWidget):
    openViewSignal = Signal(str, str)

    def __init__(self, process_info: Process, parent: QWidget = None):
        super().__init__(parent)
        self.info = process_info.metadata
        # create widget
        self.layout = QGridLayout()
        row = -1
        for inp in self.info.inputs:
            if inp.io == "input":
                row += 1
                nameLabel = QLabel(inp.name)
                descLabel = QLabel(inp.description)
                descLabel.setObjectName("BiProcessDataSelectorWidgetLabel")
                selectorWidget = BiFileSelectWidget(False, self)
                selectorWidget.id = row
                selectorWidget.TextChangedIdSignal.connect(self.showViewButton)
                viewButton = BiButton('View')
                viewButton.clickedContent.connect(self.openView)
                viewButton.setObjectName('btnPrimary')
                viewButton.content = inp.name
                viewButton.setVisible(False)
                self.layout.addWidget(nameLabel, row, 0)
                self.layout.addWidget(descLabel, row, 1)
                self.layout.addWidget(selectorWidget, row, 2)
                self.layout.addWidget(viewButton, row, 3)
                nameLabel.setVisible(False)
        self.setLayout(self.layout)     

    def inputs(self) -> list:
        inps = []
        for row in range(self.layout.rowCount()):
            nameLabel = self.layout.itemAtPosition(row, 0).widget()
            selectorWidget = self.layout.itemAtPosition(row, 2).widget()
            inps.append({"name": nameLabel.text(),
                         "uri": selectorWidget.text()})
        return inps 

    def showViewButton(self, id: int):
        button = self.layout.itemAtPosition(id, 3).widget()
        if button:
            button.setVisible(True)

    def openView(self, input_name):   
        for row in range(self.layout.rowCount()):
            selectorWidget = self.layout.itemAtPosition(row, 2).widget()
            if selectorWidget:
                format_ = self.info.inputs[selectorWidget.id].type
                print("emit open view with", format_, ", ", selectorWidget.text())
                self.openViewSignal.emit(selectorWidget.text(), format_)


class BiRunnerInputFolderWidget(QWidget):
    def __init__(self, process_info: Process, parent: QWidget = None):
        super().__init__(parent)
        self.info = process_info.metadata
        # create widget
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        row = -1
        self.inputs_count = 0
        for inp in self.info.inputs:
            if inp.io == "input":
                row += 1
                self.inputs_count += 1
                nameLabel = QLabel(inp.name)
                descLabel = QLabel(inp.description)
                descLabel.setObjectName("BiProcessDataSelectorWidgetLabel")
                selectorWidget = BiFileSelectWidget(True, self)
                filterWidget = BiRunnerInputFolderFilterWidget()
                self.layout.addWidget(nameLabel, row, 0)
                self.layout.addWidget(descLabel, row, 1)
                self.layout.addWidget(selectorWidget, row, 2)
                self.layout.addWidget(filterWidget, row, 3)
                nameLabel.setVisible(False)

        outputLabel = QLabel(self.tr("Output dir"))
        outputLabel.setObjectName("BiProcessDataSelectorWidgetLabel")
        self.outputSelector = BiFileSelectWidget(True, self) 
        self.layout.addWidget(outputLabel, self.inputs_count, 1)  
        self.layout.addWidget(self.outputSelector, self.inputs_count, 2)   
        self.setLayout(self.layout)     

    def inputs(self) -> list:
        inps = []
        for row in range(self.inputs_count):
            nameLabel = self.layout.itemAtPosition(row, 0).widget()
            selectorWidget = self.layout.itemAtPosition(row, 2).widget()
            filterWidget = self.layout.itemAtPosition(row, 3).widget()
            inps.append({"name": nameLabel.text(), "uri": selectorWidget.text(),
                         "filter": filterWidget.filter()})
        return inps 

    def output(self):
        return self.outputSelector.text()    


class BiRunnerInputFolderFilterWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        filterButton = QPushButton(self.tr("Filter"))
        filterButton.setObjectName('btnDefaultLeft')
        self.statusLabel = QLabel('OFF')
        self.statusLabel.setObjectName('BiProcessDataFilterWidgetStatus')
        layout.addWidget(filterButton)
        layout.addWidget(self.statusLabel)
        self.setLayout(layout)
        filterButton.released.connect(self.showFilter)

        self.createFilterWidget()

    def createFilterWidget(self):
        self.filterWidget = QWidget()
        self.filterWidget.setObjectName('BiWidget')
        self.filterWidget.setVisible(False)
        filterLayout = QGridLayout()
        self.filterWidget.setLayout(filterLayout)
        
        titleLabel = QLabel(self.tr('File name: '))
        self.selectWidget = QComboBox()
        self.selectWidget.addItem("Starts with")
        self.selectWidget.addItem("Contains")
        self.selectWidget.addItem("Ends with")
        self.lineEdit = QLineEdit()
        
        cancelButton = QPushButton(self.tr("Cancel"))
        cancelButton.setObjectName('btnDefault')
        validateButton = QPushButton(self.tr("Validate"))
        validateButton.setObjectName('btnPrimary')

        cancelButton.released.connect(self.cancel)
        validateButton.released.connect(self.hideFilter)

        filterLayout.addWidget(titleLabel, 0, 0)
        filterLayout.addWidget(self.selectWidget, 0, 1)
        filterLayout.addWidget(self.lineEdit, 0, 2)
        filterLayout.addWidget(cancelButton, 1, 1)
        filterLayout.addWidget(validateButton, 1, 2)

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
        if self.selectWidget.currentText() == 'Starts with':
            return '^' + self.lineEdit.text()
        if self.selectWidget.currentText() == 'Contains':
            return self.lineEdit.text() 
        if self.selectWidget.currentText() == 'Ends with':
            return "\\"+self.lineEdit.text()+'$'   


class BiRunnerInputDatasetFilterWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        filterButton = QPushButton(self.tr("Filter"))
        filterButton.setObjectName('btnDefaultLeft')
        self.statusLabel = QLabel('OFF')
        self.statusLabel.setObjectName('BiProcessDataFilterWidgetStatus')
        layout.addWidget(filterButton)
        layout.addWidget(self.statusLabel)
        self.setLayout(layout)
        filterButton.released.connect(self.showFilter)

        self.createFilterWidget()

    def createFilterWidget(self):
        self.filterWidget = QWidget()
        self.filterWidget.setObjectName('BiWidget')
        self.filterWidget.setVisible(False)
        filterLayout = QGridLayout()
        self.filterWidget.setLayout(filterLayout)
        
        tagLabel = QLabel(self.tr('Tag'))
        operatorLabel = QLabel(self.tr('Operator'))
        valueLabel = QLabel(self.tr('Value'))

        self.tagWidget = QComboBox()    
        self.operatorWidget = QComboBox()
        self.operatorWidget.addItem("=")
        self.operatorWidget.addItem("<")
        self.operatorWidget.addItem(">")
        self.lineEdit = QLineEdit()
        
        cancelButton = QPushButton(self.tr("Cancel"))
        cancelButton.setObjectName('btnDefault')
        validateButton = QPushButton(self.tr("Validate"))
        validateButton.setObjectName('btnPrimary')

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
        self.info = container.process_info.metadata

        # create widget
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)

        experimentLabel = QLabel("Experiment dir")
        self.experimentEdit = BiFileSelectWidget(True, self)
        self.experimentEdit.TextChangedSignal.connect(self.openExperiment)
        self.layout.addWidget(experimentLabel, 0, 1)
        self.layout.addWidget(self.experimentEdit, 0, 2, 1, 2)

        outputDatasetLabel = QLabel("Output dataset name")
        self.outputDatasetNameEdit = QLineEdit()
        self.outputDatasetNameEdit.setText(self.info.id)
        self.layout.addWidget(outputDatasetLabel, 1, 1)
        self.layout.addWidget(self.outputDatasetNameEdit, 1, 2, 1, 2)

        row = 1
        self.inputs_count = 0
        for inp in self.info.inputs:
            if inp.io == "input":
                row += 1
                self.inputs_count += 1
                nameLabel = QLabel(inp.name)
                descLabel = QLabel(inp.description)
                descLabel.setObjectName("BiProcessDataSelectorWidgetLabel")
                selectorWidget = QComboBox()
                filterWidget = BiRunnerInputDatasetFilterWidget()
                filterWidget.setMaximumWidth(100)
                self.layout.addWidget(nameLabel, row, 0)
                self.layout.addWidget(descLabel, row, 1)
                self.layout.addWidget(selectorWidget, row, 2)
                self.layout.addWidget(filterWidget, row, 3)
                nameLabel.setVisible(False)
 
        self.setLayout(self.layout)    

    def openExperiment(self):
        experiment_uri = os.path.join(self.experimentEdit.text(),
                                      'experiment.md.json')
        datasets_text = ['data']
        datasets_name = ['data']
        datasets_origin = ['']
        tags = []
        if os.path.isfile(experiment_uri):
            experiment = Experiment(experiment_uri)
            self.container.experiment = experiment
            tags = experiment.metadata.tags
            for i in range(experiment.get_processed_datasets_size()):
                pdataset = experiment.get_processed_dataset_at(i)
                # get run
                run_uri = os.path.join(os.path.dirname(pdataset.md_uri),
                                       'run.md.json')
                if os.path.isfile(run_uri):
                    run = Run(run_uri)
                    process = Process(run.metadata.process_uri)
                    for output in process.metadata.outputs:
                        datasets_text.append(pdataset.metadata.name + ":" +
                                             output.description)
                        datasets_name.append(pdataset.metadata.name)
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
    def __init__(self, process_info: Process, parent: QWidget = None):
        super().__init__(parent) 
        self.info = process_info.metadata
        self.labels = dict() # <str, QLabel>
        self.widgets = dict() # <str, BiProcessInputWidget>

        self.layout = QGridLayout()

        advancedToggleButton = QCheckBox(self.tr("Advanced"), self)
        advancedToggleButton.setObjectName("BiCheckBoxNegative")
        advancedToggleButton.stateChanged.connect(self.showHideAdvanced)
        self.advancedMode = False
        self.layout.addWidget(advancedToggleButton, 0, 0)

        row = 0
        for parameter in self.info.inputs:
            if parameter.io == "param":
                row += 1
                titleLabel = QLabel(parameter.description)
                titleLabel.setObjectName("BiProcessDataSelectorWidgetLabel")
                titleLabel.setWordWrap(True)
                titleLabel.setMaximumWidth(150)
                self.labels[parameter.name] = titleLabel
                self.layout.addWidget(titleLabel, row, 0)

                if parameter.type == "integer" or parameter.type == "number" \
                        or parameter.type == "string":
                    valueEdit = BiProcessInputValue(self) 
                    valueEdit.setKey(parameter.name)
                    valueEdit.setValue(parameter.value)
                    valueEdit.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = valueEdit
                    self.layout.addWidget(titleLabel, row, 0)
                    self.layout.addWidget(valueEdit, row, 1)
                
                elif parameter.type == "select":
                    w = BiProcessInputSelect(self)
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
            #p = dict()
            #p['name'] = key
            #p['value'] = self.widgets[key].value()
            #parameters.append(p)
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
        runButton.setObjectName("btnPrimaryNegative")

        layout.addWidget(runButton)
        self.setLayout(layout)

    def run(self):
        self.runSignal.emit()    


class BiRunnerProgressWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)  

        self.setObjectName('BiWidget')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.progressBar = QProgressBar() 
        self.logWidget = QTextEdit()
        self.logWidget.setReadOnly(True)

        layout.addWidget(self.progressBar)
        layout.addWidget(self.logWidget)

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
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self._dataType = ''
        self._key = ''
        self._value = ''
        self._advanced = False

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
#                BiProcessInputValue                //
# ///////////////////////////////////////////////// //
class BiProcessInputValue(BiProcessInputWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.valueEdit = QLineEdit(self)
        self.layout.insertWidget(0,self.valueEdit)
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
        self.layout.insertWidget(0, self.conbobox)
        self.conbobox.currentTextChanged.connect(self.updateValue)
        self.conbobox.currentTextChanged.connect(self.emitValueChanged)

    def emitValueChanged(self, value: str):
        self.valueChanged.emit(self._key, value)

    def setContent(self, content: str):
        for c in content.values:
            self.conbobox.addItem(c)

    def setContentList(self, content: list):
        for c in content:
            item = c.replace(" ", "")
            if item != '':
                self.conbobox.addItem(item)

    def updateValue(self, value: str):
        self._value = value


# ///////////////////////////////////////////////// //
#                BiProcessInputBrowser
# ///////////////////////////////////////////////// //
class BiProcessInputBrowser(BiProcessInputWidget):
    def __init__(self, parent: QWidget, isDir: bool):
        super().__init__(parent)
        self.isDir = isDir
        self.pathEdit = QLineEdit(self)
        button = QPushButton(self.tr("..."), self)
        button.setObjectName("btnDefault")
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
