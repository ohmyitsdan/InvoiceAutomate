import smtplib
import os
import json
import tkinter as tk
from mailmerge import MailMerge
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders 
from docx2pdf import convert
from datetime import date
from tkinter import ttk

# TODO: create gsheets func

# loads the company info from cinfo.json - should be done at start
def loadCompanyinfo():
    global companyInfo
    with open("cinfo.json", "r") as read_file:
        companyInfo = json.load(read_file)

# loads the user info from userinfo.json - should be done at start
def loadUserinfo():
    global userinfo
    with open("userinfo.json", "r") as read_file:
        userinfo = json.load(read_file)

# adds a new company to companyInfo dict
def addCompany(name, add, email, inv, end, rate):
    companyInfo[name]={}
    companyInfo[name].update({"address":add,"email":email,"lastInvoiceNo":inv,
    "end":end,"rate":rate})
    saveCompanyList()

# Updates cinfo.json with updated company info
def saveCompanyList():
    if len(companyInfo) > 1:
        with open("cinfo.json", "w") as write_file:
            json.dump(companyInfo, write_file)
    else:
        print('No Company Info Loaded.')

# Adds a new user to the userinfo dict
def addUser(name, user, password, start, address, accNum, sortCode, phone):
    userinfo[name]={}
    userinfo[name].update({"username":user,"password":password,"start":start,
    "address":address,"accNum":accNum,"sort":sortCode,"phone":phone})   
    saveUserList() 

# Updates userinfo.json with updated user info
def saveUserList():
    if len(userinfo) > 1:
        with open("userinfo.json", "w") as write_file:
            json.dump(userinfo, write_file)
    else:
        print('No User Info Loaded.')

# TODO: Update spreadsheet & tracker with userinfo from form

# Generate Invoice No.
def genInvoiceNo():
    start = userinfo[client].get('start')
    mid = int(companyInfo[company]['lastInvoiceNo']) + 1
    mid = str(mid)
    while len(mid) < 4:
        mid = '0' + mid
    end = companyInfo[company]['end']
    global InvoiceNum
    InvoiceNum = start + mid + end
    companyInfo[company].update({'lastInvoiceNo': mid})
    saveCompanyList()
    return InvoiceNum

# Create Doc based on userinfo from form and save in location
def createDoc(jobDesc, daysWorked, numDays, PO):
    print('Creating Doc...')
    loadCompanyinfo()
    genInvoiceNo()
    template = 'template.docx'
    document = MailMerge(template)
    rate = companyInfo[company]['rate']
    total = str(int(rate)*int(numDays))

    document.merge(
    name = client,
    userAddress = userinfo[client].get('address'),
    phone = userinfo[client].get('phone'),
    comAddress = companyInfo[company]['address'],
    rate = rate,
    daysWorked = numDays,
    Amount = total,
    total = total,
    date = '{:%d-%b-%Y}'.format(date.today()),
    InvoiceNo = InvoiceNum,
    workDays = daysWorked,
    po = PO,
    jobdesc = jobDesc,
    sortcode = userinfo[client].get('sort'),
    accnum = userinfo[client].get('accNum')
    )

    document.write(InvoiceNum + '.docx')
    print('Document Created.')
    createPDFfromFile(InvoiceNum) # Sends Doc to create PDF
    

# Generate PDF from doc
def createPDFfromFile(inFile):
    print('Creating PDF...')
    convert(inFile+'.docx', 'Invoices\\'+inFile+'.pdf')
    print('PDF Created.')
	
