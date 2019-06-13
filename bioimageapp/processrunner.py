from bioimagepy.process import BiProcess

import PySide2.QtCore
from PySide2.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QSplitter, QScrollArea, QLabel

from framework import BiContainer, BiModel, BiComponent
from experiment import BiExperimentContainer
from widgets import BiWebBrowser

class BiProcessMultiEditorContainer(BiContainer):
    ProcessAdded = "BiProcessMultiEditorContainer::ProcessAdded"

    def __init__(self):
        super(BiProcessMultiEditorContainer, self).__init__()
        self._object_name = 'BiProcessMultiEditorContainer'
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

class BiProcessEditorContainer(BiContainer):
    ProcessInfoLoaded = "BiProcessEditorContainer::ProcessInfoLoaded"
    RunProcess = "BiProcessEditorContainer::RunProcess"
    ProgressChanged = "BiProcessEditorContainer::ProgressChanged"

    def __init__(self):
        super(BiProcessEditorContainer, self).__init__()
        self._object_name = 'BiProcessEditorContainer'
        self.processInfo = None
        self.selectedDataList = None
        self.progress = 0
        self.progressMessage = ''

class BiProcessMultiEditorModel(BiModel):
    def __init__(self, container: BiProcessMultiEditorContainer):
        super(BiProcessMultiEditorModel, self).__init__()
        self._object_name = 'BiProcessMultiEditorModel'
        self.container = container
        self.container.addObserver(self)  

    def update(self, container: BiContainer):
        pass

class BiProcessEditorModel(BiModel):
    def __init__(self, container: BiProcessEditorContainer, experimentContainer: BiExperimentContainer):
        super(BiProcessEditorModel, self).__init__()
        self._object_name = 'BiProcessEditorModel'
        self.container = container
        self.container.addObserver(self)  
        self.experimentContainer = experimentContainer
        self.experimentContainer.addObserver(self)

    def update(self, container: BiContainer):
        if container.action == BiProcessEditorContainer.RunProcess:
            self.runProcess()

    def runProcess(self):
        print("Run process not yet implemented")

    def progress(self, pourcentage: int, message: str):
        self.processExecContainer.setProgress(pourcentage, message)
        self.processExecContainer.notify(BiProcessEditorContainer.ProgressChanged)


class BiProcessMultiEditorToolBarComponent(BiComponent):
    def __init__(self, container: BiProcessMultiEditorContainer):
        super(BiProcessMultiEditorToolBarComponent, self).__init__()
        self.container = container
        self.container.addObserver(self)
        self.widget = QWidget()

    def get_widget(self):
        return self.widget    


class BiProcessEditorComponent(BiComponent):
    def __init__(self, container: BiProcessEditorContainer, experimentContainer: BiExperimentContainer):
        super(BiProcessEditorComponent, self).__init__()
        self._object_name = 'BiProcessMultiEditorComponent'
        self.container = container
        self.container.addObserver(self)
        self.experimentContainer = experimentContainer
        self.experimentContainer.addObserver(self)

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
        self.execLayout = QVBoxLayout
        execWidget.setLayout(self.execLayout)
        splitter.addWidget(execScrollArea)
        splitter.setStretchFactor(0,1)
        splitter.setStretchFactor(1,3)

    def update(self, container: BiContainer):
        if container.action == BiProcessEditorContainer.ProcessInfoLoaded:
            self.docWidget.setHomePage(self.editContainer.processInfo.doc(), True)
            self.buildExecWidget()

        if container.action == BiProcessEditorContainer.ProgressChanged:
            self.runWidget.setProgress(self.editContainer.progress())
            self.runWidget.setProgressMessage(self.editContainer.progressMessage())
            if self.editContainer.progress == 100:
                self.runWidget.setRunFinished()

    def buildExecWidget(self):

        self.execLayout.addWidget(QLabel("Empty widget"))    

        #processInfo = self.editContainer.processInfo
        
        ## inputs gui
        #inputLabel = QLabel(self.widget.tr("Inputs"))
        #inputLabel.setObjectName("BiLabelFormHeader1Negative")
        #self.dataSelectorWidget = BiProcessDataSelectorWidget(processInfo.getIO())
        #self.dataSelectorWidget.setTags(self.projectContainer.info().tags())
        #dataList = ["Data"]
        #self.dataSelectorWidget.setDataList(dataList)

        #self.execLayout.addWidget(inputLabel, 0, PySide2.QtCore.Qt.AlignTop)
        #self.execLayout.addWidget(self.dataSelectorWidget, 0, PySide2.QtCore.Qt.AlignTop)

        ## parameters gui
        #parametersLabel = QLabel(self.widget.tr("Parameters"))
        #parametersLabel.setObjectName("biLabelFormHeader1Negative")
        #self.parametersSelectorWidget = BiProcessParameterSelectorWidget(processInfo.parameters())
        #self.execLayout.addWidget(parametersLabel, 0, PySide2.QtCore.Qt.AlignTop)
        #self.execLayout.addWidget(self.parametersSelectorWidget, 0, PySide2.QtCore.Qt.AlignTop)

        ## run
        #self.runWidget = BiProcessRunWidget()
        #self.runWidget.setProgressRange(0,100)
        #self.execLayout.addWidget(self.runWidget, 0, PySide2.QtCore.Qt.AlignTop)
        #self.runWidget.run.connect(self.run)

        ## exec log
        #self.standardOutputViewer = BiProcessStandardOutputViewer()
        #self.standardOutputViewer.setVisible(False)
        #self.execLayout.addWidget(self.standardOutputViewer, 1, PySide2.QtCore.Qt.AlignTop)

        ## fill
        #fillWidget = QWidget()
        #self.execLayout.addWidget(fillWidget, 1, PySide2.QtCore.Qt.AlignTop)

        ## hide parameters if there are no parameter
        #if processInfo.parameters().count() < 1:
        #    parametersLabel.setVisible(False)
        #    self.parametersSelectorWidget.setVisible(False)
        

    def run(self):
        # create the input datalist
        selectedDataList = self.dataSelectorWidget.selectedData()
        self.editContainer.setSelectedData(selectedDataList)
        self.editContainer.notify(BiProcessEditorContainer.RunProcess)

    def get_widget(self):
        return self.widget      

class BiProcessMultiEditorComponent(BiComponent):
    def __init__(self, container: BiProcessMultiEditorContainer, experimentContainer: BiExperimentContainer):
        super(BiProcessMultiEditorComponent, self).__init__()
        self._object_name = 'BiProcessMultiEditorComponent'
        self.container = container
        self.container.addObserver(self)

        self.experimentContainer = experimentContainer

        self.widget = QWidget()
        self.widget.setObjectName("BiLightGrayWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        self.widget.setLayout(layout)

        self.tabWidget = QTabWidget()
        layout.addWidget(self.tabWidget)

    def update(self, container: BiContainer):
        if container.action == BiProcessMultiEditorContainer.ProcessAdded:
            self.openProcess()

    def openProcess(self):
        processInfo = self.container.lastAddedProcess()

        processEditorContainer = BiProcessEditorContainer()
        processEditorContainer.setProcessInfo(processInfo)

        processExecComponent = BiProcessEditorComponent(processEditorContainer, self.experimentContainer)

        processEditorModel = BiProcessEditorModel(processEditorContainer, self.experimentContainer)

        processEditorContainer.notify(BiProcessEditorContainer.ProcessInfoLoaded)
        self.tabWidget.addTab(processExecComponent.widget(), processInfo.name())

    def get_widget(self):
        return self.widget      
