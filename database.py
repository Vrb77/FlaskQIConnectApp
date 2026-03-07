'''
Dictionaries in db:
- users: dictionary to store user information dictionary (email(email), password)
-> Customer related database
- myRequests: maps userid to the list of their submitted requests.
- requestDetails: maps requestID to dictionary that contains request fields
- requestResponses: maps requestID to the list of reponseIDs
- responseDetails: maps responseID to dictionary of response fields.
-> Vendor related database
- myProducts: maps userID to the list of product productIDs
- productDetails: maps productID to product fields - dictionary
- productCustomers: maps productsIDs to matching customer IDs
- customerDetails: maps customerID to customer fields
'''
import base64
from datetime import date, datetime, timedelta
import json
import pickle
import lzma
import os
import uuid
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask,render_template,request,redirect,url_for, flash,send_from_directory,send_file

from flask import Flask
import bcrypt
import threading
import pickle
import lzma
import os
import json
import base64
import smtplib  # For sending emails (SMTP protocol)
from flask import Flask
salt = bcrypt.gensalt(rounds=10)


dbFile_name = "Data.db.xz"
dbFile = os.path.join('data_folder',dbFile_name)
jsonFile_name = "Data.json.xz"
jsonFile = os.path.join('data_folder',jsonFile_name)
UPLOAD_FOLDER ='C:\\Users\\vrbad\\Desktop\\Messaging_project_3\\Messaging_project\\attachment_uploaded'
UPLOAD_FILES_CUSTOMERS='C:\\Users\\vrbad\\Desktop\\Messaging_project_3\\Messaging_project\\upload_customers_files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FILES_CUSTOMERS'] = UPLOAD_FILES_CUSTOMERS

db = {}
users = {}  #userID to userDetails mapping
transactionDict={}
subscriptions = {} #userID to subscription details
requestDetails = {} #requestID to request fields
requestResponses = {} #requestID to responseIDs list
responseDetails = {} #responseID to response fields
productDetails = {} #productID to product details
db['users'] = {}
db['subscriptions'] = {} #assign subscriptons dict
db['requests'] = {} #assign requests dict
db['requestDetails'] = {} #assign requestDetails dict
db['requestResponses'] = {} #assign requestResponses Dict
db['responseDetails'] = {} #assign
RequestFormDict={}
ServiceFormDict={}
MessagesDict={}
VendorContractDetDict={}
OrderByCustomer={}
ProjectReceivedToVendor={}
AdvertisementDict={}
contactDict={}
notificationDict={}
class getID:   
    def __init__(self):
        self.number=1
        self.alpha=chr(ord('a'))
    def generate_id(self):
        self.number+=1
        if self.number==300:
            self.alpha=chr(ord(self.alpha)+1)
            self.number=0       
        date = datetime.now().strftime('%Y-%m-%d')
        id = f"{date}-{self.alpha}{self.number}"
        return id
    
generateIdObj=getID()

def generate_id():
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        unique_id = uuid.uuid4()
        id = f"{timestamp}-{unique_id}"
        return id

def generateID():
        timestamp = datetime.now().strftime('%Y-%m-%d')
        unique_id = uuid.uuid4()
        id = f"{timestamp}-{unique_id}"
        return id

db['users'] = {}
db['transactionDict']={}
db['RequestFormDict'] = {} 
db['ServiceFormDict'] = {} 
db['MessagesDict']={}
db['VendorContractDetDict']={}
db['OrderByCustomer']={}
db['ProjectReceivedToVendor']={}
db['AdvertisementDict']={}
db['contactDict']={}
db['notificationDict']={}


