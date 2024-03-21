from fastapi import APIRouter
from routes.similarity import get_cached_embedding, get_cached_tag
router = APIRouter()


@router.get("/cache_status")
def cache_status():
    """Endpoint to get status of caches."""
    cache_info = {}
    for cache_func in [get_cached_embedding, get_cached_tag]:
        cache_info[cache_func.__name__] = {
            "hits": cache_func.cache_info().hits,
            "misses": cache_func.cache_info().misses,
            "maxsize": cache_func.cache_info().maxsize,
            "currsize": cache_func.cache_info().currsize,
        }
    return cache_info
