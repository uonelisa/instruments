import time
import instruments
import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


# class Counter:
#     def __init__(self):
#         self.data = np.arange(0, 10000)
#         self.data_ready = True
#
#     def get_data(self):
#         return self.data
#
#     def loop(self):


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    dataReady = QtCore.pyqtSignal(np.ndarray)
    stopped = QtCore.pyqtSignal(bool)
    data = np.arange(0, 10000)
    is_stopped = False

    @QtCore.pyqtSlot()
    def processB(self):
        print("Worker.processB()")
        i = 1
        while (i < 10 and not self.is_stopped):
            self.data = self.data * 1.1
            time.sleep(5)
            self.dataReady.emit(self.data)
            i += 1
        self.finished.emit()


def onDataReady(array):
    plt.plot(array)
    plt.pause(0.01)


app = QtWidgets.QApplication(sys.argv)

thread = QtCore.QThread()
obj = Worker()
obj.dataReady.connect(onDataReady)

obj.moveToThread(thread)

obj.finished.connect(thread.quit)

thread.start()


def on_start():
    QtCore.QMetaObject.invokeMethod(obj, 'processB', Qt.QueuedConnection)


def on_stop():
    thread.quit()
    # TODO: replace this with only killing thread. thread.exit no worky
    # TODO: Need to make a connection to allow process to end by updating worker's is_stopped


window = QtWidgets.QWidget()
window.setWindowTitle("Control Window")
window.show()
layout = QtWidgets.QGridLayout(window)
start_button = QtWidgets.QPushButton('Start', window)
stop_button = QtWidgets.QPushButton('Stop', window)
start_button.clicked.connect(on_start)
stop_button.clicked.connect(on_stop)
layout.addWidget(start_button, 0, 0)
layout.addWidget(stop_button, 1, 0)
window.resize(480, 160)



app.exec_()
thread.finished.connect(app.exit)