def saveDB():
    global db,generateIdObj
    db['users'] = users
    db['subscriptions']  = subscriptions
    db['RequestFormDict']  = RequestFormDict
    db['ServiceFormDict'] = ServiceFormDict
    db['MessagesDict']=MessagesDict
    db['generate_id']=generateIdObj
    db['VendorContractDetDict']=VendorContractDetDict
    db['ProjectReceivedToVendor']=ProjectReceivedToVendor
    db['OrderByCustomer']=OrderByCustomer
    db['AdvertisementDict']=AdvertisementDict
    db['contactDict']=contactDict
    db['notificationDict']=notificationDict
    db['transactionDict']=transactionDict
    print('saving...')
            # Convert bytes to base64-encoded strings before serialization
    def convert_bytes(obj):
        if isinstance(obj, bytes):
            return {'_bytes_': True, 'data': base64.b64encode(obj).decode('utf-8')}
        return obj

    with open(jsonFile, 'w') as f:
        dict={}
        for key,value in db.items():
            if(key!='generate_id'):
                dict.update({key:value})
        # print(dict)
        json.dump(dict, f, indent=4, default=convert_bytes)

    with lzma.open(dbFile, 'wb') as f:
        pickle.dump(db, f)
    print('Finished writing')

def loadDB():  
    global db,users,subscriptions,RequestFormDict,ServiceFormDict,MessagesDict,generateIdObj,VendorContractDetDict,ProjectReceivedToVendor,OrderByCustomer,AdvertisementDict,contactDict,notificationDict,transactionDict
    
    if os.path.exists(dbFile):
        print('loading dctbrn')
        db.clear()
        with lzma.open(dbFile, 'rb') as f:
            db = pickle.load(f)
        users = db['users']
        subscriptions = db['subscriptions']
        RequestFormDict = db['RequestFormDict']
        ServiceFormDict = db['ServiceFormDict']
        MessagesDict=db['MessagesDict'] 
        generateIdObj=db['generate_id']
        VendorContractDetDict=db['VendorContractDetDict']
        ProjectReceivedToVendor=db['ProjectReceivedToVendor']
        OrderByCustomer=db['OrderByCustomer']
        AdvertisementDict=db['AdvertisementDict']
        contactDict=db['contactDict'] 
        notificationDict=db['notificationDict']  
        transactionDict=db['transactionDict']
    print('ready')

def add_contact_us_form(name,mail,phone,subject,message) :
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    contact_dict={
        "name":name,
        "mail":mail,
        "phone":phone,
        "message":message,
        "subject":subject,
        "timestamp":timestamp,
    }
    if(mail not in contactDict.keys()):
        contactDict[mail]={}
    contactDict[mail][generate_id()]=contact_dict
    saveDB()

'''
----------------------------------------------------------------------------------
Customer related functions
----------------------------------------------------------------------------------
'''
def add_order(email,rid,sid,price):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    id=sid+"_"+rid
    order_dict={
        "rid":rid,
        "sid":sid,
        "order_date":timestamp,
        "price":price,
        "payment_status":"Not Paid",
    }
    if(email not in OrderByCustomer.keys()):
        OrderByCustomer[email]={}
    OrderByCustomer[email][id]=order_dict
    saveDB()

def add_project(email,rid,sid,price):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    id=sid+"_"+rid
    project_dict={
        "rid":rid,
        "sid":sid,
        "project_date":timestamp,
        "price":price,
        "payment_status":"Not Paid",
    }
    if(email not in ProjectReceivedToVendor.keys()):
        ProjectReceivedToVendor[email]={}
    ProjectReceivedToVendor[email][id]=project_dict
    saveDB()

def getOrderDet(email,id):
    order=OrderByCustomer[email][id]
    return order

def getProjectDet(email,id):
    project=ProjectReceivedToVendor[email][id]
    return project

def remove_order(email,request_id,service_id):
    id=service_id+"_"+request_id
    if email in OrderByCustomer:          
            del OrderByCustomer[email][id]
    saveDB()

def remove_project(email,request_id,service_id):
    id=service_id+"_"+request_id
    if email in ProjectReceivedToVendor:          
            del ProjectReceivedToVendor[email][id]
    saveDB()

def changePaymentStatus(email,sid,rid):
    id=sid+"_"+rid
    OrderByCustomer[email][id]['payment_status']="Paid"
    email=getServiceMail(sid)
    ProjectReceivedToVendor[email][id]['payment_status']="Paid"
    saveDB()

