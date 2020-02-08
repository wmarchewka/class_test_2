from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer
from support import loader

if __name__ == '__main__':
    app = QApplication(['PORTABLE TESTER'])
    # app.setStyle("fusion")
    loader = loader.Loader()
    # the timer calls itself every 100ms to allow to break in GUI
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # runs every 100ms
    timer.start(100)
    app.exit(app.exec_())