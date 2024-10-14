from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(600, 300, 800, 400)
        self.setWindowTitle("Image Processor")
        self.initUI()

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Hey hello")
        self.label.move(50, 50)

        self.bl = QtWidgets.QPushButton(self)
        self.bl.setText("cLICK")
        self.bl.clicked.connect(self.clicked)

    def clicked(self):
        self.label.setText("You pressed the button")
        self.update()

    def update(self):
        self.label.adjustSize()




def clicked():
    print("cliecke")

def window():
    app = QApplication(sys.argv)

    win = MyWindow()
    

    
    win.show()
    sys.exit(app.exec_())

window()