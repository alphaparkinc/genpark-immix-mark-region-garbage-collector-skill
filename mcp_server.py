import sys
import json
from client import ImmixMarkRegionGC

gc = ImmixMarkRegionGC()

def handle_call(name, arguments):
    if name == "allocate":
        oid = arguments["id"]
        size = arguments.get("size", 64)
        refs = arguments.get("refs", [])
        res = gc.allocate(oid, size, refs)
        return {"id": res, "active_objects": len(gc.objects)}
    elif name == "add_root":
        gc.add_root(arguments["id"])
        return {"roots": list(gc.roots)}
    elif name == "collect":
        reclaimed = gc.collect()
        return {"reclaimed_count": reclaimed, "live_count": len(gc.objects)}
    return {"error": f"Unknown tool: {name}"}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_call(req.get("name"), req.get("arguments", {}))
            print(json.dumps({"id": req.get("id"), "result": res}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