def add_request(email,i_need,PicsFiles,objective,specifications,where,when,tentativeWhen,additionalInfo,AdditionalFiles,current_status,closeRequest,selectVendorServiceID,audio,adv_status):
        print('in add request')
        timestamp =datetime.now().strftime("%Y-%m-%d %H:%M")
        request_dict={
            "from":email,
            "i_need":i_need,
            "PicsFiles":PicsFiles,
            "objective":objective,
            "specifications":specifications,          
            "where":where,
            "when":when,
            "tentativeWhen":tentativeWhen,
            "additionalInfo":additionalInfo,
             "AdditionalFiles":AdditionalFiles,
            "timestamp":timestamp,
            "current_status":current_status,
            "closeRequest":closeRequest,
            "selectVendorServiceID":selectVendorServiceID,
            "audio":audio,
            "adv_status":adv_status,
            "combined_data_customer":i_need+" "+objective+" "+specifications+" "+where+" "+when+" "+additionalInfo,      
           
        }
        RequestFormDict[generateIdObj.generate_id()]=request_dict
        saveDB()  

def deleteRequest(rid):
    if rid in RequestFormDict:          
            del RequestFormDict[rid]
    saveDB()

def updateRequest(rid,i_need,objective,specifications,additionalInfo,where,when,tentativeWhen,addPicsfiles,updateAdditionalFiles,current_status,closeRequest,selectVendorServiceID,audio,adv_status):
    global RequestFormDict
    RequestFormDict[rid]['i_need']=i_need
    RequestFormDict[rid]['objective']=objective
    RequestFormDict[rid]['specifications']=specifications
  
    RequestFormDict[rid]['where']=where
    RequestFormDict[rid]['when']=when
    RequestFormDict[rid]['tentativeWhen']=tentativeWhen
    print(' DB addPicsfiles',addPicsfiles)
    RequestFormDict[rid]['PicsFiles']=addPicsfiles
    RequestFormDict[rid]['AdditionalFiles']=updateAdditionalFiles
    RequestFormDict[rid]['additionalInfo']=additionalInfo
    RequestFormDict[rid]['current_status']=current_status
    RequestFormDict[rid]['closeRequest']=closeRequest
    RequestFormDict[rid]['selectVendorServiceID']=selectVendorServiceID
    RequestFormDict[rid]['audio']=audio
    RequestFormDict[rid]['adv_status']=adv_status
    # print(RequestFormDict[rid])
    saveDB()  

def getRequestDetails(request_id):
    return RequestFormDict[request_id]

def myRequests(email):        
    myRequests={}
    for key, value in RequestFormDict.items():
        if (value['from']==email):
            myRequests[key]=value            
    return myRequests

def myOrders(email):
    for key, value in OrderByCustomer.items():
        if (key==email):
            return value
    return "No Orders"

def responses(rid): 
    responses={}
    # vendor responses code starts
    for key in MessagesDict:
        if MessagesDict[key]['service_id'] in ServiceFormDict and MessagesDict[key]['request_id']==rid:
            id=ServiceFormDict[MessagesDict[key]['service_id']]['from']
            vendorName=getUsername(id)
            response_dict={
                 "id":id,
                 "vendorName":vendorName,
            }
            responses[MessagesDict[key]['service_id']]=response_dict
    # vendor responses code ends
    print(responses)
    return responses

'''
----------------------------------------------------------------------------------
Vendor related functions
----------------------------------------------------------------------------------
'''  
def add_registerService_form(email,serviceName,specificFeature,benefits,bestFor,relatedProduct,where,additionalProductRelatedFiles,ProductPics,myServicesInfo,selectedPrImg,allocatedReqIDs,current_status):
     global generateIdObj
     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
     register_dict={
        "serviceName":serviceName,
        "from":email,
        "specificFeature":specificFeature,
        "benefits":benefits,
        "bestFor":bestFor,
        "where":where,
        "relatedProduct":relatedProduct,
        "additionalProductRelatedFiles":additionalProductRelatedFiles,
        "ProductPics":ProductPics,
        "selectedPrImg":selectedPrImg,
        "myServicesInfo":myServicesInfo,
        "current_status":current_status,
        "timestamp":timestamp,
        "allocatedReqIDs":allocatedReqIDs,
        "combined_data_vendor":serviceName+" "+specificFeature+" "+bestFor+" "+where+" "+relatedProduct+" "+myServicesInfo,       
    }
     vendor_name=email
     vendor_registration_info=serviceName+" "+specificFeature+" "+bestFor+" "+where+" "+relatedProduct+" "+myServicesInfo
     ServiceFormDict[generateIdObj.generate_id()]=register_dict
     saveDB()
    
