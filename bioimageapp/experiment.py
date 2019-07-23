import sys
import os
import ntpath
import PySide2.QtCore
from PySide2.QtCore import QFileInfo, QDir, QThread, QObject, Signal, Slot
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                               QGridLayout, QScrollArea, QToolButton, QComboBox,
                               QFileDialog, QTabWidget, QCheckBox, QSpinBox, QProgressBar)
from shutil import copyfile
import subprocess

from framework import BiComponent, BiContainer, BiModel, BiStates, BiAction
from widgets import BiDragLabel, BiTagWidget
from settings import BiSettingsAccess

from bioimagepy.experiment import BiExperiment 
from bioimagepy.metadata import BiRawData, BiProcessedDataSet, BiProcessedData
from  bioimagepy.metadata import create_rawdata
import bioimagepy.experiment as experimentpy 
from bioimagepy.process import BiProcessParser, BiProcessInfo

class BiExperimentStates(BiStates):
    OriginModified = "BiExperimentContainer.OriginModified"
    Loaded = "BiExperimentContainer.Loaded"
    SettingsClicked = "BiExperimentContainer.SettingsClicked"
    InfoClicked = "BiExperimentContainer.InfoClicked"
    ImportClicked = "BiExperimentContainer.ImportClicked"
    TagsClicked = "BiExperimentContainer.TagsClicked"
    InfoModified = "BiExperimentContainer.InfoModified"
    RefreshClicked = "BiExperimentContainer.RefreshClicked"
    RawDataImported = "BiExperimentContainer.RawDataImported"
    TagsModified = "BiExperimentContainer.TagsModified"
    RawDataLoaded = "BiExperimentContainer.RawDataLoaded"
    DataAttributEdited = "BiExperimentContainer.DataAttributEdited"
    ThumbnailChanged = "BiExperimentContainer.ThumbnailChanged"
    DataSetComboChanged = "BiExperimentContainer.DataSetComboChanged"
    NewProcessedDataSet = "BiExperimentContainer.NewProcessedDataSet"
    NewProcessedDataSetLoaded = "BiExperimentContainer.NewProcessedDataSetLoaded"
    DataThumbnailChanged = "BiExperimentContainer.DataThumbnailChanged"


class BiExperimentContainer(BiContainer):

    def __init__(self):
        super(BiExperimentContainer, self).__init__()
        self._object_name = 'BiExperimentContainer'
        
        # states
        self.states = BiExperimentStates()

        # data
        self.projectFile = ''
        self.experiment = None
        self.lastEditedDataIdx = 0
        self.changed_thumbnail_row = -1
        self.changed_thumbnail_column = -1
        self.changed_thumbnail_data = None
        self.changed_thumbnail_url = ''
        self.changed_combo_txt = ''
        self.changed_data_thumbnail_id = -1
        self.changed_data_thumbnail_url = "" 

    def projectRootDir(self):
        return os.path.dirname(self.projectFile)

    def setTagValue(self, dataIdx: int, tag: str, value: str):
        self.experiment.rawdataset().data(dataIdx).set_tag(tag, value)

    def setDataName(self, dataIdx: int, name: str):
        self.experiment.rawdataset().data(dataIdx).set_name(name)

    def setLastEditedDataIdx(self, idx):
        self.lastEditedDataIdx = idx    
   

class BiExperimentImportDataStates(BiStates):
    NewImport = "BiExperimentImportDataContainer.NewImport"
    DataImported = "BiExperimentImportDataContainer.DataImported"
    NewImportDir = "BiExperimentImportDataContainer.NewImportDir"
    Progress = "BiExperimentImportDataContainer.Progress"

class BiExperimentImportDataContainer(BiContainer):

    def __init__(self):
        super(BiExperimentImportDataContainer, self).__init__()
        self._object_name = 'BiExperimentImportDataContainer'

        # states
        self.states = BiExperimentImportDataStates()

        # data
        self.originFile = ''
        self.destinationFile = ''
        self.author = ''
        self.createddate = ''
        self.data = None
        self.dir_data_path = ''
        self.dir_recursive = False
        self.dir_filter = -1
        self.dir_filter_value = ''
        self.dir_copy_data = False
        self.progress = dict()

class BiExperimentAddTagsStates(BiStates):
    ValidatedUsingName = "BiExperimentAddTagsContainer.ValidatedUsingName"
    ValidatedUsingSeparator = "BiExperimentAddTagsContainer.ValidatedUsingSeparator"

class BiExperimentAddTagsContainer(BiContainer):

    def __init__(self):
        super(BiExperimentAddTagsContainer, self).__init__()
        self._object_name = 'BiExperimentAddTagsContainer'

        # states
        self.states = BiExperimentAddTagsStates()

        # data
        self.usingname_tag = ''
        self.usingname_search = []
        self.usingseparator_tags = []
        self.usingseparator_separator = []
        self.usingseparator_position = []


class BiExperimentModel(BiModel):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentModel, self).__init__()
        self._object_name = 'BiExperimentModel'
        self.container = container
        self.container.register(self)  
        self.thumbnailCreator = BiThumbnailMaker()
        self.thumbnailCreator.experimentContainer = self.container

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.OriginModified:
            print('change origin to :',  self.container.projectFile)
            self.container.experiment = BiExperiment(self.container.projectFile)
            self.container.emit(BiExperimentStates.Loaded)
            return

        if action.state == BiExperimentStates.NewProcessedDataSet:
            self.container.experiment.read()
            self.container.emit(BiExperimentStates.NewProcessedDataSetLoaded)
            return    

        if action.state == BiExperimentStates.InfoModified or action.state == BiExperimentStates.TagsModified:
            self.container.experiment.write()
            return
        
        if action.state == BiExperimentStates.RawDataImported:
            self.container.experiment.rawdataset().write()    
            self.container.experiment.rawdataset().last_data().write()
            self.container.emit(BiExperimentStates.RawDataLoaded)
            return

        if action.state == BiExperimentStates.DataAttributEdited:
            lastEditedIndex = self.container.lastEditedDataIdx
            rawData = self.container.experiment.rawdataset().data(lastEditedIndex)
            rawData.write()
            return

        if action.state == BiExperimentStates.RefreshClicked:
            self.thumbnailCreator.start()              

