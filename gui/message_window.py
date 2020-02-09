from PyQt5.QtWidgets import QMessageBox

class MessageWindow(QMessageBox):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('QMessageBox')
        self.setGeometry(300, 300, 300, 200)

    def close(self):
        reply = QMessageBox.information("INFO", "CLOSE")
        if reply == QMessageBox.Yes:
            print("YES")
        else:
            print("NO")
