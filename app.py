from base64 import b64encode
import base64
from collections import Counter
from io import BytesIO
from reportlab.pdfgen import canvas
import json
import os
from dotenv import load_dotenv
load_dotenv()
import flask
from flask import Flask, jsonify, make_response,render_template,request,redirect, session,url_for, flash,send_from_directory,send_file
from werkzeug.utils import secure_filename
from flask import render_template
from functools import wraps
import database as DB
from datetime import date, datetime
from wtforms import MultipleFileField
from werkzeug.exceptions import BadRequest

from jinja2 import Environment, FileSystemLoader
import flask
import stripe
import requests
from flask import redirect, url_for , request , flash, session, send_from_directory, jsonify
import flask_login as fl
import re
from flask import render_template
from functools import wraps
import database as db1
from flask_wtf.csrf import CSRFProtect
import json
import bcrypt 
from database import salt
from functools import wraps
import os
from werkzeug.utils import secure_filename
import random  # For generating a temporary password
import string  # For generating a temporary password
import logging
import hashlib
import pycountry
from flask_login import login_user
from geoloc import get_country_from_ip  # Import the function we just created

app = flask.Flask(__name__)

# app.secret_key = 'super secret string'  # Change this!
UPLOAD_FOLDER ='attachment_uploaded'
UPLOAD_FILES_CUSTOMERS='upload_customers_files'
UPLOAD_FILES_VENDORS='upload_vendors_files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FILES_CUSTOMERS'] = UPLOAD_FILES_CUSTOMERS
app.config['UPLOAD_FILES_VENDORS'] = UPLOAD_FILES_VENDORS
# Set a secret key for the Flask application
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# from login module code starts

stripe.api_key =os.getenv("STRIPE_SECRET_KEY")
# Set the UPLOAD_FOLDER_profile configuration variable
UPLOAD_FOLDER_profile = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Configure app to store uploaded images in UPLOAD_FOLDER_profile
app.config['UPLOAD_FOLDER_profile'] = UPLOAD_FOLDER_profile

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index_page():
    return render_template('index.html')

'''
----------------------------------------------------------------------------------
User Login related functions
----------------------------------------------------------------------------------
'''
@app.route('/login',methods=['POST','GET'])

def login():
     if request.method=='POST':
        email=request.form['email']
        valid_user, user_type = db1.validateUser(request=request)
        
        if valid_user and user_type=='customer':
            session['email'] = email
            session['userType'] = 'customer'
            session['userProfileImg'] = DB.getUserProfileImg(email)
            fl.login_user(getUserObj(email))
            return redirect(f'/customer_home')
        elif valid_user and user_type=='vendor':
            session['email'] = email
            session['userType'] = 'vendor'
            session['userProfileImg'] = DB.getUserProfileImg(email)
            fl.login_user(getUserObj(email))
            return redirect(f'/vendor_home')
        else:
            flash('Invalid credentials', category='error')
            return render_template('login.html')
     else: 
        return render_template('login.html')
        

@app.route('/contact_us',methods=['POST','GET'])
def contact_us():
    print("In contact_us fun")
    if fl.current_user.is_authenticated:
        if( session['userType'] == 'customer'):
            breadcrumbs=[
            {'name':'Home','url':f'/customer_home'},
            {'name':'Contact Us','url':f'/contact_us'},
        ] 
        if( session['userType'] == 'vendor'):
            breadcrumbs=[
            {'name':'Home','url':f'/vendor_home'},
            {'name':'Contact Us','url':f'/contact_us'},
        ]        
    else:
        breadcrumbs=[]

    if request.method=="POST":
        name=request.form.get("name")
        mail=request.form.get("mail")
        phone=request.form.get("phone")
        subject=request.form.get('subject')
        message=request.form.get("message")
        DB.add_contact_us_form(name,mail,phone,subject,message)
        if fl.current_user.is_authenticated:
            if( session['userType'] == 'customer'): 
                flash("Contact Us form submitted")          
                return redirect(f'/contact_us')
            if( session['userType'] == 'vendor'): 
                flash("Contact Us form submitted")          
                return redirect(f'/contact_us')
        else:
            flash("Contact Us form submitted")
            return redirect(f'/')
    return render_template("Common/contact_form.html",breadcrumbs=breadcrumbs)
@app.route('/oops_page')
def oops_page():
    return render_template("Common/Oops_page.html")
'''
----------------------------------------------------------------------------------
Customer pages
----------------------------------------------------------------------------------
'''

# 'url':f'/customer_home'
@app.route('/customer_home')

def customer_home():
   AccType=DB.users[session['email']]['type']
   user = db1.getProfile(session['email'])
   print("user info",user)
   user_img=user.get('profileImg')
   print(user_img)
   if user_img==None:
       user_img="default_user_img.jpg"
   breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
    ]
   return render_template("Customer/customer_home.html",AccType=AccType,session=session,breadcrumbs=breadcrumbs,user_img=user_img)


@app.route('/request_form',methods=['POST','GET'])
def request_form():
    email=session['email']
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'Request Form','url':f'/request_form'},
    ]
    if request.method=='POST':
        i_need=request.form.get('i_need')
        addPics=request.files.getlist('AddPics')
        objective=request.form.get('objective')
        specification=request.form.get('specifications')
        where=request.form.get('where')
        when=request.form.get('when')
        tentativeWhen=request.form.get('tentativeWhen')
        adv_status=request.form.get('adv_status')
        additionalInfo=request.form.get("additionalInfo")
        additionalFiles=request.files.getlist('additionalFiles')
        current_status=request.form.get('status')
        closeRequest=request.form.get("closeButton")
        selectVendorServiceID=request.form.get("selectVendorServiceID")
        audio=request.files['AudioFile']
        audioFile=audio.filename
        print("Audio file")
        print("saveAudio",audio)
        if(audio.filename!=''):
            file_name = secure_filename(audio.filename)
            audio.save(os.path.join(app.config['UPLOAD_FILES_CUSTOMERS'],file_name))

        PicsFiles=[]
        if(addPics[0].filename!=''):
            for file in addPics:              
                file_name = secure_filename(file.filename)
                PicsFiles.append(file_name)
                file.save(os.path.join(app.config['UPLOAD_FILES_CUSTOMERS'],file_name))
        
        AdditionalFiles=[]
        if(additionalFiles[0].filename!=''):
            for file in additionalFiles:           
                file_name = secure_filename(file.filename)
                AdditionalFiles.append(file_name)
                file.save(os.path.join(app.config['UPLOAD_FILES_CUSTOMERS'],file_name))
        DB.add_request(email,i_need,PicsFiles,objective,specification,where,when,tentativeWhen,additionalInfo,AdditionalFiles,current_status,closeRequest,selectVendorServiceID,audioFile,adv_status)
        flash('Request added Successfully. Vendors will review your request & approach you soon! Till then you will find more details here')
        return redirect(f'/my_requests')
    else:
         return render_template("Customer/request_form.html",breadcrumbs=breadcrumbs)

@app.route('/infoOfHowToSubmitRequest')
def infoOfHowToSubmitRequest():
    return render_template("Customer/infoOfHowToSubmitRequest.html")
   
# 'url':f'/my_requests'    
@app.route('/my_requests')

def my_requests():
    myRequests=DB.myRequests(session['email'])
    count=DB.countEle(myRequests)
    myRequests=reversed(list(myRequests.items()))
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'My Requests','url':f'/my_requests'},
    ]
    context={
        'session':session,
        'myRequests':myRequests,
        'count':count,
        'breadcrumbs':breadcrumbs,
    }
    return render_template("Customer/my_requests.html",**context)

# 'url':f'/deleteRequest/{rid}'
@app.route('/deleteRequest', methods=['POST','GET'])
def deleteRequest():
    rid = flask.request.args.get('rid')
    rd = DB.getRequestDetails(rid)
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'My Requests','url':f'/my_requests'},
        {'name':'Delete Request','url':f'/deleteRequest/{rid}'}
    ] 
    context={
        'rd':rd,
        'rid':rid,
        'breadcrumbs':breadcrumbs,
    }
    if request.method=='POST':
        print('in delete post')
        DB.deleteRequest(rid)
        flash('Request deleted')
        return redirect('my_requests')   
    return render_template("Customer/delete_request.html",**context)

