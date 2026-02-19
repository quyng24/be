import firebase_admin
from firebase_admin import credentials
import os
import json

firebase_json_str = os.getenv("FIREBASE_CONFIG_JSON")

if firebase_json_str:
    firebase_info = json.loads(firebase_json_str)
    cred = credentials.Certificate(firebase_info)
    firebase_admin.initialize_app(cred)
else:
    print("LỖI: Biến môi trường FIREBASE_CONFIG_JSON chưa được thiết lập!")

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_json_str)
        firebase_admin.initialize_app(cred)