# Fills the email with content and sends
def sendemail(body):
    if client in userinfo.keys():                            # Gets user userinfo
        username = userinfo[client].get('username')
        password = userinfo[client].get('password')
    else:
        print('User does not exist')                 

    sub = 'Invoice: ' + InvoiceNum
    path = 'Invoices\\'
    filename = InvoiceNum+'.pdf'
    # MIME adding content and attachment
    msg = MIMEMultipart()                                    # instance of MIMEMultipart
    msg['From'] = username							         # storing the senders email address 
    msg['To'] = companyInfo[company]['email']		         # storing the receivers email address
    msg['Subject'] = sub                                     # storing the subject
    msg.attach(MIMEText(body, 'plain')) 			         # attach the body with the msg instance 

	# filename = "File_name_with_extension"  
    attachment = open(path + r'/' + filename, "rb")	         # open the file to be sent

    instance = MIMEBase('application', 'octet-stream')       # instance of MIMEBase
    instance.set_payload((attachment).read()) 				 # To change the payload into encoded form 
    encoders.encode_base64(instance) 						 # encode into base64 
    instance.add_header('Content-Disposition', f'attachment; filename= {filename}') 
	
	
    msg.attach(instance)                                     # attach the instance to instance 'msg'
    text = msg.as_string()                                   # Converts the Multipart msg into a string 

	# Sending email part
    conn = smtplib.SMTP('smtp.gmail.com', 587)
	# conn.ehlo() # not necessary any longer?
    conn.starttls()
    conn.login(username, password)
	
	# sendemail - filltext needs to have subject + text and \n to separate
    conn.sendmail(username, companyInfo[company]['email'], text)
    conn.quit()
    print('Email Sent.')

def popupSend():
        def acceptSend():            
            body = messageBox.get('1.0', 'end')
            sendemail(body)
            popup.destroy()

        message = f'To whom it may concern,\nPlease find attached an invoice for {jobdesc} for {company}.\n\nIf there is any other information you need please do get in touch.\n\nMany Thanks,\n{client}'
        popup = tk.Tk()
        popup.wm_title("Message Preview")

        header = tk.Label(popup, text='Ready to Send?', bg='gray', padx=200, pady=20, font=LARGE_FONT)
        header.grid(column=0, row=0, columnspan=2)

        fromBox = tk.Label(popup,text='From: '+client, font=normal_font)
        fromBox.grid(column=0, row=1, pady=10)
        toBox = tk.Label(popup,text='To: '+companyInfo[company]['email'], font=normal_font)
        toBox.grid(column=1, row=1, pady=10)
        messageBox = tk.Text(popup, height=20, width=60, font=input_font)
        messageBox.insert(tk.END, message)
        messageBox.grid(pady=10, padx=10, column=0, row=2, columnspan=2)
        attach = tk.Label(popup, text='Attachment: ', font=normal_font)
        attach.grid(column=0, row=3, sticky='e')
        attachfile = ttk.Button(popup, text=InvoiceNum+'.pdf', command=lambda: os.system('Invoices\\'+InvoiceNum+'.pdf'))
        attachfile.grid(column=1, row=3, sticky='w')

        backbtn = ttk.Button(popup, text="Back", command=popup.destroy)
        backbtn.grid(column=0, row=5, pady=10)
        acceptbtn = ttk.Button(popup, text="Send", command=acceptSend)
        acceptbtn.grid(column=1, row=5, pady=10)

        popup.mainloop()

# GUI
LARGE_FONT = ("Verdana", 12)
input_font = ("Monaco", 10)
normal_font = ("Verdana", 10)

class App(tk.Tk):
    # Initialise
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, 'meh.ico')
        tk.Tk.title(self, 'Invoice Automation')
        tk.Tk.geometry(self, '550x500')

        container = tk.Frame(self)                              # Sets a container for everything to show in
        container.grid(column=0, row=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}                                        

        for F in (StartPage, InvoicePage, addCompanyPage, 
        addUserPage):                                           # Pages that can appear in frame
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='ns')
            # frame.columnconfigure(0,weight=1)

        self.show_frame(StartPage)                              # First frame to show

    
    def show_frame(self, cont):                                 # Function to pull frames to front
        frame = self.frames[cont]
        frame.tkraise()

 

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Invoice Automation", bg='gray', pady=20, padx=200, font=LARGE_FONT)
        label.grid(column=0, row=0, columnspan=3, sticky='ew')

        # Nav Buttons
        ttk.Button(self, text='Add a New User', command=lambda: controller.show_frame(addUserPage)).grid(column=1, row=1, pady=5)        
        ttk.Button(self, text='Add a New Company', command=lambda: controller.show_frame(addCompanyPage)).grid(column=1, row=2, pady=5)        
        ttk.Button(self, text='Create an Invoice', command=lambda: controller.show_frame(InvoicePage)).grid(column=1, row=3, pady=5)
        


class InvoicePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        loadCompanyinfo()
        loadUserinfo()
        options = []
        users = []
        for x in companyInfo.keys():                         # Finds Company Info
            options.append(x)
        options.sort()
        for x in userinfo.keys():                            # Finds User Info
            users.append(x)
        users.sort()
            
        def go():
            global company
            global client
            global jobdesc
            jobdesc = enjobDesc.get()
            client = getUser.get()                           # Passes the User to global client
            company = choose.get()                           # Passes the company info to create doc
            createDoc(enjobDesc.get(), enDays.get(), 
            enNoDays.get(), enPO.get())
            popupSend()
            

        def clear_text(self):
            self.companylist.delete(0, 'end')
            self.enjobDesc.delete(0, 'end')
            self.enPO.delete(0, 'end')
            self.enDays.delete(0, 'end')
            self.enNoDays.delete(0, 'end')

        choose = tk.StringVar()
        getUser = tk.StringVar()

        header = tk.Label(self, text='Create an Invoice', bg='gray', padx=200, pady=20, font=LARGE_FONT)
        header.grid(column=0, row=0, columnspan=2)

        # Dropdowns
        lblUser = tk.Label(self, text='User: ', font=normal_font)
        lblUser.grid(column=0, row=1)
        chooseUser = ttk.OptionMenu(self, getUser, 'Choose User', *users)
        chooseUser.grid(column=1, row=1)

        # Text boxes and grid for Invoice Info
        lblCompanyName = tk.Label(self, text='Choose Company:', font=normal_font)
        lblCompanyName.grid(column=0, row=2, pady=5)
        companylist = ttk.OptionMenu(self, choose, 'Choose Company', *options)
        companylist.grid(column=1, row =2, pady=5)
        lbljobDesc = tk.Label(self, text='Job Description:', font=normal_font)
        lbljobDesc.grid(column=0, row =3, pady=5)
        enjobDesc = tk.Entry(self, width=30)
        enjobDesc.grid(column=1, row=3, pady=5)
        lblPO = tk.Label(self, text='PO Number:', font=normal_font)
        lblPO.grid(column=0, row=4, pady=5)
        enPO = tk.Entry(self, width=30)
        enPO.grid(column=1, row=4, pady=5)
        lblDays = tk.Label(self, text='Days Worked:', font=normal_font)
        lblDays.grid(column=0, row=5, pady=5)
        enDays = tk.Entry(self, width=30)
        enDays.grid(column=1, row=5, pady=5)
        lblNoDays = tk.Label(self, text='Number of Days:', font=normal_font)
        lblNoDays.grid(column=0, row=6, pady=5)
        enNoDays = tk.Entry(self, width=30)
        enNoDays.grid(column=1, row=6, pady=5)

        # Nav Buttons
        but = ttk.Button(self, text="Create", command=go)
        but.grid(column=1, row=100, columnspan=2, padx=20, pady=20)
        but1 = ttk.Button(self, text='back', command=lambda: controller.show_frame(StartPage))
        but1.grid(column=0, row=100)
  
class addCompanyPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def createCom():
            addCompany(enCompanyName.get(), enCompanyAdd.get('1.0', 'end'), enCompanyemail.get(), enInvoiceNo.get(),
             enendsIn.get(), enrate.get())

        header = tk.Label(self, text='Add a New Company', bg='gray', padx=200, pady=20, font=LARGE_FONT)
        header.grid(column=0, row=0, columnspan=2)

        lblCompanyName = tk.Label(self, text='Company Name:', font=normal_font, pady=5)
        lblCompanyName.grid(column=0, row=1)
        enCompanyName = tk.Entry(self, width=30, font=input_font)
        enCompanyName.grid(column=1, row=1)
        lblCompanyAdd = tk.Label(self, text='Company Address:', font=normal_font, pady=5)
        lblCompanyAdd.grid(column=0, row=2)
        enCompanyAdd = tk.Text(self, height=5, width=30, font=input_font)
        enCompanyAdd.grid(column=1, row=2)
        lblCompanyemail = tk.Label(self, text='Contact email:', font=normal_font, pady=5)
        lblCompanyemail.grid(column=0, row=3)
        enCompanyemail = tk.Entry(self, width=30, font=input_font)
        enCompanyemail.grid(column=1, row=3)
        lblInvoiceNo = tk.Label(self, text='Last Invoice No:', font=normal_font, pady=5)
        lblInvoiceNo.grid(column=0, row=4)
        enInvoiceNo = tk.Entry(self, width=30, font=input_font)
        enInvoiceNo.grid(column=1, row=4)
        lblendsIn = tk.Label(self, text='Invoice Suffix:', font=normal_font, pady=5)
        lblendsIn.grid(column=0, row=5)
        enendsIn = tk.Entry(self, width=30, font=input_font)
        enendsIn.grid(column=1, row=5)
        lblrate = tk.Label(self, text='Rate:', font=normal_font, pady=5)
        lblrate.grid(column=0, row=6)
        enrate = tk.Entry(self, width=30, font=input_font)
        enrate.grid(column=1, row=6)
        
        # Nav Buttons
        but = ttk.Button(self, text='Create', command=createCom)
        but.grid(column=1, row=100, padx=20, pady=20)     
        but1 = ttk.Button(self, text='back', command=lambda: controller.show_frame(StartPage))
        but1.grid(column=0, row=100)

class addUserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
     
        def createUser():
            addUser(enName.get(), enusername.get(), enpassword.get(), enPrefix.get(), enUserAdd.get('1.0', 'end'),
            enAccNum.get(), enSortCode.get(), enPhone.get())

        header = tk.Label(self, text='Add a New User', bg='gray', padx=200, pady=20, font=LARGE_FONT)
        header.grid(column=0, row=0, columnspan=2)             

        lblName = tk.Label(self, text='Name: ', font=normal_font, pady=5)
        lblName.grid(column=0, row=1)
        enName = tk.Entry(self, width=30, font=input_font)
        enName.grid(column=1, row=1)
        lblusername = tk.Label(self, text='email Username: ', font=normal_font, pady=5)
        lblusername.grid(column=0, row=3)
        enusername = tk.Entry(self, width=30, font=input_font)
        enusername.grid(column=1, row=3)
        lblpassword = tk.Label(self, text='Password: ', font=normal_font, pady=5)
        lblpassword.grid(column=0, row=4)
        enpassword = tk.Entry(self, width=30, font=input_font)
        enpassword.grid(column=1, row=4)
        lblPrefix = tk.Label(self, text='Invoice Prefix:', font=normal_font, pady=5)
        lblPrefix.grid(column=0, row=5)
        enPrefix = tk.Entry(self, width=30, font=input_font)
        enPrefix.grid(column=1, row=5)
        lblUserAdd = tk.Label(self, text='Address:', font=normal_font, pady=5)
        lblUserAdd.grid(column=0, row=6)
        enUserAdd = tk.Text(self, height=5, width=30, font=input_font)
        enUserAdd.grid(column=1, row=6)
        lblAccNum = tk.Label(self, text='Account Number:', font=normal_font, pady=5)
        lblAccNum.grid(column=0, row=7)
        enAccNum = tk.Entry(self, width=30, font=input_font)
        enAccNum.grid(column=1, row=7)
        lblSortCode = tk.Label(self, text='Sort Code:', font=normal_font, pady=5)
        lblSortCode.grid(column=0, row=8)
        enSortCode = tk.Entry(self, width=30, font=input_font)
        enSortCode.grid(column=1, row=8)
        lblPhone = tk.Label(self, text='Phone Number:', font=normal_font, pady=5)
        lblPhone.grid(column=0, row=9)
        enPhone = tk.Entry(self, width=30, font=input_font)
        enPhone.grid(column=1, row=9)

        # Nav Buttons
        but = ttk.Button(self, text='Create', command=createUser)
        but.grid(column=1, row=100, padx=20, pady=20)     
        but1 = ttk.Button(self, text='back', command=lambda: controller.show_frame(StartPage))
        but1.grid(column=0, row=100)


App().mainloop()