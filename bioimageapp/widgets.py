import PySide2.QtCore
from PySide2.QtCore import QMimeData, QSize, QRect, QPoint, QPropertyAnimation, QEasingCurve
from PySide2.QtGui import QMouseEvent, QDrag
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, QToolButton, 
                               QFileDialog, QHBoxLayout, QLineEdit, QVBoxLayout,
                               QLayout, QLayoutItem, QSizePolicy, QStyle, QStackedWidget 
                               )
from PySide2.QtCore import QObject, Signal, Slot, QUrl 

class BiButton(QPushButton):
    clickedId = Signal(int)
    clickedContent = Signal(str)

    def __init__(self, title: str, parent: QWidget = None):
        super(BiButton, self).__init__(title, parent)
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

    def __init__(self, isDir: bool, parent: QWidget):
        super().__init__(parent)

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
            
        else:
            file = QFileDialog.getOpenFileName(self, "Open a file", '', "*.*")
            if file != "":
                self.lineEdit.setText(file[0])

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
        self.remove(self.tagName.text())

class BiWebBrowser(QWidget):
    def __init__(self, parent: QWidget):
        super(BiWebBrowser, self).__init__(parent)

        thisLayout = QVBoxLayout()
        thisLayout.setContentsMargins(0,0,0,0)
        thisLayout.setSpacing(0)

        toolBar = self.createToolBar()
        toolBar.setMaximumHeight(48)
        self.webView = QWebEngineView(self)

        thisLayout.addWidget(toolBar)
        thisLayout.addWidget(self.webView)

        totalWidget = QWidget()
        totalLayout = QVBoxLayout()
        totalLayout.setContentsMargins(0,0,0,0)
        totalWidget.setLayout(thisLayout)
        self.setLayout(totalLayout)
        totalLayout.addWidget(totalWidget)
        totalWidget.setObjectName("BiWebBrowser")

    def createToolBar(self) -> QWidget:
        toolbar = QWidget()
        toolbar.setObjectName("BiSubToolBar")

        backButton = QPushButton()
        backButton.setFixedSize(32,32)
        backButton.pressed.connect(self.back)
        backButton.setObjectName("BiWebBrowserBack")

        forwardButton = QPushButton()
        forwardButton.setFixedSize(32,32)
        forwardButton.pressed.connect(self.forward)
        forwardButton.setObjectName("BiWebBrowserForward")

        homeButton = QPushButton()
        homeButton.setFixedSize(32,32)
        homeButton.pressed.connect(self.home)
        homeButton.setObjectName("BiWebBrowserHome")

        barLayout = QHBoxLayout()
        barLayout.setSpacing(1)
        barLayout.setContentsMargins(2,2,2,2)
        barLayout.addWidget(backButton)
        barLayout.addWidget(forwardButton)
        barLayout.addWidget(homeButton)
        barLayout.addWidget(QWidget())

        toolbar.setLayout(barLayout)
        return toolbar

    def forward(self):
        self.webView.forward()

    def back(self):
        self.webView.back()

    def home(self):
        self.setHomePage(self.homeURL, self.isWebURL)

    def setHomePage(self, pageURL: str, isWebURL: bool):
        self.homeURL = pageURL
        self.isWebURL = isWebURL
        if self.isWebURL:
            self.webView.load(pageURL)
        else:
            self.homeURL = self.homeURL.replace("\\", "/")
            self.webView.load( "file:///" + self.homeURL)


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

        layout = QHBoxLayout()
        layout.setSpacing(2)
        self.setLayout(layout)
        self.setObjectName("BiToolBar")

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
        self.button.setObjectName("biHideableWidgetTitleButton" + "Level" + str(level))

        titleArea = QWidget(self)
        titleArea.setObjectName("biHideableWidgetTitle" + "Level" + str(level))
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
        self.animation = QPropertyAnimation()
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


class BiSlidingStackedWidget(QStackedWidget):

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
        self.vertical=vertical

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

    def slideInIdx(self, idx: int, direction: str):

        if idx > count()-1:
            if self.vertical:
                direction = TOP2BOTTOM
            else:
                direction = RIGHT2LEFT
            idx=(idx)%self.count()

        elif idx<0:
            if self.vertical:
                direction = BOTTOM2TOP
            else:
                direction = LEFT2RIGHT       
            idx=(idx+self.count())%self.count()
        
        self.slideInWgt(self.widget(idx), direction)


    def slideInWgt(newwidget: QWidget, direction: str):

        if self.active:
                return
        else:
            self.active = True

        directionhint = ""
        now = self.currentIndex()
        next=indexOf(newwidget)
        if now == next:
            self.active = False
            return
        elif now < next:
            if self.vertical:
                directionhint = TOP2BOTTOM
            else:
                directionhint = RIGHT2LEFT        
        else:
            if self.vertical:
                directionhint = BOTTOM2TOP
            else:
                directionhint = LEFT2RIGHT   
        
        if direction.equals(AUTOMATIC):
            direction = directionhint
        

        # calculate the shifts

        offsetx = self.frameRect().width()
        offsety = self.frameRect().height()

        self.widget(next).setGeometry ( 0,  0, offsetx, offsety )

        if direction.equals(BOTTOM2TOP):
                offsetx = 0
                offsety = -offsety
        
        elif direction.equals(TOP2BOTTOM):
                offsetx = 0
        
        elif direction.equals(RIGHT2LEFT):
                offsetx = -offsetx
                offsety = 0
        
        elif direction.equals(LEFT2RIGHT):
                offsety = 0
        
        pnext = self.widget(next).pos()
        pnow = self.widget(now).pos()
        self.pnow = pnow

        self.widget(next).move(pnext.x()-offsetx,pnext.y()-offsety)
        self.widget(next).show()
        self.widget(next).raise()

        animnow = QPropertyAnimation(self.widget(now), "pos")

        animnow.setDuration(m_speed)
        animnow.BackwardsetEasingCurve(m_animationtype)
        animnow.setStartValue(QPoint(pnow.x(), pnow.y()))
        animnow.setEndValue(QPoint(offsetx+pnow.x(), offsety+pnow.y()))
        animnext = QPropertyAnimation(self.widget(next), "pos")
        animnext.setDuration(self.speed)
        animnext.setEasingCurve(m_animationtype)
        animnext.setStartValue(QPoint(-offsetx+pnext.x(), offsety+pnext.y()))
        animnext.setEndValue(QPoint(pnext.x(), pnext.y()))

        animgroup = QParallelAnimationGroup()

        animgroup.addAnimation(animnow)
        animgroup.addAnimation(animnext)

        animgroup.finished.connect(self.animationDoneSlot)

        self.next = next
        self.now = now
        self.active = true
        animgroup.start()


    def animationDoneSlot():
        self.setCurrentIndex(self.next);  
        self.widget(self.now).hide()
        self.widget(self.now).move(self.pnow)
        self.active = False
        self.animationFinished.emit()
    