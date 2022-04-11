from re import I
import qtpy.QtCore
from qtpy.QtCore import Signal, QObject, QTimeLine, QRectF, QPointF, QSize, QEvent
from qtpy.QtGui import QWheelEvent, QPainter, QBrush, qRgb, QCursor
from qtpy.QtWidgets import (QMenu, QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, 
                            QGraphicsSceneDragDropEvent, QGraphicsItem, QAction)

from ._scene_items import BiDesignerViewNode, BiDesignerViewPort, BiDesignerViewConnection


class BiDesignerGraphicScene(QGraphicsScene):
    ask_new_node = Signal(str, int, int)
    
    def __init__(self):
        super().__init__()

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        pass

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        pass

    def dropEvent(self, event: QGraphicsSceneDragDropEvent):    
        print("BiDesignerGraphicScene: dropEvent")
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            print("url = ", urls[0])
            self.ask_new_node.emit(urls[0].toString(), event.scenePos().toPoint().x(), event.scenePos().toPoint().y())


class BiDesignerViewNodesEditor(QObject):
    show_parameters = Signal(str)

    def __init__(self, editMode, parent):
        super().__init__(parent)
        self.conn = None
        self.editMode = editMode
        self.scene = None
        self.view = None

        self.clicked_node_uuid = -1
        self.clickedNodePosx = -1 # X position of the clicked process
        self.clickedNodePosy = -1 # Y position of the clicked process
        self.clickedTool = None
        self.docPath = '' # last doc URL

        # create context menu
        if self.editMode:
            self.actionParameters = QAction("Parameters", self)
            self.actionParameters.triggered.connect(self.parameters_node)
            self.actionDelete = QAction("Delete", self)
            self.actionDelete.triggered.connect(self.delete_node)
            self.actionDoc = QAction("Help", self)
            self.actionDoc.triggered.connect(self.AskDoc)

            self.menu = QMenu()
            self.menu.addAction(self.actionParameters)
            self.menu.addAction(self.actionDelete)
            self.menu.addSeparator()
            self.menu.addAction(self.actionDoc)
        else:
            self.actionDoc = QAction("Help", self)
            self.actionDoc.triggered.connect(self.AskDoc)
            m_menu = QMenu()
            m_menu.addAction(self.actionDoc)

    def install(self, scene: QGraphicsScene):
        scene.installEventFilter(self)
        self.scene = scene
    
    def setView(self, view: QGraphicsView):
        self.view = view    

    def itemAt(self, pos):
        items = self.scene.items(QRectF(pos - QPointF(1,1), QSize(3,3)))
        for item in items:  
            if item.type() > QGraphicsItem.UserType:
                return item
        return None
    
    def delete_node(self):
        # delete the block
        point = QPointF(self.clickedNodePosx, self.clickedNodePosy)
        item = self.itemAt(point)
        for port in item.ports:
            for conn in port.connections:
                self.scene.removeItem(conn)
        self.scene.removeItem(item)

    def parameters_node(self):
        point = QPointF(self.clickedNodePosx, self.clickedNodePosy)
        item = self.itemAt(point)
        print('BiDesignerViewNodesEditor: emit show parameter: ', item.id)
        self.show_parameters.emit(item.id)

    def AskDoc(self):
        self.docBlock.emit(self.docPath)

    def free(self):
        print("khComposerViewNodesEditor::free()")
        L = self.scene.items()
        while len(L) > 0:
            self.scene.removeItem( L.first() ) # this line isn't necessary --- item destructor will handle this
            item = L.first()
            del item
            L.removeFirst()
        print("khComposerViewNodesEditor::free() finish")   
        
    def eventFilter(self, obj, event): 
        """Filter the user mouse and keybord events
        
        Parameters
        ----------
        obj: QObject
            Origin object
        event: QEvent
            User input event    
        """
        #  QObject *o, QEvent *e
        event_type = event.type()    
        if event_type == QEvent.GraphicsSceneMousePress:
            button = event.button()
            if button == qtpy.QtCore.Qt.LeftButton:
                item = self.itemAt(event.scenePos())
                if item is not None and item.type() == BiDesignerViewPort.Type:
                    return self._create_connection(item, event)
            elif button == qtpy.QtCore.Qt.RightButton:
                item = self.itemAt(event.scenePos())
                if self.editMode:
                    if item is not None and item.type() == BiDesignerViewConnection.Type:
                        self._remove_connecttion(item)
                    elif item is not None and item.type() == BiDesignerViewNode.Type:
                        self._show_context_menu(item)
                else:
                    if item is not None and item.type() == BiDesignerViewNode.Type:
                        self._show_context_menu(item)

        elif event_type == QEvent.GraphicsSceneMouseMove:
            return self._draw_connection(event)

        elif event_type == QEvent.GraphicsSceneMouseRelease:
            return self._ends_connection(event)
            
        elif event_type == QEvent.GraphicsSceneMouseDoubleClick:
            item = self.itemAt(event.scenePos())
            if item is not None and item.type() == BiDesignerViewNode.Type:
                return self._show_node_widget(item)

        #return False
        return QObject.eventFilter(self, obj, event)  
    
    def _create_connection(self, item, event):
        if self.editMode:
            print('create connection')
            self.conn = BiDesignerViewConnection(None, self.scene)
            self.conn.setPort1(item)
            self.conn.setPos1(item.scenePos())
            self.conn.setPos2(event.scenePos())
            self.conn.updatePath()
        return True    

    def _remove_connecttion(self, item):
        self.scene.removeItem(item) 
        #return True 

    def _show_context_menu(self, item):
        self.clicked_node_uuid = item.uuid
        if item.node_type == 'Process':
            # Process menu
            self.clickedTool = item.tool
            self.clickedNodePosx = item.scenePos().x()
            self.clickedNodePosy = item.scenePos().y()
            self.docPath = item.nodeName()
            self.menu.exec_(QCursor.pos())    
        else:
            # I/O menu
            self.clickedNodePosx = item.scenePos().x()
            self.clickedNodePosy = item.scenePos().y()
            self.docPath = item.nodeName()
            self.menu.exec_(QCursor.pos())   
        return True      

    def  _draw_connection(self, event):
        if self.conn is not None:
            self.conn.setPos2(event.scenePos())
            self.conn.updatePath()
        #return True        

    def _show_node_widget(self, item):
        self.show_parameters.emit(item.id)
        #return True

    def _ends_connection(self, event):
        if self.conn is not None and event.button() == qtpy.QtCore.Qt.LeftButton:
            item = self.itemAt(event.scenePos())
            if item is not None and item.type() == BiDesignerViewPort.Type:
                port1 = self.conn.port1
                port2 = item
                if port1.node() != port2.node() and port1.isOutput != port2.isOutput and not port1.isConnected(port2) and (port1.typeId == port2.typeId or port1.typeId=='Any' or port2.typeId=='Any'):
                    self.conn.setPos2(port2.scenePos())
                    self.conn.setPort2(port2)
                    self.conn.updatePath()
                    self.conn = None
                    return True
                else:
                    self.scene.removeItem(self.conn)
            else:
                self.scene.removeItem(self.conn)

            del self.conn
            self.conn = None
            return True        


