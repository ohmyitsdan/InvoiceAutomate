import os
import base64
from datetime import date
from mailmerge import MailMerge
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from docx2pdf import convert
from utils import *
from mail import googleAPIcreds

class Automate:
    def __init__(self, client, company):
        self.userInfo = loadUserInfo()
        self.companyInfo = loadCompanyInfo()
        self.clientname = client
        self.client = self.userInfo[client]
        self.company = self.companyInfo[company]
        self.InvoiceNum = ''

    def genInvoiceNo(self):
        self.start = self.client['start']
        self.mid = int(self.company['lastInvoiceNo']) + 1
        self.mid = str(self.mid)
        while len(self.mid) < 4:
            self.mid = '0' + self.mid
        self.end = self.company['end']
        self.InvoiceNum = self.start + self.mid + self.end
        self.company.update({'lastInvoiceNo': self.mid})
        saveCompanyList(self.companyInfo)

    def createDoc(self, jobDesc, startDate, endDate, PO, other=None):
        self.PO = PO
        self.jobDesc = jobDesc
        self.startDate = startDate
        self.endDate = endDate
        self.dayDiff = endDate - startDate
        self.numDays = str(self.dayDiff.days)
        self.genInvoiceNo()
        self.template = self.company['template']
        self.document = MailMerge(self.template)
        self.other = other
        self.total = str(int(self.company['rate'])*int(self.numDays))
        if not self.startDate.month == self.endDate.month:
            self.daysWorked = '{:%d/%b} - {:%d/%b}'.format(self.startDate, self.endDate)
        else:
            self.daysWorked = '{:%d}-{:%d %b}'.format(self.startDate, self.endDate)

        self.document.merge(
            name = self.client['name'],
            userAddress = self.client['address'],
            phone = self.client['phone'],
            comAddress = self.company['address'],
            rate = self.company['rate'],
            daysWorked = self.numDays,
            Amount = self.total,
            total = self.total,
            date = '{:%d-%b-%Y}'.format(date.today()),
            InvoiceNo = self.InvoiceNum,
            workDays = self.daysWorked,
            po = self.PO,
            jobdesc = self.jobDesc,
            sortcode = self.client['sort'],
            accnum = self.client['accNum']
        )
        if self.other != None:
            self.document.merge(other=self.other)

        self.document.write('Invoices\\'+self.InvoiceNum+'.docx')

    def createPDFfromFile(self):
        convert('Invoices\\'+self.InvoiceNum+'.docx','Invoices\\'+self.InvoiceNum+'.pdf')
        os.remove('Invoices\\'+self.InvoiceNum+'.docx')

    def createEmail(self, body=None):
        self.body = self.company['body']
        if body:
            self.body = body

        self.msg = MIMEMultipart()
        self.msg['From'] = self.client['username']
        self.msg['To'] = os.environ.get('my_email') # To be removed for final version
        # self.msg['To'] = companyInfo[company]['email']
        self.msg['Subject'] = 'Invoice - ' + self.InvoiceNum
        self.msg.attach(MIMEText(self.body, 'plain'))
        self.attachment = open(os.path.join('Invoices',self.InvoiceNum+'.pdf'), "rb")	

        self.instance = MIMEBase('application', 'octet-stream')
        self.instance.set_payload((self.attachment).read())
        encoders.encode_base64(self.instance)
        self.instance.add_header('Content-Disposition', f'attachment; filename= {self.InvoiceNum+".pdf"}')
        self.msg.attach(self.instance)
        self.raw_message = base64.urlsafe_b64encode(self.msg.as_string().encode("utf-8"))
        return {'raw': self.raw_message.decode("utf-8")}

    def sendEmail(self, msg=None):
        self.service = googleAPIcreds()
        if not msg:
            msg = {'raw': self.raw_message.decode("utf-8")}
        try:
            self.message = self.service.users().messages().send(userId='me', body=msg).execute()
            return self.message
        except Exception as e:
            print(f'An error occurred: {e}')
            return None