class BiThumbnailMaker(QThread):
    thumbnailChanged = Signal(int, str)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.experimentContainer = None
        self.thumbnailChanged.connect(self.notifyThumbnailChanged)

    def notifyThumbnailChanged(self, i: int, thumbnail_url: str):
        self.experimentContainer.changed_data_thumbnail_id = i
        self.experimentContainer.changed_data_thumbnail_url = thumbnail_url
        self.experimentContainer.emit(BiExperimentStates.DataThumbnailChanged) 

    def run(self):
        for i in range(self.experimentContainer.experiment.rawdataset().size()):
            raw_data = self.experimentContainer.experiment.rawdataset().raw_data(i)
            if raw_data.thumbnail() == '':
                fileName = os.path.splitext(raw_data.name())
                raw_data.set_thumbnail(fileName[0]+'_thumb.jpg')
                raw_data.write()
                settingsGroups = BiSettingsAccess().instance
                program = settingsGroups.value("Experiment", "fiji") # "/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx"
                arguments = [program, "--headless", "--console", "-macro", settingsGroups.value("Experiment", "thumbnail macro"), raw_data.url()]
                subprocess.run(arguments)  
                self.thumbnailChanged.emit(i, raw_data.thumbnail())

class BiThumbnailMakerProcessedData(QThread):
    thumbnailChanged = Signal(int, int, BiProcessedData)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.experimentContainer = None
        self.thumbnailChanged.connect(self.notifyThumbnailChanged)
        self.data = []

    def set_container(self, container: BiExperimentContainer):    
        self.experimentContainer = container

    def set_data(self, data: list):
        self.data = data

    def notifyThumbnailChanged(self, row: int, column: int, data: BiProcessedData):
        self.experimentContainer.changed_thumbnail_row = row
        self.experimentContainer.changed_thumbnail_column = column
        self.experimentContainer.changed_thumbnail_data = data
        self.experimentContainer.emit(BiExperimentStates.ThumbnailChanged) 

    def run(self):
        for data in self.data:
            processed_data = data['processeddata']
            if processed_data.datatype() == 'image' and processed_data.thumbnail() == '':
                fileName = os.path.splitext(processed_data.name())
                processed_data.set_thumbnail(fileName[0]+'_thumb.jpg')
                processed_data.write()
                settingsGroups = BiSettingsAccess().instance
                program = settingsGroups.value("Experiment", "fiji") # "/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx"
                arguments = [program, "--headless", "--console", "-macro", settingsGroups.value("Experiment", "thumbnail macro"), processed_data.url()]
                subprocess.run(arguments)  
                self.thumbnailChanged.emit(data['row'], data['column'], processed_data)


class BiExperimentImportDataModel(BiModel):
    def __init__(self, experimentContainer: BiExperimentContainer, importContainer: BiExperimentImportDataContainer):
        super(BiExperimentImportDataModel, self).__init__()
        self._object_name = 'BiExperimentImportDataModel'
        self.experimentContainer = experimentContainer
        self.importContainer = importContainer
        self.importContainer.register(self)  
        self.thumbnailCreator = BiThumbnailMaker()  
        self.thumbnailCreator.experimentContainer = self.experimentContainer 

    def update(self, action: BiAction):
        if action.state == BiExperimentImportDataStates.NewImport:
            self.importData()
            self.importContainer.emit(BiExperimentImportDataStates.DataImported)
            return

        if action.state == BiExperimentImportDataStates.NewImportDir:
            self.importDir()
            self.importContainer.emit(BiExperimentImportDataStates.DataImported)   
            return 

    def notify(self, data: dict):
        self.importContainer.progress = data
        self.importContainer.emit(BiExperimentImportDataStates.Progress)

    def importDir(self):

        filter_regexp = ''
        if self.importContainer.dir_filter == 0:
            filter_regexp = '\\' + self.importContainer.dir_filter_value + '$'
        elif self.importContainer.dir_filter == 1:
            filter_regexp = self.importContainer.dir_filter_value    
        elif self.importContainer.dir_filter == 2:
            filter_regexp = '^' + self.importContainer.dir_filter_value  

        importObj = experimentpy.BiExperimentImport()   
        importObj.register(self)  
        importObj.import_dir(experiment=self.experimentContainer.experiment, 
                      dir_path=self.importContainer.dir_data_path, 
                      filter=filter_regexp, 
                      author=self.importContainer.author, 
                      datatype='image', 
                      createddate=self.importContainer.createddate, 
                      copy_data=self.importContainer.dir_copy_data)

        self.importContainer.emit(BiExperimentImportDataStates.DataImported) 
        self.create_thumbnails()             

    def create_thumbnails(self):
        self.thumbnailCreator.start()

    def importData(self):
        self.createMetaDataFile()
        self.copyInputFile()
        self.createThumb()

    def createMetaDataFile(self):
        self.importContainer.data.write()

    def copyInputFile(self):
        copyfile(self.importContainer.originFile, self.importContainer.destinationFile)

    def createThumb(self):
        destinationPath = self.importContainer.destinationFile

        settingsGroups = BiSettingsAccess().instance
        program = settingsGroups.value("Experiment", "fiji") # "/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx"
        arguments = [program, "--headless", "--console", "-macro", settingsGroups.value("Experiment", "thumbnail macro"), destinationPath]

        print("create thumb:")
        print("program: ", program)
        print("arguments: ", arguments)
        subprocess.run(arguments)


class BiExperimentAddTagsModel(BiModel):
    def __init__(self, experimentContainer: BiExperimentContainer, addTagsContainer: BiExperimentAddTagsContainer):
        super(BiExperimentAddTagsModel, self).__init__()
        self._object_name = 'BiExperimentAddTagsModel'
        self.experimentContainer = experimentContainer
        self.addTagsContainer = addTagsContainer
        self.addTagsContainer.register(self)  

    def update(self, action: BiAction):
        if action.state == BiExperimentAddTagsStates.ValidatedUsingName:
            experimentpy.tag_rawdata_from_name(self.experimentContainer.experiment, 
                                                self.addTagsContainer.usingname_tag, 
                                                self.addTagsContainer.usingname_search )
            self.experimentContainer.emit(BiExperimentStates.TagsModified)                                      
            return 

        if action.state == BiExperimentAddTagsStates.ValidatedUsingSeparator:
            for i in range(len(self.addTagsContainer.usingseparator_tags)):
                experimentpy.tag_rawdata_using_seperator(self.experimentContainer.experiment, 
                                                         tag=self.addTagsContainer.usingseparator_tags[i], 
                                                         separator=self.addTagsContainer.usingseparator_separator[i], 
                                                         value_position=self.addTagsContainer.usingseparator_position[i]) 
                self.experimentContainer.emit(BiExperimentStates.TagsModified)                                         
            return                                                                                


class BiExperimentComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentComponent, self).__init__()
        self._object_name = 'BiExperimentComponent'
        self.container = container
        self.container.register(self)

        self.buildWidget()

    def buildWidget(self):
        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        self.dataComponent = BiExperimentDataComponent(self.container)
        layout.addWidget(self.dataComponent.get_widget())    
        self.processedDataComponent = BiExperimentProcessedDataComponent(self.container)
        layout.addWidget(self.processedDataComponent.get_widget())  

        self.dataComponent.get_widget().setVisible(True)
        self.processedDataComponent.get_widget().setVisible(False)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.DataSetComboChanged:
            if self.container.changed_combo_txt == 'Data':
                self.dataComponent.get_widget().setVisible(True)
                self.processedDataComponent.get_widget().setVisible(False)
            else:
                self.dataComponent.get_widget().setVisible(False)
                self.processedDataComponent.get_widget().setVisible(True)                    

    def get_widget(self):
        return self.widget      


class BiExperimentHelpComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentHelpComponent, self).__init__()
        self._object_name = 'BiExperimentHelpComponent'
        self.container = container
        self.container.register(self)

class BiExperimentProcessedDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super().__init__()
        self._object_name = 'BiExperimentProcessedDataComponent'
        self.container = container
        self.container.register(self)
        self.thumbnailList = []
        self.thumbnailMaker = BiThumbnailMakerProcessedData()
        self.thumbnailMaker.set_container(self.container)
        
        self.widget = QWidget()
        self.widget.setObjectName('BiWidget')

        layout = QVBoxLayout()
        layout.setContentsMargins(5,0,5,5)
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(2)

        labels = ["", "Name"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.tableWidget) 

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.DataSetComboChanged:
            dataset = self.container.experiment.processeddataset_by_name(self.container.changed_combo_txt)
            self.load(dataset)
            self.thumbnailMaker.set_data(self.thumbnailList)
            self.thumbnailMaker.start()

        if action.state == BiExperimentStates.ThumbnailChanged:
            self.set_thumbnail(self.container.changed_thumbnail_row, self.container.changed_thumbnail_column, self.container.changed_thumbnail_data, self.container.changed_thumbnail_data.thumbnail())  

    def load(self, processeddataset: BiProcessedDataSet):

        # get process info
        process_url = processeddataset.process_url()
        parser = BiProcessParser(process_url)
        process_info = parser.parse()

        if process_info.type == 'sequential':
            self.load_sequential(processeddataset, process_info)
        else:
            self.load_merge(processeddataset, process_info)    
        
    def load_merge(self, processeddataset: BiProcessedDataSet, process_info: BiProcessInfo):

        # header
        self.tableWidget.setColumnCount(1 + len(process_info.outputs))
        labels = ["Name"]
        for output in process_info.outputs:
            labels.append(output.description)
        self.tableWidget.setHorizontalHeaderLabels(labels)

        # data
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(1)

        self.tableWidget.setItem(0, 0, QTableWidgetItem(process_info.name)) 

        for j in range(processeddataset.size()):
            processed_data = processeddataset.processed_data(j)
            oID = 0
            for output in process_info.outputs:
                oID += 1
                if processed_data.metadata['origin']['output']['label'] == output.description:
                    if processed_data.metadata['origin']['output']['label'] == output.description:
                        if processed_data.datatype() == 'image': 
                            thumbInfo = dict()
                            thumbInfo['row'] = 0
                            thumbInfo['column'] = oID
                            thumbInfo['processeddata'] = processed_data
                            self.thumbnailList.append(thumbInfo)
                            self.set_thumbnail(0, oID, processed_data, processed_data.thumbnail())
                        elif processed_data.datatype() == 'number':
                            with open(processed_data.url(), 'r') as content_file:
                                p = content_file.read() 
                                self.tableWidget.setItem(0, oID, QTableWidgetItem(p)) 
                        elif processed_data.datatype() == 'array':
                            with open(processed_data.url(), 'r') as content_file:
                                p = content_file.read() 
                                self.tableWidget.setItem(0, oID, QTableWidgetItem(p))  
                        elif processed_data.datatype() == 'table':
                                label = self.table_data_thumb(processed_data.url())
                                self.tableWidget.setCellWidget(0, oID, label) 

    def load_sequential(self, processeddataset: BiProcessedDataSet, process_info: BiProcessInfo):

        # headers
        processed_data_column_offset = 2 + self.container.experiment.tags_size()
        self.tableWidget.setColumnCount(2 + self.container.experiment.tags_size() + len(process_info.outputs))
        labels = ["", "Name"]
        for tag in self.container.experiment.tags():
            labels.append(tag)
        for output in process_info.outputs:
            labels.append(output.description)
        self.tableWidget.setHorizontalHeaderLabels(labels)

        exp_size = self.container.experiment.rawdataset().size()
        if exp_size < 10:
            self.tableWidget.verticalHeader().setFixedWidth(20)
        elif exp_size >= 10 and exp_size < 100  :
            self.tableWidget.verticalHeader().setFixedWidth(40)  
        elif exp_size >= 100 and exp_size < 1000  :    
            self.tableWidget.verticalHeader().setFixedWidth(60)  

        # data
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(self.container.experiment.rawdataset().size())

        self.tableWidget.setColumnWidth(0, 64)
        for i in range(self.container.experiment.rawdataset().size()):
               
            info = self.container.experiment.rawdataset().raw_data(i)

            # thumbnail
            self.set_thumbnail(i, 0, info, info.thumbnail())
    
            # name
            self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name()))

            # tags
            for t in range(self.container.experiment.tags_size()):
                self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tag(self.container.experiment.tag(t))))

            for t in range(self.container.experiment.tags_size()):
                self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tag(self.container.experiment.tag(t))))

            # processed data
            for j in range(processeddataset.size()):
                processed_data = processeddataset.processed_data(j)
                origin_raw_data = processed_data.origin_raw_data()
                if info.url() == origin_raw_data.url():
                    oID = 0
                    for output in process_info.outputs:
                        oID += 1
                        if processed_data.metadata['origin']['output']['label'] == output.description:
                            if processed_data.datatype() == 'image':
                                thumbInfo = dict()
                                thumbInfo['row'] = i
                                thumbInfo['column'] = oID + processed_data_column_offset-1
                                thumbInfo['processeddata'] = processed_data
                                self.thumbnailList.append(thumbInfo)
                                self.set_thumbnail(i, oID + processed_data_column_offset-1, processed_data, processed_data.thumbnail())
                            elif processed_data.datatype() == 'number':
                                with open(processed_data.url(), 'r') as content_file:
                                    p = content_file.read() 
                                    self.tableWidget.setItem(i, oID + processed_data_column_offset-1, QTableWidgetItem(p)) 
                            elif processed_data.datatype() == 'array':
                                with open(processed_data.url(), 'r') as content_file:
                                    p = content_file.read() 
                                    self.tableWidget.setItem(i, oID + processed_data_column_offset-1, QTableWidgetItem(p))  
                            elif processed_data.datatype() == 'table':
                                    label = self.table_data_thumb(processed_data.url())
                                    self.tableWidget.setCellWidget(i, oID + processed_data_column_offset-1, label)              


    def table_data_thumb(self, file: str) -> QLabel:
        with open(file, 'r') as content_file:
            p = content_file.read() 
        
        content = '<table border="0.2"><tbody>'
        contentRows = p.split('\n')
        for row in contentRows:
            ds = row.split(',')
            if len(ds) > 1:
                content += '<tr>'
                for d in ds:
                    content += '<td>' + d + '</td>'
                content += '</tr>'
        content += '</tbody></table>'
        label = QLabel(content)
        label.setTextFormat(PySide2.QtCore.Qt.RichText)
        return label


    def set_thumbnail(self, row, column, info, thumbnail):
        metaLabel = BiDragLabel(self.widget)
        metaLabel.setMimeData(info.url())
        if thumbnail != "":
            image = QImage(thumbnail)
            metaLabel.setPixmap(QPixmap.fromImage(image))
            self.tableWidget.setRowHeight(row, 64)
        else:
            metaLabel.setObjectName("BiExperimentDataComponentLabel")
            self.tableWidget.setRowHeight(row, 64)
        self.tableWidget.setCellWidget(row, column, metaLabel) 

    def get_widget(self):
        return self.widget        


