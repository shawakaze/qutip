import qutip.examples
import sys,os,time
from numpy import arange,floor

import qutip.gui.syntax
from qutip.examples import exconfig
from qutip.examples import *
if os.environ['QUTIP_GUI']=="PYSIDE":
    from PySide import QtGui, QtCore

elif os.environ['QUTIP_GUI']=="PYQT4":
    from PyQt4 import QtGui, QtCore

CD_BASE = os.path.dirname(__file__)

class Examples(QtGui.QWidget):
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.frameSize()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    def moveout(self):
        #self.clearFocus()
        for op in arange(0.9,-0.1,-0.1):
            time.sleep(.02)
            self.setWindowOpacity(op)
        #self.setVisible(False)
    def movein(self):
        self.focusWidget()
        self.setVisible(True)
        for op in arange(0.1,1.1,0.1):
            time.sleep(.02)
            self.setWindowOpacity(op)
    
    def __init__(self,version,direc,parent=None):
        QtGui.QWidget.__init__(self, parent)
        from qutip.examples.examples_text import tab_labels,button_labels,button_desc,button_nums
        #set tab button style
        tab_button_style='QPushButton {font-family: Verdana;border-width: 2px;border-color:#666666;border-style: solid;border-radius: 7;background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #B8E2EF, stop: 0.1 #A5DBEB, stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1, stop: 1 #57BCD9)}'
        #set quit button style
        quit_style='QPushButton {font-family: Verdana;border-width: 2px;border-color:#666666;border-style: solid;border-radius: 7;font-size: 16px;background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFAAAA, stop: 0.1 #FF9999, stop: 0.49 #FF8888, stop: 0.5 #FF7777, stop: 1 #FF6666)}'
        
        #WINDOW PROPERTIES
        self.setWindowTitle('QuTiP Examples')
        self.setWindowIcon(QtGui.QIcon(CD_BASE + "/icon.png"))
        self.resize(1300, 720)
        self.setMinimumSize(1300, 720)
        self.setMaximumSize(1300, 720)
        self.center()
        self.setFocus()
        self.dir=direc+'/examples/'
        mapper = QtCore.QSignalMapper(self)
        
        
        
        title_font = QtGui.QFont()
        title_font.setFamily("Verdana")
        title_font.setBold(True)
        if sys.platform=='darwin':
            title_font.setPointSize(14)
        else:
            title_font.setPointSize(12)
        title_fm = QtGui.QFontMetrics(title_font)
        #text across top of demos window
        title = QtGui.QLabel(self)
        title.setFont(title_font)
        title_text="Click button once for code preview.  Click again to run example."
        pixelswide = title_fm.width(title_text)
        title.setText(title_text)
        title.setGeometry((self.width()-pixelswide)/2.0, 0, 800, 30)
        
        
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setBold(True)
        if sys.platform=='darwin':
            font.setPointSize(12)
        else:
            font.setPointSize(10)
        fm = QtGui.QFontMetrics(font)

        
        #QUIT BUTTON-----------------
        #quit = HoverExit('Close',self)
        #quit.setGeometry(1120, 710, 70, 40)
        #quit.setStyleSheet(quit_style)
        #quit.setFocusPolicy(QtCore.Qt.NoFocus)
        #quit.clicked.connect(self.close)
        
        #copyright text
        copyright = QtGui.QLabel(self)
        copy_text="Copyright (c) 2011-2013, P. D. Nation & J. R. Johansson"
        copyright.setText(copy_text)
        font.setBold(False)
        copyright.setFont(font)
        copyright.setGeometry(10, 695, 400, 30)
        #tab widget
        tab_widget = QtGui.QTabWidget() 
        tab_widget.move(10,10)
        tab_widget.resize(600,665)
        tab_widget.setFixedSize(600,665)
        #tabs for tab widget
        num_tabs=len(tab_labels)
        tabs=[QtGui.QWidget() for k in range(num_tabs)]
        for k in range(num_tabs):
            tab_widget.addTab(tabs[k],tab_labels[k])
        tab_widget.setTabShape(QtGui.QTabWidget.Triangular)
        tab_widget.setCurrentIndex(exconfig.tab)
        
        
        #tab buttons
        self.tab_verts =[QtGui.QVBoxLayout(tabs[k]) for k in range(num_tabs)]
        self.num_elems=[len(button_labels[k]) for k in range(num_tabs)]
        self.tab_buttons=[[] for j in range(num_tabs)]
        for j in range(num_tabs):
            for k in range(self.num_elems[j]):
                button=HoverButton(button_nums[j][k],button_labels[j][k])
                button.setFont(font)
                if button_nums[j][k]==exconfig.is_green:
                    button.setText('Run Example')
                    button.setStyleSheet('QPushButton {font-family: Verdana;border-width: 2px;border-color:#666666;border-style: solid;border-radius: 7;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0F1E0, stop: 0.1 #C1E3C1, stop: 0.49 #A3D6A3, stop: 0.5 #84C884, stop: 1 #66BB66)}')
                else:
                    button.setText(button_labels[j][k])
                    button.setStyleSheet(tab_button_style)
                button.setFixedSize(170, 40)
                self.connect(button, QtCore.SIGNAL("clicked()"), mapper, QtCore.SLOT("map()"))
                mapper.setMapping(button,button_nums[j][k])
                self.tab_buttons[j].append(button)
        
        #font for example descriptions
        font2 = QtGui.QFont()
        font2.setFamily("Verdana")
        font2.setBold(False)
        if sys.platform=='darwin':
            font2.setPointSize(12)
        else:
            font2.setPointSize(10)
        
        self.tab_button_desc = [[] for j in range(num_tabs)]
        for j in range(num_tabs):
            for k in range(self.num_elems[j]):
                _label=QtGui.QLabel(button_desc[j][k])
                _label.setWordWrap(True) #auto wrap
                _label.setFont(font2)
                self.tab_button_desc[j].append(_label)
        
        self.tab_widgets=[[QtGui.QWidget() for k in range(self.num_elems[j])] for j in range(num_tabs)]
        self.tab_horiz_layouts=[[QtGui.QHBoxLayout(self.tab_widgets[j][k]) for k in range(self.num_elems[j])] for j in range(num_tabs)]
        for j in range(num_tabs):
            for k in range(self.num_elems[j]):
                self.tab_horiz_layouts[j][k].addWidget(self.tab_buttons[j][k])
                self.tab_horiz_layouts[j][k].addSpacing(15)
                self.tab_horiz_layouts[j][k].addWidget(self.tab_button_desc[j][k])
        for j in range(num_tabs):
            for k in range(self.num_elems[j]):
                self.tab_verts[j].addWidget(self.tab_widgets[j][k])
            self.tab_verts[j].addStretch()
        
        #set mapper to on_button_clicked funtions
        self.connect(mapper, QtCore.SIGNAL("mapped(int)"), self.on_button_clicked)
        self.layout = QtGui.QGridLayout(self)
        #create text editor widget
        self.editor = QtGui.QTextEdit()
        self.editor.setCurrentFont(QtGui.QFont("Courier"))
        if sys.platform=='darwin':
            self.editor.setFontPointSize(12)
        else:
            self.editor.setFontPointSize(10)
        self.editor.setReadOnly(True)
        self.editor.resize(600,665)
        self.editor.setFixedSize(600,666)
        #add tabwidget and textwidget to main window
        self.layout.addWidget(tab_widget, 0, 0, 5, 1)
        self.layout.addWidget(self.editor, 0, 3, 5, 1)
        #set text of editor if demos previsouly ran.
        if exconfig.is_green!=0:
            qutip.gui.syntax.PythonHighlighter(self.editor.document())
            self.editor.show()
            _text_file=compile("infile = open(self.dir+'ex_"+str(exconfig.is_green)+".py', 'r')",'<string>', 'exec')
            _locals = locals()
            exec(_text_file, globals(), _locals)
            infile = _locals["infile"]
            self.editor.setPlainText(infile.read())
            
        
    
    def on_button_clicked(self,num):
        """
        Receives integers from button click to use for calling example script
        """
        if exconfig.button_num!=num and exconfig.is_green!=num:
            tab_num=int(floor(num/10))-1
            row_num=num % 10
            self.tab_buttons[tab_num][row_num].setStyleSheet('QPushButton {font-family: Verdana;border-width: 3px;border-color:#111111;border-style: solid;border-radius: 7;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0F1E0, stop: 0.1 #C1E3C1, stop: 0.49 #A3D6A3, stop: 0.5 #84C884, stop: 1 #66BB66)}')
            self.tab_buttons[tab_num][row_num].setText('Run Example')
            exconfig.button_num=num
            old_tab_num=int(floor(exconfig.is_green/10))-1
            old_row_num=exconfig.is_green % 10
            self.tab_buttons[old_tab_num][old_row_num].setStyleSheet('QPushButton {font-family: Verdana;border-width: 2px;border-color:#666666;border-style: solid;border-radius: 7;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #B8E2EF, stop: 0.1 #A5DBEB, stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1, stop: 1 #57BCD9)}')
            self.tab_buttons[old_tab_num][old_row_num].setText(self.tab_buttons[old_tab_num][old_row_num].label)
            exconfig.is_green=num
            qutip.gui.syntax.PythonHighlighter(self.editor.document())
            self.editor.show()
            _text_file=compile("infile = open(self.dir+'ex_"+str(exconfig.is_green)+".py', 'r')",'<string>', 'exec')
            _locals = locals()
            exec(_text_file, globals(), _locals)
            infile = _locals["infile"]
            self.editor.setPlainText(infile.read())
        else:
            self.moveout()
            exconfig.tab=int(floor(num/10))-1
            exconfig.option=num
            self.close()


