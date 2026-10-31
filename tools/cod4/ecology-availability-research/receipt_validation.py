"""Fail-closed receipt aggregation. Reads cached source as bytes, never runs it.
Reviewer authorization is the user's local role assignment plus exact namespace/label,
not a cryptographic identity proof. Receipt byte hashes bind the inspected files.
"""
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from evidence import ROOT, DOCS, TOOLS, sha

AUTHORIZED = {
 'coordinator': {
  'labels': {'coordinator independent semantic read',
             'coordinator independent full-chain semantic read',
             'coordinator independent complete-chain read',
             'coordinator independent full-chain read'},
  'decisions': {'ACCEPT_ONE_RELATED_IMPLEMENTATION'},
  'checks': ('source_sha256_match','git_blob_match','fixed_revision_match','excerpt_exact')},
 'carson': {
  'labels': {'Carson independent source/semantic review',
             'Carson independent full-chain text and semantic review',
             'Carson independent complete source-chain review'},
  'decisions': {'ACCEPT_ONE_RELATED_IMPLEMENTATION_WITH_EXPLICIT_LIMITS'},
  'checks': ('source_byte_SHA_match','blob_header_SHA1_matches_tree_entry',
             'cached_revision_metadata_match','excerpt_exact')},
}
ALL_ACCEPT_DECISIONS=set().union(*(r['decisions'] for r in AUTHORIZED.values()))
HEX40=re.compile(r'[0-9a-f]{40}\Z')
HEX64=re.compile(r'[0-9a-f]{64}\Z')
NAME=re.compile(r'(coordinator|carson)-EA([0-9]{4})\.json\Z')

class InvalidReceipt(ValueError): pass

def require(condition, reason):
    if not condition: raise InvalidReceipt(reason)

def local_path(value, base):
    require(isinstance(value,str) and value!='', 'missing local path')
    p=(ROOT/value).resolve()
    require(p.is_relative_to(base.resolve()), 'path outside authorized evidence root')
    require(not Path(value).is_absolute() and '..' not in Path(value).parts, 'noncanonical local path')
    return p

class Snapshot:
    def __init__(self, overrides=None):
        self.bytes={}
        self.jsons={}
        self.overrides=overrides or {}  # in-memory negative audit only; never writes source
        self.source_cache={}
    def read(self,p):
        p=Path(p).resolve()
        if p not in self.bytes:
            self.bytes[p]=self.overrides[p] if p in self.overrides else p.read_bytes()
        return self.bytes[p]
    def json(self,p):
        p=Path(p).resolve()
        if p not in self.jsons: self.jsons[p]=json.loads(self.read(p))
        return self.jsons[p]
    def stable(self):
        require(not self.overrides, 'synthetic snapshots cannot publish actual acceptance')
        for p,raw in self.bytes.items():
            require(sha(p.read_bytes())==sha(raw), 'evidence changed during aggregation: '+str(p.relative_to(ROOT)))

