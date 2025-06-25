from supabase.client import Client

from util.db_result import DbResult

def add_role_to_user(supabase: Client, user_id: str, role: str) -> DbResult:
    try:
        role_resp = supabase.table('roles').select('id').eq('name', role).single().execute()
        if not role_resp.data:
            raise ValueError(f"Role '{role}' not found")
        role_id = role_resp.data['id']
        if not role_id:
            raise ValueError("Role ID not found")
        
        res = supabase.table('user_roles').insert({
            'user_id': user_id,
            'role_id': role_id
        }).execute()
        
        return DbResult(
            success=True,
            data={"user_id": user_id, "role_id": role_id}
        )
    except Exception as e:
        return DbResult(
            success=False,
            error=str(e)
        )
    
def has_role(supabase: Client, user_id: str, role: str) -> bool:
    try:
        # Fetch the role ID from the roles table
        role_resp = supabase.table('roles').select('id').eq('name', role).single().execute()
        if not role_resp.data:
            return False
        role_id = role_resp.data['id']
        
        # Check if the user has the specified role
        user_role_resp = supabase.table('user_roles').select('*').eq('user_id', user_id).eq('role_id', role_id).single().execute()
        return user_role_resp.data is not None
    except Exception as e:
        print(f"Error checking role: {e}")
        return False