class BiExperimentDataComponent(BiComponent):        
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentDataComponent, self).__init__()
        self._object_name = 'BiExperimentDataComponent'
        self.container = container
        self.container.register(self)
  
        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        layout.setContentsMargins(5,0,5,5)
        self.widget.setLayout(layout)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.cellChanged.connect(self.cellChanged)

        labels = ["", "Name", "Author", "Date"]
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.tableWidget) 

    def update(self, action: BiAction):
        if (action.state == BiExperimentStates.Loaded or 
            action.state == BiExperimentStates.TagsModified or 
            action.state == BiExperimentStates.RawDataLoaded
            ):
            self.update_table()
            return
 
        if action.state == BiExperimentStates.DataThumbnailChanged:
            i = self.container.changed_data_thumbnail_id
            thumbnail = self.container.changed_data_thumbnail_url
            info = self.container.experiment.rawdataset().raw_data(i)
            self.set_thumbnail(i, info, thumbnail)

    def update_table(self):
        # headers
        self.tableWidget.setColumnCount(4 + self.container.experiment.tags_size())
        labels = ["", "Name"]
        for tag in self.container.experiment.tags():
            labels.append(tag)
        labels.append("Author")
        labels.append("Date")
        self.tableWidget.setHorizontalHeaderLabels(labels)

        exp_size = self.container.experiment.rawdataset().size()
        if exp_size < 10:
            self.tableWidget.verticalHeader().setFixedWidth(20)
        elif exp_size >= 10 and exp_size < 100  :
            self.tableWidget.verticalHeader().setFixedWidth(40)  
        elif exp_size >= 100 and exp_size < 1000  :    
            self.tableWidget.verticalHeader().setFixedWidth(60)  

        # data
        self.tableWidget.cellChanged.disconnect(self.cellChanged)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(self.container.experiment.rawdataset().size())

        self.tableWidget.setColumnWidth(0, 64)
        for i in range(self.container.experiment.rawdataset().size()):
               
            info = self.container.experiment.rawdataset().raw_data(i)

            # thumbnail
            self.set_thumbnail(i, info, info.thumbnail())

            # name
            self.tableWidget.setItem(i, 1, QTableWidgetItem(info.name()))

            # tags
            for t in range(self.container.experiment.tags_size()):
                self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tag(self.container.experiment.tag(t))))

            for t in range(self.container.experiment.tags_size()):
                self.tableWidget.setItem(i, 2+t, QTableWidgetItem(info.tag(self.container.experiment.tag(t))))

            # author
            itemAuthor = QTableWidgetItem(info.author())
            itemAuthor.setFlags(PySide2.QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(i, 2 + self.container.experiment.tags_size(), itemAuthor)

            # created date
            itemCreatedDate = QTableWidgetItem(info.createddate())
            itemCreatedDate.setFlags(PySide2.QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(i, 3 + self.container.experiment.tags_size(), itemCreatedDate)
            
        self.tableWidget.cellChanged.connect(self.cellChanged)

    def set_thumbnail(self, i, info, thumbnail):
        # thumbnail
        metaLabel = BiDragLabel(self.widget)

        metaLabel.setMimeData(info.url())
        if thumbnail != "":
            image = QImage(thumbnail)
            metaLabel.setPixmap(QPixmap.fromImage(image))
            self.tableWidget.setRowHeight(i, 64)
        else:
            metaLabel.setObjectName("BiExperimentDataComponentLabel")
            self.tableWidget.setRowHeight(i, 64)

        self.tableWidget.setCellWidget(i, 0, metaLabel)          
        
    def cellChanged(self, row: int, col: int):
        if col == 1:
            self.container.setLastEditedDataIdx(row)
            self.container.setDataName(row, self.tableWidget.item(row, col).text())
            self.container.emit(BiExperimentStates.DataAttributEdited)
        elif  col > 1 and col < 4 + self.container.experiment.tags_size() :
            self.container.setLastEditedDataIdx(row)
            self.container.setTagValue(row, self.container.experiment.tag(col-2), self.tableWidget.item(row, col).text())
            self.container.emit(BiExperimentStates.DataAttributEdited)

    def get_widget(self):
        return self.widget  

class BiExperimentInfoEditorComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentInfoEditorComponent, self).__init__()
        self._object_name = 'BiExperimentDataComponent'
        self.container = container
        self.container.register(self)   

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Informations"))
        title.setObjectName("BiLabelFormHeader1")

        self.nameEdit = QLineEdit()
        self.authorEdit = QLineEdit()
        self.createdEdit = QLineEdit()

        nameLabel = QLabel(self.widget.tr("Project Name:"))
        authorLabel = QLabel(self.widget.tr("User:"))
        createdLabel = QLabel(self.widget.tr("Created date:"))

        layout.addWidget(title, 0, 0, 1, 2)
        layout.addWidget(nameLabel, 1, 0)
        layout.addWidget(self.nameEdit, 1, 1)
        layout.addWidget(authorLabel, 2, 0)
        layout.addWidget(self.authorEdit, 2, 1)
        layout.addWidget(createdLabel, 3, 0)
        layout.addWidget(self.createdEdit, 3, 1)

        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        layout.addWidget(saveButton, 4, 1, PySide2.QtCore.Qt.AlignRight)
        saveButton.released.connect(self.saveClicked)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            self.nameEdit.setText(self.container.experiment.name())
            self.authorEdit.setText(self.container.experiment.author())
            self.createdEdit.setText(self.container.experiment.createddate())

    def saveClicked(self):
        self.container.experiment.set_name(self.nameEdit.text())
        self.container.experiment.set_author(self.authorEdit.text())
        self.container.experiment.set_createddate(self.createdEdit.text())

        self.container.emit(BiExperimentStates.InfoModified)

    def get_widget(self):
        return self.widget  

class BiExperimentTagsListComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentTagsListComponent, self).__init__()
        self._object_name = 'BiExperimentTagsListComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Tags"))
        title.setObjectName("BiLabelFormHeader1")

        # add widget
        addWidget = QWidget()
        addLayout = QHBoxLayout()
        addWidget.setLayout(addLayout)

        self.addEdit = QLineEdit(self.widget)
        addButton = QPushButton(self.widget.tr("Add"))
        addButton.setObjectName("btnDefault")
        addLayout.addWidget(self.addEdit)
        addLayout.addWidget(addButton)

        self.tagListWidget = QWidget()
        self.tagListWidget.setObjectName("BiWidget")
        self.tagListLayout = QVBoxLayout()
        self.tagListWidget.setLayout(self.tagListLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setObjectName("BiWidget")
        scrollArea.setWidget(self.tagListWidget)

        # button area
        buttonsWidget = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setContentsMargins(0,0,0,0)
        buttonsLayout.setSpacing(2)
        buttonsWidget.setLayout(buttonsLayout)
        cancelButton = QPushButton(self.widget.tr("Cancel"))
        cancelButton.setObjectName("btnDefault")
        saveButton = QPushButton(self.widget.tr("Save"))
        saveButton.setObjectName("btnPrimary")
        buttonsLayout.addWidget(cancelButton, 1, PySide2.QtCore.Qt.AlignRight)
        buttonsLayout.addWidget(saveButton, 0, PySide2.QtCore.Qt.AlignRight)

        layout.addWidget(title)
        layout.addWidget(addWidget)
        layout.addWidget(scrollArea)
        layout.addWidget(buttonsWidget)

        addButton.released.connect(self.addButtonClicked)
        cancelButton.released.connect(self.cancelButtonClicked)
        saveButton.released.connect(self.saveButtonClicked)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded:
            self.reload()
            return

    def reload(self):
        # free layout
        for i in reversed(range(self.tagListLayout.count())): 
            self.tagListLayout.itemAt(i).widget().deleteLater()

        # add tags
        for t in range(self.container.experiment.tags_size()):
            tagWidget = BiTagWidget() 
            tagWidget.setContent(self.container.experiment.tag(t))
            tagWidget.remove.connect(self.removeClicked)
            self.tagListLayout.addWidget(tagWidget)
        self.tagListWidget.adjustSize()

    def addButtonClicked(self):
        if self.addEdit.text() != "":
            tagWidget = BiTagWidget()
            tagWidget.setContent(self.addEdit.text())
            tagWidget.remove.connect(self.removeClicked)
            self.tagListLayout.addWidget(tagWidget)
            self.addEdit.setText("")
            self.tagListLayout.update()

    def cancelButtonClicked(self):
        self.reload()

    def saveButtonClicked(self):
        self.container.experiment.clear_tags()
        for i in range(self.tagListLayout.count()):
            item = self.tagListLayout.itemAt(i)
            widget = item.widget()
            if widget:
                self.container.experiment.add_tag(widget.content())
        self.container.emit(BiExperimentStates.TagsModified)

    def removeClicked(self, tag: str):
        for i in range(self.tagListLayout.count()):
            item = self.tagListLayout.itemAt( i )
            widget = item.widget()
            if widget:
                if widget.content() == tag:
                    itemd = self.tagListLayout.takeAt( i )
                    itemd.widget().deleteLater()
        self.tagListWidget.adjustSize() 

    def get_widget(self):
        return self.widget   

class BiExperimentTagsUsingSeparatorsComponent(BiComponent):
    def __init__(self, experimentContainer: BiExperimentContainer, addTagsContainer: BiExperimentAddTagsContainer):
        super(BiExperimentTagsUsingSeparatorsComponent, self).__init__()
        self._object_name = 'BiExperimentTagsUsingSeparatorsComponent'
        self.experimentContainer = experimentContainer
        self.experimentContainer.register(self)  
        self.addTagsContainer = addTagsContainer
        self.addTagsContainer.register(self)  
        self._tagsEdit = []
        self._separatorEdit = []
        self._positionSpinBox = []

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Tag using separator"))
        title.setObjectName("BiLabelFormHeader1")

        gridWidget = QWidget()
        self.gridLayout = QGridLayout()
        gridWidget.setLayout(self.gridLayout)

        tagLabel = QLabel(self.widget.tr("Tag"))
        separatorLabel = QLabel(self.widget.tr("Separator"))
        positionLabel = QLabel(self.widget.tr("Position"))

        tagsEdit = QLineEdit()
        self._tagsEdit.append(tagsEdit)
        separatorEdit = QLineEdit()
        self._separatorEdit.append(separatorEdit)
        positionSpinBox = QSpinBox()
        self._positionSpinBox.append(positionSpinBox)

        addLineButton = QPushButton(self.widget.tr("Add line"))
        addLineButton.setObjectName('btnDefault')
        addLineButton.released.connect(self.addLine)

        validateButton = QPushButton(self.widget.tr("Validate"))
        validateButton.setObjectName('btnPrimary')
        validateButton.released.connect(self.validated)

        layout.addWidget(title, 0, 0, 1, 3)
        
        self.gridLayout.addWidget(tagLabel, 0, 0)
        self.gridLayout.addWidget(separatorLabel, 0, 1)
        self.gridLayout.addWidget(positionLabel, 0, 2)

        self.gridLayout.addWidget(tagsEdit, 1, 0)
        self.gridLayout.addWidget(separatorEdit, 1, 1)
        self.gridLayout.addWidget(positionSpinBox, 1, 2)

        layout.addWidget(gridWidget, 1, 0, 1, 3)
        layout.addWidget(addLineButton, 2, 0)
        layout.addWidget(validateButton, 3, 2)

    def validated(self):
        tags = []
        separator = []
        position = []
        for tag in self._tagsEdit:
            tags.append(tag.text())    
        for sep in self._separatorEdit:
            separator.append(sep.text())
        for pos in self._positionSpinBox:
            position.append(pos.value())    

        self.addTagsContainer.usingseparator_tags = tags
        self.addTagsContainer.usingseparator_separator = separator
        self.addTagsContainer.usingseparator_position = position
        self.addTagsContainer.emit(BiExperimentAddTagsStates.ValidatedUsingSeparator)

    def addLine(self):
        tagsEdit = QLineEdit()
        self._tagsEdit.append(tagsEdit)
        separatorEdit = QLineEdit()
        self._separatorEdit.append(separatorEdit)
        positionSpinBox = QSpinBox()
        self._positionSpinBox.append(positionSpinBox)

        rowIdx = self.gridLayout.count()
        self.gridLayout.addWidget(tagsEdit, rowIdx, 0)
        self.gridLayout.addWidget(separatorEdit, rowIdx, 1)
        self.gridLayout.addWidget(positionSpinBox, rowIdx, 2)

    def update(self, action: BiAction):
        pass    

    def get_widget(self):
        return self.widget  

class BiExperimentTagsUsingNameComponent(BiComponent):
    def __init__(self, experimentContainer: BiExperimentContainer, addTagsContainer: BiExperimentAddTagsContainer):
        super(BiExperimentTagsUsingNameComponent, self).__init__()
        self._object_name = 'BiExperimentTagsUsingNameComponent'
        self.experimentContainer = experimentContainer
        self.experimentContainer.register(self)  
        self.addTagsContainer = addTagsContainer
        self.addTagsContainer.register(self) 
        self._namesEdit = []

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Tag using name"))
        title.setObjectName("BiLabelFormHeader1")

        tagLabel = QLabel(self.widget.tr("Tag:"))
        self.tagEdit = QLineEdit()

        searchLabel = QLabel(self.widget.tr("Search names:"))
        searchWidget = QWidget()
        self.searchLayout = QVBoxLayout()
        self.searchLayout.setContentsMargins(0,0,0,0)
        searchWidget.setLayout(self.searchLayout)

        nameEdit = QLineEdit()
        self._namesEdit.append(nameEdit)
        self.searchLayout.addWidget(nameEdit)

        addLineButton = QPushButton(self.widget.tr("Add name"))
        addLineButton.setObjectName('btnDefault')
        addLineButton.released.connect(self.addLine)

        validateButton = QPushButton(self.widget.tr("Validate"))
        validateButton.setObjectName('btnPrimary')
        validateButton.released.connect(self.validated)

        layout.addWidget(title, 0, 0)
        layout.addWidget(tagLabel, 1, 0, 1, 1, PySide2.QtCore.Qt.AlignTop)
        layout.addWidget(self.tagEdit, 1, 1)
        layout.addWidget(searchLabel, 2, 0, 1, 1, PySide2.QtCore.Qt.AlignTop )
        layout.addWidget(searchWidget, 2, 1)
        layout.addWidget(addLineButton, 3, 1)
        layout.addWidget(validateButton, 4, 2)

    def validated(self):
        names = []
        for name in self._namesEdit:
            names.append(name.text())
        self.addTagsContainer.usingname_tag = self.tagEdit.text()
        self.addTagsContainer.usingname_search = names
        self.addTagsContainer.emit(BiExperimentAddTagsStates.ValidatedUsingName)

    def addLine(self):
        nameEdit = QLineEdit()
        self._namesEdit.append(nameEdit)
        self.searchLayout.addWidget(nameEdit)

    def update(self, action: BiAction):
        pass    

    def get_widget(self):
        return self.widget          

class BiExperimentTagsComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer, addTagsContainer: BiExperimentAddTagsContainer):
        super(BiExperimentTagsComponent, self).__init__()
        self._object_name = 'BiExperimentTagsComponent'
        self.container = container
        self.container.register(self) 
        self.addTagsContainer = addTagsContainer
        self.addTagsContainer.register(self)    

        self.widget = QWidget()
        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)

        tagsListComponent = BiExperimentTagsListComponent(self.container)
        tagUsingSeparatorComponent = BiExperimentTagsUsingSeparatorsComponent(self.container, self.addTagsContainer)
        tagUsingNameComponent = BiExperimentTagsUsingNameComponent(self.container, self.addTagsContainer)

        tabWidget.addTab(tagsListComponent.get_widget(), self.widget.tr("Tags"))
        tabWidget.addTab(tagUsingSeparatorComponent.get_widget(), self.widget.tr("Tag using separator"))
        tabWidget.addTab(tagUsingNameComponent.get_widget(), self.widget.tr("Tag using name"))

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget      

class BiExperimentImportSingleDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer, importContainer: BiExperimentImportDataContainer):
        super(BiExperimentImportSingleDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportSingleDataComponent'
        self.container = container
        self.container.register(self)  
        self.importContainer = importContainer
        self.importContainer.register(self) 

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Import single data"))
        title.setObjectName("BiLabelFormHeader1")

        dataLabel = QLabel(self.widget.tr("Data"))
        self.dataPath = QLineEdit()
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("BiBrowseButton")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        nameLabel = QLabel(self.widget.tr("Name"))
        self.nameEdit = QLineEdit()

        authorLabel = QLabel(self.widget.tr("Author"))
        self.authorEdit = QLineEdit()

        createddateLabel = QLabel(self.widget.tr("Created date"))
        self.createddateEdit = QLineEdit()

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btnPrimary")
        importButton.released.connect(self.importButtonClicked)

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(dataLabel, 1, 0)
        layout.addWidget(self.dataPath, 1, 1)
        layout.addWidget(browseDataButton, 1, 2)
        layout.addWidget(nameLabel, 2, 0)
        layout.addWidget(self.nameEdit, 2, 1, 1, 2)
        layout.addWidget(authorLabel, 3, 0)
        layout.addWidget(self.authorEdit, 3, 1, 1, 2)
        layout.addWidget(createddateLabel, 4, 0)
        layout.addWidget(self.createddateEdit, 4, 1, 1, 2)
        layout.addWidget(importButton, 5, 2, PySide2.QtCore.Qt.AlignRight)

    def update(self, container: BiContainer):
        pass

    def importButtonClicked(self):
        # origin/destination data file url
        originFile = self.dataPath.text()
        originFileInfo = QFileInfo(originFile)
        originfilename = originFileInfo.fileName()
        originBasename = originFileInfo.baseName()

        rawDataSetmdFileInfo = self.container.experiment.rawdataset().md_file_path()
        destinationFile = rawDataSetmdFileInfo + QDir.separator() + originfilename

        # meta data
        data_md_file = rawDataSetmdFileInfo + QDir.separator() + originBasename + ".md.json"

        print('import data to:', data_md_file)

        data = create_rawdata(data_md_file) 
        data.set_url(ntpath.basename(destinationFile))
        data.set_name(self.nameEdit.text())
        data.set_author(self.authorEdit.text())
        data.set_createddate(self.createddateEdit.text())
        data.set_datatype("image")
        data.set_thumbnail(originBasename + "_thumb.jpg")
        
        self.container.experiment.rawdataset().add_data(data)
        self.container.emit(BiExperimentStates.RawDataImported)

        self.importContainer.data = data
        self.importContainer.originFile = originFile
        self.importContainer.destinationFile = destinationFile
        self.importContainer.emit(BiExperimentImportDataStates.NewImport)

    def browseDataButtonClicked(self):
        fileName = QFileDialog.getOpenFileName(self.widget, self.widget.tr("Import file"), 'Data (*.*)')
        print('filename: ', fileName[0])
        self.dataPath.setText(fileName[0])

    def get_widget(self):
        return self.widget  


class BiExperimentImportDirectoryDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer, importContainer: BiExperimentImportDataContainer):
        super(BiExperimentImportDirectoryDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportDirectoryDataComponent'
        self.container = container
        self.container.register(self)  
        self.importContainer = importContainer
        self.importContainer.register(self) 

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QGridLayout()
        self.widget.setLayout(layout)

        # title
        title = QLabel(self.widget.tr("Import from folder"))
        title.setObjectName("BiLabelFormHeader1")

        dataLabel = QLabel(self.widget.tr("Folder"))
        self.dataPath = QLineEdit()
        browseDataButton = QPushButton(self.widget.tr("..."))
        browseDataButton.setObjectName("BiBrowseButton")
        browseDataButton.released.connect(self.browseDataButtonClicked)

        recursiveLabel = QLabel(self.widget.tr("Recursive"))
        self.recursiveBox = QCheckBox()
        self.recursiveBox.setChecked(True)

        filterLabel = QLabel(self.widget.tr("Filter"))
        self.filterComboBox = QComboBox()
        self.filterComboBox.addItem(self.widget.tr('Ends With'))
        self.filterComboBox.addItem(self.widget.tr('Start With'))
        self.filterComboBox.addItem(self.widget.tr('Contains'))
        self.filterEdit = QLineEdit()
        self.filterEdit.setText('.tif')

        copyDataLabel = QLabel(self.widget.tr("Copy data"))
        self.copyDataBox = QCheckBox()
        self.copyDataBox.setChecked(True)

        authorLabel = QLabel(self.widget.tr("Author"))
        self.authorEdit = QLineEdit()

        createddateLabel = QLabel(self.widget.tr("Created date"))
        self.createddateEdit = QLineEdit()

        importButton = QPushButton(self.widget.tr("import"))
        importButton.setObjectName("btnPrimary")
        importButton.released.connect(self.importButtonClicked)

        layout.addWidget(title, 0, 0, 1, 4)
        layout.addWidget(dataLabel, 1, 0)
        layout.addWidget(self.dataPath, 1, 1, 1, 2)
        layout.addWidget(browseDataButton, 1, 3)
        layout.addWidget(recursiveLabel, 2, 0)
        layout.addWidget(self.recursiveBox, 2, 1, 1, 2)
        layout.addWidget(filterLabel, 3, 0)
        layout.addWidget(self.filterComboBox, 3, 1, 1, 1)
        layout.addWidget(self.filterEdit, 3, 2, 1, 2)
        layout.addWidget(copyDataLabel, 4, 0)
        layout.addWidget(self.copyDataBox, 4, 1, 1, 2)
        layout.addWidget(authorLabel, 5, 0)
        layout.addWidget(self.authorEdit, 5, 1, 1, 2)
        layout.addWidget(createddateLabel, 6, 0)
        layout.addWidget(self.createddateEdit, 6, 1, 1, 2)
        layout.addWidget(importButton, 7, 3, PySide2.QtCore.Qt.AlignRight)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar, 8, 1, 1, 3)

    def update(self, action: BiAction):
        if action.state == BiExperimentImportDataStates.Progress:
            if 'progress' in self.importContainer.progress:
                self.progressBar.setVisible(True)
                self.progressBar.setValue(self.importContainer.progress)
                if self.importContainer.progress == 100:
                    self.progressBar.setVisible(False)
                 

    def importButtonClicked(self):

        self.importContainer.dir_data_path = self.dataPath.text()
        self.importContainer.dir_recursive = self.recursiveBox.isChecked()
        self.importContainer.dir_filter = self.filterComboBox.currentIndex()
        self.importContainer.dir_filter_value = self.filterEdit.text()
        self.importContainer.dir_copy_data = self.copyDataBox.isChecked()
        self.importContainer.author = self.authorEdit.text()
        self.importContainer.createddate = self.createddateEdit.text()
        self.importContainer.emit(BiExperimentImportDataStates.NewImportDir)

    def browseDataButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self.widget, self.widget.tr("Select Directory"),
                                       "",
                                       QFileDialog.ShowDirsOnly
                                       | QFileDialog.DontResolveSymlinks)
        self.dataPath.setText(directory)

    def get_widget(self):
        return self.widget  

class BiExperimentImportDataComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer, importContainer: BiExperimentImportDataContainer):
        super(BiExperimentImportDataComponent, self).__init__()
        self._object_name = 'BiExperimentImportDataComponent'
        self.container = container
        self.container.register(self)  
        self.importContainer = importContainer
        self.importContainer.register(self) 

        self.widget = QWidget()
        self.widget.setObjectName("BiWidget")

        layout = QVBoxLayout()
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)
        self.widget.setLayout(layout)

        importSingleComponent = BiExperimentImportSingleDataComponent(container, importContainer)
        tabWidget.addTab(importSingleComponent.get_widget(), self.widget.tr("Single Data"))

        importDirectoryComponent = BiExperimentImportDirectoryDataComponent(container, importContainer)
        tabWidget.addTab(importDirectoryComponent.get_widget(), self.widget.tr("Multiple Data"))

    def update(self, action: BiAction):
        pass

    def get_widget(self):
        return self.widget


class BiExperimentTitleToolBarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentTitleToolBarComponent, self).__init__()
        self._object_name = 'BiExperimentTitleToolBarComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        self.widget.setObjectName("BiToolBar")
        layout = QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # title
        layout.addWidget(QWidget(), 1)
        self.titleLabel = QLabel("default Title")
        layout.addWidget(self.titleLabel, 0, PySide2.QtCore.Qt.AlignRight)
        self.titleLabel.setObjectName("BiExperimentTitleToolBarTitle")

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded or action.state == BiExperimentStates.InfoModified:
            self.titleLabel.setText(self.container.experiment.name())

    def get_widget(self):
        return self.widget          