# 'url':f'/updateRequest/{rid}'
@app.route('/updateRequest', methods=['POST','GET'])
def update_request_form():
    rid = flask.request.args.get('rid')
    rd = DB.getRequestDetails(rid)
    if(rd['PicsFiles']==['']):
        LenPicsFiles=0   
    else:
        LenPicsFiles=len(rd['PicsFiles'])

    if(rd['AdditionalFiles']==['']):
        LenAdditionalFiles=0   
    else:
        LenAdditionalFiles=len(rd['AdditionalFiles'])
    print('LenPicsFiles',LenPicsFiles)
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'My Requests','url':f'/my_requests'},
        {'name':'View and Update Request','url':f'/updateRequest?rid={rid}'}
    ] 
    context={
        'rd':rd,
        'rid':rid,
        'breadcrumbs':breadcrumbs,
        'LenPicsFiles':LenPicsFiles,
        'LenAdditionalFiles':LenAdditionalFiles,
    }   
    if request.method=="POST":
        i_need=request.form.get('i_need')
        addPics=request.files.getlist('AddPics')
        prevFiles=request.form.get("prevFiles")
        print('prevFiles before split',prevFiles)
        PrevPics=prevFiles.split(",")
        print('PrevPics after split',PrevPics)
        objective=request.form.get('objective')
        specifications=request.form.get('specifications')
        
        where=request.form.get('where')
        when=request.form.get('when')
        tentativeWhen=request.form.get('tentativeWhen')
        adv_status=request.form.get('adv_status')

        additionalFiles=request.files.getlist('additionalFiles')
        additionalInfo=request.form.get("additionalInfo")
        addPrevFiles=request.form.get("addPrevFiles")
        PrevAddFiles=addPrevFiles.split(",")
        audio=request.files['AudioFile']
        audioFile=audio.filename
        current_status=request.form.get('status')
        print(current_status)
        closeRequest=request.form.get("closeButton")
        selectVendorServiceID=request.form.get("selectVendorServiceID")
        if(current_status=="Request is closed" and rd['selectVendorServiceID']!=''):
            DB.remove_order(rd['from'],rid,rd['selectVendorServiceID'])
            vendor_mail=DB.getServiceDetails(rd['selectVendorServiceID'])['from']
            DB.remove_project(vendor_mail,rid,rd['selectVendorServiceID'])
            selectVendorServiceID=""

        if(audio.filename!=''):
            file_name = secure_filename(audio.filename)
            audio.save(os.path.join(app.config['UPLOAD_FILES_CUSTOMERS'],file_name))

        addPicsfiles=[]
        if(addPics[0].filename!=''):
            for file in addPics:  
                file_name = secure_filename(file.filename)
                addPicsfiles.append(file_name)
                file.save(os.path.join(app.config['UPLOAD_FILES_CUSTOMERS'],file_name))
        print('addPicsfiles',addPicsfiles)
        updateAdditionalFiles=[]
        if(additionalFiles[0].filename!=''):
            for file in additionalFiles:  
                file_name = secure_filename(file.filename)
                updateAdditionalFiles.append(file_name)
                file.save(os.path.join(app.config['UPLOAD_FILES_CUSTOMERS'],file_name))

        if(rd['PicsFiles']==[''] or PrevPics==[''] ):
            res_list=addPicsfiles
            print("res_list in if",res_list)
        else:
            print("PrevPics",*PrevPics)
            res_list=[*addPicsfiles,*PrevPics]
        print("res_list",res_list)
        if(rd['AdditionalFiles']==[''] or PrevAddFiles==['']):
            resAddList=updateAdditionalFiles
        else:
            resAddList=[*updateAdditionalFiles,*PrevAddFiles]

        DB.updateRequest(rid,i_need,objective,specifications,additionalInfo,where,when,tentativeWhen,res_list,resAddList,current_status,closeRequest,selectVendorServiceID,audioFile,adv_status)
        flash('Request updated')
        return redirect('/my_requests')
    else:
        return render_template("Customer/update_request.html",**context)

@app.route('/vendor_profile',methods=['GET'])
def vendor_profile():
    email=flask.request.args.get("email")
    rid=flask.request.args.get("rid")
    sid=flask.request.args.get("sid")
    sd = DB.getServiceDetails(sid) 
    vd=DB.getVendorProfile(email)
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'My Requests','url':f'/my_requests'},
       {'name':'Vendor Responses','url':f'/vendor_responses_details?rid={rid}'},
       {'name':'Vendor Profile','url':f'/vendor_profile?email={email}&rid={rid}'}
    ] 
    context={
        'vd':vd,
        'sd':sd,
        'email':email,
        'breadcrumbs':breadcrumbs,
    }
    
    return render_template("Customer/vendor_profile.html",**context)

@app.route('/countVendorResponses',methods=['GET'])
def countVendorResponses():
    request_id = flask.request.args.get('request_id')
    responses=DB.responses(request_id)
    count=DB.countEle(responses)
    return jsonify(count)

# 'url':f'/vendor_responses_details/{rid}'
@app.route('/vendor_responses_details', methods=['POST','GET'])
def vendor_response_details():
    rid = flask.request.args.get('rid')
    rd = DB.getRequestDetails(rid) 
    responses=DB.responses(rid)
    count=DB.countEle(responses)
    matchVendors=DB.matching_vendors(rid)
    countMatchvendor=DB.countEle(matchVendors)
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'My Requests','url':f'/my_requests'},
        {'name':'Vendor Responses','url':f'/vendor_responses_details?rid={rid}'}
    ] 

    context={
        'rd':rd,
        'rid':rid,
        'responses':responses,
        'count':count,
        'breadcrumbs':breadcrumbs,
        'matchVendors':matchVendors,
        'countMatchvendor':countMatchvendor,
    }
    return render_template("Customer/vendor_responses_details.html",**context)

@app.route('/countOfMatchVendors',methods=['POST','GET'])
def countOfMatchVendors():
    rid = flask.request.args.get('rid')
    matchVendors=DB.matching_vendors(rid)
    countMatchvendor=DB.countEle(matchVendors)
    return jsonify(countMatchvendor)
    
@app.route('/countOfMatchCustomers',methods=['POST','GET'])
def countOfMatchCustomers():
    sid = flask.request.args.get('sid')
    matchCustomers=DB.matching_customers(sid)
    countMatchcustomer=DB.countEle(matchCustomers)
    return jsonify(countMatchcustomer)
    
@app.route('/vendor_responses', methods=['POST','GET'])
def vendor_response():
    rid = flask.request.args.get('rid')
    responses=DB.responses(rid)
    count=DB.countEle(responses)
    matchVendors=DB.matching_vendors(rid)
    countMatchvendor=DB.countEle(matchVendors)
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'My Requests','url':f'/my_requests'},
        {'name':'Vendor Responses','url':f'/vendor_responses_details?rid={rid}'},
        {'name':'Responses','url':f'/vendor_responses?rid={rid}'}
    ] 
    context={
        'rid':rid,
        'responses':responses,
        'count':count,
        'breadcrumbs':breadcrumbs,
        'matchVendors':matchVendors,
        'countMatchvendor':countMatchvendor,
    }
    return render_template("Customer/responses.html",**context)


@app.route('/messagingFromCustomer', methods=['POST','GET'])
def messagingFromCustomer():
    request_id = flask.request.args.get('request_id')
    service_id = flask.request.args.get('service_id')
    id=service_id+"_"+request_id
    vendorContractDet=DB.getVendorContractDet(id)
    sd = DB.getServiceDetails(service_id)
    rd = DB.getRequestDetails(request_id) 
    vd=DB.getVendorProfile(sd['from'])
    To=sd['from']
    From=rd['from']
    Messages=reversed(list(DB.getMessages(request_id,service_id)))
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'My Requests','url':f'/my_requests'},
        {'name':'Vendor Responses','url':f'/vendor_responses_details?rid={request_id}'},
        {'name':'Contact', 'url':f'/messagingFromCustomer?service_id={service_id}&request_id={request_id}'},   
    ] 
    context={
        'To':To,
        'From':From,
        'sd':sd,
        'rd':rd,
        'vd':vd,
        'session':session,
        'Messages':Messages, 
        "request_id":request_id,
        "service_id":service_id,  
        'breadcrumbs':breadcrumbs,
        'vendorContractDet':vendorContractDet,    
    }
    if request.method=="POST":
        if (rd['selectVendorServiceID']!=service_id and rd['selectVendorServiceID']!='') :   
            print(DB.ServiceFormDict[service_id]['allocatedReqIDs'])   
            if(request_id in DB.ServiceFormDict[rd['selectVendorServiceID']]['allocatedReqIDs']):     
                DB.ServiceFormDict[rd['selectVendorServiceID']]['allocatedReqIDs'].remove(request_id)
            DB.remove_order(From,request_id,rd['selectVendorServiceID'])
            DB.remove_project(To,request_id,rd['selectVendorServiceID'])  
        print(DB.getVendorContractPrice(id))
        if(DB.getVendorContractPrice(id)!="-" and DB.getVendorContractLocation(id)!="-" and rd['current_status']!="Request is closed"):     
            selected_vendor=service_id
            rd['selectVendorServiceID']=selected_vendor
            sd['allocatedReqIDs'].append(request_id)
            DB.saveDB()
            DB.add_order(From,request_id,service_id,vendorContractDet['price'])
            DB.add_project(To,request_id,service_id,vendorContractDet['price'])
            flash('Order is placed')
        else:
            flash('Location or Price is not quoted by vendors or The request is closed', category='error') 
            return render_template("Customer/messaging.html",**context)
            
    return render_template("Customer/messaging.html",**context)

