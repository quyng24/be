import firebase_admin
from firebase_admin import credentials
import os
import json

def init_firebase():
    firebase_json_str = os.getenv("FIREBASE_CONFIG_JSON")

    if not firebase_json_str:
        raise Exception("FIREBASE_CONFIG_JSON chưa được thiết lập")

    firebase_dict = json.loads(firebase_json_str)

    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)