def validate_source(e, snap):
    """Recompute source/header/tree/revision and exact excerpt; no trusted PASS flags."""
    for field in ('repo','revision','path','source_local','source_sha256','git_blob_sha1',
                  'tree_metadata','source_metadata','excerpt','excerpt_sha256','url'):
        require(isinstance(e.get(field),str), 'missing evidence field '+field)
    require(HEX40.fullmatch(e['revision']) is not None, 'revision is not fixed40')
    repo=e['repo']; require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo) is not None, 'bad repo identity')
    base=TOOLS/'sources'/repo.replace('/','__')
    expected_source=base/e['path']
    src=local_path(e['source_local'],base)
    require(src==expected_source.resolve(), 'source_local vs repo/path mismatch')
    tree_path=local_path(e['tree_metadata'],base)
    meta_path=local_path(e['source_metadata'],base)
    require(tree_path==base.resolve()/'tree.json' and meta_path==base.resolve()/'source.json', 'metadata path mismatch')
    key=(str(src),e['source_sha256'],e['revision'],e['git_blob_sha1'],str(tree_path),str(meta_path))
    if key not in snap.source_cache:
        raw=snap.read(src); meta=snap.json(meta_path); tree=snap.json(tree_path)
        require(meta.get('repo')==repo,'source metadata repo mismatch')
        revisions=[meta[k] for k in ('sha','commit') if k in meta]
        require(bool(revisions) and all(v==e['revision'] for v in revisions),'metadata revision mismatch')
        require(tree.get('sha')==e['revision'] and tree.get('truncated') is False,'tree revision/truncation mismatch')
        require(sha(raw)==e['source_sha256'],'actual source SHA256 mismatch')
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob==e['git_blob_sha1'],'actual Git blob SHA1 mismatch')
        entries=[x for x in tree['tree'] if x['path']==e['path']]
        require(len(entries)==1 and entries[0]['type']=='blob' and entries[0]['sha']==blob,'fixed tree blob mismatch')
        snap.source_cache[key]=raw.decode('utf-8').splitlines()
    lines=snap.source_cache[key]
    start,end=e.get('line'),e.get('end_line')
    require(type(start) is int and type(end) is int and 1<=start<=end<=len(lines),'invalid source range')
    excerpt='\n'.join(lines[start-1:end])
    require(excerpt==e['excerpt'] and sha(excerpt.encode())==e['excerpt_sha256'],'actual excerpt mismatch')
    url=f"https://github.com/{repo}/blob/{e['revision']}/{e['path']}#L{start}-L{end}"
    require(e['url']==url,'immutable source URL mismatch')
    return {'source_local':e['source_local'],'line':start,'end_line':end,
            'source_sha256':e['source_sha256'],'git_blob_sha1':e['git_blob_sha1'],
            'revision':e['revision'],'excerpt_sha256':e['excerpt_sha256'],
            'source_metadata_sha256':sha(snap.read(meta_path)),
            'tree_metadata_sha256':sha(snap.read(tree_path))}

def extra_support(review,record,snap):
    extra=review.get('additional_source_check')
    if extra is None: return None
    require(isinstance(extra,dict),'invalid additional source support')
    raw=snap.read(local_path(extra['path'],TOOLS/'sources'))
    require(raw.decode()==extra['full_file_excerpt'],'extra full-file excerpt mismatch')
    e=dict(record['chain'][0])
    prefix=f"tools/cod4/ecology-availability-research/sources/{record['repo'].replace('/','__')}/"
    require(extra['path'].startswith(prefix),'extra repo path mismatch')
    e.update(path=extra['path'][len(prefix):],source_local=extra['path'],
             source_sha256=extra['source_sha256'],git_blob_sha1=extra['git_blob_sha1'],
             revision=extra['revision'],line=1,end_line=len(raw.decode().splitlines()),
             excerpt='\n'.join(raw.decode().splitlines()))
    e['excerpt_sha256']=sha(e['excerpt'].encode())
    e['url']=f"https://github.com/{e['repo']}/blob/{e['revision']}/{e['path']}#L1-L{e['end_line']}"
    require(extra.get('tree_and_cached_metadata_match') is True,'extra support reviewer mismatch')
    return validate_source(e,snap)

