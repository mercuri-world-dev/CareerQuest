import os
from flask import request
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

url = os.environ.get("SUPABASE_URL")

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