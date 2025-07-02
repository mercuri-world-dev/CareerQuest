import os
from flask import g
from werkzeug.local import LocalProxy
from supabase.client import Client, ClientOptions
from main.flask_storage import FlaskSessionStorage
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")

def get_supabase() -> Client:
    if not url or not key:
        raise ValueError("Supabase URL and Anon Key must be set in environment variables.")
    if "supabase" not in g:
        g.supabase = Client(
            url,
            key,
            options=ClientOptions(
                storage=FlaskSessionStorage(),
                flow_type="pkce",
                auto_refresh_token=True
            ),
        )
    return g.supabase

supabase: Client = LocalProxy(get_supabase)