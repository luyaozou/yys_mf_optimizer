#! encoding = utf-8

'''
Window panels
定义主窗口中的各模块
'''

from PyQt5 import QtWidgets, QtCore

class TaskEditor(QtWidgets.QGroupBox):
    ''' Edit task list 编辑悬赏任务列表 '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('编辑阴阳师悬赏任务')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(False)

        # add task entries
        addBtn = QtWidgets.QPushButton('添加')
        delBtn = QtWidgets.QPushButton('移除')

        self.entryWidgetList = []
        self.entryLayout = QtWidgets.QGridLayout()
        self.entryLayout.setAlignment(QtCore.Qt.AlignTop)

        # add entries
        self.entryLayout.addWidget(QtWidgets.QLabel('怪物'), 0, 1, 1, 2)
        self.entryLayout.addWidget(QtWidgets.QLabel('数量'), 0, 3, 1, 2)
        self.entryLayout.addWidget(QtWidgets.QLabel('任务星级'), 0, 5, 1, 2)
        self.entryLayout.addWidget(addBtn, 1, 0, 1, 1)


        entryWidgets = QtWidgets.QWidget()
        entryWidgets.setLayout(self.entryLayout)

        entryArea = QtWidgets.QScrollArea()
        entryArea.setWidgetResizable(True)
        entryArea.setWidget(entryWidgets)

        # Set up main layout
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(entryArea)
        self.setLayout(mainLayout)

        addBtn.clicked.connect(self.add_entry)
        delBtn.clicked.connect(self.del_current_entry)

    def add_entry(self):
        '''
        Add a batch entry to the task list
        向悬赏任务列表中添加一个任务
        '''

        pass

    def del_current_entry(self):
        '''
        delete current entry from the task list
        移除列表中的当前任务
        '''

        pass


class BanEditor(QtWidgets.QGroupBox):
    ''' Edit bans 编辑任务限制条件 '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('编辑任务限定条件')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(False)


        # 单选器

        self.selBoss = BanIfSelector('探索副本', '首领')      # 探索副本是否选择打首领
        self.selGroup = BanIfSelector('御魂副本', '组队')     # 御魂副本是否选择组队
        self.selTaskStar = BanIfSelector('任务星级', '高星优先')  # 是否优先考虑高星级任务

        # 其他副本层数
        self.yuhunLevel = BanLevelSelector()    # 御魂副本
        self.miwenLevel = BanLevelSelector()    # 秘闻副本
        selLevel = QtWidgets.QWidget()
        selLevelLayout = QtWidgets.QGridLayout()
        selLevelLayout.setAlignment(QtCore.Qt.AlignTop)
        selLevelLayout.addWidget(QtWidgets.QLabel('副本层数'), 0, 0)
        selLevelLayout.addWidget(QtWidgets.QLabel('御魂副本'), 1, 0)
        selLevelLayout.addWidget(QtWidgets.QLabel('秘闻副本'), 2, 0)
        for i in range(10):
            selLevelLayout.addWidget(QtWidgets.QLabel(str(i+1)), 0, i+1)
            selLevelLayout.addWidget(self.yuhunLevel.level[i], 1, i+1)
            selLevelLayout.addWidget(self.miwenLevel.level[i], 2, i+1)
        selLevel.setLayout(selLevelLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.selBoss)
        mainLayout.addWidget(self.selGroup)
        mainLayout.addWidget(self.selTaskStar)
        mainLayout.addWidget(selLevel)
        self.setLayout(mainLayout)


class BanIfSelector(QtWidgets.QWidget):
    ''' 任务限制条件单选器 '''

    def __init__(self, str1, str2):
        QtWidgets.QWidget.__init__(self)

        selLayout = QtWidgets.QHBoxLayout()
        selLayout.addWidget(QtWidgets.QLabel(str1))
        self.ifBtn = QtWidgets.QCheckBox(str2)
        self.ifBtn.setCheckState(False)
        selLayout.addWidget(self.ifBtn)
        self.setLayout(selLayout)


class BanLevelSelector(QtWidgets.QButtonGroup):
    ''' 副本层数选择器 '''

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.setExclusive(False)

        self.level = []

        for i in range(10):
            _l = QtWidgets.QCheckBox('')
            _l.setChecked(True)
            self.level.append(_l)
            self.addButton(_l)
