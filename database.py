'''
MongoDB-backed database for FlaskQIConnectApp.
Replaces the pickle/lzma file-based storage so data persists on Render.

Collections in MongoDB:
  - users           : { _id: email, pwd, type, firstname, lastname, address, bizinfo, ... }
  - requests        : { _id: requestID, from, i_need, ... }
  - services        : { _id: serviceID, from, serviceName, ... }
  - messages        : { _id: messageID, from, to, message, ... }
  - orders          : { _id: email+"_"+orderID, email, rid, sid, ... }
  - projects        : { _id: email+"_"+projectID, email, rid, sid, ... }
  - contracts       : { _id: contractID, when, price }
  - advertisements  : { _id: email+"_"+sid, email, sid, ... }
  - notifications   : { _id: notificationID, vendorMail, ... }
  - transactions    : { _id: transactionID, email, order_name, ... }
  - contacts        : { _id: contactID, mail, name, ... }
  - meta            : { _id: "generateId", number, alpha }
'''

import base64
import os
import ssl
import uuid
import smtplib
from datetime import date, datetime, timedelta

import bcrypt
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from flask import Flask

# ---------------------------------------------------------------------------
# MongoDB connection  (SSL fix for Render / Atlas compatibility)
# ---------------------------------------------------------------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/qiconnect")
_client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=20000,
    socketTimeoutMS=20000,
)
_db = _client.get_default_database() if "/" in MONGO_URI.split("@")[-1] else _client["qiconnect"]

col_users        = _db["users"]
col_requests     = _db["requests"]
col_services     = _db["services"]
col_messages     = _db["messages"]
col_orders       = _db["orders"]
col_projects     = _db["projects"]
col_contracts    = _db["contracts"]
col_advertisements = _db["advertisements"]
col_notifications  = _db["notifications"]
col_transactions   = _db["transactions"]
col_contacts     = _db["contacts"]
col_meta         = _db["meta"]

# ---------------------------------------------------------------------------
# Bcrypt salt
# ---------------------------------------------------------------------------
salt = bcrypt.gensalt(rounds=10)

# ---------------------------------------------------------------------------
# Upload folder paths (relative, Linux-compatible for Render)
# ---------------------------------------------------------------------------
UPLOAD_FOLDER            = os.path.join(os.getcwd(), 'attachment_uploaded')
UPLOAD_FILES_CUSTOMERS   = os.path.join(os.getcwd(), 'upload_customers_files')
UPLOAD_FILES_VENDORS     = os.path.join(os.getcwd(), 'upload_vendors_files')
UPLOAD_FOLDER_PROFILE    = os.path.join(os.getcwd(), 'uploads')

