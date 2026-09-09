from client import ImmixMarkRegionGC

def main():
    print("=== Testing Immix Mark-Region Garbage Collector ===")
    gc = ImmixMarkRegionGC()

    gc.allocate("root_node", 120, refs=["child_a"])
    gc.allocate("child_a", 240, refs=[])
    gc.allocate("garbage_obj", 300, refs=[])

    gc.add_root("root_node")
    print("Objects before GC:", list(gc.objects.keys()))

    reclaimed = gc.collect()
    print(f"GC completed. Reclaimed {reclaimed} unreachable object(s).")
    assert "garbage_obj" not in gc.objects
    assert "root_node" in gc.objects and "child_a" in gc.objects
    print("Live objects after GC:", list(gc.objects.keys()))
    print("=== All tests passed successfully! ===")

if __name__ == "__main__":
    main()