def deleteProduct(sid):
    if sid in ServiceFormDict:          
            del ServiceFormDict[sid]
    saveDB()

def updateProduct(sid,serviceName,specificFeature,benefits,bestFor,where,when,relatedProduct,additionalProductRelatedFiles,ProductPics,myServicesInfo,selectedPrImg,current_status):
    ServiceFormDict[sid]['serviceName']=serviceName
    ServiceFormDict[sid]['specificFeature']=specificFeature
    ServiceFormDict[sid]['benefits']=benefits
    ServiceFormDict[sid]['bestFor']=bestFor
    ServiceFormDict[sid]['where']=where
    ServiceFormDict[sid]['when']=when
    ServiceFormDict[sid]['relatedProduct']=relatedProduct
    ServiceFormDict[sid]['additionalProductRelatedFiles']=additionalProductRelatedFiles
    ServiceFormDict[sid]['ProductPics']=ProductPics
    ServiceFormDict[sid]['selectedPrImg']=selectedPrImg
    ServiceFormDict[sid]['myServicesInfo']=myServicesInfo
    ServiceFormDict[sid]['current_status']=current_status
    # print(ServiceFormDict[sid])
    saveDB() 

def getServiceDetails(service_id):
    return ServiceFormDict[service_id]

def getServiceDetailsCombinedData(service_id):
    return ServiceFormDict[service_id]['combined_data_vendor']

def getServiceMail(sid):
    return ServiceFormDict[sid]['from']
def myProducts(email):
    myProducts={}
    for key, value in ServiceFormDict.items():
        if (value['from']==email):
            myProducts[key]=value
    return myProducts  

def addVendorContractDet(id,when,price):
    print(id)
    VendorContractDict={
        "when":when,
        "price":price,
    }
    VendorContractDetDict[id]=VendorContractDict
    saveDB()

def getVendorContractDet(id):
    if id not in VendorContractDetDict:
        return None
    else:
        return VendorContractDetDict[id]   

def CustomerResponses(sid): 
    responses={}
    # vendor responses code starts
    for key in MessagesDict:
        if MessagesDict[key]['request_id'] in RequestFormDict and MessagesDict[key]['service_id']==sid:
            id=RequestFormDict[MessagesDict[key]['request_id']]['from']
            customerName=users[id]['name']
            response_dict={
                 "id":id,
                 "customerName":customerName,
            }
            responses[MessagesDict[key]['request_id']]=response_dict
    # vendor responses code ends
    print(responses)
    return responses

def myProjects(email):   
    for key, value in ProjectReceivedToVendor.items():
        if (key==email):
            return value
    return "No Projects"

'''
----------------------------------------------------------------------------------
DS Functions
----------------------------------------------------------------------------------
''' 
CustomerMatchingDict={}
def matching_customers(sid):
    combined_data_vendor=ServiceFormDict[sid]['combined_data_vendor']
    #Code for finding matching customers starts
    for customer in RequestFormDict:
        combined_data_customer=RequestFormDict[customer]['combined_data_customer']
        distance=get_distance(combined_data_customer,combined_data_vendor) 
        if(distance!=0):      
            CustomerMatchingDict[customer]=distance
    return CustomerMatchingDict

VendorMatchingDict={}
def matching_vendors(rid):
    combined_data_customer=RequestFormDict[rid]['combined_data_customer']
    #Code for finding matching vendors starts
    for vendor in ServiceFormDict:
        combined_data_vendor=ServiceFormDict[vendor]['combined_data_vendor']
        distance=get_distance(combined_data_customer,combined_data_vendor) 
        if(distance!=0):   
            VendorMatchingDict[vendor]=distance
    return VendorMatchingDict

