import os
import sys
import json
import subprocess
import requests

SESSION_FILE = "session.json"
FIREBASE_API_KEY = "AIzaSyAW6uLgwztqCbprQ-vAS1jwd3hTczBmWHk"
FIREBASE_PROJECT_ID = "pkm-bonjer"
def get_hwid():
    """Mengambil ID Unik Perangkat (Cross-Platform)"""
    try:
        if sys.platform.startswith('win'):
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True).decode().split()
            return output[1] if len(output) > 1 else "UNKNOWN_WIN"
        elif sys.platform.startswith('darwin'):
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
            output = subprocess.check_output(cmd, shell=True).decode()
            return output.split('"')[-2]
    except Exception:
        return "ERROR_FETCHING_HWID"

def login_with_approval(email, password, hwid):
    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    register_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    
    try:
        auth_resp = requests.post(login_url, json=payload, timeout=5)
        auth_data = auth_resp.json()
        
        if auth_resp.status_code != 200:
            reg_auth_resp = requests.post(register_url, json=payload, timeout=5)
            reg_auth_data = reg_auth_resp.json()
            
            if reg_auth_resp.status_code == 200:
                local_id = reg_auth_data['localId']
                db_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users_device/{local_id}"
                register_payload = {"fields": {"email": {"stringValue": email}, "hwid": {"stringValue": hwid}, "status": {"stringValue": "PENDING"}}}
                requests.patch(db_url, json=register_payload, timeout=5)
                return False, "Akun BARU dibuat! Status: PENDING.", "FIRST_REGISTER", None
            return False, "Login Gagal!", "AUTH_ERROR", None
                
        local_id = auth_data['localId']
        db_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users_device/{local_id}"
        db_resp = requests.get(db_url, timeout=5)
        
        if db_resp.status_code == 200:
            db_data = db_resp.json()
            registered_hwid = db_data.get('fields', {}).get('hwid', {}).get('stringValue', '')
            status = db_data.get('fields', {}).get('status', {}).get('stringValue', 'PENDING')
            
            if registered_hwid.upper() != hwid.upper(): return False, "HWID Mismatch!", "DEVICE_MISMATCH", None
            if status == "APPROVED": return True, "Login Berhasil!", "APPROVED", local_id
            return False, f"Status akun: {status}", status, None
        return False, "Data tidak ditemukan", "NOT_FOUND", None
    except Exception as e:
        return False, str(e), "ERROR", None

def check_auto_login(local_id, hwid):
    try:
        db_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users_device/{local_id}"
        db_resp = requests.get(db_url, timeout=5)
        if db_resp.status_code == 200:
            db_data = db_resp.json()
            registered_hwid = db_data.get('fields', {}).get('hwid', {}).get('stringValue', '')
            status = db_data.get('fields', {}).get('status', {}).get('stringValue', 'PENDING')
            if registered_hwid.upper() == hwid.upper() and status == "APPROVED": return True
        return False
    except: return False