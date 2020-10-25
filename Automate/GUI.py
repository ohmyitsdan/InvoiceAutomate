import sys
import Automate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from utils import *

class InvoiceAutomateGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.companyInfo = loadCompanyInfo()
        self.userInfo = loadUserInfo()
        loadUi("ui//InvoiceAutomate.ui", self)
        self.setWindowTitle('Invoice tobenamed')
        self.chooseCompany.setPlaceholderText('Choose a Company')
        self.chooseCompany.addItems(self.companyInfo.keys())
        self.chooseUser.setPlaceholderText('Choose a User')
        self.chooseUser.addItems(self.userInfo.keys())
        self.chooseCompany.blockSignals(True) # Signals are triggering other methods?
        self.chooseUser.blockSignals(True)
        self.jobDesc.setPlaceholderText('Job Description')
        self.PONum.setPlaceholderText('PO Number')
        self.PONeeded.stateChanged.connect(self.PONeededChange)
        self.startDate.setDate(datetime.now()-relativedelta(weeks=2))
        self.endDate.setDate(datetime.now()-relativedelta(weeks=1))
        self.createInvoice.clicked.connect(self.goCreateInvoice)

        # Menu
        self.addUser.triggered.connect(self.addUserClicked)
        self.addCompany.triggered.connect(self.addCompanyClicked)
        self.editCompany.triggered.connect(self.editCompanyClicked)
        self.editUser.triggered.connect(self.editUserClicked)
        self.about.triggered.connect(self.aboutClicked)

    def goCreateInvoice(self):
        self.user = self.chooseUser.currentText()
        self.company = self.chooseCompany.currentText()
        self.desc = self.jobDesc.toPlainText()
        self.PO = self.PONum.toPlainText() if self.PONeeded else None
        self.stDate = self.startDate.date().toPyDate()
        self.endDate = self.endDate.date().toPyDate()
        self.session = Automate.Automate(self.user, self.company)
        self.session.createDoc(
            self.desc, 
            self.stDate,
            self.endDate,
            self.PO
        )
        infoWin = InfoWindow(self)
        infoWin.exec()
        # self.session.createPDFfromFile()
        # self.session.createEmail()
        # self.session.sendEmail()

    def PONeededChange(self):
        if self.PONeeded.isChecked():
            self.PONum.setDisabled(False)
        else:
            self.PONum.setDisabled(True)

    def editCompanyClicked(self):
        editCom = EditCompany(self)
        editCom.exec()

    def editUserClicked(self):
        editUser = EditUser(self)
        editUser.exec()

    def addCompanyClicked(self):
        addCom = AddCompany(self)
        addCom.exec()

    def addUserClicked(self):
        addUser = AddUser(self)
        addUser.exec()

    def aboutClicked(self):
        about = About(self)
        about.exec()


class EditCompany(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui//editCompany.ui", self)
        self.companyInfo = loadCompanyinfo()
        self.chooseCompany.setPlaceholderText('Choose a Company')
        self.chooseCompany.addItems(self.companyInfo.keys())
        self.chooseCompany.currentTextChanged.connect(self.loadCompany)
        self.discardBtn = self.saveDiscardButton.button(QDialogButtonBox.Discard)
        self.discardBtn.clicked.connect(self.discard)
        self.saveBtn = self.saveDiscardButton.button(QDialogButtonBox.Save)
        self.saveBtn.clicked.connect(self.saveCompany)

    def loadCompany(self, company):
        self.cNameBox.setText(self.companyInfo[company]['name'])
        self.cAddressBox.setText(self.companyInfo[company]['address'])
        self.cEmailBox.setText(self.companyInfo[company]['email'])
        self.cInvoiceBox.setText(self.companyInfo[company]['lastInvoiceNo'])
        self.cSuffixBox.setText(self.companyInfo[company]['end'])
        self.cRateBox.setText(self.companyInfo[company]['rate'])

    def saveCompany(self, company):
        addEditCompany(self.chooseCompany.currentText(),
                       self.cNameBox.toPlainText(),
                       self.cAddressBox.toPlainText(),
                       self.cEmailBox.toPlainText(),
                       self.cInvoiceBox.toPlainText(),
                       self.cSuffixBox.toPlainText(),
                       self.cRateBox.toPlainText(),
                       new=False)
        self.discard()

    def deleteCompany(self):
        pass

    def discard(self):
        self.close()

class AddCompany(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui//addCompany.ui", self)

class InfoWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Processing')
        self.setMinimumSize(400,100)
        self.infoLabel = QLabel("", self)
        self.layout = QVBoxLayout(self)
        self.progressBar = QProgressBar()
        self.layout.addWidget(self.infoLabel)
        self.layout.addWidget(self.progressBar)

class EditUser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui//editUser.ui", self)

class AddUser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui//addUser.ui", self)

class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui//about.ui", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InvoiceAutomateGUI()
    win.show()
    sys.exit(app.exec())