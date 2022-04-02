import qtpy.QtCore
from qtpy.QtCore import Signal, QObject, QTimeLine
from qtpy.QtGui import QWheelEvent, QPainter, QBrush, qRgb
from qtpy.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsSceneDragDropEvent

from ._scene_items import BiDesignerViewNode, BiDesignerViewPort


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
    def __init__(self, editMode, parent):
        super().__init__(parent)
        self.conn = 0
        self.editMode = editMode
        self.scene = None
        self.view = None

    def install(self, scene: QGraphicsScene):
        scene.installEventFilter(self)
        self.scene = scene
    
    def setView(self, view: QGraphicsView):
        self.view = view;    


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
        #self.sender()->~QObject();
        #del self.sender()

    def wheelEvent (self, event: QWheelEvent ):
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15;  # see QWheelEvent documentation
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
        #connect(m_scene, SIGNAL(askNewNode(QString,int,int)), this, SLOT(addNode(QString, int, int)));

        self.view = BiDesignerGraphicView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.view.setBackgroundBrush(QBrush(qRgb(245,245,245), qtpy.QtCore.Qt.CrossPattern))

        self.nodesEditor = BiDesignerViewNodesEditor(True, self)
        self.nodesEditor.install(self.scene)
        self.nodesEditor.setView(self.view)
        #connect(m_nodesEditor, SIGNAL(clone(QString,int,int)), this, SLOT(addBlockByName(QString,int,int)));
        #connect(m_nodesEditor, SIGNAL(deleteBlock(QString)), this, SLOT(deleteNode(QString)));
        #connect(m_nodesEditor, SIGNAL(docBlock(QString)), this, SLOT(emitAskDocBlock(QString)));
    
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
