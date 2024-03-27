import re

import GPUtil
import aiofiles
import torch
from fastapi import APIRouter
from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

from routes.similarity import get_cached_embedding, get_cached_tag

router = APIRouter()


# Regular expression for detailed process information related to similarity requests
process_info_regex = re.compile(
    r"INFO:root:Processed similarity request: (?P<sequences>\d+) sequences, Total sequence length: (?P<length>\d+), Response size \(total hits\): (?P<hits>\d+), Execution time: (?P<execution_time>[\d\.]+) seconds"
)


async def parse_log_line(line: str) -> dict | None:
    # Check for process info related to similarity requests
    if process_info_match := process_info_regex.match(line):
        return {"type": "similarity_process_info", **process_info_match.groupdict()}
    # Skip lines that don't match the above criteria
    return None


async def get_last_n_lines(filename: str, n: int) -> list[dict]:
    parsed_lines = []
    async with aiofiles.open(filename, "r", encoding="utf-8") as file:
        async for line in file:
            parsed_line = await parse_log_line(line)
            if parsed_line:  # Only add the line if parse_log_line returns a dict
                parsed_lines.append(parsed_line)
                if len(parsed_lines) > n:  # Keep the buffer size to n
                    parsed_lines.pop(0)

    return parsed_lines


@router.get("/logs/similarity")
async def read_similarity_logs(
    lines: int = Query(
        100,
        alias="lines",
        description="The number of lines to retrieve from the log file related to similarity requests.",
    )
):
    log_entries = await get_last_n_lines("nohup.out", lines)
    return {"logs": log_entries}


@router.get("/logs")
async def read_logs(
    lines: int = Query(100, alias="lines", description="The number of lines to retrieve from the log file.")
):
    log_entries = await get_last_n_lines("nohup.out", lines)
    return {"logs": log_entries}


@router.get("/cache_status")
async def cache_status():
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
                "total_memory": gpu.memoryTotal,
            }
            gpu_info.append(info)

        cleanup_message = "GPU memory cache cleanup not requested."
        # Cleaning PyTorch GPU cache if cleanup flag is True
        if cleanup and torch.cuda.is_available():
            torch.cuda.empty_cache()  # Clears memory cache
            cleanup_message = "PyTorch GPU cache cleaned."

        # Combining both GPU stats and cleanup message in the response
        response = {"gpu_stats": gpu_info, "cleanup_message": cleanup_message}

        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
