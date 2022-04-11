"""Implements scene items for the designer


Classes
-------
BiDedignerViewItem
BiDesignerViewPort

"""

import qtpy.QtCore
from qtpy.QtCore import QPointF
from qtpy.QtGui import QPainterPath, QPen, QFontMetrics, QFont, QColor, QGradient, QLinearGradient
from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsScene, QGraphicsPathItem, QGraphicsItem, QGraphicsTextItem


class BiDesignerViewItem(QGraphicsPathItem):
    def __init__(self, parent: QGraphicsItem, scene: QGraphicsScene):
        super().__init__(parent)
        self.scene = scene
        self.useWidget = False
        self.name = ''
        self.settingWidget = None
        self.widget = None

    def type(self):
        return QGraphicsItem.UserType

    def setName(self, name):
        self.name = name

    def setSettingWidget(self, widget):
        self.settingWidget = widget

    def setWidget(self, widget):
        self.useWidget = True
        self.widget = widget


class BiDesignerViewPort(BiDesignerViewItem):
    Type = QGraphicsItem.UserType + 1
    NamePort = 1
    TypePort = 2

    def __init__(self, parent: QGraphicsItem, scene: QGraphicsScene):
        super().__init__(parent, scene)

        self.block = None # BiDesignerViewNode
        self.typeId = ''
        self.isOutput = False
        self.isInput = False
        self.label = QGraphicsTextItem(self)
        self.radius = 3
        self.margin = 2
        self.connections = [] # QVector<khComposerViewConnection*>
        self.portFlags = 0
        self.ptr = 0

        self.label.setDefaultTextColor( QColor(255, 255, 255) )

        p = QPainterPath()
        p.addEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
        self.setPath(p)
        self.setPen(QPen(qtpy.QtCore.Qt.darkGray))
        self.setBrush(qtpy.QtCore.Qt.gray)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

    def __del__(self):  
        for conn in self.connections:
            del conn

    def type(self):
        return QGraphicsItem.UserType +1

    def setNode(self, b):
        """
        Parameters
        ----------
        b: BiDesignerViewNode
            Node
        """
        self.block = b

    def setName(self, name):
        self.name = name
        self.label.setPlainText(name)

    def setTypeId(self, typeId):
        self.typeId = typeId

    def setIsInputOutput(self, isInput, isOutput ):
        self.isOutput = isOutput
        self.isInput = isInput

        fm = QFontMetrics(self.scene.font())

        if self.isOutput:
            self.label.setPos(-self.radius - self.margin - self.label.boundingRect().width(), -self.label.boundingRect().height()/2)
        else:
            self.label.setPos(self.radius + self.margin, -self.label.boundingRect().height()/2)

    def setPortFlags(self, f: int):
        self.portFlags = f

        if self.portFlags == BiDesignerViewPort.TypePort:
            font = QFont(self.scene().font())
            font.setItalic(True)
            self.label.setFont(font)
            self.setPath(QPainterPath())
        elif self.portFlags == BiDesignerViewPort.NamePort:
            font = QFont(self.scene.font())
            font.setBold(True)
            self.label.setFont(font)
            self.setPath(QPainterPath())

    def node(self):
        return self.block

    def isConnected(self, other):
        #other: khComposerViewPort
        for conn in self.connections:
            if conn.port1 == other or conn.port2 == other:
                return True
        return False

    def itemChange(self, change, value):
        #  GraphicsItemChange change, const QVariant &value
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            for conn in self.connections:
                conn.updatePosFromPorts()
                conn.updatePath()
        return value
   

