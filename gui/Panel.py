#! encoding = utf-8

'''
Window panels
定义主窗口中的各模块
'''

from PyQt5 import QtWidgets, QtCore, QtGui
from data import yysdata, yyslib
from os import path

class TaskEditor(QtWidgets.QGroupBox):
    ''' Edit task list 编辑悬赏任务列表 '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('编辑阴阳师悬赏任务')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(False)


        self.taskRowDict = {}   # {id: taskRowWidget}
        newBtn = QtWidgets.QPushButton('新增任务')
        # the button group stores all delete buttons so that
        # I can track them down
        self.delBtnGroup = QtWidgets.QButtonGroup()

        # set up layout
        self.entryLayout = QtWidgets.QGridLayout()
        self.entryLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignJustify)
        self.entryLayout.addWidget(newBtn, 0, 0)
        self.entryLayout.addWidget(QtWidgets.QLabel(''), 0, 1)
        self.entryLayout.addWidget(QtWidgets.QLabel('怪物'), 0, 2)
        self.entryLayout.addWidget(QtWidgets.QLabel('数量'), 0, 3)
        self.entryLayout.addWidget(QtWidgets.QLabel('任务星级'), 0, 4)

        # preset one row
        self._add_entry()

        entryWidgets = QtWidgets.QWidget()
        entryWidgets.setLayout(self.entryLayout)

        entryArea = QtWidgets.QScrollArea()
        entryArea.setWidgetResizable(True)
        entryArea.setWidget(entryWidgets)

        # Set up main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setSpacing(0)
        mainLayout.addWidget(entryArea)
        self.setLayout(mainLayout)

        newBtn.clicked.connect(self._add_entry)
        self.delBtnGroup.buttonClicked[int].connect(self._del_entry)

    def _add_entry(self):
        '''
        Add a batch entry to the task list
        向悬赏任务列表中添加一个任务
        '''

        # get current task number
        if self.taskRowDict:
            n = max(self.taskRowDict.keys()) + 1
        else:
            n = 0
        task = TaskRow(self)
        self.taskRowDict[n] = task
        self.entryLayout.addWidget(task.delBtn, n+1, 0)
        self.entryLayout.addWidget(task.editBtn, n+1, 1)
        self.entryLayout.addWidget(task.creepEdit, n+1, 2)
        self.entryLayout.addWidget(task.numEdit, n+1, 3)
        self.entryLayout.addWidget(task.starEdit, n+1, 4)
        self.delBtnGroup.addButton(task.delBtn, n)

    def _del_entry(self, btn_id):
        '''
        delete entry from the task list
        移除列表中的任务
        '''

        task = self.taskRowDict[btn_id]
        self.delBtnGroup.removeButton(task.delBtn)
        del self.taskRowDict[btn_id]
        task.delRow()

    def showTasks(self):
        ''' Return task list 返回任务列表
            [(creep_name, creep_num, task_star), ...]
        '''

        a_list = []
        for id, task in self.taskRowDict.items():
            a_list.append(task.getInput())
        return a_list


class TaskRow(QtWidgets.QWidget):
    ''' 单行任务模块 '''

    def __init__(self, parent):

        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.creepEdit = QtWidgets.QLineEdit()
        self.numEdit = QtWidgets.QLineEdit()
        self.numEdit.setValidator(QtGui.QIntValidator(1, 50))
        self.starEdit = QtWidgets.QLineEdit()
        self.starEdit.setValidator(QtGui.QIntValidator(1, 10))

        # set auto completion
        creepCompleter = QtWidgets.QCompleter(yysdata.CREEP_LIST)
        self.creepEdit.setCompleter(creepCompleter)
        self.creepEdit.setPlaceholderText('自动补全')

        self.editBtn = QtWidgets.QPushButton('确定')
        self.delBtn = QtWidgets.QPushButton('删除')
        self.editBtn.clicked.connect(self._edit_entry)

    def _edit_entry(self):
        ''' Edit task entry '''

        # 如果按钮显示的是修改，修改当前任务
        if self.editBtn.text() == '修改':
            # 修改样式
            self.creepEdit.setStyleSheet('color: black')
            self.numEdit.setStyleSheet('color: black')
            self.starEdit.setStyleSheet('color: black')
            # 设为可编辑
            self.creepEdit.setReadOnly(False)
            self.numEdit.setReadOnly(False)
            self.starEdit.setReadOnly(False)
            # 重置光标位置
            self.creepEdit.setCursorPosition(0)
            self.numEdit.setCursorPosition(0)
            self.starEdit.setCursorPosition(0)
            # 更改按钮文字
            self.editBtn.setText('更新')
        elif self.editBtn.text() in ('更新', '确定'):
            # 如果按钮显示的是输入/更新，更新当前任务：设为只读
            # 修改样式
            self.creepEdit.setStyleSheet('background-color: #F0F0F0')
            self.numEdit.setStyleSheet('background-color: #F0F0F0')
            self.starEdit.setStyleSheet('background-color: #F0F0F0')
            # 设为只读
            self.creepEdit.setReadOnly(True)
            self.numEdit.setReadOnly(True)
            self.starEdit.setReadOnly(True)
            # 重置光标位置
            self.creepEdit.setCursorPosition(0)
            self.numEdit.setCursorPosition(0)
            self.starEdit.setCursorPosition(0)
            # 更改按钮文字
            self.editBtn.setText('修改')

    def delRow(self):
        ''' Delete current task entry '''

        self.creepEdit.clear()
        self.numEdit.clear()
        self.starEdit.clear()
        self.creepEdit.deleteLater()
        self.numEdit.deleteLater()
        self.starEdit.deleteLater()
        self.editBtn.deleteLater()
        self.delBtn.deleteLater()

    def getInput(self):
        ''' Retrieve input from widgets.
        Returns:
            (creep_name, creep_num, task_star)
        '''

        creep_name = self.creepEdit.text()
        creep_num = self.numEdit.text()
        task_star = self.starEdit.text()

        # if all 3 slots have valid inputs
        if creep_name and creep_num and task_star:
            # make sure creep name is input correctly
            if creep_name in yysdata.CREEP_LIST:
                return (creep_name, int(creep_num), int(task_star))
            else:
                return False
        else:
            return False


class BanEditor(QtWidgets.QGroupBox):
    ''' Edit bans 编辑任务限制条件 '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('编辑任务限定条件')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(False)

        # 如果有设定文件，加载上次关闭程序时的设定。否则初始化默认值
        if path.isfile('data/yyspreset.dat'):
            with open('data/yyspreset.dat', 'r') as f:
                for l in f:
                    info = l.split()
                    if info[0] == 'isBoss':
                        self.isBoss = int(info[1])
                    elif info[0] == 'isTeam':
                        self.isTeam = int(info[1])
                    elif info[0] == 'isYH':
                        self.isYH = int(info[1])
                    elif info[0] == 'isMW':
                        self.isMW = int(info[1])
                    elif info[0] == 'yhLevel':
                        self.yhMinLevel = int(info[1])
                        self.yhMaxLevel = int(info[2])
                    elif info[0] == 'mwLevel':
                        self.mwMinLevel = int(info[1])
                        self.mwMaxLevel = int(info[2])
                    else:
                        pass
        else:
            self.isBoss = 0
            self.isTeam = 0
            self.isYH = 0
            self.isMW = 0
            self.yhMinLevel = 0
            self.yhMaxLevel = 0
            self.mwMinLevel = 0
            self.mwMaxLevel = 0

        # initialize widgets
        self.bossSel = QtWidgets.QCheckBox('允许攻打探索副本首领')
        self.bossSel.setTristate(False)
        self.bossSel.setCheckState(self.isBoss)
        self.teamSel = QtWidgets.QCheckBox('可以组队')
        self.teamSel.setTristate(False)
        self.teamSel.setCheckState(self.isTeam)
        self.bossSel.setMaximumWidth(240)
        self.teamSel.setMaximumWidth(240)
        self.yhSel = QtWidgets.QCheckBox('攻打御魂副本')
        self.yhSel.setTristate(False)
        self.yhSel.setCheckState(self.isYH)
        self.mwSel = QtWidgets.QCheckBox('攻打秘闻副本')
        self.mwSel.setTristate(False)
        self.mwSel.setCheckState(self.isMW)
        self.yhSel.setMaximumWidth(200)
        self.mwSel.setMaximumWidth(200)
        yhLabel = QtWidgets.QLabel('≤ 御魂副本层数 ≤')
        mwLabel = QtWidgets.QLabel('≤ 秘闻副本层数 ≤')
        yhLabel.setMaximumWidth(140)
        mwLabel.setMaximumWidth(140)
        self.yhMinLevelEdit = QtWidgets.QLineEdit(str(self.yhMinLevel))
        self.yhMaxLevelEdit = QtWidgets.QLineEdit(str(self.yhMaxLevel))
        self.yhMinLevelEdit.setValidator(QtGui.QIntValidator(1, 10))
        self.yhMaxLevelEdit.setValidator(QtGui.QIntValidator(1, 10))
        self.mwMinLevelEdit = QtWidgets.QLineEdit(str(self.mwMinLevel))
        self.mwMaxLevelEdit = QtWidgets.QLineEdit(str(self.mwMaxLevel))
        self.mwMinLevelEdit.setValidator(QtGui.QIntValidator(1, 10))
        self.mwMaxLevelEdit.setValidator(QtGui.QIntValidator(1, 10))
        self.yhMinLevelEdit.setMaximumWidth(35)
        self.yhMaxLevelEdit.setMaximumWidth(35)
        self.mwMinLevelEdit.setMaximumWidth(35)
        self.mwMaxLevelEdit.setMaximumWidth(35)
        # initialize edit box style
        self._yh_state(self.yhSel.checkState())
        self._mw_state(self.mwSel.checkState())
        # dynamically reassign validator
        self.yhMinLevelEdit.editingFinished.connect(self._reval_yhmax)
        self.yhMaxLevelEdit.editingFinished.connect(self._reval_yhmin)
        self.mwMinLevelEdit.editingFinished.connect(self._reval_mwmax)
        self.mwMaxLevelEdit.editingFinished.connect(self._reval_mwmin)
        # dynamically set edit box style
        self.yhSel.stateChanged.connect(self._yh_state)
        self.mwSel.stateChanged.connect(self._mw_state)
        self.yhSel.stateChanged.connect(self._refresh)
        self.mwSel.stateChanged.connect(self._refresh)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        mainLayout.addWidget(self.bossSel, 0, 0)
        mainLayout.addWidget(self.teamSel, 1, 0)
        mainLayout.addWidget(self.yhSel, 0, 1)
        mainLayout.addWidget(yhLabel, 0, 3)
        mainLayout.addWidget(self.yhMinLevelEdit, 0, 2)
        mainLayout.addWidget(self.yhMaxLevelEdit, 0, 4)
        mainLayout.addWidget(self.mwSel, 1, 1)
        mainLayout.addWidget(mwLabel, 1, 3)
        mainLayout.addWidget(self.mwMinLevelEdit, 1, 2)
        mainLayout.addWidget(self.mwMaxLevelEdit, 1, 4)
        self.setLayout(mainLayout)

    def banOpts(self):
        ''' Return ban options {'option-name': value} '''

        self._refresh()
        a_dict = {}
        a_dict['isBoss'] = self.isBoss
        a_dict['isTeam'] = self.isTeam
        a_dict['yhLevel'] = (self.yhMinLevel, self.yhMaxLevel)
        a_dict['mwLevel'] = (self.mwMinLevel, self.mwMaxLevel)

        return a_dict

    def _refresh(self):
        ''' Refresh ban options '''

        self.isBoss = self.bossSel.checkState()
        self.isTeam = self.teamSel.checkState()
        self.isYH = self.yhSel.checkState()
        self.isMW = self.mwSel.checkState()
        if self.yhSel.checkState() == QtCore.Qt.Checked:
            self.yhMinLevel = int(self.yhMinLevelEdit.text())
            self.yhMaxLevel = int(self.yhMaxLevelEdit.text())
        else:   # make both 0 will disable yh levels in the calculation
            self.yhMinLevel = 0
            self.yhMaxLevel = 0
        if self.mwSel.checkState() == QtCore.Qt.Checked:
            self.mwMinLevel = int(self.mwMinLevelEdit.text())
            self.mwMaxLevel = int(self.mwMaxLevelEdit.text())
        else:   # make both 0 will disable mw levels in the calculation
            self.mwMinLevel = 0
            self.mwMaxLevel = 0

    def _yh_state(self, state):
        ''' Adjust yh widget state '''
        if state:
            self.yhMinLevelEdit.setReadOnly(False)
            self.yhMaxLevelEdit.setReadOnly(False)
            self.yhMinLevelEdit.setStyleSheet('color: black')
            self.yhMaxLevelEdit.setStyleSheet('color: black')
            if self.yhMinLevelEdit.text() == '0':
                self.yhMinLevelEdit.setText('1')
            if self.yhMaxLevelEdit.text() == '0':
                self.yhMaxLevelEdit.setText('10')
        else:
            self.yhMinLevelEdit.setReadOnly(True)
            self.yhMaxLevelEdit.setReadOnly(True)
            self.yhMinLevelEdit.setStyleSheet('background-color: #F0F0F0')
            self.yhMaxLevelEdit.setStyleSheet('background-color: #F0F0F0')

    def _mw_state(self, state):
        ''' Adjust mw widget state '''
        if state:
            self.mwMinLevelEdit.setReadOnly(False)
            self.mwMaxLevelEdit.setReadOnly(False)
            self.mwMinLevelEdit.setStyleSheet('color: black')
            self.mwMaxLevelEdit.setStyleSheet('color: black')
            if self.mwMinLevelEdit.text() == '0':
                self.mwMinLevelEdit.setText('1')
            if self.mwMaxLevelEdit.text() == '0':
                self.mwMaxLevelEdit.setText('10')
        else:
            self.mwMinLevelEdit.setReadOnly(True)
            self.mwMaxLevelEdit.setReadOnly(True)
            self.mwMinLevelEdit.setStyleSheet('background-color: #F0F0F0')
            self.mwMaxLevelEdit.setStyleSheet('background-color: #F0F0F0')

    def _reval_yhmin(self):
        ''' Reset validator for yhmin '''
        self.yhMinLevelEdit.setValidator(QtGui.QIntValidator(1, int(self.yhMaxLevelEdit.text())))

    def _reval_yhmax(self):
        ''' Reset validator for yhmax '''
        self.yhMaxLevelEdit.setValidator(QtGui.QIntValidator(int(self.yhMinLevelEdit.text()), 10))

    def _reval_mwmin(self):
        ''' Reset validator for mwmin '''
        self.mwMinLevelEdit.setValidator(QtGui.QIntValidator(1, int(self.mwMaxLevelEdit.text())))

    def _reval_mwmax(self):
        ''' Reset validator for mwmax '''
        self.mwMaxLevelEdit.setValidator(QtGui.QIntValidator(int(self.mwMinLevelEdit.text()), 10))


