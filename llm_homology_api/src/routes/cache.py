import GPUtil
import torch
from fastapi import APIRouter
from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

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




@router.get("/gpu_stats")
async def gpu_stats(cleanup: bool = Query(default=False, description="Flag to trigger GPU memory cleanup")):
    """Endpoint to provide GPU stats. Optionally cleans GPU memory cache if cleanup flag is set to True."""
    try:
        # Getting GPU stats using GPUtil
        gpus = GPUtil.getGPUs()
        gpu_info = []
        for gpu in gpus:
            info = {
                "id": gpu.id,
                "name": gpu.name,
                "load": gpu.load,
                "temperature": gpu.temperature,
                "free_memory": gpu.memoryFree,
                "used_memory": gpu.memoryUsed,
                "total_memory": gpu.memoryTotal
            }
            gpu_info.append(info)

        cleanup_message = "GPU memory cache cleanup not requested."
        # Cleaning PyTorch GPU cache if cleanup flag is True
        if cleanup and torch.cuda.is_available():
            torch.cuda.empty_cache()  # Clears memory cache
            cleanup_message = "PyTorch GPU cache cleaned."

        # Combining both GPU stats and cleanup message in the response
        response = {
            "gpu_stats": gpu_info,
            "cleanup_message": cleanup_message
        }

        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