# Ensure upload dirs exist at startup
for _d in [UPLOAD_FOLDER, UPLOAD_FILES_CUSTOMERS, UPLOAD_FILES_VENDORS, UPLOAD_FOLDER_PROFILE]:
    os.makedirs(_d, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER']          = UPLOAD_FOLDER
app.config['UPLOAD_FILES_CUSTOMERS'] = UPLOAD_FILES_CUSTOMERS
app.config['UPLOAD_FILES_VENDORS']   = UPLOAD_FILES_VENDORS

# ---------------------------------------------------------------------------
# In-memory dict shim so app.py can do  DB.users[email]  etc.
# We keep this in sync by always reading from Mongo.
# ---------------------------------------------------------------------------
class _UsersProxy(dict):
    """Thin proxy that reads/writes through to MongoDB."""
    def __getitem__(self, email):
        doc = col_users.find_one({"_id": email})
        if doc is None:
            raise KeyError(email)
        doc.pop("_id", None)
        return doc

    def __setitem__(self, email, value):
        value["_id"] = email
        col_users.replace_one({"_id": email}, value, upsert=True)

    def __contains__(self, email):
        return col_users.count_documents({"_id": email}, limit=1) > 0

    def get(self, email, default=None):
        try:
            return self[email]
        except KeyError:
            return default

    def items(self):
        return [(d["_id"], {k: v for k, v in d.items() if k != "_id"})
                for d in col_users.find()]

users = _UsersProxy()

# Kept for backward compat with code that accesses DB.ServiceFormDict / DB.RequestFormDict directly
class _DictProxy:
    """Proxy that wraps a MongoDB collection as a dict-like object."""
    def __init__(self, collection):
        self._col = collection

    def __getitem__(self, key):
        doc = self._col.find_one({"_id": key})
        if doc is None:
            raise KeyError(key)
        doc.pop("_id", None)
        return doc

    def __setitem__(self, key, value):
        value["_id"] = key
        self._col.replace_one({"_id": key}, value, upsert=True)

    def __delitem__(self, key):
        self._col.delete_one({"_id": key})

    def __contains__(self, key):
        return self._col.count_documents({"_id": key}, limit=1) > 0

    def keys(self):
        return [d["_id"] for d in self._col.find({}, {"_id": 1})]

    def items(self):
        return [(d["_id"], {k: v for k, v in d.items() if k != "_id"})
                for d in self._col.find()]

    def values(self):
        return [{k: v for k, v in d.items() if k != "_id"} for d in self._col.find()]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def __iter__(self):
        return iter(self.keys())

    def pop(self, key, *args):
        doc = self._col.find_one_and_delete({"_id": key})
        if doc is None:
            if args:
                return args[0]
            raise KeyError(key)
        doc.pop("_id", None)
        return doc

RequestFormDict      = _DictProxy(col_requests)
ServiceFormDict      = _DictProxy(col_services)
MessagesDict         = _DictProxy(col_messages)
VendorContractDetDict = _DictProxy(col_contracts)
OrderByCustomer      = _DictProxy(col_orders)
ProjectReceivedToVendor = _DictProxy(col_projects)
AdvertisementDict    = _AdvertisementProxy = None   # replaced below
notificationDict     = _DictProxy(col_notifications)
transactionDict      = _DictProxy(col_transactions)
contactDict          = _DictProxy(col_contacts)

# ---------------------------------------------------------------------------
# Advertisement is nested: { email: { sid: {...} } }
# We flatten to _id = email + "___" + sid in MongoDB.
# ---------------------------------------------------------------------------
class _AdvertisementDictProxy:
    """
    Presents the same nested-dict interface as the old AdvertisementDict:
        AdvertisementDict[email][sid] = {...}
    but stores flat docs in MongoDB with _id = email+"___"+sid.
    """
    _SEP = "___"

    def _flat_id(self, email, sid):
        return f"{email}{self._SEP}{sid}"

    def _split_id(self, flat_id):
        parts = flat_id.split(self._SEP, 1)
        return (parts[0], parts[1]) if len(parts) == 2 else (flat_id, "")

    # ---- outer dict interface ----
    def __contains__(self, email):
        return col_advertisements.count_documents({"email": email}, limit=1) > 0

    def keys(self):
        return list({d["email"] for d in col_advertisements.find({}, {"email": 1})})

    def items(self):
        result = {}
        for doc in col_advertisements.find():
            email = doc["email"]
            sid   = doc["sid"]
            data  = {k: v for k, v in doc.items() if k not in ("_id", "email", "sid")}
            result.setdefault(email, {})[sid] = data
        return result.items()

    def __iter__(self):
        return iter(self.keys())

    # ---- nested access: AdvertisementDict[email] returns inner proxy ----
    def __getitem__(self, email):
        return _InnerAdProxy(email, col_advertisements, self._SEP)

    def __setitem__(self, email, inner_dict):
        # Called as AdvertisementDict[email] = {}  (initialise)
        pass  # inner dict is already empty; items added via inner proxy

    def __delitem__(self, email):
        col_advertisements.delete_many({"email": email})

    def get(self, email, default=None):
        if email in self:
            return self[email]
        return default


class _InnerAdProxy:
    def __init__(self, email, collection, sep):
        self._email = email
        self._col   = collection
        self._sep   = sep

    def _flat_id(self, sid):
        return f"{self._email}{self._sep}{sid}"

    def __getitem__(self, sid):
        doc = self._col.find_one({"_id": self._flat_id(sid)})
        if doc is None:
            raise KeyError(sid)
        return {k: v for k, v in doc.items() if k not in ("_id", "email", "sid")}

    def __setitem__(self, sid, value):
        doc = dict(value)
        doc["_id"]   = self._flat_id(sid)
        doc["email"] = self._email
        doc["sid"]   = sid
        self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    def __delitem__(self, sid):
        self._col.delete_one({"_id": self._flat_id(sid)})

    def __contains__(self, sid):
        return self._col.count_documents({"_id": self._flat_id(sid)}, limit=1) > 0

    def keys(self):
        return [d["sid"] for d in self._col.find({"email": self._email}, {"sid": 1})]

    def items(self):
        return [(d["sid"], {k: v for k, v in d.items() if k not in ("_id", "email", "sid")})
                for d in self._col.find({"email": self._email})]

    def __iter__(self):
        return iter(self.keys())

    def values(self):
        return [{k: v for k, v in d.items() if k not in ("_id", "email", "sid")}
                for d in self._col.find({"email": self._email})]


AdvertisementDict = _AdvertisementDictProxy()

# ---------------------------------------------------------------------------
# Notification nested proxy { vendorMail: { notifID: {...} } }
# ---------------------------------------------------------------------------
class _NotificationDictProxy:
    _SEP = "___"

    def _flat_id(self, email, nid):
        return f"{email}{self._SEP}{nid}"

    def __contains__(self, email):
        return col_notifications.count_documents({"email": email}, limit=1) > 0

    def keys(self):
        return list({d["email"] for d in col_notifications.find({}, {"email": 1})})

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, email):
        return _InnerNotifProxy(email, col_notifications, self._SEP)

    def __setitem__(self, email, val):
        pass

    def items(self):
        result = {}
        for doc in col_notifications.find():
            email = doc["email"]
            nid   = doc["nid"]
            data  = {k: v for k, v in doc.items() if k not in ("_id", "email", "nid")}
            result.setdefault(email, {})[nid] = data
        return result.items()

    def get(self, email, default=None):
        return self[email] if email in self else default