@app.route('/getRequestDetails',methods=['POST','GET'])
def getRequestDetails():
    request_id=flask.request.args.get('request_id')
    rd=DB.getRequestDetails(request_id)
    return rd

@app.route('/customer_orders')
def customer_orders():
    email=flask.request.args.get('email')
    myOrders=DB.myOrders(email)
    if type(myOrders)==str:
        count=0
    else:
        count=DB.countEle(myOrders)
    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'Orders','url':f'/customer_orders?email={email}'},
    ] 
    context={
        'count':count,
        'email':email,
        'myOrders':myOrders,
        'breadcrumbs':breadcrumbs,
    }
    return render_template("Customer/customer_orders.html",**context)

@app.route('/view_order')
def view_order():
    email=flask.request.args.get('email')
    id=flask.request.args.get('id')
    order=DB.getOrderDet(email,id)
    rid=order['rid']
    print(rid)
    sid=order['sid']
    rd=DB.getRequestDetails(rid)
    sd = DB.getServiceDetails(sid)
    vendor_name=DB.getUsername(sd['from'])
    vendor_address=DB.getUserAddress(sd['from'])

    breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'Orders','url':f'/customer_orders?email={email}'},
        {'name':'view_order','url':f'/view_order?email={email}&id={id}'},      
    ] 
    context={
        'rid':rid,
        'sid':sid,
        'sd':sd,
        'rd':rd,
        'order':order,
        'vendor_name':vendor_name,
        'vendor_address':vendor_address,
        'breadcrumbs':breadcrumbs,
        'order_id':id,
    }
    return render_template("Customer/view_order.html",**context)

@app.route('/cancelOrder')
def cancelOrder():   
    rid=flask.request.args.get('rid')
    sid=flask.request.args.get('sid')
    rd=DB.getRequestDetails(rid)
    sd=DB.getServiceDetails(sid)
    DB.ServiceFormDict[sid]['allocatedReqIDs'].remove(rid)
    DB.RequestFormDict[rid]['selectVendorServiceID']=""
    DB.saveDB()
    print("In cancel order fun")  
    customerEmail=session['email'] 
    DB.remove_project(sd['from'],rid,sid)
    DB.remove_order(customerEmail,rid,sid)
    return redirect(url_for('customer_orders', email=customerEmail))

'''
----------------------------------------------------------------------------------
Vendor pages
----------------------------------------------------------------------------------
'''
@app.route('/vendor_home')
def vendor_home():
   AccType=DB.users[session['email']]['type']
   user = db1.getProfile(session['email'])
   print("user info",user)
   user_img=user.get('profileImg')
   print(user_img)
   if user_img==None:
       user_img="default_user_img.jpg"
   breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
    ]
   return render_template("Vendor/vendor_home.html",AccType=AccType,session=session,breadcrumbs=breadcrumbs,user_img=user_img)

@app.route('/register_product_form',methods=['POST','GET'])
def register_product_form():
    email=session['email']
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Register Product Form','url':f'/register_product_form'},
    ]
    if request.method=='POST':
        serviceName=request.form.get('serviceName')
        specificFeature=request.form.get('specificFeature')
        benefits=request.form.get('benefits')
        bestFor=request.form.get('bestFor')
        relatedProduct=request.form.get('relatedProduct')
        addProductPics=request.files.getlist('addProductPics')
        print("add product pics",addProductPics)
        selectedPrImg=request.form.get('productImg')
        print("selected img",selectedPrImg)
        current_status=request.form.get('status')
        allocatedReqID=request.form.get("allocatedReqID")
        allocatedReqIDs=[]
        
        if(allocatedReqID!=""):
            allocatedReqIDs.append(allocatedReqID)

        if((selectedPrImg==None and addProductPics[0].filename=='')):
            selectedPrImg="serviceImg.jpg"
        elif (selectedPrImg==None and addProductPics[0].filename!=''):
            selectedPrImg=addProductPics[0].filename
        print("selected img",selectedPrImg)
        where=request.form.get('where')
        myServicesInfo=request.form.get('myServicesInfo')
        additionalRelatedFiles=request.files.getlist('additionalRelatedFiles')
        ProductPics=[]
        if(addProductPics[0].filename!=''):
            for file in addProductPics:
                file_name=secure_filename(file.filename)
                ProductPics.append(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FILES_VENDORS'],file_name))

        additionalProductRelatedFiles=[]
        if(additionalRelatedFiles[0].filename!=''):
            for file in additionalRelatedFiles:
                file_name=secure_filename(file.filename)
                additionalProductRelatedFiles.append(file_name)
                file.save(os.path.join(app.config['UPLOAD_FILES_VENDORS'],file_name))
 
        DB.add_registerService_form(email,serviceName,specificFeature,benefits,bestFor,relatedProduct,where,additionalProductRelatedFiles,ProductPics,myServicesInfo,selectedPrImg,allocatedReqIDs,current_status) 
        flash('Product/service added')         
        return redirect(f'/my_products')
    else:
         return render_template("Vendor/register_product_form.html",breadcrumbs=breadcrumbs)

@app.route('/infoOfHowToRegisterProduct')
def infoOfHowToRegisterProduct():
    return render_template("Vendor/infoOfHowToRegisterProduct.html")

@app.route('/my_products')
def my_products():
    myProducts=DB.myProducts(session['email'])
    print("My Services",myProducts)
    count=DB.countEle(myProducts)
    myProducts=reversed(list(myProducts.items()))
    AdPlaced=DB.AdPlaced(session['email'])
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Services','url':f'/my_products'},
    ]
    context={
        'session':session,
        'myProducts':myProducts,
        'count':count,
        'breadcrumbs':breadcrumbs,
        'AdPlaced':AdPlaced,
    }
    return render_template("Vendor/my_products.html",**context)

@app.route('/deleteProduct', methods=['POST','GET'])
def deleteProduct():
    sid = flask.request.args.get('sid')
    sd = DB.getServiceDetails(sid)  
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Services','url':f'/my_products'},
        {'name':'Delete Product','url':f'/deleteProduct'},
    ] 
    context={
        'sd':sd,
        'sid':sid,
        'breadcrumbs':breadcrumbs,
    }
    if request.method=='POST':
        DB.deleteProduct(sid)
        flash('Product/Service deleted')
        return redirect('/my_products')
    return render_template("Vendor/delete_register_product.html",**context)

