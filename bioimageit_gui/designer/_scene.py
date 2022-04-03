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
    clone = Signal(str, int, int)
    deleteBlock = Signal(str)
    docBlock = Signal(str)

    def __init__(self, editMode, parent):
        super().__init__(parent)
        self.conn = None
        self.editMode = editMode
        self.scene = None
        self.view = None

        self.clickedProcessId = '' # id of the clicked process
        self.clickedPluginPath = '' # Url of the clicked process
        self.clickedPluginPosx = -1 # X position of the clicked process
        self.clickedPluginPosy = -1 # Y position of the clicked process
        self.docPath = '' # last doc URL

        # create context menu
        if self.editMode:
            self.actionClone = QAction("Clone", self)
            self.actionClone.triggered.connect(self.AskClone)
            self.actionDelete = QAction("Delete", self)
            self.actionDelete.triggered.connect(self.AskDelete)
            self.actionDoc = QAction("Doc", self)
            self.actionDoc.triggered.connect(self.AskDoc)

            self.menu = QMenu()
            self.menu.addAction(self.actionClone)
            self.menu.addAction(self.actionDelete)
            self.menu.addSeparator()
            self.menu.addAction(self.actionDoc)
        else:
            self.actionDoc = QAction("Doc", self)
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
        print('itemAt -> items:', items)
        for item in items:  
            print('item user type = ', QGraphicsItem.UserType)
            print('item type = ', item.type())
            if item.type() > QGraphicsItem.UserType:
                return item
        return None

    def AskClone(self):
        self.clone.emit(self.clickedPluginPath, self.clickedPluginPosx + 15, self.clickedPluginPosy + 15)
    

    def AskDelete(self):
        # delete the block
        point = QPointF(self.clickedPluginPosx, self.clickedPluginPosy)
        item = self.itemAt(point)
        del item

        # delete the settings widgets
        self.deleteBlock.emit(self.clickedProcessId)

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
        
    def eventFilter(self, obj, e): #  QObject *o, QEvent *e

        event_type = e.type()    
        
        if event_type == QEvent.GraphicsSceneMousePress:
            button = e.button()
            if button == qtpy.QtCore.Qt.LeftButton:
                item = self.itemAt(e.scenePos())
                print('left click item=', item)
                if item is not None and item.type() == BiDesignerViewPort.Type:
                    print('item is recognized as viewport=')
                    if self.editMode:
                        print('create connection')
                        self.conn = BiDesignerViewConnection(None, self.scene)
                        self.conn.setPort1(item)
                        self.conn.setPos1(item.scenePos())
                        self.conn.setPos2(e.scenePos())
                        self.conn.updatePath()
                        return True
            elif button == qtpy.QtCore.Qt.RightButton:
                #print('event type = ', event_type)
                #print('is edit mode:', self.editMode)
                item = self.itemAt(e.scenePos())
                #print('item=', item)
                if self.editMode:
                    if item is not None and item.type() == BiDesignerViewConnection.Type:
                        del item
                    elif item is not None and item.type() == BiDesignerViewNode.Type:
                        self.clickedProcessId = item.process.id + " " + item.process.name
                        self.clickedPluginPath = item.process.name
                        self.clickedPluginPosx = item.scenePos().x()
                        self.clickedPluginPosy = item.scenePos().y()
                        self.docPath = item.nodeName()
                        self.menu.exec_(QCursor.pos())
                else:
                    if item is not None and item.type() == BiDesignerViewNode.Type:
                        self.clickedProcessId = item.process().processId() + " " + item.process().processName()
                        self.clickedPluginPath = item.process().processName()
                        self.clickedPluginPosx = item.scenePos().x()
                        self.clickedPluginPosy = item.scenePos().y()
                        self.docPath = item.nodeName()
                        self.menu.exec_(QCursor.pos())
        elif event_type == QEvent.GraphicsSceneMouseMove:
            if self.conn is not None:
                self.conn.setPos2(e.scenePos())
                self.conn.updatePath()
                return True
        elif event_type == QEvent.GraphicsSceneMouseRelease:
            print('release event')
            if self.conn is not None and e.button() == qtpy.QtCore.Qt.LeftButton:
                item = self.itemAt(e.scenePos())
                print('release event item=', item)
                if item is not None and item.type() == BiDesignerViewPort.Type:
                    print('release event item=', item)
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

        elif event_type == QEvent.GraphicsSceneMouseDoubleClick:
            item = self.itemAt(e.scenePos())
            if item is not None and item.type() == BiDesignerViewNode.Type:
                if item.useWidget():
                    w = item.widget()
                    w.move(QCursor.pos().x(), QCursor.pos().y())
                    w.show()

        #return False
        return QObject.eventFilter(self, obj, e)  
    

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