def get_distance(combined_data_customer,combined_data_vendor):
     # Tokenize and create a vocabulary
    vectorizer = CountVectorizer().fit([combined_data_customer,combined_data_vendor])
    # CountVectorizer
    # Vector representation of sentences
    vector1 = vectorizer.transform([combined_data_customer]).toarray().flatten()
    vector2 = vectorizer.transform([combined_data_vendor]).toarray().flatten()
    # Calculate cosine similarity
    cosine_sim = cosine_similarity([vector1, vector2])[0, 1]
    # print(f"Cosine Similarity: {cosine_sim}")
    return cosine_sim

loadDB()
AdvertisementMatchingDict={}

def all_request_combined_data(email):
    #Code for finding all customer requests combined data starts
    all_req_data=""
    for customer in RequestFormDict:
        if(RequestFormDict[customer]['from']==email):
            combined_data_customer=RequestFormDict[customer]['combined_data_customer']
            all_req_data=all_req_data+" "+combined_data_customer.strip()          
    return all_req_data

def getAdvertisementName(service_id):
    for x, obj in AdvertisementDict.items():   
        for y in obj:
            if(y==service_id):
                return obj[y]["AdvertisementName"]


def all_advertisement_combined_data(email):
    array_matching_ad_sid=[]
    print("type of array match dict:",type(array_matching_ad_sid))
    for key,value in AdvertisementDict.items():
        for key1 in value:
            print("key",key1)
            serviceDet=getServiceDetailsCombinedData(key1)
            all_req_data=all_request_combined_data(email)
            distance=get_distance(serviceDet,all_req_data) 
            print(distance)
            if(distance>0):   
                array_matching_ad_sid.append(key1)
            print("array_matching_ad_sid",array_matching_ad_sid)
    print("array_matching_ad_sid",array_matching_ad_sid)
    AdvertisementMatchingDict[email]=array_matching_ad_sid
    return AdvertisementMatchingDict
# result=all_advertisement_combined_data(email="customer1@gmail.com")
# print("result",result)
# print("advertisement dict",AdvertisementDict)
'''
----------------------------------------------------------------------------------
Messaging related functions
----------------------------------------------------------------------------------
'''     
def addMessage(To,From,message,sendfile_name,request_id,service_id,audioFile_name,videoFile_name):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    msg={
        "from":From,
        "to":To,
        "message":message,
        "file":sendfile_name,
       "audioFile_name":audioFile_name, 
      "videoFile_name":videoFile_name,
        "timestamp":timestamp, 
        "request_id":request_id,
        "service_id":service_id,     
        }
    MessagesDict[generate_id()]=msg
    saveDB()

def getMessages(request_id,service_id):
    Message=[]
    for key, value in MessagesDict.items():
        if ((value['request_id']==request_id and value['service_id']==service_id) or (value['request_id']==service_id and value['service_id']==request_id) ):
            Message.append(value)
    return Message

def lastMessage(request_id,service_id):   
    try:
        Message=[]
        for key, value in MessagesDict.items():
            if ((value['request_id']==request_id and value['service_id']==service_id) or (value['request_id']==service_id and value['service_id']==request_id) ):
                Message.append(value)
        lastMessage=Message[-1]['message'] +" "+Message[-1]['file']+" "+Message[-1]['audioFile_name']+" "+Message[-1]['videoFile_name']
        return lastMessage
    except IndexError:
        error_message = "Index out of range"
        return "No Message"

def getVendorContractPrice(id):
    if id in VendorContractDetDict:
        price=VendorContractDetDict[id]['price']
        return price
    return "-"

def getVendorContractLocation(id):
    if id in VendorContractDetDict:
        when=VendorContractDetDict[id]['when']
        return when
    return "-"