@app.route('/updateProduct', methods=['POST','GET'])
def update_product_form():
    sid = flask.request.args.get('sid')   
    sd = DB.getServiceDetails(sid) 
    AdPlaced=DB.AdPlaced(session['email'])
    print("adv placed",AdPlaced)
    if(sd['ProductPics']==['']):
        LenProductPics=0   
    else:
        LenProductPics=len(sd['ProductPics'])

    if(sd['additionalProductRelatedFiles']==['']):
        LenAdditionalProductRelatedFiles=0   
    else:
        LenAdditionalProductRelatedFiles=len(sd['additionalProductRelatedFiles'])

    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Services','url':f'/my_products'},
        {'name':'View and update Product','url':f'/updateProduct'},
    ] 
    context={
        'sd':sd,
        'sid':sid,
        'breadcrumbs':breadcrumbs,
        'LenProductPics':LenProductPics,
        'LenAdditionalProductRelatedFiles':LenAdditionalProductRelatedFiles,
        'AdPlaced':AdPlaced,
    }
    if request.method=='POST':
        serviceName=request.form.get('serviceName')
        specificFeature=request.form.get('specificFeature')
        benefits=request.form.get('benefits')
        bestFor=request.form.get('bestFor')
        relatedProduct=request.form.get('relatedProduct')
        addProductPics=request.files.getlist('addProductPics')
        selectedPrImg=request.form.get('productImg')
        current_status=request.form.get('status')

        if((selectedPrImg==None and addProductPics[0].filename=='')):
            selectedPrImg="serviceImg.jpg"
        elif (selectedPrImg==None and addProductPics[0].filename!=''):
            selectedPrImg=addProductPics[0].filename
        print("selected img",selectedPrImg)
        prevFiles=request.form.get("prevFiles")
        PrevPicFiles=prevFiles.split(",")

        where=request.form.get('where')
        when=request.form.get('when')
        myServicesInfo=request.form.get('myServicesInfo')
        additionalRelatedFiles=request.files.getlist('additionalRelatedFiles')
        addPrevFiles=request.form.get("addPrevFiles")
        PrevAddFiles=addPrevFiles.split(",")
        ProductPics=[]
        if(addProductPics[0].filename!=''):
            for file in addProductPics:
                file_name=secure_filename(file.filename)
                ProductPics.append(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FILES_VENDORS'],file_name))
       
        additionalProductRelatedFiles=[]
        if(additionalRelatedFiles[0].filename!=''):
            for file in additionalRelatedFiles:
                file_name=secure_filename(file.filename)
                additionalProductRelatedFiles.append(file_name)
                file.save(os.path.join(app.config['UPLOAD_FILES_VENDORS'],file_name))
        if(sd['ProductPics']==[''] or PrevPicFiles==[''] ):
            res_list=ProductPics
        else:
            res_list=[*ProductPics,*PrevPicFiles]

        if(sd['additionalProductRelatedFiles']==[''] or PrevAddFiles==['']):
            resAddList=additionalProductRelatedFiles
        else:
            resAddList=[*additionalProductRelatedFiles,*PrevAddFiles]

        print("res_list",res_list)
        DB.updateProduct(sid,serviceName,specificFeature,benefits,bestFor,where,when,relatedProduct,resAddList,res_list,myServicesInfo,selectedPrImg,current_status)  
        flash('Product/Service updated')              
        return redirect('/my_products')
    else:
        return render_template("Vendor/update_register_product.html",**context)

@app.route('/customer_profile',methods=['GET'])
def customer_profile():
    email=flask.request.args.get("email")
    sid=flask.request.args.get("sid")
    cd=DB.getCustomerProfile(email)
    breadcrumbs=[
       {'name':'Home','url':f'/vendor_home'},
        {'name':'My Services','url':f'/my_products'},
        {'name':'Matching Customers','url':f'/matchingCustomers?sid={sid}'},
       {'name':'Customer Profile','url':f'/customer_profile?email={email}&sid={sid}'}
    ] 
    context={
        'cd':cd,
        'breadcrumbs':breadcrumbs,
    }
    
    return render_template("Vendor/customer_profile.html",**context)

@app.route('/countMatchCustomers',methods=['GET'])
def countMatchCustomers():
    service_id = flask.request.args.get('service_id')
    matchCustomers=DB.matching_customers(service_id)
    count=DB.countEle(matchCustomers)
    return jsonify(count)

@app.route('/matchingCustomers', methods=['POST','GET'])
def matching_customers():
    sid = flask.request.args.get('sid')
    sd = DB.getServiceDetails(sid) 
    # responses=DB.CustomerResponses(sid)
    # count=DB.countEle(responses)
    matchCustomers=DB.matching_customers(sid)
    countMatchCustomer=DB.countEle(matchCustomers)
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Services','url':f'/my_products'},
        {'name':'Matching Customers','url':f'/matchingCustomers?sid={sid}'},
    ] 
    context={
        'sd':sd,
        'sid':sid,
        'matchCustomers':matchCustomers,
        'countMatchCustomer':countMatchCustomer,
        # 'responses':responses,
        # 'count':count,
        'breadcrumbs':breadcrumbs,
    }
    return render_template("Vendor/matching_customers.html",**context)

@app.route('/CustomerResponses', methods=['POST','GET'])
def CustomerResponses():
    sid = flask.request.args.get('sid')
    sd = DB.getServiceDetails(sid) 
    responses=DB.CustomerResponses(sid)
    count=DB.countEle(responses)
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Services','url':f'/my_products'},
        {'name':'Matching Customers','url':f'/matchingCustomers?sid={sid}'},
        {'name':'Customer responses','url':f'/CustomerResponses?sid={sid}'},

    ] 
    context={
        'sd':sd,
        'sid':sid,
        'responses':responses,
        'count':count,
        'breadcrumbs':breadcrumbs,
    }
    return render_template("Vendor/responses.html",**context)


@app.route('/messagingFromVendor', methods=['POST','GET'])
def messagingFromVendor():
    request_id = flask.request.args.get('request_id')
    service_id = flask.request.args.get('service_id')
    sd = DB.getServiceDetails(service_id)
    rd = DB.getRequestDetails(request_id) 
    cd=DB.getVendorProfile(rd['from'])
    id=service_id+"_"+request_id
    vendorContractDet=DB.getVendorContractDet(id)
    To=rd['from']
    From=sd['from']
    Messages=reversed(list(DB.getMessages(request_id,service_id)))
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Services','url':f'/my_products'},
        {'name':'Matching Customers','url':f'/matchingCustomers?sid={service_id}'},
        {'name':'Contact','url':f'/messagingFromVendor?request_id={request_id}&service_id={service_id}'},
    ]
    context={
        'To':To,
        'From':From,
        'sd':sd,
        'rd':rd,
        'cd':cd,
        'session':session,
        'Messages':Messages,
        "request_id":request_id,
        "service_id":service_id, 
        'breadcrumbs':breadcrumbs, 
        'vendorContractDet':vendorContractDet,   
    }
    return render_template("Vendor/messaging.html",**context)

@app.route('/updateVendorContract',methods=['POST','GET'])
def updateVendorContract():
    id=flask.request.args.get('id')
    print("id",id)
    if request.method=="POST":
        when=request.form.get('when')
        price=request.form.get('price', type=int)
    DB.addVendorContractDet(id,when,price)
    flash("Contract details submitted successfully")
    data={
        "when":when,
        "price":price
    }
    return data

@app.route('/getVendorContractPrice',methods=['POST','GET'])
def getVendorContractPrice():
    id=flask.request.args.get('id')
    if id in DB.VendorContractDetDict:
        print(DB.VendorContractDetDict)
        price=DB.VendorContractDetDict[id]['price']

        return jsonify(price)
    return jsonify("-")

@app.route('/getServiceDetails',methods=['POST','GET'])
def getServiceDetails():
    service_id=flask.request.args.get('service_id')
    sd=DB.getServiceDetails(service_id)
    return sd

@app.route('/vendor_projects')
def vendor_projects():
    email=flask.request.args.get('email')
    myProjects=DB.myProjects(email)
    if type(myProjects)==str:
        count=0
    else:
        count=DB.countEle(myProjects)
    print(myProjects)
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Project','url':f'/vendor_projects'},
    ]
    context={
        'email':email,
        'myProjects':myProjects,
         'breadcrumbs':breadcrumbs,
         'count':count, 

    }
    return render_template("Vendor/vendor_projects.html",**context)

@app.route('/view_project_det')
def view_project_det():
    email=flask.request.args.get('email')
    id=flask.request.args.get('id')
    project=DB.getProjectDet(email,id)
    rid=project['rid']
    sid=project['sid']
    rd=DB.getRequestDetails(rid)
    sd = DB.getServiceDetails(sid)
    customer_name=DB.getUsername(rd['from'])
    customer_address=DB.getUserAddress(rd['from'])
    
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'My Project','url':f'/vendor_projects'},
        {'name':'Project Detail','url':f'/view_project_det?request_id={rid}&service_id={sid}'},
    ]
    context={
        'email':email,
        'id':id,
        'rid':rid,
        'sid':sid,
        'sd':sd,
        'rd':rd,
         'breadcrumbs':breadcrumbs, 
        'customer_name':customer_name,
        'customer_address':customer_address,
        'project':project,
    }  
    return render_template("Vendor/view_project_det.html",**context)

'''
----------------------------------------------------------------------------------
common
----------------------------------------------------------------------------------
'''

@app.route('/getUserName',methods=['POST','GET'])
def getUserName():
    email=flask.request.args.get('email')
    name=DB.getUsername(email)
    return jsonify(name)

