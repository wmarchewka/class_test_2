from PyQt5.QtWidgets import QMessageBox

# ********************************************************************************
# TODO speed 1 and speed 2 need to be linked and scaled etc
class PopupWindow(QMessageBox):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setWindowTitle('QMessageBox')
        self.setGeometry(300, 300, 300, 200)
        #self.show()

    def close(self):
        #reply = QMessageBox.information(self, display_string)
        reply = QMessageBox.information("INFO", "CLOSE")
        if reply == QMessageBox.Yes:
            print("YES")
        else:
            print("NO")