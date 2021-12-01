"""Set of basic widgets for BioImageIT

Classes
-------
BiButton
BiToolButton
BiFileSelectWidget
BiDragLabel
BiTagWidget
BiWebBrowser
BiFlowLayout
BiNavigationBar
BiHideableWidget
BiClosableButton
BiStaticStackedWidget
BiSlidingStackedWidget

"""

import qtpy.QtCore
from qtpy.QtCore import (QMimeData, QSize, QRect, QPoint, QPropertyAnimation, 
                            QEasingCurve, QParallelAnimationGroup)
from qtpy.QtGui import QMouseEvent, QDrag, QCursor, QIcon, QStandardItemModel
from qtpy.QtWidgets import (QWidget, QLabel, QPushButton, QToolButton, QTreeView,
                               QFileDialog, QHBoxLayout, QLineEdit, QVBoxLayout,
                               QLayout, QLayoutItem, QSizePolicy, QStyle, QStackedWidget)
from qtpy.QtCore import Signal, Slot, QUrl 


class BiButton(QPushButton):
    clickedId = Signal(int)
    clickedContent = Signal(str)

    def __init__(self, title: str, parent: QWidget = None):
        super(BiButton, self).__init__(title, parent)
        #self.setCursor(QCursor(qtpy.QtCore.Qt.PointingHandCursor))
        self.pressed.connect(self.emitClicked)
        self.id = 0
        self.content = ''

    def emitClicked(self):
        self.clickedId.emit(self.id)
        self.clickedContent.emit(self.content)


class BiToolButton(QToolButton):
    clickedId = Signal(int)
    clickedContent = Signal(str)

    def __init__(self, parent: QWidget = None):
        super(BiToolButton, self).__init__(parent)
        self.pressed.connect(self.emitClicked)
        self.id = 0
        self.content = ''

    def emitClicked(self):
        self.clickedId.emit(self.id)
        self.clickedContent.emit(self.content)        


class BiFileSelectWidget(QWidget):
    TextChangedSignal = Signal()
    TextChangedIdSignal = Signal(int)

    def __init__(self, isDir: bool, parent: QWidget):
        super().__init__(parent)

        self.id = -1
        self.isDir = isDir

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.lineEdit = QLineEdit()
        self.lineEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        layout.addWidget(self.lineEdit)

        browseButton = QPushButton("...")
        browseButton.setObjectName("BiBrowseButton")
        layout.addWidget(browseButton, 0, qtpy.QtCore.Qt.AlignRight)
        browseButton.released.connect(self.browseClicked)

    def setText(self, text: str):
        self.lineEdit.setText(text)

    def text(self):
        return self.lineEdit.text()

    def browseClicked(self):

        if self.isDir:
            dir = QFileDialog.getExistingDirectory(self, "Open a directory")
            if dir != "":
                self.lineEdit.setText(dir)
                self.TextChangedSignal.emit()
                self.TextChangedIdSignal.emit(self.id)
        else:
            file = QFileDialog.getOpenFileName(self, "Open a file", '', "*.*")
            if file != "":
                self.lineEdit.setText(file[0])
                self.TextChangedSignal.emit()
                self.TextChangedIdSignal.emit(self.id)


class BiDragLabel(QLabel):
    def __init__(self, parent: QWidget):
        super(BiDragLabel, self).__init__(parent)

    def setMimeData(self, data: str):
        self.mimeData = data

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == qtpy.QtCore.Qt.LeftButton:
            drag = QDrag(self)
            mimeData = QMimeData()
            urlList = [QUrl(self.mimeData)]

            mimeData.setUrls(urlList)
            drag.setMimeData(mimeData)

            if self.pixmap():
                drag.setPixmap(self.pixmap())
            
            drag.exec_()
        