@app.route('/displayMessages',methods=['POST','GET'])
def displayMessages():
    print("in post form")
    request_id = flask.request.args.get('request_id')
    service_id = flask.request.args.get('service_id')
    sd = DB.getServiceDetails(service_id)
    rd = DB.getRequestDetails(request_id)
    userType=session['userType']
    if(userType=='customer'):
        To=sd['from']
        From=rd['from']
    if(userType=='vendor'):
        To=rd['from']
        From=sd['from']
    Messages=reversed(list(DB.getMessages(request_id,service_id)))
    msg=DB.getMessages(request_id,service_id)
    
    if request.method=="POST":
        message=request.form.get('message')
        sendfile = request.files['messageFile']   
        print("sendFile:",sendfile)
        
        audio=request.files['AudioFile']
        print("saveAudio",audio)

        video=request.files['VideoFile']
        print("saveVideo",video)
       
        if(audio.filename!=''):   
            file_name = secure_filename(audio.filename)
            audio.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

        if(video.filename!=''):   
                    file_name = secure_filename(video.filename)
                    video.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
      
        if(sendfile.filename!=''):   
            file_name = secure_filename(sendfile.filename)
            sendfile.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

        sendfile_name=sendfile.filename
        audioFile_name=audio.filename
        videoFile_name=video.filename
       
        DB.addMessage(To,From,message,sendfile_name,request_id,service_id,audioFile_name,videoFile_name)
        msg=DB.getMessages(request_id,service_id)
        data={
            "msg":msg,
            "To":To,
            "From":From,
            "user":session['email'],
        }
        return data

    else:
        data={
            "msg":msg,
            "To":To,
            "From":From,
            "user":session['email'],
        }

    return data

'''
----------------------------------------------------------------------------------
filter
----------------------------------------------------------------------------------
'''  
@app.template_filter('custom_round')
def custom_round(value):
    return round(value,2)

# Custom filter to subtract two dates
@app.template_filter('date_diff')
def date_diff(date1, date2, date_format='%Y-%m-%d'):
    today=datetime.today().strftime("%Y-%m-%d")
    d1 = datetime.strptime(date1[:10], date_format)
    d2 = datetime.strptime(today, date_format)
    return (d1 - d2).days

'''
----------------------------------------------------------------------------------
Messages
----------------------------------------------------------------------------------
'''
@app.route('/lastMessage', methods=['GET'])
def last_message():
    request_id = flask.request.args.get('request_id')
    service_id = flask.request.args.get('service_id')
    lastMessage=DB.lastMessage(request_id,service_id)
    return jsonify(lastMessage )  

'''
----------------------------------------------------------------------------------
Advertisement
----------------------------------------------------------------------------------
'''
@app.route('/advertisementForm',methods=['POST','GET'])
def advertisementForm():
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Advertisement Form','url':f'/advertisementForm'},
    ]
    sid=flask.request.args.get('sid')
    sd = DB.getServiceDetails(sid) 
    context={
        'sid':sid,
        'sd':sd,
        'breadcrumbs':breadcrumbs,
    }
    return render_template("Vendor/advertisementForm.html",**context)

@app.route('/getAdvertisement',methods=['POST','GET'])
def getAdvertisement():
    advertisement=DB.getAllAdvertisement(session['email'])
    print("in route Advertisement  ",advertisement)
    for email, ids in advertisement.items():
        advertisement[email] = [DB.getAdvertisementName(ad_id) for ad_id in ids]
    return render_template("Common/advertisement.html",advertisement=advertisement)

@app.route('/getAdvertisementName',methods=['POST','GET'])
def getAdvertisementName():
    service_id=flask.request.args.get('service_id')
    name=DB.getAdvertisementName(service_id)
    return name

@app.route('/adRegisterProduct',methods=['POST','GET'])
def adRegisterProduct():
    myProducts=DB.myProducts(session['email'])
    count=DB.countEle(myProducts)
    AdPlaced=DB.AdPlaced(session['email'])
    if type(AdPlaced)==str:
        countAd=0
    else:      
        countAd=DB.countEle(AdPlaced)

    myProducts=reversed(list(myProducts.items()))
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Promote the service','url':f'/adRegisterProduct'},
    ]
    email=session['email']
    context={
        'session':session,
        'myProducts':myProducts,
        'count':count,
        'countAd':countAd,
        'AdPlaced':AdPlaced,   
        'breadcrumbs':breadcrumbs,
        'email':email,
    }
    if request.method=='POST':
        sid=request.form.get('sid')
        AdDuration=request.form.get('AdDuration', type=int)
        price=request.form.get('price', type=int)
        paymentStatus=request.form.get('paymentStatus')
        DB.add_advertisement(email,sid,AdDuration,price,paymentStatus) 
        flash('Advertisement added')         
        return redirect("/addedADProduct")
    else:
        return render_template('Vendor/adRegisterProduct.html',**context)
    

@app.route('/addedADProduct',methods=['POST','GET'])
def addedADProduct():
    email=session['email']   
    AdPlaced=DB.AdPlaced(email)
    if type(AdPlaced)==str:
        count=0
    else:      
        count=DB.countEle(AdPlaced)
        AdPlaced=reversed(list(AdPlaced.items()))
        AdPlaced = list(AdPlaced)

    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Promoted services','url':f'/addedADProduct'},
    ]
    context={
        'email':email,
        'AdPlaced':AdPlaced,      
         'count':count, 
          'breadcrumbs':breadcrumbs,
    }
    return render_template('Vendor/addedADProduct.html',**context)

@app.route('/promoted_services',methods=['POST','GET'])
def promoted_services():
    sid=flask.request.args.get("sid")
    Ad=DB.getAdvDetByID(sid)
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Promoted services','url':f'/promoted_services'},
    ]
    context={
        'Ad':Ad,       
          'breadcrumbs':breadcrumbs,
    }
    return render_template('Common/promoted_services.html',**context)

@app.route('/delete_advertisement',methods=['DELETE'])
def delete_advertisement():
    print("Inside delete advertisement")
    email=session['email']
    sid=flask.request.args.get("sid")
    print(sid)
    result=DB.delete_advertisement(email,sid)
    print(result)
    notificationStr=flask.request.args.get("notificationStr")
    DB.add_nofification(email,notificationStr)
    return redirect('/addedADProduct')

@app.route('/addNotification',methods=['POST','GET'])
def addNotification():
    print("In notification function")
    vendorMail=flask.request.args.get("vendorMail")
    print("vendor mail",vendorMail)
    notificationStr=flask.request.args.get("notificationStr")
    DB.add_nofification(vendorMail,notificationStr)
    print("notification added")

@app.route('/notifications')
def notifications():
    email=session['email'] 
    allNotifications=DB.getAllNotifications(email)
    print(allNotifications)
    if type(allNotifications)==str:
        count=0
    else:      
        count=DB.countEle(allNotifications)
        allNotifications=reversed(list(allNotifications.items()))
    breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'notifications','url':f'/notifications'},
    ]
    context={
        'allNotifications':allNotifications,      
         'count':count, 
          'breadcrumbs':breadcrumbs,
    }
    return render_template("Vendor/vendorNotifications.html",**context)

@app.route('/deleteNotification')
def deleteNotification():
    email=session['email']
    notificationID=flask.request.args.get("notificationID")
    DB.popNotification(notificationID,email)
    print("notification deleted")
    return redirect(f'/notifications')

'''
----------------------------------------------------------------------------------
Others
----------------------------------------------------------------------------------
'''
@app.route('/download_file')
def download_file():
    fname= flask.request.args.get('fname')
    filepath = os.path.join('attachment_uploaded', fname)
    return send_file(filepath, as_attachment=True)

@app.route('/view_file')
def view_file():
    fname=flask.request.args.get('fname')
    fname=fname.replace(" ","_")
    fname=fname.replace("(","")
    fname=fname.replace(")","")
    return send_from_directory(app.config["UPLOAD_FOLDER"], fname) 

@app.route('/view_file_customer')
def view_file_customer():
    fname=flask.request.args.get('fname')
    fname=fname.replace(" ","_")
    fname=fname.replace("(","")
    fname=fname.replace(")","")
    return send_from_directory(app.config["UPLOAD_FILES_CUSTOMERS"], fname) 

@app.route('/view_file_vendor')
def view_file_vendor():
    fname=flask.request.args.get('fname')    
    fname=fname.replace(" ","_")
    fname=fname.replace("(","")
    fname=fname.replace(")","")
    return send_from_directory(app.config["UPLOAD_FILES_VENDORS"],fname) 

