"""Bounded read-only support search; no game, Java, extraction or credit."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
assert not (HERE/'RECEIPT.json').exists()
inventory=ROOT/'docs/architecture/research-20261101-dungeons-024/fixed-source-screen.json'
raw=inventory.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='ad75a4b8b8a0a21d60df21849f0654c5f29b21b157656df007087857fbd1d94a'
archives=json.loads(raw)['archives']
needle=b'swamp_big_house_1'
pillar=b'trek:feature/block_column/oak_log'
resource='data/trek/worldgen/template_pool/feature/block_column/oak_log.json'
results=[]
hits=[]
for index,entry in enumerate(archives):
    p=Path(entry['path'])
    rec=dict(path=str(p),expected_sha256=entry['sha256'],status='NOT_SCANNED')
    try:
        before=p.stat()
        h=hashlib.sha256()
        with p.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
        rec['actual_sha256']=h.hexdigest()
        if h.hexdigest()!=entry['sha256']:
            rec['status']='CHANGED_ARCHIVE_EXCLUDED'
        else:
            count=0
            with ZipFile(p) as z:
                for member in z.namelist():
                    if not member.startswith('data/') or not member.endswith(('.json','.mcfunction')):continue
                    data=z.read(member)
                    count+=1
                    if needle in data or pillar in data or member==resource:
                        hits.append(dict(archive=str(p),archive_sha256=h.hexdigest(),member=member,
                            sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),
                            exact_body_name=needle in data,pillar_reference=pillar in data,
                            exact_pillar_definition=member==resource,
                            text=data.decode('utf-8')))
            after=p.stat()
            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
                raise RuntimeError('Archive changed during scan')
            rec.update(status='PINNED_ARCHIVE_DATA_TEXT_SCANNED',resources_scanned=count,bytes=after.st_size)
    except Exception as exc:
        rec.update(status='ERROR_NOT_COVERED',error=type(exc).__name__+': '+str(exc))
    results.append(rec)
    if (index+1)%25==0:print(json.dumps(dict(scanned_archives=index+1,hit_records=len(hits))),flush=True)

def write(name,value):(HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
write('fixed-support-scan.json',dict(inventory_path=str(inventory),inventory_sha256=hashlib.sha256(raw).hexdigest(),
    archives=results,hits=hits,scope='Only pinned292 local archives data/*.json and mcfunction resources; no nested archives/classes/world packs.',
    automatic_reference_credit=0,production_changes=0,java_executed=False))
write('active-checkpoint.json',dict(batch=317,status='SUPPORT_SCAN_CAPTURED_NOT_YET_SEMANTICALLY_REVIEWED',
    archived_results=len(results),hits=len(hits),formal_credit_added=0,gate_met=False,
    next='Read actual hit resources and classify references vs definitions; no automatic closure of316 parent/support.'))
print(json.dumps(dict(done=True,archives=len(results),verified=sum(x['status']=='PINNED_ARCHIVE_DATA_TEXT_SCANNED'for x in results),
    resources=sum(x.get('resources_scanned',0)for x in results),hits=len(hits))),flush=True)
