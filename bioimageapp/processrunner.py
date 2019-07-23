from bioimagepy.process import BiProcess, BiProcessInfo
import bioimagepy.process as processpy
import bioimagepy.runner as runnerpy
from bioimagepy.core import BiProgressObserver

import PySide2.QtCore
from PySide2.QtCore import Signal, QThread, QObject
from PySide2.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QSplitter, 
                               QScrollArea, QLabel, QGridLayout, QComboBox,
                               QPushButton, QLineEdit, QCheckBox, QFileDialog,
                               QHBoxLayout, QProgressBar, QTextEdit)

from framework import BiStates, BiAction, BiContainer, BiModel, BiComponent
from experiment import BiExperimentStates, BiExperimentContainer
from widgets import BiWebBrowser, BiHideableWidget

class BiProcessMultiEditorStates(BiStates):
    ProcessAdded = "BiProcessMultiEditorContainer::ProcessAdded"


class BiProcessMultiEditorContainer(BiContainer):
    
    def __init__(self):
        super(BiProcessMultiEditorContainer, self).__init__()
        self._object_name = 'BiProcessMultiEditorContainer'

        #states
        self.states = BiProcessMultiEditorStates

        # data
        self.processes = []
        self.curentProcess = -1

    def processAdd(self, info: BiProcess):  
        self.processes.append(info)

    def processAt(self, i: int):
        return self.processes[i]

    def processesCount(self) -> int:
        return len(self.processes)

    def processesClear(self):
        self.processes.clear()

    def lastAddedProcess(self) -> BiProcess:
        return self.processes[len(self.processes) - 1]


class BiProcessEditorStates(BiStates):
    ProcessInfoLoaded = "BiProcessEditorContainer::ProcessInfoLoaded"
    RunProcess = "BiProcessEditorContainer::RunProcess"
    ProgressChanged = "BiProcessEditorContainer::ProgressChanged"


class BiProcessEditorContainer(BiContainer):

    def __init__(self):
        super(BiProcessEditorContainer, self).__init__()
        self._object_name = 'BiProcessEditorContainer'

        # states
        self.states = BiProcessEditorStates()

        # data
        self.processInfo = None
        self.selectedDataList = None
        self.parametersList = []
        self.progress = 0
        self.progressMessage = ''

    def setProcessInfo(self, info: str):
        self.processInfo = info    

    def setParameters(self, parameters: list):
        self.parametersList = parameters  

    def setSelectedData(self, data: list):
        self.selectedDataList = data   

    def setProgress(self, progress: int, message: str):
        self.progress = progress
        self.progressMessage = message


class BiProcessMultiEditorModel(BiModel):
    def __init__(self, container: BiProcessMultiEditorContainer):
        super(BiProcessMultiEditorModel, self).__init__()
        self._object_name = 'BiProcessMultiEditorModel'
        self.container = container
        self.container.register(self)  

    def update(self, action: BiAction):
        pass

class BiProcessEditorModel(BiModel):
    def __init__(self, container: BiProcessEditorContainer, experimentContainer: BiExperimentContainer):
        super(BiProcessEditorModel, self).__init__()
        self._object_name = 'BiProcessEditorModel'
        self.container = container
        self.container.register(self)  
        self.experimentContainer = experimentContainer
        self.experimentContainer.register(self)
        self.runThread = BiProcessRunThread()
        self.runThread.progressSignal.connect(self.notifyProgress)

    def update(self, action: BiAction):
        if action.state == BiProcessEditorStates.RunProcess:
            self.runProcess()

    def runProcess(self):
        self.runThread.experiment = self.experimentContainer.experiment
        self.runThread.processInfo = self.container.processInfo
        self.runThread.parametersList = self.container.parametersList
        self.runThread.selectedDataList = self.container.selectedDataList
        self.runThread.start()

    def notifyProgress(self, progress: dict):
        self.progress(progress['progress'], progress['message'])

    def progress(self, pourcentage: int, message: str):
        self.container.setProgress(pourcentage, message)
        self.container.emit(BiProcessEditorStates.ProgressChanged)
        if pourcentage == 100 :
            self.experimentContainer.emit(BiExperimentStates.NewProcessedDataSet)    

class BiProcessRunObserver(QObject):
    progressSignal = Signal(dict)

    def __init__(self):
        super().__init__()
        self._objectname = "BiProcessRunObserver"  

    def notify(self, data: dict):
        self.progressSignal.emit(data)