# Initialize an empty list to store user input data
transaction_data = []
@app.route('/generate-pdf', methods=['GET', 'POST'])
def generate_pdf():
    plan=request.args.get('plan')
    price=request.args.get('price')
    order_name=request.args.get('price')
    payment_method=request.args.get('payment_method')
    order_date=request.args.get('order_date')
    customer_name=session['email']
    # Validate and store the user input
    
    transaction_data.append({
        'customer_name':customer_name,
        'order_name':order_name,
        'plan': plan,
        'price': price,
        
        'payment_method':payment_method,
        'order_date':order_date,
       
    })
 
    pdf_file = generate_pdf_file()
    transaction_data.clear()
    return send_file(pdf_file, as_attachment=True, download_name='wcs_transaction_receipt.pdf')
 
def generate_pdf_file():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
 
    # Create a PDF document
    p.drawString(100, 750, "Transaction receipt")
 
    y = 700
    for transaction in transaction_data:
        p.drawString(100, y, f"customer_name: {transaction['customer_name']}")
        p.drawString(100, y-20, f"order_name: {transaction['order_name']}")
        p.drawString(100, y-40, f"order_date: {transaction['order_date']}")
        p.drawString(100, y-60, f"plan: {transaction['plan']}")
        p.drawString(100, y-80, f"payment_method: {transaction['payment_method']}")
        p.drawString(100, y - 100, f"price: {transaction['price']}")
        y -= 60
 
    p.showPage()
    p.save()
 
    buffer.seek(0)
    
    return buffer

#login and account module routes starts


'''
----------------------------------------------------------------------------------
User Login related functions
----------------------------------------------------------------------------------
'''

login_manager = fl.LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect()
csrf.init_app(app)



class User(fl.UserMixin): # it defines a custom User
    pass

def getUserObj(email):  #to create a user object based on the provided email address.
    userobj = User()
    userobj.id = email
    userobj.name = db1.getName(email)
    userobj.type = db1.getUserType(email)
    return userobj

@login_manager.user_loader      # user_loader and request_loader functions to load a user object based on the user's email.
def user_loader(email):
    if db1.userExists(email):
        return getUserObj(email)
    return

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if db1.userExists(email):
        return getUserObj(email)
    return

@login_manager.unauthorized_handler
def unauthorized_handler():
    context = {'permissions':'None'}
    return render_template('Common/requireslogin.html', context=context )

def getUserType():              #to retrieve the user type from the database
    if not fl.current_user.is_authenticated:
        return 'anonymous'
    email = fl.current_user.id
    usertype = db1.getUserType(email)
    return usertype

def customeronly(fn):  #check previlages--> switch function(user_type)               #to restrict access to certain routes based on the user's type
    @wraps(fn)
    def validate(*args, **kwargs):
        ut = getUserType()
        if ut == 'customer':
            return fn(*args, **kwargs)
        context = {'permissions':'Customers only'}
        return render_template('Common/requireslogin.html', context=context)
    return validate

def vendoronly(fn):
    @wraps(fn)
    def validate(*args, **kwargs):
        ut = getUserType()
        if ut == 'vendor':
            return fn(*args, **kwargs)
        context = {'permissions':'Vendors only'}
        return render_template('Common/requireslogin.html', context=context)
    return validate

def manageRedirects(page):                     #a function to handle redirects based on user types.
    if page == 'vendor':
        return redirect(url_for('vendor_home'))
    if page == 'customer':
        return redirect(url_for('customer_home'))
    if page == 'login':
        return render_template('Common/profilesettings.html')
    if page == 'userexists':
        return render_template('Common/profilesettings.html')
    return redirect(url_for('about'))

'''
----------------------------------------------------------------------------------
Customer pages
----------------------------------------------------------------------------------
'''
# Import the necessary functions from dbfile.py
# from dbfile import loadDB, saveDB, createUser, setName, setAddress, setBizInfo
# Ensure the database is loaded when the application starts


@app.route('/customers/createaccount', methods=['GET', 'POST'])       #Create Account Route
def createaccount():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        pwd1 = request.form.get('pwd1')
        utype = "customer"

        print(f'email: {email}')
        print(f'pwd: {pwd}')
        print(f'pwd1: {pwd1}')
        print(f'type: {utype}')

        # Validate email format using regular expression
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        
        if not email_pattern.match(email):
            flash('Invalid email format. Please use a valid email address.', category='error')
        elif len(email) < 4:
            flash('Email must be provided and greater than 4 characters.', category='error')
        elif pwd != pwd1:
            flash('Passwords don\'t match.', category='error')
        elif pwd is None or len(pwd) < 7:
            flash('Password must be provided and at least 7 characters.', category='error')
        else:
            # Save the user data to the database
            if db1.createUser(email, pwd, utype):
                session['email'] = email
                 # Save the entire database after creating the user
                db1.saveDB()
                if(utype=="customer"):
                    flash('Customer account created successfully!', category='success')
                if(utype=="vendor"):
                    flash('Vendor account created successfully!', category='success')
                return redirect(url_for('profile_info'))
            else:
                flash('User already exist', category='error')
    return render_template("customers/createaccount.html")

@app.route('/profile_info')
def profile_info():  
    return render_template('Common/profile_info.html')

@app.route('/process_profile_info', methods=['POST', 'GET'])
def process_profile_info():
    if request.method == 'POST':
        create_profile = request.form.get('create_profile')

        if create_profile == 'yes':
            user_email = request.form.get('email')
            if user_email:
                # Store the email in the session
                session['email'] = user_email
                user_type=DB.getUserType(user_email)
                print("user type",user_type)
                return render_template('Common/fill_profile_info.html',user_type=user_type)
            else:
                flash('Email is required for profile creation.', category='error')
            return render_template('Common/fill_profile_info.html',user_type=user_type)
        else:
            return redirect('/account')

    # Handle GET request or other cases
    # You may want to add additional logic or rendering here
    
    # Add a default return statement for other cases
    user_type=DB.getUserType(session['email'])
    return render_template('Common/fill_profile_info.html',user_type=user_type)

@app.route('/countries')
def get_countries():
    countries = [(country.name, country.alpha_2) for country in pycountry.countries]
    return jsonify(countries)

country_currencies = {
    'India': 'INR',
    'United States': 'USD',
    'United Kingdom': 'GBP',
    'Canada': 'CAD',
    'Australia': 'AUD',
    # Add more country names and currencies as needed
}

