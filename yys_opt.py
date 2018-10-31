#! encoding = utf-8

'''
阴阳师悬赏封印任务规划器
MF strategy optimizer for Yinyangshi
'''

import sys
from PyQt5 import QtWidgets, QtGui
from gui import Panel


class MainWindow(QtWidgets.QMainWindow):
    '''
        Implements the main window
    '''
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.setStyleSheet('font-size: 10pt; font-family: default')

        # Set global window properties
        self.setWindowTitle('阴阳师悬赏封印任务规划器')
        self.setMinimumWidth(1200)
        self.setMinimumHeight(800)
        self.setWindowIcon(QtGui.QIcon('yys.jpg'))

        self.taskEditor = Panel.TaskEditor(self)
        self.banEditor = Panel.BanEditor(self)
        self.calcBtn = QtWidgets.QPushButton('计算')

        # Set window layout
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(self.taskEditor, 0, 0, 1, 3)
        self.mainLayout.addWidget(self.banEditor, 0, 3, 1, 3)
        self.mainLayout.addWidget(self.calcBtn, 5, 5, 1, 1)

        # Enable main window
        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def on_exit(self):
        self.close()

    def closeEvent(self, event):
        q = QtWidgets.QMessageBox.question(self, '退出？',
                       '确定要退出吗？', QtWidgets.QMessageBox.Yes |
                       QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        if q == QtWidgets.QMessageBox.Yes:
            self.close()
        else:
            event.ignore()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