'''
----------------------------------------------------------------------------------
Advertisement
----------------------------------------------------------------------------------
'''
def add_advertisement(email,sid,AdDuration,price,AdvertisementName,AdvertisementHeading,AdvertisementSubHeading,paymentStatus) :
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    AdDuration=int(AdDuration)
    expiry_date = (date.today()  + timedelta(AdDuration)).strftime("%Y-%m-%d")
    print("expiry date",expiry_date)
    add_ad_dict={
        "email":email,
        "sid":sid,
        "AdDuration":AdDuration,
        "price":price,
        "AdvertisementName":AdvertisementName,
        "AdvertisementHeading":AdvertisementHeading,
        "AdvertisementSubHeading":AdvertisementSubHeading,
        "paymentStatus":paymentStatus,
        "advertisementStatus":"active",
        "ad_date":timestamp,
        "expiry_date":expiry_date,
    }
    if(email not in AdvertisementDict.keys()):
        AdvertisementDict[email]={}
    AdvertisementDict[email][sid]=add_ad_dict
    saveDB()


def getAllAdvertisement(email):
    result=all_advertisement_combined_data(email)
    if(result=={}):
        return "No Advertisement"
    return result

def AdPlaced(email): 
    for key, value in AdvertisementDict.items():
        if (key==email):
            return value
    return "No Projects"

def allAdPlaced(): 
    allAdv=[]
    for key, value in AdvertisementDict.items():
        for key1 in value:
            allAdv.append(key1)
    return allAdv
    
def getAdvDetByID(sid):
    for key, value in AdvertisementDict.items():
        print("key in getAdv",key)
        print("value in getAdv",value[sid])
        if (key):
            return value[sid]
    
    
    
def add_nofification(vendorMail,notificationStr):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("in notification function in Database")
    add_notification_dict={
        "notify_date":timestamp,
        "notificationStr":notificationStr,
    }
    if(vendorMail not in notificationDict.keys()):
        notificationDict[vendorMail]={}
    notificationDict[vendorMail][generateID()]=add_notification_dict
    saveDB()

def getAllNotifications(email):
    for key, value in notificationDict.items():
        if (key==email):
            return notificationDict[email]
    return "No Notification"

def popNotification(notificationID,email):
    notificationDict[email].pop(notificationID)
    saveDB()

def delete_advertisement(email,sid):
    del AdvertisementDict[email][sid]
    saveDB()
    return "Adv deleted"

'''
----------------------------------------------------------------------------------
get Profile
----------------------------------------------------------------------------------
'''  
def getCustomerProfile(email):
     custProfile=users[email]
     return custProfile

def getVendorProfile(email):
     vendorProfile=users[email]
     return vendorProfile

def getProfileDetails(email):
    return users[email]

def getUsername(email):
    if 'firstname' not in users[email]:
        name="Not Known"
    else:
        name=users[email]['firstname']
        print("name",name)
    return name

def getUserAddress(email):
    if 'address' not in users[email]:
        address="Not Known"
    else:
        address=users[email]['address']
        print("address",address)
    return address

# Count number of elements in dictionary
def countEle(dict):
    count=len(dict)
    return count

'''
----------------------------------------------------------------------------------
login and account modules related functions
----------------------------------------------------------------------------------
'''  

def hashit(pwd):
    bytes = pwd.encode('utf-8')
    pwd = bcrypt.hashpw(bytes, salt)
    print(pwd)
    return pwd

def userExists(email):
    if email in users:
        return True
    return False

def validateUser(request):
    email = request.form.get('email')
    if email in users:
        pwd = request.form.get('pwd')
        pwd = pwd.encode('utf-8')
        if bcrypt.checkpw(pwd, users[email]['pwd']):
            return True, users[email]['type']
    return False, None

def getUserType(email):
    return users[email]['type']

def getName(email):
    user_info = users.get(email, {})
    firstname = user_info.get('firstname', '')
    lastname = user_info.get('lastname', '')
    name = f"{firstname} {lastname}"
    return name

def setUser(email, pwd):
    print(email,pwd)
    global users
    pwd = hashit(pwd)
    users[email] = {'pwd':pwd}

def setUserType(email, type):
    users[email]['type'] = type

def getUserByEmail(email):
    return users.get(email, None)

def createUser(email, pwd, type):
    if email in users:
       return False
    setUser(email, pwd)
    setUserType(email, type)
    return True
def setPassword(email, new_password):
    # Assuming 'users' is a dictionary in your database
    if email in users:
        users[email]['pwd'] = new_password
        saveDB()  # Make sure to save the changes to the database

