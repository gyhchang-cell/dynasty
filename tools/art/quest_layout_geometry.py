"""Pure geometry of FTB straight dependencies; no native rendering claim."""

def visible_edges(chapter):
    byid = {q['id']: q for q in chapter['quests']}
    return [(byid[d], q) for q in chapter['quests']
            if not q.get('hide_dependency_lines') for d in q['deps']
            if d in byid and not byid[d].get('hide_dependent_lines')]


def penetrates(a, b, q):
    """Segment enters the button's square bounds with a 0.08-unit margin.

    The square bound is conservative for diamond/circle nodes. Endpoints are
    excluded by callers; near misses do not count as actual obscured connections.
    """
    half = q.get('size', 1.) / 2 - .08
    lo, hi = 0., 1.
    for axis in ('x', 'y'):
        delta = b[axis] - a[axis]
        start, end = q[axis] - half, q[axis] + half
        if abs(delta) < 1e-9:
            if not start < a[axis] < end:
                return False
        else:
            t0, t1 = sorted(((start-a[axis])/delta, (end-a[axis])/delta))
            lo, hi = max(lo, t0), min(hi, t1)
            if hi <= lo:
                return False
    return hi > lo and hi > 0 and lo < 1


def crossings(edges):
    def turn(a, b, c):
        return (b['x']-a['x'])*(c['y']-a['y'])-(b['y']-a['y'])*(c['x']-a['x'])
    result = []
    for i, (a, b) in enumerate(edges):
        for c, d in edges[i+1:]:
            if len({a['id'], b['id'], c['id'], d['id']}) < 4:
                continue
            if turn(a,b,c)*turn(a,b,d) < -1e-8 and turn(c,d,a)*turn(c,d,b) < -1e-8:
                result.append([a['id'],b['id'],c['id'],d['id']])
    return result


def audit(chapter):
    edges = visible_edges(chapter)
    hits = []
    for a, b in edges:
        for q in chapter['quests']:
            if q['id'] not in (a['id'], b['id']) and penetrates(a,b,q):
                hits.append({'from':a['id'],'to':b['id'],'through':q['id'],
                             'titles':[a['title'],b['title'],q['title']],
                             'section':b.get('section')})
    return {'chapter':chapter['file'],'quests':len(chapter['quests']),
            'visible_edges':len(edges),'button_penetrations':hits,
            'edge_crossings':crossings(edges)}