class BiProcessRunThread(QThread):
    progressSignal = Signal(dict)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.experiment = None
        self.processInfo = None
        self.parametersList = []
        self.selectedDataList = []

        self.runObserver = BiProcessRunObserver()
        self.runObserver.progressSignal.connect(self.emitProgress)

    def emitProgress(self, progress: dict):
        self.progressSignal.emit(progress)    

    def run(self): 
        # instanciate runner
        runner = runnerpy.BiRunnerExperiment(self.experiment) 
        runner.add_observer(self.runObserver)

        # set process and parameters
        params = []
        for p in self.parametersList:
            params.append(p["name"])
            params.append(p["value"])
        runner.set_process(self.processInfo.xml_file_url, *params) 

        # set inputs
        for data in self.selectedDataList:
            _id = data['id']
            
            _dataset_name = ''
            _data_name = ''

            _names = data['name'].split(':')
            if len(_names) == 2:
                _dataset_name = _names[0]  
                _data_name = _names[1] 
            else:
                _dataset_name = data['name']    

            _query = ''
            for _filter in data['filters']:
                _query += _filter['name'] + _filter['operator'] + _filter['value']
            
            runner.add_input(_id, _dataset_name, _query, _data_name)

        #run
        runner.run()  

        # final progress
        progress = dict()
        progress["progress"] = 100
        progress["message"] = 'done'
        self.progressSignal.emit(progress) 

class BiProcessMultiEditorToolBarComponent(BiComponent):
    def __init__(self, container: BiProcessMultiEditorContainer):
        super().__init__()
        self._object_name = "BiProcessMultiEditorToolBarComponent"
        self.container = container
        self.container.register(self)
        self.widget = QWidget()

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget    


class BiProcessEditorComponent(BiComponent):
    def __init__(self, container: BiProcessEditorContainer, experimentContainer: BiExperimentContainer):
        super(BiProcessEditorComponent, self).__init__()
        self._object_name = 'BiProcessMultiEditorComponent'
        self.editorContainer = container
        self.editorContainer.register(self)
        self.experimentContainer = experimentContainer
        self.experimentContainer.register(self)

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(layout)

        splitter = QSplitter(self.widget)
        layout.addWidget(splitter)

        # doc view
        self.docWidget = BiWebBrowser(self.widget)
        splitter.addWidget(self.docWidget)

        # exec view
        execWidget = QWidget()
        execWidget.setObjectName("BiWidgetNegative")
        execScrollArea = QScrollArea()
        execScrollArea.setMinimumWidth(300)
        execScrollArea.setWidgetResizable(True)
        execScrollArea.setWidget(execWidget)
        self.execLayout = QVBoxLayout()
        execWidget.setLayout(self.execLayout)
        splitter.addWidget(execScrollArea)
        splitter.setStretchFactor(0,1)
        splitter.setStretchFactor(1,3)

    def update(self, action: BiAction):
        if action.state == BiProcessEditorStates.ProcessInfoLoaded:
            self.docWidget.setHomePage(self.editorContainer.processInfo.help, True)
            self.buildExecWidget()

        if action.state == BiProcessEditorStates.ProgressChanged:
            self.runWidget.setProgress(self.editorContainer.progress)
            self.runWidget.setProgressMessage(self.editorContainer.progressMessage)
            if self.editorContainer.progress == 100:
                self.runWidget.setRunFinished()

    def get_experiment_data_list(self):

        data_list = ['data:data']  
        experiment = self.experimentContainer.experiment
        for i in range(experiment.processeddatasets_size()):
            processeddataset = experiment.processeddataset(i)
            parser = processpy.BiProcessParser(processeddataset.process_url())
            process_info = parser.parse()
            for output in process_info.outputs:
                data_list.append(processeddataset.name() + ':' + output.description)

        return data_list       
                

    def buildExecWidget(self):

        processInfo = self.editorContainer.processInfo
        
        # inputs gui
        inputLabel = QLabel(self.widget.tr("Inputs"))
        inputLabel.setObjectName("BiLabelFormHeader1Negative")

        self.dataSelectorWidget = BiProcessDataSelectorWidget(processInfo, self.get_experiment_data_list(), self.experimentContainer.experiment.tags())

        self.execLayout.addWidget(inputLabel, 0, PySide2.QtCore.Qt.AlignTop)
        self.execLayout.addWidget(self.dataSelectorWidget, 0, PySide2.QtCore.Qt.AlignTop)

        # parameters gui
        parametersLabel = QLabel(self.widget.tr("Parameters"))
        parametersLabel.setObjectName("BiLabelFormHeader1Negative")
        self.parametersSelectorWidget = BiProcessParameterSelectorWidget(processInfo)
        self.execLayout.addWidget(parametersLabel, 0, PySide2.QtCore.Qt.AlignTop)
        self.execLayout.addWidget(self.parametersSelectorWidget, 0, PySide2.QtCore.Qt.AlignTop)

        # run
        self.runWidget = BiProcessRunWidget()
        self.runWidget.setProgressRange(0,100)
        self.execLayout.addWidget(self.runWidget, 0, PySide2.QtCore.Qt.AlignTop)
        self.runWidget.runSignal.connect(self.run)

        # exec log
        self.standardOutputViewer = BiProcessStandardOutputViewer()
        self.standardOutputViewer.setVisible(False)
        self.execLayout.addWidget(self.standardOutputViewer, 1, PySide2.QtCore.Qt.AlignTop)

        # fill
        fillWidget = QWidget()
        self.execLayout.addWidget(fillWidget, 1, PySide2.QtCore.Qt.AlignTop)

        # hide parameters if there are no parameter
        if processInfo.param_size() < 1:
            parametersLabel.setVisible(False)
            self.parametersSelectorWidget.setVisible(False)
        
    def run(self):
        # create the input datalist
        selectedDataList = self.dataSelectorWidget.selectedData()
        parameters = self.parametersSelectorWidget.parameters() 

        print('run clicked with data:')
        print('selectedDataList:', selectedDataList)
        print('parameters:', parameters)
        self.editorContainer.setSelectedData(selectedDataList)
        self.editorContainer.setParameters(parameters)
        self.editorContainer.emit(BiProcessEditorStates.RunProcess)

    def get_widget(self):
        return self.widget      

