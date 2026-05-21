import requests
import json
res = requests.post("http://127.0.0.1:8080/api/solve", json={"test": "Puzzle_01_7x7_Tree", "algo": "step2"})
data = res.json()
if "trace_history" in data:
    print("Trace History length:", len(data["trace_history"]))
    print("Sample:", data["trace_history"][-1] if data["trace_history"] else "[]")
else:
    print("No trace history")
