#!/usr/bin/env python3
"""Compare source identity and rotated geometry, without writing any registry."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
REF = ROOT / 'docs/architecture/continuation-20261022/references'
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash, role
from whole_building_candidates import AIR


def variants(cells):
 result = []
 for r in range(4):
  ps = []
  for x, y, z in cells:
   for _ in range(r): x, z = -z, x
   ps.append((x, y, z))
  mins = [min(p[a] for p in ps) for a in range(3)]
  result.append(frozenset(tuple(p[a] - mins[a] for a in range(3)) for p in ps))
 return result


def find_records(value, index, result):
 if isinstance(value, dict):
  member = value.get('member') or value.get('complete_building_identity') or value.get('source_member')
  v = value.get('verifiable_source', {})
  jar = value.get('source_archive') or value.get('source_jar') or v.get('local_jar')
  if jar and member and isinstance(member, str) and member.endswith('.nbt'):
   key = (jar, member)
   result.setdefault(key, dict(archive=jar, member=member, prior_indices=[]))['prior_indices'].append(index)
  for child in value.values(): find_records(child, index, result)
 elif isinstance(value, list):
  for child in value: find_records(child, index, result)


def load(row):
 with ZipFile(row['archive']) as z: raw = z.read(row['member'])
 d = read(raw); pal = d.get('palette') or d['palettes'][0]
 cells = {tuple(b['pos']): pal[b['state']]['Name'] for b in d['blocks'] if pal[b['state']]['Name'] not in AIR}
 return dict(nbt_sha256=hashlib.sha256(raw).hexdigest(),
  role_sha256=geometry_hash({p: role(n) for p, n in cells.items()}, d['size']),
  occupancy_sha256=geometry_hash({p: 1 for p in cells}, d['size']), variants=variants(cells))


def main():
 indices = [REF / 'full-buildings.json'] + sorted(REF.glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder == OUT: continue
  for name in ('sources.json', 'scope-expansion-sources.json', 'manual-review.json'):
   path = folder / name
   if path.is_file(): indices.append(path)
 historical = {}
 for path in indices: find_records(json.loads(path.read_text()), str(path), historical)
 old = []
 for row in historical.values():
  if not Path(row['archive']).is_file(): raise FileNotFoundError(row['archive'])
  old.append((row, load(row)))
 sources = json.loads((OUT / 'sources.json').read_text())
 current = [(c, load(dict(archive=c['source_archive'], member=c['member']))) for c in sources['candidates']]
 entries = []
 for c, data in current:
  matches = []; near = []
  for h, hd in old:
   same = [key for key in ('nbt_sha256', 'role_sha256', 'occupancy_sha256') if data[key] == hd[key]]
   if c['member'] == h['member']: same.append('member')
   if same: matches.append(dict(member=h['member'], archive=h['archive'], reasons=same))
   a = data['variants'][0]
   best = 0.0
   for b in hd['variants']:
    intersection = len(a & b); score = intersection / (len(a) + len(b) - intersection)
    best = max(best, score)
   near.append(dict(member=h['member'], archive=h['archive'], occupancy_jaccard=round(best, 5)))
  entries.append(dict(id=c['id'], member=c['member'],
   **{k: v for k, v in data.items() if k != 'variants'}, historical_exact_matches=matches,
   nearest_occupancy_only=sorted(near, key=lambda r: -r['occupancy_jaccard'])[:3]))
 pairs = []
 for i, (a, ad) in enumerate(current):
  for b, bd in current[i+1:]:
   if ad['occupancy_sha256'] == bd['occupancy_sha256'] or ad['role_sha256'] == bd['role_sha256']:
    pairs.append([a['id'], b['id']])
 report = dict(historical_indices_checked=[str(p) for p in indices],
  historical_unique_local_archive_member_pairs=len(old), formal_identity_records_checked=148,
  history_units='Local archive/member pairs include held and component studies; not reference-credit totals.',
  nearest_method='Maximum four-rotation occupancy Jaccard with minima aligned; no scale matching. A similarity heuristic, never proof of family novelty.',
  within_batch_exact_duplicate_pairs=pairs, entries=entries, formal_credit_added=0)
 (OUT / 'dedup-evidence.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
 for row in entries:
  print(row['id'], 'exact', len(row['historical_exact_matches']), 'nearest', row['nearest_occupancy_only'][0])
 print('Local archive/member pairs checked:', len(old), '; within-batch exact duplicate pairs:', pairs)


if __name__ == '__main__': main()