class BiProcessDataFilterWidget(QWidget):
    def __init__(self, inputId: str, inputName: str, tags: list, parent: QWidget = None):
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
        self.inputId = inputId
        self.tags = tags
        self.filtersTags = []
        self.filtersOperations = []
        self.filtersValues = []

        filterButton.released.connect(self.showFilter)

        self.filterWidget = QWidget()
        self.filterWidget.setObjectName('BiWidget')
        self.filterWidget.setVisible(False)
        filterLayout = QVBoxLayout()
        self.filterWidget.setLayout(filterLayout)
        titleLabel = QLabel(self.tr('Filter: ') + inputName)
        titleLabel.setObjectName("BiLabelFormHeader1")
        
        filterAreaWidget = QWidget()
        self.filterAreaLayout = QGridLayout()
        filterAreaWidget.setLayout(self.filterAreaLayout)

        tagLabel = QLabel(self.tr("Tag"))
        operatorLabel = QLabel(self.tr("Operator"))
        valueLabel = QLabel(self.tr("Value"))
        self.filterAreaLayout.addWidget(tagLabel, 0, 0)
        self.filterAreaLayout.addWidget(operatorLabel, 0, 1)
        self.filterAreaLayout.addWidget(valueLabel, 0, 2)
        self.addFilter()

        addFilterButton = QPushButton(self.tr("Add filter"))
        addFilterButton.setObjectName('btnDefault')
        validateButton = QPushButton(self.tr("Validate"))
        validateButton.setObjectName('btnPrimary')

        addFilterButton.released.connect(self.addFilter)
        validateButton.released.connect(self.hideFilter)

        filterLayout.addWidget(titleLabel)
        filterLayout.addWidget(filterAreaWidget)
        filterLayout.addWidget(addFilterButton, 0, PySide2.QtCore.Qt.AlignLeft)
        filterLayout.addWidget(validateButton, 0, PySide2.QtCore.Qt.AlignRight)

    def addFilter(self):

        comboBox = QComboBox(self)
        comboBox.addItem('No filter')
        for t in self.tags:
            comboBox.addItem(t)
        valueEdit = QLineEdit(self)

        operationComboBox = QComboBox(self)
        operationComboBox.addItem('=')
        operationComboBox.addItem('<')
        operationComboBox.addItem('>')
        operationComboBox.addItem('<=')
        operationComboBox.addItem('>=')
        
        self.filtersTags.append(comboBox)
        self.filtersOperations.append(operationComboBox)
        self.filtersValues.append(valueEdit)

        row = self.filterAreaLayout.rowCount()
        self.filterAreaLayout.addWidget(comboBox, row, 0)
        self.filterAreaLayout.addWidget(operationComboBox, row, 1)
        self.filterAreaLayout.addWidget(valueEdit, row, 2)

    def showFilter(self):
        self.filterWidget.setVisible(True)

    def hideFilter(self):  
        self.filterWidget.setVisible(False)
        on = False
        for row in range(self.filterAreaLayout.rowCount()):
            if row > 0:
                if self.filterAreaLayout.itemAtPosition(row, 2).widget().text() != '' and self.filterAreaLayout.itemAtPosition(row, 0).widget().currentText() != "No filter":
                    on = True
        if on:
            self.statusLabel.setText("ON")
        else:
            self.statusLabel.setText("OFF")    

    def get_input_id(self) -> str:
        return self.inputId

    def get_filters(self):
        filters = []
        for row in range(self.filterAreaLayout.rowCount()):
            if row > 0:
                f = dict()
                f["name"] = self.filterAreaLayout.itemAtPosition(row, 0).widget().currentText()
                f["operator"] = self.filterAreaLayout.itemAtPosition(row, 1).widget().currentText()
                f["value"] = self.filterAreaLayout.itemAtPosition(row, 2).widget().text()
                if f['name'] != "No filter" and f["value"] != '':
                    filters.append(f)
        return filters    