class HoverButton(QtGui.QPushButton):
    def __init__(self,num,label):
            super(HoverButton, self).__init__()
            self.num=num
            self.label=label
    def enterEvent(self,event):  
        if exconfig.is_green==self.num:
            self.setStyleSheet('QPushButton {font-family: Verdana;border-width: 3px;border-color:#111111;border-style: solid;border-radius: 7;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0F1E0, stop: 0.1 #C1E3C1, stop: 0.49 #A3D6A3, stop: 0.5 #84C884, stop: 1 #66BB66)}')
        else:
            self.setStyleSheet('QPushButton {font-family: Verdana;border-width: 3px;border-color:#111111;border-style: solid;border-radius: 7;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #B8E2EF, stop: 0.1 #A5DBEB, stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1, stop: 1 #57BCD9)}')
    def leaveEvent(self,event):  
        if exconfig.is_green==self.num:
            self.setStyleSheet('QPushButton {font-family: Verdana;border-width: 2px;border-color:#666666;border-style: solid;border-radius: 7;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0F1E0, stop: 0.1 #C1E3C1, stop: 0.49 #A3D6A3, stop: 0.5 #84C884, stop: 1 #66BB66)}')
        else:
            self.setStyleSheet('QPushButton {font-family: Verdana;border-width: 2px;border-color:#666666;border-style: solid;border-radius: 7;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #B8E2EF, stop: 0.1 #A5DBEB, stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1, stop: 1 #57BCD9)}')


class HoverExit(QtGui.QPushButton): 
    def enterEvent(self,event):  
        self.setStyleSheet('QPushButton {font-family: Verdana;border-width: 3px;border-color:#111111;border-style: solid;border-radius: 7;font-size: 16px;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFAAAA, stop: 0.1 #FF9999, stop: 0.49 #FF8888, stop: 0.5 #FF7777, stop: 1 #FF6666)}')
    def leaveEvent(self,event):  
        self.setStyleSheet('QPushButton {font-family: Verdana;border-width: 2px;border-color:#666666;border-style: solid;border-radius: 7;font-size: 16px;background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFAAAA, stop: 0.1 #FF9999, stop: 0.49 #FF8888, stop: 0.5 #FF7777, stop: 1 #FF6666)}')











