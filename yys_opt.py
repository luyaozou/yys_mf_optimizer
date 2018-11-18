#! encoding = utf-8

'''
阴阳师悬赏封印任务规划器
MF strategy optimizer for Yinyangshi
'''

import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from gui import Panel
from data import yyslib


class MainWindow(QtWidgets.QMainWindow):
    '''
        Implements the main window
    '''
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.setStyleSheet('font-size: 10pt; font-family: default')

        # Set global window properties
        self.setWindowTitle('阴阳师悬赏封印任务规划器')
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        self.setWindowIcon(QtGui.QIcon('logo.jpg'))
        self.resize(QtCore.QSize(900, 800))

        self.taskEditor = Panel.TaskEditor(self)
        self.banEditor = Panel.BanEditor(self)
        self.calcBtn = QtWidgets.QPushButton('计算')
        self.calcBtn.clicked.connect(self.calc)

        # Set window layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(self.taskEditor)
        self.mainLayout.addWidget(self.banEditor)
        self.mainLayout.addWidget(self.calcBtn)

        # Enable main window
        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        # load data
        yyslib.load_data()

    def on_exit(self):
        self.close()

    def closeEvent(self, event):
        q = QtWidgets.QMessageBox.question(self, '退出？',
                       '确定要退出吗？', QtWidgets.QMessageBox.Yes |
                       QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        if q == QtWidgets.QMessageBox.Yes:
            self._write_setting()
            self.close()
        else:
            event.ignore()

    def calc(self):
        ''' 计算最优任务规划 '''

        task_entries = self.taskEditor.showTasks()
        ban_opts = self.banEditor.banOpts()

        if self._verify(task_entries):
            full_res = yyslib.wrap_all_together(task_entries, ban_opts)
            self.msgResult = Panel.MsgResult(self, full_res)
            self.msgResult.exec_()
        else:
            pass

    def _verify(self, task_entries):
        ''' verify validity. Return boolean '''

        if task_entries:
            for task in task_entries:
                if task:
                    pass
                else:
                    msg = Panel.MsgWarning(self, '参数错误', '任务参数存在空缺或错误，请补全参数或移除多余任务')
                    msg.exec_()
                    return False
                return True
        else:
            msg = Panel.MsgWarning(self, '缺少任务', '请输入至少一个任务')
            msg.exec_()
            return False


    def _write_setting(self):
        ''' Save ban settings to file '''

        with open('data/yyspreset.dat', 'w') as f:
            f.write('isBoss {:d}\n'.format(self.banEditor.isBoss))
            f.write('isTeam {:d}\n'.format(self.banEditor.isTeam))
            f.write('yhLevel {:d} {:d}\n'.format(self.banEditor.yhMinLevel, self.banEditor.yhMaxLevel))
            f.write('mwLevel {:d} {:d}\n'.format(self.banEditor.mwMinLevel, self.banEditor.mwMaxLevel))


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
