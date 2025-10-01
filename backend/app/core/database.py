from supabase import create_client, Client
from app.core.config import settings

# Supabase Clientのシングルトン
_supabase_client: Client = None


def get_supabase_client() -> Client:
    """Supabase Clientを取得（シングルトン）"""
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _supabase_client


def get_db() -> Client:
    """FastAPI Dependency用のSupabase Client取得関数"""
    return get_supabase_client()