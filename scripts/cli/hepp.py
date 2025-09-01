import json, os, time
from pathlib import Path

def emit(obj): print(json.dumps(obj), flush=True)

if __name__ == "__main__":
    emit({"progress": 0.10, "msg": "starting"})
    time.sleep(0.2)
    emit({"progress": 0.50, "msg": "halfway"})

    base = Path(os.environ.get("RESULTS_DIR", "results")).resolve()
    (base / "figures").mkdir(parents=True, exist_ok=True)
    p = base / "figures" / "hello.txt"
    p.write_text("demo artifact\n")

    emit({"artifact": {"kind": "file", "name": p.name, "path": str(p)}})
    emit({"progress": 1.0, "msg": "done"})