class BiDesignerViewNode(BiDesignerViewItem):
    print('create the view Node')
    Type = QGraphicsItem.UserType + 3

    def __init__(self, parent, scene):
        super().__init__(parent, scene)

        p = QPainterPath()
        p.addRoundedRect(-50, -15, 100, 30, 5, 5)
        self.setPath(p)
        self.setPen(QPen(qtpy.QtCore.Qt.darkRed))
        self.setBrush(qtpy.QtCore.Qt.darkRed)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.horzMargin = 100
        self.vertMargin = 15
        self.width =self.horzMargin
        self.height_right = self.vertMargin
        self.height_left = self.vertMargin

        # information for the pipeline
        self.uuid = -1
        self.node_type = ''
        self.widget = None

        self.scene.addItem(self)
        self.ports = []

    def type(self):
        return QGraphicsItem.UserType +3

    def addPort(self, name, typeName, isOutput, isInput, flags=0, ptr=0):
        fm = QFontMetrics(self.scene.font())
        w = fm.width(name)
        h = fm.height()
        if typeName == '':
            nameLines = name.split("\n")
            h = (h)*(len(nameLines)) + h/2
            maxi = 0
            val = 0
            for tname in nameLines:
                val = fm.width(tname)
                if val > maxi:
                    maxi = val
            w = maxi
        if ptr == BiDesignerViewPort.NamePort:
            self.name = name
        
        port = BiDesignerViewPort(self, self.scene)
        port.setName(name)
        port.setTypeId(typeName)
        port.setIsInputOutput(isInput, isOutput)
        port.setNode(self)
        port.setPortFlags(flags)
        #port.setPtr(ptr)

        if w > self.width - self.horzMargin:
            self.width = w + self.horzMargin

        if port.isOutput:
            self.height_right += h
        elif port.isInput:
            self.height_left += h
        else:
            if len(name.split("\n")) > 1:
                self.height_right += h+5
                self.height_left += h+5
            else:
                self.height_right += h
                self.height_left += h

        p = QPainterPath()
        if self.height_right > self.height_left:
            p.addRoundedRect(-self.width/2+5, -self.height_right/2+5, self.width-10, self.height_right+5, 5, 5)
        else:
            p.addRoundedRect(-self.width/2+5, -self.height_left/2+5, self.width-10, self.height_left+5, 5, 5)

        self.setPath(p)

        y_left = -self.height_left / 2 + self.vertMargin + port.radius
        y_right = -self.height_right / 2 + self.vertMargin + port.radius
        for port_ in self.childItems():
            port = port_
            if port.isOutput:
                port.setPos(self.width/2 - 2*port.radius, y_right+h)
                y_right+=h
            elif port.isInput:
                port.setPos(-self.width/2 + 2*port.radius, y_left+h)
                y_left += h
            else:
                if len(port.name.split("\n")) > 1:
                    port.setPos(-self.width/2 + 2*port.radius, y_left+5)
                    y_left += h+5
                    y_right+=h+5
                else:
                    port.setPos(-self.width/2 + 2*port.radius, y_left)
                    y_left += h
                    y_right+=h
        self.ports.append(port)            
        return port

    def addInputPort(self, name, typeName):
        self.addPort(name, typeName, False, True)

    def addOutputPort(self, name, typeName):
        self.addPort(name, typeName, True, False)
    
    def addInputPorts(self, names, typeName):
        for i, _ in enumerate(names):
            self.addInputPort(names[i], typeName[i])

    def addOutputPorts(self, names, typeName):
        for i, _ in enumerate(names):
            self.addOutputPort(names[i], typeName[i])

    def paint(self, painter, option, widget):
        """Paint the item 

        Parameters
        ----------
        painter: QPainter
            Painter object
        option: QStyleOptionGraphicsItem
            Options for the painting style     
        widget: Widget  
            Parent widget

        """
        if self.isSelected():
            pen = QPen()
            pen.setColor(QColor(183, 130, 237, 255))
            pen.setWidth(3)
            painter.setPen(pen)
        else:
            pen = QPen()
            if self.node_type == "Data" or self.node_type == "Save":
                pen.setColor(QColor(0, 115, 0, 127))
            elif self.node_type == "Process":
                pen.setColor(QColor(0, 113, 195, 127)) 
            pen.setWidth(3)
            painter.setPen(pen)     

        startPoint = QPointF(0.0,0.0)
        endPoint = QPointF(0.0,150.0)
        gradient = QLinearGradient(startPoint, endPoint)

        if self.node_type == 'Data' or self.node_type == 'Save':
            gradient.setColorAt(0.1,QColor(0, 115, 0, 127))
            gradient.setColorAt(0.3,QColor(0, 115, 0, 155))
            gradient.setColorAt(0.8,QColor(0, 115, 0, 200))
            gradient.setColorAt(0.9,QColor(0, 115, 0, 255))
        if self.node_type == "Process":
            gradient.setColorAt(0.1,QColor(0, 113, 195, 127))
            gradient.setColorAt(0.3,QColor(0, 113, 195, 155))
            gradient.setColorAt(0.9,QColor(0, 113, 195, 200))
            gradient.setColorAt(0.9,QColor(0, 113, 195, 255))
        
        gradient.setSpread(QGradient.PadSpread)
        painter.setBrush(gradient)
        painter.drawPath(self.path())

    def ports(self):
        res = []
        for port_ in self.childItems():
            if port_.type == BiDesignerViewPort.Type:
                res.append(port_)
        return res

    def itemChange(self, change, value):
        return value

    def nodeName(self):
        return self.name


class TmpParameterWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setObjectName('bi-widget')
        layout.addWidget(QLabel(title))


class BiDesignerViewNodeSave(BiDesignerViewNode):
    def __init__(self, uuid, parent, scene):
        super().__init__(parent, scene)
        self.uuid = uuid
        print('create node save')
        self.name = 'Save'
        self.id = f"#{uuid}: Save"
        self.node_type = 'Save'
        self.addPort( f"#{uuid}: Save", "", False, False, BiDesignerViewPort.NamePort, None)
        self.addInputPort('Any', 'Any')
        self.widget = TmpParameterWidget('This is the Save Node parameter widget') # TODO implement the real widget

    def set_pos(self, x, y):
        self.setPos(x, y) 


class BiDesignerViewNodeData(BiDesignerViewNode):
    def __init__(self, uuid, parent, scene):
        super().__init__(parent, scene)
        self.name = 'Data'
        self.id = f"#{uuid}: Data"
        self.node_type = 'Data'
        self.addPort( f"#{uuid}: Data", "", False, False, BiDesignerViewPort.NamePort, None)
        self.addOutputPort('Any', 'Any')
        self.processType = 'Save'
        self.widget = TmpParameterWidget('This is the Data Node parameter widget') # TODO implement the real widget

    def set_pos(self, x, y):
        self.setPos(x, y) 


class BiDesignerViewNodeTool(BiDesignerViewNode):
    def __init__(self, tool, uuid, parent, scene):
        super().__init__(parent, scene)
        self.name = 'Process'
        self.node_type = 'Process' 
        self.addPort( f"#{uuid}: {tool.name}", "", False, False, BiDesignerViewPort.NamePort, None)
        self.id = f"#{uuid}: {tool.name}"
        for input in tool.inputs:
            if input.is_data:
                self.addInputPort(input.description, input.type)
        for output in tool.outputs:
            self.addOutputPort(output.description, output.type)
        self.tool = tool   
        self.already_ran = False 
        self.widget = TmpParameterWidget('This is the Tool Node parameter widget') # TODO implement the real widget
        self.widget.setObjectName('bi-widget')
        
    def set_pos(self, x, y):
        self.setPos(x, y)    


class BiDesignerViewConnection(BiDesignerViewItem):
    Type = QGraphicsItem.UserType + 2

    def __init__(self, parent, scene):
        super().__init__(parent, scene)
        
        self.setPen(QPen(qtpy.QtCore.Qt.lightGray, 2))
        self.setBrush(qtpy.QtCore.Qt.NoBrush)
        self.setZValue(-1)
        self.port1 = None
        self.port2 = None
        self.pos1 = 0
        self.pos2 = 0
        self.scene.addItem(self)

    def __del__(self):    
        if self.port1:
            self.port1.connections.remove(self)
        if self.port2:
            self.port2.connections.remove(self)

    def type(self):
        return QGraphicsItem.UserType + 2

    def setPos1(self, p):
        self.pos1 = p

    def setPos2(self, p):
        self.pos2 = p

    def setPort1(self, p):
        self.port1 = p
        self.port1.connections.append(self)

    def setPort2(self, p):
        self.port2 = p
        self.port2.connections.append(self)

    def updatePosFromPorts(self):
        if self.pos1 is not None:
            self.pos1 = self.port1.scenePos()
        if self.pos2 is not None:    
            self.pos2 = self.port2.scenePos()

    def updatePath(self):
        p = QPainterPath()

        p.moveTo(self.pos1)

        dx = self.pos2.x() - self.pos1.x()
        dy = self.pos2.y() - self.pos1.y()

        ctr1 = QPointF(self.pos1.x() + dx * 0.7, self.pos1.y() + dy * 0.1)
        ctr2 = QPointF(self.pos1.x() + dx * 0.3, self.pos1.y() + dy * 0.9)

        p.cubicTo(ctr1, ctr2, self.pos2)

        self.setPath(p)
