import os
from flask import request
import requests
from dotenv import load_dotenv, find_dotenv
import jwt
from datetime import datetime, timedelta, timezone
from main.supabase_client import get_supabase

load_dotenv(find_dotenv())

url = os.environ.get("SUPABASE_URL")
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 1

def get_supabase_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        print(f"JWT decode error: {e}")
        return None

def fetch_user_roles(user_id):
    supabase = get_supabase()
    # Get roles for user
    roles_resp = supabase.table('user_roles').select('role_id').eq('user_id', user_id).execute()
    if not roles_resp.data:
        return []
    return [r['role_id'] for r in roles_resp.data]

def fetch_permissions(user_roles):
    supabase = get_supabase()
    if not user_roles:
        return []
    perms_resp = supabase.table('role_permissions').select('permission_id').in_('role_id', user_roles).execute()
    permissions = [p['permission_id'] for p in perms_resp.data] if perms_resp.data else []
    return permissions

def create_jwt_token(user_id, permissions, roles):
    payload = {
        "sub": user_id,
        "permissions": permissions,
        "roles": roles,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None