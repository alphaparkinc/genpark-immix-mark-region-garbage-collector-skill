class ImmixMarkRegionGC:
    """
    Immix Garbage Collector: Blocks (4096B) divided into Lines (128B).
    Provides line marking, contiguous line object allocation, root tracing, and sweep.
    """
    BLOCK_SIZE = 4096
    LINE_SIZE = 128
    LINES_PER_BLOCK = BLOCK_SIZE // LINE_SIZE

    def __init__(self):
        self.blocks = []
        self.roots = set()
        self.objects = {} # obj_id -> (block_idx, line_start, line_count, payload, refs)

    def allocate(self, obj_id, payload_size, refs=None):
        lines_needed = max(1, (payload_size + self.LINE_SIZE - 1) // self.LINE_SIZE)
        if lines_needed > self.LINES_PER_BLOCK:
            raise ValueError("Large object exceeds block size")

        for b_idx, block in enumerate(self.blocks):
            start = block.find_free_lines(lines_needed)
            if start is not None:
                block.occupy(start, lines_needed)
                self.objects[obj_id] = (b_idx, start, lines_needed, payload_size, set(refs or []))
                return obj_id

        new_block = ImmixBlock(len(self.blocks), self.LINES_PER_BLOCK)
        start = new_block.find_free_lines(lines_needed)
        new_block.occupy(start, lines_needed)
        self.blocks.append(new_block)
        b_idx = len(self.blocks) - 1
        self.objects[obj_id] = (b_idx, start, lines_needed, payload_size, set(refs or []))
        return obj_id

    def add_root(self, obj_id):
        self.roots.add(obj_id)

    def remove_root(self, obj_id):
        self.roots.discard(obj_id)

    def collect(self):
        reachable = set()
        queue = list(self.roots)
        while queue:
            curr = queue.pop()
            if curr in self.objects and curr not in reachable:
                reachable.add(curr)
                queue.extend(self.objects[curr][4])

        for block in self.blocks:
            block.reset_marks()

        for obj_id in reachable:
            b_idx, start, count, _, _ = self.objects[obj_id]
            self.blocks[b_idx].mark_lines(start, count)

        dead = [oid for oid in self.objects if oid not in reachable]
        for oid in dead:
            b_idx, start, count, _, _ = self.objects[oid]
            self.blocks[b_idx].unmark_lines(start, count)
            del self.objects[oid]

        return len(dead)

class ImmixBlock:
    def __init__(self, block_id, num_lines):
        self.block_id = block_id
        self.num_lines = num_lines
        self.line_occupied = [False] * num_lines

    def find_free_lines(self, count):
        run = 0
        for i, occ in enumerate(self.line_occupied):
            if not occ:
                run += 1
                if run == count:
                    return i - count + 1
            else:
                run = 0
        return None

    def occupy(self, start, count):
        for i in range(start, start + count):
            self.line_occupied[i] = True

    def reset_marks(self):
        pass

    def mark_lines(self, start, count):
        for i in range(start, start + count):
            self.line_occupied[i] = True

    def unmark_lines(self, start, count):
        for i in range(start, start + count):
            self.line_occupied[i] = False
