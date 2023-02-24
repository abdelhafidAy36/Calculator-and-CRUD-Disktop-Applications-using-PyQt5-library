import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import AppCal

class Mainwindows(QWidget):
    def __init__(self):
        super().__init__()
        self.Form = QWidget()
        self.Cal = AppCal.Ui_Form()
        self.Cal.setupUi(self.Form)

        self.Form.setWindowTitle("Calculatrice")
        self.Form.setWindowIcon(QIcon("calculator.png"))

        self.operation = ""
        self.connect_Button()

        self.Form.show()

    def connect_Button(self):
        self.Cal.pushButton_Num0.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num1.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num2.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num3.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num4.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num5.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num6.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num7.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num8.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Num9.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Plus.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Moins.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Mult.clicked.connect(self.Mult)
        self.Cal.pushButton_Div.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Point.clicked.connect(self.Onclicked)
        self.Cal.pushButton_Module.clicked.connect(self.Onclicked)
        self.Cal.pushButton_signal.clicked.connect(self.Signal)
        self.Cal.pushButton_Egal.clicked.connect(self.Egal)
        self.Cal.pushButto_C.clicked.connect(self.C)

    def Onclicked(self):
        btn = self.sender()
        self.operation += btn.text()
        self.Cal.label.setText(self.operation)

    def Mult(self):
        self.operation += '*'
        self.Cal.label.setText(self.operation)

    def Signal(self):
        self.operation = "-(" + self.operation + ')'
        self.Cal.label.setText(self.operation)

    def Egal(self):
        try:
            Resltat = eval(str(self.operation))
            self.operation = str(Resltat)
            self.Cal.label.setText(self.operation[:10])
        except:
            self.operation = ""
            self.Cal.label.setText('Error')

    def C(self):
        self.operation = ""
        self.Cal.label.setText("0")


app = QApplication(sys.argv)
Windows = Mainwindows()
app.exec_()


