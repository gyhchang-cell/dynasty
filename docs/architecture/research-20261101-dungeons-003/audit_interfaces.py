#!/usr/bin/env python3
"""Read outgoing pool evidence without assembling, running, or crediting it."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent

def main():
 s=json.loads((OUT/'sources.json').read_text()); rows=[]
 for c in s['candidates']:
  outgoing=[]
  with ZipFile(c['source_archive']) as z:
   for pool in sorted({p['data']['pool'] for p in c['sockets']}):
    namespace,name=pool.split(':',1)
    member=f'data/{namespace}/worldgen/template_pool/{name}.json'
    row=dict(pool=pool,socket_positions=[p['position'] for p in c['sockets'] if p['data']['pool']==pool],member=member)
    if member in z.namelist():
     raw=z.read(member); data=json.loads(raw)
     row.update(status='FOUND_LOCAL',sha256=hashlib.sha256(raw).hexdigest(),data=data)
     components=[]
     for item in data['elements']:
      element=item['element']; loc=element.get('location')
      if loc:
       ns,rest=loc.split(':',1); target=f'data/{ns}/structures/{rest}.nbt'
       components.append(dict(member=target,projection=element.get('projection'),weight=item['weight'],
        exists_in_archive=target in z.namelist(),
        sha256=hashlib.sha256(z.read(target)).hexdigest() if target in z.namelist() else None,
        studied_or_credited_as_complete_building=False))
     row['component_identities_only']=components
    else: row.update(status='NOT_IN_THIS_ARCHIVE',automatic_credit=0)
    outgoing.append(row)
  rows.append(dict(id=c['id'],outgoing_pools=outgoing))
 report=dict(entries=rows,formal_credit_added=0,assembled=False,network_requests=0,
  limits='One-level pool definition and component identity audit only. Does not simulate jigsaw matching, recursive expansion, terrain processors, assembly termination, or gameplay.',
  distinction='sources.json pool_references identifies incoming pools selecting the candidate; this file records actual outgoing socket pools.',
  quarry='Four stoneworks sockets select among eleven component templates. The stoneworks JSON name differs from its path identifier and fallback refers to the same path pool; no runtime conclusion or complete-factory credit.')
 (OUT/'interface-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Read outgoing interfaces for 12 templates; no assembly or credit.')

if __name__=='__main__': main()