@app.route('/process_fill_profile_info', methods=['POST', 'GET'])
def process_fill_profile_info():
    if request.method == 'POST':
        # Retrieve form data
        phone = request.form.get('phone')
        zip_code = request.form.get('zip')
        image = request.files['image']  # Retrieve the uploaded image file
        print("profile img",image)
        country_name = request.form.get('countryName')
        state = request.form.get('state')
        city = request.form.get('city')
        country = request.form.get('country')

        # Get the currency code based on the country name
        currency_code = country_currencies.get(country_name)

        if image.filename == '':
            filename="default_user_img.jpg"
        else:
            # Ensure the filename is secure
            filename = secure_filename(image.filename)
            # Add user's email as part of the filename
            user_email = session.get('email')  # Assuming user's email is stored in the session
            if user_email:
                filename = f"{user_email}_{filename}"
            else:
                flash('User email not found in the session. Please try again.', category='error')
                return redirect(url_for('fill_profile_info'))  # Redirect to the profile filling page
            # Save the uploaded image to the uploads folder
            image.save(os.path.join(app.config['UPLOAD_FOLDER_profile'], filename))

        # Print the filename for debugging
        print("Filename:", filename)

        # Assuming you have the user's email available, replace 'user_email' with the actual email variable
        user_email = session.get('email')  # Replace with the actual user's email
        if user_email:
            # Update the profile information in the database using the retrieved email
            db1.setName(user_email, request)
            db1.setAddress(user_email, request)
            # Add the currency code to the user's profile information
            db1.setCurrency(user_email, country_name)
            # Save the entire database after updating user information
            db1.setProfileImg(user_email,filename)
            db1.saveDB()
            user_type=DB.getUserType(user_email)
            if(user_type=="vendor"):
                flash('Profile created successfully', category='success')
                return redirect('/business_info')
            if(user_type=="customer"):
                flash('Customer\'s complete profile created successfully.', category='success')
                return redirect('/login')
        else:
            flash('User email not found in the session. Please try again.', category='error')

    return render_template("Common/fill_profile_info.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER_profile'], filename)

@app.route('/business_info')
def business_info():
    return render_template('Common/business_info.html')

@app.route('/process_business_info', methods=['POST', 'GET'])
def process_business_info():
    if request.method == 'POST':
        fill_business_info = request.form.get('fill_business_info')

        if fill_business_info == 'yes':
            user_email = request.form.get('email')
            if user_email:
                # Store the email in the session
                session['email'] = user_email
                return redirect('/process_fill_business_info')
            else:
                flash('Email is required for Business profile creation.', category='error')
            return render_template('Common/fill_business_info.html')
        else:
            return redirect('/login')
    return render_template('Common/fill_business_info.html')   
    
@app.route('/process_fill_business_info', methods=['POST', 'GET'])
def process_fill_business_info():
    if request.method == 'POST':
        phone = request.form.get('bizphone')
        zip = request.form.get('bizzip')
      
       
        # Assuming you have the user's email available, replace 'user_email' with the actual email variable
        user_email = session.get('email') 
        if user_email:
            db1.setBizInfo(user_email, request)
            # Save the entire database after updating business information
            db1.saveDB()
            flash('Vendor\'s complete profile created successfully.', category='success')
            return redirect(url_for('login'))
        else:
            flash('User email not found in the session. Please try again.', category='error')

    return render_template("Common/fill_business_info.html")

# Ensure the database is saved when the application stops
@app.teardown_appcontext
def save_database_on_shutdown(exception=None):
    db1.saveDB()

'''
----------------------------------------------------------------------------------
Vendor pages
----------------------------------------------------------------------------------
'''
@app.route('/vendors/createaccount', methods=['GET', 'POST'])
def create_vendor_account():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        pwd1 = request.form.get('pwd1')
        utype="vendor"
        print(f'email: {email}')
        print(f'pwd: {pwd}')
        print(f'pwd1: {pwd1}')

        # Validate email format using regular expression
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

        if not email_pattern.match(email):
            flash('Invalid email format. Please use a valid email address.', category='error')
        elif len(email) < 4:
            flash('Email must be provided and greater than 4 characters.', category='error')
        elif pwd != pwd1:
            flash('Passwords don\'t match.', category='error')
        elif pwd is None or len(pwd) < 7:
            flash('Password must be provided and at least 7 characters.', category='error')
        else:
            # Save the user data to the database
            if db1.createUser(email, pwd, utype):
                session['email'] = email
                # Save the entire database after creating the user
                db1.saveDB()
                flash('Account created!', category='success')
                return redirect(url_for('profile_info'))  # Update the redirection based on your application flow
            else:
                flash('User already exists.', category='error')

    return render_template("vendors/vendoraccount.html")  # Update the template path based on your file structure

'''
----------------------------------------------------------------------------------
Admin pages
----------------------------------------------------------------------------------
'''
@app.route('/admin/createaccount', methods=['GET', 'POST'])       #Create Account Route
def create_admin_account():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        pwd1 = request.form.get('pwd1')
        utype = request.form.get('usertype')

        print(f'email: {email}')
        print(f'pwd: {pwd}')
        print(f'pwd1: {pwd1}')
        print(f'type: {utype}')

        # Validate email format using regular expression
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        
        if not email_pattern.match(email):
            flash('Invalid email format. Please use a valid email address.', category='error')
        elif len(email) < 4:
            flash('Email must be provided and greater than 4 characters.', category='error')
        elif pwd != pwd1:
            flash('Passwords don\'t match.', category='error')
        elif pwd is None or len(pwd) < 7:
            flash('Password must be provided and at least 7 characters.', category='error')
        else:
            # Save the user data to the database
            if db1.createUser(request, type='admin'):
                session['email'] = email
                 # Save the entire database after creating the user
                db1.saveDB()
                flash('Account created!', category='success')
                return redirect(url_for('profile_info'))
            else:
                flash('User already exists.', category='error')

    return render_template("admin/createadminaccount.html")

'''
----------------------------------------------------------------------------------
Common pages
----------------------------------------------------------------------------------
'''
@app.route('/account')
def account():
    context = {}
    loggedin = fl.current_user.is_authenticated
    if loggedin == False:
        return loginForm()
    else:
        return profileSettings()

def loginForm():
    return render_template('login.html')

@app.route('/logout')
def logout():
    flask.session.clear()
    fl.logout_user()
    return redirect(url_for('login'))

def createUserAccount(type):
    if flask.request.method =="POST":
        res = db1.createUser(request = flask.request, type=type)
        if res:
            db1.setProfile(request=flask.request)
            #We want user to login automatically on successfuly creating the account
            #No need to login again
            #email = flask.request.form.get('email')
            return manageRedirects('login')
        else:
            return manageRedirects('userexists')
    context = {'accounttype':type }
    return render_template('Common/mainmenu.html', context = context)

@app.route('/Common/profilesettings', methods=['GET', 'POST'])
@fl.login_required
def profileSettings():
    if not fl.current_user.is_authenticated:
        # Redirect to login page if the user is not authenticated
        return redirect(url_for('login'))
    # Retrieve the email from the session
    email = session.get('email')
    
    # Fetch user's name and address from the database
    user = db1.getProfile(email)
    user_img={'profileImg':user.get('profileImg','')}
    if user_img.get('profileImg') =='':
        user_img={'profileImg':'default_user_img.jpg'}

    user_name = {'firstname': user.get('firstname', ''), 'lastname': user.get('lastname', '')}
    print("profile image",user_img)
    user_address = user.get('address', {'street': '', 'city': '', 'state': '', 'zip': '', 'country': '','country_code':'','city_code':'','state_code':'', 'phone': ''})
    print(user_address)
    # Create a context dictionary to pass to the template
    # Fetch user's business info from the database
    business_info = user.get('bizinfo', { 'bizname': '', 'aboutme': '', 'whytochooseme': '', 'role': '', 'website': '', 'bizstate': '',
                                         'bizcity': '', 'bizzip': '', 'bizcountry': '', 'bizphone': '','bizstate_code':'','bizcity_code':'','bizcountry_code':''})
    
    print(business_info)
    context = {
        'user_name': user_name,
        'user_img':user_img,
        'user_address': user_address,
        'business_info': business_info,
    }
    if session['userType']=="customer":
        breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'Profile','url':f'/Common/profilesettings'},
        ]
        context['breadcrumbs']=breadcrumbs
    if session['userType']=="vendor":
        breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Profile','url':f'/Common/profilesettings'},
        ]
        context['breadcrumbs']=breadcrumbs
    if flask.request.method == 'POST':
         # Get the data from the form       
        new_firstname = flask.request.form.get('firstname')
        new_lastname = flask.request.form.get('lastname')
        new_street = flask.request.form.get('street')
        new_city = flask.request.form.get('cityName')
        new_state = flask.request.form.get('stateName')
        new_zip = flask.request.form.get('zip')
        new_country = flask.request.form.get('countryName')
        country_code=flask.request.form.get('country')
        state_code=flask.request.form.get('state')
        city_code=flask.request.form.get('city')
        new_phone = flask.request.form.get('phone')
        
        bizname = flask.request.form.get('bizname')
        aboutme= request.form.get('bizaboutme')
        whytochooseme= request.form.get('bizwhytochooseme')
        role = flask.request.form.get('role')
        website = flask.request.form.get('bizwebsite')
        bizcountry = flask.request.form.get('bizcountryName')
        bizstate = flask.request.form.get('bizstateName')
        bizcity = flask.request.form.get('bizcityName')
        bizzip = flask.request.form.get('bizzip')
        bizphone = flask.request.form.get('bizphone')
        bizcountry_code=flask.request.form.get('bizcountry')
        bizstate_code=flask.request.form.get('bizstate')
        bizcity_code=flask.request.form.get('bizcity')
        # Update the user's profile in the database
        db1.setProfile(flask.request, email, user_type =session['userType'] , update=True)
        db1.saveDB()
        flash('Profile updated successfully!')

         # Update the context with the new data for rendering the template
        user_name = {'firstname': new_firstname, 'lastname': new_lastname}
        user_address = {
            'street': new_street,
            'city': new_city,
            'state': new_state,
            'zip': new_zip,
            'country': new_country,
            'country_code':country_code,
            'city_code':city_code,
            'state_code':state_code,
            'phone': new_phone,
        }
        business_info = {
            'bizname': bizname,
            'aboutme':aboutme,
            'whytochooseme':whytochooseme,
            'role': role,
            'website': website,
            'bizcountry': bizcountry,
            'bizstate': bizstate,
            'bizcity': bizcity,
            'bizzip': bizzip,
            
            'bizphone': bizphone,
            'bizcountry_code':bizcountry_code,
            'bizstate_code':bizstate_code,
            'bizcity_code':bizcity_code,
        }  

        context['user_name'] = user_name
        context['user_address'] = user_address
        context['user_img']=user_img
        context['business_info'] = business_info
        # db1.setProfile(flask.request)
        return render_template('Common/profilesettings.html',**context)
   
    return render_template('Common/profilesettings.html',**context)