class MsgWarning(QtWidgets.QMessageBox):
    ''' Warning message box '''

    def __init__(self, parent, title_text, moretext=''):
        QtWidgets.QWidget.__init__(self, parent)

        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.addButton(QtWidgets.QMessageBox.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)


class MsgResult(QtWidgets.QDialog):
    ''' Result message box '''

    def __init__(self, parent, full_res):
        ''' Arguments: full_res -- {task_star: (status, solution, total_s)}
            status -- pulp status: 'Optimal', 'Unbound', 'Unsolvable'
            solution -- {'level_name': level_num}
            total_s -- total stamina, int
        '''

        QtWidgets.QDialog.__init__(self, parent)

        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setWindowTitle('结果')
        self.resize(QtCore.QSize(600, 600))
        self.setWindowIcon(QtGui.QIcon('logo.jpg'))

        msgWidget = QtWidgets.QWidget()
        self.msgLayout = QtWidgets.QVBoxLayout()
        self.msgLayout.setAlignment(QtCore.Qt.AlignTop)
        self._add_widget(full_res)
        msgWidget.setLayout(self.msgLayout)

        msgArea = QtWidgets.QScrollArea()
        msgArea.setWidgetResizable(True)
        msgArea.setWidget(msgWidget)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(msgArea)
        self.setLayout(mainLayout)

    def _add_widget(self, full_res):
        ''' add result widgets '''

        for key in full_res.keys():
            status, solution, total_s = full_res[key]
            if status == -1 or not(bool(solution)):
                title = '无法完成 ≥{:d} 星的所有任务'.format(key)
                msg = ['当前限制条件下无法完成悬赏任务。请调整限制条件，如允许攻打首领或更多副本层数。']
                self.msgLayout.addWidget(MsgResultEntry(title, msg))
            elif status == 1:
                title = '完成 ≥{:d} 星任务的推荐策略'.format(key)
                msg = []
                n = []
                isBoss = []
                for item in solution:
                    # ([<'level_name'>, ], <value, float>)
                    _b = False
                    names, value = item
                    names.reverse()
                    s = names.pop()
                    if s in yysdata.BOSS_LEVEL_LINK.keys():
                        _b = True
                    else:
                        pass
                    while names:
                        _t = names.pop()
                        if _t in yysdata.BOSS_LEVEL_LINK.keys():
                            _b = True
                        else:
                            pass
                        s += '\n' + _t
                    msg.append(s)
                    n.append(value)
                    isBoss.append(_b)
                msg.append('总消耗体力：{:.0f}'.format(total_s))
                self.msgLayout.addWidget(MsgResultEntry(title, msg, n, isBoss))
            else:
                pass


