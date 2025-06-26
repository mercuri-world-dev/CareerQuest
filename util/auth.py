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

def decode_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, audience="authenticated", algorithms=[JWT_ALGORITHM])
        print(f"Decoded JWT payload: {payload}")  # Debugging line
        return payload
    except jwt.ExpiredSignatureError:
        print(e) # TODO: Handle expired token 
        return None
    except jwt.InvalidTokenError as e:
        print('Invalid token: ', e) # TODO: Handle invalid token
        return None

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
  
def fetch_user_role(token):
  res = decode_jwt(token)
  if not res:
    return None
  return res.get('user_role')

# def create_jwt_token(user_id, permissions, roles):
#     payload = { 
#         "sub": user_id,
#         "permissions": permissions,
#         "roles": roles,
#         "exp": datetime.now(tz=timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
#     }
#     token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     if isinstance(token, bytes):
#         token = token.decode('utf-8')
#     return token

# def verify_jwt_token(token):
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None