class _InnerNotifProxy:
    def __init__(self, email, collection, sep):
        self._email = email
        self._col   = collection
        self._sep   = sep

    def _flat_id(self, nid):
        return f"{self._email}{self._sep}{nid}"

    def __getitem__(self, nid):
        doc = self._col.find_one({"_id": self._flat_id(nid)})
        if doc is None:
            raise KeyError(nid)
        return {k: v for k, v in doc.items() if k not in ("_id", "email", "nid")}

    def __setitem__(self, nid, value):
        doc = dict(value)
        doc["_id"]   = self._flat_id(nid)
        doc["email"] = self._email
        doc["nid"]   = nid
        self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    def __delitem__(self, nid):
        self._col.delete_one({"_id": self._flat_id(nid)})

    def keys(self):
        return [d["nid"] for d in self._col.find({"email": self._email}, {"nid": 1})]

    def items(self):
        return [(d["nid"], {k: v for k, v in d.items() if k not in ("_id", "email", "nid")})
                for d in self._col.find({"email": self._email})]

    def __iter__(self):
        return iter(self.keys())

    def pop(self, nid, *args):
        doc = self._col.find_one_and_delete({"_id": self._flat_id(nid)})
        if doc is None:
            if args:
                return args[0]
            raise KeyError(nid)
        return {k: v for k, v in doc.items() if k not in ("_id", "email", "nid")}


notificationDict = _NotificationDictProxy()

# ---------------------------------------------------------------------------
# ID generator  (persisted in MongoDB "meta" collection)
# ---------------------------------------------------------------------------
class getID:
    def __init__(self):
        doc = col_meta.find_one({"_id": "generateId"})
        if doc:
            self.number = doc["number"]
            self.alpha  = doc["alpha"]
        else:
            self.number = 1
            self.alpha  = 'a'

    def _save(self):
        col_meta.replace_one(
            {"_id": "generateId"},
            {"_id": "generateId", "number": self.number, "alpha": self.alpha},
            upsert=True
        )

    def generate_id(self):
        self.number += 1
        if self.number == 300:
            self.alpha  = chr(ord(self.alpha) + 1)
            self.number = 0
        self._save()
        d = datetime.now().strftime('%Y-%m-%d')
        return f"{d}-{self.alpha}{self.number}"


generateIdObj = getID()


def generate_id():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    unique_id = uuid.uuid4()
    return f"{timestamp}-{unique_id}"


def generateID():
    timestamp = datetime.now().strftime('%Y-%m-%d')
    unique_id = uuid.uuid4()
    return f"{timestamp}-{unique_id}"


# ---------------------------------------------------------------------------
# saveDB / loadDB  (no-ops now — Mongo is always live)
# ---------------------------------------------------------------------------
def saveDB():
    pass   # All writes go directly to MongoDB via the proxies


def loadDB():
    pass   # MongoDB is always available; nothing to load


