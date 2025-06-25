from main.supabase_client import get_supabase


_role_name_to_id = None
_permission_name_to_id = None

def get_role_name_to_id():
    global _role_name_to_id
    if _role_name_to_id is None:
        supabase = get_supabase()
        resp = supabase.table('roles').select('id, name').execute()
        _role_name_to_id = {r['name']: r['id'] for r in (resp.data or [])}
    return _role_name_to_id

def get_permission_name_to_id():
    global _permission_name_to_id
    if _permission_name_to_id is None:
        supabase = get_supabase()
        resp = supabase.table('permissions').select('id, name').execute()
        _permission_name_to_id = {p['name']: p['id'] for p in (resp.data or [])}
    return _permission_name_to_id