class BiProcessRunWidget(QWidget):
    runSignal = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        layout = QVBoxLayout()

        previewButton = QPushButton(self.tr("Preview"), self)
        previewButton.setObjectName("btnPrimaryNegative")
        self.runButton = QPushButton(self.tr("Execute"), self)
        self.runButton.setObjectName("btnPrimaryNegative")

        self.progressLabel = QLabel(self)
        self.progressLabel.setObjectName("BiLabelNegative")
        self.progressBar = QProgressBar(self)

        buttonsWidget = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setContentsMargins(0,0,0,0)
        buttonsWidget.setLayout(buttonsLayout)
        buttonsLayout.addWidget(previewButton, 0, PySide2.QtCore.Qt.AlignLeft)
        buttonsLayout.addWidget(self.runButton, 0, PySide2.QtCore.Qt.AlignLeft)

        layout.addWidget(buttonsWidget, 0, PySide2.QtCore.Qt.AlignLeft)
        layout.addWidget(self.progressLabel)
        layout.addWidget(self.progressBar)

        self.setLayout(layout)
        self.setMaximumWidth(350)

        self.progressBar.setRange(0, 0)
        self.progressBar.setVisible(False)
        self.runButton.released.connect(self.run)

    def run(self):
        self.runSignal.emit()

    def setProgressRange(self, minValue: int, maxValue: int):
        self.progressBar.setRange(minValue, maxValue)

    def setProgress(self, value: int):
        if value == 100:
            self.progressBar.setVisible(False)
        else:
            self.progressBar.setRange(0, 100)
            self.progressBar.setVisible(True)
            self.progressBar.setValue(value)

    def setProgressMessage(self, message: str):
        self.progressLabel.setText(message)

    def setRunning(self):
        self.progressBar.setVisible(True)
        self.runButton.setEnabled(False)

    def setRunFinished(self):
        self.runButton.setEnabled(True)


