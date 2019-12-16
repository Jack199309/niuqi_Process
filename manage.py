import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWidgets import QMainWindow
from UI.py.untitled import Ui_MainWindow
from UI.py.new_down import download


class QueryWaitThread(QtCore.QThread):
    # 定义线程需要用到的信号
    query_signal = QtCore.pyqtSignal()  # 查询
    on_complete = QtCore.pyqtSignal(int)  # 每次查询完成时发送，可以发送参数
    terminate_thread = QtCore.pyqtSignal()  # 结束线程

    def __init__(self, url, name):
        self.url = url
        self.name = name
        super(QueryWaitThread, self).__init__()

    def run(self):  # 只发送信号，然后休眠。
        try:
            download(self.url, self.name)
        except IndexError:
            print('请输入参数url和要保存的名称')
            self.kill_thread()

    def kill_thread(self):
        self.terminate()


class UsingTest(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(UsingTest, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('牛气学堂')
        # 控件绑定的处理函数
        self.pushButton.clicked.connect(self.spider)

    # 注册按钮绑定函数
    def spider(self):
        url = self.lineEdit.text()  # 获取文本框内容
        name = self.lineEdit_2.text()  # 获取文本框内容
        self.T = QueryWaitThread(url, name)
        self.T.start()  # 开始执行线程函数
        # self.T.join() # 回收线程
        print(123)

    # 重载退出消息提示框
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '信息', '确认退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':  # 程序的入口
    app = QApplication(sys.argv)
    win = UsingTest()
    win.show()
    sys.exit(app.exec_())
