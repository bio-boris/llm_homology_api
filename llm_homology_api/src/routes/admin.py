from typing import Union

import GPUtil
import aiofiles
import torch
from fastapi import APIRouter
from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse
import re
from routes.similarity import get_cached_embedding, get_cached_tag

router = APIRouter()

# Regular expressions to match different log line formats
process_info_regex = re.compile(
    r"INFO:root:Processed similarity request: (?P<sequences>\d+) sequences, Total sequence length: (?P<length>\d+), Response size \(total hits\): (?P<hits>\d+), Execution time: (?P<execution_time>[\d\.]+) seconds"
)
http_request_regex = re.compile(
    r"INFO: +(?P<ip>[\d\.]+:\d+) - \"(?P<method>\w+) (?P<endpoint>.+) HTTP/1.\d\" (?P<status_code>\d+) (?P<status_message>\w+)"
)
progress_regex = re.compile(
    r"(?P<progress>\d+)%\|[\w\s]+\| (?P<completed>\d+)/(?P<total>\d+) \[(?P<elapsed_time>.+)\]"
)


async def parse_log_line(line: str) -> Union[Dict[str, str], None]:
    if process_info_match := process_info_regex.match(line):
        return {"type": "process_info", **process_info_match.groupdict()}
    elif http_request_match := http_request_regex.match(line):
        return {"type": "http_request", **http_request_match.groupdict()}
    elif progress_match := progress_regex.match(line):
        return {"type": "progress", **progress_match.groupdict()}
    return None  # Return None for lines that do not match any pattern


async def get_last_n_lines(filename: str, n: int) -> list[dict[str, str]]:
    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        lines = await file.readlines()

    # Parse lines and filter out None values for lines that didn't match any pattern
    parsed_lines = [await parse_log_line(line) for line in lines]
    parsed_lines = [line for line in parsed_lines if line is not None]
    return parsed_lines[-n:] if len(parsed_lines) >= n else parsed_lines


@router.get("/logs")
async def read_logs(lines: int = Query(100, alias="lines", description="The number of lines to retrieve from the log file.")):
    log_entries = await get_last_n_lines('nohup.out', lines)
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
