"""Lay out real prerequisite levels while keeping recipe materials together."""


def prerequisite_rows(quests, columns=9):
    existing = [q for q in quests if not q.get('journey_new')]
    newcomers = [q for q in quests if q.get('journey_new')]
    preparations = {q['id']: [] for q in existing}
    for q in newcomers:
        parent=q.get('for_quest') or q.get('journey_site_parent')
        if parent in preparations:
            preparations[parent].append(q)
    units = [preparations[q['id']]+[q] for q in existing]
    consumed = {q['id'] for unit in units for q in unit}
    units.extend([q] for q in newcomers if q['id'] not in consumed)
    owner = {q['id']: i for i, unit in enumerate(units) for q in unit}
    parents = {i: {owner[d] for q in unit for d in q['deps']
                   if d in owner and owner[d] != i} for i, unit in enumerate(units)}
    depth = {}; active = set()
    def level(i):
        if i in depth:
            return depth[i]
        assert i not in active, 'Recipe lane dependency cycle'
        active.add(i)
        depth[i] = max([level(p)+1 for p in parents[i]]+[0])
        active.remove(i)
        return depth[i]
    for i in range(len(units)):
        level(i)
    neighbours = {i: set(parents[i]) for i in parents}
    for i, ps in parents.items():
        for p in ps:
            neighbours[p].add(i)
    remaining = set(parents); components = []
    while remaining:
        todo = [min(remaining)]; component = set()
        while todo:
            i = todo.pop()
            if i in component:
                continue
            component.add(i); todo.extend(neighbours[i]-component)
        remaining -= component; components.append(component)
    rows = []; placed = {}; singles = []
    def append_short(nodes):
        nonlocal singles
        if len(singles)+len(nodes) > columns:
            rows.append(singles); singles = []
        singles.extend(nodes)
    for component in components:
        children = {i: sum(i in parents[n] for n in component) for i in component}
        linear = all(len(parents[i]) <= 1 and children[i] <= 1 for i in component)
        ordered = sorted(component,key=lambda i:(depth[i],i))
        if linear and sum(len(units[i]) for i in component) <= columns:
            # Small independent tutorials read left-to-right as complete lanes.
            append_short([q for i in ordered for q in units[i]])
            continue
        if singles:
            rows.append(singles); singles = []
        # Disconnected families must not sit between a root and its children.
        rows.extend(layered_rows(component, units, parents, depth, columns, placed))
    if singles:
        rows.append(singles)
    return rows


def layered_rows(component, units, parents, depth, columns, placed):
    rows = []
    for rank in sorted({depth[i] for i in component}):
        # Child branches stay near the center of their prerequisite branches.
        current = sorted((i for i in component if depth[i] == rank),
                         key=lambda i: (sum(placed[p] for p in parents[i])/len(parents[i])
                                        if parents[i] else 0., i))
        buffer = []; width = 0
        def flush():
            nonlocal buffer, width
            if not buffer:
                return
            row = [q for i in buffer for q in units[i]]
            rows.append(row)
            offset = -(len(row)-1)/2
            for i in buffer:
                placed[i] = offset+(len(units[i])-1)/2
                offset += len(units[i])
            buffer = []; width = 0
        for i in current:
            assert len(units[i]) <= columns, 'Recipe lane exceeds section width'
            if width+len(units[i]) > columns:
                flush()
            buffer.append(i); width += len(units[i])
        flush()
    return rows
