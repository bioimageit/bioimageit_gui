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

import PySide2.QtCore
from PySide2.QtCore import (QMimeData, QSize, QRect, QPoint, QPropertyAnimation, 
                            QEasingCurve, QParallelAnimationGroup)
from PySide2.QtGui import QMouseEvent, QDrag, QCursor, QIcon
from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, QToolButton,
                               QFileDialog, QHBoxLayout, QLineEdit, QVBoxLayout,
                               QLayout, QLayoutItem, QSizePolicy, QStyle, QStackedWidget)
from PySide2.QtCore import Signal, Slot, QUrl 


class BiButton(QPushButton):
    clickedId = Signal(int)
    clickedContent = Signal(str)

    def __init__(self, title: str, parent: QWidget = None):
        super(BiButton, self).__init__(title, parent)
        #self.setCursor(QCursor(PySide2.QtCore.Qt.PointingHandCursor))
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
        layout.addWidget(self.lineEdit)

        browseButton = QPushButton("...")
        browseButton.setObjectName("BiBrowseButton")
        layout.addWidget(browseButton, 0, PySide2.QtCore.Qt.AlignRight)
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
        if event.button() == PySide2.QtCore.Qt.LeftButton:
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
        layout.addWidget(removeButton, 0, PySide2.QtCore.Qt.AlignRight)
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
                        QSizePolicy.PushButton, QSizePolicy.PushButton, PySide2.QtCore.Qt.Horizontal)
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = wid.style().layoutSpacing(
                        QSizePolicy.PushButton, QSizePolicy.PushButton, PySide2.QtCore.Qt.Vertical)
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

    def smartSpacing(self, pm: PySide2.QtWidgets.QStyle.PixelMetric) -> int:
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
        widget.setAttribute(PySide2.QtCore.Qt.WA_StyledBackground, True)
        widget.setObjectName("BiToolBar")

        # previous
        previousButton = QToolButton()
        previousButton.setObjectName("BiNavigationBarPreviousButton")
        previousButton.setToolTip(self.tr("Previous"))
        previousButton.released.connect(self.previousClicked)
        layout.addWidget(previousButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # next
        nextButton = QToolButton()
        nextButton.setObjectName("BiNavigationBarNextButton")
        nextButton.setToolTip(self.tr("Next"))
        nextButton.released.connect(self.nextClicked)
        layout.addWidget(nextButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # home
        homeButton = QToolButton()
        homeButton.setObjectName("BiNavigationBarHomeButton")
        homeButton.setToolTip(self.tr("Home"))
        homeButton.released.connect(self.homeClicked)
        layout.addWidget(homeButton, 0, PySide2.QtCore.Qt.AlignLeft)

        # bar
        self.lineEdit = QLineEdit()
        self.lineEdit.setAttribute(PySide2.QtCore.Qt.WA_MacShowFocusRect, False)
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
        titleLayout.addWidget(titleLabel, 1, PySide2.QtCore.Qt.AlignLeft)
        titleLayout.addWidget(self.button, 0, PySide2.QtCore.Qt.AlignRight)

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
            layout.addWidget(closeButton, 1, PySide2.QtCore.Qt.AlignTop | PySide2.QtCore.Qt.AlignRight)
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

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(QWidget(), 1, PySide2.QtCore.Qt.AlignTop)

        # global
        layout = QHBoxLayout()
        w = QWidget()
        #w.setObjectName("BiHomeToolBar")
        layout.addWidget(w, 1, PySide2.QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(0, 7, 0, 0)
        w.setLayout(self.layout)

        # total
        tlayout = QHBoxLayout()
        wt = QWidget()
        tlayout.addWidget(wt, 1, PySide2.QtCore.Qt.AlignHCenter)
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
        self.layout.insertWidget(self.layout.count() -1, button, 0, PySide2.QtCore.Qt.AlignHCenter)

        button.clicked.connect(self.open)
        button.closed.connect(self.close)

    def removeButton(self, id: int):
        for i in range(self.layout.count()-1, -1, -1):
            item = self.layout.itemAt(i)
            button = item.widget()
            if button:
                if isinstance(button, BiClosableButton):
                    if (button.id() == id):
                        del button
                        return

    def setChecked(self, id: int, update_current: bool):
        for i in range(0, self.layout.count()):
            button = self.layout.itemAt(i).widget()
            if isinstance(button, BiClosableButton):
                if button.id() == id and update_current:
                    button.setChecked(True)   
                else:
                    button.setChecked(False)          
    