# ---------------------------------------------------------------------------
# Contact Us
# ---------------------------------------------------------------------------
def add_contact_us_form(name, mail, phone, subject, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    doc = {
        "_id":   generate_id(),
        "email": mail,
        "name":  name,
        "mail":  mail,
        "phone": phone,
        "subject": subject,
        "message": message,
        "timestamp": timestamp,
    }
    col_contacts.insert_one(doc)


# ---------------------------------------------------------------------------
# Orders  (customer)
# ---------------------------------------------------------------------------
def add_order(email, rid, sid, price):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    _id = f"{email}___{sid}_{rid}"
    doc = {
        "_id":          _id,
        "email":        email,
        "rid":          rid,
        "sid":          sid,
        "order_date":   timestamp,
        "price":        price,
        "payment_status": "Not Paid",
    }
    col_orders.replace_one({"_id": _id}, doc, upsert=True)


def add_project(email, rid, sid, price):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    _id = f"{email}___{sid}_{rid}"
    doc = {
        "_id":          _id,
        "email":        email,
        "rid":          rid,
        "sid":          sid,
        "project_date": timestamp,
        "price":        price,
        "payment_status": "Not Paid",
    }
    col_projects.replace_one({"_id": _id}, doc, upsert=True)


def _order_id(email, sid, rid):
    return f"{email}___{sid}_{rid}"


def getOrderDet(email, id):
    # id is in format sid_rid (as stored in OrderByCustomer keys in app.py)
    full_id = f"{email}___{id}"
    doc = col_orders.find_one({"_id": full_id})
    if doc:
        return {k: v for k, v in doc.items() if k not in ("_id", "email")}
    return None


def getProjectDet(email, id):
    full_id = f"{email}___{id}"
    doc = col_projects.find_one({"_id": full_id})
    if doc:
        return {k: v for k, v in doc.items() if k not in ("_id", "email")}
    return None


def remove_order(email, request_id, service_id):
    _id = f"{email}___{service_id}_{request_id}"
    col_orders.delete_one({"_id": _id})


def remove_project(email, request_id, service_id):
    _id = f"{email}___{service_id}_{request_id}"
    col_projects.delete_one({"_id": _id})


def changePaymentStatus(email, sid, rid):
    _id = f"{email}___{sid}_{rid}"
    col_orders.update_one({"_id": _id}, {"$set": {"payment_status": "Paid"}})
    vendor_email = getServiceMail(sid)
    _vid = f"{vendor_email}___{sid}_{rid}"
    col_projects.update_one({"_id": _vid}, {"$set": {"payment_status": "Paid"}})


def myOrders(email):
    docs = list(col_orders.find({"email": email}))
    if not docs:
        return "No Orders"
    result = {}
    for doc in docs:
        key = doc["_id"].replace(f"{email}___", "", 1)
        result[key] = {k: v for k, v in doc.items() if k not in ("_id", "email")}
    return result


def myProjects(email):
    docs = list(col_projects.find({"email": email}))
    if not docs:
        return "No Projects"
    result = {}
    for doc in docs:
        key = doc["_id"].replace(f"{email}___", "", 1)
        result[key] = {k: v for k, v in doc.items() if k not in ("_id", "email")}
    return result


# ---------------------------------------------------------------------------
# Requests  (customer)
# ---------------------------------------------------------------------------
def add_request(email, i_need, PicsFiles, objective, specifications, where, when,
                tentativeWhen, additionalInfo, AdditionalFiles, current_status,
                closeRequest, selectVendorServiceID, audio, adv_status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    rid = generateIdObj.generate_id()
    doc = {
        "_id":          rid,
        "from":         email,
        "i_need":       i_need,
        "PicsFiles":    PicsFiles,
        "objective":    objective,
        "specifications": specifications,
        "where":        where,
        "when":         when,
        "tentativeWhen": tentativeWhen,
        "additionalInfo": additionalInfo,
        "AdditionalFiles": AdditionalFiles,
        "timestamp":    timestamp,
        "current_status": current_status,
        "closeRequest": closeRequest,
        "selectVendorServiceID": selectVendorServiceID,
        "audio":        audio,
        "adv_status":   adv_status,
        "combined_data_customer": (i_need + " " + objective + " " + specifications +
                                   " " + where + " " + when + " " + additionalInfo),
    }
    col_requests.insert_one(doc)


def deleteRequest(rid):
    col_requests.delete_one({"_id": rid})


def updateRequest(rid, i_need, objective, specifications, additionalInfo, where, when,
                  tentativeWhen, addPicsfiles, updateAdditionalFiles, current_status,
                  closeRequest, selectVendorServiceID, audio, adv_status):
    col_requests.update_one({"_id": rid}, {"$set": {
        "i_need":        i_need,
        "objective":     objective,
        "specifications": specifications,
        "where":         where,
        "when":          when,
        "tentativeWhen": tentativeWhen,
        "PicsFiles":     addPicsfiles,
        "AdditionalFiles": updateAdditionalFiles,
        "additionalInfo": additionalInfo,
        "current_status": current_status,
        "closeRequest":  closeRequest,
        "selectVendorServiceID": selectVendorServiceID,
        "audio":         audio,
        "adv_status":    adv_status,
        "combined_data_customer": (i_need + " " + objective + " " + specifications +
                                   " " + where + " " + when + " " + additionalInfo),
    }})


def getRequestDetails(request_id):
    doc = col_requests.find_one({"_id": request_id})
    if doc:
        doc["_id_key"] = doc.pop("_id")
        return doc
    return None


def myRequests(email):
    result = {}
    for doc in col_requests.find({"from": email}):
        rid = doc.pop("_id")
        result[rid] = doc
    return result


def responses(rid):
    result = {}
    for doc in col_messages.find({"request_id": rid}):
        sid = doc.get("service_id")
        if sid and col_services.count_documents({"_id": sid}, limit=1):
            vendor_email = col_services.find_one({"_id": sid}, {"from": 1})["from"]
            result[sid] = {
                "id":         vendor_email,
                "vendorName": getUsername(vendor_email),
            }
    return result


# ---------------------------------------------------------------------------
# Services / Products  (vendor)
# ---------------------------------------------------------------------------
def add_registerService_form(email, serviceName, specificFeature, benefits, bestFor,
                              relatedProduct, where, additionalProductRelatedFiles,
                              ProductPics, myServicesInfo, selectedPrImg,
                              allocatedReqIDs, current_status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    sid = generateIdObj.generate_id()
    doc = {
        "_id":          sid,
        "from":         email,
        "serviceName":  serviceName,
        "specificFeature": specificFeature,
        "benefits":     benefits,
        "bestFor":      bestFor,
        "where":        where,
        "relatedProduct": relatedProduct,
        "additionalProductRelatedFiles": additionalProductRelatedFiles,
        "ProductPics":  ProductPics,
        "selectedPrImg": selectedPrImg,
        "myServicesInfo": myServicesInfo,
        "current_status": current_status,
        "timestamp":    timestamp,
        "allocatedReqIDs": allocatedReqIDs,
        "combined_data_vendor": (serviceName + " " + specificFeature + " " + bestFor +
                                 " " + where + " " + relatedProduct + " " + myServicesInfo),
    }
    col_services.insert_one(doc)


def deleteProduct(sid):
    col_services.delete_one({"_id": sid})


def updateProduct(sid, serviceName, specificFeature, benefits, bestFor, where, when,
                  relatedProduct, additionalProductRelatedFiles, ProductPics,
                  myServicesInfo, selectedPrImg, current_status):
    col_services.update_one({"_id": sid}, {"$set": {
        "serviceName":   serviceName,
        "specificFeature": specificFeature,
        "benefits":      benefits,
        "bestFor":       bestFor,
        "where":         where,
        "when":          when,
        "relatedProduct": relatedProduct,
        "additionalProductRelatedFiles": additionalProductRelatedFiles,
        "ProductPics":   ProductPics,
        "selectedPrImg": selectedPrImg,
        "myServicesInfo": myServicesInfo,
        "current_status": current_status,
        "combined_data_vendor": (serviceName + " " + specificFeature + " " + bestFor +
                                 " " + where + " " + relatedProduct + " " + myServicesInfo),
    }})


def getServiceDetails(service_id):
    doc = col_services.find_one({"_id": service_id})
    if doc:
        doc["_id_key"] = doc.pop("_id")
        return doc
    return None


def getServiceDetailsCombinedData(service_id):
    doc = col_services.find_one({"_id": service_id}, {"combined_data_vendor": 1})
    return doc["combined_data_vendor"] if doc else ""


def getServiceMail(sid):
    doc = col_services.find_one({"_id": sid}, {"from": 1})
    return doc["from"] if doc else None


def myProducts(email):
    result = {}
    for doc in col_services.find({"from": email}):
        sid = doc.pop("_id")
        result[sid] = doc
    return result


def CustomerResponses(sid):
    result = {}
    for doc in col_messages.find({"service_id": sid}):
        rid = doc.get("request_id")
        if rid and col_requests.count_documents({"_id": rid}, limit=1):
            customer_email = col_requests.find_one({"_id": rid}, {"from": 1})["from"]
            result[rid] = {
                "id":           customer_email,
                "customerName": users[customer_email].get("name", getUsername(customer_email)),
            }
    return result


# ---------------------------------------------------------------------------
# Vendor contract
# ---------------------------------------------------------------------------
def addVendorContractDet(id, when, price):
    col_contracts.replace_one(
        {"_id": id},
        {"_id": id, "when": when, "price": price},
        upsert=True
    )


def getVendorContractDet(id):
    doc = col_contracts.find_one({"_id": id})
    if doc:
        return {k: v for k, v in doc.items() if k != "_id"}
    return None


def getVendorContractPrice(id):
    doc = col_contracts.find_one({"_id": id}, {"price": 1})
    return doc["price"] if doc else "-"


def getVendorContractLocation(id):
    doc = col_contracts.find_one({"_id": id}, {"when": 1})
    return doc["when"] if doc else "-"


# ---------------------------------------------------------------------------
# Matching (ML)
# ---------------------------------------------------------------------------
def get_distance(text1, text2):
    if not text1.strip() or not text2.strip():
        return 0
    vectorizer = CountVectorizer().fit([text1, text2])
    v1 = vectorizer.transform([text1]).toarray().flatten()
    v2 = vectorizer.transform([text2]).toarray().flatten()
    return float(cosine_similarity([v1, v2])[0, 1])


def matching_customers(sid):
    doc = col_services.find_one({"_id": sid}, {"combined_data_vendor": 1})
    if not doc:
        return {}
    vendor_data = doc["combined_data_vendor"]
    result = {}
    for req in col_requests.find({}, {"_id": 1, "combined_data_customer": 1}):
        dist = get_distance(req.get("combined_data_customer", ""), vendor_data)
        if dist != 0:
            result[req["_id"]] = dist
    return result


def matching_vendors(rid):
    doc = col_requests.find_one({"_id": rid}, {"combined_data_customer": 1})
    if not doc:
        return {}
    customer_data = doc["combined_data_customer"]
    result = {}
    for svc in col_services.find({}, {"_id": 1, "combined_data_vendor": 1}):
        dist = get_distance(customer_data, svc.get("combined_data_vendor", ""))
        if dist != 0:
            result[svc["_id"]] = dist
    return result


def all_request_combined_data(email):
    all_data = ""
    for doc in col_requests.find({"from": email}, {"combined_data_customer": 1}):
        all_data += " " + doc.get("combined_data_customer", "").strip()
    return all_data


def all_advertisement_combined_data(email):
    matching = []
    for ad_doc in col_advertisements.find():
        sid = ad_doc.get("sid")
        if not sid:
            continue
        service_data = getServiceDetailsCombinedData(sid)
        req_data = all_request_combined_data(email)
        dist = get_distance(service_data, req_data)
        if dist > 0:
            matching.append(sid)
    return {email: matching}


def getAllAdvertisement(email):
    result = all_advertisement_combined_data(email)
    if not result or result == {}:
        return "No Advertisement"
    return result


# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------
def addMessage(To, From, message, sendfile_name, request_id, service_id,
               audioFile_name, videoFile_name):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    doc = {
        "_id":            generate_id(),
        "from":           From,
        "to":             To,
        "message":        message,
        "file":           sendfile_name,
        "audioFile_name": audioFile_name,
        "videoFile_name": videoFile_name,
        "timestamp":      timestamp,
        "request_id":     request_id,
        "service_id":     service_id,
    }
    col_messages.insert_one(doc)


def getMessages(request_id, service_id):
    query = {
        "$or": [
            {"request_id": request_id, "service_id": service_id},
            {"request_id": service_id,  "service_id": request_id},
        ]
    }
    return [{k: v for k, v in doc.items() if k != "_id"}
            for doc in col_messages.find(query)]


def lastMessage(request_id, service_id):
    msgs = getMessages(request_id, service_id)
    if not msgs:
        return "No Message"
    last = msgs[-1]
    return (last.get("message", "") + " " + last.get("file", "") + " " +
            last.get("audioFile_name", "") + " " + last.get("videoFile_name", ""))


# ---------------------------------------------------------------------------
# Advertisements
# ---------------------------------------------------------------------------
def add_advertisement(email, sid, AdDuration, price, AdvertisementName,
                      AdvertisementHeading, AdvertisementSubHeading, paymentStatus):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    expiry_date = (date.today() + timedelta(int(AdDuration))).strftime("%Y-%m-%d")
    flat_id = f"{email}___{sid}"
    doc = {
        "_id":                   flat_id,
        "email":                 email,
        "sid":                   sid,
        "AdDuration":            int(AdDuration),
        "price":                 price,
        "AdvertisementName":     AdvertisementName,
        "AdvertisementHeading":  AdvertisementHeading,
        "AdvertisementSubHeading": AdvertisementSubHeading,
        "paymentStatus":         paymentStatus,
        "advertisementStatus":   "active",
        "ad_date":               timestamp,
        "expiry_date":           expiry_date,
    }
    col_advertisements.replace_one({"_id": flat_id}, doc, upsert=True)


def AdPlaced(email):
    docs = list(col_advertisements.find({"email": email}))
    if not docs:
        return "No Projects"
    return {doc["sid"]: {k: v for k, v in doc.items() if k not in ("_id", "email")}
            for doc in docs}


def allAdPlaced():
    return [doc["sid"] for doc in col_advertisements.find({}, {"sid": 1})]


def getAdvDetByID(sid):
    doc = col_advertisements.find_one({"sid": sid})
    if doc:
        return {k: v for k, v in doc.items() if k not in ("_id", "email")}
    return None


def getAdvertisementName(service_id):
    doc = col_advertisements.find_one({"sid": service_id}, {"AdvertisementName": 1})
    return doc["AdvertisementName"] if doc else None


def delete_advertisement(email, sid):
    flat_id = f"{email}___{sid}"
    col_advertisements.delete_one({"_id": flat_id})
    return "Adv deleted"


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
def add_nofification(vendorMail, notificationStr):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    nid = generateID()
    flat_id = f"{vendorMail}___{nid}"
    doc = {
        "_id":            flat_id,
        "email":          vendorMail,
        "nid":            nid,
        "notify_date":    timestamp,
        "notificationStr": notificationStr,
    }
    col_notifications.insert_one(doc)


def getAllNotifications(email):
    docs = list(col_notifications.find({"email": email}))
    if not docs:
        return "No Notification"
    return {doc["nid"]: {"notify_date": doc["notify_date"],
                         "notificationStr": doc["notificationStr"]}
            for doc in docs}


def popNotification(notificationID, email):
    flat_id = f"{email}___{notificationID}"
    col_notifications.delete_one({"_id": flat_id})


# ---------------------------------------------------------------------------
# Profile helpers
# ---------------------------------------------------------------------------
def getCustomerProfile(email):
    return users[email]


def getVendorProfile(email):
    return users[email]


def getProfileDetails(email):
    return users[email]


def getUsername(email):
    user = col_users.find_one({"_id": email}, {"firstname": 1})
    return user.get("firstname", "Not Known") if user else "Not Known"


def getUserAddress(email):
    user = col_users.find_one({"_id": email}, {"address": 1})
    return user.get("address", "Not Known") if user else "Not Known"


def countEle(d):
    return len(d)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def hashit(pwd):
    b = pwd.encode('utf-8')
    return bcrypt.hashpw(b, salt)


def userExists(email):
    return col_users.count_documents({"_id": email}, limit=1) > 0


def validateUser(request):
    email = request.form.get('email')
    if not userExists(email):
        return False, None
    doc = col_users.find_one({"_id": email}, {"pwd": 1, "type": 1})
    pwd = request.form.get('pwd', '').encode('utf-8')
    if bcrypt.checkpw(pwd, doc['pwd']):
        return True, doc['type']
    return False, None


def getUserType(email):
    doc = col_users.find_one({"_id": email}, {"type": 1})
    return doc["type"] if doc else None


def getName(email):
    doc = col_users.find_one({"_id": email}, {"firstname": 1, "lastname": 1})
    if not doc:
        return ""
    return f"{doc.get('firstname', '')} {doc.get('lastname', '')}"


def setUser(email, pwd):
    hashed = hashit(pwd)
    col_users.update_one({"_id": email}, {"$set": {"pwd": hashed}}, upsert=True)


def setUserType(email, utype):
    col_users.update_one({"_id": email}, {"$set": {"type": utype}}, upsert=True)


def getUserByEmail(email):
    return users.get(email)


def createUser(email, pwd, utype):
    if userExists(email):
        return False
    setUser(email, pwd)
    setUserType(email, utype)
    return True


def setPassword(email, new_password):
    col_users.update_one({"_id": email}, {"$set": {"pwd": new_password}})


def setProfileImg(user_email, filename):
    col_users.update_one({"_id": user_email}, {"$set": {"profileImg": filename}})


def getUserProfileImg(user_email):
    doc = col_users.find_one({"_id": user_email}, {"profileImg": 1})
    return doc.get("profileImg", "default_user_img.jpg") if doc else "default_user_img.jpg"


def setName(email, request):
    fn = request.form.get('firstname')
    ln = request.form.get('lastname')
    update = {}
    if fn is not None:
        update["firstname"] = fn
    if ln is not None:
        update["lastname"] = ln
    if update:
        col_users.update_one({"_id": email}, {"$set": update}, upsert=True)


country_currencies = {
    'India': 'INR',
    'United States': 'USD',
    'United Kingdom': 'GBP',
    'Canada': 'CAD',
    'Australia': 'AUD',
}


def setAddress(email, request):
    col_users.update_one({"_id": email}, {"$set": {"address": {
        "street":     request.form.get('street'),
        "city":       request.form.get('cityName'),
        "state":      request.form.get('stateName'),
        "state_code": request.form.get('state'),
        "city_code":  request.form.get('city'),
        "zip":        request.form.get('zip'),
        "country":    request.form.get('countryName'),
        "country_code": request.form.get('country'),
        "phone":      request.form.get('phone'),
    }}}, upsert=True)


def setCurrency(email, country_name):
    currency_code = country_currencies.get(country_name)
    col_users.update_one({"_id": email},
                         {"$set": {"currency": {"country": country_name, "code": currency_code}}},
                         upsert=True)


def setBizInfo(email, request):
    col_users.update_one({"_id": email}, {"$set": {"bizinfo": {
        "bizname":          request.form.get('bizname'),
        "aboutme":          request.form.get('bizaboutme'),
        "whytochooseme":    request.form.get('bizwhytochooseme'),
        "role":             request.form.get('role'),
        "website":          request.form.get('bizwebsite'),
        "bizstate":         request.form.get('bizstateName'),
        "bizcity":          request.form.get('bizcityName'),
        "bizstate_code":    request.form.get('bizstate'),
        "bizcity_code":     request.form.get('bizcity'),
        "bizzip":           request.form.get('bizzip'),
        "bizcountry_code":  request.form.get('bizcountry'),
        "bizcountry":       request.form.get('bizcountryName'),
        "bizphone":         request.form.get('bizphone'),
    }}}, upsert=True)


def setBizTrue(email):
    col_users.update_one({"_id": email}, {"$set": {"isbiz": "on"}}, upsert=True)


def setEmptyRequestsList(email):
    col_users.update_one({"_id": email}, {"$set": {"requests": []}}, upsert=True)


def setEmptyProductsList(email):
    col_users.update_one({"_id": email}, {"$set": {"products": []}}, upsert=True)


def saveDatabase():
    pass   # no-op with MongoDB


def setProfile(request, email, user_type=None, update=False):
    setName(email, request)
    setAddress(email, request)
    if user_type == 'vendor':
        setBizInfo(email, request)
    setUserType(email, user_type)

    if not update:
        t = getUserType(email)
        setUserType(email, t)
        setEmptyRequestsList(email)
        setEmptyProductsList(email)
        if user_type == 'vendor':
            setBizTrue(email)


def updateProfileInDatabase(email, user_type, request):
    update = {
        "firstname": request.form.get('firstname'),
        "lastname":  request.form.get('lastname'),
        "address": {
            "street":     request.form.get('street'),
            "city":       request.form.get('cityName'),
            "state":      request.form.get('stateName'),
            "zip":        request.form.get('zip'),
            "country":    request.form.get('countryName'),
            "country_code": request.form.get('country'),
            "state_code": request.form.get('state'),
            "city_code":  request.form.get('city'),
            "phone":      request.form.get('phone'),
        }
    }
    if user_type == 'vendor':
        update["bizinfo"] = {
            "bizname":         request.form.get('bizname'),
            "aboutme":         request.form.get('bizaboutme'),
            "whytochooseme":   request.form.get('bizwhytochooseme'),
            "role":            request.form.get('role'),
            "website":         request.form.get('bizwebsite'),
            "bizstate":        request.form.get('bizstateName'),
            "bizcity":         request.form.get('bizcityName'),
            "bizzip":          request.form.get('bizzip'),
            "bizcountry":      request.form.get('bizcountryName'),
            "bizphone":        request.form.get('bizphone'),
            "bizstate_code":   request.form.get('bizstate'),
            "bizcity_code":    request.form.get('bizcity'),
            "bizcountry_code": request.form.get('bizcountry'),
        }
    col_users.update_one({"_id": email}, {"$set": update}, upsert=True)


def getProfile(email):
    return users.get(email)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------
def addTransaction(email, order_name, total, payment_method, date_str, time_str):
    tid = str(uuid.uuid4())
    doc = {
        "_id":            f"{email}___{tid}",
        "email":          email,
        "tid":            tid,
        "order_name":     order_name,
        "total":          total,
        "payment_method": payment_method,
        "date":           date_str,
        "time":           time_str,
    }
    col_transactions.insert_one(doc)


def getAllTransactions(email):
    docs = list(col_transactions.find({"email": email}))
    if not docs:
        return "No Transactions"
    return {doc["tid"]: {k: v for k, v in doc.items() if k not in ("_id", "email", "tid")}
            for doc in docs}


def getTranDet(tran_key, email):
    doc = col_transactions.find_one({"email": email, "tid": tran_key})
    if doc:
        return {k: v for k, v in doc.items() if k not in ("_id", "email", "tid")}
    return None


# ---------------------------------------------------------------------------
# Email (unchanged stub)
# ---------------------------------------------------------------------------
def send_email(email, temp_password):
    smtp_server   = 'smtp.example.com'
    smtp_port     = 587
    sender_email  = 'your_email@example.com'
    sender_password = 'your_email_password'
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    subject = 'Password Reset Request'
    body    = f'Your temporary password is: {temp_password}'
    message = f'Subject: {subject}\n\n{body}'
    server.sendmail(sender_email, email, message)
    server.quit()