class BiExperimentToolBarComponent(BiComponent):
    def __init__(self, container: BiExperimentContainer):
        super(BiExperimentToolBarComponent, self).__init__()
        self._object_name = 'BiExperimentToolBarComponent'
        self.container = container
        self.container.register(self)  

        self.widget = QWidget()
        self.widget.setObjectName("BiToolBar")
        layout = QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(7,0,7,0)
        self.widget.setLayout(layout)

        # settings
        settingsButton = QToolButton()
        settingsButton.setObjectName("BiExperimentToolBarSettingsButton")
        settingsButton.setToolTip(self.widget.tr("Application settings"))
        settingsButton.released.connect(self.settingsButtonClicked)
        layout.addWidget(settingsButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # info
        openInfoButton = QToolButton()
        openInfoButton.setObjectName("BiExperimentToolBarInfoButton")
        openInfoButton.setToolTip(self.widget.tr("Project informations"))
        openInfoButton.released.connect(self.infoButtonClicked)
        layout.addWidget(openInfoButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # import
        importButton = QToolButton()
        importButton.setObjectName("BiExperimentToolBarImportButton")
        importButton.setToolTip(self.widget.tr("Import data"))
        importButton.released.connect(self.importButtonClicked)
        layout.addWidget(importButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # Tags
        tagsButton = QToolButton()
        tagsButton.setObjectName("BiExperimentToolBarTagsButton")
        tagsButton.setToolTip(self.widget.tr("Tags"))
        tagsButton.released.connect(self.tagsButtonClicked)
        layout.addWidget(tagsButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # data selector
        self.dataCombo = QComboBox()
        self.dataCombo.addItem("Data")
        self.dataCombo.currentTextChanged.connect(self.dataComboChanged)
        layout.addWidget(self.dataCombo, 0, PySide2.QtCore.Qt.AlignLeft)

        # refresh
        refreshButton = QToolButton()
        refreshButton.setObjectName("BiExperimentToolBarRefreshButton")
        refreshButton.setToolTip(self.widget.tr("Refresh"))
        refreshButton.released.connect(self.refreshButtonClicked)
        layout.addWidget(refreshButton, 0, PySide2.QtCore.Qt.AlignLeft)

        layout.addWidget(QWidget(), 1)

    def update(self, action: BiAction):
        if action.state == BiExperimentStates.Loaded or action.state == BiExperimentStates.NewProcessedDataSetLoaded:
            for i in range(self.container.experiment.processeddatasets_size()):
                processedDataSet = self.container.experiment.processeddataset(i)
                # add the dataset to the list only if it is not already in
                found = False
                for n in range(self.dataCombo.count()):
                    if self.dataCombo.itemText(n) == processedDataSet.name():
                        found = True  
                        break
                if not found:
                    self.dataCombo.addItem(processedDataSet.name())
        
    def settingsButtonClicked(self):
        self.container.emit(BiExperimentStates.SettingsClicked)

    def infoButtonClicked(self):
        self.container.emit(BiExperimentStates.InfoClicked)

    def dataComboChanged(self, text: str):
        self.container.changed_combo_txt = text
        self.container.emit(BiExperimentStates.DataSetComboChanged)

    def refreshButtonClicked(self):
        self.container.emit(BiExperimentStates.RefreshClicked)

    def importButtonClicked(self):
        self.container.emit(BiExperimentStates.ImportClicked)

    def tagsButtonClicked(self):    
        self.container.emit(BiExperimentStates.TagsClicked)

    def get_widget(self):
        return self.widget      

