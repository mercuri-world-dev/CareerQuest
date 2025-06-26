import json
import os
from flask import session
from supabase.client import Client
from dotenv import load_dotenv, find_dotenv
import jwt

load_dotenv(find_dotenv())

url = os.environ.get("SUPABASE_URL")
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 1

def decode_jwt(token):
  try:
    payload = jwt.decode(token, JWT_SECRET, audience="authenticated", algorithms=[JWT_ALGORITHM])
    return payload
  except jwt.ExpiredSignatureError:
    return None
  except jwt.InvalidTokenError as e:
    return None
  
def fetch_user_role(token):
  res = decode_jwt(token)
  if not res:
    return None
  return res.get('user_role')

def get_access_token():
  supabase_token = session.get('supabase.auth.token')
  if not supabase_token:
      return None
  if isinstance(supabase_token, str):
      try:
          supabase_token_json = json.loads(supabase_token)
      except json.JSONDecodeError:
          return None
  return supabase_token_json.get('access_token')

def get_current_user_id(supabase: Client):
  user = supabase.auth.get_user()
  if user and user.user and user.user.id:
    return user.user.id
  return None

def is_authenticated():
  access_token = get_access_token()
  if not access_token:
    return False
  return True

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