class BiTagWidget(QWidget):
    remove = Signal(str)

    def __init__(self, parent: QWidget = None):
        super(BiTagWidget, self).__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.tagName = QLineEdit()
        self.tagName.setReadOnly(True)
        layout.addWidget(self.tagName)

        removeButton = QPushButton(self.tr("Remove"))
        removeButton.setObjectName("btnDanger")
        layout.addWidget(removeButton, 0, qtpy.QtCore.Qt.AlignRight)
        removeButton.released.connect(self.emitRemove)

        self.setLayout(layout)

    def setContent(self, content: str):
        self.tagName.setText(content)

    def content(self) -> str:
        return self.tagName.text()

    def emitRemove(self): 
        self.remove.emit(self.tagName.text())


class BiFlowLayout(QLayout):
    def __init__(self, parent: QWidget = None, margin: int = -1, hSpacing: int = -1, vSpacing: int = -1):
        super().__init__(parent)
        self.hSpace = hSpacing
        self.vSpace = vSpacing
        self.setContentsMargins(margin, margin, margin, margin)
        self.itemList = []

    def addItem(self, item: QLayoutItem):
        self.itemList.append(item)

    def horizontalSpacing(self) -> int:
        if self.hSpace >= 0:
            return self.hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self) -> str:
        if self.vSpace >= 0:
            return self.vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self) -> int:
        return len(self.itemList)

    def itemAt(self, index: int) -> QLayoutItem:
        if index < len(self.itemList):
            return self.itemList[index]
        return None   

    def takeAt(self, index: int) -> QLayoutItem:
        if index >= 0 and index < len(self.itemList):
            item = self.itemList[index]
            self.itemList.pop(index)
            return item
        else:
            return 0

    def expandingDirections(self) -> int: 
        return 0

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect: QRect):
        #QLayout.setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2*self.margin(), 2*self.margin())
        return size

    def doLayout(self, rect: QRect, testOnly: bool) -> int:
        left = 0
        top = 0
        right = 0
        bottom = 0
        #self.getContentsMargins(left, top, right, bottom)
        effectiveRect = rect.adjusted(+left, +top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = wid.style().layoutSpacing(
                        QSizePolicy.PushButton, QSizePolicy.PushButton, qtpy.QtCore.Qt.Horizontal)
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = wid.style().layoutSpacing(
                        QSizePolicy.PushButton, QSizePolicy.PushButton, qtpy.QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        
        return y + lineHeight - rect.y() + bottom

    def smartSpacing(self, pm: qtpy.QtWidgets.QStyle.PixelMetric) -> int:
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
    

class BiNavigationBar(QWidget):
    previousSignal = Signal()
    nextSignal = Signal()
    homeSignal = Signal()
    returnSignal = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        widget = QWidget(self)
        globalLayout = QHBoxLayout()
        globalLayout.setContentsMargins(0,0,0,0)
        self.setLayout(globalLayout)
        globalLayout.addWidget(widget)

        layout = QHBoxLayout()
        layout.setSpacing(2)
        widget.setLayout(layout)
        widget.setAttribute(qtpy.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("BiToolBar")

        # previous
        previousButton = QToolButton()
        previousButton.setObjectName("BiNavigationBarPreviousButton")
        previousButton.setToolTip(self.tr("Previous"))
        previousButton.released.connect(self.previousClicked)
        layout.addWidget(previousButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # next
        nextButton = QToolButton()
        nextButton.setObjectName("BiNavigationBarNextButton")
        nextButton.setToolTip(self.tr("Next"))
        nextButton.released.connect(self.nextClicked)
        layout.addWidget(nextButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # home
        homeButton = QToolButton()
        homeButton.setObjectName("BiNavigationBarHomeButton")
        homeButton.setToolTip(self.tr("Home"))
        homeButton.released.connect(self.homeClicked)
        layout.addWidget(homeButton, 0, qtpy.QtCore.Qt.AlignLeft)

        # bar
        self.lineEdit = QLineEdit()
        self.lineEdit.setAttribute(qtpy.QtCore.Qt.WA_MacShowFocusRect, False)
        self.lineEdit.returnPressed.connect(self.returnPressed)
        layout.addWidget(self.lineEdit, 1)

    def set_path(self, path: str):
        self.lineEdit.setText(path)

    def previousClicked(self):
        self.previousSignal.emit()

    def nextClicked(self):
        self.nextSignal.emit()    

    def homeClicked(self):
        self.homeSignal.emit()  

    def returnPressed(self):
        self.returnSignal.emit()       


class BiHideableWidget(QWidget):
    def __init__(self, title: str, level: int = 1, parent: QWidget = None, useFlowLayout: bool = False):
        super().__init__(parent)

        self.useFlowLayout = useFlowLayout

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # title area
        titleLabel = QLabel(title, self)
        titleLabel.setObjectName("BiHideableWidgetTitleText" + "Level" + str(level))
        self.button = QPushButton(self)
        self.button.setCheckable(True)
        self.button.setObjectName("BiHideableWidgetTitleButton" + "Level" + str(level))

        titleArea = QWidget(self)
        titleArea.setObjectName("BiHideableWidgetTitle" + "Level" + str(level))
        titleLayout = QHBoxLayout()
        titleLayout.setContentsMargins(0,0,0,0)
        titleArea.setLayout(titleLayout)
        titleLayout.addWidget(titleLabel, 1, qtpy.QtCore.Qt.AlignLeft)
        titleLayout.addWidget(self.button, 0, qtpy.QtCore.Qt.AlignRight)

        layout.addWidget(titleArea)

        # hideable widget
        self.hideableWidget = QWidget(self)
        self.hideableWidget.setObjectName("BiHideableWidget" + "Level" + str(level))
        self.isVisible = True
        self.animation = QPropertyAnimation(self.hideableWidget, b"maximumHeight")
        self.useAnimation = True 

        if useFlowLayout:
            self.flowLayout = BiFlowLayout()
            self.hideableWidget.setLayout(self.flowLayout)
        else:
            self.layout = QVBoxLayout()
            self.layout.setContentsMargins(0,0,0,0)
            self.hideableWidget.setLayout(self.layout)

        layout.addWidget(self.hideableWidget)

        # connections
        self.button.released.connect(self.switchView)

    def setUseAnimation(self, useAnimation: bool):
        self.useAnimation = useAnimation

    def switchView(self):
        if self.isVisible:
            if self.useAnimation:
                self.animation.setDuration(1000)
                self.animation.setStartValue(self.height)
                self.animation.setEndValue(0)
                self.animation.start()
            else:
                self.hideableWidget.setVisible(False)
            self.isVisible = False
        else:
            if self.useAnimation:
                self.animation.setDuration(2000)
                self.animation.setStartValue(0)
                self.animation.setEndValue(self.height)
                self.animation.start()
            else:
                self.hideableWidget.setVisible(True)
            self.isVisible = True

    def addWidget(self, widget: QWidget):
        if self.useFlowLayout:
            self.flowLayout.addWidget(widget)
        else:
            self.layout.addWidget(widget)
        self.height = 500


class BiClosableButton(QPushButton):
    clicked = Signal(int)
    closed = Signal(int)

    def __init__(self, closable: bool = True,  parent: QWidget = None):
        super().__init__(parent)

        self._id = -1

        if closable:
            layout = QVBoxLayout()
            layout.setContentsMargins(0,0,0,0)
            closeButton = QPushButton()
            closeButton.setObjectName("BiCloseButton")
            closeButton.setFixedSize(12,12)
            layout.addWidget(closeButton, 1, qtpy.QtCore.Qt.AlignTop | qtpy.QtCore.Qt.AlignRight)
            self.setLayout(layout)
            closeButton.pressed.connect(self.emitClosed)

        self.pressed.connect(self.emitClicked)    

    def id(self) -> int:
        return self._id

    def setId(self, id: int):
        self._id = id

    def emitClicked(self):
        self.clicked.emit(self._id)

    def emitClosed(self):
        self.closed.emit(self._id)


class BiStaticStackedWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self._currentIndex = -1
        self.widgets = []

    def remove(self, idx: int):
        self.widgets.pop(idx)
        self.layout.itemAt(idx).widget().deleteLater()

    def currentIndex(self):
        return self._currentIndex

    def setCurrentIndex(self, idx: int):
        self._currentIndex = idx

    def addWidget(self, widget: QWidget):
        self.layout.addWidget(widget)
        self.widgets.append(widget)

    def count(self) -> int:
        return self.layout.count()

    def slideInIdx(self, idx: int):

        self._currentIndex = idx
        for i in range(len(self.widgets)):
            if i == idx:
                self.widgets[i].setVisible(True)
            else:
                self.widgets[i].setVisible(False)


class BiSlidingStackedWidget(QStackedWidget):

    animationFinished = Signal()

    LEFT2RIGHT = "LEFT2RIGHT"
    RIGHT2LEFT = "RIGHT2LEFT"
    TOP2BOTTOM = "TOP2BOTTOM"
    BOTTOM2TOP = "BOTTOM2TOP"
    AUTOMATIC = "AUTOMATIC"

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        if parent != None:
            self.mainwindow=parent
        else:
            self.mainwindow=self
            print("ATTENTION: untested mainwindow case !")

        self.vertical=False
        self.speed=500
        self.animationtype = QEasingCurve.OutQuad
        self.now=0
        self.next=0
        self.wrap=False
        self.pnow=QPoint(0,0)
        self.active=False

    def setVerticalMode(self, vertical: bool ):
        self.vertical = vertical

    def setSpeed(self, speed: int):
        self.speed = speed

    def setAnimation(self, animationtype):
        self.animationtype = animationtype

    def setWrap(self, wrap: bool):
            self.wrap = wrap

    def slideInNext(self):
        now = self.currentIndex()
        if self.wrap or (now<self.count()-1):
            self.slideInIdx(now+1)

    def slideInPrev(self):
        now = self.currentIndex()
        if self.wrap or now > 0:
            self.slideInIdx(now-1)

    def slideInIdx(self, idx: int, direction: str = "AUTOMATIC"):

        if idx > self.count()-1:
            if self.vertical:
                direction = BiSlidingStackedWidget.TOP2BOTTOM
            else:
                direction = BiSlidingStackedWidget.RIGHT2LEFT
            idx=(idx)%self.count()

        elif idx<0:
            if self.vertical:
                direction = BiSlidingStackedWidget.BOTTOM2TOP
            else:
                direction = BiSlidingStackedWidget.LEFT2RIGHT       
            idx=(idx+self.count())%self.count()
        
        self.slideInWgt(self.widget(idx), direction)


    def slideInWgt(self, newwidget: QWidget, direction: str):

        if self.active:
            return
        else:
            self.active = True

        directionhint = ""
        now = self.currentIndex()
        next_=self.indexOf(newwidget)
        if now == next_:
            self.active = False
            return
        elif now < next_:
            if self.vertical:
                directionhint = BiSlidingStackedWidget.TOP2BOTTOM
            else:
                directionhint = BiSlidingStackedWidget.RIGHT2LEFT        
        else:
            if self.vertical:
                directionhint = BiSlidingStackedWidget.BOTTOM2TOP
            else:
                directionhint = BiSlidingStackedWidget.LEFT2RIGHT   
        
        if direction == BiSlidingStackedWidget.AUTOMATIC:
            direction = directionhint
        
        print("sliding direction: ", direction)
        # calculate the shifts

        offsetx = self.frameRect().width()
        offsety = self.frameRect().height()

        self.widget(next_).setGeometry ( 0,  0, offsetx, offsety )

        if direction == BiSlidingStackedWidget.BOTTOM2TOP:
                offsetx = 0
                offsety = -offsety
        
        elif direction == BiSlidingStackedWidget.TOP2BOTTOM:
                offsetx = 0
        
        elif direction == BiSlidingStackedWidget.RIGHT2LEFT:
                offsetx = -offsetx
                offsety = 0
        
        elif direction == BiSlidingStackedWidget.LEFT2RIGHT:
                offsety = 0
        
        pnext = self.widget(next_).pos()
        pnow = self.widget(now).pos()
        self.pnow = pnow

        self.widget(next_).move(pnext.x()-offsetx,pnext.y()-offsety)
        self.widget(next_).show()
        self.widget(next_).raise_()

        animnow = QPropertyAnimation(self.widget(now), b"pos")

        animnow.setDuration(self.speed)
        animnow.setEasingCurve(self.animationtype)
        animnow.setStartValue(QPoint(pnow.x(), pnow.y()))
        animnow.setEndValue(QPoint(offsetx+pnow.x(), offsety+pnow.y()))
        animnext = QPropertyAnimation(self.widget(next_), b"pos")
        animnext.setDuration(self.speed)
        animnext.setEasingCurve(self.animationtype)
        animnext.setStartValue(QPoint(-offsetx+pnext.x(), offsety+pnext.y()))
        animnext.setEndValue(QPoint(pnext.x(), pnext.y()))

        animgroup = QParallelAnimationGroup()

        animgroup.addAnimation(animnow)
        animgroup.addAnimation(animnext)

        animgroup.finished.connect(self.animationDoneSlot)

        self.next = next_
        self.now = now
        self.active = True
        animgroup.start()

    def animationDoneSlot(self):
        self.setCurrentIndex(self.next)  
        self.widget(self.now).hide()
        self.widget(self.now).move(self.pnow)
        self.active = False
        self.animationFinished.emit()


class BiAppBar(QWidget):
    open = Signal(int)
    close = Signal(int)

    def __init__(self):
        super().__init__()

        self.current_tab_id = -1
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(QWidget(), 1, qtpy.QtCore.Qt.AlignTop)

        # global
        layout = QHBoxLayout()
        w = QWidget()
        #w.setObjectName("BiHomeToolBar")
        layout.addWidget(w, 1, qtpy.QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(0, 7, 0, 0)
        w.setLayout(self.layout)

        # total
        tlayout = QHBoxLayout()
        wt = QWidget()
        tlayout.addWidget(wt, 1, qtpy.QtCore.Qt.AlignHCenter)
        tlayout.setContentsMargins(0, 0, 0, 0)
        wt.setLayout(layout)
        wt.setObjectName("BiHomeToolBar")
        wt.setFixedWidth(52)
        self.setFixedWidth(52)
        self.setLayout(tlayout)

    def addButton(self, icon: str, toolTip: str, id: int, closable: bool):
        button = BiClosableButton(closable, self)
        button.setObjectName('BiHomeToolBarButton')
        button.setCheckable(True)
        button.setIcon(QIcon(icon))
        if (toolTip != ""):
            button.setToolTip(toolTip)
        button.setId(id)
        self.layout.insertWidget(self.layout.count() -1, button, 0, qtpy.QtCore.Qt.AlignHCenter)

        button.clicked.connect(self.open)
        button.closed.connect(self.close)

    def print_buttons(self):
        for i in range(self.layout.count()-1, -1, -1):
            item = self.layout.itemAt(i)
            button = item.widget()
            if button:
                if isinstance(button, BiClosableButton):
                    print("button:", button.id())

    def removeButton(self, id: int):
        for i in range(self.layout.count()-1, -1, -1):
            item = self.layout.itemAt(i)
            button = item.widget()
            if button:
                if isinstance(button, BiClosableButton):
                    if (button.id() == id):
                        button.deleteLater()
                    elif button.id() > id:
                        button.setId(button.id()-1)              

    def setChecked(self, id: int, update_current: bool):
        self.current_tab_id = id
        for i in range(0, self.layout.count()):
            button = self.layout.itemAt(i).widget()
            if isinstance(button, BiClosableButton):
                if button.id() == id and update_current:
                    button.setChecked(True)   
                else:
                    button.setChecked(False)          
    

class BiDictViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.tree = QTreeView(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)
        self.model = TreeModel(["Key", "Value"], {})
        self.tree.header().setDefaultSectionSize(180)
        self.tree.setModel(self.model)
        self.tree.expandAll()    

    def import_data(self, data):
        """Import a dict (from json) in the view
        
        Parameters
        ----------
        data: dict
            Dictionary of data to import

        """ 
        self.model = TreeModel(["Key", "Value"], data)
        self.tree.setModel(self.model)


class TreeModel(qtpy.QtCore.QAbstractItemModel):
    def __init__(self, headers, data, parent=None):
        super(TreeModel, self).__init__(parent)
        """ subclassing the standard interface item models must use and 
                implementing index(), parent(), rowCount(), columnCount(), and data()."""

        rootData = [header for header in headers]
        self.rootItem = TreeNode(rootData)
        indent = -1
        self.parents = [self.rootItem]
        self.indentations = [0]
        self.createData(data, indent)

    def createData(self, data, indent):
        if type(data) == dict:
            indent += 1
            position = 4 * indent
            for dict_keys, dict_values in data.items():
                if position > self.indentations[-1]:
                    if self.parents[-1].childCount() > 0:
                        self.parents.append(self.parents[-1].child(self.parents[-1].childCount() - 1))
                        self.indentations.append(position)
                else:
                    while position < self.indentations[-1] and len(self.parents) > 0:
                        self.parents.pop()
                        self.indentations.pop()
                parent = self.parents[-1]
                parent.insertChildren(parent.childCount(), 1, parent.columnCount())
                parent.child(parent.childCount() - 1).setData(0, dict_keys)
                if type(dict_values) != dict:
                    parent.child(parent.childCount() - 1).setData(1, str(dict_values))
                self.createData(dict_values, indent)

    def index(self, row, column, index=qtpy.QtCore.QModelIndex()):
        """ Returns the index of the item in the model specified by the given row, column and parent index """

        if not self.hasIndex(row, column, index):
            return qtpy.QtCore.QModelIndex()
        if not index.isValid():
            item = self.rootItem
        else:
            item = index.internalPointer()

        child = item.child(row)
        if child:
            return self.createIndex(row, column, child)
        return qtpy.QtCore.QModelIndex()

    def parent(self, index):
        """ Returns the parent of the model item with the given index
                If the item has no parent, an invalid QModelIndex is returned """

        if not index.isValid():
            return qtpy.QtCore.QModelIndex()
        item = index.internalPointer()
        if not item:
            return qtpy.QtCore.QModelIndex()

        parent = item.parentItem
        if parent == self.rootItem:
            return qtpy.QtCore.QModelIndex()
        else:
            return self.createIndex(parent.childNumber(), 0, parent)

    def rowCount(self, index=qtpy.QtCore.QModelIndex()):
        """ Returns the number of rows under the given parent
                When the parent is valid it means that rowCount is returning the number of children of parent """

        if index.isValid():
            parent = index.internalPointer()
        else:
            parent = self.rootItem
        return parent.childCount()

    def columnCount(self, index=qtpy.QtCore.QModelIndex()):
        """ Returns the number of columns for the children of the given parent """

        return self.rootItem.columnCount()

    def data(self, index, role=qtpy.QtCore.Qt.DisplayRole):
        """ Returns the data stored under the given role for the item referred to by the index """

        if index.isValid() and role == qtpy.QtCore.Qt.DisplayRole:
            return index.internalPointer().data(index.column())
        elif not index.isValid():
            return self.rootItem.data(index.column())

    def headerData(self, section, orientation, role=qtpy.QtCore.Qt.DisplayRole):
        """ Returns the data for the given role and section in the header with the specified orientation """

        if orientation == qtpy.QtCore.Qt.Horizontal and role == qtpy.QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)


class TreeNode(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.children = []

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)

    def childNumber(self):
        if self.parentItem is not None:
            return self.parentItem.children.index(self)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return self.itemData[column]

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.children):
            return False
        for row in range(count):
            data = [v for v in range(columns)]
            item = TreeNode(data, self)
            self.children.insert(position, item)

    def parent(self):
        return self.parentItem

    def setData(self, column, value):
        if column < 0 or column >= len(self.itemData):
            return False
        self.itemData[column] = value