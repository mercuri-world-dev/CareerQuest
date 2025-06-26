from supabase.client import Client

from util.db_result import DbResult

def add_role_to_user(supabase: Client, user_id: str, role: str) -> DbResult:
  return DbResult(
    success=False,
    error="not implemented yet"
  )