@app.route('/Common/securitysettings', methods=['GET', 'POST'])
@fl.login_required
def securitySettings():
    # Fetch the user's email from the database
    email = fl.current_user.id 

    if request.method == 'POST':
        old_password = request.form.get('pswd')
        new_password = request.form.get('pswd1')
        confirm_password = request.form.get('pswd2')

        # Fetch the user's password from the database
        stored_password = db1.users.get(email, {}).get('pwd', '')

        # Check if the old password matches the stored password
        if bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
            # Check if the new password and confirm password match
            if new_password == confirm_password:
                # Update the password in the database
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
                db1.setPassword(email, hashed_new_password)
                db1.saveDB()
                flash('Password updated successfully!', category='success')
            else:
                flash('New password and confirm password do not match.', category='error')
        else:
            flash('Old password is incorrect.', category='error')
    # Pass the email to the template
    context = {'email': email}
    if session['userType']=="customer":
        breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'Security','url':f'/Common/securitysettings'},
        ]
        context['breadcrumbs']=breadcrumbs
    if session['userType']=="vendor":
        breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Security','url':f'/Common/securitysettings'},
        ]
        context['breadcrumbs']=breadcrumbs
    return render_template('Common/securitysettings.html', **context)

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form.get('email')
        # Check if the email exists in your database
        if email in db1.users:
            # Generate a temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # Update the password in the database (for testing purposes)
            hashed_temp_password = bcrypt.hashpw(temp_password.encode('utf-8'), salt)
            db1.setPassword(email, hashed_temp_password)
            db1.saveDB()
            flash(f'A temporary password has been generated: {temp_password}', category='success')
            return redirect(url_for('login'))  # Redirect to login page after generating temp password
        else:
            flash('Email address not found.', category='error')
    return render_template('Common/forgotpassword.html')

# Your other Flask routes and functions go here

@app.route('/Common/subscriptionsettings')
@fl.login_required
def subscriptionSettings():
    context={}
    if session['userType']=="customer":
        breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'Subscription','url':f'/Common/subscriptionsettings'},
        ]
        context['breadcrumbs']=breadcrumbs
    if session['userType']=="vendor":
        breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Subscription','url':f'/Common/subscriptionsettings'},
        ]
        context['breadcrumbs']=breadcrumbs
    return render_template('Common/subscriptionsettings.html', **context )

'''
----------------------------------------------------------------------------------
Payment 
----------------------------------------------------------------------------------
'''

@app.route('/Common/payment', methods=['GET', 'POST'])
def payment():
    plan=request.args.get('plan')
    price=request.args.get('price')
    context={
        "plan":plan,
        "price":price,
    }
    if plan=="Advertisement":
        print("in advertisement")
        sid=request.args.get('sid')
        sd = DB.getServiceDetails(sid) 
        AdDuration=request.args.get('AdDuration')
        AdvertisementName=request.args.get('AdvertisementName')
        AdvertisementHeading=request.args.get('AdvertisementHeading')
        AdvertisementSubHeading=request.args.get('AdvertisementSubHeading')
        context={
        "plan":plan,
        "price":price,
        "sid":sid,
        "sd":sd,
        "AdDuration":AdDuration,
         "AdvertisementHeading":AdvertisementHeading,
        "AdvertisementSubHeading":AdvertisementSubHeading,
        'AdvertisementName':AdvertisementName,
        }
    if plan=="Service":
        print("in service")
        sid=request.args.get('sid')
        sd = DB.getServiceDetails(sid) 
        rid=request.args.get('rid')
        rd = DB.getRequestDetails(rid)
        context={
        "plan":plan,
        "price":price,
        "sid":sid,
        "sd":sd,
        "rid":rid,
        "rd":rd,
        }
    return render_template('Common/paymentpicker.html',**context)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    total_amount = request.form.get('total')
    order_name = request.form.get('order_name')
    sid=request.form.get('sid')
    AdDuration=request.form.get('AdDuration')
    AdvertisementHeading=request.form.get('AdvertisementHeading')
    AdvertisementSubHeading=request.form.get('AdvertisementSubHeading')
    AdvertisementName=request.form.get('AdvertisementName')
    rid=request.form.get('rid')
    print("AdvertisementName",AdvertisementName)
    if total_amount is None or not total_amount.strip().replace('.', '', 1).isdigit():
        return 'Invalid price value'
    try:
        total_amount_float = float(total_amount)
    except ValueError:
        return 'Invalid price value'

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': order_name,
                        },
                        'unit_amount': int(total_amount_float * 100),  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('thankyou', _external=True) + '?order_name='+order_name+'&total='+total_amount+'&payment_method=stripe'+'&sid='+ sid +'&rid='+ rid +'&AdDuration='+AdDuration+'&AdvertisementName='+AdvertisementName+'&AdvertisementHeading='+AdvertisementHeading+'&AdvertisementSubHeading='+AdvertisementSubHeading+'&date_time=' + datetime.now().isoformat() + 'Z',
            cancel_url=url_for('cancel', _external=True),
        )
    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancle.html')

@app.route('/razorpay')
@fl.login_required
def app_create():
    plan = request.form.get('plan')
    price = request.form.get('price')
    return render_template('Common/paymentpicker.html')

@app.route('/Common/thankyou', endpoint='thankyou')
def thank_you(): 
    order_name = request.args.get('order_name')
    total = request.args.get('total')
    payment_method = request.args.get('payment_method')
    date_time_str = request.args.get('date_time')
    sid=request.args.get('sid')
    rid=request.args.get('rid')
    AdDuration=request.args.get('AdDuration')
    AdvertisementName=request.args.get('AdvertisementName')
    AdvertisementSubHeading=request.args.get('AdvertisementSubHeading')
    AdvertisementHeading=request.args.get('AdvertisementHeading')
    # Retrieve email from session
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))  # Redirect to login if email is not in session

    # Parse ISO 8601 datetime format with milliseconds
    date_obj = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
    date = date_obj.strftime('%Y-%m-%d')
    time = date_obj.strftime('%H:%M:%S')

    DB.addTransaction(email,order_name,total,payment_method,date,time)
    if(order_name=="Advertisement"):
        paymentStatus="successful"
        print("AdvertisementName",AdvertisementName)
        DB.add_advertisement(email,sid,AdDuration,total,AdvertisementName,AdvertisementHeading,AdvertisementSubHeading,paymentStatus)
    if(order_name=="Service"):
        DB.changePaymentStatus(email,sid,rid)

    context={
        "order_name":order_name,
        "total":total,
        "payment_method":payment_method,
        "date_time_str":date_time_str,
        "sid":sid,
        "rid":rid,
        "AdDuration":AdDuration,
    }
    return render_template('Common/thankyou.html', **context)

@app.route('/transaction-history')
def transaction_history():
    email = session.get('email')
    transactions=DB.getAllTransactions(email)
    print(transactions)
    context={}
    if session['userType']=="customer":
        breadcrumbs=[
        {'name':'Home','url':f'/customer_home'},
        {'name':'Transaction History','url':f'/transaction-history'},
        ]
        context['breadcrumbs']=breadcrumbs
    if session['userType']=="vendor":
        breadcrumbs=[
        {'name':'Home','url':f'/vendor_home'},
        {'name':'Transaction History','url':f'/transaction-history'},
        ]
        context['breadcrumbs']=breadcrumbs
    return render_template('Common/transaction_history.html', transactions=transactions,**context)

@app.route('/view_receipt', methods=['GET'])
def view_receipt():
    tran_key=request.args.get('tran_key')
    email = session.get('email')
    receipt_det=DB.getTranDet(tran_key,email)
    
    return render_template('Common/view_receipt.html',receipt_det=receipt_det)

def generate_unique_user_id(email):
    # Generate a unique user ID based on the email address
    # Using MD5 hash for simplicity, you can use a stronger hash function if needed
    return hashlib.md5(email.encode()).hexdigest()

@app.route('/get_user_country', methods=['GET'])
def get_user_country():
    user_ip = request.remote_addr
    country_code = get_country_from_ip(user_ip)
    return jsonify({'country_code': country_code})


#login and account module routes ends

if __name__ == '__main__': 
    # DB.saveDB()  
    DB.loadDB()
    app.debug=True
    app.run()

