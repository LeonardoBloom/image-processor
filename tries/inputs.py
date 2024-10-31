import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QDialog, QDialogButtonBox

class CustomInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Dialog")
        
        # Layout and Widgets
        layout = QVBoxLayout()

        # First Input
        self.input1 = QLineEdit(self)
        self.input1.setPlaceholderText("Enter first value")
        layout.addWidget(self.input1)

        # Second Input
        self.input2 = QLineEdit(self)
        self.input2.setPlaceholderText("Enter second value")
        layout.addWidget(self.input2)

        # OK and Cancel Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def getInputs(self):
        return self.input1.text(), self.input2.text()

class InputDialogExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Input Dialog Example")

        # Layout and Widgets
        layout = QVBoxLayout()

        self.label = QLabel("Your inputs will appear here.", self)
        layout.addWidget(self.label)

        self.button = QPushButton("Enter values", self)
        self.button.clicked.connect(self.showInputDialog)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def showInputDialog(self):
        dialog = CustomInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            input1, input2 = dialog.getInputs()
            self.label.setText(f"Input 1: {input1}, Input 2: {input2}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InputDialogExample()
    ex.show()
    sys.exit(app.exec_())