def validate_receipt(path, raw, batches_by_id, snap):
    path=Path(path)
    require(path.resolve()==(DOCS/'independent-reviews'/path.name).resolve() and
            path.resolve().parent==(DOCS/'independent-reviews').resolve(),
            'receipt outside authorized review directory')
    match=NAME.fullmatch(path.name)
    require(match is not None,'unauthorized receipt filename/role namespace')
    role,num=match.groups(); policy=AUTHORIZED[role]
    d=json.loads(raw)
    require(isinstance(d,dict),'receipt must be a JSON object')
    require(d.get('reviewer') in policy['labels'],'reviewer not in user-authorized exact-label whitelist')
    identifier='EA-'+num
    require(d.get('id')==identifier,'receipt filename/id mismatch')
    require(identifier in batches_by_id,'unknown/candidate identifier')
    batch_path,r=batches_by_id[identifier]
    require(r.get('status')=='reviewed_proposed' and r.get('proposed_credit')==1,'record not an eligible reviewed proposal')
    require(d.get('semantic_key')==r['semantic_key'],'semantic key mismatch')
    batch_raw=snap.read(batch_path)
    expected_sha=d.get('reviewed_batch_sha256')
    require(isinstance(expected_sha,str) and HEX64.fullmatch(expected_sha) is not None and sha(batch_raw)==expected_sha,'reviewed batch SHA mismatch')
    # Carson names the path reviewed_batch; coordinator originally binds by SHA only.
    require(role!='carson' or 'reviewed_batch' in d,'Carson schema missing reviewed_batch path')
    if 'reviewed_batch' in d:
        require(local_path(d['reviewed_batch'],DOCS)==batch_path.resolve(),'reviewed_batch path mismatch')
    batch=snap.json(batch_path)
    actual=[x for x in batch['records'] if x.get('id')==identifier]
    require(len(actual)==1 and actual[0]==r,'id not bound to exact batch record')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS,'accept decision not authorized for this reviewer schema')
        return {'state':'non_accepting','role':role,'id':identifier,'decision':decision,
                'receipt':str(path.relative_to(ROOT)),'receipt_sha256':sha(raw),
                'reason':'reject/gap/candidate/other decisions confer zero credit and block automatic acceptance for same id'}
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'accepted credit must be integer1')
    observed=d.get('observed_chain',d.get('observed_complete_chain'))
    require(isinstance(observed,list) and bool(observed) and all(isinstance(x,str) and x.strip() for x in observed),'missing semantic full-chain observations')
    checks=d.get('source_checks'); chain=r.get('chain')
    require(isinstance(checks,list) and isinstance(chain,list) and len(checks)==len(chain)>0,'incomplete source range coverage')
    identities=[]; verified=[]
    for c,e in zip(checks,chain):
        require(isinstance(c,dict),'invalid source check')
        expected_path=e['source_local'] if role=='coordinator' else e['path']
        require((c.get('path'),c.get('line'),c.get('end_line'))==(expected_path,e['line'],e['end_line']),'source check range/path/order mismatch')
        require(all(c.get(k) is True for k in policy['checks']),'reviewer source check is not all explicit true')
        # Carson receipts bind values, coordinator receipts bind ranges + PASS; both replay actual bytes.
        fields=('source_local','source_sha256','git_blob_sha1','revision','excerpt_sha256','url')
        for k in fields:
            if role=='carson' or k in c: require(c.get(k)==e[k],'receipt source value mismatch: '+k)
        if 'excerpt' in c: require(c['excerpt']==e['excerpt'],'receipt excerpt content mismatch')
        proof=validate_source(e,snap)
        for k in ('source_metadata_sha256','tree_metadata_sha256'):
            if k in d: require(d[k]==proof[k],'receipt metadata byte hash mismatch: '+k)
        identity=(e['source_local'],e['line'],e['end_line'])
        require(identity not in identities,'duplicate source ranges cannot stand in for missing coverage')
        identities.append(identity); verified.append(proof)
    for k in ('repo','revision','path','source_local','source_sha256','git_blob_sha1','line','end_line','excerpt','excerpt_sha256','url'):
        require(r[k]==chain[0][k],'record primary evidence not equal to chain head: '+k)
    extra=extra_support(d,r,snap)
    result={'state':'validated_acceptance','id':identifier,'role':role,'reviewer':d['reviewer'],
            'decision':decision,'semantic_key':r['semantic_key'],'accepted_credit':1,
            'receipt':str(path.relative_to(ROOT)),'receipt_sha256':sha(raw),
            'batch':str(batch_path.relative_to(ROOT)),'batch_sha256':sha(batch_raw),
            'source_checks_recomputed':verified,'supporting_ranges_credit':0,
            'limitations':d.get('limits',d.get('remaining_gaps',d.get('boundaries',[]))),
            'observed_chain':observed,'verification_correction':d.get('verification_correction'),
            'additional_correction':d.get('additional_correction')}
    if extra: result['additional_support_check']=extra
    return result