# Function to send email
def send_email(email, temp_password):
    # Code to send email using SMTP
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    sender_email = 'your_email@example.com'
    sender_password = 'your_email_password'

    # Create SMTP server connection
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Compose email message
    subject = 'Password Reset Request'
    body = f'Your temporary password is: {temp_password}'
    message = f'Subject: {subject}\n\n{body}'

    # Send email
    server.sendmail(sender_email, email, message)
    # Close SMTP server connection
    server.quit()

def setProfileImg(user_email,filename):
    users[user_email]['profileImg']=filename
    saveDB()

def getUserProfileImg(user_email):
    if 'profileImg' not in users[user_email]:
        img="default_user_img.jpg"
    else:
        img=users[user_email]['profileImg']
    return img


def setName(email, request):
    fn = request.form.get('firstname')
    ln = request.form.get('lastname')

    print(f"Received firstname: {fn}")
    print(f"Received lastname: {ln}")

    # Check if 'firstname' is present in the form data before updating the dictionary
    if fn is not None:
        users[email]['firstname'] = fn  

    # Check if 'lastname' is present in the form data before updating the dictionary
    if ln is not None:
        users[email]['lastname'] = ln

    print(f"Updated firstname: {users[email]['firstname']}")
    print(f"Updated lastname: {users[email]['lastname']}")
    # print(fn)

country_currencies = {
    'India': 'INR',
    'United States': 'USD',
    'United Kingdom': 'GBP',
    'Canada': 'CAD',
    'Australia': 'AUD',
    # Add more country names and currencies as needed
}

def setAddress(email, request):
    st = request.form.get('street')
    city = request.form.get('cityName')
    state = request.form.get('stateName')
    city_code = request.form.get('city')
    state_code = request.form.get('state')
    zip = request.form.get('zip')
    country = request.form.get('countryName')
    country_code=request.form.get("country")  
    phone = request.form.get('phone')
    print(st,city,state,zip,country,country_code)
    users[email]['address'] = {'street':st, 'city': city, 'state':state,'state_code':state_code,'city_code':city_code,
                               'zip':zip, 'country':country ,'country_code':country_code, 'phone':phone}
    
def setCurrency(email, country_name):
    currency_code = country_currencies.get(country_name)
    users[email]['currency'] = {'country': country_name, 'code': currency_code}
   
def setBizInfo(email, request):
    bizname=request.form.get('bizname')
    aboutme=request.form.get('bizaboutme')
    whytochooseme=request.form.get('bizwhytochooseme')
    role=request.form.get('role')
    website = request.form.get('bizwebsite')
    bizstate = request.form.get('bizstateName')
    bizcity =   request.form.get('bizcityName')
    bizstate_code = request.form.get('bizstate')
    bizcity_code =   request.form.get('bizcity')
    bizzip = request.form.get('bizzip')
    bizcountry_code = request.form.get('bizcountry')
    bizcountry = request.form.get('bizcountryName')
    bizphone = request.form.get('bizphone')
    print(bizname, aboutme,role,whytochooseme,website,bizstate,bizcity,bizzip,bizcountry,bizphone)
    users[email]['bizinfo'] = {'bizname':bizname, 'aboutme':aboutme, 'whytochooseme':whytochooseme, 'role':role, 'website':website, 'bizstate':bizstate,
                               'bizcity':bizcity, 'bizzip':bizzip, 'bizcountry':bizcountry,
                               'bizphone':bizphone,'bizstate_code':bizstate_code,'bizcity_code':bizcity_code,'bizcountry_code':bizcountry_code
                               }

def setBizTrue(email):
    users[email]['isbiz'] = 'on'

def setEmptyRequestsList(email):
    users[email]['requests'] = []

def setEmptyProductsList(email):
    users[email]['products'] = []

def saveDatabase():
    t1 = threading.Thread(target = saveDB, args=())
    t1.start()