class MsgResultEntry(QtWidgets.QGroupBox):
    ''' 单个结果条目 '''

    def __init__(self, title, msg, n=[], isBoss=False):
        QtWidgets.QWidget.__init__(self)

        self.setTitle(title)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setCheckable(False)

        # check if task solvable. (non-solvable prob returns only one line)
        if len(msg) == 1:
            mainLayout = QtWidgets.QVBoxLayout()
            _p = QtWidgets.QLabel(msg[0])
            _p.setWordWrap(True)
            _p.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            mainLayout.addWidget(_p)
        else:
            mainLayout = QtWidgets.QGridLayout()
            for i in range(len(msg)-1):
                _p = QtWidgets.QLabel(msg[i])
                _p.setWordWrap(False)
                _p.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
                if isBoss[i]:
                    _q = QtWidgets.QLabel('所有关卡 × {:.0f} 次'.format(n[i]))
                    _q.setStyleSheet('color: #D63333')
                else:
                    _q = QtWidgets.QLabel('任意关卡 × {:.0f} 次'.format(n[i]))
                _q.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
                _q.setMaximumWidth(300)
                _c = Counter()
                mainLayout.addWidget(_p, i, 0)
                mainLayout.addWidget(_q, i, 1)
                mainLayout.addWidget(_c, i, 2)
            _p = QtWidgets.QLabel(msg[-1])
            _p.setWordWrap(True)
            _p.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            mainLayout.addWidget(_p, len(msg), 0)

        self.setLayout(mainLayout)


class Counter(QtWidgets.QWidget):
    ''' 计数器 '''

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.numLabel = QtWidgets.QLineEdit('0')
        self.numLabel.setReadOnly(True)
        self.numLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.plusBtn = QtWidgets.QPushButton('+')
        self.minusBtn = QtWidgets.QPushButton('-')
        self.plusBtn.clicked.connect(self._plus)
        self.minusBtn.clicked.connect(self._minus)
        self.numLabel.setMaximumWidth(50)
        self.plusBtn.setMaximumWidth(30)
        self.minusBtn.setMaximumWidth(30)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.numLabel)
        mainLayout.addWidget(self.plusBtn)
        mainLayout.addWidget(self.minusBtn)
        self.setLayout(mainLayout)
        self.setMaximumWidth(120)

    def _plus(self):
        n = int(self.numLabel.text())
        self.numLabel.setText(str(n+1))

    def _minus(self):
        n = int(self.numLabel.text())
        self.numLabel.setText(str(n-1))
