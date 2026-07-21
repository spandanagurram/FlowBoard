from django.core.cache import cache

def get_cache(key):
    return cache.get(key)

def set_cache(key, value, timeout=None):
    cache.set(key, value, timeout)

def delete_cache(key):
    cache.delete(key)
    
def delete_dashboard_cache(user_id):
    cache.delete(f"dashboard_summary_{user_id}")