class BiDesignerGraphicView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=0):
        super().__init__(scene, parent)   
        self._numScheduledScalings = 0 
        self.setAcceptDrops(True)

    def scalingTime(self, x):
        factor = 1.0 + float(self._numScheduledScalings) / 300.0
        self.scale(factor, factor)

    def animFinished(self):
        if (self._numScheduledScalings > 0):
            self._numScheduledScalings-=1
        else:
            self._numScheduledScalings+=1
        #self.sender().~QObject()
        #del self.sender()

    def wheelEvent (self, event: QWheelEvent ):
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15  # see QWheelEvent documentation
        self._numScheduledScalings += numSteps
        if (self._numScheduledScalings * numSteps < 0):  # if user moved the wheel in another direction, we reset previously scheduled scalings
            self._numScheduledScalings = numSteps
        anim = QTimeLine(350, self)
        anim.setUpdateInterval(20)
        anim.valueChanged.connect(self.scalingTime)
        anim.finished.connect(self.animFinished)
        anim.start()


class BiDesignerView(QWidget):
    def __init__(self):
        super().__init__()
    
        self.scene = BiDesignerGraphicScene()
        #connect(m_scene, SIGNAL(askNewNode(QString,int,int)), this, SLOT(addNode(QString, int, int)))

        self.view = BiDesignerGraphicView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.view.setBackgroundBrush(QBrush(qRgb(245,245,245), qtpy.QtCore.Qt.CrossPattern))

        self.nodesEditor = BiDesignerViewNodesEditor(True, self)
        self.nodesEditor.install(self.scene)
        self.nodesEditor.setView(self.view)
        #connect(m_nodesEditor, SIGNAL(clone(QString,int,int)), this, SLOT(addBlockByName(QString,int,int)))
        #connect(m_nodesEditor, SIGNAL(deleteBlock(QString)), this, SLOT(deleteNode(QString)))
        #connect(m_nodesEditor, SIGNAL(docBlock(QString)), this, SLOT(emitAskDocBlock(QString)))
    
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.b = BiDesignerViewNode(None, self.scene)
        self.b.processType = 'process'
        self.b.addPort( "#2: Spitfire", "", False, False, BiDesignerViewPort.NamePort, None)
        self.b.addInputPorts(['Image'], ['imagetiff'])
        self.b.addOutputPorts(['Image'], ['imagetiff'])

        self.b1 = BiDesignerViewNode(None, self.scene)
        self.b1.processType = 'I/O'
        self.b1.addPort( "#1: Data", "", False, False, BiDesignerViewPort.NamePort, None)
        self.b1.addOutputPorts(['Image'], ['imagetiff'])


        self.b3 = BiDesignerViewNode(None, self.scene)
        self.b3.processType = 'save'
        self.b3.addPort( "#3: Save", "", False, False, BiDesignerViewPort.NamePort, None)
        self.b3.addInputPorts(['Image'], ['imagetiff'])

        self.b3 = BiDesignerViewNode(None, self.scene)
        self.b3.processType = 'process'
        self.b3.addPort( "#4: Threshold particles", "", False, False, BiDesignerViewPort.NamePort, None)
        self.b3.addInputPorts(['Image'], ['imagetiff'])
        self.b3.addOutputPorts(['draw', 'count', "measure"], ['imagetiff', 'Number', 'csv'])

        self.scene.update()