def setProfile(request, email, user_type = None, update = False):
    # def setProfile(request, user_type=None, update=False):
    # email = request.form.get('email')
   
    setName(email, request)
    setAddress(email, request)
    if user_type == 'vendor':
        setBizInfo(email, request)
    setUserType(email, user_type)
      
    if update:
        # Update profile information in the database
        updateProfileInDatabase(email,user_type, request)
        # updateBizInfo(email, request)

    if not update:
        t = getUserType(email)
        setUserType(email, t)
        setEmptyRequestsList(email)
        setEmptyProductsList(email)
        if user_type == 'vendor':
            setBizTrue(email)

    saveDatabase()

def updateProfileInDatabase(email,user_type, request):
    global users
    # Assuming 'users' is a dictionary in your database
    if email in users:
        new_firstname = request.form.get('firstname')
        new_lastname = request.form.get('lastname')
        new_street = request.form.get('street')
        new_city = request.form.get('cityName')
        new_state = request.form.get('stateName')
        new_zip = request.form.get('zip')
        new_country = request.form.get('countryName')
        country_code=request.form.get('country')
        city_code = request.form.get('city')
        state_code = request.form.get('state')
        new_phone = request.form.get('phone')
        
        bizname = request.form.get('bizname')
        aboutme=request.form.get('bizaboutme')
        whytochooseme=request.form.get('bizwhytochooseme')
        role = request.form.get('role')
        website = request.form.get('bizwebsite')
        bizcountry = request.form.get('bizcountryName')
        bizstate = request.form.get('bizstateName')
        bizcity = request.form.get('bizcityName')
        
        bizzip = request.form.get('bizzip')
        
        bizphone = request.form.get('bizphone')
        bizstate_code = request.form.get('bizstate')
        bizcity_code = request.form.get('bizcity')
        bizcountry_code = request.form.get('bizcountry')
        

        # Update the user's profile information
        if user_type == 'vendor':
            profile_updates = {
            'firstname': new_firstname,
            'lastname': new_lastname,
            'address': {
                'street': new_street,
                'city': new_city,
                'state': new_state,
                'zip': new_zip,
                'country': new_country,
                'country_code':country_code,
                'state_code':state_code,
                'city_code':city_code,
                'phone': new_phone,
            },
            'bizinfo': {
                'bizname': bizname,
                'aboutme':aboutme,
                'whytochooseme':whytochooseme,
                'role': role,
                'website': website,
                'bizstate': bizstate,
                'bizcity': bizcity,
                'bizzip': bizzip,
                'bizcountry': bizcountry,
                'bizphone': bizphone,
                'bizstate_code':bizstate_code,
                'bizcity_code':bizcity_code,
                'bizcountry_code':bizcountry_code,                   
                
            }
        }

        if user_type == 'customer':
            profile_updates = {
            'firstname': new_firstname,
            'lastname': new_lastname,
            'address': {
                'street': new_street,
                'city': new_city,
                'state': new_state,
                'zip': new_zip,
                'country': new_country,
                'country_code':country_code,
                'state_code':state_code,
                'city_code':city_code,
                'phone': new_phone,
            }
            }
        users[email].update(profile_updates)

        # Save the changes to the database
        saveDB()

def getProfile(email):
    return users.get(email, None)

def addTransaction(email,order_name,total,payment_method,date,time):
    # Generate a unique transaction ID
    transaction_id = str(uuid.uuid4())
    # Create a new order dictionary
    new_order = {
        'order_name': order_name,
        'total': total,
        'payment_method': payment_method,
        'date': date,
        'time': time,
    }
    if(email not in transactionDict.keys()):
        transactionDict[email]={}
    transactionDict[email][transaction_id]=new_order
    saveDB()

def getAllTransactions(email):
    if email not in transactionDict.keys():
        transactions="No Transactions"
    else:
        transactions=transactionDict[email]
    return transactions

def getTranDet(tran_key,email):
    return transactionDict[email][tran_key]

# if __name__=='__main__':      
#       loadDB()  
#       saveDB()
#     # generateIdObj =getID()
#     var=generateIdObj.generate_id()
#     print(var)
#     var1=generateIdObj.generate_id()
#     print(var1)
#     var2=generateIdObj.generate_id()
#     print(var2)
#     saveDB()