class BiProcessStandardOutputViewer(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        header = BiHideableWidget(self.tr("Execution Log"), 1, self)
        layout.addWidget(header)
        self.setLayout(layout)
        self.textEdit = QTextEdit(self)
        self.textEdit.setMinimumHeight(150)
        header.addWidget(self.textEdit)

    def updateOutput(self, data: str):
        self.textEdit.append(data)

    def updateError(self, data: str):
        self.textEdit.append(data)


class BiProcessDataSelectorWidget(QWidget):
    def __init__(self, info: BiProcessInfo, datalist: list, tags: list, parent: QWidget = None):
        super().__init__(parent)
        self.info = info

        self.layout = QGridLayout()
        row = -1
        for inp in self.info.inputs:
            if inp.io == processpy.IO_INPUT():
                row += 1
                nameLabel = QLabel(inp.description)
                nameLabel.setObjectName("BiProcessDataSelectorWidgetLabel")
                dataComboBox = QComboBox()
                for data in datalist:
                    dataComboBox.addItem(data)
                filterWidget = BiProcessDataFilterWidget(inp.name, inp.description, tags)
                filterWidget.setObjectName("btnDefault")
                self.layout.addWidget(nameLabel, row, 0)
                self.layout.addWidget(dataComboBox, row, 1)
                self.layout.addWidget(filterWidget, row, 2)

        self.setLayout(self.layout)     

    def selectedData(self) -> list:
        selectedData = []
        for row in range(self.layout.rowCount()):
            d = dict()
            d['name'] =  self.layout.itemAtPosition(row, 1).widget().currentText()
            filterWidget = self.layout.itemAtPosition(row, 2).widget()
            d['id'] =  filterWidget.get_input_id()
            d['filters'] = filterWidget.get_filters()
            selectedData.append(d)
        return selectedData    

            
class BiProcessParameterSelectorWidget(QWidget):
    def __init__(self, info: BiProcessInfo, parent: QWidget = None):
        super().__init__(parent)
        self.info = info
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
            if parameter.io == processpy.IO_PARAM():
                row += 1
                titleLabel = QLabel(parameter.description)
                titleLabel.setObjectName("BiProcessDataSelectorWidgetLabel")
                titleLabel.setWordWrap(True)
                titleLabel.setMaximumWidth(150)
                self.labels[parameter.name] = titleLabel
                self.layout.addWidget(titleLabel, row, 0)

                if parameter.type == "integer" or parameter.type == processpy.PARAM_NUMBER() or parameter.type == processpy.PARAM_STRING():
                    valueEdit = BiProcessInputValue(self) 
                    valueEdit.setKey(parameter.name)
                    valueEdit.setValue(parameter.value)
                    valueEdit.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = valueEdit
                    self.layout.addWidget(titleLabel, row, 0)
                    self.layout.addWidget(valueEdit, row, 1)
                
                elif parameter.type == processpy.PARAM_SELECT():
                    w = BiProcessInputSelect(self)
                    w.setKey(parameter.name)
                    w.setContent(parameter.value)
                    w.setAdvanced(parameter.is_advanced)
                    self.widgets[parameter.name] = w
                    #connect(w, SIGNAL(valueChanged(QString, QString)), this, SLOT(showHideConditional(QString,QString)))
                    self.layout.addWidget(titleLabel, row, 0)
                    self.layout.addWidget(w, row, 1)
        
                elif parameter.type == processpy.PARAM_FILE():
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
            p = dict()
            p['name'] = key
            p['value'] = self.widgets[key].value()
            parameters.append(p)
        return parameters    



class BiProcessMultiEditorComponent(BiComponent):
    def __init__(self, container: BiProcessMultiEditorContainer, experimentContainer: BiExperimentContainer):
        super(BiProcessMultiEditorComponent, self).__init__()
        self._object_name = 'BiProcessMultiEditorComponent'
        self.container = container
        self.container.register(self)

        self.experimentContainer = experimentContainer

        self.widget = QWidget()
        self.widget.setObjectName("BiLightGrayWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        self.widget.setLayout(layout)

        self.tabWidget = QTabWidget()
        layout.addWidget(self.tabWidget)

    def update(self, action: BiAction):
        if action.state == BiProcessMultiEditorStates.ProcessAdded:
            self.openProcess()

    def openProcess(self):
        processInfo = self.container.lastAddedProcess()
        
        processEditorContainer = BiProcessEditorContainer()
        processEditorContainer.setProcessInfo(processInfo)

        processExecComponent = BiProcessEditorComponent(processEditorContainer, self.experimentContainer)

        processEditorModel = BiProcessEditorModel(processEditorContainer, self.experimentContainer)

        processEditorContainer.emit(BiProcessEditorStates.ProcessInfoLoaded)
        self.tabWidget.addTab(processExecComponent.get_widget(), processInfo.name)
 
    def get_widget(self):
        return self.widget      


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
        self.conbobox.currentIndexChanged.connect(self.updateValue)
        self.conbobox.currentIndexChanged.connect(self.emitValueChanged)

    def emitValueChanged(self, value: str):
        self.valueChanged.emit(self._key, value)

    def setContentStr(self, content: str):
        contentList = content.split(";")
        self.setContentList(contentList)

    def setContentList(self, content: list):
        for c in content:
            item = c.simplified()
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