def resolve(rows):
    grouped=defaultdict(list)
    for row in rows:
        if row.get('role') in AUTHORIZED and row.get('id'): grouped[row['id']].append(row)
    accepted=[]; conflicts=[]
    for identifier,group in sorted(grouped.items()):
        valid=[x for x in group if x['state']=='validated_acceptance']
        if not valid: continue
        fingerprints={(x['semantic_key'],x['batch_sha256']) for x in valid}
        if len(fingerprints)!=1 or len(valid)!=len(group):
            conflicts.append({'id':identifier,'action':'HOLD_ZERO_PENDING_HUMAN_RECONCILIATION',
                              'receipts':[{'receipt':x['receipt'],'receipt_sha256':x['receipt_sha256'],
                                           'state':x['state'],'reason':x.get('reason')} for x in group]})
            continue
        first=valid[0]
        accepted.append({'id':identifier,'semantic_key':first['semantic_key'],'accepted_credit':1,
                         'batch':first['batch'],'batch_sha256':first['batch_sha256'],
                         'scope':'one mechanism regardless of number of reviewers/supporting ranges',
                         'reviews':valid})
    # Different ids reusing a semantic key are also held, never added as distinct references.
    same=defaultdict(list)
    for row in accepted: same[row['semantic_key']].append(row['id'])
    duplicated={identifier for ids in same.values() if len(ids)>1 for identifier in ids}
    for identifier in sorted(duplicated): conflicts.append({'id':identifier,'action':'HOLD_ZERO_DUPLICATE_SEMANTIC_KEY'})
    return [x for x in accepted if x['id'] not in duplicated],conflicts

def aggregate(batches_by_id, receipt_inputs=None, snap=None):
    snap=snap or Snapshot()
    inputs=receipt_inputs if receipt_inputs is not None else [
        (p,snap.read(p)) for p in sorted((DOCS/'independent-reviews').glob('*.json'))]
    rows=[]
    for p,raw in inputs:
        try:
            rows.append(validate_receipt(p,raw,batches_by_id,snap))
        except (InvalidReceipt,ValueError,KeyError,TypeError,OSError,UnicodeError) as exc:
            match=NAME.fullmatch(Path(p).name)
            # Fail closed for an invalid receipt in an authorized namespace; untrusted labels never grant credit.
            rows.append({'state':'invalid','receipt':str(Path(p).relative_to(ROOT)),
                         'receipt_sha256':sha(raw),'role':match.group(1) if match else None,
                         'id':'EA-'+match.group(2) if match else None,'reason':str(exc)})
    accepted,conflicts=resolve(rows)
    return accepted,{'schema':'ecology-independent-receipt-validation-v2',
        'authorized_reviewers':{k:{'exact_labels':sorted(v['labels']),'accept_decisions':sorted(v['decisions'])} for k,v in AUTHORIZED.items()},
        'identity_boundary':'local user-authorized role/filename/exact label; not cryptographic identity authentication',
        'receipt_inputs':rows,'conflicts':conflicts,
        'counts':{'inspected_receipts':len(rows),'validated_acceptance_receipts':sum(x['state']=='validated_acceptance' for x in rows),
                  'invalid_or_nonaccepting':sum(x['state']!='validated_acceptance' for x in rows),
                  'unique_accepted_ids':len(accepted)},
        'upstream_execution':False,'production_or_runtime_credit':0},snap
