import json

def loadCompanyInfo():
    try:
        with open("cinfo.json", "r") as read_file:
            return json.load(read_file)
    except:
        pass

def loadUserInfo():
    try:
        with open("userinfo.json", "r") as read_file:
            return json.load(read_file)
    except:
        pass

# adds a new company to companyInfo dict
def addEditCompany(name, altname, add, email, inv, end, rate, new=True):
    companyInfo = loadCompanyinfo()
    if new:
        companyInfo[name]={}
    companyInfo[name].update({"address":add,"email":email,"lastInvoiceNo":inv,
    "end":end,"rate":rate})
    saveCompanyList(companyInfo)

def saveCompanyList(companyInfo):
    if len(companyInfo) > 1:
        with open("cinfo.json", "w") as write_file:
            json.dump(companyInfo, write_file)

def addUser(name, user, password, start, address, accNum, sortCode, phone, new=True):
    userInfo = loadUserInfo()
    if new:
        userInfo[name]={}
    userInfo[name].update({"username":user,"password":password,"start":start,
    "address":address,"accNum":accNum,"sort":sortCode,"phone":phone})   
    saveUserList(userInfo) 

def saveUserList(userInfo):
    if len(userInfo) > 1:
        with open("userinfo.json", "w") as write_file:
            json.dump(userinfo, write_file)