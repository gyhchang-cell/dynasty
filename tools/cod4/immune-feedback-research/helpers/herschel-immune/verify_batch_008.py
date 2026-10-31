"""Independent receipt/source/range checker. Integrity does not grant research credit."""
from pathlib import Path
import json,hashlib,re,importlib.util
ROOT=Path(__file__).resolve().parents[5]
DOC=ROOT/'docs/cod4/audit-20261022/immune-feedback-research/helpers/herschel-immune'
TOOLS=ROOT/'tools/cod4/immune-feedback-research/helpers/herschel-immune'
MASTER=ROOT/'docs/cod4/audit-20261022/immune-feedback-research'
sha=lambda x:hashlib.sha256(x).hexdigest()
spec=importlib.util.spec_from_file_location('reader',ROOT/'tools/cod4/immune-feedback-research/helpers/halley-immune/inspect_methods.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
batch=json.loads((DOC/'batch-008.json').read_text());manifest=json.loads((DOC/'source-manifest-008.json').read_text());sources={}
errors=[];tree_verified=0;inventory_verified=0;methodrefs=0;resources=0
for src in manifest['sources']:
 p=ROOT/src['local'];data=p.read_bytes();assert sha(data)==src['sha256'],p
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==src['computed_git_blob_sha1']
 localrepo=TOOLS/'sources-batch008'/src['source_key'].split('/')[0] if 'source_key' in src else TOOLS/'sources-batch008'/src['repo'].replace('/','__')
 metadata=json.loads((localrepo/'source.json').read_text());assert metadata.get('commit',metadata.get('sha'))==src['commit']
 if 'Git tree' in src['proof']:
  tree=json.loads((localrepo/'tree.json').read_text());assert tree['sha']==src['commit'];assert next(x['sha'] for x in tree['tree'] if x['path']==src['path'])==blob;tree_verified+=1
 else:
  assert next(x['sha256'] for x in metadata['files'] if x['path']==src['path'])==sha(data);inventory_verified+=1
 key=src['repo'].replace('/','__')+'/'+src['path'];sources[key]=src
refs=[x for row in batch['rows'] for x in row['source_refs']]+[x for row in batch['support_for_prior_batches'] for x in row['source_refs']]
for ref in refs:
 src=sources[ref['source_key']];data=(ROOT/src['local']).read_bytes();lines=data.decode().splitlines(keepends=True);a,b=ref['lines'];assert 1<=a<=b<=len(lines)
 excerpt=''.join(lines[a-1:b]);assert excerpt==ref['excerpt'];assert sha(excerpt.encode())==ref['excerpt_sha256'];assert sha(re.sub(r'\s+','',excerpt).encode())==ref['normalized_excerpt_sha256'];assert sha(data)==ref['file_sha256'];assert '/blob/'+src['commit']+'/' in ref['url']
 if ref.get('unit')=='complete_support_resource':resources+=1
 else:assert reader.end_method(lines,a)==b,(src['path'],a,b);methodrefs+=1
for row in batch['rows']:
 focus=row.get('decision_focus')
 if focus:
  ref=row['source_refs'][0];a,b=ref['lines'];c,d=focus['lines'];assert a<=c<=d<=b
  ls=ref['excerpt'].splitlines(keepends=True);assert sha(''.join(ls[c-a:d-a+1]).encode())==focus['excerpt_sha256']
ids=[x['id'] for x in batch['rows']];keys=[x['semantic_dedup_key'] for x in batch['rows']];assert len(ids)==len(set(ids))==batch['reviewed_units'];assert len(keys)==len(set(keys));assert all(x['research_credit']==x['suggested_credit']==0 for x in batch['rows'])
masterbytes=(MASTER/'reviewed.json').read_bytes();master=json.loads(masterbytes);overlaps=[]
for row in batch['rows']:
 ref=row['source_refs'][0];src=sources[ref['source_key']]
 for entry in master:
  for old in entry.get('source_refs',[]):
   if entry['repo']==src['repo'] and entry['commit']==src['commit'] and old.get('source_path')==src['path']:
    a,b=old['lines'];c,d=ref['lines']
    if max(a,c)<=min(b,d):overlaps.append({'helper':row['id'],'master':entry['id'],'master_range':old['lines'],'helper_range':ref['lines'],'review_required':True,'explanation':row['deduplication']})
report={'status':'PASS','batch_sha256':sha((DOC/'batch-008.json').read_bytes()),'master_snapshot_count':len(master),'master_snapshot_sha256':sha(masterbytes),'source_files':len(sources),'git_tree_blob_verified_files':tree_verified,'archive_inventory_sha256_verified_files':inventory_verified,'complete_method_references_including_support':methodrefs,'complete_support_resource_references':resources,'unique_primary_methods':len(set(x['source_refs'][0]['normalized_excerpt_sha256'] for x in batch['rows'])),'master_primary_range_overlaps':overlaps,'errors':errors,'research_credit':0,'suggested_credit':0,'limit':'Integrity is not semantic credit. Prior-batch supplements never add credit; overlapping prior event/template strategies require primary semantic review.'}
(DOC/'integrity-008.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
