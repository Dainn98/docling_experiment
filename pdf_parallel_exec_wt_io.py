import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from system_resources import check_system_resources
from worker import convert_to_markdown

BASE_OUTPUT_DIR = "output/docling"

def create_storage():
    uid = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(BASE_OUTPUT_DIR, uid)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir, uid

def init_storage(run_dir: str, sources: list[str]):
    output_path = os.path.join(run_dir, "results.json")
    data = {
        "meta": {
            "total": len(sources),
            "start_time": datetime.now().isoformat()
        },
        "documents": []
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return output_path

def append_result(output_json: str, record: dict):
    with open(output_json, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["documents"].append(record)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

def convert_list(sources: list[str], batch_size: int = 4):

    run_dir, uid = create_storage()
    output_json = init_storage(run_dir, sources)

    print(f"Output folder: {run_dir}")

    resources = check_system_resources()
    cpu_count = resources["cpu_count"]
    gpu_available = resources["gpu_available"]

    max_workers = min(cpu_count, batch_size)

    print(f"Starting conversion with {max_workers} workers")
    print(f"GPU available: {gpu_available}")

    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(convert_to_markdown, src, gpu_available): src
            for src in sources
        }

        for idx, future in enumerate(as_completed(futures), 1):
            src = futures[future]
            try:
                content = future.result()
                record = {
                    "source": src,
                    "status": "success",
                    "content": content
                }
                results.append(result)
                print(f"[{idx}/{len(sources)}] Done: {src}")
            except Exception as e:
                record = {
                    "source": src,
                    "status": "error",
                    "error": str(e)
                }
                print(f"Error processing {src}: {e}")

            append_result(output_json, record)

            # resource check mỗi 3 file
            if idx % 3 == 0:
                res = check_system_resources()
                if res["cpu_percent"] > 90:
                    print("⚠ CPU HIGH USAGE detected")

                if res["gpu_available"] and res["gpu_mem_free_mb"] < 2048:
                    print("⚠ GPU memory low → future jobs still on CPU")

    return results
