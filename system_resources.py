import psutil
import torch

def check_system_resources():
    cpu_count = psutil.cpu_count(logical=False)
    cpu_percent = psutil.cpu_percent(interval=0.2)

    gpu_available = torch.cuda.is_available()
    gpu_mem_free = None

    if gpu_available:
        free, total = torch.cuda.mem_get_info()
        gpu_mem_free = free // (1024 ** 2)  # MB

    return {
        "cpu_count": cpu_count,
        "cpu_percent": cpu_percent,
        "gpu_available": gpu_available,
        "gpu_mem_free_mb": gpu_mem_free
    }
