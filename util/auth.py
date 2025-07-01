import json
import os
from flask import session
from dotenv import load_dotenv, find_dotenv
import jwt

from util.supabase.supabase_client import get_supabase

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

def check_has_profile(token):
  res = decode_jwt(token)
  if not res:
    return False
  return res.get('has_profile', False)

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

def refresh_access_token():
  supabase = get_supabase()
  if not supabase:
      return None
  try:
      session = supabase.auth.refresh_session().session
      if not session:
          print("No session object returned from refresh_session.")
          return None
      supabase.auth.set_session(session.access_token, session.refresh_token)
  except Exception as e:
      print(f"Error refreshing access token: {e}")
      return None

def is_authenticated():
  access_token = get_access_token()
  if not access_token:
    return False
  return True