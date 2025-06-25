from supabase.client import Client, ClientOptions

def add_role_to_user(supabase: Client, user_id: str, role: str):
    try:
        user = supabase.auth.get_user(user_id)
        if not user or not user.user:
            raise ValueError("User not found")

        # Fetch the role ID from the roles table
        role_resp = supabase.table('roles').select('id').eq('name', role).single().execute()
        if not role_resp.data:
            raise ValueError(f"Role '{role}' not found")
        role_id = role_resp.data['id']
        if not role_id:
            raise ValueError("Role ID not found")
        
        res = supabase.table('user_roles').insert({
            'user_id': user.user.id,
            'role_id': role_id
        }).execute()
        if res.error:
            raise Exception(f"Failed to add role: {res.error.message}")

        return True
    except Exception as e:
        print(f"Error adding role to user: {e}")
        return False