"""PROPOSED bounded source/shape audit, entirely in-memory fixtures, stdout only.

No complete author receipt is written or validated. No grant/marker is created.
Never imports installed receipt_validation or its historical validators. Require
Main's separate static review before anyone executes this proposed audit.
"""
from pathlib import Path
import copy
import importlib.util
import json
import sys


class MemoryReader:
    def __init__(self, mapping):
        self.mapping = mapping

    def read(self, path):
        path = Path(path)
        if path in self.mapping:
            return self.mapping[path]
        return path.read_bytes()

    def json(self, path):
        return json.loads(self.read(path))


def main():
    # The only loadable module is the sibling proposed source, not installed old
    # receipt_validation. This file is itself inert until a separately reviewed run.
    here = Path(__file__).resolve().parent
    proposal_dir = here.parent
    require_path = proposal_dir/'audit-inputs.json'
    inputs = json.loads(require_path.read_bytes())
    root = Path(inputs['root'])
    module_path = here/'maned_wolf_v36.py'
    module_spec = importlib.util.spec_from_file_location('proposed_maned_wolf_v36',module_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    for d in inputs['checked_private_inputs']:
        raw = Path(d['path']).read_bytes()
        module.require(module.sha(raw)==d['sha256'] and len(raw)==d['bytes'], 'private audit input changed')
    batch = json.loads(Path(inputs['batch']['path']).read_bytes())
    record = batch['records'][0]
    policy = json.loads((here/'maned_wolf_v36_policy.json').read_bytes())
    mapping = {root/e['source_local']:Path(e['payload']['path']).read_bytes() for e in inputs['new_cache_payloads']}
    reader = MemoryReader(mapping)
    positive = module.typed_sources(record,policy,reader,root)
    module.require(len(positive)==32,'exact source audit')
    # An in-memory shape fixture only; missing real grant/marker and no call to
    # validate_receipt can make this a formal author receipt or acceptance.
    shape_fixture = copy.deepcopy(record)
    shape_fixture.update(accepted_credit=1,reviewer=module.LABEL,reviewer_thread_id=module.AUTHOR,
        decision=module.DECISION,reviewed_batch=module.BATCH,reviewed_batch_sha256=policy['batch_sha256'],
        actual_author_confirmation=True,execution_grant=None,actual_attempt_marker=None,author_execution_token=None)
    module.record_shape(shape_fixture,record,policy)
    rejected = []
    def reject(name, call):
        try:
            call()
        except (ValueError,KeyError,TypeError):
            rejected.append(name)
        else:
            raise AssertionError('accepted synthetic negative: '+name)
    for name, kind in [('native_forged_Git','nativegit'),('range_bool','bool'),('wrong_revision','revision'),
                       ('changed_excerpt','excerpt'),('source_path_escape','escape'),('unknown_source_kind','kind')]:
        r=copy.deepcopy(record)
        if kind=='nativegit':next(e for e in r['chain'] if e['source_kind']=='artifact_native')['revision']='0'*40
        if kind=='bool':r['chain'][0]['line']=True
        if kind=='revision':r['chain'][0]['revision']='0'*40
        if kind=='excerpt':r['chain'][0]['excerpt']+='changed'
        if kind=='escape':r['chain'][0]['source_local']='../outside.java'
        if kind=='kind':r['chain'][0]['source_kind']='unknown'
        reject(name,lambda r=r:module.typed_sources(r,policy,reader,root))
    # Freeze-chain check above intentionally rejects any unauthorized mutation
    # even before detailed provenance. These separate byte tests retain exact
    # record/chain so they exercise actual source, metadata and archive reads.
    e=record['chain'][0]
    native=next(e for e in record['chain'] if e['source_kind']=='artifact_native')
    for name,path in [('source_bytes',root/e['source_local']),('metadata_bytes',root/e['source_metadata']),
                      ('tree_bytes',root/e['tree_metadata']),('native_archive_bytes',root/native['source_artifact']['path'])]:
        mm=dict(mapping);mm[path]=b'{}\n'
        reject(name,lambda mm=mm:module.typed_sources(record,policy,MemoryReader(mm),root))
    for name,key,value in [('wrong_author','reviewer_thread_id',module.MAIN),('wrong_decision','decision','PASS'),
                           ('credit_bool','accepted_credit',True),('missing_confirmation','actual_author_confirmation',False)]:
        f=copy.deepcopy(shape_fixture);f[key]=value
        reject(name,lambda f=f:module.record_shape(f,record,policy))
    f=copy.deepcopy(shape_fixture);f['limits']=f['limits'][:-1]
    reject('dropped_original_limit',lambda:module.record_shape(f,record,policy))
    f=copy.deepcopy(shape_fixture);f['unexpected_acceptance_flag']=True
    reject('unrecognized_receipt_field',lambda:module.record_shape(f,record,policy))
    reject('absolute_source_path',lambda:module.relative(root,'/tmp/outside.java'))
    module.receipt_bytes(b'shape-only-fixture', b'shape-only-fixture')
    module.inventory_match({'old-peer'}, {'old-peer'})
    reject('caller_raw_different_from_actual_file', lambda:module.receipt_bytes(b'caller', b'actual'))
    reject('late_competing_inventory_entry', lambda:module.inventory_match({'old-peer','competitor'}, {'old-peer'}))
    reject('missing_original_inventory_entry', lambda:module.inventory_match(set(), {'old-peer'}))
    module.require(len(rejected)==20,'bounded exact negative case count')
    # Re-read the private input closure; no publishing, old Snapshot, actual
    # author grant or marker involved in this source/shape audit.
    for d in inputs['checked_private_inputs']:
        raw=Path(d['path']).read_bytes()
        module.require(module.sha(raw)==d['sha256'] and len(raw)==d['bytes'],'private audit input changed')
    print(json.dumps(dict(status='PROPOSED_PRIVATE_SOURCE_AND_SHAPE_AUDIT_ONLY',typed_sources=len(positive),
        negative_cases=rejected,formal_receipts_created=0,complete_receipt_validator_calls=0,
        installed_or_old_validator_calls=0,grants_or_markers_created=0,live_writes=0,formal_credit=0)))


if __name__=='__main__':
    if not sys.dont_write_bytecode:
        raise SystemExit('Require Python -I -B; no bytecode files')
    main()
