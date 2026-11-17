"""Fail-closed receipt aggregation. Reads cached source as bytes, never runs it.
Reviewer authorization is the user's local role assignment plus exact namespace/label,
not a cryptographic identity proof. Receipt byte hashes bind the inspected files.
"""
import hashlib
import io
import json
import re
import zipfile
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
 'general': {
  'labels': {'general existing-chat independent complete-chain source and semantic review'},
  'decisions': {'ACCEPT_ONE_RELATED_IMPLEMENTATION_GENERAL_WITH_EXPLICIT_LIMITS'},
  'checks': ('source_sha256_match','git_blob_match','fixed_revision_match','excerpt_exact'),
  'thread_id': '01a12516-2eaf-73e2-b615-20f8b422158c',
  'allowed_ids': {'EA-0016', 'EA-0017', 'EA-0018', 'EA-0019', 'EA-0021', 'EA-0022', 'EA-0023', 'EA-0024', 'EA-0025', 'EA-0026', 'EA-0027', 'EA-0028', 'EA-0029', 'EA-0030', 'EA-0031', 'EA-0032', 'EA-0033', 'EA-0034', 'EA-0035', 'EA-0036', 'EA-0037', 'EA-0038', 'EA-0039', 'EA-0040', 'EA-0041', 'EA-0042', 'EA-0043', 'EA-0044', 'EA-0045', 'EA-0046', 'EA-0047', 'EA-0048', 'EA-0049', 'EA-0050', 'EA-0051', 'EA-0052'},
  'proposal_author_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34'},
}
ALL_ACCEPT_DECISIONS=set().union(*(r['decisions'] for r in AUTHORIZED.values()))
HEX40=re.compile(r'[0-9a-f]{40}\Z')
HEX64=re.compile(r'[0-9a-f]{64}\Z')
NAME=re.compile(r'(coordinator|carson|general)-EA([0-9]{4})\.json\Z')

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

def general_context(review, record, snap, policy, identifier):
    """One explicitly scoped new reviewer, including its original native support.

    These are bindings, not automatic semantic judgment or remote identity proof.
    Neither legacy reviewer schema nor native/gameplay credit is expanded.
    """
    require(identifier in policy['allowed_ids'], 'general reviewer scope not authorized for this id')
    require(review.get('reviewer_thread_id')==policy['thread_id'], 'general reviewer thread mismatch')
    require(record.get('author_thread_id')==policy['proposal_author_thread_id'] and
            record['author_thread_id']!=review['reviewer_thread_id'], 'general review not independent of proposal author')
    descriptor=record.get('complete_chain_proposal')
    require(review.get('complete_chain_proposal')==descriptor and isinstance(descriptor,dict),
            'complete original proposal binding mismatch')
    proposal_path=local_path(descriptor['path'],DOCS)
    require(sha(snap.read(proposal_path))==descriptor['sha256'],'complete proposal SHA mismatch')
    proposal=snap.json(proposal_path)
    require(proposal.get('candidate_id')==record.get('original_candidate_id') and
            proposal.get('semantic_key')==record['semantic_key'] and
            proposal.get('source_commit')==record['revision'], 'complete proposal identity mismatch')
    complete=review.get('complete_chain_review')
    require(isinstance(complete,dict),'missing independent complete-chain review')
    complete_path=local_path(complete['path'],DOCS)
    require(sha(snap.read(complete_path))==complete['sha256'],'complete independent review SHA mismatch')
    peer=snap.json(complete_path)
    require(peer.get('reviewer_thread_id')==policy['thread_id'] and peer.get('proposal')==descriptor and
            peer.get('candidate_id')==proposal['candidate_id'] and peer.get('semantic_key')==record['semantic_key'],
            'complete independent review identity mismatch')
    require(peer.get('status')=='INDEPENDENT_SOURCE_REVIEW_RECOMMEND_ACCEPT_AT_MOST_ONE_WITH_EXPLICIT_CORRECTIONS_ZERO_APPLIED_CREDIT' and
            type(peer.get('recommended_maximum_credit')) is int and peer['recommended_maximum_credit']==1 and
            all(type(peer.get(k)) is int and peer[k]==0 for k in ('accepted_credit','applied_credit','supporting_ranges_credit')),
            'complete review not an eligible independent one-family recommendation')
    refs=proposal.get('actual_read_ranges'); checks=peer.get('range_checks')
    require(isinstance(refs,list) and isinstance(checks,list) and len(refs)==len(checks)==29,
            'complete native/mod range coverage missing')
    artifact=proposal['native_artifact']
    require(artifact==record.get('native_auxiliary_artifact') and
            artifact==peer['source_provenance']['native_artifact'], 'native artifact binding mismatch')
    archive_path=Path(artifact['source_archive']).resolve()
    require(archive_path.is_relative_to((ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches').resolve()),
            'native archive outside original evidence cache')
    archive_raw=snap.read(archive_path)
    require(sha(archive_raw)==artifact['sha']==peer['source_provenance']['native_archive_sha256_recomputed'],
            'native archive SHA mismatch')
    native_base=local_path(artifact['private_source'],ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources')
    native_files=set()
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        for index,(ref,check) in enumerate(zip(refs,checks)):
            require(check.get('index')==index and check.get('actual_text_read') is True and
                    type(check.get('support_credit')) is int and check['support_credit']==0,
                    'complete review missing actual zero-credit source read')
            for field in ('path','source_path','lines','file_sha256','excerpt_sha256'):
                require(check.get(field)==ref[field],'complete source binding mismatch: '+field)
            source=local_path(ref['path'],ROOT/'tools/cod4')
            raw=snap.read(source)
            lo,hi=ref['lines']; lines=raw.decode().splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(lines), 'complete source range invalid')
            require(sha(raw)==ref['file_sha256'] and
                    sha(''.join(lines[lo-1:hi]).encode())==ref['excerpt_sha256'], 'complete actual source/excerpt mismatch')
            if ref.get('repo')==record['repo']:
                require(check.get('tree_blob_matches') is True and check.get('commit')==record['revision'],
                        'complete mod binding mismatch')
                # The formal chain replays the same fixed blob under the ecology evidence root.
                linked=[e for e in record['chain'] if (e['path'],e['line'],e['end_line'])==
                        (ref['source_path'],lo,hi)]
                require(len(linked)==1 and linked[0]['source_sha256']==sha(raw) and
                        linked[0]['git_blob_sha1']==ref['git_blob_sha1']==check['git_blob_sha1'],
                        'complete mod range not bound to formal source chain')
            else:
                require(source==(native_base/ref['source_path']).resolve(), 'native source vs archive path mismatch')
                require(check.get('archive_entry_exact') is True and check.get('source_archive_sha256')==artifact['sha'],
                        'native reviewer archive binding mismatch')
                require(archive.read(ref['source_path'])==raw,'actual native source differs from archive entry')
                native_files.add(ref['source_path'])
    require(len(native_files)==6, 'native support file coverage missing')
    return {'proposal':descriptor,'review':complete,'range_count_support0':len(refs),
            'native_archive_sha256':artifact['sha'],'native_files_support0':len(native_files),
            'original_proposal_author_thread_id':record['author_thread_id'],
            'actual_reviewer_thread_id':review['reviewer_thread_id'],'native_gameplay_credit':0}

GENERAL_EA16_BINDINGS = {
    'complete_chain_proposal': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-skreecher-alarm-latch-proposal-20261102.json',
        'sha256': '0a6d1e1587ca76121689cd0a4e904800b7c2c37a9592d5c61fc73a786d543a2f'},
    'complete_chain_review': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-skreecher-alarm-latch-review-20261102.json',
        'sha256': '78c301cd11633efbde13f25ca7020f880352c3fc153f11766c76626c75bcaa82'},
    'complete_chain_clarification': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-skreecher-floor-guard-clarification-20261102.json',
        'sha256': '54b04dd0e34996f06ce2225e38d157b3ff7c4ea3605301e5aab65eed469bca7e'},
}


def general_skreecher_context(review, record, snap, policy, identifier):
    """EA16 only; actual prior read plus immutable floor clarification, support0.

    Local role authorization is not cryptographic identity authentication. The
    old EA17 general_context and legacy reviewer validation stay unchanged.
    """
    require(identifier == 'EA-0016' and identifier in policy['allowed_ids'],
            'Skreecher general reviewer scope mismatch')
    require(review.get('reviewer_thread_id') == policy['thread_id'],
            'Skreecher actual reviewer thread mismatch')
    require(record.get('author_thread_id') == policy['proposal_author_thread_id'] and
            record['author_thread_id'] != review['reviewer_thread_id'],
            'Skreecher proposal and review authors not independent')
    require(record.get('general_context_schema') == 'skreecher-alarm-latch-v1',
            'EA16 requires its own context schema, not EA17 schema')
    require(type(record.get('proposed_credit')) is int and record['proposed_credit'] == 1 and
            type(record.get('accepted_credit')) is int and record['accepted_credit'] == 0 and
            type(record.get('supporting_ranges_credit')) is int and record['supporting_ranges_credit'] == 0,
            'EA16 proposal and support credits must be exact integers')
    require('original_candidate_id' not in record and 'candidate_id' not in record and
            'original_candidate_id' not in review and 'candidate_id' not in review,
            'EA16 has no candidate id; invented candidate identity rejected')
    documents = {}
    for field, expected in GENERAL_EA16_BINDINGS.items():
        require(record.get(field) == expected and review.get(field) == expected,
                'EA16 exact original document binding mismatch: ' + field)
        path = local_path(expected['path'], DOCS)
        require(sha(snap.read(path)) == expected['sha256'], 'EA16 original document SHA mismatch: ' + field)
        documents[field] = snap.json(path)
    proposal = documents['complete_chain_proposal']
    peer = documents['complete_chain_review']
    clarification = documents['complete_chain_clarification']
    require('candidate_id' not in proposal and 'candidate_id' not in peer,
            'Skreecher original documents do not use a candidate id')
    require(record.get('repo') == 'AlexModGuy/AlexsMobs' and
            record.get('revision') == proposal.get('source_commit') == '09755dade2cfbdf14839e026d3af446f9d3ff843' and
            record.get('semantic_key') == proposal.get('semantic_key') == peer.get('semantic_key') ==
            'ai-alarm-triggered-local-encounter-with-persisted-single-attempt-latch',
            'EA16 source or semantic identity mismatch')
    require(peer.get('reviewer_thread_id') == policy['thread_id'] and
            peer.get('proposal') == GENERAL_EA16_BINDINGS['complete_chain_proposal'] and
            peer.get('status') == 'INDEPENDENT_COMPLETE_LOCAL_SOURCE_REVIEW_RECOMMEND_AT_MOST_ONE_WITH_EXPLICIT_LIMITS_ZERO_APPLIED_CREDIT' and
            peer.get('draft_association') == proposal.get('draft_association'),
            'EA16 complete review identity/schema mismatch')
    require(type(peer.get('recommended_maximum_credit')) is int and peer['recommended_maximum_credit'] == 1 and
            all(type(peer.get(k)) is int and peer[k] == 0 for k in
                ('accepted_credit', 'applied_credit', 'supporting_ranges_credit')),
            'EA16 complete review is not an integer1 recommendation with zero applied credit')
    require(clarification.get('reviewer_thread_id') == policy['thread_id'] and
            clarification.get('review') == GENERAL_EA16_BINDINGS['complete_chain_review'] and
            clarification.get('status') == 'IMMUTABLE_REVIEW_WORDING_CLARIFICATION_ZERO_CREDIT' and
            clarification.get('recommendation_changed') is False and
            type(clarification.get('recommended_maximum_credit')) is int and clarification['recommended_maximum_credit'] == 1 and
            all(type(clarification.get(k)) is int and clarification[k] == 0 for k in
                ('applied_credit', 'new_source_read_credit')),
            'EA16 immutable floor clarification identity or credit mismatch')
    refs, checks = proposal.get('actual_read_ranges'), peer.get('range_checks')
    require(isinstance(refs, list) and isinstance(checks, list) and len(refs) == len(checks) == 24,
            'EA16 complete24 range coverage missing')
    formal = record.get('chain')
    require(isinstance(formal, list) and len(formal) == 15, 'EA16 formal15 mod ranges missing')
    native_refs = [r for r in refs if r.get('source_kind') == 'native_forge_archive']
    require(len(native_refs) == 9 and record.get('native_auxiliary_ranges') == native_refs,
            'EA16 original native9 ranges mismatch')
    artifact = proposal['native_artifact']
    require(artifact == record.get('native_auxiliary_artifact') == peer['provenance']['native_artifact'],
            'EA16 native artifact identity mismatch')
    archive_path = Path(artifact['source_archive']).resolve()
    require(archive_path.is_relative_to((ROOT / 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches').resolve()),
            'EA16 native archive outside original cache')
    archive_raw = snap.read(archive_path)
    require(sha(archive_raw) == artifact['sha'] == peer['provenance']['native_archive_sha256_recomputed'],
            'EA16 actual native archive SHA mismatch')
    native_base = local_path(artifact['private_source'], ROOT / 'tools/cod4/legacy-migration-acceptance/.work/sources')
    identities, native_files, mod_count = set(), set(), 0
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        for index, (ref, check) in enumerate(zip(refs, checks)):
            require(type(check.get('index')) is int and check['index'] == index and
                    check.get('actual_text_read') is True and ref.get('actually_read') is True and
                    all(type(x.get('support_credit')) is int and x['support_credit'] == 0 for x in (ref, check)),
                    'EA16 missing actual read or exact integer0 support')
            for field in ('path', 'source_path', 'lines', 'file_sha256', 'excerpt_sha256', 'source_kind'):
                require(check.get(field) == ref[field], 'EA16 complete source binding mismatch: ' + field)
            source = local_path(ref['path'], ROOT / 'tools/cod4')
            raw = snap.read(source)
            lo, hi = ref['lines']
            lines = raw.decode('utf-8').splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines),
                    'EA16 invalid complete source range')
            identity = (ref['path'], lo, hi)
            require(identity not in identities, 'EA16 duplicate complete source range')
            identities.add(identity)
            require(sha(raw) == ref['file_sha256'] and sha(''.join(lines[lo-1:hi]).encode()) == ref['excerpt_sha256'],
                    'EA16 actual complete source/excerpt mismatch')
            if ref['source_kind'] == 'fixed_mod_git':
                mod_count += 1
                require(ref.get('repo') == check.get('repo') == record['repo'] and
                        ref.get('commit') == check.get('commit') == record['revision'] and
                        check.get('tree_blob_matches') is True,
                        'EA16 original mod repo/revision/tree binding mismatch')
                linked = [e for e in formal if (e['path'], e['line'], e['end_line']) == (ref['source_path'], lo, hi)]
                require(len(linked) == 1, 'EA16 mod range not linked exactly once to formal chain')
                evidence = linked[0]
                require(evidence['source_sha256'] == sha(raw) and
                        evidence['git_blob_sha1'] == ref['git_blob_sha1'] == check['git_blob_sha1'] and
                        evidence['url'] == ref['url'] == check['url'], 'EA16 mod blob/URL mismatch')
                require(snap.read(local_path(evidence['source_local'], TOOLS / 'sources')) == raw,
                        'EA16 relocated formal source differs from original bytes')
                proof = validate_source(evidence, snap)
                require(proof['source_metadata_sha256'] == proposal['source_metadata_sha256'] == check['source_metadata_sha256'] and
                        proof['tree_metadata_sha256'] == proposal['source_tree_sha256'] == check['tree_metadata_sha256'],
                        'EA16 actual source metadata/tree SHA mismatch')
            else:
                require(ref['source_kind'] == 'native_forge_archive', 'EA16 unknown complete source kind')
                require(source == (native_base / ref['source_path']).resolve(), 'EA16 native source path mismatch')
                require(ref.get('source_archive_sha256') == check.get('source_archive_sha256') == artifact['sha'] and
                        ref.get('archive_entry_exact') is True and check.get('archive_entry_exact') is True,
                        'EA16 native archive-entry binding mismatch')
                require(archive.read(ref['source_path']) == raw, 'EA16 actual native entry differs from source')
                native_files.add(ref['source_path'])
    require(mod_count == 15 and len(native_files) == 4, 'EA16 exact15mod/4native-file coverage missing')
    return {'proposal': GENERAL_EA16_BINDINGS['complete_chain_proposal'],
            'review': GENERAL_EA16_BINDINGS['complete_chain_review'],
            'clarification': GENERAL_EA16_BINDINGS['complete_chain_clarification'],
            'range_count_support0': 24, 'mod_ranges_support0': 15, 'native_ranges_support0': 9,
            'native_files_support0': 4, 'native_archive_sha256': artifact['sha'],
            'original_proposal_author_thread_id': record['author_thread_id'],
            'actual_reviewer_thread_id': review['reviewer_thread_id'], 'native_gameplay_credit': 0}


GENERAL_EA18_BINDINGS = {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-terrapin-parent-payload-proposal-20261102.json', 'sha256': '1607ef4f719ab013a0d0bb59cb72499e55677a4d781f513e88e8429719fcbf47'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-terrapin-parent-payload-review-20261103.json', 'sha256': 'bb28c1f73828ba83fcb2c12e84c08d6b05f8c0b24a31eee316bbf0302d9f6e55'}, 'complete_chain_clarification': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-terrapin-nbt-merge-clarification-20261102.json', 'sha256': 'ca2fca70dcc17651265bd3415b878b9ca9fb856a041dd2539a0fc20ddf2ccaae'}}


def general_terrapin_context(review, record, snap, policy, identifier):
    """EA18 only: actual independent parent-payload review; all ranges support0."""
    require(identifier == 'EA-0018' and identifier in policy['allowed_ids'], 'EA18 reviewer scope mismatch')
    require(review.get('reviewer_thread_id') == policy['thread_id'] and
            record.get('author_thread_id') == policy['proposal_author_thread_id'] and
            record['author_thread_id'] != review['reviewer_thread_id'], 'EA18 actual independent authors mismatch')
    require(record.get('general_context_schema') == 'terrapin-parent-payload-v1', 'EA18 wrong context schema')
    require(all(type(record.get(k)) is int and record[k] == value for k, value in
                [('proposed_credit',1),('accepted_credit',0),('supporting_ranges_credit',0)]), 'EA18 exact proposal credits required')
    require(all(k not in obj for obj in (record,review) for k in ('candidate_id','original_candidate_id')),
            'EA18 has no candidate identifier')
    documents = {}
    for field, expected in GENERAL_EA18_BINDINGS.items():
        require(record.get(field) == review.get(field) == expected, 'EA18 exact document binding mismatch: '+field)
        path = local_path(expected['path'], DOCS)
        require(sha(snap.read(path)) == expected['sha256'], 'EA18 immutable document SHA mismatch')
        documents[field] = snap.json(path)
    proposal, peer = documents['complete_chain_proposal'], documents['complete_chain_review']
    require(peer.get('reviewer_thread_id') == policy['thread_id'] and
            peer.get('proposal') == GENERAL_EA18_BINDINGS['complete_chain_proposal'] and
            peer.get('status') == 'INDEPENDENT_COMPLETE_PARENT_PAYLOAD_REVIEW_RECOMMEND_AT_MOST_ONE_WITH_CONDITIONAL_CORRECTIONS_ZERO_APPLIED_CREDIT' and
            type(peer.get('recommended_maximum_credit')) is int and peer['recommended_maximum_credit'] == 1 and
            all(type(peer.get(k)) is int and peer[k] == 0 for k in ('accepted_credit','applied_credit','supporting_ranges_credit')),
            'EA18 eligible actual independent recommendation missing')
    require(record['repo'] == 'AlexModGuy/AlexsMobs' and record['revision'] == proposal['source_commit'] ==
            '09755dade2cfbdf14839e026d3af446f9d3ff843' and record['semantic_key'] == proposal['semantic_key'] == peer['semantic_key'] ==
            'phenotypic-parent-payload-across-pregnancy-egg-block-stack-silk-and-bucket-boundaries', 'EA18 source/semantic identity mismatch')
    require(record['observation'] == review.get('observed_chain') == peer['observed_chain'] and review.get('limits') == record['limits'] and
            record['limits'] == peer['limitations']+[x['correction'] for x in peer['proposal_corrections_and_conditions']],
            'EA18 complete corrected semantic observations/limits mismatch')
    refs, checks, formal = proposal['actual_read_ranges'], peer['range_checks'], record['chain']
    require(len(refs) == len(checks) == 51 and len(formal) == 22, 'EA18 exact51/22 range coverage missing')
    artifact = proposal['native_artifact']
    require(artifact == record.get('native_auxiliary_artifact') == peer['provenance']['native_artifact'] and
            record.get('native_auxiliary_ranges') == [r for r in refs if r['source_kind']=='native_forge_archive'],
            'EA18 native artifact/range mismatch')
    archive_path = Path(artifact['source_archive']).resolve()
    require(archive_path.is_relative_to((ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches').resolve()),
            'EA18 native archive outside original cache')
    archive_raw = snap.read(archive_path)
    require(sha(archive_raw) == artifact['sha'] == peer['provenance']['native_archive_sha256_recomputed'], 'EA18 actual archive SHA mismatch')
    native_base = local_path(artifact['private_source'], ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources')
    native_files, identities, mod_count = set(), set(), 0
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        for index,(ref,check) in enumerate(zip(refs,checks)):
            require(type(check.get('index')) is int and check['index']==index and check.get('actual_text_read') is True and
                    ref.get('actually_read') is True and all(type(x.get('support_credit')) is int and x['support_credit']==0 for x in (ref,check)),
                    'EA18 actual read/support identity mismatch')
            for field in ('path','source_path','lines','file_sha256','excerpt_sha256','source_kind'):
                require(ref[field] == check.get(field), 'EA18 complete source binding mismatch: '+field)
            source = local_path(ref['path'], ROOT/'tools/cod4')
            raw = snap.read(source); lo,hi=ref['lines']; lines=raw.decode().splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(lines), 'EA18 invalid range')
            identity=(ref['path'],lo,hi)
            require(identity not in identities, 'EA18 duplicate complete range')
            identities.add(identity)
            require(sha(raw)==ref['file_sha256'] and sha(''.join(lines[lo-1:hi]).encode())==ref['excerpt_sha256'],
                    'EA18 actual complete source/excerpt mismatch')
            if ref['source_kind']=='fixed_mod_git':
                mod_count+=1
                require(ref['repo']==check.get('repo')==record['repo'] and ref['commit']==check.get('commit')==record['revision'] and
                        check.get('tree_blob_matches') is True, 'EA18 original mod identity mismatch')
                linked=[e for e in formal if (e['path'],e['line'],e['end_line'])==(ref['source_path'],lo,hi)]
                require(len(linked)==1, 'EA18 mod range not linked exactly once')
                e=linked[0]
                require(e['source_sha256']==sha(raw) and e['git_blob_sha1']==ref['git_blob_sha1']==check.get('git_blob_sha1') and
                        e['url']==ref['url']==check.get('url') and snap.read(local_path(e['source_local'],TOOLS/'sources'))==raw,
                        'EA18 formal/original source/blob/URL mismatch')
                proof=validate_source(e,snap)
                require(proof['source_metadata_sha256']==proposal['source_metadata_sha256']==check.get('source_metadata_sha256') and
                        proof['tree_metadata_sha256']==proposal['source_tree_sha256']==check.get('tree_metadata_sha256'),
                        'EA18 actual metadata/tree mismatch')
            else:
                require(ref['source_kind']=='native_forge_archive' and source==(native_base/ref['source_path']).resolve(),
                        'EA18 native source identity mismatch')
                require(ref.get('source_archive_sha256')==check.get('source_archive_sha256')==artifact['sha'] and
                        ref.get('archive_entry_exact') is True and check.get('archive_entry_exact') is True and
                        archive.read(ref['source_path'])==raw, 'EA18 actual native entry mismatch')
                native_files.add(ref['source_path'])
        extras=peer.get('additional_native_support_checks')
        require(isinstance(extras,list) and len(extras)==10, 'EA18 ten native delta supports missing')
        for index,ref in enumerate(extras):
            require(type(ref.get('index')) is int and ref['index']==index and ref.get('actual_text_read') is True and
                    type(ref.get('support_credit')) is int and ref['support_credit']==0 and
                    ref.get('source_kind')=='native_forge_archive' and ref.get('source_archive_sha256')==artifact['sha'] and
                    ref.get('archive_entry_exact') is True, 'EA18 native delta reviewer binding mismatch')
            source=local_path(ref['path'],native_base)
            require(source==(native_base/ref['source_path']).resolve(), 'EA18 native delta path mismatch')
            raw=snap.read(source); lo,hi=ref['lines']; lines=raw.decode().splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(lines) and archive.read(ref['source_path'])==raw and
                    sha(raw)==ref['file_sha256'] and sha(''.join(lines[lo-1:hi]).encode())==ref['excerpt_sha256'],
                    'EA18 actual native delta bytes/excerpt mismatch')
    require(mod_count==22 and len(native_files)==12, 'EA18 exact mod/native file coverage missing')
    return dict(proposal=GENERAL_EA18_BINDINGS['complete_chain_proposal'], review=GENERAL_EA18_BINDINGS['complete_chain_review'],
                clarification=GENERAL_EA18_BINDINGS['complete_chain_clarification'], range_count_support0=51,
                native_delta_ranges_support0=10, mod_ranges_support0=22, native_ranges_support0=29, native_files_support0=12,
                native_archive_sha256=artifact['sha'], original_proposal_author_thread_id=record['author_thread_id'],
                actual_reviewer_thread_id=review['reviewer_thread_id'], native_gameplay_credit=0)

GENERAL_EA19_BINDINGS = {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-ferrouslime-cohort-transfer-proposal-20261103.json', 'sha256': 'c422b5a6ffa94d6c9da58cc1b79bffb1797e0dc9449dc3e42363e938c20f58bb'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-ferrouslime-cohort-transfer-review-20261103.json', 'sha256': '7802f8ddd2878763342397afbd66d6ce532c9bdfed01ab085d25f9054525c751'}, 'complete_chain_corrections': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-ferrouslime-peer-corrections-20261103.json', 'sha256': 'b04e3313b8c605088490912c7efe2fedb58c51d98299e2ede3da3b371d7e5199'}}


def general_ferrouslime_context(review, record, snap, policy, identifier):
    """EA19 only, original complete cohort source review with mandatory corrections."""
    require(identifier=='EA-0019' and identifier in policy['allowed_ids'], 'EA19 reviewer scope mismatch')
    require(review.get('reviewer_thread_id')==policy['thread_id'] and
            record.get('author_thread_id')==policy['proposal_author_thread_id'] and
            record['author_thread_id']!=review['reviewer_thread_id'], 'EA19 actual independent authors mismatch')
    require(record.get('general_context_schema')=='ferrouslime-cohort-transfer-v1', 'EA19 wrong context schema')
    require(all(type(record.get(k)) is int and record[k]==v for k,v in
                [('proposed_credit',1),('accepted_credit',0),('supporting_ranges_credit',0)]), 'EA19 exact proposal credits required')
    require(all(k not in obj for obj in (record,review) for k in ('candidate_id','original_candidate_id')), 'EA19 no candidate identifier')
    docs={}
    for field,expected in GENERAL_EA19_BINDINGS.items():
        require(record.get(field)==review.get(field)==expected, 'EA19 exact document binding mismatch: '+field)
        path=local_path(expected['path'],DOCS)
        require(sha(snap.read(path))==expected['sha256'], 'EA19 immutable document SHA mismatch')
        docs[field]=snap.json(path)
    proposal,peer,corrections=[docs[k] for k in GENERAL_EA19_BINDINGS]
    require(peer.get('reviewer_thread_id')==policy['thread_id'] and peer.get('proposal')==GENERAL_EA19_BINDINGS['complete_chain_proposal'] and
            peer.get('status')=='INDEPENDENT_COMPLETE_COHORT_SOURCE_REVIEW_RECOMMEND_AT_MOST_ONE_WITH_MANDATORY_CORRECTIONS_ZERO_APPLIED_CREDIT' and
            type(peer.get('recommended_maximum_credit')) is int and peer['recommended_maximum_credit']==1 and
            all(type(peer.get(k)) is int and peer[k]==0 for k in ('accepted_credit','applied_credit','supporting_ranges_credit')),
            'EA19 actual independent complete source recommendation missing')
    require(record['repo']=='AlexModGuy/AlexsCaves' and record['revision']==peer['provenance']['revision']=='4718f4287c65b810aecb211789b45f54d405a94d' and
            record['semantic_key']==proposal['proposed_semantic_key']==peer['semantic_key']==corrections['semantic_key']==
            'live-cohort-head-aggregation-and-stall-or-death-triggered-bisection-with-uncommitted-adds', 'EA19 source/semantic identity mismatch')
    require(corrections.get('author_thread_id')==record['author_thread_id'] and type(corrections.get('accepted_credit')) is int and corrections['accepted_credit']==0 and
            corrections.get('mandatory_corrections')==peer['proposal_corrections_and_conditions'] and len(peer['proposal_corrections_and_conditions'])==5,
            'EA19 five mandatory corrections missing')
    require(record['observation']==review.get('observed_chain')==corrections['corrected_observations']==peer['observed_chain'] and
            record['limits']==review.get('limits')==corrections['limitations']+[x['mandatory_correction'] for x in peer['proposal_corrections_and_conditions']],
            'EA19 corrected complete observations/limits mismatch')
    formal,refs,checks=record['chain'],proposal['source_refs'],peer['source_checks']
    require(len(formal)==7 and len(refs)==len(checks)==6, 'EA19 exact original6 plus header coverage missing')
    header=corrections['additional_mod_header_binding']
    require(header==peer['additional_mod_header_support'] and header.get('actual_text_read') is True and
            type(header.get('support_credit')) is int and header['support_credit']==0, 'EA19 additional mod header review mismatch')
    header_ref=dict(refs[2],path=header['source_local'],source_path=header['source_path'],lines=header['lines'],excerpt_sha256=header['raw_excerpt_sha256'])
    header_ref['url']='https://github.com/AlexModGuy/AlexsCaves/blob/'+header['revision']+'/'+header['source_path']+'#L1-L20'
    allrefs=refs+[header_ref]
    for index,(ref,e) in enumerate(zip(allrefs,formal)):
        lo,hi=ref['lines'];source=local_path(ref['path'],ROOT/'tools/cod4');raw=snap.read(source);lines=raw.decode().splitlines(keepends=True)
        require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(lines) and sha(raw)==ref['file_sha256'] and
                sha(''.join(lines[lo-1:hi]).encode())==ref['excerpt_sha256'], 'EA19 original mod source/excerpt mismatch')
        require((e['path'],e['line'],e['end_line'])==(ref['source_path'],lo,hi) and e['url']==ref['url'] and
                e['source_sha256']==sha(raw) and e['git_blob_sha1']==ref['git_blob_sha1'] and
                snap.read(local_path(e['source_local'],TOOLS/'sources'))==raw, 'EA19 exact formal/original mod identity mismatch')
        proof=validate_source(e,snap)
        require(proof['source_metadata_sha256']==ref['source_metadata_sha256'] and proof['tree_metadata_sha256']==ref['tree_metadata_sha256'],
                'EA19 original fixed metadata/tree mismatch')
        if index<6:
            check=checks[index]
            require(type(check.get('index')) is int and check['index']==index and check.get('actual_text_read_by_this_reviewer') is True and
                    check.get('metadata_tree_revision_match') is True and check.get('raw_excerpt_matches') is True and
                    type(check.get('reviewer_support_credit')) is int and check['reviewer_support_credit']==0 and ref.get('coordinator_actually_read') is True,
                    'EA19 original mod actual reading/support mismatch')
            require(all(check.get(k)==ref[k] for k in ('path','source_path','lines','file_sha256','git_blob_sha1','revision','excerpt_sha256','url')) and
                    check.get('raw_file_sha256_recomputed')==sha(raw) and check.get('blob_header_sha1_recomputed')==e['git_blob_sha1'],
                    'EA19 independent mod source proof mismatch')
    artifact={'source_archive':peer['provenance']['archive'],'sha256':peer['provenance']['archive_sha256']}
    require(record.get('native_auxiliary_artifact')==artifact and record.get('native_auxiliary_ranges')==corrections['native_raw_binding_checks'],
            'EA19 corrected raw native artifact/coverage mismatch')
    archive_path=local_path(artifact['source_archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches')
    archive_raw=snap.read(archive_path)
    require(sha(archive_raw)==artifact['sha256']=='1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0', 'EA19 actual native archive SHA mismatch')
    original_native=proposal['native_source_refs'];native_checks=peer['native_source_checks'];extras=peer['additional_native_support_checks'];raw_checks=corrections['native_raw_binding_checks']
    require(len(original_native)==len(native_checks)==6 and len(extras)==16 and len(raw_checks)==22, 'EA19 exact6+16 native coverage missing')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        identities=set()
        for index,(ref,raw_check) in enumerate(zip(original_native+extras,raw_checks)):
            entry=ref['entry'];lo,hi=ref['lines'];raw=archive.read(entry);lines=raw.decode().splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(lines) and (entry,lo,hi) not in identities, 'EA19 invalid/duplicate native range')
            identities.add((entry,lo,hi));excerpt=''.join(lines[lo-1:hi]).encode();normalized=('\n'.join(raw.decode().splitlines()[lo-1:hi])+'\n').encode()
            require(ref['archive']==artifact['source_archive'] and ref['archive_sha256']==artifact['sha256'] and sha(raw)==ref['entry_sha256'] and
                    raw_check['entry']==entry and raw_check['lines']==[lo,hi] and raw_check['entry_sha256']==sha(raw) and raw_check['raw_excerpt_sha256']==sha(excerpt) and
                    raw_check.get('coordinator_actually_read') is True and type(raw_check.get('support_credit')) is int and raw_check['support_credit']==0,
                    'EA19 actual corrected native raw bytes mismatch')
            if index<6:
                check=native_checks[index]
                require(ref.get('coordinator_actually_read') is True and type(ref.get('research_credit')) is int and ref['research_credit']==0 and
                        type(check.get('index')) is int and check['index']==index and check.get('actual_text_read_by_this_reviewer') is True and
                        type(check.get('reviewer_support_credit')) is int and check['reviewer_support_credit']==0 and
                        check.get('actual_archive_entry_sha256')==sha(raw) and check.get('actual_raw_excerpt_sha256')==sha(excerpt) and
                        check.get('proposal_excerpt_matches_LF_join_plus_terminal_LF') is True and sha(normalized)==ref['excerpt_sha256'] and
                        check.get('proposal_excerpt_matches_raw_bytes') is (sha(excerpt)==ref['excerpt_sha256']),
                        'EA19 explicit original normalized-vs-raw native proof mismatch')
            else:
                require(ref.get('actual_text_read') is True and type(ref.get('support_credit')) is int and ref['support_credit']==0 and
                        ref['raw_excerpt_sha256']==sha(excerpt), 'EA19 extra native raw reading proof mismatch')
    for comp in peer['semantic_comparisons']:
        descriptor=comp.get('batch') or comp.get('receipt')
        require(descriptor is not None and sha(snap.read(local_path(descriptor['path'],DOCS)))==descriptor['sha256'], 'EA19 comparison evidence bytes changed')
    return dict(proposal=GENERAL_EA19_BINDINGS['complete_chain_proposal'],review=GENERAL_EA19_BINDINGS['complete_chain_review'],
                corrections=GENERAL_EA19_BINDINGS['complete_chain_corrections'],mod_ranges_support0=7,native_ranges_support0=22,
                mandatory_corrections=5,original_normalized_native_ranges=6,actual_reviewer_thread_id=review['reviewer_thread_id'],native_gameplay_credit=0)

COORDINATOR_EA20_BINDINGS = {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/reviewer-tusklin-dimension-conversion-proposal-20261103.json', 'sha256': '359b7068a6019fb34bb3fbdc6eb5c74724a7ef0fdc6e637ec370db37c617443c'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-tusklin-dimension-conversion-review-20261103.json', 'sha256': '9448d57e957c1baf6fba4e4a4be485dcf1fb21a1e843add253b2443dd0ad599a'}}


def coordinator_tusklin_context(review, record, snap, policy, identifier, role):
    """EA20 only: real coordinator peer review of separate General authored source proposal."""
    require(identifier == 'EA-0020' and role == 'coordinator', 'EA20 requires actual coordinator reviewer role')
    author = '01a12516-2eaf-73e2-b615-20f8b422158c'
    reviewer = '01a16364-cac0-7ca2-a042-a5312781ca34'
    require(review.get('reviewer_thread_id') == reviewer and record.get('author_thread_id') == author and
            record.get('independent_reviewer_thread_id') == reviewer and author != reviewer,
            'EA20 actual independent authors mismatch')
    require(record.get('coordinator_context_schema') == 'tusklin-precommitted-conversion-v1', 'EA20 context schema mismatch')
    require(all(type(record.get(k)) is int and record[k] == n for k,n in
                [('proposed_credit',1),('accepted_credit',0),('supporting_ranges_credit',0)]), 'EA20 exact proposal credit types required')
    require(all(type(review.get(k)) is int and review[k] == 0 for k in ('supporting_ranges_credit','native_gameplay_credit')),
            'EA20 review support/native credits must be integer0')
    require(all(k not in obj for obj in (review,record) for k in ('candidate_id','original_candidate_id')), 'EA20 no invented candidate identifier')
    require(review.get('reviewed_batch') == str((DOCS/'batch-015.json').relative_to(ROOT)), 'EA20 exact reviewed batch path required')
    documents = {}
    for field, descriptor in COORDINATOR_EA20_BINDINGS.items():
        require(record.get(field) == review.get(field) == descriptor, 'EA20 exact immutable descriptor mismatch: '+field)
        path = local_path(descriptor['path'], DOCS)
        require(sha(snap.read(path)) == descriptor['sha256'], 'EA20 immutable document bytes mismatch')
        documents[field] = snap.json(path)
    proposal, peer = documents['complete_chain_proposal'], documents['complete_chain_review']
    require(proposal.get('author_thread_id') == author and peer.get('reviewer_thread_id') == reviewer and
            peer.get('original_author_thread_id') == author and peer.get('proposal') == COORDINATOR_EA20_BINDINGS['complete_chain_proposal'],
            'EA20 immutable actual source authors mismatch')
    require(peer.get('status') == 'INDEPENDENT_WHOLE_CHAIN_REVIEW_ACCEPT_MAXIMUM_ONE_PENDING_FORMAL_PACKAGE' and
            peer.get('decision') == 'ACCEPT_ONE_RELATED_WHOLE_DIMENSION_EXPOSURE_NATIVE_HANDOFF_MECHANISM_WITH_EXPLICIT_LIMITS' and
            type(peer.get('maximum_whole_mechanisms_supported')) is int and peer['maximum_whole_mechanisms_supported'] == 1 and
            type(peer.get('formal_accepted_credit_applied')) is int and peer['formal_accepted_credit_applied'] == 0 and
            peer.get('formal_EA_id_assigned') is False and peer['main_actual_reading_scope'].get('all_range_text_read_by_main') is True,
            'EA20 actual independent whole-source recommendation missing')
    require(type(proposal.get('maximum_proposed_credit')) is int and proposal['maximum_proposed_credit'] == 1 and
            all(type(proposal.get(k)) is int and proposal[k] == 0 for k in ('accepted_credit','applied_credit','supporting_ranges_credit')),
            'EA20 original proposal credits invalid')
    require(record['repo'] == proposal['repo'] == 'AlexModGuy/AlexsMobs' and
            record['revision'] == proposal['source_commit'] == peer['source_pin_checks']['mod_commit'] == '09755dade2cfbdf14839e026d3af446f9d3ff843' and
            record['semantic_key'] == proposal['proposed_semantic_key'] == peer['semantic_key'] ==
            'dimension-exposure-driven-species-conversion-through-precommitted-native-handoff', 'EA20 fixed source/semantic mismatch')
    require(record['observation'] == review.get('observed_chain') == proposal['observed_complete_chain']+peer['main_findings'] and
            peer['limitations'] == proposal['limitations'] and record['limits'] == review.get('limits') ==
            proposal['limitations']+peer['mandatory_package_constraints'] and len(peer['mandatory_package_constraints']) == 5,
            'EA20 complete observations/constraints/limits mismatch')
    require(record['application'] == proposal['application'] and record['deduplication'] == proposal['deduplication'], 'EA20 application/deduplication mismatch')
    refs, formal, checks = proposal['mod_read_ranges'], record['chain'], review.get('source_checks')
    require(len(refs) == len(formal) == 8 and peer['main_actual_mod_read_ranges'] == refs and isinstance(checks,list) and len(checks) == 8,
            'EA20 complete8 mod consumer coverage missing')
    for index,(ref,e,check) in enumerate(zip(refs,formal,checks)):
        require(type(ref.get('index')) is int and ref['index'] == index and ref.get('actual_text_read') is True and
                type(ref.get('support_credit')) is int and ref['support_credit'] == 0, 'EA20 mod actual-read/support mismatch')
        src = local_path(ref['source_local'], ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs')
        raw = snap.read(src); lines = raw.decode().splitlines(keepends=True); lo,hi = ref['lines']
        require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines) and sha(raw) == ref['file_sha256'] and
                sha(''.join(lines[lo-1:hi]).encode()) == ref['raw_excerpt_sha256'], 'EA20 actual original mod/raw excerpt mismatch')
        require((e['path'],e['line'],e['end_line']) == (ref['source_path'],lo,hi) and e['repo'] == ref['repo'] == record['repo'] and
                e['revision'] == ref['revision'] == record['revision'] and e['url'] == ref['url'] and
                e['git_blob_sha1'] == ref['git_blob_sha1'] and e['source_sha256'] == sha(raw) and
                snap.read(local_path(e['source_local'],TOOLS/'sources')) == raw, 'EA20 exact formal/original mod mapping mismatch')
        for k in ('source_local','source_sha256','git_blob_sha1','revision','excerpt_sha256','url'):
            require(check.get(k) == e[k], 'EA20 mandatory actual source proof missing: '+k)
        proof = validate_source(e,snap)
        for field,pfield in [('source_metadata','source_metadata_sha256'),('tree_metadata','tree_metadata_sha256')]:
            original = local_path(ref[field], ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs')
            require(sha(snap.read(original)) == ref[pfield] == proof[pfield] and snap.read(original) ==
                    snap.read(local_path(e[field],TOOLS/'sources')), 'EA20 fixed original/formal metadata bytes mismatch')
    artifact = proposal['native_artifact']
    require(record.get('native_auxiliary_artifact') == peer['source_pin_checks']['native_artifact'] == artifact and
            record.get('native_auxiliary_ranges') == peer['main_actual_native_read_ranges'] == proposal['native_read_ranges'] and
            len(proposal['native_read_ranges']) == 22, 'EA20 complete22 raw native core coverage missing')
    archive_path = local_path(artifact['source_archive'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches')
    archive_raw = snap.read(archive_path)
    require(sha(archive_raw) == artifact['sha256'] == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0', 'EA20 actual native archive mismatch')
    native_base = local_path(artifact['extracted_source_root'],ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        identities = set()
        for index,ref in enumerate(proposal['native_read_ranges']):
            lo,hi = ref['lines']; src = local_path(ref['source_local'],native_base)
            require(src == (native_base/ref['entry']).resolve() and type(ref.get('index')) is int and ref['index'] == index and
                    ref.get('source_kind') == 'native_forge_archive' and ref.get('actual_text_read') is True and
                    ref.get('archive_entry_exact') is True and type(ref.get('support_credit')) is int and ref['support_credit'] == 0 and
                    ref['archive'] == artifact['source_archive'] and ref['archive_sha256'] == artifact['sha256'], 'EA20 native source/read/support identity mismatch')
            raw = snap.read(src); lines = raw.decode().splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines) and (ref['entry'],lo,hi) not in identities,
                    'EA20 invalid/duplicate native range')
            identities.add((ref['entry'],lo,hi))
            require(archive.read(ref['entry']) == raw and sha(raw) == ref['entry_sha256'] and
                    sha(''.join(lines[lo-1:hi]).encode()) == ref['raw_excerpt_sha256'], 'EA20 actual native entry/raw excerpt mismatch')
        required = {('net/minecraft/world/entity/Mob.java',1204,1249),
                    ('net/minecraft/world/level/entity/PersistentEntitySectionManager.java',1,109),
                    ('net/minecraft/world/entity/EntityType.java',524,526),
                    ('net/minecraft/server/level/ServerLevel.java',855,867)}
        require(required <= identities, 'EA20 native core consumers missing')
        reused = proposal['prior_native_complete_read_reused']
        require(record.get('reused_native_support') == peer['main_actual_reading_scope']['prior_PathfinderMob_read_reused'] == reused and
                reused.get('read_reused_not_reread') is True and reused.get('archive_entry_exact') is True and
                type(reused.get('support_credit')) is int and reused['support_credit'] == 0, 'EA20 reused parent reading binding mismatch')
        prior_path = local_path(reused['prior_review']['path'],DOCS)
        require(sha(snap.read(prior_path)) == reused['prior_review']['sha256'], 'EA20 prior actual parent review changed')
        raw = snap.read(native_base/reused['entry']); lo,hi = reused['lines']
        require(archive.read(reused['entry']) == raw and sha(raw) == reused['entry_sha256'] and
                sha(''.join(raw.decode().splitlines(keepends=True)[lo-1:hi]).encode()) == reused['raw_excerpt_sha256'], 'EA20 reused parent actual bytes mismatch')
        for ref in proposal['native_parent_symbol_inventory_support_only']:
            raw = snap.read(native_base/ref['entry'])
            require(archive.read(ref['entry']) == raw and sha(raw) == ref['entry_sha256'] and
                    ref.get('machine_inventory_not_full_text_semantic_review') is True and type(ref.get('support_credit')) is int and ref['support_credit'] == 0 and
                    all(raw.decode().count(k) == n for k,n in ref['exact_symbol_counts'].items()), 'EA20 original parent inventory changed')
        for ref in peer['parent_symbol_inventory_support_only']:
            raw = snap.read(native_base/ref['entry'])
            require(archive.read(ref['entry']) == raw and sha(raw) == ref['sha256'] and type(ref.get('support_credit')) is int and ref['support_credit'] == 0,
                    'EA20 coordinator parent inventory source mismatch')
    for ref in proposal['semantic_comparisons']:
        desc = ref['batch']; require(sha(snap.read(local_path(desc['path'],DOCS))) == desc['sha256'], 'EA20 original comparison batch changed')
    for ref in peer['prior_substantive_decisions_main_actually_read']:
        require(sha(snap.read(local_path(ref['batch'],DOCS))) == ref['batch_sha256'], 'EA20 independent comparison batch changed')
    return dict(proposal=COORDINATOR_EA20_BINDINGS['complete_chain_proposal'],review=COORDINATOR_EA20_BINDINGS['complete_chain_review'],
                mod_ranges_support0=8,native_ranges_support0=22,reused_parent_ranges_support0=1,mandatory_package_constraints=5,
                original_author_thread_id=author,actual_reviewer_thread_id=reviewer,native_gameplay_credit=0)

GENERAL_EA21_BINDINGS = {
    'complete_chain_proposal': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-raccoon-shoreline-food-proposal-20261103.json',
        'sha256': '77e580fa3cd2552e60d6d01015695edbf537ddd2635fba47efcd1cd4a3027a4c'},
    'complete_chain_review': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-raccoon-shoreline-food-review-20261103.json',
        'sha256': '1154467320e4374aaa269e1aad305c8925aeb268affaa6a293546980afc93f4a'},
}


def general_raccoon_context(review, record, snap, policy, identifier, role):
    """EA21 only: actual General review of coordinator-authored parameterized policy.

    The native/source inventory supports one whole mechanism at most. Exact local
    role bindings are not cryptographic authentication or runtime evidence.
    """
    same = lambda left,right: json.dumps(left,sort_keys=True,separators=(',',':')) == json.dumps(right,sort_keys=True,separators=(',',':'))
    author = '01a16364-cac0-7ca2-a042-a5312781ca34'
    reviewer = '01a12516-2eaf-73e2-b615-20f8b422158c'
    require(identifier == 'EA-0021' and role == 'general' and identifier in policy['allowed_ids'],
            'EA21 requires exactly authorized General reviewer role')
    require(review.get('reviewer_thread_id') == policy['thread_id'] == reviewer and
            record.get('author_thread_id') == policy['proposal_author_thread_id'] == author and
            record.get('independent_reviewer_thread_id') == reviewer and author != reviewer,
            'EA21 actual independent authors mismatch')
    require(record.get('general_context_schema') == 'raccoon-held-food-shoreline-v1', 'EA21 context schema mismatch')
    for key, expected in [('evidence_scope', 'parameterized_source_policy_only'),
                          ('resource_membership_state', 'same_pin_tree_only_raw_missing')]:
        require(record.get(key) == review.get(key) == expected, 'EA21 symbolic resource/scope boundary missing')
    require(all(type(record.get(k)) is int and record[k] == n for k,n in
                [('proposed_credit',1),('accepted_credit',0),('supporting_ranges_credit',0),
                 ('native_gameplay_credit',0),('runtime_material_payment_credit',0)]),
            'EA21 exact proposal credit types required')
    require(all(type(review.get(k)) is int and review[k] == 0 for k in
                ('supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit')),
            'EA21 support/native/material credits must be integer0')
    require(all(k not in obj for obj in (review,record) for k in ('candidate_id','original_candidate_id')),
            'EA21 invented candidate identity rejected')
    require(review.get('reviewed_batch') == str((DOCS/'batch-016.json').relative_to(ROOT)), 'EA21 exact formal batch required')
    documents = {}
    for field, descriptor in GENERAL_EA21_BINDINGS.items():
        require(record.get(field) == review.get(field) == descriptor, 'EA21 immutable descriptor mismatch: '+field)
        path = local_path(descriptor['path'], DOCS)
        require(sha(snap.read(path)) == descriptor['sha256'], 'EA21 immutable source review bytes mismatch')
        documents[field] = snap.json(path)
    proposal, peer = documents['complete_chain_proposal'], documents['complete_chain_review']
    require(proposal.get('author_thread') == author and peer.get('original_author_thread_id') == author and
            peer.get('reviewer_thread_id') == reviewer and peer.get('proposal') == GENERAL_EA21_BINDINGS['complete_chain_proposal'],
            'EA21 immutable actual source authors mismatch')
    require(proposal.get('status') == 'WHOLE_MECHANISM_PROPOSAL_PENDING_INDEPENDENT_REVIEW_RESOURCE_MEMBERSHIP_LIMIT_RETAINED' and
            type(proposal.get('maximum_proposed_whole_mechanisms')) is int and proposal['maximum_proposed_whole_mechanisms'] == 1 and
            type(proposal.get('research_credit_applied')) is int and proposal['research_credit_applied'] == 0 and
            proposal.get('formal_id_assigned') is False,
            'EA21 original source proposal recommendation missing')
    require(peer.get('status') == 'INDEPENDENT_WHOLE_SOURCE_POLICY_REVIEW_ACCEPT_MAXIMUM_ONE_WITH_SYMBOLIC_TAG_LIMIT_PENDING_FORMAL_PACKAGE' and
            peer.get('decision') == 'ACCEPT_AT_MOST_ONE_COMPLETE_RELATED_SOURCE_POLICY_WITH_EXPLICIT_LIMITS' and
            type(peer.get('maximum_whole_mechanisms_supported')) is int and peer['maximum_whole_mechanisms_supported'] == 1 and
            all(type(peer.get(k)) is int and peer[k] == 0 for k in ('accepted_credit','applied_credit','supporting_ranges_credit')) and
            peer.get('formal_EA_id_assigned') is False and peer['scope'].get('source_text_actually_read_not_machine_scan') is True,
            'EA21 actual independent full-policy review recommendation missing')
    require(record.get('repo') == 'AlexModGuy/AlexsMobs' and
            record.get('revision') == proposal['source_pin_checks']['mod_commit'] == peer['source_pin_checks']['mod_commit'] ==
            '09755dade2cfbdf14839e026d3af446f9d3ff843' and
            record.get('semantic_key') == proposal['semantic_key'] == peer['semantic_key'] ==
            'shoreline-mediated-held-food-processing-with-delayed-thrower-conditioned-taming',
            'EA21 fixed source/semantic identity mismatch')
    require(record.get('observation') == review.get('observed_chain') == proposal['full_chain_findings']+peer['independent_findings'] and
            record.get('limits') == review.get('limits') == peer['limits']+peer['mandatory_package_constraints'] and
            len(peer['mandatory_package_constraints']) == 8 and peer['limits'][:len(proposal['remaining_gaps'])] == proposal['remaining_gaps'],
            'EA21 full findings/eight constraints/resource limits missing')
    require(record.get('application') == peer['application'] and record.get('deduplication') == peer['deduplication'] and
            record.get('proposal_dedup_limit') == proposal['dedup_limit'], 'EA21 whole-policy application/dedup mismatch')
    refs, actual, formal = proposal['actual_mod_read_ranges'], peer['actual_independent_mod_read_ranges'], record.get('chain')
    require(isinstance(formal,list) and len(refs) == len(actual) == len(formal) == 17 and
            same(record.get('original_mod_ranges'),refs) and same(record.get('independent_mod_ranges'),actual),
            'EA21 complete17 mod consumers missing')
    original_base = ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs'
    for field in ('source_metadata','tree_metadata'):
        descriptor = proposal['source_pin_checks'][field]
        require(peer['source_pin_checks'][field] == descriptor and
                sha(snap.read(local_path(descriptor['path'],original_base))) == descriptor['sha256'],
                'EA21 original fixed metadata bytes mismatch')
    mod_identities = set()
    for ref, check, e in zip(refs,actual,formal):
        for field in ref:
            require(check.get(field) == ref[field], 'EA21 independent original mod binding mismatch: '+field)
        require(ref.get('actual_text_read') is True and check.get('actual_independent_text_read') is True and
                all(check.get(k) is True for k in ('source_sha256_match','git_blob_match','fixed_revision_match','raw_excerpt_exact')) and
                type(ref.get('credit')) is int and ref['credit'] == 0 and type(check.get('support_credit')) is int and check['support_credit'] == 0,
                'EA21 independent actual mod read/support mismatch')
        src = local_path(ref['source_local'], original_base); raw = snap.read(src)
        lines = raw.decode().splitlines(keepends=True); lo,hi = ref['lines']; identity = (ref['source_path'],lo,hi)
        require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines) and identity not in mod_identities,
                'EA21 invalid/duplicate mod range')
        mod_identities.add(identity)
        require(sha(raw) == ref['file_sha256'] and sha(''.join(lines[lo-1:hi]).encode()) == ref['raw_excerpt_sha256'] and
                (not ref['full_file'] or (lo,hi) == (1,len(lines))), 'EA21 actual mod/raw whole range mismatch')
        require((e['path'],e['line'],e['end_line']) == identity and e['repo'] == record['repo'] and
                e['revision'] == ref['revision'] == record['revision'] and e['source_sha256'] == sha(raw) and
                e['git_blob_sha1'] == ref['git_blob_sha1'] and e['url'] == check['url'] and
                snap.read(local_path(e['source_local'],TOOLS/'sources')) == raw, 'EA21 formal/original source mapping mismatch')
        proof = validate_source(e,snap)
        for field in ('source_metadata','tree_metadata'):
            descriptor = proposal['source_pin_checks'][field]
            require(proof[field+'_sha256'] == descriptor['sha256'] and
                    snap.read(local_path(e[field],TOOLS/'sources')) == snap.read(local_path(descriptor['path'],original_base)),
                    'EA21 original/formal metadata mismatch')
    artifact = proposal['source_pin_checks']['native_artifact']
    require(same(record.get('native_auxiliary_artifact'),artifact) and same(peer['source_pin_checks']['native_artifact'],artifact) and
            same(record.get('native_auxiliary_ranges'),proposal['actual_native_read_ranges']) and
            same(record.get('native_independent_ranges'),peer['actual_independent_native_read_ranges']) and
            same(record.get('native_additional_ranges'),peer['additional_actual_native_support_ranges']) and
            len(record['native_auxiliary_ranges']) == len(record['native_independent_ranges']) == 22 and
            len(record['native_additional_ranges']) == 9, 'EA21 complete22 original plus9 independent native consumers missing')
    archive_raw = snap.read(local_path(artifact['source_archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive_raw) == artifact['sha256'] == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0',
            'EA21 fixed actual native archive mismatch')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        identities = set()
        for ref,check in zip(record['native_auxiliary_ranges'],record['native_independent_ranges']):
            for field in ref:
                require(check.get(field) == ref[field], 'EA21 actual independent native binding mismatch: '+field)
            require(ref.get('actual_text_read') is True and check.get('actual_independent_text_read') is True and
                    check.get('archive_entry_exact') is True and check.get('raw_excerpt_exact') is True and
                    type(ref.get('credit')) is int and ref['credit'] == 0 and
                    type(check.get('support_credit')) is int and check['support_credit'] == 0,
                    'EA21 actual independent native read/support mismatch')
        for ref in record['native_auxiliary_ranges']+record['native_additional_ranges']:
            require(ref['archive'] == artifact['source_archive'] and ref['archive_sha256'] == artifact['sha256'],
                    'EA21 native archive reference mismatch')
            raw = archive.read(ref['entry']); lines = raw.decode().splitlines(keepends=True); lo,hi = ref['lines']
            identity = (ref['entry'],lo,hi)
            require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines) and identity not in identities,
                    'EA21 invalid/duplicate native range')
            identities.add(identity)
            require(sha(raw) == ref['entry_sha256'] and sha(''.join(lines[lo-1:hi]).encode()) == ref['raw_excerpt_sha256'] and
                    (not ref['full_file'] or (lo,hi) == (1,len(lines))), 'EA21 actual native raw range mismatch')
        for ref in record['native_additional_ranges']:
            require(ref.get('actual_independent_text_read') is True and ref.get('archive_entry_exact') is True and
                    type(ref.get('support_credit')) is int and ref['support_credit'] == 0,
                    'EA21 added native independent read/support mismatch')
        core = {('net/minecraft/world/entity/item/ItemEntity.java',30,96),
                ('net/minecraft/world/entity/Mob.java',742,780),
                ('net/minecraft/world/entity/TamableAnimal.java',1,207),
                ('net/minecraft/world/entity/OwnableEntity.java',1,18),
                ('net/minecraft/world/entity/ai/goal/GoalSelector.java',1,158),
                ('net/minecraft/world/entity/ai/goal/WrappedGoal.java',1,89)}
        require(core <= identities, 'EA21 native owner/AI/thrower core missing')
    boundary = peer['resource_membership_boundary']
    require(same(record.get('resource_membership_boundary'),boundary) and same(review.get('resource_membership_boundary'),boundary) and
            boundary.get('source_policy_scope_blocked') is False and boundary.get('concrete_item_or_runtime_reachability_scope_blocked') is True and
            len(boundary['same_pin_tree_paths_without_raw_contents']) == 5, 'EA21 symbolic resource boundary rebound')
    tree = snap.json(local_path(proposal['source_pin_checks']['tree_metadata']['path'],original_base))
    tree_entries = {e['path']:e for e in tree['tree']}
    for ref in boundary['same_pin_tree_paths_without_raw_contents']:
        require(ref.get('resource_contents_read') is False and ref.get('tag_members_inferred') is False and
                type(ref.get('support_credit')) is int and ref['support_credit'] == 0 and
                tree_entries[ref['source_path']]['sha'] == ref['tree_blob_sha1_metadata_only'],
                'EA21 tree-only metadata cannot confer tag member credit')
    require(same(record.get('closest_prior_decisions'),peer['closest_prior_substantive_decisions_actually_read']) and
            same(record.get('all19_semantic_context'),peer['all19_actual_accepted_semantic_labels_compared']),
            'EA21 complete prior semantic context rebound')
    seen = set()
    for ref in record['closest_prior_decisions']:
        path = local_path(ref['batch']['path'],DOCS); raw = snap.read(path)
        require(sha(raw) == ref['batch']['sha256'], 'EA21 prior decision batch changed')
        found = [x for x in snap.json(path)['records'] if x.get('id') == ref['id']]
        require(len(found) == 1 and found[0]['semantic_key'] == ref['semantic_key'] and
                sha(json.dumps(found[0],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()) == ref['record_canonical_sha256'],
                'EA21 substantive prior decision record changed')
        seen.add(ref['id'])
    require('EA-0020' in seen and len(seen) == 7, 'EA21 actual EA20 whole-policy comparison missing')
    for descriptor in peer['prior_actual_independent_source_judgments_reused_not_reread']:
        require(sha(snap.read(local_path(descriptor['path'],DOCS))) == descriptor['sha256'], 'EA21 prior actual judgment changed')
    return dict(proposal=GENERAL_EA21_BINDINGS['complete_chain_proposal'],review=GENERAL_EA21_BINDINGS['complete_chain_review'],
                mod_ranges_support0=17,native_original_ranges_support0=22,native_added_ranges_support0=9,
                mandatory_package_constraints=8,actual_original_author_thread_id=author,actual_reviewer_thread_id=reviewer,
                evidence_scope='parameterized_source_policy_only',concrete_tag_membership_credit=0,
                native_gameplay_credit=0,runtime_material_payment_credit=0)


GENERAL_EA22_BINDINGS = {
    'complete_chain_proposal': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-hummingbird-feeder-pollination-proposal-20261103.json',
        'sha256': 'ec8c16f3739e6c2e9ea9f7174f2f253b6b51e5d298a11432c4a891b03aa07df0'},
    'complete_chain_review': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-hummingbird-feeder-pollination-review-20261103.json',
        'sha256': '5099461f26d780fd7688ad726b9cad783c8b43160e1ee7b40327028261c7b3cf'},
    'complete_chain_closure': {
        'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-hummingbird-independent-review-closure-20261103.json',
        'sha256': 'de10308f64ad8d3fdfb94a79f6950d70e0d4f451fd32cc4e534bddd130204714'},
}


def general_hummingbird_context(review, record, snap, policy, identifier, role):
    """EA22 only: frozen actual whole-policy review; no execution or gameplay claim.

    Original 38 excerpts append LF; formal source excerpts do not. Raw keepends
    hashes are recomputed separately, including the five documented EOF cases.
    Exact local roles bind authorization, not remote cryptographic identity.
    """
    same = lambda a,b: json.dumps(a,sort_keys=True,separators=(',',':')) == json.dumps(b,sort_keys=True,separators=(',',':'))
    zero = lambda obj,keys: all(type(obj.get(k)) is int and obj[k] == 0 for k in keys)
    author, reviewer = '01a16364-cac0-7ca2-a042-a5312781ca34', '01a12516-2eaf-73e2-b615-20f8b422158c'
    require(identifier == 'EA-0022' and role == 'general' and identifier in policy['allowed_ids'], 'EA22 exactly authorized General role required')
    require(review.get('reviewer_thread_id') == policy['thread_id'] == reviewer and
            record.get('author_thread_id') == policy['proposal_author_thread_id'] == author and
            record.get('independent_reviewer_thread_id') == reviewer and author != reviewer, 'EA22 actual author/reviewer mismatch')
    require(record.get('general_context_schema') == 'hummingbird-facility-shared-crop-service-v1', 'EA22 context schema mismatch')
    for key,value in [('evidence_scope','parameterized_source_policy_only'), ('resource_membership_state','same_pin_tree_only_raw_missing_with_code_tree_spelling_mismatch')]:
        require(record.get(key) == review.get(key) == value, 'EA22 source/resource scope mismatch')
    zero_keys = ('supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','crop_growth_or_harvest_acceptance')
    require(zero(record,zero_keys+('accepted_credit',)) and type(record.get('proposed_credit')) is int and record['proposed_credit'] == 1 and
            zero(review,zero_keys), 'EA22 exact integer source-only credit fields required')
    require(all(k not in obj for obj in (record,review) for k in ('candidate_id','original_candidate_id')), 'EA22 invented candidate identity rejected')
    require(review.get('reviewed_batch') == str((DOCS/'batch-017.json').relative_to(ROOT)), 'EA22 exact batch required')
    documents = {}
    for key,descriptor in GENERAL_EA22_BINDINGS.items():
        require(same(record.get(key),descriptor) and same(review.get(key),descriptor), 'EA22 immutable descriptor mismatch: '+key)
        path = local_path(descriptor['path'],DOCS)
        require(sha(snap.read(path)) == descriptor['sha256'], 'EA22 actual immutable evidence bytes mismatch: '+key)
        documents[key] = snap.json(path)
    q,p,c = (documents[k] for k in ('complete_chain_proposal','complete_chain_review','complete_chain_closure'))
    require(q['author_thread'] == author and p['original_author_thread_id'] == author and p['reviewer_thread_id'] == reviewer and
            same(p['proposal'],GENERAL_EA22_BINDINGS['complete_chain_proposal']) and
            same(c['proposal'],GENERAL_EA22_BINDINGS['complete_chain_proposal']) and
            same(c['actual_independent_review'],GENERAL_EA22_BINDINGS['complete_chain_review']), 'EA22 actual source-role chain mismatch')
    require(q['status'] == 'PENDING_REAL_INDEPENDENT_REVIEW_NO_CREDIT' and q['formal_id_assigned'] is False and
            type(q['maximum_proposed_whole_mechanisms']) is int and q['maximum_proposed_whole_mechanisms'] == 1 and
            zero(q,('research_credit_applied',)), 'EA22 original proposal scope mismatch')
    require(p['status'] == 'INDEPENDENT_WHOLE_SOURCE_POLICY_REVIEW_ACCEPT_MAXIMUM_ONE_WITH_RESOURCE_RETRY_AND_NORMALIZATION_LIMITS_ZERO_APPLIED' and
            p['decision'] == 'ACCEPT_AT_MOST_ONE_COMPLETE_RELATED_PARAMETERIZED_SOURCE_POLICY_WITH_EXPLICIT_LIMITS' and
            type(p['maximum_whole_mechanisms_supported']) is int and p['maximum_whole_mechanisms_supported'] == 1 and
            p['formal_EA_id_assigned'] is False and zero(p,('supporting_ranges_credit','native_birth_kill_pickup_credit','runtime_material_payment_credit',
            'crop_growth_or_harvest_acceptance','accepted_credit','applied_credit')), 'EA22 actual independent recommendation mismatch')
    require(c['status'] == 'MAIN_REVIEW_SUPPORTS_MAXIMUM_ONE_PARAMETERIZED_SOURCE_POLICY_PENDING_FORMAL_PACKAGE_AND_REAL_RECEIPT' and
            c['formal_id_assigned'] is False and type(c['maximum_whole_mechanisms_supported']) is int and
            c['maximum_whole_mechanisms_supported'] == 1 and zero(c,('credit_applied','native_gameplay_credit','material_payment_crop_growth_harvest_credit')),
            'EA22 main independent-review closure mismatch')
    semantic = 'player-filled-poi-facility-and-flower-visits-share-persistent-crop-service-counter-with-uncommitted-growth'
    require(record.get('semantic_key') == q['semantic_key'] == p['semantic_key'] == semantic and
            record.get('repo') == 'AlexModGuy/AlexsMobs' and record.get('revision') == q['source_pin_checks']['mod_commit'] ==
            p['source_pin_checks']['mod_commit'] == '09755dade2cfbdf14839e026d3af446f9d3ff843', 'EA22 semantic/revision mismatch')
    findings, limits = q['full_chain_findings']+p['independent_findings'], q.get('remaining_gaps',[])+p['limits']+p['mandatory_package_constraints']
    require(same(record.get('observation'),findings) and same(review.get('observed_chain'),findings) and
            same(record.get('limits'),limits) and same(review.get('limits'),limits) and len(p['mandatory_package_constraints']) == 9 and
            same(c['full_nine_constraints_must_be_preserved'],p['mandatory_package_constraints']), 'EA22 full findings/nine constraints missing')
    require(same(record.get('application'),p['application']) and same(record.get('deduplication'),p['closest_substantive_decisions_compared']) and
            record.get('proposal_dedup_limit') == q['dedup_limit'], 'EA22 whole-policy application/dedup mismatch')
    bindings = {'original_mod_ranges':q['actual_mod_read_ranges'], 'independent_mod_ranges':p['actual_mod_checks'],
                'native_auxiliary_ranges':q['actual_native_read_ranges'], 'native_independent_ranges':p['actual_native_checks'],
                'native_additional_ranges':p['additional_native_support_read_now'], 'resource_membership_boundary':p['resource_boundary'],
                'resource_boundary_decision':p['resource_boundary_blocking_decision'], 'excerpt_normalization_corrections':p['excerpt_normalization_corrections'],
                'closest_prior_decisions':p['closest_substantive_decisions_compared'], 'prior_raccoon_whole_review':p['prior_raccoon_whole_independent_read_reused'],
                'prior_raccoon_formal_receipt':p['actual_raccoon_formal_receipt_observed_not_aggregation_claim'],
                'other_semantic_context':p['other_formal_semantic_labels_only_not_renewed_source_reads'],
                'native_auxiliary_artifact':q['source_pin_checks']['native_artifact']}
    for key,expected in bindings.items():
        require(same(record.get(key),expected), 'EA22 frozen complete context rebound: '+key)
    for key in ('resource_membership_boundary','resource_boundary_decision','excerpt_normalization_corrections','excerpt_byte_conventions'):
        require(same(review.get(key),record.get(key)), 'EA22 real receipt boundary mismatch: '+key)
    conventions = {'original_proposal':'UTF8 splitlines, join LF, append exactly one terminal LF',
                   'raw_excerpt':'raw bytes splitlines(keepends=True), exact selected lines',
                   'formal_source_excerpt':'UTF8 splitlines, join LF, no added terminal LF'}
    require(same(record.get('excerpt_byte_conventions'),conventions) and same(c['normalization_correction_required'],p['excerpt_normalization_corrections']),
            'EA22 explicit raw/original/formal excerpt conventions required')
    original_base = ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs'
    for key in ('source_metadata','tree_metadata'):
        d = q['source_pin_checks'][key]
        require(same(p['source_pin_checks'][key],d) and sha(snap.read(local_path(d['path'],original_base))) == d['sha256'], 'EA22 original metadata mismatch')
    corrections, seen = [], set()
    def check_span(raw,ref,check,kind,index):
        lo,hi = ref['line'],ref['end_line']; lines = raw.decode().splitlines(); identity = (kind,ref['path'],lo,hi)
        require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines) and identity not in seen, 'EA22 invalid/duplicate span')
        seen.add(identity)
        raw_excerpt = b''.join(raw.splitlines(keepends=True)[lo-1:hi]); normalized = ('\n'.join(lines[lo-1:hi])+'\n').encode()
        require(sha(raw) == ref['source_sha256'] == check['source_sha256'] and sha(raw_excerpt) == check['raw_excerpt_sha256'] and
                sha(normalized) == ref['excerpt_sha256'] == check['proposal_excerpt_sha256'] and
                check['proposal_excerpt_algorithm'] == conventions['original_proposal'] and check['proposal_excerpt_exact_under_declared_algorithm'] is True and
                check['raw_equals_original_proposal_excerpt'] is (raw_excerpt == normalized) and check['index'] == index,
                'EA22 raw/original normalized excerpt mismatch')
        require(all(same(check.get(k),value) for k,value in ref.items()), 'EA22 original/independent span binding mismatch')
        require(check['source_sha256_match'] is True and type(check['support_credit']) is int and check['support_credit'] == 0, 'EA22 actual source check/support mismatch')
        if raw_excerpt != normalized:
            corrections.append(dict(kind=kind,path=ref['path'],line=lo,end_line=hi,actual_file_sha256=sha(raw),actual_raw_excerpt_sha256=sha(raw_excerpt),
                                    original_normalized_excerpt_sha256=sha(normalized),actual_file_has_terminal_LF=raw.endswith(b'\n'),
                                    normalization_algorithm=conventions['original_proposal'],raw_original_excerpt_match=False,normalized_original_excerpt_match=True,support_credit=0))
    refs, checks, formal = record['original_mod_ranges'],record['independent_mod_ranges'],record.get('chain')
    require(isinstance(formal,list) and len(refs) == len(checks) == len(formal) == 17, 'EA22 complete17 mod chain required')
    for index,(ref,check,e) in enumerate(zip(refs,checks,formal)):
        raw = snap.read(local_path(ref['local_path'],original_base)); check_span(raw,ref,check,'mod',index)
        require(check['actual_independent_text_read_now'] is True and check['git_blob_tree_match'] is True and check['fixed_revision_match'] is True,
                'EA22 actual mod reading/check missing')
        require((e['path'],e['line'],e['end_line']) == (ref['path'],ref['line'],ref['end_line']) and
                e['revision'] == ref['revision'] == record['revision'] and e['git_blob_sha1'] == ref['git_blob_sha1'] and
                snap.read(local_path(e['source_local'],TOOLS/'sources')) == raw, 'EA22 formal/original mod mapping mismatch')
        proof = validate_source(e,snap)
        for key in ('source_metadata','tree_metadata'):
            d = q['source_pin_checks'][key]
            require(proof[key+'_sha256'] == d['sha256'] and snap.read(local_path(e[key],TOOLS/'sources')) == snap.read(local_path(d['path'],original_base)),
                    'EA22 formal/original metadata mismatch')
    artifact = record['native_auxiliary_artifact']; archive_raw = snap.read(local_path(artifact['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive_raw) == artifact['sha256'] == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0' and
            len(record['native_auxiliary_ranges']) == len(record['native_independent_ranges']) == 21 and len(record['native_additional_ranges']) == 4,
            'EA22 fixed native archive/21plus4 inventory mismatch')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        native_base = ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/minecraft-forge-1.20.1-47.4.10'
        for index,(ref,check) in enumerate(zip(record['native_auxiliary_ranges'],record['native_independent_ranges'])):
            raw = archive.read(ref['path']); require(snap.read(local_path(ref['local_path'],native_base)) == raw and check['archive_entry_exact'] is True, 'EA22 native local/archive mismatch')
            check_span(raw,ref,check,'native',index)
            if check['read_reused_not_reread']:
                d = check['prior_actual_read']; require(sha(snap.read(local_path(d['path'],DOCS))) == d['sha256'], 'EA22 prior actual native reading changed')
        for ref in record['native_additional_ranges']:
            raw = archive.read(ref['entry']); lo,hi = ref['lines']; lines = raw.splitlines(keepends=True)
            require(ref['archive'] == artifact['path'] and ref['archive_sha256'] == artifact['sha256'] and sha(raw) == ref['entry_sha256'] and
                    type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines) and
                    sha(b''.join(lines[lo-1:hi])) == ref['raw_excerpt_sha256'] and ref['actual_independent_text_read_now'] is True and
                    ref['archive_entry_exact'] is True and type(ref['support_credit']) is int and ref['support_credit'] == 0 and
                    (not ref['full_file'] or (lo,hi) == (1,len(lines))), 'EA22 added actual native support mismatch')
    require(len(corrections) == 5 and same(corrections,record['excerpt_normalization_corrections']), 'EA22 exact five EOF normalization differences required')
    boundary = record['resource_membership_boundary']; tree = snap.json(local_path(q['source_pin_checks']['tree_metadata']['path'],original_base))
    entries = {e['path']:e for e in tree['tree']}; require(len(boundary) == 5, 'EA22 five resource boundaries required')
    for ref in boundary:
        found = entries.get(ref['path'])
        require(ref['resource_members_read'] is False and ref['raw_in_selected_root'] is False and ref['in_fixed_tree'] is (found is not None) and
                ref['tree_blob_sha1'] == (found['sha'] if found else None), 'EA22 tree metadata is not raw resource contents')
    decision = record['resource_boundary_decision']
    require(decision['parameterized_source_policy_reference_blocked'] is False and
            decision['default_concrete_inputs_loaded_tag_reachability_payment_growth_and_harvest_receipt_blocked'] is True and
            decision['raw_resources_silently_fetched_or_fixed'] is False, 'EA22 concrete gameplay boundary missing')
    descriptors = [ref['source_decision'] for ref in record['closest_prior_decisions']]+[record['prior_raccoon_whole_review'],record['prior_raccoon_formal_receipt']]
    for descriptor in descriptors:
        require(sha(snap.read(local_path(descriptor['path'],DOCS))) == descriptor['sha256'], 'EA22 substantive prior judgment changed')
    return dict(**GENERAL_EA22_BINDINGS,mod_ranges_support0=17,native_original_ranges_support0=21,native_added_ranges_support0=4,
                mandatory_package_constraints=9,explicit_EOF_normalization_corrections=5,actual_original_author_thread_id=author,actual_reviewer_thread_id=reviewer,
                evidence_scope='parameterized_source_policy_only',concrete_tag_membership_credit=0,native_gameplay_credit=0,runtime_material_payment_credit=0,
                crop_growth_or_harvest_acceptance=0)


ACTOR_SERVICE_SPECS = {
    'EA-0023': {
        'schema': 'platypus-charged-substrate-service-v1',
        'slug': 'platypus-charged-excavation',
        'closure_slug': 'platypus',
        'hashes': ('35dc3f5eb981642b97d87e1083bdced72029d35bd508177011c4f4fabb7c96f8',
                   '0583f9581d919b69715cc97b6e3cdf8aa74187cfd984973a4bb065bb43bbb3a1',
                   '7df89d955c9cb92a5b77092c112889358dadce66ac2f62f859b50baa85ed9c61'),
        'counts': (14, 19, 0, 10, 6),
    },
    'EA-0024': {
        'schema': 'toucan-retained-block-dispersal-service-v1',
        'slug': 'toucan-block-dispersal',
        'closure_slug': 'toucan',
        'hashes': ('cbd7bab14ef8dfe4a458cfbdada4c991478961c8719abe7af07da7128314b62a',
                   '9c3acf53785166174854994c123f61a06c2ccda8b0f5581a4986f34fa305190f',
                   '7ba4712c2f5473e524224de0dbdaf1a34974b2aa826a6a6aa02e3d146749269d'),
        'counts': (7, 16, 1, 9, 3),
    },
}
ACTOR_SERVICE_PROVENANCE = 'local cached official-repo identity and fixed recursive Git tree; no fresh online verification'


def actor_service_bindings(identifier):
    spec = ACTOR_SERVICE_SPECS[identifier]
    names = ('coordinator-'+spec['slug']+'-proposal-20261103.json',
             'independent-'+spec['slug']+'-review-20261103.json',
             'coordinator-'+spec['closure_slug']+'-independent-review-closure-20261103.json')
    return {key: {'path': str((DOCS/name).relative_to(ROOT)), 'sha256': digest}
            for key, name, digest in zip(('complete_chain_proposal', 'complete_chain_review', 'complete_chain_closure'), names, spec['hashes'])}


def actor_service_fields(q, p, c, identifier):
    """Exact substantive context, including mandatory limitations; no source copy."""
    platypus = identifier == 'EA-0023'
    return dict(
        semantic_key=q['semantic_key'], general_context_schema=ACTOR_SERVICE_SPECS[identifier]['schema'],
        evidence_scope='parameterized_source_policy_only', resource_membership_state='fixed_tree_only_raw_missing_no_loaded_membership',
        author_thread_id='01a16364-cac0-7ca2-a042-a5312781ca34', independent_reviewer_thread_id='01a12516-2eaf-73e2-b615-20f8b422158c',
        observation=q['full_chain_findings']+p['independent_findings'], limits=q['remaining_gaps']+p['limits']+p['mandatory_package_constraints'],
        application=p['application'], deduplication=p['semantic_deduplication'] if platypus else p['deduplication'],
        proposal_dedup_limit=q['dedup_limit'], original_mod_ranges=q['actual_mod_read_ranges'],
        independent_mod_ranges=p['actual_independent_mod_read_ranges'],
        native_auxiliary_artifact=q['source_pin_checks']['native_artifact'], native_auxiliary_ranges=q['actual_native_read_ranges'],
        native_independent_ranges=p['actual_independent_native_read_ranges'], native_additional_ranges=p.get('additional_actual_native_support_ranges', []),
        resource_membership_boundary=p['resource_boundary'], resource_boundary_decision=p['resource_boundary_blocking_decision'],
        mandatory_package_constraints=p['mandatory_package_constraints'],
        main_closure_constraints=c['must_preserve'] if platypus else c['mandatory_package_constraints'],
        closest_prior_comparisons=p['closest_substantive_comparisons'] if platypus else p['closest_prior_whole_mechanism_comparison'],
        prior_actual_whole_judgments=p['prior_actual_source_judgments_reused_not_reread'] if platypus else p['prior_actual_whole_judgments_reused'],
        other_semantic_context=p['all20_accepted_semantic_labels_only_screened'] if platypus else p['all_current_formal_semantic_labels_only_screened'],
        excerpt_byte_conventions={'original_and_independent': 'raw UTF8 splitlines(keepends=True) slice; no synthetic LF',
                                  'formal_source_excerpt': 'UTF8 splitlines, join LF, no added terminal LF'},
        supporting_ranges_credit=0, native_gameplay_credit=0, runtime_material_payment_credit=0,
        crop_growth_or_harvest_acceptance=0, global_novelty_credit=0, new_migration_credit=0,
        **actor_service_bindings(identifier))


def general_actor_service_context(review, record, snap, policy, identifier, role):
    """Only two frozen, genuinely reviewed actor-service policies, at most one each.

    This extends neither old role scopes nor candidate authorization. Native and
    resource data are inspected as bytes. It does not run upstream code.
    """
    same = lambda a, b: json.dumps(a, sort_keys=True, separators=(',', ':')) == json.dumps(b, sort_keys=True, separators=(',', ':'))
    zero = lambda obj, keys: all(type(obj.get(k)) is int and obj[k] == 0 for k in keys)
    author, reviewer = '01a16364-cac0-7ca2-a042-a5312781ca34', '01a12516-2eaf-73e2-b615-20f8b422158c'
    require(identifier in ACTOR_SERVICE_SPECS and role == 'general' and identifier in policy['allowed_ids'], 'actor service exact General scope required')
    require(review.get('reviewer_thread_id') == policy['thread_id'] == reviewer and author == policy['proposal_author_thread_id'] and author != reviewer,
            'actor service true independent reviewer required')
    require(review.get('reviewed_batch') == str((DOCS/'batch-018.json').relative_to(ROOT)), 'actor service exact batch required')
    bindings = actor_service_bindings(identifier)
    documents = {}
    for key, descriptor in bindings.items():
        require(same(record.get(key), descriptor) and same(review.get(key), descriptor), 'actor service immutable descriptor mismatch: '+key)
        path = local_path(descriptor['path'], DOCS)
        require(sha(snap.read(path)) == descriptor['sha256'], 'actor service actual proposal/review/closure bytes changed: '+key)
        documents[key] = snap.json(path)
    q, p, c = (documents[k] for k in ('complete_chain_proposal', 'complete_chain_review', 'complete_chain_closure'))
    require(q['author_thread'] == p['original_author_thread_id'] == author and p['reviewer_thread_id'] == reviewer and
            same(p['proposal'], bindings['complete_chain_proposal']) and same(c['proposal'], bindings['complete_chain_proposal']) and
            all(c['independent_review'].get(k) == v for k, v in bindings['complete_chain_review'].items()), 'actor service actual source author/reviewer closure mismatch')
    require(type(q['maximum_proposed_whole_mechanisms']) is int and q['maximum_proposed_whole_mechanisms'] == 1 and
            type(p['maximum_whole_mechanisms_supported']) is int and p['maximum_whole_mechanisms_supported'] == 1 and
            zero(q, ('research_credit_applied',)) and zero(p, ('accepted_credit', 'applied_credit', 'supporting_ranges_credit',
            'native_birth_kill_pickup_credit', 'runtime_material_payment_credit')), 'actor service original recommendation scope mismatch')
    require(p['formal_EA_id_assigned'] is None and c['formal_EA_id_assigned'] is None and
            p['evidence_scope'] == 'parameterized_source_policy_only', 'actor service preformal scope must remain explicit')
    if identifier == 'EA-0023':
        require(c['decision'] == 'ACCEPT_INDEPENDENT_SCOPE_AND_LIMITS_MAX_ONE_PENDING_FORMAL_PACKAGE' and
                type(c['maximum_whole_mechanisms']) is int and c['maximum_whole_mechanisms'] == 1 and
                zero(c, ('formal_research_credit_applied',)), 'Platypus main closure mismatch')
    else:
        require(c['status'] == 'INDEPENDENT_SOURCE_REVIEW_CLOSED_MAX_ONE_PARAMETERIZED_POLICY_PENDING_FORMAL_RECEIPT' and
                c['author_thread_id'] == author and c['reviewer_thread_id'] == reviewer and
                type(c['maximum_whole_mechanisms_supported']) is int and c['maximum_whole_mechanisms_supported'] == 1 and
                zero(c, ('applied_credit',)), 'Toucan main closure mismatch')
    expected = actor_service_fields(q, p, c, identifier)
    for key, value in expected.items():
        require(same(record.get(key), value), 'actor service complete frozen context mismatch: '+key)
    for key in ('evidence_scope', 'resource_membership_state', 'resource_membership_boundary', 'resource_boundary_decision',
                'mandatory_package_constraints', 'excerpt_byte_conventions'):
        require(same(review.get(key), expected[key]), 'actor service real receipt boundary missing: '+key)
    require(same(review.get('observed_chain'), expected['observation']) and same(review.get('limits'), expected['limits']),
            'actor service full actual observations and limits required')
    zero_keys = ('supporting_ranges_credit', 'native_gameplay_credit', 'runtime_material_payment_credit',
                 'crop_growth_or_harvest_acceptance', 'global_novelty_credit', 'new_migration_credit')
    require(zero(record, zero_keys+('accepted_credit',)) and zero(review, zero_keys) and
            type(record.get('proposed_credit')) is int and record['proposed_credit'] == 1, 'actor service exact integer credit boundary required')
    require(all(k not in obj for obj in (record, review) for k in ('candidate_id', 'original_candidate_id')), 'actor service invented candidate rejected')
    require(record.get('repo') == 'AlexModGuy/AlexsMobs' and record.get('revision') == q['source_pin_checks']['mod_commit'] ==
            p['source_pin_checks']['mod_commit'] == '09755dade2cfbdf14839e026d3af446f9d3ff843', 'actor service fixed repository/revision mismatch')
    nmod, nnative, nadded, nconstraints, ngaps = ACTOR_SERVICE_SPECS[identifier]['counts']
    require(len(p['mandatory_package_constraints']) == nconstraints and same(expected['main_closure_constraints'], p['mandatory_package_constraints']),
            'actor service mandatory complete main/peer constraints required')
    base = ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs'
    for key in ('source_metadata', 'tree_metadata'):
        d = q['source_pin_checks'][key]
        require(same(p['source_pin_checks'][key], d) and sha(snap.read(local_path(d['path'], base))) == d['sha256'], 'actor service original metadata mismatch')
    tree = snap.json(local_path(q['source_pin_checks']['tree_metadata']['path'], base))
    require(tree['truncated'] is False and tree['sha'] == record['revision'], 'actor service fixed tree mismatch')
    entries = {e['path']: e for e in tree['tree']}
    originals, checks, formal = record['original_mod_ranges'], record['independent_mod_ranges'], record.get('chain')
    require(isinstance(formal, list) and len(originals) == len(checks) == len(formal) == nmod, 'actor service complete mod inventory required')
    seen = set()
    for ref, check, evidence in zip(originals, checks, formal):
        raw = snap.read(local_path(ref['source_local'], base)); lo, hi = ref['lines']; lines = raw.splitlines(keepends=True)
        identity = (ref['source_path'], lo, hi)
        require(identity not in seen and type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines), 'actor service invalid or duplicate mod span')
        seen.add(identity)
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(sha(raw) == ref['file_sha256'] == check['file_sha256'] and blob == ref['git_blob_sha1'] == entries[ref['source_path']]['sha'] and
                sha(b''.join(lines[lo-1:hi])) == ref['raw_excerpt_sha256'] == check['raw_excerpt_sha256'], 'actor service actual raw/blob/tree span mismatch')
        require(all(same(check.get(k), v) for k, v in ref.items()) and check['actual_independent_text_read_now'] in (True, False) and
                type(check['support_credit']) is int and check['support_credit'] == 0 and
                (not ref['full_file'] or (lo, hi) == (1, len(lines))), 'actor service actual original/peer mod scope mismatch')
        require((evidence['path'], evidence['line'], evidence['end_line']) == identity and
                evidence['revision'] == ref['revision'] == record['revision'] and evidence['git_blob_sha1'] == blob and
                evidence.get('provenance') == ACTOR_SERVICE_PROVENANCE and
                snap.read(local_path(evidence['source_local'], TOOLS/'sources')) == raw, 'actor service formal mapping/provenance mismatch')
        proof = validate_source(evidence, snap)
        for key in ('source_metadata', 'tree_metadata'):
            require(proof[key+'_sha256'] == q['source_pin_checks'][key]['sha256'], 'actor service formal metadata byte identity mismatch')
    require(record.get('provenance') == formal[0]['provenance'] == ACTOR_SERVICE_PROVENANCE, 'actor service primary provenance required')
    artifact = record['native_auxiliary_artifact']
    archive_raw = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive_raw) == artifact['sha256'] == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0' and
            len(record['native_auxiliary_ranges']) == len(record['native_independent_ranges']) == nnative and
            len(record['native_additional_ranges']) == nadded, 'actor service complete fixed native inventory required')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        for ref in record['native_auxiliary_ranges']+record['native_additional_ranges']:
            raw = archive.read(ref['entry']); lo, hi = ref['lines']; lines = raw.splitlines(keepends=True)
            require(ref['archive'] == artifact['path'] and ref['archive_sha256'] == artifact['sha256'] and
                    type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines) and
                    sha(raw) == ref['entry_sha256'] and sha(b''.join(lines[lo-1:hi])) == ref['raw_excerpt_sha256'] and
                    (not ref['full_file'] or (lo, hi) == (1, len(lines))), 'actor service actual native archive/raw span mismatch')
        for ref, check in zip(record['native_auxiliary_ranges'], record['native_independent_ranges']):
            require(all(same(check.get(k), v) for k, v in ref.items()) and type(check['support_credit']) is int and
                    check['support_credit'] == 0, 'actor service native original/independent scope mismatch')
    gaps = record['resource_membership_boundary']; require(len(gaps) == ngaps, 'actor service full raw gap inventory required')
    for gap in gaps:
        path = gap.get('source_path', gap.get('path')); location = gap.get('raw_not_found_at', gap.get('raw_not_present_at'))
        require(entries[path]['sha'] == gap['tree_blob_sha1_metadata_only'] and gap['resource_contents_read'] is False and
                type(gap['credit']) is int and gap['credit'] == 0 and not local_path(location, base).exists() and
                local_path(location, base) not in snap.overrides, 'actor service raw gap cannot imply actual loaded contents')
    def verify_descriptors(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str) and value['path'].startswith(str(DOCS.relative_to(ROOT))+'/'):
                require(sha(snap.read(local_path(value['path'], DOCS))) == value['sha256'], 'actor service retained prior actual judgment changed')
            if isinstance(value.get('batch'), str) and isinstance(value.get('batch_sha256'), str):
                require(sha(snap.read(local_path(value['batch'], DOCS))) == value['batch_sha256'], 'actor service prior batch changed')
            for child in value.values(): verify_descriptors(child)
        elif isinstance(value, list):
            for child in value: verify_descriptors(child)
    for value in (record['independent_mod_ranges'], record['native_independent_ranges'], record['closest_prior_comparisons'], record['prior_actual_whole_judgments']):
        verify_descriptors(value)
    return dict(**bindings, mod_ranges_support0=nmod, native_original_ranges_support0=nnative, native_added_ranges_support0=nadded,
                mandatory_package_constraints=nconstraints, missing_raw_resource_ranges=ngaps,
                evidence_scope='parameterized_source_policy_only', actual_original_author_thread_id=author, actual_reviewer_thread_id=reviewer,
                concrete_tag_membership_credit=0, native_gameplay_credit=0, runtime_material_payment_credit=0,
                crop_growth_or_harvest_acceptance=0, global_novelty_credit=0, new_migration_credit=0)



# Exactly four already-read whole mechanisms; immutable byte contracts, no general factory.
CLOSED_SERVICE_SPECS = {'EA-0025': {'schema': 'crow-closed-source-policy-v1', 'animal': 'crow', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-crow-crop-cargo-routing-proposal-20261103.json', 'sha256': 'd8a519d3a527d648a5760ee2c308e9157641d928487a67b5a2fd052926126cf6'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-crow-crop-cargo-routing-review-20261103.json', 'sha256': '5d2d2032dd7a2f1258e9ddc1005d865edd0528e46cc123af6c24e3852829a927'}, 'complete_chain_closure': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-crow-independent-review-closure-20261103.json', 'sha256': 'c14f304a5ddb6102e965bcb0bf6715de41b7ac9bb012a38afe01b7433b21ee64'}}, 'canonical_record_sha256': '0d6b1ed13c4b949e0ce9cf723daa4b17ce0f565a7293e1d2651efd9a60ba997f', 'native': False}, 'EA-0026': {'schema': 'seal-closed-source-policy-v1', 'animal': 'seal', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-seal-feeder-loot-handoff-proposal-20261103.json', 'sha256': 'c71546ce0e7f08284aaef1119ebc5e30886e701a2a912518229de67d2e02b21a'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-seal-feeder-loot-handoff-review-20261103.json', 'sha256': 'd4b478a4fc4661760b411a864f7ce1e7f00d9fdfee0e8760bf7bb50a8ddaf490'}, 'complete_chain_closure': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-seal-independent-review-closure-20261103.json', 'sha256': 'e26dfad504d00ecd67f314606622f7960e92330fdc658f0bae42f8c4f7e2f4c2'}}, 'canonical_record_sha256': 'e7f8bf44a8a8e867e347de14fca6b62ea47f449a4ee33914b8cb515f52fb0ac2', 'native': False}, 'EA-0027': {'schema': 'shoebill-closed-source-policy-v1', 'animal': 'shoebill', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-shoebill-earned-fishing-proposal-20261103.json', 'sha256': '6f4430c1d5f6a09217d0e6cd9c263d716b6d802be3ca7c8f7b3c0d7598abca89'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-shoebill-earned-fishing-review-20261103.json', 'sha256': '271d1bba6afcfe8d28d4daf466c6ba2712b958e7560a178ad4ee42de274c6c48'}, 'complete_chain_closure': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-shoebill-independent-review-closure-20261103.json', 'sha256': '12b6cf522a61d1cd0fc225f2a3a71c0abfe43ebfb345038e237f6f9eaec55032'}}, 'canonical_record_sha256': '2e58f614e4c311969da3fe6e73a2771d741e57e66e2114fe6ba9f944b43fa157', 'native': False}, 'EA-0028': {'schema': 'dolphin-closed-source-policy-v1', 'animal': 'dolphin', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-dolphin-paid-guidance-proposal-20261103.json', 'sha256': '2f08dd808ab28819c9c2f0a128317b6a2b223d7d743b94e5b18e507eb07e2df1'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-dolphin-paid-guidance-review-20261103.json', 'sha256': '364e0ccd4b08daf6d5dedcd024c89b8eddbd8c6d978827b7a46ed47537cf0447'}, 'complete_chain_closure': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-dolphin-independent-review-closure-20261103.json', 'sha256': 'b5a9ebd91119d1722f97ca84ccf7fa50f4286c79741cc738bfce5e96d6ef1be7'}}, 'canonical_record_sha256': 'f4609739a3cc72b6c532e8271f030193ba8c279f17b86b682e007c653bdb8f1d', 'native': True}}
CLOSED_NATIVE_SOURCE_HASHES = ('9566cdc38e7d2b3c7effeb022f878ee396aa86f37028335c35698d44fbc69515', 'f6bbaf24364739fdfd35f552e0d5578362b97f99070fa5a587f566d9b7b58507', '7c6206620193f4599497968dcf3e0addc9be819a127428ac688f076aef386e06', '0d26462d6a7ee9f7b920d20aadb9e5d2474f7d999b07096f513e7591fa77761d', '1376088a4929a1f7c8ca02af67994a55ad7b765ecc4345db390b176ac3916d0d', 'bded7ddb24afb86bf8c25cd2229dae50a0e1782ae539e42e73c4160e1bf4e960', '9fed35fb86e4a9fccb78dcc60c0973d3bfd9fa7fa2356cdda77937afa0f85cb3', '27326dadf7d934f67cb614f43643f385988928783348e844c746ab0402674c06', 'b2c9741fdf909572b70d26e0658ae2eb728c8b714d96a044947bda10c6c27567', 'dd55dac0410ad4b88aa1e2850a671de0c951b5ed1021788e65a7d6e5e909a90d', '8e82a27804feae6198d8330c1aeceb1a35edb568bd9fda44133a7ef72b91da00', '7f708e1deae953479196ac4341bbb52343fe77da0e3d6f12d61b7e391182836f', '302994adeb39fa865e7671b96185ca707d7152421adc506fbcbf0194817c0c69')


def validate_closed_native_source(e, snap):
    canonical = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in CLOSED_NATIVE_SOURCE_HASHES, 'closed native source outside exact Dolphin contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo', 'revision', 'git_blob_sha1', 'tree_metadata', 'source_metadata')),
            'native artifact cannot impersonate Git provenance')
    artifact = e['source_artifact']
    archive_raw = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive_raw) == artifact['sha256'] == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0', 'closed native archive bytes changed')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as z:
        raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'closed native ZIP entry/copied bytes mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'closed native invalid range')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and
            sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'closed native excerpt mismatch')
    return {k: e[k] for k in ('source_kind', 'source_coordinate', 'source_artifact', 'source_local', 'source_sha256', 'path', 'line', 'end_line', 'excerpt_sha256', 'raw_excerpt_sha256')}


def validate_closed_service_receipt(path, raw, batches_by_id, snap):
    path = Path(path)
    match = NAME.fullmatch(path.name)
    require(match is not None and match.group(1) == 'general' and
            path.resolve() == (DOCS/'independent-reviews'/path.name).resolve(), 'closed service exact General receipt namespace required')
    identifier = 'EA-'+match.group(2)
    require(identifier in CLOSED_SERVICE_SPECS and identifier in AUTHORIZED['general']['allowed_ids'], 'closed service unauthorized identifier')
    policy = AUTHORIZED['general']; d = json.loads(raw); spec = CLOSED_SERVICE_SPECS[identifier]
    require(d.get('id') == identifier and d.get('reviewer') in policy['labels'] and
            d.get('reviewer_thread_id') == policy['thread_id'], 'closed service exact independent reviewer required')
    require(identifier in batches_by_id, 'closed service missing actual batch')
    batch_path, r = batches_by_id[identifier]
    canonical = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(r)) == spec['canonical_record_sha256'], 'closed service complete frozen record changed')
    require(batch_path.resolve() == (DOCS/'batch-019.json').resolve() and
            d.get('reviewed_batch') == str(batch_path.relative_to(ROOT)) and
            d.get('reviewed_batch_sha256') == sha(snap.read(batch_path)), 'closed service actual batch binding mismatch')
    require([v for v in snap.json(batch_path)['records'] if v.get('id') == identifier] == [r], 'closed service exact unique batch row required')
    for field in ('semantic_key', 'general_context_schema', 'evidence_scope', 'mandatory_package_constraints',
                  'resource_membership_boundary', 'migration_owner', 'limits', 'global_novelty_credit', 'new_migration_credit',
                  'supporting_ranges_credit', 'native_gameplay_credit', 'runtime_material_payment_credit', 'crop_growth_or_harvest_acceptance'):
        require(canonical(d.get(field)) == canonical(r[field]), 'closed service receipt full context missing: '+field)
    require(d.get('observed_chain') == r['observation'] and all(isinstance(x, str) and x for x in d['observed_chain']), 'closed service actual complete observations missing')
    for field in ('global_novelty_credit', 'new_migration_credit', 'supporting_ranges_credit', 'native_gameplay_credit',
                  'runtime_material_payment_credit', 'crop_growth_or_harvest_acceptance'):
        require(type(d.get(field)) is int and d[field] == 0, 'closed service support/global/runtime credit must be integer0')
    require(not any(k in obj for obj in (r, d) for k in ('candidate_id', 'original_candidate_id')), 'closed service fabricated candidate identity')
    for key, descriptor in spec['bindings'].items():
        require(r[key] == d.get(key) == descriptor, 'closed service immutable descriptor mismatch')
        actual = snap.read(local_path(descriptor['path'], DOCS))
        require(sha(actual) == descriptor['sha256'], 'closed service original/review/closure changed')
        context_key = {'complete_chain_proposal':'proposal', 'complete_chain_review':'independent_review', 'complete_chain_closure':'closure'}[key]
        require(r['frozen_mechanism_context'][context_key] == json.loads(actual), 'closed service complete original context omitted')
    q, p, c = (r['frozen_mechanism_context'][k] for k in ('proposal', 'independent_review', 'closure'))
    original_author = 'main-coordinator' if identifier == 'EA-0025' else policy['proposal_author_thread_id']
    require(r['author_thread_id'] == policy['proposal_author_thread_id'] and p['reviewer_thread_id'] == policy['thread_id'] and p['original_author_thread_id'] == original_author and
            p['reviewer_thread_id'] != p['original_author_thread_id'] and p['formal_EA_id_assigned'] is None and c['formal_EA_id_assigned'] is None,
            'closed service actual independent preformal identity mismatch')
    owner = r['migration_owner']; ledger = ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl'
    owner_rows = [json.loads(line) for line in snap.read(ledger).decode().splitlines() if line.strip()]
    owner_rows = [v for v in owner_rows if v.get('candidate_id') == owner['candidate_id']]
    require(len(owner_rows) == 1 and sha(canonical(owner_rows[0])) == owner['canonical_full_row_sha256'], 'closed service whole existing migration owner changed')
    native_refs = (q['actual_read_ranges'] if spec['native'] else q['actual_native_read_ranges']) + p.get('additional_actual_native_support_ranges', []) + p.get('prior_actual_native_support_ranges_reused_not_reread', []) + p.get('prior_actual_native_item_context_reused_not_reread', [])
    artifact = q['source_artifact'] if spec['native'] else {'path': native_refs[0]['archive'], 'sha256': native_refs[0]['archive_sha256']}
    archive_raw = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive_raw) == artifact['sha256'] == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0', 'closed service native support archive changed')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as z:
        for ref in native_refs:
            b = z.read(ref['entry']); lo, hi = ref['lines']; part = b''.join(b.splitlines(keepends=True)[lo-1:hi])
            if 'archive' not in ref:
                prior = ref.get('prior_actual_read_reused', {})
                require(identifier == 'EA-0025' and ref['entry'] == 'net/minecraft/world/entity/ai/goal/MoveToBlockGoal.java' and
                        prior.get('sha256') == '5099461f26d780fd7688ad726b9cad783c8b43160e1ee7b40327028261c7b3cf' and
                        sha(snap.read(local_path(prior['path'], DOCS))) == prior['sha256'], 'closed service exact prior inherited archive binding required')
            require(ref.get('archive', artifact['path']) == artifact['path'] and ref.get('archive_sha256', artifact['sha256']) == artifact['sha256'] and
                    sha(b) == ref['entry_sha256'] and type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(b.splitlines()) and
                    sha(part) == ref['raw_excerpt_sha256'] and (not ref['full_file'] or (lo, hi) == (1, len(b.splitlines()))), 'closed service full native raw support mismatch')
            if 'raw_excerpt_utf8' in ref: require(part.decode() == ref['raw_excerpt_utf8'], 'closed service raw native text mismatch')
    if not spec['native']:
        base = ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs'
        tree = snap.json(base/'tree.json'); entries = {e['path']: e for e in tree['tree']}
        require(tree['sha'] == r['revision'] == '09755dade2cfbdf14839e026d3af446f9d3ff843' and tree['truncated'] is False, 'closed service fixed mod tree changed')
        for ref in q['actual_mod_read_ranges'] + p.get('prior_actual_mod_support_ranges_reused_not_reread', []):
            b = snap.read(local_path(ref['source_local'], base)); lo, hi = ref['lines']
            blob = hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
            require(sha(b) == ref.get('file_sha256', ref.get('source_sha256')) and blob == ref['git_blob_sha1'] == entries[ref.get('source_path', ref.get('repo_path'))]['sha'] and
                    sha(b''.join(b.splitlines(keepends=True)[lo-1:hi])) == ref['raw_excerpt_sha256'] and
                    (not ref['full_file'] or (lo, hi) == (1, len(b.splitlines()))), 'closed service actual mod support mismatch')
        for gap in r['resource_membership_boundary']:
            rel = gap.get('repo_path', gap.get('path'))
            require(entries[rel]['sha'] == gap['tree_blob_sha1_metadata_only'], 'closed service missing raw tree identity mismatch')
            roots = [ROOT/x['root'] for x in gap.get('four_fixed_cache_checks', [])] or [base, TOOLS/'sources/AlexModGuy__AlexsMobs']
            require(all(not (root/rel).exists() and (root/rel).resolve() not in snap.overrides for root in roots), 'closed service raw gap changed; no loaded membership inference')
    else:
        with zipfile.ZipFile(io.BytesIO(archive_raw)) as z:
            require(not [n for n in z.namelist() if n.endswith('/fishes.json') or n.endswith('/dolphin_located.json')], 'Dolphin selected archive gap changed')
    decision = d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS, 'closed service accept decision role mismatch')
        return dict(state='non_accepting', role='general', id=identifier, decision=decision, receipt=str(path.relative_to(ROOT)), receipt_sha256=sha(raw), reason='explicit nonaccepting receipt confers0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit'] == 1, 'closed service accepted credit must be integer1')
    checks = d.get('source_checks'); require(isinstance(checks, list) and len(checks) == len(r['chain']), 'closed service incomplete range coverage')
    verified = []
    for check, e in zip(checks, r['chain']):
        require(check.get('evidence') == e, 'closed service exact typed source receipt required')
        flags = ('archive_sha256_match', 'entry_bytes_match', 'fixed_coordinate_match', 'excerpt_exact') if spec['native'] else policy['checks']
        require(all(check.get(k) is True for k in flags), 'closed service explicit typed source checks missing')
        verified.append(validate_closed_native_source(e, snap) if spec['native'] else validate_source(e, snap))
    for key in r['chain'][0]: require(r.get(key) == r['chain'][0][key], 'closed service primary source/chain head mismatch')
    return dict(state='validated_acceptance', id=identifier, role='general', reviewer=d['reviewer'], decision=decision,
                semantic_key=r['semantic_key'], accepted_credit=1, receipt=str(path.relative_to(ROOT)), receipt_sha256=sha(raw),
                batch=str(batch_path.relative_to(ROOT)), batch_sha256=sha(snap.read(batch_path)), source_checks_recomputed=verified,
                supporting_ranges_credit=0, limitations=d['limits'], observed_chain=d['observed_chain'],
                complete_chain_support_proof=dict(**spec['bindings'], source_kind='artifact_native' if spec['native'] else 'git_repository',
                     scope=r['evidence_scope'], native_gameplay_credit=0, runtime_material_payment_credit=0, global_novelty_credit=0, new_migration_credit=0))


TASMANIAN_V12_SPEC = {'id': 'EA-0029', 'canonical_record_sha256': '5ef3af6e5a8ee43e48659266c6bf38078317f8d16f6e91053cffc954c4368be3', 'batch': 'batch-020.json', 'schema': 'tasmanian-original-author-confirmed-distinct-main-independent-review-v1', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-tasmanian-devil-feeding-retreat-proposal-20261104.json', 'sha256': 'f0ce5f6e67b7974a72b69ade3d930cf2e20e90393692c4ba4a3f3e582968635c'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-tasmanian-devil-feeding-retreat-independent-review-20261104.json', 'sha256': '161502b7f98576db63205c140411165e1e0cd73a8d41726c117995efd4a9ad91'}, 'complete_chain_count_correction': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-tasmanian-devil-feeding-retreat-count-clarification-20261104.json', 'sha256': 'f0ed648c68b174e35b7c872de6e85d78c11c6d940e2ce9a49afdb21dfe35140c'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_count_correction': 'count_correction'}, 'native_source_hashes': ['95d7f6b6b522d54911371d771063d4d04aca9f2c40343346bdd149679da527fe', '51a640854cfdd2c487b516354547dced4c30a8b7cc5b722550fe83f65564dddb', '0d7df1d3f70ca35ce01ec33edb32e74320017ac2dd3b437da36d3e07fa639982', 'b4a20ccef939df72d738b65b201533702bdce396a79af0b542ca1132696159b6', '76158d70c209fa26ee2ec09a54141cf5bfd524957cda62a7c6c698339d28d4e6', '8d80d0df25393ae570898a6fe5a8a77e6bc690a99a542529396e081ae826462a', '9293d4a879f35e27a925bb03c8beb815a37cc556359abb3722ae472cdacfcaf0', '87e674ff7d8f96d7bc6531a0afe966a51708a5a3fab2d38c023b2c23cfcb594e', '43f6f69972c17ea65ce6e571cfefbd84cddd1ba9cbe7ea0967f99723f32f33ff', '2d0e7c3d65d311bfb928d3f36dc31dfb0c306bb9ec8bf3fb352d6ae80880b09c', '8efb7208c47165f6bccb6112506576ce9aae053af4b687fefec6cbf66aac19a3', 'e03c389a0cb52cea5b2e7303ef18895eb25d5e64a8178081577203ca7e472ce8', '86b08ecd16486932d553ecde186d5ade65b3b648c58f9ca45a61205d3a9d203b', '815b7539349d35237e903935b40f614bd87c65f4c560435f795b8c39f0bc09ab', '9f1de06fffd1432bdd02b23d63d2fd2c003a8cc0d9475022316b273540ac6ab3', '43e8f62ae64d2b7fe0da54b94885cffca89ef00e908efec7a78601af33981bbe'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_tasmanian_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in TASMANIAN_V12_SPEC['native_source_hashes'], 'Tasmanian native outside exact16-source contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Tasmanian native cannot impersonate Git')
    artifact = TASMANIAN_V12_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == TASMANIAN_V12_SPEC['coordinate'], 'Tasmanian native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Tasmanian native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Tasmanian native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Tasmanian native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Tasmanian native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_tasmanian_receipt(path, raw, batches_by_id, snap):
    path = Path(path); spec = TASMANIAN_V12_SPEC; policy = AUTHORIZED['general']
    require(path.resolve() == (DOCS/'independent-reviews/general-EA0029.json').resolve(), 'Tasmanian exact General author namespace required')
    d = json.loads(raw)
    require(d.get('id') == 'EA-0029' and 'EA-0029' in policy['allowed_ids'] and d.get('reviewer') == spec['receipt_label'] and d.get('reviewer_thread_id') == policy['thread_id'], 'Tasmanian actual original author confirmation identity mismatch')
    require('EA-0029' in batches_by_id, 'Tasmanian actual batch missing')
    batch_path, r = batches_by_id['EA-0029']
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(r)) == spec['canonical_record_sha256'], 'Tasmanian complete frozen record changed')
    require(batch_path.resolve() == (DOCS/spec['batch']).resolve() and d.get('reviewed_batch') == str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256') == sha(snap.read(batch_path)), 'Tasmanian exact actual batch binding mismatch')
    require(snap.json(batch_path)['records'] == [r] and type(r['proposed_credit']) is int and r['proposed_credit'] == 1 and r['status'] == 'reviewed_proposed', 'Tasmanian only one exact whole row eligible')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','crop_growth_or_harvest_acceptance'):
        require(canonical(d.get(field)) == canonical(r[field]), 'Tasmanian full receipt context omitted: '+field)
    require(d.get('observed_chain') == r['observation'] and all(isinstance(v,str) and v for v in d['observed_chain']), 'Tasmanian whole observed chain missing')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','crop_growth_or_harvest_acceptance'):
        require(type(d.get(field)) is int and d[field] == 0, 'Tasmanian support/runtime/global credit must be integer0')
    require(not any(k in obj for obj in (d,r) for k in ('candidate_id','original_candidate_id')), 'Tasmanian fabricated candidate identity')
    for key, desc in spec['bindings'].items():
        require(r[key] == d.get(key) == desc, 'Tasmanian proposal/Main review/count correction binding mismatch')
        b = snap.read(local_path(desc['path'], DOCS))
        require(sha(b) == desc['sha256'] and json.loads(b) == r['frozen_mechanism_context'][spec['binding_context_keys'][key]], 'Tasmanian complete immutable context changed')
    q = r['frozen_mechanism_context']['proposal']; m = r['frozen_mechanism_context']['independent_main_review']; correction = r['frozen_mechanism_context']['count_correction']
    require(q['owner_thread_id'] == r['author_thread_id'] == policy['thread_id'] and r['independent_reviewer_thread_id'] == policy['proposal_author_thread_id'] and r['author_thread_id'] != r['independent_reviewer_thread_id'], 'Tasmanian original author and independent Main cannot be conflated')
    require(m['reviewer'] == 'main-coordinator' and m['proposer_thread_id'] == q['owner_thread_id'] and m['proposal_sha256'] == spec['bindings']['complete_chain_proposal']['sha256'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and m['applied_credit'] == 0 and m['accepted_maximum_whole_mechanisms'] == 1, 'Tasmanian distinct preformal Main review missing')
    require(m['required_count_correction']['sha256'] == spec['bindings']['complete_chain_count_correction']['sha256'] and m['required_count_correction']['native_new_read_ranges'] == 13 and m['required_count_correction']['native_new_read_lines'] == 405 and correction['formal_credit'] == 0, 'Tasmanian13/405 correction missing')
    base = ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs'
    for key in ('source_metadata','tree_metadata'):
        require(sha(snap.read(local_path(q['source'][key], base))) == q['source'][key+'_sha256'], 'Tasmanian original source metadata changed')
    tree = snap.json(base/'tree.json'); entries = {e['path']:e for e in tree['tree']}
    require(tree['sha'] == q['source']['revision'] == '09755dade2cfbdf14839e026d3af446f9d3ff843' and tree['truncated'] is False, 'Tasmanian fixed mod tree changed')
    for ref in q['actual_mod_read_ranges']:
        b = snap.read(local_path(ref['source_local'], base)); lo, hi = ref['lines']; part = b''.join(b.splitlines(keepends=True)[lo-1:hi])
        require(sha(b) == ref['file_sha256'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == ref['git_blob_sha1'] == entries[ref['source_path']]['sha'], 'Tasmanian original mod raw/blob mismatch')
        require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(b.splitlines()) and sha(part) == ref['raw_excerpt_sha256'] and part.decode() == ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi) == (1,len(b.splitlines()))), 'Tasmanian original mod excerpt/range mismatch')
    for ref in q['actual_mod_read_ranges']+q['actual_native_read_ranges']:
        prior = ref.get('prior_actual_own_review')
        if prior: require(sha(snap.read(local_path(prior['path'], DOCS))) == prior['sha256'], 'Tasmanian prior actual own reuse changed')
    for prior in q['prior_whole_decisions']:
        require(sha(snap.read(local_path(prior['path'], DOCS))) == prior['sha256'], 'Tasmanian prior whole decision changed')
    archive_raw = snap.read(local_path(spec['artifact']['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive_raw) == spec['artifact']['sha256'], 'Tasmanian support ZIP changed')
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as z:
        for ref in q['actual_native_read_ranges']:
            b = z.read(ref['entry']); lo,hi = ref['lines']; part = b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive'] == spec['artifact']['path'] and ref['archive_sha256'] == spec['artifact']['sha256'] and ref['coordinate'] == spec['coordinate'] and sha(b) == ref['entry_sha256'], 'Tasmanian original native artifact/entry mismatch')
            require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(b.splitlines()) and sha(part) == ref['raw_excerpt_sha256'] and part.decode() == ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi) == (1,len(b.splitlines()))), 'Tasmanian original native full range/excerpt mismatch')
    gap = r['resource_membership_boundary']; rel = gap['path']
    require(entries[rel] == gap['tree_metadata'] and gap['contents_read'] is False and gap['raw_in_selected_root'] is False, 'Tasmanian raw tag gap identity changed')
    require(all(not (b/rel).exists() and (b/rel).resolve() not in snap.overrides for b in (base,TOOLS/'sources/AlexModGuy__AlexsMobs')), 'Tasmanian raw tag now exists; re-review membership boundary')
    decision = d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS, 'Tasmanian acceptance decision role mismatch')
        return dict(state='non_accepting',role='general',id='EA-0029',decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit'] == 1, 'Tasmanian accepted credit must be integer1')
    checks = d.get('source_checks'); require(isinstance(checks,list) and len(checks) == len(r['chain']), 'Tasmanian full mixed-source coverage required')
    verified = []
    for check,e in zip(checks,r['chain']):
        native = e.get('source_kind') == 'artifact_native'
        require(check.get('evidence') == e, 'Tasmanian exact typed evidence required')
        flags = ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact') if native else policy['checks']
        require(all(check.get(k) is True for k in flags), 'Tasmanian explicit typed source checks missing')
        verified.append(validate_tasmanian_native_source(e,snap) if native else validate_source(e,snap))
    for k in r['chain'][0]: require(r.get(k) == r['chain'][0][k], 'Tasmanian primary/chain head mismatch')
    return dict(state='validated_acceptance',id='EA-0029',role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='mixed_git_repository_and_explicit_artifact_native',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




ALLAY_V13_SPEC = {'id': 'EA-0030', 'canonical_record_sha256': '57a1691488458ba27311508cf481978856dc0d161f0bd0f0a9424916c0d1e85e', 'batch': 'batch-021.json', 'schema': 'allay-original-author-confirmed-distinct-main-independent-review-v1', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-allay-music-duplication-proposal-20261104.json', 'sha256': 'c35628c04c30ff4e33eb2de8f6f37250249516328dc5b1ab1baf3cf9c20e6574'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-allay-music-duplication-independent-review-20261104.json', 'sha256': '689989895b706a6bd696f7cae80725a375c9b820b2d8b48b4d6163af81799a30'}, 'complete_chain_wording_correction': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-allay-cooldown-wording-correction-20261104.json', 'sha256': '00fe562cf33dcac7d5ed1fec65b542ff1649fc688df2cd6763f228f246a9af74'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_wording_correction': 'source_wording_correction'}, 'native_source_hashes': ['a208110d3a089bf7b85f6b2bdb4d012f2ef70804d8bc02b7177e50528373e1ed', '33b0dfa64552470592e9f1655571b9c8610515318b9d0523900f9f333351279f', '76e4e722f9d9738f8f618a291d0f5cedda89078b89156996b4475905ad3c0cdb', '408a582c94f801e9edb9c148bfe44d0d1f11e29ace5069932528460927dcfefe', '085842641f303011b1816d64e0c179785d9f7e077595a907262a8678a8dcc9df', '2f02b12de2f78787f3d2b33b6b1974f2c53cec71baa9847750b01f0cfbba5c12', '6670cf4c7ea5297880281f3480a58d59384addf11f3e98d835686f0e25b424a8', '616b785d84559cf76f23204dbf07e2f4f8c5abc0374d63ab2a8a9171ccdd56aa', 'c6c2ab58b9b5990bca8b0deee349fdc0c65f2882ccd94eea96d79e9a716c20e2', '0b55f928a827fa718b33e81f37cdac39f4af7d70b90bd6bf73a2bb4a52516a95', '4e3ac374b86cbaedec886ce3c66bd97b0c6ecbf2fef3093e78f6b8dbcfb04190', '88b5d74ab650ca0fc67bf93e04d2be4321f6bbad481abf4c4493bed2682ec5d9', '24283910a7770b59643ca4e587e33ed642fa6278227f2f0afc0f80b689c0975f', 'eaf89dff0f07c2f5a382f4d2b07f1af8abd3c84980b81df36fc94db14ed56152', 'a522d60d5f70dc2548904b70128e1d69af85948b8c26896c4c4f7c267d4dc482', '0656cab26a0117f2b9ba0fb30d4257a583b94fda127916fd0760b5712c288db4', 'abcaa2440fffff060d98e00fbfb74ab4988992002c8e7d1092acca70b6642974', '6638363df6d81933343dcb10d14fbba60ae4c171873af2b0973923510b38c5d9', 'dc8b4c0764dff0abc9ee78072018cfe63caf20e7c8687703e36e79f60dd5ef2d', 'f017951ae82e6b48574130d21a5963a5dbbcbec69ff96ddfe254f4dfb039eda3', '30a4dd242c84d2454943c7e8db157d3f89e3bd933a0e26ae11c1d65393ebe0d7', '3b6145a28400ebdbe38d38577be286aa6c2aa7dd39b9640b080447ebab203773', 'e7b76305539757ca81722e991de33fd16bb2d3d005f816ff185e86b28545b509', '2e6523631c67a067bdf9197b9ff5de7b3d3973e370959f97e56d8a53215be811', '672551c5adc1e25e32f8f5c755c3b0ffa392c069ff29ed6e9d13676e0007cbaf', 'fe1bc7a0d1ea9de5689bbf9be038a32423a8146f80a9e0baa8d599422ec65e76', '52bd5186e5ecc3260b9914c81479be82b803849cd5f1bfecf18af939b9cd1016', '3a6d811d410c4258c0d781a93a0327c5f15890a6debc124911b85bb5c5844d21', 'e868355fd42619e4a91c9c3e45e206e0f5c4b6c3d3debd2e9a55f925facb8edb', '0a54ecc8e8cb1094e91e81fa6846931161d80b9522321f9bb45af211eda353df', '55b8c7645ef303a0c85d1b11a814e55665ff49595ba99dad04cd30cbff6723f8', '9e2b689c38a3287c824a5fe2713025fc0ceb0aca6b16772e4e18ef7796a10cb6', 'a6b83873a2e4746070370297a3fc82c4b576f3fa5283846dc3cb3653d74b590f', '53aee0289a8b0ab275119a5fa7f6b85c85566535abed5f47900cee0eb170fcf5', 'e5eb0f6331018e1eb666f937b0bcf46ad5ca158f0f7ab44ebcd69cea63c6689d', '66831f711a04c863ae288c2a0d564d1e52c89e79ea62e51e6accfc819ddc4f7b', '4c4dcf6da712933e95b70cf8e0ac6d944ea92cc40565a9f9f1ee64401c2b6c05', '011aac1a81ae115f80f23da684b925946dad1e36b7f51e4d2a5037da73142890'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_allay_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in ALLAY_V13_SPEC['native_source_hashes'], 'Allay native outside exact38-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Allay native cannot impersonate Git')
    artifact = ALLAY_V13_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == ALLAY_V13_SPEC['coordinate'], 'Allay native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Allay native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Allay native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Allay native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Allay native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_allay_receipt(path, raw, batches_by_id, snap):
    path = Path(path); spec = ALLAY_V13_SPEC; policy = AUTHORIZED['general']
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(path.resolve() == (DOCS/'independent-reviews/general-EA0030.json').resolve(), 'Allay exact original author namespace required')
    d = json.loads(raw)
    require(isinstance(d,dict) and d.get('id') == spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer') == spec['receipt_label'] and d.get('reviewer_thread_id') == policy['thread_id'], 'Allay original author identity mismatch')
    require(spec['id'] in batches_by_id, 'Allay actual batch missing')
    batch_path, r = batches_by_id[spec['id']]
    require(sha(canonical(r)) == spec['canonical_record_sha256'], 'Allay frozen full record changed')
    require(batch_path.resolve() == (DOCS/spec['batch']).resolve() and d.get('reviewed_batch') == str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256') == sha(snap.read(batch_path)), 'Allay exact actual batch binding required')
    require(snap.json(batch_path)['records'] == [r] and type(r['proposed_credit']) is int and r['proposed_credit'] == 1 and type(r['accepted_credit']) is int and r['accepted_credit'] == 0 and r['status'] == 'reviewed_proposed', 'Allay only one proposed whole row')
    context_fields = ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_package_constraints','mandatory_corrections','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','limits','deduplication','frozen_mechanism_context','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit')
    for field in context_fields:
        require(canonical(d.get(field)) == canonical(r[field]), 'Allay complete receipt context missing: '+field)
    require(d.get('observed_chain') == r['observation'] and all(isinstance(v,str) and v for v in d['observed_chain']), 'Allay corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field] == 0, 'Allay non-ecology/runtime/support credit must be integer0')
    require(not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')), 'Allay invented global candidate identity')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False, 'Allay source is not execution')
    for key, desc in spec['bindings'].items():
        require(r[key] == d.get(key) == desc, 'Allay immutable proposal/review/correction binding mismatch')
        b = snap.read(local_path(desc['path'], DOCS))
        require(sha(b) == desc['sha256'] and json.loads(b) == r['frozen_mechanism_context'][spec['binding_context_keys'][key]], 'Allay frozen context changed')
    q = r['frozen_mechanism_context']['proposal']; m = r['frozen_mechanism_context']['independent_main_review']; c = r['frozen_mechanism_context']['source_wording_correction']
    require(q['owner_thread_id'] == r['author_thread_id'] == policy['thread_id'] and r['independent_reviewer_thread_id'] == policy['proposal_author_thread_id'] and r['author_thread_id'] != r['independent_reviewer_thread_id'], 'Allay source author cannot be own independent reviewer')
    require(m['reviewer'] == 'Main coordinator; distinct from original General author' and m['proposal'] == spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and m['recommended_maximum_credit'] == 1 and type(m['recommended_maximum_credit']) is int and m['accepted_credit'] == 0 and m['applied_credit'] == 0, 'Allay distinct max1 preformal Main review required')
    require(m['decision'] == 'ACCEPT_AT_MOST_ONE_WHOLE_PARAMETERIZED_ECOLOGY_SOURCE_POLICY_WITH_MANDATORY_CORRECTION; pending formal source package and real original-author acceptance receipt', 'Allay independent Main decision changed')
    require(m['prior_whole_decision_bindings'] == q['prior_whole_decisions'] == r['deduplication'] and m['existing_global_migration_whole_owners'] == q['existing_global_migration_whole_owners'] == r['migration_owner'], 'Allay prior whole owners/comparisons missing')
    require(m['mandatory_corrections'] == r['mandatory_corrections'] and m['actual_native_read_ranges'] == [{k:v for k,v in a.items() if k != 'raw_excerpt_utf8'} for a in q['actual_native_read_ranges']], 'Allay Main exact full native coverage/evaluation correction missing')
    corrected = list(m['independent_findings'])
    require(c['original_review'] == spec['bindings']['complete_chain_review'] and c['reviewer_thread_id'] == r['independent_reviewer_thread_id'] and c['field'] == 'independent_findings[10]' and corrected[10].count(c['incorrect_phrase']) == 1 and c['maximum_recommended_credit_unchanged'] == 1 and c['new_semantic_credit'] == 0, 'Allay distinct Main true/false correction context missing')
    corrected[10] = c['corrected_complete_finding']
    require(r['observation'] == corrected and 'set true (false->true rearm)' in corrected[10], 'Allay literal cooldown true/false correction required')
    for prior in q['prior_whole_decisions'] + q['supporting_prior_receipts']:
        require(sha(snap.read(local_path(prior['path'], DOCS))) == prior['sha256'], 'Allay exact reused whole decision changed')
    owner_rows = [json.loads(line) for line in snap.read(ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl').decode().splitlines() if line.strip()]
    for owner in r['migration_owner']:
        rows = [a for a in owner_rows if a.get('candidate_id') == owner['candidate_id']]
        require(len(rows) == 1 and sha(canonical(rows[0])) == owner['canonical_complete_row_sha256'] and rows[0]['status'] == 'accepted' and type(rows[0]['credit']) is int and rows[0]['credit'] == 1, 'Allay exact already-owned whole migration row changed')
        require({k:v for k,v in rows[0].items() if k != 'evidence'} == owner['current_actual_non_evidence_decision_fields'], 'Allay existing owner decision binding missing')
    archive = snap.read(local_path(spec['artifact']['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == spec['artifact']['sha256'], 'Allay fixed native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        require(r['resource_membership_boundary']['missing_entry'] not in z.namelist(), 'Allay selected sources Jar resource gap changed')
        for ref in q['actual_native_read_ranges']:
            b = z.read(ref['entry']); lo,hi = ref['lines']; part = b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive'] == spec['artifact']['path'] and ref['archive_sha256'] == spec['artifact']['sha256'] and ref['coordinate'] == spec['coordinate'] and sha(b) == ref['entry_sha256'], 'Allay original native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(b.splitlines()) and sha(part) == ref['raw_excerpt_sha256'] and part.decode() == ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi) == (1,len(b.splitlines()))), 'Allay original complete raw text/range mismatch')
        correction_source = c['actual_source_rechecked']
        require(correction_source['archive'] == spec['artifact']['path'] and correction_source['archive_sha256'] == spec['artifact']['sha256'], 'Allay cooldown correction artifact mismatch')
        for ref in correction_source['ranges']:
            b = z.read(ref['entry']); lo,hi = ref['lines']; part = '\n'.join(b.decode().splitlines()[lo-1:hi])
            require(sha(b) == ref['source_sha256'] and type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(b.splitlines()) and part == ref['excerpt'] and sha(part.encode()) == ref['excerpt_sha256'], 'Allay literal cooldown correction source mismatch')
    decision = d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS, 'Allay acceptance decision role mismatch')
        require(type(d.get('accepted_credit')) is int and d['accepted_credit'] == 0, 'Allay nonaccepting author receipt must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting original-author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit'] == 1, 'Allay accepted credit must be integer1')
    checks = d.get('source_checks'); require(isinstance(checks,list) and len(checks) == len(r['chain']), 'Allay all38 exact typed source checks required')
    verified = []
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence') == e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')), 'Allay explicit typed native checks missing')
        verified.append(validate_allay_native_source(e,snap))
    for k in r['chain'][0]: require(r.get(k) == r['chain'][0][k], 'Allay primary/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




CAT_V14_SPEC = {'id': 'EA-0031', 'canonical_record_sha256': 'd5fc603ec62d49c246a961a6931210fbafed73af97096a32f8bb1c64c7011e99', 'batch': 'batch-022.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-cat-village-hut-replenishment-proposal-20261104.json', 'sha256': '577d3d619673d13ef50ce178962a2d79a3d6a51dcd509bc6af8fc908f38132de'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-cat-habitat-replenishment-independent-review-20261104.json', 'sha256': '2d50f245a708e18c6f59225f7dc978214cb7129d1f42ea247daa4f45be92d3fe'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review'}, 'native_source_hashes': ['f93bc9c2549de76540b0c2a143cabbea9a569f8c1d71f838779c0fed0b099fb6', 'efe19dc4e4186c72604acc3580d786e1b588f101dbde22727b8bf99fea579b39', '78e115ef85ad957bab5176d4cdd3fa8989071b1ae4cd6066dc5a70d215fa483f', '77847df139a15e9b85f813019f79fd6535b4ffa477cb9e307655b5f24ba1cb8a', 'eb4d40d32fa5e755ac50aa0823bc992216146986df7e1220a43d08ebf2ec028f', 'cd8554711137425eefd122b3ce981750ef82e01b235de002f0ecd081a91a4d03', '473727ff6e674f937aa54fb7521342398adcf4ca383ea7bf83c7b5d577e0b009', 'aab7e59d0145dc14fd80275a5bb3dbde3d39bfdbe8b334d8b4fb1c44dea211a7', '2b8044814cdc98409adfa4bda7c6744a5fc5cd7feaae0be1090d52e94e569bbe', '99074184df4ec3d75306b6bc7c301f9f6275363af9532b9c1b12e82ce10e8c1f', 'f3830f7a80ef074012d73358437490fd8e44b7d8a6e2c14e5f9434dbaaf8a629', '0b35b2a9cd36d05a4031677b53a9a6ecde77ef019808937c4bde4db63eeff375', '938cc6417397e83d42e5c3e113973df2745e217462945c3546e77ddf59e8017f', '0e6dd6b7254ea4084b4d03f3939d77acc2892880857887c1573e48a7bd32b861', '932a454222cb95e7a8e528da4ae73c27c70dbfa280a177ae12f68da67adf3897', '3d87c68d697750245f114fa633e3a6b0476c9b8763aca1c7b1a46eb3f08ea354', '5d1bdb7d36336988952b7c4f25ef09d8dc20d7bb72271ed8a6caba74768413ac', 'a296262089666d5dbde19532f883ede3f29a61d870d67317fad5ed02f10136ce', '129696469b8aad9db4810525d3cf1c69d965a4be4952f9448405b8811a5092a6', 'd37c6e03f6cf32fdee124e5227e122896e90570fef9bf3fe08dc4c86499c12fb', 'a2600e7b62244e1bf051217f0703b27da91155c0c9724ab6d503ffed7312a67e', 'a0964798448382e5d76a32bf501e5acc8f8ff13462a9cd5c9e66a62b6a50e5df', '5742e58c4ff53daffae8a916688bba2bd5fbced99a76d57188d915de669775c6', 'e9f98c5d367cefc63385f7dfd0bcf35a639bb877ab299e3286a24d6df53949cd', '871e7789d3b56b19c65c87601401eb0858b942e60e0967e300e259111e0edaf1', '5b4386ed605f85afefb7cb5ec595fb683ad9540996dec738526ac6007386700e', 'c574e4614f029c2e135b3d7d6d0d52c7fe07753dd26d5bace6ea0d361e1483cf', '3b6145a28400ebdbe38d38577be286aa6c2aa7dd39b9640b080447ebab203773', '4599050bd5352ea3f38fbb474ce5dcc997e5906a2344dac3b55b3c36cee2d852', '25a84927368829ad2ccab6e09bd7d2ac9ed9bb770821590da0c2eff7ee0703ef', '191ae1a2934f4abd4a886cc92cb3093f1e793a9e0d10d89f8629277a2e145fc4', 'f3d57778bd472b6af43ffa8db13af20ecbd73b7c04b6db1c303e62dca65c69d9', 'fbce090f047d131cd0ab8f3905e3b3ff2dba7731cc56c46702e78e6320021f67'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_cat_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in CAT_V14_SPEC['native_source_hashes'], 'Cat native outside exact33-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Cat native cannot impersonate Git')
    artifact = CAT_V14_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == CAT_V14_SPEC['coordinate'], 'Cat native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Cat native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Cat native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Cat native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Cat native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_cat_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=CAT_V14_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0031.json').resolve(),'Cat exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'Cat original author identity mismatch')
    require(spec['id'] in batches_by_id,'Cat actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'Cat complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'Cat exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','Cat one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'Cat complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'Cat corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'Cat non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'Cat execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'Cat immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'Cat frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Cat author cannot be own independent reviewer')
    require(m['reviewer']=='Main independent from General original source author' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='RECOMMEND_AT_MOST_ONE_COMPLETE_RELATED_SOURCE_POLICY_AFTER_LITERAL_ORDER_CORRECTION','Cat distinct max1 preformal Main review required')
    require(m['actual_native_read_ranges']==[dict(x,Main_actually_read_bounded_original_range=True,range_credit=0) for x in q['actual_native_read_ranges']] and m['actual_raw_base_resource_reads']==q['actual_raw_base_resource_reads']==r['raw_base_resource_bindings'],'Cat all33 Main native ranges and5 raw resource bindings required')
    require(m['prior_own_admission_support_reused']==[{k:v for k,v in x.items() if k!='raw_excerpt_utf8'} for x in q['prior_actual_native_admission_support_reused']] and r['prior_native_context_bindings']==q['prior_actual_native_admission_support_reused'],'Cat exact prior admission reuse missing')
    require(r['observation']==m['independent_findings'] and r['mandatory_corrections']==m['mandatory_corrections'] and r['mandatory_package_constraints']['current_corrected_author_constraints']==r['mandatory_constraints'],'Cat current corrected Main/author constraints required')
    for original in m['mandatory_corrections'][0]['original_fields']:
        require(q[original['field']][original['index']]==original['original'],'Cat original proposal correction history changed')
    require('FIRST invokes super.finalizeSpawn' in r['mandatory_constraints'][12] and r['mandatory_constraints'][12]!=q['mandatory_constraints'][12],'Cat mandatory current super-first correction missing')
    for prior in q['prior_whole_decisions']+[x['actual_complete_decision_read'] for x in m['prior_whole_decision_bindings']]+[m['additional_complete_EA22_decision_read'],q['continuation_checkpoint']]:
        require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Cat exact prior decision/checkpoint changed')
    ledger=snap.read(ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl')
    rows=[json.loads(line) for line in ledger.decode().splitlines() if line.strip()]
    for owner,peer in zip(r['migration_owner'],m['existing_global_migration_whole_owners']):
        found=[x for x in rows if x.get('candidate_id')==owner['candidate_id']]
        require(len(found)==1 and sha(canonical(found[0]))==owner['canonical_complete_row_sha256']==peer['canonical_complete_row_sha256'] and owner['candidate_id']==peer['candidate_id'] and found[0]['status']=='accepted' and type(found[0]['credit']) is int and found[0]['credit']==1,'Cat exact existing migration whole owner changed')
        require({k:v for k,v in found[0].items() if k!='evidence'}==owner['actual_current_non_evidence_decision_fields']==peer['actual_non_evidence_fields_read'],'Cat full existing whole decision changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'Cat native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_admission_support_reused']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'Cat original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Cat complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior: require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Cat prior exact admission source changed')
        cat='\n'.join(z.read('net/minecraft/world/entity/animal/Cat.java').decode().splitlines()[335:353])
        require(cat.index('super.finalizeSpawn')<cat.index('getMoonBrightness')<cat.index('CATS_SPAWN_AS_BLACK')<cat.index('return p_28137_'),'Cat literal source order no longer matches correction')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Cat nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Cat accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==33,'Cat all33 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Cat explicit typed native check missing')
        verified.append(validate_cat_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==5,'Cat all5 actual base-resource checks required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'Cat raw resources are support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'Cat fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z: entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_read'] is True,'Cat base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'Cat primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_with_explicit_local_derived_resource_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




SIEGE_V15_SPEC = {'id': 'EA-0032', 'canonical_record_sha256': 'f1e6a75405c0584d7ff6d3e3a96a005a2e041d90f7aeef4de127d32b86684a11', 'batch': 'batch-023.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-village-siege-attempt-wave-proposal-20261104.json', 'sha256': 'a38d2e0d8e3c9a899781ff191b051eefbf2937cb0083051453b9ccf36a1055cb'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-village-siege-wave-independent-review-20261104.json', 'sha256': '719a541236ee405bb6c7d12b1c1db30a7c4df4db07bf990f72cbdb1b574ac684'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review'}, 'native_source_hashes': ['b1faa6ac5a56d3ba6afabd1f60316b912523066067a31615d078e70b59ff075f', 'baf933f8c4b44e5313fee86e3c53f6885d8e62a9aa74ea0e6be3054951386fe1', '4378543a286d967966d0d61c1d7cbd0134e95b60ea4143563f32e9572ed4c1dc', 'f68ff73dfaae518873abccae3cd1289ece60a6244a98c6b66f84a1b214df5767', '1faa9be8a0f230a06e7d1ca65c5f1427cb23908385375479f32874cdf8c93bb5', '3ba5d92de26e214b9defe875b4c179136640bf837881be9e0d665c8dba2df9f6', 'bb88ba312fc7512aff5ab74a8265d7ad7a6936514103ad69b5aa16ba595ad011', '86546f60140daa1b3fa6befc6e09ac57751d89cb38ca7562ffdfe779aa45bafc', '30a11817b25e412a2bb49055d6e47a9ddf8e1c51f9a6e082b2bc2bccde34c8ca', 'd457a585c7ca667288eeafdc7aec0dd775ffe825c26b7471f340e9f5961ebe01', '99220cbf91d0ba8cc0c9d27547e0c789204985474e60d5f1be822d1553ba144b', 'ac992a21d4608a221b618e8e0c5c161d8bce676fe496acbc755fea61131f34a7'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_siege_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in SIEGE_V15_SPEC['native_source_hashes'], 'Siege native outside exact12-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Siege native cannot impersonate Git')
    artifact = SIEGE_V15_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == SIEGE_V15_SPEC['coordinate'], 'Siege native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Siege native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Siege native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Siege native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Siege native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_siege_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=SIEGE_V15_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0032.json').resolve(),'Siege exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'Siege original author identity mismatch')
    require(spec['id'] in batches_by_id,'Siege actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'Siege complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'Siege exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','Siege one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'Siege complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'Siege corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'Siege non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and r['migration_owner']==[] and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'Siege execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'Siege immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'Siege frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Siege author cannot be own independent reviewer')
    require(m['reviewer']=='coordinator/Main; distinct from original General author' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='bounded complete source policy independently reviewed; recommend at most1; formal0 pending reviewed minimum package, actual original author receipt and existing strict aggregation','Siege distinct max1 preformal Main review required')
    require(m['actual_native_read_ranges']==[{k:v for k,v in x.items() if k!='raw_excerpt_utf8'} for x in q['actual_native_read_ranges']],'Siege all12 Main native range descriptors required')
    require(m['actual_raw_base_resource_reads']==[{k:v for k,v in x.items() if k!='raw_utf8'} for x in q['actual_raw_base_resources']] and r['raw_base_resource_bindings']==q['actual_raw_base_resources'],'Siege exact raw resource context required')
    require(m['prior_own_native_support_reused']==[dict({k:v for k,v in x.items() if k!='raw_excerpt_utf8'},reuse_credit=0,current_actual_read_basis='Exact ownMainCat or Allay source coverage verified; no fresh reread claimed') for x in q['prior_actual_native_context_reused_not_new_read_credit']] and r['prior_native_context_bindings']==q['prior_actual_native_context_reused_not_new_read_credit'],'Siege exact12 prior native reuse required')
    current=list(q['mandatory_constraints']);current[15]=m['independent_findings'][15]
    require(r['observation']==m['independent_findings'] and r['mandatory_corrections']==m['mandatory_corrections'] and r['mandatory_constraints']==current and r['mandatory_package_constraints']['current_corrected_author_constraints']==current,'Siege current corrected whole constraints required')
    require(m['semantic_comparison_rationale']==m['independent_findings'][15]==r['deduplication']['current_whole_policy_comparison'] and r['deduplication']['author_prior_bindings_without_superseded_difference']==[{k:v for k,v in x.items() if k!='difference'} for x in q['prior_whole_decisions']] and r['deduplication']['historical_original_differences_not_current_semantic_proof'] is True and r['mandatory_package_constraints']['historical_original_comparison_strings_superseded'] is True,'Siege historical copied Cat comparison cannot supply current proof')
    for prior in q['prior_whole_decisions']+[x['actual_complete_decision_read'] for x in m['prior_whole_decision_bindings']]+[m['prior_own_complete_review_basis']]:
        require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Siege exact prior decision changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'Siege native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_context_reused_not_new_read_credit']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'Siege original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Siege complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Siege prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Siege nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Siege accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==12,'Siege all12 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Siege explicit typed native check missing')
        verified.append(validate_siege_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==1,'Siege one actual base-resource check required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'Siege raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'Siege fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True,'Siege base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'Siege primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_with_explicit_local_derived_resource_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




PHANTOM_V16_SPEC = {'id': 'EA-0033', 'canonical_record_sha256': 'bd95dcf5e72c6e3cef2a1a97baf2d41eed643fcf49a35e693ca75e37b53275c4', 'batch': 'batch-024.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-phantom-insomnia-player-group-proposal-20261104.json', 'sha256': 'c1a7e3554ed3cbed6dc500febe9b4e3c995dc154e33b4b2eec1f5b24204b152e'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-phantom-rest-debt-independent-review-20261104.json', 'sha256': '10e1e40cdcbac67e7b862c828c9dc2f3ecae906cfad4f0abc09f521c6cff33e2'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review'}, 'native_source_hashes': ['8f1a2528a585d7780ece1d26a9a2b3bf3d54957d874cbc83984dd75001c64962', '97ae786d8bd3d667302a348c89e9a5083bf4e14ef9acf667f53f4602902822a3', '2912e31f00d578d08dc79799851ccc6acd9934e470b21add78296ffdc52677c8', '4b5c705071f472cfcdfded8ad7b24663a9644cd57bb24767b7590533962488df', '0c9575cb5a2df114e7775bb5e3161a6e9c57742538ffeee4222dab4ee91fe5ec', '3c9daffb575bd5b693bed79cf72ae942ad380ff000df91ea40b27c213ee7f682', 'f34c1618fc35d69906333b2f114d50ff22b5137459a91b3a1047b12db6302ae2', 'cd488a3b0b911101796f2e6c18b1d31eb75ff405f6fc8467d0199ac2cc51c54f', '35ccf9edd6b88508d2cb931e609a45645aa8c9f71595378957f61838e3bbcef6', '1fe80fc591c1166a80c6c4f50171049e9e2f98514828134d293c36a685150e13', 'c2981073175668c5a4489b15a605312cd679dcc33a29bfedeeecd93ed7b22bad', '9c5695c16649663fc32593437858eb406875c392ed902cc776eaf14eabc9e1c8', 'c45606cc939ad51621035b02383ceb1e099ed40e4dd95e998e743849b0cc3847', 'bc9ae0c4493f3ed1e4b52aa12add4eef58247bfddaa5f584d1720cbc07bbc43c', '4e388ed1b062709dacfb060c64518609cb71aa308e3660c683885995c34a6415', 'c9b365ab66391a940786d5a9db5560284c13858be6fa4106bd5c9bf7f9d1c506', '1b908aabf16d5eeb5baf560195b9bb2351ebf08354f95e622b5c89610a5846dd'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_phantom_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in PHANTOM_V16_SPEC['native_source_hashes'], 'Phantom native outside exact17-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Phantom native cannot impersonate Git')
    artifact = PHANTOM_V16_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == PHANTOM_V16_SPEC['coordinate'], 'Phantom native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Phantom native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Phantom native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Phantom native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Phantom native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_phantom_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=PHANTOM_V16_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0033.json').resolve(),'Phantom exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'Phantom original author identity mismatch')
    require(spec['id'] in batches_by_id,'Phantom actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'Phantom complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'Phantom exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','Phantom one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'Phantom complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'Phantom corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'Phantom non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and r['migration_owner']==r['frozen_mechanism_context']['proposal']['existing_global_migration_whole_owners'] and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'Phantom execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'Phantom immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'Phantom frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Phantom author cannot be own independent reviewer')
    require(m['reviewer']=='coordinator/Main; independent of original General author' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='whole bounded source policy independently reviewed; recommend atmost1, formal0 pending actual minimum package/author receipt/strict aggregation','Phantom distinct max1 preformal Main review required')
    require(m['actual_native_read_ranges']==[{k:v for k,v in x.items() if k!='raw_excerpt_utf8'} for x in q['actual_native_read_ranges']],'Phantom all17 Main native range descriptors required')
    require(m.get('actual_raw_base_resource_reads', [])==[{k:v for k,v in x.items() if k!='raw_utf8'} for x in q.get('actual_raw_base_resources', [])] and r['raw_base_resource_bindings']==q.get('actual_raw_base_resources', []),'Phantom exact raw resource context required')
    require(m['prior_own_native_support_reused']==[dict({k:v for k,v in x.items() if k!='raw_excerpt_utf8'},new_complete_old_source_read_claimed=False) for x in q['prior_actual_native_context_reused_not_new_read_credit']] and r['prior_native_context_bindings']==q['prior_actual_native_context_reused_not_new_read_credit'],'Phantom exact12 prior native reuse required')
    current=list(q['mandatory_constraints']);current[14]=m['independent_findings'][13]
    require(r['observation']==m['independent_findings'] and r['mandatory_corrections']==m['mandatory_corrections'] and r['mandatory_constraints']==current and r['mandatory_package_constraints']['current_corrected_author_constraints']==current,'Phantom current corrected whole constraints required')
    require(m['semantic_comparison_rationale']==m['independent_findings'][13]==r['deduplication']['current_whole_policy_comparison'] and r['deduplication']['author_prior_bindings_without_superseded_difference']==[{k:v for k,v in x.items() if k!='difference'} for x in q['prior_whole_decisions']] and r['deduplication']['historical_original_differences_not_current_semantic_proof'] is True and r['mandatory_package_constraints']['historical_original_comparison_strings_superseded'] is True,'Phantom historical copied Cat comparison cannot supply current proof')
    for prior in q['prior_whole_decisions']+[x['actual_complete_decision_read'] for x in m['prior_whole_decision_bindings']]+m['prior_own_complete_review_basis']:
        require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Phantom exact prior decision changed')
    require(r['migration_owner']==q['existing_global_migration_whole_owners']==m['existing_global_migration_whole_owners'] and len(r['migration_owner'])==1,'Phantom existing whole migration owner context required')
    ledger=snap.read(ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl')
    rows=[json.loads(line) for line in ledger.decode().splitlines() if line.strip()]
    for owner in r['migration_owner']:
        found=[x for x in rows if x.get('candidate_id')==owner['candidate_id']]
        require(len(found)==1 and sha(canonical(found[0]))==owner['canonical_complete_row_sha256'] and found[0]['status']=='accepted' and type(found[0]['credit']) is int and found[0]['credit']==1,'Phantom exact retained whole owner changed')
        require({k:v for k,v in found[0].items() if k!='evidence'}==owner['actual_current_non_evidence_decision_fields'],'Phantom complete retained non-evidence owner decision changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'Phantom native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_context_reused_not_new_read_credit']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'Phantom original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Phantom complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Phantom prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Phantom nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Phantom accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==17,'Phantom all17 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Phantom explicit typed native check missing')
        verified.append(validate_phantom_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==0,'Phantom no raw resource checks invented')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'Phantom raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'Phantom fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True,'Phantom base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'Phantom primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_with_explicit_local_derived_resource_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




PATROL_V17_SPEC = {'id': 'EA-0034', 'canonical_record_sha256': '2cc3f68c484b0840485863d6266da8d75973e08a5cb65481b24b82c1ae6239c6', 'batch': 'batch-025.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-patrol-captain-first-group-proposal-20261104.json', 'sha256': 'f64a426552954538983c298e7f110174dfde6f6d57ad0274f4b5c3156ac10c0f'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-patrol-captain-group-independent-review-20261104.json', 'sha256': '6d840bd1de72b0274b4103a168588a01a90d9b1eed1ce146ccdb2e8113f705c2'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review'}, 'native_source_hashes': ['39cb305a366cd84e2af82208fbc3460ebf794bf16eb8289f33235d10b24230bd', '87c88d1a61011dbe1bbe2ababbf1c629ba642960196d74bf103fea1d164ba0b8', '3bec9f1c36ba7b2c904b75e8c1590ccb75934ef6d04b22a1f555efb9f6331926', '3ff51bab3c5d33352284b88e0223fe7abbc97782a090283ad9935b3881473be8', 'f7d5ef73d5f68fecf9e47ee694d5a16ab1690c968cedc69f3f3557d29372703f', '1c42c477b00881599192625bf3d5465234a65b41a74aff7a119854548af345f4', 'caf2e490c5f9d6854bb4dae43fcc4c9d6404315032159bf1cfde903f4eac0eb1'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_patrol_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in PATROL_V17_SPEC['native_source_hashes'], 'Patrol native outside exact7-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Patrol native cannot impersonate Git')
    artifact = PATROL_V17_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == PATROL_V17_SPEC['coordinate'], 'Patrol native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Patrol native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Patrol native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Patrol native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Patrol native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_patrol_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=PATROL_V17_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0034.json').resolve(),'Patrol exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'Patrol original author identity mismatch')
    require(spec['id'] in batches_by_id,'Patrol actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'Patrol complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'Patrol exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','Patrol one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','additional_independent_literal_header_bindings','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'Patrol complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'Patrol corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'Patrol non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and r['migration_owner']==r['frozen_mechanism_context']['proposal']['existing_global_migration_whole_owners'] and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'Patrol execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'Patrol immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'Patrol frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Patrol author cannot be own independent reviewer')
    require(m['reviewer']=='coordinator/Main independent of original General author' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='bounded whole original-source policy reviewed; recommend atmost1, no formal credit before minimum reviewed package/actual authorreceipt/strictaggregation','Patrol distinct max1 preformal Main review required')
    require(m['actual_native_read_ranges']==[{k:v for k,v in x.items() if k!='raw_excerpt_utf8'} for x in q['actual_native_read_ranges']],'Patrol all7 Main native range descriptors required')
    require(m.get('actual_raw_base_resource_reads', [])==[{k:v for k,v in x.items() if k!='raw_utf8'} for x in q.get('actual_raw_base_resources', [])] and r['raw_base_resource_bindings']==q.get('actual_raw_base_resources', []),'Patrol exact raw resource context required')
    require(m['prior_own_native_support_reused']==[dict({k:v for k,v in x.items() if k!='raw_excerpt_utf8'},current_new_read_claimed=False) for x in q['prior_actual_native_context_reused_not_new_read_credit']] and r['prior_native_context_bindings']==q['prior_actual_native_context_reused_not_new_read_credit'],'Patrol exact18 prior native reuse required')
    current=list(q['mandatory_constraints']);current[13]=m['independent_findings'][12]
    require(r['observation']==m['independent_findings'] and r['mandatory_corrections']==m['mandatory_corrections'] and r['mandatory_constraints']==current and r['mandatory_package_constraints']['current_corrected_author_constraints']==current,'Patrol current corrected whole constraints required')
    require(m['semantic_comparison_rationale']==m['independent_findings'][12]==r['deduplication']['current_whole_policy_comparison'] and r['deduplication']['author_prior_bindings_without_superseded_difference']==[{k:v for k,v in x.items() if k!='difference'} for x in q['prior_whole_decisions']] and r['deduplication']['historical_original_differences_not_current_semantic_proof'] is True and r['mandatory_package_constraints']['historical_original_comparison_strings_superseded'] is True,'Patrol historical copied Cat comparison cannot supply current proof')
    for prior in q['prior_whole_decisions']+[x['actual_complete_decision_read'] for x in m['prior_whole_decision_bindings']]+m['prior_own_complete_review_basis']:
        require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Patrol exact prior decision changed')
    require(r['migration_owner']==q['existing_global_migration_whole_owners']==m['existing_global_migration_whole_owners'] and len(r['migration_owner'])==1,'Patrol existing whole migration owner context required')
    ledger=snap.read(ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl')
    rows=[json.loads(line) for line in ledger.decode().splitlines() if line.strip()]
    for owner in r['migration_owner']:
        found=[x for x in rows if x.get('candidate_id')==owner['candidate_id']]
        require(len(found)==1 and sha(canonical(found[0]))==owner['canonical_complete_row_sha256'] and found[0]['status']=='accepted' and type(found[0]['credit']) is int and found[0]['credit']==1,'Patrol exact retained whole owner changed')
        require({k:v for k,v in found[0].items() if k!='evidence'}==owner['actual_current_non_evidence_decision_fields'],'Patrol complete retained non-evidence owner decision changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'Patrol native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_context_reused_not_new_read_credit']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'Patrol original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Patrol complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Patrol prior exact native context changed')
    require(r['additional_independent_literal_header_bindings']==m['additional_actual_literal_header_reads'] and len(m['additional_actual_literal_header_reads'])==3,'Patrol all3 literal Main inheritance header bindings required')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in m['additional_actual_literal_header_reads']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and sha(b)==ref['entry_sha256'] and type(lo) is int and type(hi) is int and 1<=lo==hi<=len(b.splitlines()),'Patrol literal header fixed identity or range changed')
            require(sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and type(ref['range_credit']) is int and ref['range_credit']==0 and ref['actual_current_literal_header_read'] is True,'Patrol exact supporting0 header bytes changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Patrol nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Patrol accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==7,'Patrol all7 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Patrol explicit typed native check missing')
        verified.append(validate_patrol_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==1,'Patrol one exact raw base resource check required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'Patrol raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'Patrol fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True,'Patrol base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'Patrol primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_with_explicit_local_derived_resource_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



ENDERPEARL_V18_SPEC = {'id': 'EA-0035', 'canonical_record_sha256': '5ebee478d4dc5f6a516afc90dde04410a27fd732011b865fe2df18eb66fa6196', 'batch': 'batch-026.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-enderpearl-origin-temporary-encounter-proposal-20261104.json', 'sha256': '081e87208abff6a1998e7fbdec3ef339308879752e4176c02dba81f830bde8ad'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-enderpearl-temporary-encounter-independent-review-20261104.json', 'sha256': 'b7e96347b5d90d233fe1b669e6f37f5ebf82c17c0462f95096e37502a3684102'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review'}, 'native_source_hashes': ['b789e064c72f2bc9318af0279c09bec41eb5e47cc22aacf8c840a1da07bb49f3', '32ef721d1af46abb17ccddca7a25cecbf3ffdcd53f658a0dd6ec83f432294e16', 'c93b197ee67bec37c0ccc8dde482f4b92904ba7c2b87231ac52f2062b1d30ac7', '7dc066d02d0aaf6303096aea9859ea3a7087c7fe1076fdcbd06adea1ec4e7c45', '218d58f3c1bc3eb2dffa6a4d001bb223a8014bb5a4ea6c0ae3fbb28545c95584', '60dccf559500b473e2268127da71bc4c28434fc296df99fa13ed5b169e62552f', 'a6dcc0dfe1e5c36df970eb344d06b3420dce5edc0d2391a68c1e87601bf2b399', 'a254b0984ad65bf2b658a7179fad636843f92b72a860630f4fec83c86b5c0ccb', '41602d436201b075d9662edd10f023d311ac64148d245c8d1ec50f14f7fb996b', '6e12f5d291a761a3c5ddf2ac3eb3b7c4d7e43fc445e9cd14b92737242314c066', 'dc1e59e03580a96eb0c02092538085a8f09c5c2798d9737e96dd1c652b09b65c', 'dd924dfc80ede2bed7cc7d108d3cd893816d1f10ab1ddafc5f5321e973f4a01a', '5b0ea327cd8dbc7b45aa81e4512056539e717ab3b8c51d520d566a839a8f3bf8', '70aea24c9a4b079b46c3feaa71ec0f420e94a6a2b156150823be5bc5a2531598', 'c41fdb5dcf41cb668e07e25eb20d8755d45821e8afb7ea8c386b0ccf8ca2b2db', '532a4bcaacbc6645d7f6f975611166414214645af6f4f161f44ffe883166f9e3', '08fe7dc4b8498e0a29c2f520a0d6df9219bd52c4d40990e50f20d9413f560410'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_enderpearl_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in ENDERPEARL_V18_SPEC['native_source_hashes'], 'EnderPearl native outside exact17-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'EnderPearl native cannot impersonate Git')
    artifact = ENDERPEARL_V18_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == ENDERPEARL_V18_SPEC['coordinate'], 'EnderPearl native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'EnderPearl native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'EnderPearl native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'EnderPearl native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'EnderPearl native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_enderpearl_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=ENDERPEARL_V18_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0035.json').resolve(),'EnderPearl exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'EnderPearl original author identity mismatch')
    require(spec['id'] in batches_by_id,'EnderPearl actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'EnderPearl complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'EnderPearl exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','EnderPearl one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'EnderPearl complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'EnderPearl corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'EnderPearl non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and [{k:v for k,v in x.items() if k!='actual_current_non_evidence_decision_fields'} for x in r['migration_owner']]==r['frozen_mechanism_context']['proposal']['existing_whole_directions_excluded'] and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'EnderPearl execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'EnderPearl immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'EnderPearl frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'EnderPearl author cannot be own independent reviewer')
    require(m['reviewer']=='Main distinct independent source-policy reviewer' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='BOUNDED_COMPLETE_SOURCE_POLICY_RECOMMEND_MAXIMUM_ONE_PENDING_MINIMUM_DELTA_AND_REAL_AUTHOR_CONFIRMATION','EnderPearl distinct max1 preformal Main review required')
    require(m['actual_native_read_ranges']==q['actual_native_read_ranges'],'EnderPearl all17 Main native range descriptors required')
    require(m.get('actual_raw_base_resource_reads', [])==[{k:v for k,v in x.items() if k!='raw_utf8'} for x in q.get('actual_raw_base_resources', [])] and r['raw_base_resource_bindings']==q.get('actual_raw_base_resources', []),'EnderPearl exact raw resource context required')
    require(m['prior_own_native_support_reused']==[dict(x,**{'main_prior_actual_review': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-allay-music-duplication-independent-review-20261104.json', 'main_prior_actual_review_sha256': '689989895b706a6bd696f7cae80725a375c9b820b2d8b48b4d6163af81799a30', 'new_semantic_credit': 0, 'fresh_source_reread_claimed': False}) for x in q['prior_actual_native_admission_support_reused']] and r['prior_native_context_bindings']==q['prior_actual_native_admission_support_reused'],'EnderPearl exact3 prior native reuse required')
    current=list(q['mandatory_constraints'])
    require(r['observation']==m['independent_findings'] and r['mandatory_corrections']==m['mandatory_corrections'] and r['mandatory_constraints']==current and r['mandatory_package_constraints']['current_author_constraints']==current,'EnderPearl unchanged current whole author constraints and distinct Main findings required')
    require(m['semantic_comparison_rationale']==m['independent_findings'][13]==r['deduplication']['current_whole_policy_comparison'] and r['deduplication']['author_prior_whole_decisions']==q['prior_whole_decisions']==m['prior_whole_decision_bindings']==r['deduplication']['independent_Main_prior_decisions'] and r['deduplication']['original_author_comparisons_retained'] is True and r['mandatory_package_constraints']['corrections_required'] is False and m['mandatory_corrections']==[],'EnderPearl actual original and Main whole comparisons must remain current and exact')
    for prior in q['prior_whole_decisions']+q['continuation_checkpoints']+[dict(path='docs/cod4/audit-20261022/ecology-availability-research/coordinator-allay-music-duplication-independent-review-20261104.json',sha256='689989895b706a6bd696f7cae80725a375c9b820b2d8b48b4d6163af81799a30')]:
        require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'EnderPearl exact prior decision changed')
    require([{k:v for k,v in x.items() if k!='actual_current_non_evidence_decision_fields'} for x in r['migration_owner']]==q['existing_whole_directions_excluded']==m['existing_whole_directions_excluded'] and len(r['migration_owner'])==3,'EnderPearl existing whole migration owner context required')
    ledger=snap.read(ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl')
    rows=[json.loads(line) for line in ledger.decode().splitlines() if line.strip()]
    for owner in r['migration_owner']:
        found=[x for x in rows if x.get('candidate_id')==owner['candidate_id']]
        require(len(found)==1 and sha(canonical(found[0]))==owner['canonical_complete_row_sha256'] and found[0]['status']=='accepted' and type(found[0]['credit']) is int and found[0]['credit']==1,'EnderPearl exact retained whole owner changed')
        require({k:v for k,v in found[0].items() if k!='evidence'}==owner['actual_current_non_evidence_decision_fields'],'EnderPearl complete retained non-evidence owner decision changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'EnderPearl native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_admission_support_reused']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'EnderPearl original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'EnderPearl complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'EnderPearl prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'EnderPearl nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'EnderPearl accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==17,'EnderPearl all17 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'EnderPearl explicit typed native check missing')
        verified.append(validate_enderpearl_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==0,'EnderPearl no raw resource checks invented')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'EnderPearl raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'EnderPearl fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True,'EnderPearl base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'EnderPearl primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_with_explicit_local_derived_resource_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



SILVERFISH_V19_SPEC = {'id': 'EA-0036', 'canonical_record_sha256': '37c59b53bc034d757c1b5cd41c4b9b40282b395a3c0f7f23e9e9a952ac475b78', 'batch': 'batch-027.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-silverfish-dormant-habitat-disturbance-proposal-20261104.json', 'sha256': '4ae7bb7a8b4620ebf1d97c7d6f5b5dbe9f2ebb05e84cd426a4c423b9e10a897f'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-silverfish-latent-habitat-independent-review-20261104.json', 'sha256': 'e33284c09855a1963b982ebe16da1465c54aedcecb9ca3c29fddebe1e26d4ccf'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review'}, 'native_source_hashes': ['998b19826bde6b86e40245452cc85375c80f376e450920f10abbcb5e19e43749', 'dab36759f6f104550f6312dd489112a83d6df446fb09b4b4cce5fc047a4dc0b1', '520b983eaf6107ceab6d7388a68efae0108deefea0e86cf2bfae10b24f31f253', '5c27c56d83a9c6eb3f48978ef2df845114823554b76c77c370922459238d9ea8', '904845f7678d0e5a7bfc8581024d8a8252bb03a36e8d7da1b4ba183ed81e87e3', 'c64bbc8664605582bb99d308f89b3bfd376bd09152442d981d45515a41e2bd82', '24a3f4c3b91678255f5207c17f822b680eb9a81067cc0f92bd823991b28db158', '7b1bbdf7d1266f22cc518752a55e42b61ee3ac3942a973640e78766681a0b1d2', 'c6f80a95ed61e86725e4c88bcdf729f03ca1fd77b0e567cf8000aa517ff5f580', 'a1fd42488206decdf3a2dd39d64b08b4b03f3a3c2e14d27d4e0492b50c5dd23b', 'a939490adce2bd048d6c692504bf59bf1b4316b2e4ed4a52aa4b05a2a1d22cca', 'f7f4e16d375470472dd524fba147630fc5ebf494c7b1b550aaaad37f32ee03e3', '4b782c48e3dce139beb69b342b9b2035f6bd57fd47bc32bdd98667505f30e857', 'ccd858408191dd4cef440e42e2865c182ad781a901bd05ec14888bbb5bdbdf9b', '0b745c166c84cf99083ba3785a71040126695e4dc30d830d5e5e1082a7faf3f3', '12854e35516e093c34fb976da1d178b625cb65176f35b998caf4639d609dbb8e'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_silverfish_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in SILVERFISH_V19_SPEC['native_source_hashes'], 'Silverfish native outside exact16-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Silverfish native cannot impersonate Git')
    artifact = SILVERFISH_V19_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == SILVERFISH_V19_SPEC['coordinate'], 'Silverfish native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Silverfish native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Silverfish native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Silverfish native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Silverfish native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_silverfish_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=SILVERFISH_V19_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0036.json').resolve(),'Silverfish exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'Silverfish original author identity mismatch')
    require(spec['id'] in batches_by_id,'Silverfish actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'Silverfish complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'Silverfish exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','Silverfish one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'Silverfish complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'Silverfish corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'Silverfish non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and r['migration_owner']==[] and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'Silverfish execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'Silverfish immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'Silverfish frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Silverfish author cannot be own independent reviewer')
    require(m['reviewer']=='Main distinct independent complete source-policy reviewer' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='BOUNDED_WHOLE_LATENT_HABITAT_DISTURBANCE_POLICY_MAXIMUM_ONE_PENDING_FORMAL_DELTA','Silverfish distinct max1 preformal Main review required')
    require(m['actual_native_read_ranges']==q['actual_native_read_ranges'],'Silverfish all16 Main native range descriptors required')
    require(m['actual_raw_base_resource_reads']==q['actual_raw_base_resource_reads']==r['raw_base_resource_bindings'],'Silverfish exact raw resource context required')
    require(m['prior_own_native_support_reused']==[dict(x,**{'main_prior_actual_review': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-allay-music-duplication-independent-review-20261104.json', 'main_prior_actual_review_sha256': '689989895b706a6bd696f7cae80725a375c9b820b2d8b48b4d6163af81799a30', 'new_credit': 0, 'fresh_source_reread': False}) for x in q['prior_actual_native_admission_support_reused']] and r['prior_native_context_bindings']==q['prior_actual_native_admission_support_reused'],'Silverfish exact3 prior native reuse required')
    current=list(q['mandatory_constraints'])
    require(r['observation']==m['independent_findings'] and r['mandatory_corrections']==m['mandatory_corrections'] and r['mandatory_constraints']==current and r['mandatory_package_constraints']['current_author_constraints']==current,'Silverfish unchanged current whole author constraints and distinct Main findings required')
    require(m['semantic_comparison_rationale']==m['independent_findings'][13]==r['deduplication']['current_whole_policy_comparison'] and r['deduplication']['author_prior_whole_decisions']==q['prior_whole_decisions']==m['prior_whole_decision_bindings']==r['deduplication']['independent_Main_prior_decisions'] and r['deduplication']['prior_comparison_reading']==m['prior_comparison_reading'] and r['deduplication']['original_author_comparisons_retained'] is True and r['mandatory_package_constraints']['corrections_required'] is False and m['mandatory_corrections']==[],'Silverfish actual original and Main whole comparisons must remain current and exact')
    for prior in q['prior_whole_decisions']+[dict(path='docs/cod4/audit-20261022/ecology-availability-research/coordinator-allay-music-duplication-independent-review-20261104.json',sha256='689989895b706a6bd696f7cae80725a375c9b820b2d8b48b4d6163af81799a30')]:
        require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Silverfish exact prior decision changed')
    require(r['migration_owner']==[] and d['migration_owner']==[],'Silverfish no global owner or novelty may be invented')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'Silverfish native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_admission_support_reused']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'Silverfish original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Silverfish complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Silverfish prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Silverfish nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Silverfish accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==16,'Silverfish all16 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Silverfish explicit typed native check missing')
        verified.append(validate_silverfish_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==1,'Silverfish exactly one raw base resource check required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'Silverfish raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'Silverfish fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_read'] is True and type(ref['support_credit']) is int and ref['support_credit']==0 and ref['current_runtime_membership_proved'] is False,'Silverfish base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'Silverfish primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_with_explicit_local_derived_resource_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



GORILLA_V20_SPEC = {'id': 'EA-0037', 'canonical_record_sha256': '4d9216f95bf288adcf296bb8c6560e777b9eeddf13aeec658d8781b94b30dfff', 'batch': 'batch-028.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-gorilla-native-caravan-whole-policy-proposal-20261104.json', 'sha256': 'b70784bd10040e0832a0f201d37882544fbe04e9ed0241906ab5a489ef30220f'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-root-anchored-caravan-independent-review-20261104.json', 'sha256': '6c4cf25a1498ec133d062540f422c4f75921ded0451f209eb16f5d6166a79c88'}, 'complete_chain_current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-gorilla-caravan-package-normalization-20261104.json', 'sha256': '6ddfb28bd8a3aa9146a5288aa8b6d1718a7eac975370e3d50d8b74d3d89ca811'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_current_normalization': 'current_constraint_normalization'}, 'native_source_hashes': ['bbfa32278eec888a3fbc3d9d0a5d6997b24aae4ed56c87c571b67bbbaab9bb1e', '264de45c7ffbf9df80ac2f20bbf377f73271710006f1a5905d1df9644c4631cd', 'b120695b613ff0d8262bbe58e33f6e7d8b56486b3f9fd57784caefd0fc5a255e', 'e9eb9723bb1ac49c1e0168f8450b4d8cfba91aa18bcf21517d0c8c2fe24fd44f'], 'mod_source_hashes': ['56145f6c044d654005ae04dbdc94548a2a4800df4d8767b8e139271ea649fb6d', '087d03fc9da29f5e069f88f3350e38a72bcf0f2fd1f69e7c92c7b59753a578de', 'c7cca9193e7b0d851ab6c0e740b8be0d6957ff3436a4bea8ca5cfb37b5c9b780', '6d3e64a066627e2e1967fe12a091660938b9b0202a753136f54d325d448e9716', '3c157b091ac658a76e834d04fbaa54e8a6bd35c9719fa0dd23a22d24f5287217', 'e31d0ee369daacb505045e6d5219af61da5a7da49e740151a2fd2c9ac4d3d1ef', 'a6a5924ef1be90190fe8af653c00ece89c5c7a63a8a9cd36b00b5012e170707f', '9b137b66278df5da4b1215a122a5b15eddb253f6a616e39449da6cc383329e2e'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is the distinct Main review, not self-review'}


def validate_gorilla_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in GORILLA_V20_SPEC['native_source_hashes'], 'Gorilla native outside exact4-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Gorilla native cannot impersonate Git')
    artifact = GORILLA_V20_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == GORILLA_V20_SPEC['coordinate'], 'Gorilla native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Gorilla native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Gorilla native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Gorilla native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Gorilla native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_gorilla_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=GORILLA_V20_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0037.json').resolve(),'Gorilla exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'Gorilla original author identity mismatch')
    require(spec['id'] in batches_by_id,'Gorilla actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'Gorilla complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'Gorilla exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','Gorilla one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','migration_metadata_screen_only','mixed_source_family_boundary','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'Gorilla complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'Gorilla corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'Gorilla non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and r['migration_owner']==[] and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'Gorilla execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'Gorilla immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'Gorilla frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Gorilla author cannot be own independent reviewer')
    require(m['reviewer']=='coordinator/Main; independent of original General author' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='whole bounded source policy independently reviewed; recommend atmost1 merged native-derived caravan family, formal0 pending minimum package/actual author receipt/strict aggregation','Gorilla distinct max1 preformal Main review required')
    norm=r['frozen_mechanism_context']['current_constraint_normalization']
    require(norm['original_proposal']==spec['bindings']['complete_chain_proposal'] and norm['distinct_Main_review']==spec['bindings']['complete_chain_review'] and norm['mandatory_corrections']==m['mandatory_corrections'] and norm['current_observation']==m['independent_findings'] and norm['current_whole_comparison']==m['semantic_comparison_rationale'],'Gorilla current correction provenance changed')
    require(r['observation']==m['independent_findings'] and r['mandatory_constraints']==norm['current_constraints']==r['mandatory_package_constraints']['current_author_constraints'] and r['mandatory_corrections']==m['mandatory_corrections'],'Gorilla current literal query correction and full observations required')
    require(r['deduplication']['current_whole_policy_comparison']==m['semantic_comparison_rationale'] and r['deduplication']['current_literal_query_correction']==norm['mandatory_source_correction'] and r['deduplication']['author_prior_whole_decisions_historical']==q['prior_whole_decisions'] and r['deduplication']['independent_Main_prior_decisions']==m['prior_whole_decision_bindings'] and r['deduplication']['original_prior_source_chains_reread'] is False,'Gorilla complete current whole comparison missing')
    for field in ('actual_mod_read_ranges','actual_native_read_ranges'):
        require(m[field]==[{k:v for k,v in x.items() if k!='raw_excerpt_utf8'} for x in q[field]],'Gorilla all mixed Main read descriptors required')
    require(m['fixed_mod_source']==q['fixed_mod_source'] and r['migration_owner']==[] and r['migration_metadata_screen_only']==m['migration_metadata_screen_only'] and r['prior_native_context_bindings']==[] and r['raw_base_resource_bindings']==[],'Gorilla source family boundary or invented owner/resource')
    require([(x['path'],x['sha256']) for x in m['prior_whole_decision_bindings']]==[(x['path'],x['sha256']) for x in q['prior_whole_decisions']],'Gorilla Main whole prior bindings changed')
    for prior,independent in zip(q['prior_whole_decisions'],m['prior_whole_decision_bindings']):
        b=snap.read(local_path(prior['path'],DOCS));require(sha(b)==prior['sha256'],'Gorilla prior full decision changed');j=json.loads(b)
        require({k:j[k] for k in prior['actual_complete_semantic_decision_fields']}==prior['actual_complete_semantic_decision_fields'] and independent['actual_complete_decision_fields_read']==list(prior['actual_complete_semantic_decision_fields']) and independent['support_credit']==0 and independent['old_source_chains_reread'] is False,'Gorilla exact prior complete judgment fields missing')
    prior=q['continuation_checkpoint'];require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Gorilla original actual read checkpoint changed')
    fixed=q['fixed_mod_source'];legacy=ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/AlexModGuy__AlexsMobs'
    for key in ('source_metadata','tree_metadata'):
        desc=fixed[key];require(sha(snap.read(local_path(desc['path'],legacy)))==desc['sha256'],'Gorilla pinned original metadata changed')
    tree=snap.json(local_path(fixed['tree_metadata']['path'],legacy));meta=snap.json(local_path(fixed['source_metadata']['path'],legacy));revision=fixed['revision'];entries={x['path']:x for x in tree['tree']}
    revisions=[meta[k] for k in ('sha','commit') if k in meta]
    require(fixed['repo']=='AlexModGuy/AlexsMobs' and revision=='09755dade2cfbdf14839e026d3af446f9d3ff843' and tree['sha']==revision and tree['truncated'] is False and meta['repo']==fixed['repo'] and bool(revisions) and all(x==revision for x in revisions),'Gorilla exact original Git metadata identity changed')
    for ref in q['actual_mod_read_ranges']:
        b=snap.read(local_path(ref['source_local'],legacy));lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        require(ref['repo']==fixed['repo'] and ref['revision']==revision and ref['source_metadata']==fixed['source_metadata'] and ref['tree_metadata']==fixed['tree_metadata'] and sha(b)==ref['source_sha256'] and blob==ref['git_blob_sha1']==entries[ref['path']]['sha'] and entries[ref['path']]['type']=='blob','Gorilla original mod raw/tree/blob changed')
        require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Gorilla original full raw mod excerpt changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'Gorilla native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'Gorilla original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Gorilla complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Gorilla prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Gorilla nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Gorilla accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==12,'Gorilla all12 exact typed mixed checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        native=e.get('source_kind')=='artifact_native'
        require(e.get('source_kind') in ('artifact_native','repository_git') and sha(canonical(e)) in (spec['native_source_hashes'] if native else spec['mod_source_hashes']),'Gorilla exact mixed source whitelist mismatch')
        flags=('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact') if native else policy['checks']
        require(check.get('evidence')==e and all(check.get(k) is True for k in flags),'Gorilla explicit typed mixed check missing')
        verified.append(validate_gorilla_native_source(e,snap) if native else validate_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==0,'Gorilla no raw resource checks invented')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'Gorilla raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'Gorilla fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_read'] is True and type(ref['support_credit']) is int and ref['support_credit']==0 and ref['current_runtime_membership_proved'] is False,'Gorilla base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'Gorilla primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='mixed_git_repository_and_explicit_artifact_native',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



GOLEM_V21_SPEC = {'id': 'EA-0038', 'canonical_record_sha256': 'a0712e64a2a89ee2f0835ca87eb73e689d9184cfc157f571f8afb7bc8b0ebf86', 'batch': 'batch-029.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-villager-community-golem-whole-policy-proposal-20261104.json', 'sha256': 'eae9f9c0284cf5f73cd97ec0b903e7844ec9848ad444f2ade884991f5909f590'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-villager-community-golem-independent-review-20261104.json', 'sha256': 'e084a2120126b7057082da474f73a4e8dcd3911ee4aec25462db76f2a05f8701'}, 'complete_chain_current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-villager-community-golem-package-normalization-20261104.json', 'sha256': 'ae5c2ac3d3537b743f45b56a6f9e9ad5b8025668eda5671d6536462492feb11f'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_current_normalization': 'current_constraint_normalization'}, 'native_source_hashes': ['1408dd07d0623425e201e12ef7e1a777363ab775bbe8c4de79f2c9b6f2b40571', '3d1032d5e0e5a6057d9e4379449e1f7cd9688aa1180703ebe58d161e14b4c47f', 'bf571e19e5b15c685a830a305b6240bf681fc224a2de6e5b4f25292e6d4f13e7', '32f643ecc7fc6998c90c37a638951187779fd32efe7bbd3cdf58ca50d4edd03b', '64a78f7a0e9466dd9dddd7c1e6bf0e50b56071e91e3b958cacb10fc723088de6', '03d486025ceb9f0379a7fa58e7c547b745986f62c9d802df65cb6d8f8c88e560', '41549511f6f6109f38ec68feefe675035570459ad2093fbaf2779f9028dd8337', '6fc10cd29e38c2ee8b7fc2c6bea0b40690e90ccd51c59ad396863498e57b7466', '6013c03a6a13d6ddba04e349501dc75e4d3640d5e097607d07f36b6314627c37', '4087c60ca88ae3087075ca379e2217d1db04d640fb1e0884b51b808d0186a5bb', '96ac2af457cc3ff332e9d127a8d9e2345b2e18a8aca1d9a035a7e600edfd8d63', '8e1c6739ffb7a788e6019ec6471cfbae093697f56d9d8f975adfd918de72aeb4', '997ef1354d37cd679f7199425c3fa89df40da95e53339c46c3779772472d17ad', '13fdcc029d1fe0bf03c81987dc0e6644f00694a261da5ee990773ff2f22e4395', 'c07b05603bba7202d73fc4c75fe2b1666e97599ca6d15eb77e9b796ae53f1979', 'ea54a3a60cd8fd085badfd73ec36e790403698e07d75269fce4717be6d6001e4', '3e89c5fc27d410b0980a19163afb1732158bd88f99fa885c0acb36c8d2344d26', '3c9207de0df238f0df35534afd3d7d938fa303c2473cb53c9d849876ec682c77', '80f28e44a5371e37795e76ec4b2a88365d2714ed20d052e9b68a03d57723cd46', '1424baf485425e0568bb9d14e80cc1345043de86c59facbd4551aa72de6ecec9', 'bf0d31b52ad769c4318bd6d81492f866f13d6745e257382fcf9199a98e6486d8', 'eb4d40d32fa5e755ac50aa0823bc992216146986df7e1220a43d08ebf2ec028f', '246e7bef1bee0d0fe3dbbb38a0ba54023e987937a2339769a393515cbea78bbc', '69a539e34cf46b6cde3a69f11ee0c890518c0126bd45ecae25013ba3720e2e6b', '04b29e4b3613452e62d92cfd7c1237e5f124a2a2d53e30d1de79131f31a1d95e', '8cc255e03dc363702af68e5daa643d656e135e4cd6492699f51f65f4524a60a4', '5e2898874e4962b6beb9a3a8445b6e7d5c66808d56e5093a16959defac2eef1f', '551ad8259bcf1236b17eb6c5de5eb46809be3a967b7ab53c87b18f72e33a6a5a', '632baa72ad82cdf8308098ed877fb56367152bef71c7d2727287e2d9ee4fb49a', '90d7527a752414abc5ba6b51d5232983358332caa8e76aad6ea5c109ba9d6cb7', '86c8cc4b0de98d3f20f8bd1ba8f549ae7cbebe3f90d769ee65c58aa501681295', '157b99d118b9a545e2a1c1fdd73cdaf7e6d91c9f08201696c6f36c24e23f61cf', 'ee2093f106a0849e82bdfa4172d251b473d191aed9a680fd4f2da3c71cf8963e', '15ad2fd95097aaec5f09962209923e86435f78e9efaf2bf7aa9497886f782403'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is distinct Main review, not self-review'}


def validate_golem_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in GOLEM_V21_SPEC['native_source_hashes'], 'Golem native outside exact34-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Golem native cannot impersonate Git')
    artifact = GOLEM_V21_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == GOLEM_V21_SPEC['coordinate'], 'Golem native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Golem native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Golem native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Golem native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Golem native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_golem_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=GOLEM_V21_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0038.json').resolve(),'Golem exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'Golem original author identity mismatch')
    require(spec['id'] in batches_by_id,'Golem actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'Golem complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'Golem exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','Golem one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','additional_Main_range_support_only','prior_actual_own_matching_Brain_range','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'Golem complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'Golem corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'Golem non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'Golem execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'Golem immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'Golem frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Golem author cannot be own independent reviewer')
    require(m['reviewer']=='Main coordinator independent semantic review' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='RECOMMEND_AT_MOST_ONE_WHOLE_POLICY_AFTER_QUERY_MEMBERSHIP_AND_BODY_FLUID_QUALIFICATION;FORMAL0','Golem distinct max1 preformal Main review required')
    norm=r['frozen_mechanism_context']['current_constraint_normalization']
    require(norm['original_proposal']==spec['bindings']['complete_chain_proposal'] and norm['distinct_Main_review']==spec['bindings']['complete_chain_review'] and norm['mandatory_corrections']==m['mandatory_corrections'],'Golem exact current correction provenance required')
    require(norm['original_frozen_semantic_key']==q['semantic_key']==m['semantic_key'] and r['semantic_key']==norm['current_semantic_key'],'Golem corrected eligibility-filtered query semantic key required')
    require(r['observation']==norm['current_observation']==m['independent_findings'] and r['mandatory_constraints']==norm['current_constraints']==r['mandatory_package_constraints']['current_author_constraints'] and r['mandatory_corrections']==m['mandatory_corrections'] and r['mandatory_package_constraints']['original_author_constraints_historical']==q['mandatory_constraints'] and r['mandatory_package_constraints']['corrections_required'] is True,'Golem full normalized query and literal empty-fluid observations required')
    require(r['deduplication']['current_whole_policy_comparison']==norm['current_whole_comparison']==m['semantic_comparison_rationale'] and r['deduplication']['author_prior_whole_decisions_historical']==r['deduplication']['independent_Main_prior_decisions']==q['prior_whole_decisions']==m['prior_whole_decision_bindings'] and r['deduplication']['original_prior_source_chains_reread'] is False,'Golem separate whole-policy comparison and prior complete decisions required')
    require(m['actual_native_read_ranges']==q['actual_native_read_ranges']+norm['additional_Main_range_support_only'] and len(q['actual_native_read_ranges'])==34 and len(norm['additional_Main_range_support_only'])==1 and r['additional_Main_range_support_only']==norm['additional_Main_range_support_only'],'Golem original34 and Main-only extra1 distinct scopes required')
    require(m['prior_own_native_support_reused']==q['prior_actual_native_admission_support_reused']==r['prior_native_context_bindings'] and q['actual_raw_base_resource_reads']==r['raw_base_resource_bindings']==[],'Golem prior exact3 and no invented raw resource required')
    for prior in q['prior_whole_decisions']:
        b=snap.read(local_path(prior['path'],DOCS));require(sha(b)==prior['sha256'],'Golem exact prior complete decision changed');j=json.loads(b)
        require({k:j[k] for k in prior['actual_complete_decision_fields']}==prior['actual_complete_decision_fields'] and prior['complete_old_source_chains_reread_claimed'] is False and prior['support_credit']==0,'Golem substantive prior decision fields missing')
    checkpoint=q['read_checkpoint'];require(sha(snap.read(local_path(checkpoint['path'],DOCS)))==checkpoint['sha256'],'Golem original read checkpoint changed')
    brain=norm['prior_actual_own_matching_Brain_range'];b=snap.read(local_path(brain['path'],DOCS));require(sha(b)==brain['sha256'] and r['prior_actual_own_matching_Brain_range']==brain and brain['source_reread_claimed'] is False and brain['credit']==0,'Golem prior actual own Brain support changed')
    matching=[x for x in json.loads(b)['actual_native_read_ranges'] if x['entry']==brain['entry'] and x['lines']==brain['lines'] and x['raw_excerpt_sha256']==brain['raw_excerpt_sha256']]
    require(len(matching)==1 and all(matching[0][k]==norm['additional_Main_range_support_only'][0][k] for k in ('archive','archive_sha256','coordinate','entry','entry_sha256','lines','raw_excerpt_sha256','raw_excerpt_utf8')),'Golem Main-only extra8lines not exact prior own support')
    require(r['migration_owner']==m['existing_global_migration_whole_owners'] and len(r['migration_owner'])==len(q['existing_global_migration_whole_owners'])==2,'Golem exact existing whole owners required')
    ledger=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl';rows=[json.loads(x) for x in snap.read(ledger).decode().splitlines() if x.strip()]
    for author,main in zip(q['existing_global_migration_whole_owners'],m['existing_global_migration_whole_owners']):
        matching=[x for x in rows if x['candidate_id']==author['candidate_id']]
        require(len(matching)==1 and sha(canonical(matching[0]))==author['canonical_complete_row_sha256']==main['canonical_complete_row_sha256'],'Golem retained whole owner canonical row changed')
        require({k:v for k,v in matching[0].items() if k!='evidence'}==author['actual_current_non_evidence_decision_fields']==main['actual_current_non_evidence_decision_fields'] and author['retained_credit']==main['retained_credit']==main['new_credit']==0,'Golem complete current non-evidence owner decision changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'Golem native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_admission_support_reused']+norm['additional_Main_range_support_only']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'Golem original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'Golem complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'Golem prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Golem nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Golem accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==34,'Golem all34 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Golem explicit typed native check missing')
        verified.append(validate_golem_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==0,'Golem no raw resource checks may be invented')
    resource_verified=[]
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'Golem primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_with_current_query_and_literal_fluid_correction',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



NATURAL_BUDGET_V22_SPEC = {'id': 'EA-0039', 'canonical_record_sha256': '9ef814c0437b5d10b65e3dadc763991ac703b270638af7ef2d3347fe17938807', 'batch': 'batch-030.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-natural-population-budget-whole-policy-proposal-20261104.json', 'sha256': '244d4411cb9f35e8e6223a8b706d018ecc35e0610d094c26faa38caf5f834b0a'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-natural-population-budget-independent-review-20261104.json', 'sha256': 'f68613db4382ef4c0994cb071c4b348f49727db288fe2065ee161d24969627ca'}, 'complete_chain_current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-natural-population-budget-package-normalization-20261104.json', 'sha256': '121c082e65385cd9f78a529c0755c7f1b7b77784484983af412d60210f6f9c5f'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_current_normalization': 'current_constraint_normalization'}, 'native_source_hashes': ['2f124bf39a4aeee11bc6e26555bbdabb243303259bdccd25cce11acc91564cc3', '6c94ae32c8b93dc59842bae824b32c93f904372002ee950c2ccca0fcc407df4e', '8014d30ebbbd7aa52defdd2b8dad7f88e6d106c928663f5a04525f0da11f571f', '8c1d497a85fc00d03ad4522c35a9a6e797295bb95c7b273a5714a651ad174972', 'a89eedd8c511ed8dfc7bfd57722b179ee85649558c05260113798e3c341a1744', 'e8816415ccc1962fdb59e142acb2a1f7b5d89abc6c7dd34b089659a03f5a18ac', 'b1c39d9a1ce1cd1c1456c5b70eec1cc2a4dce1f62cb78834bcbfdd82ec3167fd', '7101a26a1f0d633016ac34008b243c0a8066c91da1b6fd65a3aabae0f6b33523', '1a809a3bf41147b6cc21bf2c4c010cfe1eec5173f053d9e79b65feb9cdae72c2', 'ccd23470ad7db784fb47dfff2b666ab4efb07620153f053544e86f894de0e1ba', '252ee4ac9258113c07a381520b68cfdae8d54ecd0674b5875d2121cbe17c979e', 'dee8564cd78dd372c97a2cb47358ccfac7ed03013fb5fffd929b05e64dfb910e', 'd8d6be21cc254a7c22b68971026bd7bca10efd578d04b28b86833a595bfd2f26'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is distinct Main review, not self-review'}


def validate_natural_budget_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in NATURAL_BUDGET_V22_SPEC['native_source_hashes'], 'NaturalBudget native outside exact13-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'NaturalBudget native cannot impersonate Git')
    artifact = NATURAL_BUDGET_V22_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == NATURAL_BUDGET_V22_SPEC['coordinate'], 'NaturalBudget native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'NaturalBudget native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'NaturalBudget native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'NaturalBudget native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'NaturalBudget native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_natural_budget_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=NATURAL_BUDGET_V22_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0039.json').resolve(),'NaturalBudget exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'NaturalBudget original author identity mismatch')
    require(spec['id'] in batches_by_id,'NaturalBudget actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'NaturalBudget complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'NaturalBudget exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','NaturalBudget one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','Main_prior_native_context_bindings','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'NaturalBudget complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'NaturalBudget corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'NaturalBudget non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'NaturalBudget execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'NaturalBudget immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'NaturalBudget frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'NaturalBudget author cannot be own independent reviewer')
    require(m['reviewer']=='Main distinct independent coordinator' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='ONE_RELATED_WHOLE_POLICY_SUPPORTED_MAX1_PENDING_REAL_AUTHOR_FORMAL_PACKAGE','NaturalBudget distinct max1 preformal Main review required')
    norm=r['frozen_mechanism_context']['current_constraint_normalization']
    require(norm['original_proposal']==spec['bindings']['complete_chain_proposal'] and norm['distinct_Main_review']==spec['bindings']['complete_chain_review'] and norm['mandatory_corrections']==m['mandatory_corrections'],'NaturalBudget current correction provenance required')
    require(norm['original_frozen_semantic_key']==norm['current_semantic_key']==q['semantic_key']==m['semantic_key']==r['semantic_key'],'NaturalBudget exact whole semantic key required')
    intake=norm['prior_review_intake'];b=snap.read(local_path(intake['path'],DOCS));require(sha(b)==intake['sha256'],'NaturalBudget actual prior review intake changed')
    selected=[x for x in json.loads(b)['entries'] if x['original_proposal']==spec['bindings']['complete_chain_proposal']]
    require(selected==[norm['intake_natural_entry_only']] and norm['other_intake_entries_included'] is False,'NaturalBudget only matching intake scope required')
    require(r['observation']==norm['current_observation']==m['independent_findings']==selected[0]['current_observation'] and len(r['observation'])==16,'NaturalBudget complete Main16 findings required')
    require(r['mandatory_constraints']==norm['current_constraints']==q['mandatory_constraints']+norm['explicit_Main_supported_supplemental_constraints']==selected[0]['current_constraints_for_later_package'] and len(r['mandatory_constraints'])==22 and len(q['mandatory_constraints'])==21 and norm['all21_original_constraints_unchanged'] is True,'NaturalBudget all21 original and explicit Main supplement required')
    require(r['mandatory_constraints']==r['mandatory_package_constraints']['current_author_constraints'] and r['mandatory_package_constraints']['original_author_constraints_historical']==q['mandatory_constraints'] and r['mandatory_corrections']==m['mandatory_corrections']==selected[0]['mandatory_corrections'] and len(r['mandatory_corrections'])==3 and r['mandatory_package_constraints']['corrections_required'] is True,'NaturalBudget all three whole/admission/numeric corrections required')
    require(r['deduplication']['current_whole_policy_comparison']==norm['current_whole_comparison']==m['semantic_comparison_rationale']==selected[0]['current_whole_comparison'] and r['deduplication']['author_prior_whole_decisions_historical']==r['deduplication']['independent_Main_prior_decisions']==q['prior_whole_decisions']==m['prior_whole_decision_bindings'] and r['deduplication']['original_prior_source_chains_reread'] is False,'NaturalBudget full separate whole comparison required')
    require(m['actual_native_read_ranges']==[{k:v for k,v in x.items() if k!='raw_excerpt_utf8'} for x in q['actual_native_read_ranges']] and len(q['actual_native_read_ranges'])==13,'NaturalBudget Main exact13 descriptors omit only raw text; General raw preserved')
    require(q['prior_actual_native_admission_support_reused']==r['prior_native_context_bindings'] and len(r['prior_native_context_bindings'])==4 and m['prior_own_native_support_reused']==r['Main_prior_native_context_bindings'] and len(r['Main_prior_native_context_bindings'])==4 and q['actual_raw_base_resource_reads']==r['raw_base_resource_bindings']==[],'NaturalBudget prior exact4 and no invented raw resource required')
    for author,main in zip(q['prior_actual_native_admission_support_reused'],m['prior_own_native_support_reused']):
        require({k:v for k,v in author.items() if k!='raw_excerpt_utf8'}=={k:v for k,v in main.items() if k not in ('Main_prior_actual_read_coverage','new_semantic_read_credit')} and main['new_semantic_read_credit']==0,'NaturalBudget exact prior support projection, not new source credit')
        for p in main['Main_prior_actual_read_coverage']:
            require(sha(snap.read(local_path(p['path'],DOCS)))==p['sha256'],'NaturalBudget Main prior actual support judgment changed')
    for prior in q['prior_whole_decisions']:
        b=snap.read(local_path(prior['path'],DOCS));require(sha(b)==prior['sha256'],'NaturalBudget exact prior whole decision changed');j=json.loads(b)
        require({k:j[k] for k in prior['actual_complete_decision_fields']}==prior['actual_complete_decision_fields'] and prior['complete_old_source_chains_reread_claimed'] is False and prior['support_credit']==0,'NaturalBudget EA0003/EA0007 full substantive whole comparison required')
    checkpoint=q['read_checkpoint'];require(sha(snap.read(local_path(checkpoint['path'],DOCS)))==checkpoint['sha256'],'NaturalBudget original read checkpoint changed')
    require(r['migration_owner']==q['existing_global_migration_whole_owners']==m['existing_global_migration_whole_owners'] and len(r['migration_owner'])==1,'NaturalBudget sole existing tent whole owner required')
    ledger=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl';rows=[json.loads(x) for x in snap.read(ledger).decode().splitlines() if x.strip()]
    for owner in r['migration_owner']:
        matching=[x for x in rows if x['candidate_id']==owner['candidate_id']]
        require(len(matching)==1 and sha(canonical(matching[0]))==owner['canonical_complete_row_sha256'] and {k:v for k,v in matching[0].items() if k!='evidence'}==owner['actual_current_non_evidence_decision_fields'] and owner['new_credit']==0 and owner['embedded_prior_source_newly_read'] is False,'NaturalBudget retained tent quota-loss whole owner0 changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'NaturalBudget native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_native_admission_support_reused']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'NaturalBudget original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'NaturalBudget complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'NaturalBudget prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'NaturalBudget nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'NaturalBudget accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==13,'NaturalBudget all13 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'NaturalBudget explicit typed native check missing')
        verified.append(validate_natural_budget_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==0,'NaturalBudget no raw resource checks may be invented')
    resource_verified=[]
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'NaturalBudget primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_whole_natural_population_budget_with_exact_prior_support_projection',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



HERO_V23_SPEC = {'id': 'EA-0040', 'canonical_record_sha256': '407e6421591f2041d4798eab6352d24db764658d1408b4bb3aba96de5deb6519', 'batch': 'batch-031.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-hero-gift-whole-policy-proposal-20261104.json', 'sha256': '69166c5917751248a11729809399650fe996c807e9d637698b52282b229ae091'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-hero-gift-whole-policy-independent-review-20261104.json', 'sha256': '894d6ea2a1f77b6e981744b71c395e0711403b11c1026cebf0dec5217f021613'}, 'complete_chain_current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-hero-gift-package-normalization-20261104.json', 'sha256': '6882b750ede4594db823d1d525ec79f8d934940ec89a4319be37a5466cdeb442'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_current_normalization': 'current_constraint_normalization'}, 'native_source_hashes': ['6d97065dc724ff2c3f098b03117245fa064ed5039d5347e398bdea5b8b7d0672', '3672c61fec9df76ba1146caad99bc9ea5b582a295ad34c4f3eb5055574d4bda5', 'a9b7e02b26a86fe6f002706abbae7e06edb601aeb823d07129a7ea7d716c9fb6', 'f0dec32a6f6b307551aed98eee1d24041cdf02b2160f80e54caae20fe2113f9e', '5baf6672acc1e2a53c391f196c7c452f9d07e0718267c39d6c9540c71679e922', '90b33a16e05461c0e4a36f03ccba3a1344408c6392182a623f7768b7d566577b', '11a04fb7259e9e1dddc36d160fe70de490de760f86c19d53ad3a2eaa140f1ab3', 'b9c3caea29a5971255cc5c1a773f3b1fbd20ab66e6376ac3bc1bac2a8defef21', '5629f6c82fa654f17fa126d7395dea4d37752291108f657651f3a29472f229cb', 'bd326327d20f508a34b9b20d91b94c12562cd37683ae48f71ba9585b9bb868c2', '1762197f2c374af07f738437c428d707ed6db6af564e9063010c79e6544a64a1', 'f16d2ddb82cc7ea1ef9e28a0f234c1fd2b0507f50020ce4e9a8efa1ae50def38', '0a925449ca8049a01841cc0ae9b586fd0a01fb7e89a0c04f2018b4c248a0cce2', 'b7a81a9a1cd9af27fe62db9d07996c7d647516f8a1ed53a61e5282e45e2bb2f9'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is distinct Main review, not self-review'}


def validate_hero_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in HERO_V23_SPEC['native_source_hashes'], 'HeroGift native outside exact14-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'HeroGift native cannot impersonate Git')
    artifact = HERO_V23_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == HERO_V23_SPEC['coordinate'], 'HeroGift native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'HeroGift native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'HeroGift native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'HeroGift native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'HeroGift native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_hero_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=HERO_V23_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0040.json').resolve(),'HeroGift exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'HeroGift original author identity mismatch')
    require(spec['id'] in batches_by_id,'HeroGift actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'HeroGift complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'HeroGift exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','HeroGift one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','Main_prior_native_context_bindings','prior_global_owner_support_only','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'HeroGift complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'HeroGift corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'HeroGift non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'HeroGift execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'HeroGift immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'HeroGift frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'HeroGift author cannot be own independent reviewer')
    require(m['reviewer']=='Main distinct independent source-policy reviewer' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='BOUNDED_COMPLETE_SOURCE_POLICY_RECOMMEND_MAXIMUM_ONE_PENDING_MINIMUM_DELTA_AND_REAL_AUTHOR_CONFIRMATION','HeroGift distinct max1 preformal Main review required')
    norm=r['frozen_mechanism_context']['current_constraint_normalization']
    require(norm['original_proposal']==spec['bindings']['complete_chain_proposal'] and norm['distinct_Main_review']==spec['bindings']['complete_chain_review'] and norm['mandatory_corrections']==m['mandatory_corrections']==r['mandatory_corrections']==[],'HeroGift exact prior Main judgment and no invented correction')
    require(norm['original_frozen_semantic_key']==norm['current_semantic_key']==q['semantic_key']==m['semantic_key']==r['semantic_key'],'HeroGift exact whole semantic key required')
    intake=norm['prior_review_intake'];b=snap.read(local_path(intake['path'],DOCS));require(sha(b)==intake['sha256'],'HeroGift actual prior review intake changed')
    selected=[x for x in json.loads(b)['entries'] if x['original_proposal']==spec['bindings']['complete_chain_proposal']]
    require(selected==[norm['intake_Hero_entry_only']] and norm['other_intake_entries_included'] is False,'HeroGift matching intake only required')
    require(r['observation']==norm['current_observation']==m['independent_findings']==selected[0]['current_observation'] and len(r['observation'])==14,'HeroGift complete Main14 findings required')
    require(r['mandatory_constraints']==norm['current_constraints']==q['mandatory_constraints']+norm['explicit_Main_supported_supplemental_constraints']==selected[0]['current_constraints_for_later_package'] and len(r['mandatory_constraints'])==14 and len(q['mandatory_constraints'])==13 and q['mandatory_constraints']==m['mandatory_author_constraints_preserved'] and norm['all13_original_constraints_unchanged'] is True,'HeroGift all13 original and explicit REGISTERED memory supplement required')
    require(r['mandatory_constraints']==r['mandatory_package_constraints']['current_author_constraints'] and r['mandatory_package_constraints']['original_author_constraints_historical']==q['mandatory_constraints'] and r['mandatory_package_constraints']['corrections_required'] is False,'HeroGift full constraints and distinct no-correction provenance required')
    require(r['deduplication']['current_whole_policy_comparison']==norm['current_whole_comparison']==m['semantic_comparison_rationale']==selected[0]['current_whole_comparison'] and r['deduplication']['author_prior_whole_decision_historical']==r['deduplication']['independent_Main_prior_decision']==q['prior_complete_semantic_decision']==m['prior_complete_semantic_decision'] and r['deduplication']['global_name_screen_boundary']==q['global_screen_boundary'] and r['deduplication']['original_prior_source_chains_reread'] is False,'HeroGift full separate EA0026 comparison and bounded metadata screen required')
    require(m['actual_native_read_ranges']==q['actual_native_read_ranges'] and len(q['actual_native_read_ranges'])==14,'HeroGift exact original14 raw descriptors required')
    require(q['prior_actual_own_native_support_reused_zero']==r['prior_native_context_bindings'] and len(r['prior_native_context_bindings'])==6 and m['prior_own_native_support_reused']==r['Main_prior_native_context_bindings'] and len(r['Main_prior_native_context_bindings'])==6,'HeroGift prior exact6 source support required')
    pr=m['prior_own_source_review'];require(sha(snap.read(local_path(pr['path'],DOCS)))==pr['sha256'],'HeroGift exact Main prior Golem source review changed')
    for author,main in zip(q['prior_actual_own_native_support_reused_zero'],m['prior_own_native_support_reused']):
        require(author=={k:v for k,v in main.items() if k not in ('main_prior_actual_review','main_prior_actual_review_sha256','new_semantic_credit','fresh_source_reread_claimed')} and main['main_prior_actual_review']==pr['path'] and main['main_prior_actual_review_sha256']==pr['sha256'] and main['new_semantic_credit']==0 and main['fresh_source_reread_claimed'] is False,'HeroGift prior support provenance and0 new reading credit required')
    p=q['prior_actual_own_source_binding'];require(sha(snap.read(local_path(p['path'],DOCS)))==p['sha256'] and p['old_source_chain_reread'] is False and p['credit']==0,'HeroGift General prior Golem checkpoint changed')
    prior=q['prior_complete_semantic_decision'];b=snap.read(local_path(prior['path'],DOCS));require(sha(b)==prior['sha256'],'HeroGift exact EA0026 whole decision changed');priorj=json.loads(b)
    require({k:priorj[k] for k in prior['actual_complete_decision_fields']}==prior['actual_complete_decision_fields'] and prior['old_complete_source_chains_reread'] is False and prior['support_credit']==0,'HeroGift full Seal21 observations18 limits and substantive judgment required')
    checkpoint=q['continuation_checkpoint'];require(sha(snap.read(local_path(checkpoint['path'],DOCS)))==checkpoint['sha256'],'HeroGift original read checkpoint changed')
    require(r['raw_base_resource_bindings']==q['actual_raw_base_resources'] and len(q['actual_raw_base_resources'])==1 and m['actual_raw_base_resource_reads']==[{k:v for k,v in x.items() if k!='raw_utf8'} for x in q['actual_raw_base_resources']],'HeroGift exact derived raw armorer table projection required')
    require(r['migration_owner']==norm['Hero_migration_owners']==[],'HeroGift cannot invent own migration owner')
    owner=norm['prior_global_owner_support_only'];require(owner==r['prior_global_owner_support_only'] and owner['existing_prior_EA0026_owner_only_not_Hero_owner'] is True and owner['new_credit']==0 and owner['embedded_old_source_chains_reread'] is False and owner['candidate_id']==priorj['migration_owner']['candidate_id'] and owner['canonical_complete_row_sha256']==priorj['migration_owner']['canonical_full_row_sha256'],'HeroGift prior Seal-only migration owner0 provenance required')
    ledger=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl';rows=[json.loads(x) for x in snap.read(ledger).decode().splitlines() if x.strip()];matching=[x for x in rows if x['candidate_id']==owner['candidate_id']]
    require(len(matching)==1 and sha(canonical(matching[0]))==owner['canonical_complete_row_sha256'] and {k:v for k,v in matching[0].items() if k!='evidence'}==owner['actual_current_non_evidence_decision_fields'],'HeroGift current prior Seal whole owner changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'HeroGift native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_own_native_support_reused_zero']:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'HeroGift original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'HeroGift complete raw source range mismatch')
            prior=ref.get('prior_actual_own_source')
            if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'HeroGift prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'HeroGift nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'HeroGift accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==14,'HeroGift all14 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'HeroGift explicit typed native check missing')
        verified.append(validate_hero_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==1,'HeroGift exactly one raw derived resource support check required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'HeroGift raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'HeroGift fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True and type(ref['credit']) is int and ref['credit']==0 and ref['loaded_current_membership_proved'] is False,'HeroGift base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'HeroGift primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_Hero_social_gift_with_explicit_derived_raw_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



SHULKER_V24_SPEC = {'id': 'EA-0041', 'canonical_record_sha256': 'c97723e119ca82fa7a8781494e435ef5c703a9ea50603ef8cfb1bd041e08ce33', 'batch': 'batch-032.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-shulker-impact-replenishment-whole-policy-proposal-20261104.json', 'sha256': '98f27e0f4cadbc6aff1144517d93b5c7622f2937c54d8843670ec5f14e369e3d'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-shulker-spatial-replenishment-independent-review-20261104.json', 'sha256': 'd7cd99d56310c680494ac69acfc978474e8461c56be22b8ed63af2e4500f3106'}, 'complete_chain_current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-shulker-replenishment-package-normalization-20261104.json', 'sha256': '230d4c88ac66e8541141cd25732b18958471f18376bb60a2d2acc727f8f0e5f2'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_current_normalization': 'current_constraint_normalization'}, 'native_source_hashes': ['7d031b1fa32d30375dfbf2f1ffc0707e09694848da64c81381ccc904d21baba1', 'ed1fafe225b0e057b43cab19ad3c6a43c5d5c285b9dc6f0aa1bb1c6e0f1a69e5', '81de393a647c606cc025e41afb83e01f48e0567e2919ffde0dc5b731ccbb7d55', '2197a8dba0d1e8736faa328ea1855cfb1d927bea305ab2d5439192ad7d7ad1b9', '23438e0718d5f972d767945bb807a4ec558444e69cd6eee2a315933cf1072b8b', '7b49a50a1b7e0daf8a7fc9bce1de28251f9bf206902af6c8b69a49fafa46492f', '503dd4ccca6c777da8bd7a1a99e7b0739405da6c89b6de38c3a03122815cb4ee', '8ac53c44497df925fc88f393a22b1d7db4177ad01379a03c420f5bac19666726', 'c2d7627cfddce7cda98d04b1c3c4cf2c209096be452caa38fd6a71ea06f8127a', 'fbaba46cc83e4583c72df3c332023b346e87545482e8c7c68b70d33e0408884a', 'e59f06deb789a6d547b86c57f30879408595a1fc645fa61500762027c8ca2c1c', 'eac91c5469848a1f85389c9f89f6d588494df7282acd1c88ddffea92c1b49f92', '61628b49a74286def078968aa469621e2afa73978d09551689610bca5e8f0b0d'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is distinct Main review, not self-review'}


def validate_shulker_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in SHULKER_V24_SPEC['native_source_hashes'], 'ShulkerReplenishment native outside exact13-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'ShulkerReplenishment native cannot impersonate Git')
    artifact = SHULKER_V24_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == SHULKER_V24_SPEC['coordinate'], 'ShulkerReplenishment native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'ShulkerReplenishment native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'ShulkerReplenishment native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'ShulkerReplenishment native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'ShulkerReplenishment native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_shulker_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=SHULKER_V24_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0041.json').resolve(),'ShulkerReplenishment exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'ShulkerReplenishment original author identity mismatch')
    require(spec['id'] in batches_by_id,'ShulkerReplenishment actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'ShulkerReplenishment complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'ShulkerReplenishment exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','ShulkerReplenishment one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','Main_prior_native_context_bindings','prior_global_owner_support_only','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'ShulkerReplenishment complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'ShulkerReplenishment corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'ShulkerReplenishment non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'ShulkerReplenishment execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'ShulkerReplenishment immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'ShulkerReplenishment frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'ShulkerReplenishment author cannot be own independent reviewer')
    require(m['reviewer']=='Main distinct independent complete source-policy reviewer' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='BOUNDED_WHOLE_COMBAT_RELOCATION_SPATIAL_REPLENISHMENT_MAXIMUM_ONE_PENDING_FORMAL_DELTA','ShulkerReplenishment distinct max1 preformal Main review required')
    norm=r['frozen_mechanism_context']['current_constraint_normalization']
    require(norm['original_proposal']==spec['bindings']['complete_chain_proposal'] and norm['distinct_Main_review']==spec['bindings']['complete_chain_review'] and norm['mandatory_corrections']==m['mandatory_corrections']==q['mandatory_corrections']==r['mandatory_corrections']==[],'ShulkerReplenishment exact prior Main judgment and no invented correction')
    require(norm['original_frozen_semantic_key']==norm['current_semantic_key']==q['semantic_key']==m['semantic_key']==r['semantic_key'],'ShulkerReplenishment exact whole semantic key required')
    intake=norm['prior_review_intake'];ib=snap.read(local_path(intake['path'],DOCS));require(sha(ib)==intake['sha256'],'ShulkerReplenishment actual prior review intake changed')
    selected=[x for x in json.loads(ib)['entries'] if x['original_proposal']==spec['bindings']['complete_chain_proposal']]
    require(selected==[norm['intake_Shulker_entry_only']] and norm['other_intake_entries_included'] is False,'ShulkerReplenishment matching intake only required')
    require(r['observation']==norm['current_observation']==m['independent_findings']==selected[0]['current_observation'] and len(r['observation'])==11,'ShulkerReplenishment complete Main11 findings required')
    require(r['mandatory_constraints']==norm['current_constraints']==q['mandatory_constraints']+norm['explicit_Main_supported_supplemental_constraints']==selected[0]['current_constraints_for_later_package'] and len(r['mandatory_constraints'])==14 and len(q['mandatory_constraints'])==13 and norm['all13_original_constraints_unchanged'] is True,'ShulkerReplenishment original13 and explicit Main-only sixth prior support supplement required')
    require(r['mandatory_constraints']==r['mandatory_package_constraints']['current_author_constraints'] and r['mandatory_package_constraints']['original_author_constraints_historical']==q['mandatory_constraints'] and r['mandatory_package_constraints']['corrections_required'] is False,'ShulkerReplenishment full constraints and no-correction provenance required')
    require(r['deduplication']['current_whole_policy_comparison']==norm['current_whole_comparison']==m['semantic_comparison_rationale']==selected[0]['current_whole_comparison'] and r['deduplication']['author_prior_whole_decisions_historical']==r['deduplication']['independent_Main_prior_decisions']==q['prior_complete_semantic_decisions']==m['prior_whole_decision_bindings'] and r['deduplication']['original_prior_source_chains_reread'] is False,'ShulkerReplenishment separate complete EA30 whole comparison required')
    require(m['actual_native_read_ranges']==q['actual_native_read_ranges'] and len(q['actual_native_read_ranges'])==13 and q['actual_cited_lines']==527 and q['actual_read_entry_count']==5 and q['actual_full_file_count']==0,'ShulkerReplenishment exact General13 bounded raw descriptors not whole files required')
    require(q['prior_actual_own_native_support_reused_zero']==r['prior_native_context_bindings'] and len(r['prior_native_context_bindings'])==5 and m['prior_own_native_support_reused']==r['Main_prior_native_context_bindings'] and len(r['Main_prior_native_context_bindings'])==6,'ShulkerReplenishment General5 and distinct Main6 prior source supports required')
    for author,main in zip(q['prior_actual_own_native_support_reused_zero'],m['prior_own_native_support_reused']):
        require(author=={k:v for k,v in main.items() if k not in ('main_prior_actual_review','main_prior_actual_review_sha256','fresh_source_reread','new_credit')} and main['fresh_source_reread'] is False and main['new_credit']==0,'ShulkerReplenishment five exact prior provenance projections required')
        require(sha(snap.read(local_path(main['main_prior_actual_review'],DOCS)))==main['main_prior_actual_review_sha256'],'ShulkerReplenishment actual prior Main review changed')
    extra=m['prior_own_native_support_reused'][-1];ep=norm['Main_extra_support_actual_prior_descriptor_binding'];eb=snap.read(local_path(ep['path'],DOCS))
    require(extra==norm['Main_extra_only_prior_support'] and extra['entry']=='net/minecraft/world/entity/projectile/Projectile.java' and extra['lines']==[135,155] and extra['fresh_source_reread'] is False and extra['new_credit']==0 and ep['path']==extra['main_prior_actual_review'] and sha(eb)==ep['sha256']==extra['main_prior_actual_review_sha256'],'ShulkerReplenishment Main-only sixth prior exact actual review required')
    require([x for x in json.loads(eb)['actual_native_read_ranges'] if x['entry']==extra['entry'] and x['lines']==extra['lines']]==[ep['descriptor']],'ShulkerReplenishment prior Main extra descriptor changed')
    require(all(ep['descriptor'][k]==extra[k] for k in ('archive','archive_sha256','coordinate','entry','entry_sha256','lines','full_file','raw_excerpt_sha256','raw_excerpt_utf8')),'ShulkerReplenishment Main extra is prior support0 not General fresh source')
    for prior in q['prior_complete_semantic_decisions']:
        b=snap.read(local_path(prior['path'],DOCS));require(sha(b)==prior['sha256'],'ShulkerReplenishment exact EA30 whole decision changed');priorj=json.loads(b)
        require({k:priorj[k] for k in prior['actual_complete_decision_fields']}==prior['actual_complete_decision_fields'] and prior['old_complete_source_chains_reread'] is False and prior['support_credit']==0,'ShulkerReplenishment full corrected EA30 judgment required')
    checkpoint=q['continuation_checkpoint'];require(sha(snap.read(local_path(checkpoint['path'],DOCS)))==checkpoint['sha256'],'ShulkerReplenishment original read checkpoint changed')
    require(r['raw_base_resource_bindings']==q['actual_raw_base_resources']==m['actual_raw_base_resources'] and len(q['actual_raw_base_resources'])==1,'ShulkerReplenishment exact derived raw projectile tag required')
    require(r['migration_owner']==norm['Shulker_reproduction_migration_owners']==[],'ShulkerReplenishment cannot invent reproduction migration owner')
    owner=norm['existing_global_owner_support_only'];require(owner==r['prior_global_owner_support_only']==q['existing_global_whole_owner']==m['existing_whole_owner']==r['deduplication']['existing_whole_projectile_owner'] and owner['retained_credit']==0 and owner['embedded_old_source_whole_reread'] is False,'ShulkerReplenishment prior Bullet route owner remains sole owner support0')
    ledger=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl';rows=[json.loads(x) for x in snap.read(ledger).decode().splitlines() if x.strip()];matching=[x for x in rows if x['candidate_id']==owner['candidate_id']]
    require(len(matching)==1 and sha(canonical(matching[0]))==owner['canonical_complete_row_sha256'] and {k:v for k,v in matching[0].items() if k!='evidence'}==owner['actual_current_non_evidence_decision_fields'],'ShulkerReplenishment current complete Bullet owner changed')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'ShulkerReplenishment native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+q['prior_actual_own_native_support_reused_zero']+[extra]:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'ShulkerReplenishment original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'ShulkerReplenishment complete raw source range mismatch')
            for key in ('prior_actual_own_source','current_prior_binding'):
                prior=ref.get(key)
                if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'ShulkerReplenishment prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'ShulkerReplenishment nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'ShulkerReplenishment accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==13,'ShulkerReplenishment all13 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'ShulkerReplenishment explicit typed native check missing')
        verified.append(validate_shulker_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==1,'ShulkerReplenishment exactly one raw derived resource support check required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'ShulkerReplenishment raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'ShulkerReplenishment fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True and type(ref['credit']) is int and ref['credit']==0 and ref['loaded_current_membership_proved'] is False,'ShulkerReplenishment base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'ShulkerReplenishment primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_Shulker_spatial_replenishment_with_distinct_Main_prior_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



FARMER_V25_SPEC = {'id': 'EA-0042', 'canonical_record_sha256': '12642fc9c7eb5badd249f9207e27fd0087c88e5e3e20cef00a7eff0c34549781', 'batch': 'batch-033.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-farmer-compost-material-service-whole-policy-proposal-20261104.json', 'sha256': '1a82358a0e9eb1b5ebcc4f9a4a003aedc8078846bea6a50f830cd0aac196f0ac'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-farmer-compost-material-service-independent-review-20261104.json', 'sha256': 'fadb9ecb1c2c778ea23391d3ed26b0b70c3e44c8d98b0fd4543a867ae18a5844'}, 'complete_chain_current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-farmer-material-service-package-normalization-20261104.json', 'sha256': '242ffc384cb990c41e7681d435194d9c0b14adcef24b28feebd3ebb654fc6223'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_current_normalization': 'current_constraint_normalization'}, 'native_source_hashes': ['f64551ee5bd5946a6f85854fa12b9d601e9852162738f5db2387b7118ea3f8cf', '63a9e331a64181f9a0df752dc4abb5b21c4df4d0cf50066d459449036af6cfb9', '1b285eec65c14387d41430334d3b5c9d9b818889b288591103fc6129322afb3c', '9c08538c418516b6c17495298c2a5508b0552423a37bff10f15e2457926da0b9', '4e4ea55a080919fc9fc291a814803cb683b4b2563bc4308bf51f8ebc618354ce', '9af4d268673df4ea88433980918169c4a1d8c6c1bdaad51d4af21ca3a3832703', 'a29c634382be8d16fcb7f5864efc077b44b8c79829c1e9c6a3edba3431211e73', '4a52bcf4f730d3bc135790d66ec89da1df60a95be3f90ec634bc3b9bff2e8e33', '2ad735c671ae201fe8347ed2b97f4f585f2a647269d1e5e78dddbd09af586ea4', '619c7e548ca77be950134da9029b26ea8e1f2209619fa28cdb7f0bb1768154a6', '80e129c0615bb72833a30cacfe8b49869955dda3e696dbbbb7edfd80a21bdb39', '44d8d63820d8545a707040719c8084fd9171b6ceb3ff531297b1d27bc39ac8bd', 'f5a5bd29dd3e4054eb4db209ba212061f2b38c160254743679dd00cf9a446318', '3bea48b1b91d87cf581b081d957124f33b753dfc9dcd5dac5e2145f756638c44', '78310a3cc5a2b20b2741a7458953779eb90de62fccd71dfa002dca5e7a31c018', '47f430c546c604f77c52cfe678f9e343ce736c56d28ee86d361b09a7b0c7315d', 'f2afcf811b3d84e4a3953533eb2fbceb51d532538afed67c47b050c1aaea92eb', '15660c221370a41a6bbafc7806c66eb4a03859ffecb0389b68139611c0014406'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is distinct Main review, not self-review'}


def validate_farmer_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in FARMER_V25_SPEC['native_source_hashes'], 'FarmerMaterialService native outside exact18-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'FarmerMaterialService native cannot impersonate Git')
    artifact = FARMER_V25_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == FARMER_V25_SPEC['coordinate'], 'FarmerMaterialService native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'FarmerMaterialService native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'FarmerMaterialService native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'FarmerMaterialService native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'FarmerMaterialService native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_farmer_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=FARMER_V25_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0042.json').resolve(),'FarmerMaterialService exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'FarmerMaterialService original author identity mismatch')
    require(spec['id'] in batches_by_id,'FarmerMaterialService actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'FarmerMaterialService complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'FarmerMaterialService exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','FarmerMaterialService one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','Main_prior_native_context_bindings','prior_global_owner_support_only','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'FarmerMaterialService complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'FarmerMaterialService corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'FarmerMaterialService non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'FarmerMaterialService execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'FarmerMaterialService immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'FarmerMaterialService frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'FarmerMaterialService author cannot be own independent reviewer')
    require(m['reviewer']=='Main independent coordinator, distinct from original General author' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='ACCEPT_IN_PRINCIPLE_MAXIMUM_ONE_WHOLE_RELATED_SOURCE_POLICY_FORMAL_PENDING','FarmerMaterialService distinct max1 preformal Main review required')
    norm=r['frozen_mechanism_context']['current_constraint_normalization']
    require(norm['original_proposal']==spec['bindings']['complete_chain_proposal'] and norm['distinct_Main_review']==spec['bindings']['complete_chain_review'] and norm['mandatory_corrections']==m['mandatory_corrections']==q['mandatory_corrections']==r['mandatory_corrections']==[],'FarmerMaterialService exact Main judgment and no invented correction')
    require(norm['original_frozen_semantic_key']==norm['current_semantic_key']==q['semantic_key']==m['semantic_key']==r['semantic_key'],'FarmerMaterialService exact whole semantic key required')
    require(r['observation']==norm['current_observation']==m['independent_findings'] and len(r['observation'])==19,'FarmerMaterialService complete Main19 findings required')
    require(r['mandatory_constraints']==norm['current_constraints']==q['mandatory_constraints']==m['author_mandatory_constraints_retained'] and len(r['mandatory_constraints'])==17 and norm['all17_original_constraints_unchanged'] is True and norm['explicit_Main_supported_supplemental_constraints']==[],'FarmerMaterialService all17 original constraints unchanged required')
    require(r['mandatory_constraints']==r['mandatory_package_constraints']['current_author_constraints'] and r['mandatory_package_constraints']['original_author_constraints_historical']==q['mandatory_constraints'] and r['mandatory_package_constraints']['corrections_required'] is False,'FarmerMaterialService full constraints and no-correction provenance required')
    require(r['limits']==norm['historical_review_limits_preserved_verbatim']==m['limits'] and len(m['limits'])==9,'FarmerMaterialService full9 Main limits including historical boundaries retained')
    auth=norm['current_authorization_boundary'];closure=auth['actual_preceding_closure'];cb=snap.read(local_path(closure['path'],DOCS));require(sha(cb)==closure['sha256']=='f3d9b101cdf3606ab8a29e710ea18c1f8aa6a06b9c3ccd99027dc7a60475cd0d' and auth['formal_baseline']==40 and auth['master_sha256']=='9174cdbe6d17e57033d442598831bb95da699180a5b61d0126f51a845361dd96' and auth['Main_delegation_source_thread']==m['reviewer_thread_id']==r['independent_reviewer_thread_id'],'FarmerMaterialService current private-only authority separate from historical35/Gorilla status required')
    require(r['deduplication']['current_whole_policy_comparison']==norm['current_whole_comparison']==m['semantic_comparison_rationale'] and r['deduplication']['author_prior_whole_decisions_historical']==q['prior_complete_semantic_decisions'] and r['deduplication']['independent_Main_prior_decisions']==m['prior_whole_decision_bindings'] and r['deduplication']['original_prior_source_chains_reread'] is False,'FarmerMaterialService full EA22 comparison and distinct Main reading required')
    require(m['actual_native_read_ranges']==q['actual_native_read_ranges'] and len(q['actual_native_read_ranges'])==18 and q['actual_cited_lines']==882 and q['actual_read_entry_count']==14 and q['actual_full_file_count']==5,'FarmerMaterialService exact18 raw native contexts and actual scope required')
    prior_refs=q['prior_actual_own_native_support_reused_zero']+q['prior_actual_block_context_reused_zero']
    require(len(q['prior_actual_own_native_support_reused_zero'])==3 and len(q['prior_actual_block_context_reused_zero'])==6 and prior_refs==r['prior_native_context_bindings'] and len(prior_refs)==9 and m['prior_own_native_support_reused']==r['Main_prior_native_context_bindings'] and len(r['Main_prior_native_context_bindings'])==9,'FarmerMaterialService prior3 Golem plus6 Silverfish source supports required')
    for author,main in zip(prior_refs,m['prior_own_native_support_reused']):
        require(author=={k:v for k,v in main.items() if k not in ('main_prior_actual_review','main_prior_actual_review_sha256','actual_main_prior_read_exact_match','fresh_source_reread')} and main['actual_main_prior_read_exact_match'] is True and main['fresh_source_reread'] is False and main['fresh_source_reread_claimed'] is False and main['new_credit']==0,'FarmerMaterialService exact9 distinct Main prior provenance projections0 required')
        rb=snap.read(local_path(main['main_prior_actual_review'],DOCS));require(sha(rb)==main['main_prior_actual_review_sha256'],'FarmerMaterialService actual prior Main review changed')
        matching=[x for x in json.loads(rb)['actual_native_read_ranges'] if x['entry']==author['entry'] and x['lines']==author['lines']]
        require(len(matching)==1 and all(matching[0][k]==author[k] for k in ('archive','archive_sha256','coordinate','entry','entry_sha256','lines','full_file','raw_excerpt_sha256','raw_excerpt_utf8')),'FarmerMaterialService actual prior Main exact source descriptor required')
    require(len(q['prior_complete_semantic_decisions'])==len(m['prior_whole_decision_bindings'])==1,'FarmerMaterialService one whole prior EA22 decision required')
    for author,main in zip(q['prior_complete_semantic_decisions'],m['prior_whole_decision_bindings']):
        require(author=={k:v for k,v in main.items() if k!='actual_main_reading'} and isinstance(main['actual_main_reading'],str) and bool(main['actual_main_reading']),'FarmerMaterialService Main whole decision projection adds only actual reading note')
        b=snap.read(local_path(author['path'],DOCS));require(sha(b)==author['sha256'],'FarmerMaterialService exact EA22 whole decision changed');j=json.loads(b)
        require({k:j[k] for k in author['actual_complete_semantic_decision_fields']}==author['actual_complete_semantic_decision_fields'] and author['old_source_chains_reread'] is False and author['support_credit']==0,'FarmerMaterialService full current EA22 observations34 limits21 and resource-normalization-identity judgment required')
    checkpoint=q['continuation_checkpoint'];require(sha(snap.read(local_path(checkpoint['path'],DOCS)))==checkpoint['sha256'],'FarmerMaterialService original read checkpoint changed')
    require(r['raw_base_resource_bindings']==q['actual_raw_base_resources']==m['actual_raw_base_resource_reads'] and len(q['actual_raw_base_resources'])==1,'FarmerMaterialService exact derived six-member seed tag required')
    require(r['migration_owner']==norm['Farmer_migration_owners']==r['prior_global_owner_support_only']==norm['prior_global_owner_support_only']==[] and norm['all_prior_whole_decisions_are_support0'] is True,'FarmerMaterialService cannot invent global or migration owners; prior EA22 remains0 support')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'FarmerMaterialService native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+prior_refs:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'FarmerMaterialService original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'FarmerMaterialService complete raw source range mismatch')
            for key in ('prior_actual_own_source','current_prior_binding'):
                prior=ref.get(key)
                if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'FarmerMaterialService prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'FarmerMaterialService nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'FarmerMaterialService accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==18,'FarmerMaterialService all18 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'FarmerMaterialService explicit typed native check missing')
        verified.append(validate_farmer_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==1,'FarmerMaterialService exactly one raw derived resource support check required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'FarmerMaterialService raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'FarmerMaterialService fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True and type(ref['credit']) is int and ref['credit']==0 and ref['loaded_current_membership_proved'] is False,'FarmerMaterialService base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'FarmerMaterialService primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_Farmer_inventory_compost_crop_service_with_exact_prior_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



CAT_REST_V26_SPEC = {'id': 'EA-0043', 'canonical_record_sha256': 'cef907e1ab08834b55e4ba9fbd0c847561a38b6ab957a7d255401a51ff94948f', 'batch': 'batch-034.json', 'bindings': {'complete_chain_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-cat-rest-morning-gift-whole-policy-proposal-20261104.json', 'sha256': '25f99e142f4565b08f84cd0942d9f512b44e27e3fc50b84173a33472ab999048'}, 'complete_chain_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-cat-rest-material-service-independent-review-20261104.json', 'sha256': '6a9e2b2aa330eff7da784ee3fbb789613133b1adec9f4fa6c00e4e12175227a3'}, 'complete_chain_current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-cat-rest-material-service-package-normalization-20261109.json', 'sha256': '0082d9128977c4b0a42511891a18a7bf4066df0d0dac4de8fc48e8a2bf25fda0'}, 'complete_chain_review_intake': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-cat-rest-material-service-review-intake-20261104.json', 'sha256': 'deb2360ed16fb52143fe73e9bb5c47752b85c26aa721cd6a217bb876e432b62e'}}, 'binding_context_keys': {'complete_chain_proposal': 'proposal', 'complete_chain_review': 'independent_main_review', 'complete_chain_current_normalization': 'current_constraint_normalization', 'complete_chain_review_intake': 'actual_review_intake'}, 'native_source_hashes': ['bd36b51e617629eb4a1dd9972add3f4e55578f1ad0577e8d973c79061867b0f9', '03252b28c04c3a93c5519f52782191ffb06d6390fe17f965e009483661a83dfb', '8d9b1379b36b50d69723ac6e917895accce39b0a4ec9c414d2d4993cd32e138c', 'cdb3cf8beaf3d828d90437bd83679e6204764f217024592d56488528fe549413', '2cc10b54d9120e131fa8bd558367fce47002210f6bbe0c0e240e542fb4d525dc', '367a2d6c55794e743fe9775f72faa2d82ce2de5c94bdf76aba1ed13fc5689e4e', 'd081180b9aa1248d50f5b9c29866925afb5ca6acc947590ae6a8c4e9ebfbc60f', '16127febe315b4c2df9b6dff37da5e8b58b5ffed75d830e88e69dd1f7ac2c11e', 'b3f08ecf5b5b60b354c2aca37b2c1a8719e6442e1c546eeb0a7c632e9194c988', '5484099f7cffa8b8a27b849c8390e0429effbe70cdf702d4b39d985d1b0944df', 'cb12bc157f7adc7f128c6d91893fcae4ab97390ff0a3ee899ec499b062899431', '9ab6b03bf27d27f2ae66a186d6a620aea47d435e2d5468af18d96eecf4668a19', 'e9d52425eb91e8b2d23e2cba6dc6e6eeac050f5b1b8a7334270dbca889131872', '09992f2237bea7dc3d2c6269e4a9edd469eb03f9f3c5a98d7a3242114ab41a15'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'receipt_perspective': 'original-source-author confirmation; independent semantic acceptance is distinct Main review, not self-review'}


def validate_cat_rest_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in CAT_REST_V26_SPEC['native_source_hashes'], 'CatRest native outside exact14-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'CatRest native cannot impersonate Git')
    artifact = CAT_REST_V26_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == CAT_REST_V26_SPEC['coordinate'], 'CatRest native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'CatRest native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'CatRest native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'CatRest native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'CatRest native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_cat_rest_receipt(path, raw, batches_by_id, snap):
    path=Path(path);spec=CAT_REST_V26_SPEC;policy=AUTHORIZED['general']
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0043.json').resolve(),'CatRest exact original author namespace required')
    d=json.loads(raw)
    require(isinstance(d,dict) and d.get('id')==spec['id'] and spec['id'] in policy['allowed_ids'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==policy['thread_id'],'CatRest original author identity mismatch')
    require(spec['id'] in batches_by_id,'CatRest actual batch missing');batch_path,r=batches_by_id[spec['id']]
    require(sha(canonical(r))==spec['canonical_record_sha256'],'CatRest complete frozen record changed')
    require(batch_path.resolve()==(DOCS/spec['batch']).resolve() and d.get('reviewed_batch')==str(batch_path.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(batch_path)),'CatRest exact real batch binding mismatch')
    require(snap.json(batch_path)['records']==[r] and type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['status']=='reviewed_proposed','CatRest one exact whole proposed row required')
    for field in ('semantic_key','general_context_schema','evidence_scope','receipt_perspective','author_thread_id','independent_reviewer_thread_id','mandatory_constraints','mandatory_corrections','mandatory_package_constraints','resource_membership_boundary','framework_dependency_boundary','migration_owner','migration_ownership_boundary','deduplication','raw_base_resource_bindings','prior_native_context_bindings','frozen_mechanism_context','Main_prior_native_context_bindings','prior_global_owner_support_only','limits','global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(canonical(d.get(field))==canonical(r[field]),'CatRest complete receipt context missing: '+field)
    require(d.get('observed_chain')==r['observation'] and all(isinstance(x,str) and x for x in d['observed_chain']),'CatRest corrected complete observation required')
    for field in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(field)) is int and d[field]==0,'CatRest non-ecology/runtime/support credit must be integer0')
    require(d.get('upstream_code_executed') is False and r['upstream_code_executed'] is False and not any(k in o for o in (d,r) for k in ('candidate_id','original_candidate_id')),'CatRest execution or invented global identity')
    for key,desc in spec['bindings'].items():
        require(r[key]==d.get(key)==desc,'CatRest immutable proposal/review binding mismatch');b=snap.read(local_path(desc['path'],DOCS))
        require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][spec['binding_context_keys'][key]],'CatRest frozen context changed')
    q=r['frozen_mechanism_context']['proposal'];m=r['frozen_mechanism_context']['independent_main_review']
    require(q['owner_thread_id']==r['author_thread_id']==policy['thread_id'] and r['independent_reviewer_thread_id']==policy['proposal_author_thread_id'] and r['author_thread_id']!=r['independent_reviewer_thread_id'],'CatRest author cannot be own independent reviewer')
    require(m['reviewer']=='Main existing coordinator distinct from original author' and m['proposal']==spec['bindings']['complete_chain_proposal'] and m['formal_candidate_id'] is None and q['formal_candidate_id'] is None and type(m['recommended_maximum_credit']) is int and m['recommended_maximum_credit']==1 and m['accepted_credit']==0 and m['applied_credit']==0 and m['decision']=='ACCEPT_MAXIMUM_ONE_BOUNDED_RELATED_OWNER_REST_MATERIAL_SERVICE_PENDING_REAL_PACKAGE','CatRest distinct max1 preformal Main review required')
    norm=r['frozen_mechanism_context']['current_constraint_normalization']
    require(norm['original_proposal']==spec['bindings']['complete_chain_proposal'] and norm['distinct_Main_review']==spec['bindings']['complete_chain_review'] and norm['actual_Main_review_intake']==spec['bindings']['complete_chain_review_intake'],'CatRest exact normalization and actual intake')
    require(r['mandatory_constraints']==q['mandatory_constraints']==m['mandatory_author_constraints_preserved']==norm['current_constraints'] and len(r['mandatory_constraints'])==14 and norm['all14_original_constraints_unchanged'] is True,'CatRest all14 original constraints unchanged')
    require(r['mandatory_corrections']==q['mandatory_corrections']==m['mandatory_corrections']==norm['mandatory_corrections']==[],'CatRest no invented correction')
    require(r['mandatory_package_constraints']['current_author_constraints']==r['mandatory_constraints'] and r['mandatory_package_constraints']['original_author_constraints_historical']==q['mandatory_constraints'] and r['mandatory_package_constraints']['corrections_required'] is False,'CatRest current and historical full constraints')
    require(r['observation']==m['independent_findings']==norm['current_observation'] and len(r['observation'])==14 and r['limits']==m['limits']==norm['historical_review_limits_preserved_verbatim'] and len(r['limits'])==9,'CatRest Main14 findings9limits')
    auth=norm['current_authorization_boundary'];cl=auth['actual_preceding_closure']
    require(sha(snap.read(local_path(cl['path'],DOCS)))==cl['sha256']=='b3b23c871227f8917864b000742bc61a7a90eabf9bfcf34d8b0a94ba6249dc82' and auth['formal_baseline']==41 and auth['master_sha256']=='63bfb32a4642d27e2b795fd655b603ff493fd7cf31699646a1cccc468c970c20','CatRest separate current41 private authority, historical40 retained')
    require(q['semantic_key']==m['semantic_key']==norm['current_semantic_key']==r['semantic_key'] and r['deduplication']['current_whole_policy_comparison']==m['semantic_comparison_rationale']==norm['current_whole_comparison'],'CatRest whole semantic comparison')
    require(r['deduplication']['author_prior_whole_decisions_historical']==q['prior_complete_semantic_decisions'] and r['deduplication']['independent_Main_prior_decisions']==m['prior_whole_decision_bindings'] and r['deduplication']['original_prior_source_chains_reread'] is False,'CatRest all three current whole decisions retained')
    require(q['actual_native_read_ranges']==m['actual_native_read_ranges'] and len(q['actual_native_read_ranges'])==14 and q['actual_cited_lines']==313 and q['actual_read_entry_count']==8 and q['actual_full_file_count']==1 and q['actual_complete_nested_goal']==[{'entry':'net/minecraft/world/entity/animal/Cat.java','lines':[460,573],'source_credit':0}],'CatRest exact scope and complete nested114 not wholeCat603')
    prior_refs=q['prior_actual_own_native_support_reused_zero']
    require(prior_refs==r['prior_native_context_bindings'] and len(prior_refs)==8 and m['prior_own_native_support_reused']==r['Main_prior_native_context_bindings'],'CatRest exact8 Hero prior projections')
    for author,main in zip(prior_refs,m['prior_own_native_support_reused']):
        require(author=={k:v for k,v in main.items() if k not in ('Main_prior_actual_review','new_credit','fresh_source_reread')} and main['new_credit']==0 and main['fresh_source_reread'] is False,'CatRest distinct Main prior provenance0')
        desc=main['Main_prior_actual_review'];rawprior=snap.read(local_path(desc['path'],DOCS));require(sha(rawprior)==desc['sha256'],'CatRest actual prior Main review hash')
        matched=[x for x in json.loads(rawprior)['actual_native_read_ranges'] if x['entry']==author['entry'] and x['lines']==author['lines']]
        require(len(matched)==1 and all(matched[0][k]==author[k] for k in ('archive','archive_sha256','coordinate','entry','entry_sha256','lines','full_file','raw_excerpt_sha256','raw_excerpt_utf8')),'CatRest actual prior descriptor exact')
    require(len(q['prior_complete_semantic_decisions'])==len(m['prior_whole_decision_bindings'])==3,'CatRest Hero Seal CatSpawner complete comparison')
    for author,main in zip(q['prior_complete_semantic_decisions'],m['prior_whole_decision_bindings']):
        require(author=={k:v for k,v in main.items() if k not in ('Main_current_additional_context','complete_receipt_sha256_checked','old_original_source_reading_credit','additional_context_note')} and main['complete_receipt_sha256_checked'] is True and main['old_original_source_reading_credit']==0 and author['old_complete_source_chains_reread'] is False and author['support_credit']==0,'CatRest exact Main whole projection')
        rawprior=snap.read(local_path(author['path'],DOCS));require(sha(rawprior)==author['sha256'],'CatRest current prior whole receipt hash');j=json.loads(rawprior)
        for fields in (author['actual_complete_decision_fields'],main['Main_current_additional_context']):require({k:j[k] for k in fields}==fields,'CatRest complete current prior judgment and new fields')
    require(q['existing_global_whole_owners']==m['existing_whole_owners']==r['migration_owner']==r['prior_global_owner_support_only']==norm['prior_global_owner_support_only'] and len(r['migration_owner'])==2,'CatRest two existing whole owners only')
    ledger=DOCS.parent/'legacy-migration-acceptance/reviewed.jsonl';rows=[json.loads(x) for x in snap.read(ledger).decode().splitlines() if x.strip()]
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'],'CatRest complete old owner canonical unchanged');fields=owner['actual_current_non_evidence_decision_fields']
        require({k:matches[0][k] for k in fields}==fields and owner['new_credit']==0 and owner['old_original_source_chains_reread'] is False,'CatRest complete old non-evidence judgments0')
    for desc in (q['continuation_checkpoint'],q['prior_actual_own_source_binding'],m['prior_own_actual_Main_source_review']):require(sha(snap.read(local_path(desc['path'],DOCS)))==desc['sha256'],'CatRest actual original checkpoints')
    require(r['raw_base_resource_bindings']==q['actual_raw_base_resources']==m['actual_raw_base_resources'] and len(r['raw_base_resource_bindings'])==2,'CatRest two derived raw entries only')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive)==spec['artifact']['sha256'],'CatRest native fixed archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in q['actual_native_read_ranges']+prior_refs:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'],'CatRest original fixed native identity mismatch')
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(b.splitlines()) and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and (not ref['full_file'] or (lo,hi)==(1,len(b.splitlines()))),'CatRest complete raw source range mismatch')
            for key in ('prior_actual_own_source','current_prior_binding'):
                prior=ref.get(key)
                if prior:require(sha(snap.read(local_path(prior['path'],DOCS)))==prior['sha256'],'CatRest prior exact native context changed')
    decision=d.get('decision')
    if decision not in policy['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'CatRest nonaccepting decision must confer0')
        return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),reason='explicit nonaccepting author receipt0')
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'CatRest accepted credit must be integer1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==14,'CatRest all14 exact typed native checks required')
    verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'CatRest explicit typed native check missing')
        verified.append(validate_cat_rest_native_source(e,snap))
    resources=d.get('resource_checks');require(isinstance(resources,list) and len(resources)==len(r['raw_base_resource_bindings'])==2,'CatRest exactly two raw derived resources support check required')
    resource_verified=[]
    for check,ref in zip(resources,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'CatRest raw resource is support0 not loaded membership')
        b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'CatRest fixed local derived resource archive changed')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True and type(ref['credit']) is int and ref['credit']==0 and ref['loaded_current_membership_proved'] is False,'CatRest base raw resource bytes changed')
        resource_verified.append(dict(archive=ref['archive'],archive_sha256=ref['archive_sha256'],entry=ref['entry'],entry_sha256=ref['entry_sha256'],resource_kind='fixed_local_derived_archive_entry_not_Git_or_published_coordinate',supporting_credit=0,loaded_membership_claimed=False))
    for key in r['chain'][0]:require(r.get(key)==r['chain'][0][key],'CatRest primary native/chain head mismatch')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(batch_path.relative_to(ROOT)),batch_sha256=sha(snap.read(batch_path)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=d['limits'],observed_chain=d['observed_chain'],complete_chain_support_proof=dict(**spec['bindings'],source_kind='artifact_native_Cat_owner_rest_service_with_exact_prior_support',scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))



SNOW_V27_SPEC = {'id': 'EA-0044', 'canonical_record_sha256': '4d75fc6d7d0a5c9978bf2241c8efb46918ff9554cbe28089a41facd603dd4386', 'batch': 'batch-035.json', 'bindings': {'proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-snow-golem-footprint-material-whole-policy-proposal-20261104.json', 'sha256': '77e321bf6be8b218a81913782d5378d42f63946e9010bbc51cd333d8796cb8dd'}, 'original_Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-snow-footprint-material-independent-review-20261104.json', 'sha256': '43ee93b327f236652906580707f0efa29b7cf843320f28cac4856d28e7b19a35'}, 'fallback_clarification': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-snow-golem-raw-fallback-wording-clarification-20261104.json', 'sha256': '081e008fff5f9602d4c2dd928747d455e3c6b06c447cea4463fd9b047bf6447c'}, 'supplement': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-snow-alternative-expansion-boundary-read-20261109.json', 'sha256': 'ba1fe90ad8daf5bcf6a7c379af18b94f54cc918dc8b32c9d12101a0119a92255'}, 'supplement_Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-snow-alternative-expansion-supplement-review-20261109.json', 'sha256': '0741a30ee484486d079a1df169616f2852decb53e733920eb8f6bfa3c5bc13ec'}, 'current42_intake': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-snow-current42-single-authority-intake-20261109.json', 'sha256': '509cc713752850b8e0fccbd7618d7bd2a48eff1b3bdc6d164e47d8b72ac2bb72'}, 'current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-snow-v27-current-normalization-20261109.json', 'sha256': '496b95e832fb41bedbb23bb8a853c96da3b88f0d7d77c3fc22a1672b094e8a70'}}, 'native_source_hashes': ['8935bf342c9b5ed096ec52e24ca8e4d42cceb8fbd84f06976998f28c740f2add', 'a2a7c41f1aa16642efe89f34fd97e56c4a4b26f34bf5c540a28e9c556aa3928b', '52370401656f66fa7c54b90a95774d12c0bd0e15fc6ff0a8e9cb19b904273e34', 'ca6cc525146517d578fbdab3b443b2e8e48c81120600db154f2f00a614efc778', '9ed56922c57d3a4351991fbfcdb1a906fd551320d562bb8005c5a8ceec6da63d', '5ca7101f4e1277b96c7381890f621731c9a7a2930223b701d51d1f88383b6bf2', '037addc0db460ba0458f3d20bc298f27dd95e98e83a55b3fe750b456bbc37008', '69ce12e7a349fa4e882788a6767b8a74aeaa718e556e7ea422a45478bb9c47da', '25dbf147c4cb6ad0a4e6d12ce00987960f9fa86a627c8902487c1409719cff31', '2f7139800d2460ab354d3c4cd2014ee48c09364b2096384bb658beb33e971035', 'ec99ab11b281a831262cc0eff014189d958dc892e9a4b859e8b770b62d40ffbf', '8b43092f8932762ab880a59de8a99d05da965ff9e7392fbcd060fce7fb6a34b6', '4e6a75aae865ef4ac30e26d0c38731e52e26840b2b99f21bc6aaa9f9dccc9ed2', '0ccb7b4e36fc67ef4969865c97fe6e260c3cec67cc6625a439f527d89566c5c7', '9a0258ca9fdf4786f12a9ef7f5811ccebf87efc1448d6e909e2ea3c23b1e760d', 'a2cf575d53f5ecdfff0bf57a4a85cb3321d4983f2c8b04d1970357dfd0b49cb5', 'e69b34f42a88de9de46c005028732d5d92f049352e79bed5e61a62e2a1cc7c0d', '2204ac7de0bdfc8fd7b23b034f1dbe552a0646f1a786709e21f750f6e9a09cee', '433b9644216a983614939c23b16ac1c3fa9556d7e67aaa263b9c922f504f2b6d', '5a36988c6b0b829d1e1e5ee0f63f409fc75a58920211d075e49c2c87aa8e0ebc', '71a7e86b0b7a211aaf76273894fd323e15ccefcdbe3cd069b3d013b9b380cfb8', '835d6c773cb051972b8d95500665728b4aaa302c3611383ad240654a3660a75f', 'd9a2098aa7a281ec77b772e6389fa7c59da75c7fd08a0c0cdbae29b9bed3ff72', 'f6b9d5ccbe5254464ac4104529f91f2b943a79baeae766e54dafadc08b5834c8', 'e037ecf90832eabf9b5862937ed5c1431becb3575aaa916fc51b083b8f7125f4', '15744fb89ec52e142767009fb7551ac0dccb64e040d6906583d919c2786785d9', '5f4f2320ab5ce9a40247f0d05cb8458f8a1d7480625d7338bb44ff80f6843f09', '555aa6db3cc5a79b0f2f23fcb7380cd6c43479bf14801a5f5e32050ff7f94c18', '49ed0b398579130cd979c16818eb0081b6d3ef96f2eda47df81f91c0b17598a6', '5b8a2dc31fafc4b63f01027350d48d4a53465c54f4dcefa831c21524baf7b73e', 'a6f28d4fa7485d634dd3b1f1f4af3c29e1f5bd7cdff2591e59fc499e2dfde75d', '00ebc4d3d406a65b141e6fed5d36fafaa4a8c30b5f951c4c1846e3329b40351e', 'fd4ec38aa8abb6c077d4b2be178e58ca491f91b2a8d120d59407ab1e0324a0e7', 'bd485320f86cae428d9a6ba42b47fa457d888c02964131f96ac7821aa8ceb4cb', 'f46e92bc413254b07a855f8566bf8b6e0d7ab128a7b531cc91aeca1416e4a9c5', '68d6a3f904c22b0da3e194c5d7333a1a4c1ba5938b33104c093e9f25bde240af'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review'}

def validate_snow_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in SNOW_V27_SPEC['native_source_hashes'], 'Snow native outside exact36-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Snow native cannot impersonate Git')
    artifact = SNOW_V27_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == SNOW_V27_SPEC['coordinate'], 'Snow native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Snow native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Snow native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Snow native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Snow native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}

def validate_snow_receipt(path, raw, batches_by_id, snap):
    spec=SNOW_V27_SPEC;path=Path(path);d=json.loads(raw)
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0044.json').resolve(),'Snow exact original author namespace')
    require(d.get('id')==spec['id'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==AUTHORIZED['general']['thread_id'],'Snow actual original author identity')
    require(spec['id'] in batches_by_id,'Snow actual batch required');bp,r=batches_by_id[spec['id']]
    require(bp.resolve()==(DOCS/spec['batch']).resolve() and sha(canonical(r))==spec['canonical_record_sha256'] and snap.json(bp)['records']==[r],'Snow exact frozen whole record')
    require(d.get('reviewed_batch')==str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(bp)),'Snow actual batch binding')
    for key,value in r.items():
        if key!='accepted_credit':require(canonical(d.get(key))==canonical(value),'Snow missing complete receipt context '+key)
    require(r['author_thread_id']==d['reviewer_thread_id'] and r['independent_reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Snow distinct Main independent semantic review')
    require(r['proposed_credit']==1 and r['accepted_credit']==0 and r['upstream_code_executed'] is False and d.get('observed_chain')==r['observation'],'Snow exact pending proposal and observations')
    for key,desc in spec['bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][key],'Snow immutable full context '+key)
    f=r['frozen_mechanism_context'];q=f['proposal'];m=f['original_Main_review'];n=f['current_normalization'];sm=f['supplement_Main_review']
    require(n['current_formal_baseline']==42 and n['current_master_sha256']=='0aa87006b725d5a0f34004f38f0991fd7ebfdb29300714414ac60ab1acfb0bed' and n['original13_constraints']==q['mandatory_constraints']==m['mandatory_author_constraints_preserved'] and len(r['mandatory_constraints'])==13,'Snow current42 separate from historical40/41 and original13 constraints')
    require(n['original17_observations']==q['observed_chain'] and len(q['observed_chain'])==17 and n['current17_observations']==m['current_author_observations'] and r['observation']==m['independent_findings']+sm['independent_findings'] and len(m['independent_findings'])==16 and len(m['limits'])==10,'Snow original17/Main16/10 and new boundary retained')
    require(r['mandatory_corrections']==[f['fallback_clarification'],n['mandatory_supplement_refinement']] and n['mandatory_supplement_refinement']['required_Main_refinement']==sm['required_author_refinement'],'Snow mandatory fallback and supplied-array correction')
    for desc in r['checkpoint_bindings']:require(sha(snap.read(local_path(desc['path'],DOCS)))==desc['sha256'],'Snow original checkpoint or actual42 closure changed')
    for desc in r['decision_bindings']:
        b=snap.read(local_path(desc['path'],DOCS));require(sha(b)==desc['sha256'],'Snow complete EA22/Farmer decision changed');j=json.loads(b);require({k:j[k] for k in desc['fields']}==desc['fields'],'Snow complete prior decision fields')
    ledger=DOCS.parent/'legacy-migration-acceptance/reviewed.jsonl';rows=[json.loads(x) for x in snap.read(ledger).decode().splitlines() if x.strip()]
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'],'Snow complete36d owner canonical');fields=owner['actual_complete_current_non_evidence_fields'];require({k:matches[0][k] for k in fields}==fields and owner['new_credit']==0,'Snow current36d complete judgment0')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(archive)==spec['artifact']['sha256'],'Snow native artifact')
    refs=q['actual_native_read_ranges']+m['additional_native_support_read']+f['supplement']['actual_new_text_read']+r['prior_native_context_bindings'];require(len(refs)==44,'Snow36current+8prior support')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in refs:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);require(sha(b)==ref['entry_sha256'] and sha(part)==ref['raw_excerpt_sha256'] and part.decode()==ref['raw_excerpt_utf8'] and ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'],'Snow exact raw native context')
    for a,b in zip(r['prior_native_context_bindings'],r['Main_prior_native_context_bindings']):
        require(a=={k:v for k,v in b.items() if k not in ('main_prior_actual_review','main_prior_actual_review_sha256','actual_main_prior_read_exact_match','fresh_source_reread','new_credit')},'Snow exact prior Main projection');rb=snap.read(local_path(b['main_prior_actual_review'],DOCS));require(sha(rb)==b['main_prior_actual_review_sha256'],'Snow prior actual Main hash');match=[x for x in json.loads(rb)['actual_native_read_ranges'] if x['entry']==a['entry'] and x['lines']==a['lines']];require(len(match)==1 and all(match[0][k]==a[k] for k in ('archive','archive_sha256','coordinate','entry','entry_sha256','lines','full_file','raw_excerpt_sha256','raw_excerpt_utf8')),'Snow actual prior Main raw descriptor')
    decision=d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Snow explicit nonacceptance0');return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Snow accepted whole credit1')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==36,'Snow36 native checks');verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Snow actual typed flags');verified.append(validate_snow_native_source(e,snap))
    checks=d.get('resource_checks');require(isinstance(checks,list) and len(checks)==len(r['raw_base_resource_bindings'])==4,'Snow4 derived raw support');resources=[]
    for check,ref in zip(checks,r['raw_base_resource_bindings']):
        require(check.get('binding')==ref and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','raw_utf8_exact')) and check.get('loaded_membership_claimed') is False and type(check.get('credit')) is int and check['credit']==0,'Snow raw resource flags0');b=snap.read(local_path(ref['archive'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==ref['archive_sha256'],'Snow derived archive')
        with zipfile.ZipFile(io.BytesIO(b)) as z:entry=z.read(ref['entry'])
        require(sha(entry)==ref['entry_sha256'] and entry.decode()==ref['raw_utf8'] and ref['full_file'] is True and ref['credit']==0 and ref['loaded_current_membership_proved'] is False,'Snow complete raw bytes not loaded guarantee');resources.append(dict(archive=ref['archive'],entry=ref['entry'],entry_sha256=sha(entry),supporting_credit=0,loaded_membership_claimed=False))
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(bp.relative_to(ROOT)),batch_sha256=sha(snap.read(bp)),source_checks_recomputed=verified,base_resource_checks_recomputed=resources,supporting_ranges_credit=0,limitations=r['limits'],observed_chain=r['observation'],complete_chain_support_proof=dict(bindings=spec['bindings'],scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='original author confirmation, not self-independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




PEER_SHARING_V28_SPEC = {'id': 'EA-0045', 'canonical_record_sha256': '997233285240516e1a00fc6368ae3406fbe30529305b33a61147c6f6d82e2b21', 'batch': 'batch-036.json', 'bindings': {'proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-villager-peer-material-sharing-whole-policy-proposal-20261109.json', 'sha256': 'ba06ec031ab5a408992c12ec4e0025c07c1cbce64d9e3f04eb0ee79d07717fe4'}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-villager-peer-sharing-whole-policy-review-20261109.json', 'sha256': 'a963454c9609866d1770785b2206df60b8d204e64e4e7f524e5699a5c67bda8c'}, 'reading_correction_v3': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-villager-peer-material-sharing-read-checkpoint-v3-overlap-correction-20261109.json', 'sha256': 'a4597848d9f1c6fb2b31febf0e1b26e8eed1d9f4be90ae967bb631a797c10c7b'}, 'takeover_intake': {'path': 'tools/cod4/ecology-availability-research/.work/peer-sharing-evidence-intake-20261109/unregistered-whole-policy-intake.json', 'sha256': 'cb90787d9ac930bc6fe2426e3bf8619c6872fff56fc30c11c48442565a035be7'}, 'exact_source_intake': {'path': 'tools/cod4/ecology-availability-research/.work/peer-sharing-evidence-intake-20261109/source-excerpt-bindings.json', 'sha256': '5ab2e481187562ce8dc4d14225073a3d9b34e3eee8f4b627b2a2a8985d7507bc'}, 'Main_newline_correction': {'path': 'tools/cod4/ecology-availability-research/.work/peer-sharing-evidence-intake-20261109/explicit-prior-Main-excerpt-newline-correction.json', 'sha256': 'c8dda818847194c41beea57867508fbf2ab57f462499a66c5301f3b1d5c044e5'}, 'current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-peer-sharing-v28-current-normalization-20261109.json', 'sha256': '0cea3070e3087c698ba32013415f397b1abc2d2473f5e674536f309f0a77e413'}}, 'native_source_hashes': ['51e7c2b9c3cb300ee0448452729426cb0109cb57b7a40e43953b997d32d3222e', '0bad870c6c4935f85b5d408a038b5d155cded5ae9df6cc5712f08394a7777764', '27a86fd5090cd884b85cccd1a98fbbcc8de73dbcb5aaff72153cb9d51eaaff72', '0ab40d2f2662d5f2499f0758408e4a7801cd8c296134c74a045d1b5259a8c1c1', '0d6a53d47c112573c8873c30400d538b961a9a477ac751738807bbf08399300d', 'ee4897bc6fe5c149d0ee2e5a894047e8980d33fc61acbbb807459e9f9557df44', 'd8927d9e9850e629bcfe90013b2a309f751a52fae0ce994ed6b80e8d5e921104', 'cb5211863a791be99a954c01f08010f4ffbde1d4f1533aab6dde9cb29f27647b', '661f686b915c8c08e333e65511c9adba1c2436f4b0e9d69a73b213563a7875c2', 'e720a7a970f24be77c56c82eaa267edc116b559fed3c02a780631c189327aea6', 'c8f1cef8d766af09dc4573897e6b73d13d29b64ec8449e2f7bea6ef19e88d00e', '2ee1c9fccce693314d314eab2ebfb085666d6456b69668f5399fce54a51ffc38', '36d7db9bd1c1968c1201c8a0d7a5e7432f710c5e6edd6cea1188038528011a66', '80ba3e4533f0baebea729e6659d570c9bd59d1e5bd55c98d1709b8750fd3cbc4', '8f4814bae30b25380d88cf3037990f1358f1b2497a1061024d40c5a0d7d7bfc4', 'e7c41a5be94a22aed5098f2239c37d9894925659cb13a471a52fe611c8ff0365', '9dd17b03f7a9e25a1cd7e4798858905683e0729f88444e022e5edde2bae139ae', '66419068c7b86b3eabccdd859573584ba346699f1cd434109a1ad61faf4728c1', '8c352dde218c93d8f803aab812f08fd1cf26d9dcca98d6a9ae25e07ddfd53f39', '35ce9d842005fadd69b712c2fdfdfbb7e9d1239b6fc04ee49fb10d7974619c06', 'fc36a0c18a5b2220084b67fbf00789d2126e6367f3e534de98718672c8b5c003', '9ed511510beec4c4386d8e63312c5072fa7009ae918b32171375e208d8853f0e', 'c852c81bbafeeddbca1a4d796afcbe6fb248dad5348279536c21a3c3f132fcc3', '945d6300f73bc7b8c65d170e368e7cdd56d5bc6e6deffede540cc887c59f019c', '62f59f25e236029fd750dffb7c6da5b2fa16e1aa2073901332b6645d0b5a2ce5', '7f3a9df30e81989d294f2f53fdca73ff23d350fcf980976266ceaea46a373eb4', 'be9dd5d211738cdc81db3a59ed4e44e1164293bc1024032d7cc2d5a027af2943', 'f201d6b05246f2a9da08306c57831a421f3c393673e21eb10fd62d645367e11a', '7c76cfc64965afb0db153fc9f934bc4c6b2f1d11f1d4c565336cd8ea4a7b428f'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review', 'exact_ranges': 29}

def validate_peer_sharing_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in PEER_SHARING_V28_SPEC['native_source_hashes'], 'PeerSharing native outside exact29-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'PeerSharing native cannot impersonate Git')
    artifact = PEER_SHARING_V28_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == PEER_SHARING_V28_SPEC['coordinate'], 'PeerSharing native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'PeerSharing native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'PeerSharing native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'PeerSharing native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'PeerSharing native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}

def validate_peer_sharing_receipt(path, raw, batches_by_id, snap):
    spec=PEER_SHARING_V28_SPEC;path=Path(path);d=json.loads(raw)
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0045.json').resolve(),'PeerSharing exact original author namespace')
    require(d.get('id')==spec['id'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==AUTHORIZED['general']['thread_id'],'PeerSharing actual author identity')
    require(spec['id'] in batches_by_id,'PeerSharing actual batch required');bp,r=batches_by_id[spec['id']]
    require(bp.resolve()==(DOCS/spec['batch']).resolve() and sha(canonical(r))==spec['canonical_record_sha256'] and snap.json(bp)['records']==[r],'PeerSharing exact frozen whole record')
    require(d.get('reviewed_batch')==str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(bp)),'PeerSharing actual batch hash')
    for key,value in r.items():
        if key!='accepted_credit':require(canonical(d.get(key))==canonical(value),'PeerSharing missing complete context '+key)
    require(r['author_thread_id']==d['reviewer_thread_id'] and r['independent_reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id']!=r['independent_reviewer_thread_id'],'PeerSharing distinct Main independent semantic judgment')
    require(r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['upstream_code_executed'] is False and d.get('observed_chain')==r['observation'],'PeerSharing pending bounded policy')
    for key,desc in spec['bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][key],'PeerSharing immutable full context '+key)
    f=r['frozen_mechanism_context'];q=f['proposal'];m=f['Main_review'];v=f['reading_correction_v3'];n=f['current_normalization'];fix=f['Main_newline_correction'];src=f['exact_source_intake']
    require(n['current_formal_baseline']==43 and n['current_master_sha256']=='6c39b9f164509ed353687de94697668dbc5ea23d82181578a1a0307c6ce59242','PeerSharing exact43 package baseline not ongoing ledger authority')
    require(n['original13_observations']==q['observed_chain']==r['original_author_observations'] and len(q['observed_chain'])==13 and n['original10_constraints']==q['mandatory_constraints']==r['mandatory_constraints'] and len(r['mandatory_constraints'])==10,'PeerSharing original complete observations and constraints')
    require(n['Main11_findings']==m['actual_findings']==r['observation'] and len(m['actual_findings'])==11 and n['Main5_limits']==m['limits'] and r['limits']==q['limits']+m['limits'],'PeerSharing full Main independent judgment and limits')
    corrected=list(q['observed_chain']);corrected[8]=n['mandatory_uuid_refinement']['current_text']
    require(corrected==n['current13_observations']==r['current_author_observations'] and n['mandatory_uuid_refinement']['Main_refinement']==m['actual_findings'][7] and n['mandatory_uuid_refinement']['required_boundary']==f['takeover_intake']['required_correction'],'PeerSharing throwerUUID not intended recipient receipt')
    require(r['mandatory_corrections']==q['mandatory_corrections']+[n['mandatory_uuid_refinement'],fix] and v['actually_displayed_lines']==575 and v['prior_covered_lines']==230 and v['additional_distinct_lines']==345 and n['mandatory_reading_accounting']['line_or_range_credit']==0,'PeerSharing explicit overlap and EOF correction retained0')
    require(r['semantic_key']==m['semantic_key']==n['current_semantic_key'] and r['application']==m['quest_integration_boundary'] and r['deduplication']==m['whole_dedup_decision'],'PeerSharing entire policy and quest boundary')
    for desc in r['prior_whole_decision_bindings']:
        b=snap.read(local_path(desc['path'],DOCS));require(sha(b)==desc['sha256'],'PeerSharing prior complete EA38/42 changed');j=json.loads(b);require({k:j[k] for k in desc['fields']}==desc['fields'],'PeerSharing complete current decision fields')
    for desc in r['prior_source_document_bindings']:
        require(sha(snap.read(local_path(desc['path'],DOCS)))==desc['sha256'],'PeerSharing prior actual reading document changed')
    rows=[json.loads(x) for x in snap.read(DOCS.parent/'legacy-migration-acceptance/reviewed.jsonl').decode().splitlines() if x.strip()]
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'],'PeerSharing current global migration complete owner');fields=owner['actual_complete_current_non_evidence_fields'];require({k:matches[0][k] for k in fields}==fields and owner['new_credit']==0,'PeerSharing global owner complete judgment0')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(archive)==spec['artifact']['sha256'],'PeerSharing archive changed')
    refs=q['actual_displayed_source_ranges']+[x['descriptor'] for x in q['prior_exact_source_support_reused0']]+m['actual_prior_continuation_read_ranges']+m['actual_current_continuation_read_ranges'];require(len(refs)==47,'PeerSharing47 prior/current descriptor occurrences')
    corrections={(x['entry'],tuple(x['lines'])):x for x in fix['corrections']};used=set();unique={}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref in refs:
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);require(sha(b)==ref['entry_sha256'] and ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and 1<=lo<=hi<=len(b.splitlines()),'PeerSharing actual raw native descriptor')
            key=(ref['entry'],tuple(ref['lines']))
            if sha(part)!=ref['raw_excerpt_sha256'] or part.decode()!=ref['raw_excerpt_utf8']:
                require(key in corrections,'PeerSharing unapproved raw mismatch');c=corrections[key];require(ref['raw_excerpt_utf8']==part.decode()+'\n' and sha(ref['raw_excerpt_utf8'].encode())==ref['raw_excerpt_sha256']==c['old_claimed_raw_excerpt_sha256'] and sha(part)==c['actual_raw_excerpt_sha256'] and c['semantic_credit']==0,'PeerSharing exact historical newline refinement');used.add(key)
            unique[key]=dict(entry=ref['entry'],lines=ref['lines'],entry_sha256=sha(b),raw_excerpt_sha256=sha(part),raw_excerpt_utf8=part.decode(),full_file=(lo,hi)==(1,len(b.splitlines())))
    require(len(unique)==29 and list(unique.values())==src['unique_exact_ranges'] and used==set(corrections) and len(used)==8,'PeerSharing29 exact ranges and8 unchanged historical corrections')
    for key in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(key)) is int and d[key]==0,'PeerSharing no unsupported runtime/global credit '+key)
    decision=d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'PeerSharing explicit nonacceptance0');return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'PeerSharing one whole credit only')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==29,'PeerSharing29 exact source checks');verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'PeerSharing actual typed source check flags');verified.append(validate_peer_sharing_native_source(e,snap))
    require(d.get('resource_checks')==[],'PeerSharing no invented raw resource/loaded membership proof')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(bp.relative_to(ROOT)),batch_sha256=sha(snap.read(bp)),source_checks_recomputed=verified,base_resource_checks_recomputed=[],supporting_ranges_credit=0,limitations=r['limits'],observed_chain=r['observation'],complete_chain_support_proof=dict(bindings=spec['bindings'],scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='actual original author confirmation, not self-independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




EVOKER_V29_SPEC = {'id': 'EA-0046', 'canonical_record_sha256': 'aad264ad7439cd76144b509d7b942205bb30aad21c5660d500c3ca54a3ca4ca2', 'batch': 'batch-037.json', 'bindings': {'proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-evoker-livestock-phenotype-service-whole-policy-proposal-20261104.json', 'sha256': 'dfd1ea7bec8802b8a6b76fe1c89e20ec023f25e6575290fa9910c0814264c470'}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-evoker-livestock-phenotype-independent-review-20261104.json', 'sha256': '19db95d3cf8a0509153a739e790de2546c27ecd1b3bb56ec99ebf420dc6b01a3'}, 'author_intake': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-evoker-livestock-phenotype-review-intake-20261104.json', 'sha256': 'be099e993c39c6d7eabb7cc833a7ee0bb94faafe3dcde9c175cb431fe0ce5a20'}, 'original_read_checkpoint': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-evoker-livestock-phenotype-service-read-checkpoint-20261104.json', 'sha256': '1810232539b4eb50783b8e9420ac161de6c1c98e8415a5cebfe7cdaa81a4b4f1'}, 'current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-evoker-v29-current-normalization-20261109.json', 'sha256': 'db70fc3a7395498ec96ee2d2863e642148db7d22c541e4edf0804c96c655b641'}}, 'native_source_hashes': ['6972a5468c7b9b55e6b639fdf53079e16cf0ae4950d51be3ebbe40280a57de0a', '75b312294800d5fc85c5eaf8cecdabcf457ce25159ddc9f5ae337b04795ed8e3', '523eb18d2a9ed62a124639c01cecbddcbfea519957370da27dcc597cd9f63969', 'fbdb1968d70006af814bcbf07548308ec7c10d0bbf43b143c8c7ee71f9c52c02', '932fc60927cba6fc6c1a19dd64a58f5a165ce0473e27c904fb9548d2940db2ca', '7a54c9ee33fc142abf98dceee350194f33ceda2fc3d15d1dac6fbc9492391c9d', '0b633ba6c356cffbef0c977ddeabdbc81c42480213aaa86b898874cd3b1d2108', '9658bd46be893974abebcd2cb0780a455958749aa1cae63b369030f35551c19f', '2b3106bf647bb5c0ef5d0997c0d13a3eb90d38ac059e5916194a8b17c2c912c4', '87c24d9bb3bdd2da6a015df5a037ddeb47736b06ec80596179112b44709247ad', '15c8d8d18fe6edbe43da359214d2c408badae92affc419e64ee1c322580b8281', 'e25a563882c44050081ccb9a8d8ebd3d1c50d74887a570f625262ab0708e4b1a'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'exact_ranges': 12, 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review'}

def validate_evoker_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in EVOKER_V29_SPEC['native_source_hashes'], 'Evoker native outside exact12-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Evoker native cannot impersonate Git')
    artifact = EVOKER_V29_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == EVOKER_V29_SPEC['coordinate'], 'Evoker native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Evoker native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Evoker native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Evoker native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Evoker native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}

def validate_evoker_receipt(path, raw, batches_by_id, snap):
    spec=EVOKER_V29_SPEC;path=Path(path);d=json.loads(raw)
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0046.json').resolve(),'Evoker exact original author namespace')
    require(d.get('id')==spec['id'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==AUTHORIZED['general']['thread_id'],'Evoker actual original author identity')
    require(spec['id'] in batches_by_id,'Evoker actual batch required');bp,r=batches_by_id[spec['id']]
    require(bp.resolve()==(DOCS/spec['batch']).resolve() and sha(canonical(r))==spec['canonical_record_sha256'] and snap.json(bp)['records']==[r],'Evoker exact frozen whole batch record')
    require(d.get('reviewed_batch')==str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(bp)),'Evoker actual reviewed batch hash')
    for key,value in r.items():
        if key!='accepted_credit':require(canonical(d.get(key))==canonical(value),'Evoker missing complete context '+key)
    require(r['author_thread_id']==d['reviewer_thread_id'] and r['independent_reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Evoker distinct Main independent judgment')
    require(r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['upstream_code_executed'] is False and d.get('observed_chain')==r['observation'],'Evoker pending one bounded source policy')
    for key,desc in spec['bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and json.loads(b)==r['frozen_mechanism_context'][key],'Evoker immutable complete context '+key)
    f=r['frozen_mechanism_context'];q=f['proposal'];m=f['Main_review'];i=f['author_intake'];n=f['current_normalization'];checkpoint=f['original_read_checkpoint']
    require(m['proposal']==spec['bindings']['proposal'] and i['distinct_Main_review']['sha256']==spec['bindings']['Main_review']['sha256'],'Evoker original/distinct review binding')
    require(q['owner_thread_id']==i['owner_thread_id']==r['author_thread_id'] and m['reviewer_thread_id']==r['independent_reviewer_thread_id'],'Evoker proof of author roles')
    require(q['semantic_key']==m['semantic_key']==i['semantic_key']==r['semantic_key'] and m['recommended_maximum_credit']==q['proposed_maximum_credit']==1 and m['accepted_credit']==m['applied_credit']==q['accepted_credit']==q['applied_credit']==0,'Evoker one whole reviewed in principle only')
    require(len(q['observed_chain'])==14 and q['observed_chain']==n['original14_observations']==r['original_author_observations'],'Evoker complete original14 observations')
    require(len(q['mandatory_constraints'])==13 and q['mandatory_constraints']==m['mandatory_author_constraints_preserved']==i['all13_original_constraints_unchanged']==n['original13_constraints']==r['mandatory_constraints'],'Evoker complete13 original constraints')
    require(m['independent_findings']==i['all_Main_findings']==n['Main14_findings']==r['observation'] and len(m['independent_findings'])==14,'Evoker complete14 Main findings')
    require(m['limits']==i['all_Main_limits']==n['Main10_limits'] and len(m['limits'])==10 and q['limits']==n['original7_limits'] and r['limits']==q['limits']+m['limits'],'Evoker complete author and Main limits')
    require(q['mandatory_corrections']==m['mandatory_corrections']==r['mandatory_corrections']==n['mandatory_corrections']==[],'Evoker no silent replacement of old constraints')
    require(n['baseline_observation']==dict(count=44,master_sha256='7e791ce3366d7e1065b03893eda6f86de461633f6c62d5ca74ce17c6154be5f7',not_ongoing_master_authority=True),'Evoker immutable historical44 baseline not live authority')
    require(r['deduplication']==n['deduplication'] and r['application']==m['application'],'Evoker complete dedup and application boundary')
    require(len(r['deduplication']['current44_semantic_index'])==44 and len(r['current_ecology_comparison_bindings'])==6,'Evoker bounded current44 and six whole semantic comparisons')
    for desc in r['current_ecology_comparison_bindings']:
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'],'Evoker prior accepted batch changed');matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']]
        require(len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and {k:matches[0][k] for k in desc['actual_complete_selected_semantic_fields_read']}==desc['actual_complete_selected_semantic_fields_read'] and desc['same_complete_policy'] is False and desc['new_credit_for_prior']==0,'Evoker prior complete selected semantic judgment unchanged0')
    for desc in r['prior_whole_decision_bindings']:
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and {k:json.loads(b)[k] for k in desc['fields']}==desc['fields'] and desc['new_credit']==0,'Evoker prior EA22 complete judgment unchanged0')
    rows=[json.loads(x) for x in snap.read(DOCS.parent/'legacy-migration-acceptance/reviewed.jsonl').decode().splitlines() if x.strip()]
    require(len(r['migration_owner'])==4,'Evoker exactly four old whole owners')
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'] and {k:matches[0][k] for k in owner['fields']}==owner['fields'] and owner['new_credit']==0,'Evoker complete current global whole owner0')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(archive)==spec['artifact']['sha256'],'Evoker native archive changed')
    refs=q['actual_native_read_ranges'];require(refs==m['actual_native_read_ranges']==checkpoint['actual_native_read_ranges'] and len(refs)==12 and sum(x['lines'][1]-x['lines'][0]+1 for x in refs)==822,'Evoker original822 reading retained without replay credit')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref,e in zip(refs,r['chain']):
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'] and 1<=lo<=hi<=len(b.splitlines()),'Evoker exact original archive entry range')
            require(part.decode()==ref['raw_excerpt_utf8'] and sha(part)==ref['raw_excerpt_sha256']==e['raw_excerpt_sha256'] and ref['full_file']==((lo,hi)==(1,len(b.splitlines()))) and ref['entry']==e['path'] and [e['line'],e['end_line']]==ref['lines'],'Evoker exact raw excerpt and full-file scope')
    for key in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(key)) is int and d[key]==0,'Evoker no unsupported runtime/global credit '+key)
    decision=d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Evoker explicit nonacceptance0');return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Evoker exactly one whole source credit')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==12,'Evoker exact12 source checks');verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Evoker actual typed source check flags');verified.append(validate_evoker_native_source(e,snap))
    require(d.get('resource_checks')==[],'Evoker no invented raw loot/loaded resource proof')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(bp.relative_to(ROOT)),batch_sha256=sha(snap.read(bp)),source_checks_recomputed=verified,base_resource_checks_recomputed=[],supporting_ranges_credit=0,limitations=r['limits'],observed_chain=r['observation'],complete_chain_support_proof=dict(bindings=spec['bindings'],scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='actual original author confirmation, not self-independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




ZOMBIE_REINFORCEMENT_V30_SPEC = {'id': 'EA-0047', 'canonical_record_sha256': '51bb8cdea916d3fc39c13b37ff58fe0f2f786ff661cfbe2cf11f8c2a6f07f0cf', 'batch': 'batch-038.json', 'bindings': {'proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-zombie-reinforcement-whole-policy-proposal-20261109.json', 'sha256': 'c9a2f7253789a3c35b2da7f3712eb2f4c3285de6a978a5613502d828eef5bf37', 'bytes': 192388}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-zombie-reinforcement-whole-policy-review-20261109.json', 'sha256': '36f5ef9840a2386085225d4c13220633767b6011d77404b5c3875d142889ee7a', 'bytes': 101225}, 'current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-zombie-reinforcement-v30-current-normalization-20261109.json', 'sha256': 'd6adf0430e5de43e1365e2be94a298f1f1860db567be332ffb0955e48513bd69', 'bytes': 99834}}, 'native_source_hashes': ['408ebf7d0f027fe3ae2cc6a77a7c09fa4c837526f6a853ddae8b62283cc984cd', '61b1fa631740f9e0c7a5f97317326e60d701453988f15920f7098da330db2a1b', '3c7eff92cc350f149801d6b1eafb1ebc7996d22f842ee3277bb336a0bc482505', '7d96fb2a9daa060f35080429770788e2d6640d82c0e231a59c216668323dc22f', '6349170556e97282eef52e3a3e27b829627d3915e2d16763908f750ad67e297b', '9df481677eff26f7a726594e9d90bbe9b361eb63edc531084e0277f92c29bd12', '8893e18ecdf87f27706c6b9d8c6330384e35d6b3e6575675246932eb6ce98443', 'b482b084bda29915e3f8459e64eeae595d6d2616fb06167df7e2aa9875fa04af', '94eba868bc6ed1ec03acefdb7c91ad4101935fa78365f4c3d81a18a974cd6839', '53b7c6eeaa4df6532293ce97859136e4fd629c2476229bcb33420edb096425a7', 'e58ea30d11bf5ddc0d04152e0517b52d0549100ca90888dbaa7ad64700ad394e', '9e1a89946818e1f43f29c1504188d114b6547890312aa7ee086954845c918ce6', 'de051e3576abbc50ebddfd94700bde17966220ee958ed105fdc8da01765cdc58', '541aeef13e5b92d6b3d4d5beb4d4685e9b1073366d8d5860243e24519eba2565', 'f5c82d8a470337840b3a861259bca3ac146a9cbea663edc8281bf968fa6a7d2d', 'b337ae47e5c79a9d05915bd101bd8a961ad3e6813576652d20546690b5a147e0', '751c3f132717f9ae8f1cefa41782141aca8d4034dfed67dab2d0d8da74e6690f', '7c7c2b3a1239ff700fec8d079f0781deae6aa2a40b007b574e67da24c799f71f', '279b4caeec1c663c3fd433bc45fcf833c5317a1ea712f9ecc7d498f1101074f0', 'bffeb67644aa5bca307143fdfc31fd4266722f9c74086cee83080f9e8213fcdb', 'fdc066966e47a7f4813fd6522f8c59e98d3e3ba8da0e8b970de3138c906baaf3', 'ecae29c183162586936570834583f0907480d147122053ab7fc8a043d93f069f', 'ced83621fea9e81a603fdcc5eac1f6b9920eda4c77a17c384b421e6c13e2fdc9', '73c79a8828bb81fe587bd833397d8321a24238931e5177f095266676f495c10f', 'd3255c71323559cf901a4361cb5fd5b88440bc2462b38015bb6de5917edbdac5'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'exact_ranges': 25, 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review'}

def validate_zombie_reinforcement_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in ZOMBIE_REINFORCEMENT_V30_SPEC['native_source_hashes'], 'ZombieReinforcement native outside exact25-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'ZombieReinforcement native cannot impersonate Git')
    artifact = ZOMBIE_REINFORCEMENT_V30_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == ZOMBIE_REINFORCEMENT_V30_SPEC['coordinate'], 'ZombieReinforcement native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'ZombieReinforcement native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'ZombieReinforcement native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'ZombieReinforcement native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'ZombieReinforcement native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}

def validate_zombie_reinforcement_receipt(path, raw, batches_by_id, snap):
    spec=ZOMBIE_REINFORCEMENT_V30_SPEC;path=Path(path);d=json.loads(raw)
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0047.json').resolve(),'ZombieReinforcement exact original author namespace')
    require(d.get('id')==spec['id'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==AUTHORIZED['general']['thread_id'],'ZombieReinforcement actual original author identity')
    require(spec['id'] in batches_by_id,'ZombieReinforcement actual batch required');bp,r=batches_by_id[spec['id']]
    require(bp.resolve()==(DOCS/spec['batch']).resolve() and sha(canonical(r))==spec['canonical_record_sha256'] and snap.json(bp)['records']==[r],'ZombieReinforcement exact frozen whole batch record')
    require(d.get('reviewed_batch')==str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(bp)),'ZombieReinforcement actual reviewed batch hash')
    for key,value in r.items():
        if key!='accepted_credit':require(canonical(d.get(key))==canonical(value),'ZombieReinforcement missing complete context '+key)
    require(r['author_thread_id']==d['reviewer_thread_id'] and r['independent_reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id']!=r['independent_reviewer_thread_id'],'ZombieReinforcement distinct Main independent judgment')
    require(r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['upstream_code_executed'] is False and d.get('observed_chain')==r['observation'],'ZombieReinforcement pending one bounded source policy')
    for key,desc in spec['bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'] and json.loads(b)==r['frozen_mechanism_context'][key],'ZombieReinforcement immutable complete context '+key)
    f=r['frozen_mechanism_context'];q=f['proposal'];m=f['Main_review'];n=f['current_normalization']
    require(m['proposal']==spec['bindings']['proposal'] and q['owner_thread_id']==m['author_thread_id']==r['author_thread_id'] and m['reviewer_thread_id']==r['independent_reviewer_thread_id'],'ZombieReinforcement original and distinct review binding')
    require(q['semantic_key']==m['semantic_key']==r['semantic_key'] and m['maximum_related_whole_credit']==q['proposed_maximum_credit']==1 and m['formal_credit_applied_by_this_receipt']==q['accepted_credit']==q['applied_credit']==0 and q['formal_candidate_id'] is m['formal_candidate_id'] is None,'ZombieReinforcement one policy reviewed in principle only')
    require(len(q['observed_chain'])==17 and q['observed_chain']==m['author_observations_all17_retained']==n['original17_observations']==r['original_author_observations'],'ZombieReinforcement complete original17 observations')
    require(len(q['mandatory_constraints'])==13 and q['mandatory_constraints']==m['author_constraints_all13_retained']==n['original13_constraints']==r['mandatory_constraints'],'ZombieReinforcement complete13 original constraints')
    require(m['independent_findings']==n['Main15_findings']==r['observation'] and len(m['independent_findings'])==15,'ZombieReinforcement complete15 Main findings')
    require(m['mandatory_limits']==n['Main6_limits'] and len(m['mandatory_limits'])==6 and q['limits']==m['author_limits_all7_retained']==n['original7_limits'] and len(q['limits'])==7 and r['limits']==q['limits']+m['mandatory_limits'],'ZombieReinforcement complete author and Main limits')
    require(q['mandatory_corrections']==r['mandatory_corrections']==n['mandatory_corrections']==[],'ZombieReinforcement no silent replacement of old constraints')
    require(n['baseline_observation']==dict(count=45,master_sha256='a29beb75891e31e622872bc3d3059f74a4486db54df7237ae608ec4a5aa727f6',not_ongoing_master_authority=True),'ZombieReinforcement historical45 baseline not live authority')
    require(r['deduplication']==n['deduplication'] and r['application']==q['application'],'ZombieReinforcement complete dedup and application boundary')
    index=r['deduplication']['current45_semantic_index'];require(len(index)==45 and index==q['current45_accepted_semantic_index'],'ZombieReinforcement exact historical45 semantic index')
    for desc in index:
        b=snap.read(local_path(desc['batch'],ROOT));matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']]
        require(sha(b)==desc['batch_sha256'] and len(matches)==1 and matches[0]['semantic_key']==desc['semantic_key'] and sha(canonical(matches[0]))==desc['canonical_record_sha256'],'ZombieReinforcement preserve every old accepted whole record')
    comps=r['current_ecology_comparison_bindings'];require(len(comps)==5 and {x['id'] for x in comps}=={'EA-0016','EA-0032','EA-0036','EA-0039','EA-0041'},'ZombieReinforcement five complete selected comparisons')
    for desc in comps:
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'],'ZombieReinforcement prior accepted batch changed');matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']]
        require(len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and {k:matches[0][k] for k in desc['actual_complete_selected_semantic_fields_read']}==desc['actual_complete_selected_semantic_fields_read'] and desc['same_complete_policy'] is False and desc['new_credit_for_prior']==0,'ZombieReinforcement prior complete selected judgment unchanged0')
    lb=snap.read(local_path(q['migration_ledger']['path'],ROOT));require(sha(lb)==q['migration_ledger']['sha256'],'ZombieReinforcement exact migration ledger');rows=[json.loads(x) for x in lb.decode().splitlines() if x.strip()]
    require(len(r['migration_owner'])==3,'ZombieReinforcement exactly three old whole owners')
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'] and {k:matches[0][k] for k in owner['fields']}==owner['fields'] and owner['new_credit']==0,'ZombieReinforcement complete global whole owner0')
    archive=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(archive)==spec['artifact']['sha256'],'ZombieReinforcement native archive changed')
    refs=q['actual_native_read_ranges'];projection=lambda x:{k:x[k] for k in ('entry','entry_sha256','lines','full_file','raw_excerpt_sha256')}
    require([projection(x) for x in refs]==m['actual_Main_reading']['ranges'] and len(refs)==25 and len({x['entry'] for x in refs})==21 and sum(x['full_file'] for x in refs)==8 and sum(x['lines'][1]-x['lines'][0]+1 for x in refs)==1674,'ZombieReinforcement original1674 line inventory not new semantic credit')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for ref,e in zip(refs,r['chain']):
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'] and 1<=lo<=hi<=len(b.splitlines()),'ZombieReinforcement exact original archive entry range')
            require(part.decode()==ref['raw_excerpt_utf8'] and sha(part)==ref['raw_excerpt_sha256']==e['raw_excerpt_sha256'] and ref['full_file']==((lo,hi)==(1,len(b.splitlines()))) and ref['entry']==e['path'] and [e['line'],e['end_line']]==ref['lines'],'ZombieReinforcement exact raw excerpt and full-file scope')
    for key in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(key)) is int and d[key]==0,'ZombieReinforcement no unsupported runtime/global credit '+key)
    decision=d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'ZombieReinforcement explicit nonacceptance0');return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'ZombieReinforcement exactly one whole source credit')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==len(r['chain'])==25,'ZombieReinforcement exact25 source checks');verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'ZombieReinforcement actual typed source check flags');verified.append(validate_zombie_reinforcement_native_source(e,snap))
    require(d.get('resource_checks')==[],'ZombieReinforcement no invented loaded resource proof')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(bp.relative_to(ROOT)),batch_sha256=sha(snap.read(bp)),source_checks_recomputed=verified,base_resource_checks_recomputed=[],supporting_ranges_credit=0,limitations=r['limits'],observed_chain=r['observation'],complete_chain_support_proof=dict(bindings=spec['bindings'],scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='actual original author confirmation, not self-independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




CHARGED_TROPHY_V31_SPEC = {'id': 'EA-0048', 'canonical_record_sha256': 'd958c35f6ee66c780e579d3bf8230ffb0a84ebb6869bcca13643c8f2a014cced', 'batch': 'batch-039.json', 'bindings': {'candidate': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-charged-trophy-current46-whole-policy-candidate-20261110.json', 'sha256': 'f426408a8209aab65dd46d6126fffa5ea065f1ed50247ad23df6aad490291d77', 'bytes': 471639}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-charged-trophy-current46-whole-review-20261110.json', 'sha256': 'd224d2f0130f661943c9796aef60566e38dba7db0bef9a7945a3d206c4fd1c85', 'bytes': 218534}, 'author_confirmation': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-charged-trophy-v31-author-review-confirmation-20261110.json', 'sha256': '2b8ebdfcc38b864e2e320cd84d0c4bbbb01613de0c6852851a9117921bb70e8d', 'bytes': 37787}, 'current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-charged-trophy-v31-current-normalization-20261110.json', 'sha256': 'ed19c2860accd1a009cc886a095886db356f7bac864950c266b23be24ef1ca94', 'bytes': 256920}}, 'native_source_hashes': ['ea3d74f387c1b05cdc0bb4d35e3e9a57c1ffc69f12b1bededfc41d3400a3d780', '4ca5b0af986866c600eb8dba4535274055b4ebeef408878899bf127504f7e84c', 'f9138f2de43edaf2bc1995755c4d0ef0d205c8aad4b770146584cb8bd1c4f27b', '08ecfc3987a5422cb14b582d9dfd5ce01243d02a31a2340a7b1ffbb5907b4067', 'b9ecbb66600c599d37b583cd1bba466e4a7f80ee8196753bf4f72fd5c8676138', '8e8c7b8fa0e23f9d15e7af5735c2dbe362a47eeb4ec3faeed2f83a495a87c36b', '661755ad08d355b8c4c9d25ff72508d2406d36f66b8ba5e3a252823b498d1668', 'eb805d555fd0dacc79cc10ff267a8adc505e533e4400186c2c84011edb1ba741', 'f797bd0c902b5e865276fdbe48870a90d925b56be81b86e48ff1438702cf512d', 'd036ce448fa600190a1e75d1f4cacbc5ed88cf986add83ef0d0f39226dd42fc3', 'd2d26678ef4a323ee5f742876782764d165a964e2dd36bfbc8e012b2d423b41f', '7c36c256647483958bf743f879079e6e86e02b23b36f0d1c3e9173965ef4ccc2', '6a751000966cf2a9a2db5e7bb09d5b5eb26b397558c772c099b5ca0006618023', 'ca21173167c9fa47fac4655b11d54b585a10d2c69f98a747cc366bf26f6d87ac', 'b2f279cb101acc83ba5fae689f8873ed552ea85c0b64bc79cd4c829bfd1e71b3', '73ae24c33dedf18b98a65ce6bd38b32fe6f140ff27ebf7343880ba83b5490d1f', '613982ebf0b2d7cc97d353e219ffc625ae45bfd1bbe75b4d651e78839e94cca5', '8923d5334c87ef67ecc143387c392f48b68b04f5a4c2fbf5444d7379a41c40ce', '76ca793bb5e1d97fa3a85046b47eb42903cb6a3f227339d83c89da172e778238', 'd60af00a329f0a491e74de7f65da69c8998ecd4e3fc630c4796ca7f72da0c8a8', '463bf453ac6578bacc5b19dc8daace2835235b92d05fc960536a3a42b24bf3db', '01906ce0a69e6eb7e59d5f4735cd2b738c1569d3d1caffef5081968eb84acf7e', '95b7c5c90e142bbe447d19c082d7dcdf1881c90a29dd540e30f4dafeb46a50c1', '866c02154eac3590d87442997c10c48235f64c9e2e6f619306ac21902aa38dd4', '0bedcdbaca171226038c4caa601fc97c45b65ce7b32d682201d507c48904af68', 'd5a07b88666b8fa36d67154feeca53ba5069aa2f1e2a9c2e1387b612c858378f', '29fa3b1ccf941a0e2c121cfcc0a8dd92452a10aca4002afeb758d2a4e32f28af', 'bf540f0f74691df84c595e073734df23c77b6e4a42a1bd986e0ffb173f069630', '0768fd083a0234efb5c09ccdb9020d897eceb5e0faf3df91d402fd4b371618e9'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'exact_ranges': 29, 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete-chain review'}

def validate_charged_trophy_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in CHARGED_TROPHY_V31_SPEC['native_source_hashes'], 'ChargedTrophy native outside exact29-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'ChargedTrophy native cannot impersonate Git')
    artifact = CHARGED_TROPHY_V31_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == CHARGED_TROPHY_V31_SPEC['coordinate'], 'ChargedTrophy native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'ChargedTrophy native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'ChargedTrophy native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'ChargedTrophy native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'ChargedTrophy native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}

def validate_charged_trophy_receipt(path, raw, batches_by_id, snap):
    spec=CHARGED_TROPHY_V31_SPEC;path=Path(path);d=json.loads(raw);canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0048.json').resolve(),'ChargedTrophy exact author namespace')
    require(d.get('id')==spec['id'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==AUTHORIZED['general']['thread_id'],'ChargedTrophy actual original author identity')
    require(spec['id'] in batches_by_id,'ChargedTrophy actual batch');bp,r=batches_by_id[spec['id']]
    require(bp.resolve()==(DOCS/spec['batch']).resolve() and sha(canonical(r))==spec['canonical_record_sha256'] and snap.json(bp)['records']==[r],'ChargedTrophy exact complete frozen record')
    require(d.get('reviewed_batch')==str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(bp)),'ChargedTrophy actual batch hash')
    for key,value in r.items():
        if key!='accepted_credit':require(canonical(d.get(key))==canonical(value),'ChargedTrophy complete context '+key)
    require(r['author_thread_id']==d['reviewer_thread_id'] and r['independent_reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id']!=r['independent_reviewer_thread_id'],'ChargedTrophy distinct independent Main')
    require(r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['upstream_code_executed'] is False and d.get('observed_chain')==r['observation'],'ChargedTrophy one whole source-only pending policy')
    for key,desc in spec['bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'] and json.loads(b)==r['frozen_mechanism_context'][key],'ChargedTrophy immutable full context '+key)
    f=r['frozen_mechanism_context'];q=f['candidate'];m=f['Main_review'];a=f['author_confirmation'];n=f['current_normalization']
    require(m['proposal']==spec['bindings']['candidate'] and a['candidate']==spec['bindings']['candidate'] and a['distinct_Main_review']==spec['bindings']['Main_review'] and q['owner_thread_id']==a['owner_thread_id']==r['author_thread_id'] and m['reviewer_thread_id']==r['independent_reviewer_thread_id'],'ChargedTrophy original and all distinct review identity bindings')
    require(q['semantic_key']==m['semantic_key']==a['semantic_key']==r['semantic_key'] and q['proposed_maximum_credit']==m['proposed_maximum_credit']==1 and q['accepted_credit']==q['applied_credit']==m['formal_applied_credit']==0 and q['formal_candidate_id'] is m['formal_candidate_id'] is None,'ChargedTrophy no prior formal ID or applied credit')
    for key,desc in q['immutable_prior_bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'] and json.loads(b)==q['frozen_prior_context'][key],'ChargedTrophy frozen full prior context '+key)
    for mk,qk,ak,count in [('original_author_observations_retained','original16_observations','original16_observations',16),('original_author_constraints_retained','original14_constraints','original14_constraints',14),('original_author_limits_retained','original7_limits','original7_limits',7),('actual_Main_prior_context_reused','prior_distinct_Main16_findings','old_Main16_findings',16),('prior_Main_constraints_retained','prior_distinct_Main14_constraints','old_Main14_constraints',14),('prior_Main_limits_retained','prior_distinct_Main10_limits','old_Main10_limits',10),('original_author_supplement_observations_retained','current_supplementary_observations','supplement10_observations',10),('original_author_supplement_constraints_retained','current_additional_constraints','supplement8_constraints',8)]:
        require(m[mk]==q[qk]==a[ak] and len(q[qk])==count,'ChargedTrophy all unchanged prior/current substantive constraints '+qk)
    require(m['independent_findings']==a['new_Main13_findings']==r['observation'] and len(m['independent_findings'])==13 and m['mandatory_limits']==a['new_Main10_limits'] and len(m['mandatory_limits'])==10 and r['limits']==q['limits']+m['mandatory_limits'],'ChargedTrophy complete new Main findings and all limits')
    require(r['original_author_observations']==q['original16_observations'] and r['mandatory_constraints']==q['original14_constraints'] and r['mandatory_corrections']==q['mandatory_corrections']==[] and n['entire_new_Main_judgment_confirmed']==a and r['mandatory_package_constraints']==n,'ChargedTrophy full original author and private normalization retained')
    require(n['baseline_observation']==dict(count=46,master_sha256='10f529b20e08ad0b21cc96964354ce3f3bc8ab35d7e3b12931ac8329bcbbf049',not_ongoing_master_authority=True),'ChargedTrophy historical46 not live authority')
    index=q['current46_accepted_semantic_index'];require(len(index)==46 and index==n['all_old46_accepted_index'],'ChargedTrophy old46 index')
    for desc in index:
        b=snap.read(local_path(desc['batch'],ROOT));matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']];require(sha(b)==desc['batch_sha256'] and len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and matches[0]['semantic_key']==desc['semantic_key'],'ChargedTrophy exact all old46 complete records')
    require(r['current_ecology_comparison_bindings']==q['current_complete_selected_judgments_actually_read']==m['complete_current_five_judgments_actually_read'] and len(r['current_ecology_comparison_bindings'])==5,'ChargedTrophy five complete current selected judgments')
    for desc in r['current_ecology_comparison_bindings']:
        b=snap.read(local_path(desc['source']['path'],ROOT));matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']];require(sha(b)==desc['source']['sha256'] and len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and {k:matches[0][k] for k in desc['actual_complete_selected_judgment_fields_read']}==desc['actual_complete_selected_judgment_fields_read'] and desc['new_credit']==0,'ChargedTrophy complete current owner comparison unchanged0')
    require(r['prior_whole_decision_bindings']==q['prior_complete_EA16_EA26_judgments_reused0'] and len(r['prior_whole_decision_bindings'])==2,'ChargedTrophy two old whole ecology judgments')
    for desc in r['prior_whole_decision_bindings']:
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and {k:json.loads(b)[k] for k in desc['actual_complete_decision_fields']}==desc['actual_complete_decision_fields'] and desc['new_credit']==0,'ChargedTrophy prior complete judgment unchanged0')
    lb=q['current_migration_ledger_binding'];b=snap.read(local_path(lb['path'],ROOT));require(sha(b)==lb['sha256'],'ChargedTrophy exact migration ledger');rows=[json.loads(x) for x in b.decode().splitlines() if x.strip()]
    require(r['migration_owner']==q['current_whole_migration_owners_support_only']==m['current_four_migration_judgments_actually_read'] and len(r['migration_owner'])==4,'ChargedTrophy four whole migration owners')
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'] and {k:matches[0][k] for k in owner['actual_current_non_evidence_decision_fields']}==owner['actual_current_non_evidence_decision_fields'] and owner['new_credit']==0,'ChargedTrophy full global owner unchanged0')
    support=q['prior_own_whole_ZombieVillager_support_reused0'];b=snap.read(local_path(support['path'],ROOT));require(sha(b)==support['sha256'],'ChargedTrophy own earlier317 read remains own not Main')
    refs=n['all_actual_ref_descriptors'];require(len(refs)==len(r['chain'])==29 and refs[:15]==q['frozen_prior_context']['original_proposal']['actual_native_read_ranges'] and refs[15:28]==q['supplementary_actual_native_read_ranges']==m['actual_Main_supplementary_source_reading'],'ChargedTrophy exact original15 supplementary13 oldMain3line support')
    ar=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(ar)==spec['artifact']['sha256'],'ChargedTrophy exact mapped source archive')
    with zipfile.ZipFile(io.BytesIO(ar)) as z:
        for ref,e in zip(refs,r['chain']):
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'] and 1<=lo<=hi<=len(b.splitlines()) and part.decode()==ref['raw_excerpt_utf8'] and sha(part)==ref['raw_excerpt_sha256']==e['raw_excerpt_sha256'] and ref['full_file']==((lo,hi)==(1,len(b.splitlines()))) and ref['entry']==e['path'] and ref['lines']==[e['line'],e['end_line']],'ChargedTrophy original typed raw range identity')
    for key in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(key)) is int and d[key]==0,'ChargedTrophy no unsupported credit '+key)
    decision=d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'ChargedTrophy explicit nonacceptance0');return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'ChargedTrophy exactly one whole source credit')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==29,'ChargedTrophy exact29 typed source checks');verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'ChargedTrophy actual typed flags');verified.append(validate_charged_trophy_native_source(e,snap))
    require(d.get('resource_checks')==[],'ChargedTrophy no invented raw head loot or current resources')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(bp.relative_to(ROOT)),batch_sha256=sha(snap.read(bp)),source_checks_recomputed=verified,base_resource_checks_recomputed=[],supporting_ranges_credit=0,limitations=r['limits'],observed_chain=r['observation'],complete_chain_support_proof=dict(bindings=spec['bindings'],scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='actual original author confirmation, not self-independent review',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




FISHING_V32_SPEC = {'id': 'EA-0049', 'canonical_record_sha256': 'dde78c2150e406f98d1579fee1476ecbfcfb5dc2a02b918d0a76b9d0e34c87a8', 'batch': 'batch-040.json', 'bindings': {'candidate': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-fishing-habitat-timed-reel-whole-policy-candidate-20261110.json', 'sha256': '2ab3f8fd6bc91a05231e37638b8529b434b14575a37fb0090ec19d9dd9fa2865', 'bytes': 270106}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-fishing-current47-whole-review-20261110.json', 'sha256': '4ca28e062693dbe5748ac5f3bda11691afbd0247c7368895b01b303588b85add', 'bytes': 265862}, 'author_confirmation': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-fishing-v32-author-review-confirmation-20261110.json', 'sha256': '3cdc030bef7cc0f8ba137ae6e90263a8059022b6d5ae18dec19828d5e5f4229b', 'bytes': 33580}, 'current_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-fishing-v32-current-normalization-20261110.json', 'sha256': '077e2b2beed72f58513fc948093982605b757b43fdf8ad632482beb5fe66e6c6', 'bytes': 158796}}, 'native_source_hashes': ['38328935f47dcbc65f6d0b4d67353ce2e0168a29a259186b84a5a7780764a71f', '98b59d3a16bb76d345f11b9ec01a279cb9706f7466219ac55f6fc07bd4c6784d', 'bf9fb7c343587e002a3941a5bdae57d969e638e51b098d02f811d237a7a31ed1', '3ed3f91198f0e2344540198a311fb8b69e8e91c714b9ecb53d71896d793552cf', 'fd8fdda8cbd370dacd98f5356dd237b15166c0920845385e2227a9c15c7a23bb', '7ed09245561b1dc966d0d42bd541f06e0277eab06f531fff5a82933d3a8990aa', '3f8cedee815f837ad9a0a256cc32bac8caa5857f984f0cd797d27f4b1268f42d', '785bb05b2d9ba4c70f08d88ac0eacabe7c50cf72528d91db881ba2a580685199', 'be11954ae35e0d40ca7155c27bf068b75b915285a24b567ade3669c9d93a21a9', 'fb46d3278764fb484decf2d5b635873c300229b2ff4227d03aac6f7a33ce2d1a', '0a562a875fbc01462e428579d1007bc0f079e632807814d9e43705330093ccae', '45f494590658e8633c11a2f61ce7e6bdea9e6bf22f0d617982ff3f31f171b380', 'bb59ce260cc99b3a3e9217150c90e0f37526d74439b0c199dc1ebeff195dd8cb', '1810ad54d7c9065bf0a60af8f2632efc8efa15e0cc40506050b4b32bc8efbdab', '000d7afc7188ed9b08679639820bbd01cd25314151755e28098dca7a6ff60ad3', '6cc2643d2f3cb67f1ada5ac182a687af951856d5b0ca8a9fdd02017e415e19e4', '0e20a2edf7cb2e9ef2dfe625df1ef75b6497aa51b2456cb5273754deb628fa73', 'e7576d68240235fdb78adbf3ad282cc1dee1d2c0fbf3aabc87a47814832a1df6', '9e8a0d3270c6ab477683416ad759ca4e7602e3838c9e893f9b3e4ffa62de96e7', '7529f703accff0f28cb6785b982ea5489cf0d4777cac21e830368863de953086', 'e631a970651f8cb1e41b37da315eb49c622f327ea02b83efe5c58316db34428c', 'c361c3e83a4f942e5edb0d767164c2fffd1b56e9eb236924aa7032259739b7b6', '35bff7faf10c9d7bc973b1650effdc8eb28fdb7e80625da5d79006aa94eb4120'], 'resource_hashes': ['ece884dcb5d748d93a2de427b7826412958cbf2dcf69800ef65843b949d6e203', 'bb6fc7056c3d7d5cdd3feef7b24d5c5ffb63529eddf8d3df0451f03bca7366bc', '1e514dff42ee508a97fcd793332f36472d8c147ec867f5bd5e38a43820385b4a', 'ef4758b2112cd5cf6336ac8ce4e9e004923d05b49403badf274add513105be11'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'resource_artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar', 'sha256': 'f43d1ac034a8907edab190a17501fd4ca2b0af107d4231da364eeca8ab5ee317'}, 'exact_ranges': 23, 'exact_resources': 4, 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete fishing-chain review'}

def validate_fishing_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in FISHING_V32_SPEC['native_source_hashes'], 'Fishing native outside exact23-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'Fishing native cannot impersonate Git')
    artifact = FISHING_V32_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == FISHING_V32_SPEC['coordinate'], 'Fishing native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'Fishing native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'Fishing native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'Fishing native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'Fishing native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}

def validate_fishing_base_source(e, snap):
    canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    spec=FISHING_V32_SPEC
    require(sha(canonical(e)) in spec['resource_hashes'],'Fishing raw base resource outside exact4 contract')
    require(e.get('source_kind')=='fixed_raw_vanilla_base_resource' and e.get('source_artifact')==spec['resource_artifact'] and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')),'Fishing raw base cannot impersonate Git or current deployment')
    a=spec['resource_artifact'];b=snap.read(local_path(a['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(b)==a['sha256'],'Fishing raw base archive changed')
    with zipfile.ZipFile(io.BytesIO(b)) as z:raw=z.read(e['path'])
    copied=snap.read(local_path(e['source_local'],TOOLS/'sources/raw-vanilla-client-extra-1.20.1'))
    require(raw==copied and sha(raw)==e['source_sha256'] and raw.decode()==e['raw_utf8'],'Fishing complete raw entry/copy bytes mismatch')
    require(e['full_file'] is True and e['loaded_current_membership_proved'] is False and type(e['credit']) is int and e['credit']==0,'Fishing raw whole table support0 not loaded membership')
    json.loads(raw)
    return {k:e[k] for k in ('source_kind','source_artifact','path','source_local','source_sha256','full_file','loaded_current_membership_proved','credit')}


def validate_fishing_receipt(path, raw, batches_by_id, snap):
    spec=FISHING_V32_SPEC;path=Path(path);d=json.loads(raw);canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0049.json').resolve(),'Fishing exact original author namespace')
    require(d.get('id')==spec['id'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==AUTHORIZED['general']['thread_id'],'Fishing actual original author identity')
    require(spec['id'] in batches_by_id,'Fishing actual batch');bp,r=batches_by_id[spec['id']]
    require(bp.resolve()==(DOCS/spec['batch']).resolve() and sha(canonical(r))==spec['canonical_record_sha256'] and snap.json(bp)['records']==[r],'Fishing exact complete frozen record')
    require(d.get('reviewed_batch')==str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(bp)),'Fishing actual batch hash')
    for key,value in r.items():
        if key!='accepted_credit':require(canonical(d.get(key))==canonical(value),'Fishing complete context '+key)
    require(r['author_thread_id']==d['reviewer_thread_id'] and r['independent_reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id']!=r['independent_reviewer_thread_id'],'Fishing distinct independent Main')
    require(type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['upstream_code_executed'] is False and d.get('observed_chain')==r['observation'],'Fishing one whole pending source policy')
    for key,desc in spec['bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'] and json.loads(b)==r['frozen_mechanism_context'][key],'Fishing immutable full context '+key)
    f=r['frozen_mechanism_context'];q=f['candidate'];m=f['Main_review'];a=f['author_confirmation'];n=f['current_normalization']
    require(m['proposal']==a['candidate']==spec['bindings']['candidate'] and a['distinct_Main_review']==spec['bindings']['Main_review'] and q['owner_thread_id']==m['author_thread_id']==a['owner_thread_id']==r['author_thread_id'] and m['reviewer_thread_id']==r['independent_reviewer_thread_id'],'Fishing all original and independent identity bindings')
    require(q['semantic_key']==m['semantic_key']==a['semantic_key']==r['semantic_key'] and q['proposed_maximum_credit']==m['maximum_related_whole_credit']==1 and q['accepted_credit']==q['applied_credit']==m['formal_credit_applied_by_this_receipt']==0 and q['formal_candidate_id'] is m['formal_id'] is None,'Fishing no prior formal ID or applied credit')
    for mk,qk,ak,count in [('author32observations_preserved_verbatim','observed_chain','original32_observations',32),('author16mandatory_constraints_preserved_verbatim','mandatory_constraints','original16_constraints',16),('author13limits_preserved_verbatim','limits','original13_limits',13),('original_checkpoint9observations_preserved','original_checkpoint_observations_preserved','original_checkpoint9',9),('durability_checkpoint5observations_preserved','durability_checkpoint_observations_preserved','durability_checkpoint5',5)]:
        require(m[mk]==q[qk]==a[ak] and len(q[qk])==count,'Fishing full original context retained '+qk)
    require(m['independent_findings']==a['Main20_findings']==r['observation'] and len(m['independent_findings'])==20 and m['mandatory_limits']==a['Main12_limits'] and len(m['mandatory_limits'])==12 and r['limits']==q['limits']+m['mandatory_limits'],'Fishing entire distinct Main20/12 and original limits')
    require(r['original_author_observations']==q['observed_chain'] and r['mandatory_constraints']==q['mandatory_constraints'] and r['mandatory_corrections']==a['additive_source_corrections'] and len(r['mandatory_corrections'])==2 and n['entire_new_Main_judgment_confirmed']==a and r['mandatory_package_constraints']==n,'Fishing original unchanged with additive allINSIDE and rejected-negative qualifications')
    for desc in q['actual_read_checkpoints']:
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'],'Fishing actual immutable read checkpoint')
    require(n['baseline_observation']==dict(count=47,master_sha256='57db73b651959310f5359675e8ba914f2a746f511449f1155d12826eea7a4ed5',not_ongoing_master_authority=True),'Fishing historical47 not live authority')
    index=q['current_accepted_semantic_index'];require(len(index)==47 and index==m['current47_identity_index_only']==n['all_old47_accepted_index'],'Fishing old47 identity index')
    for desc in index:
        b=snap.read(local_path(desc['batch'],ROOT));matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']];require(sha(b)==desc['batch_sha256'] and len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and matches[0]['semantic_key']==desc['semantic_key'],'Fishing exact old47 complete records')
    require(r['current_ecology_comparison_bindings']==q['current_complete_selected_judgments_actually_read']==m['five_complete_selected_judgments_read'] and len(r['current_ecology_comparison_bindings'])==5,'Fishing five complete current comparisons')
    for desc in r['current_ecology_comparison_bindings']+[q['current_added_charged_trophy_whole_judgment_reused0']]:
        b=snap.read(local_path(desc['source']['path'],ROOT));matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']];require(sha(b)==desc['source']['sha256'] and len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and {k:matches[0][k] for k in desc['actual_complete_selected_judgment_fields_read']}==desc['actual_complete_selected_judgment_fields_read'] and desc['new_credit']==0,'Fishing existing whole owner unchanged0')
    seal=q['prior_complete_Seal_judgment_reused0'];b=snap.read(local_path(seal['path'],ROOT));require(sha(b)==seal['sha256'] and {k:json.loads(b)[k] for k in seal['actual_complete_decision_fields']}==seal['actual_complete_decision_fields'] and seal==m['complete_Seal_saved_decision_read_reused0'] and seal['new_credit']==0,'Fishing complete Seal saved decision reused0')
    charged=q['actual_charged_trophy_independent_whole_judgment_reused0'];b=snap.read(local_path(charged['source']['path'],ROOT));c=json.loads(b);require(sha(b)==charged['source']['sha256'] and c['independent_findings']==charged['independent_findings'] and c['mandatory_limits']==charged['mandatory_limits'] and charged==m['charged_trophy_Main_own_review_reused0'] and charged['new_credit']==0,'Fishing existing charged trophy Main whole judgment reused0')
    require(r['prior_whole_decision_bindings']==[seal,charged,q['current_added_charged_trophy_whole_judgment_reused0']] and q['current_added_charged_trophy_whole_judgment_reused0']==m['current_charged_trophy_owner'],'Fishing complete prior whole decisions retained')
    lb=q['current_migration_ledger_binding'];b=snap.read(local_path(lb['path'],ROOT));require(lb==m['migration_binding'] and sha(b)==lb['sha256'] and len(b)==lb['bytes'],'Fishing exact migration ledger');rows=[json.loads(x) for x in b.decode().splitlines() if x.strip()]
    require(r['migration_owner']==q['current_whole_migration_owners_support_only']==m['two_complete_migration_judgments_read'] and len(r['migration_owner'])==2,'Fishing two whole global migration owners')
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'] and {k:matches[0][k] for k in owner['actual_complete_non_evidence_decision_fields']}==owner['actual_complete_non_evidence_decision_fields'] and owner['new_credit']==0,'Fishing full global owner reused0')
    for support in q['reused_actual_native_support_only']:
        for key in ('binding','actual_own_verification'):
            if key in support:
                desc=support[key];b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'],'Fishing old actual native support binding0')
    refs=n['all_actual_ref_descriptors'];require(len(refs)==len(r['chain'])==23 and refs[:20]==q['actual_native_read_ranges']==m['Main_actual_reading']['primary_source_ranges'] and refs[20:]==[x['descriptor'] for x in q['reused_actual_native_support_only']],'Fishing exact primary20 reused3 ranges')
    ar=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(ar)==spec['artifact']['sha256'],'Fishing exact source archive')
    with zipfile.ZipFile(io.BytesIO(ar)) as z:
        for ref,e in zip(refs,r['chain']):
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'] and 1<=lo<=hi<=len(b.splitlines()) and part.decode()==ref['raw_excerpt_utf8'] and sha(part)==ref['raw_excerpt_sha256']==e['raw_excerpt_sha256'] and ref['full_file']==((lo,hi)==(1,len(b.splitlines()))) and ref['entry']==e['path'] and ref['lines']==[e['line'],e['end_line']],'Fishing typed raw source range')
    require(n['all_actual_raw_resource_descriptors']==q['actual_raw_base_resource_reads']==m['Main_actual_reading']['complete_raw_base_resources'] and len(r['base_resources'])==4,'Fishing exact four raw complete tables')
    for ref,e in zip(q['actual_raw_base_resource_reads'],r['base_resources']):
        require(ref['archive']==spec['resource_artifact']['path'] and ref['archive_sha256']==spec['resource_artifact']['sha256'] and ref['entry']==e['path'] and ref['entry_sha256']==e['source_sha256'] and ref['raw_utf8']==e['raw_utf8'] and ref['full_file'] is True and ref['loaded_current_membership_proved'] is False and type(ref['credit']) is int and ref['credit']==0,'Fishing raw resource original binding0')
    for key in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(key)) is int and d[key]==0,'Fishing no unsupported credit '+key)
    decision=d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'Fishing explicit nonacceptance0');return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'Fishing exactly one whole source credit')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==23,'Fishing exact23 typed native checks');verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'Fishing actual typed native check flags');verified.append(validate_fishing_native_source(e,snap))
    checks=d.get('resource_checks');require(isinstance(checks,list) and len(checks)==4,'Fishing exact4 typed raw base checks');resource_verified=[]
    for check,e in zip(checks,r['base_resources']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','complete_raw_utf8_match')) and check.get('loaded_current_membership_proved') is False,'Fishing actual raw base check flags');resource_verified.append(validate_fishing_base_source(e,snap))
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(bp.relative_to(ROOT)),batch_sha256=sha(snap.read(bp)),source_checks_recomputed=verified,base_resource_checks_recomputed=resource_verified,supporting_ranges_credit=0,limitations=r['limits'],observed_chain=r['observation'],complete_chain_support_proof=dict(bindings=spec['bindings'],scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='actual original author confirmation, not self-independent',native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))




MILK_CONTAINER_V33_SPEC = {'id': 'EA-0050', 'canonical_record_sha256': 'c7f61c849d61ce8924020e6c4888051ff79f26f5965815029d66727654caac5b', 'batch': 'batch-041.json', 'bindings': {'candidate': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-milk-container-curative-whole-policy-candidate-20261110.json', 'sha256': '8ec01815639209a6de0467bc1553834139ca366e48596fa4b46da42195f59dfd', 'bytes': 179384}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-milk-current48-whole-review-20261110.json', 'sha256': '3b9fdd686611f7d79e361433e59c33f02f3aa03966d17bffc1c0c07966b72688', 'bytes': 190976}, 'current48_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-milk-container-current48-normalization-20261110.json', 'sha256': '3d021ef9148d6ea3b79c116ba402d646c972c9a74da9d2948d9f56eea94d1fdb', 'bytes': 334324}, 'author_confirmation': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-milk-v33-author-review-confirmation-20261110.json', 'sha256': '248cf0141b24f629d526980d90a11943deda6a513fa6fec8d435ddb7dd18cbf9', 'bytes': 38816}, 'package_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-milk-v33-package-normalization-20261110.json', 'sha256': '6a735ad2482099c1170865a0aa2747c1c7c90830151d01757d50e949e3c55348', 'bytes': 131219}}, 'native_source_hashes': ['ea22fca04c779d35214085e72d9459af05a2f3c3764f49983e24d7c2fbdb6b2b', 'd72880bb9325773d042391eec224f6cfa43860c1ee33d51d0b1506e7fd26a360', '84ab7e58fde5f350560103fa253ef7a29ce6a2b881870223177c64da587742c5', '4be678acec5c8ba2e96948e4e65d5265910fe86b0daa3939920b8d8a46597917', '251aca3f3e6282fd65a503712d9964785055232fb85b11d8d50f70dc70235d7f', 'bb82d6712d44681fa9a0efa318cc211af5c25b6261a47ed3a5632f0c3adc86aa', '508e7a813d7e22f468badcaf8d399458b7d387ef0bc9db71b5ce532400caf79c', 'd73b4f3a4be49f005f319f98e40553c42ef6c99b1e43f79c32b24bfde0d85afa', '8b8994fc07c9a4ab91bb3d65ac69b338f23ae4f3d1db5aebe6cc88c72d07b050', '2e6ff06737463cc76008767ebfa4814f328a7d9bcd69aa2b24e0822d68c0c36c', '876fd1b9e51584a21d35a5fe6613d532da7b1e70c7ff28c78a6fa7e8d9efbdac', 'ef0b6c057a61d83ffb3aa493eb0d72523c65d4e55e090555e395ece341a05dba', '482e2ef43fc32d8dc5c089d8effc0a8d3d25d94a13e4a8971cf2227cb94796d7', 'b1be5ff9b4e323ac12a73aa218b16629048a784a411f68aad7b0ae20a1ab229c', 'ed274d45c18bc72f5199a39a1adfcca2e9cc0c6a51fe213ba261624560fc0b33', 'ddd3427056096fd04bb5e53f2bb9f529e7dc077920174481e69afecfb2620674', '87a9a9a61003fabdbcfb92f248ae672a97c2bfa81f1a64f3e165c1ceee9b6df3', '32d942e62bb0c4cc0e072a21bb33aaef4d52b05e18ec1aeff53d42a72aa71ae8', 'cbf323ebe4974e15672bb0eda08d6e0a43c32465b437cf4b760b010edf8d9a03', 'ae263b4c60ff02ec4b2899ab6d205385b66ffa875198e2ee1717176c22108369', 'e2212de49f26287e0fd285611b7bf219caeb6a22e6714e162c498a895d2c3330', '249b85111f6316f3014a2e5b059c1c5977cdbd58866994ca1522313303246d0b', 'a54bcb1415d1b378de93da4723754e1fc122ed371df5040a412f44bd9b31fdb9', 'b68cb403df47c8230ced93ab0aa40b82de1c6d0fbb391604bf3fa40ddf465c35', '91f227b51a6a42590488b00e1d913cf6faad138c39328dd9a8f62bd8fcfde36e', '5123d6090e23289daea0953f26de2003c79d84b01bdd849a7a848c2cc4b4ae4d', 'e280d81b8afeb7fa1272561e90b82a41d9209c231af31d025387f37c0951f159', 'b9d07431bd7da8b344788e4a36cb7931b3711593174b14d1206ae0d3be3606b2'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'exact_ranges': 28, 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete living-provider/container review'}

def validate_milk_container_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in MILK_CONTAINER_V33_SPEC['native_source_hashes'], 'MilkContainer native outside exact28-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'MilkContainer native cannot impersonate Git')
    artifact = MILK_CONTAINER_V33_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == MILK_CONTAINER_V33_SPEC['coordinate'], 'MilkContainer native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'MilkContainer native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'MilkContainer native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'MilkContainer native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'MilkContainer native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}

def validate_milk_container_receipt(path, raw, batches_by_id, snap):
    spec=MILK_CONTAINER_V33_SPEC;path=Path(path);d=json.loads(raw);canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    require(path.resolve()==(DOCS/'independent-reviews/general-EA0050.json').resolve(),'MilkContainer exact original author namespace')
    require(d.get('id')==spec['id'] and d.get('reviewer')==spec['receipt_label'] and d.get('reviewer_thread_id')==AUTHORIZED['general']['thread_id'],'MilkContainer actual original author identity')
    require(spec['id'] in batches_by_id,'MilkContainer actual batch');bp,r=batches_by_id[spec['id']]
    require(bp.resolve()==(DOCS/spec['batch']).resolve() and sha(canonical(r))==spec['canonical_record_sha256'] and snap.json(bp)['records']==[r],'MilkContainer exact complete frozen record')
    require(d.get('reviewed_batch')==str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256')==sha(snap.read(bp)),'MilkContainer actual batch hash')
    for key,value in r.items():
        if key!='accepted_credit':require(canonical(d.get(key))==canonical(value),'MilkContainer complete context '+key)
    require(r['author_thread_id']==d['reviewer_thread_id'] and r['independent_reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id']!=r['independent_reviewer_thread_id'],'MilkContainer distinct independent Main')
    require(type(r['proposed_credit']) is int and r['proposed_credit']==1 and type(r['accepted_credit']) is int and r['accepted_credit']==0 and r['upstream_code_executed'] is False and d.get('observed_chain')==r['observation'],'MilkContainer one pending whole source policy')
    for key,desc in spec['bindings'].items():
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'] and json.loads(b)==r['frozen_mechanism_context'][key],'MilkContainer immutable complete context '+key)
    f=r['frozen_mechanism_context'];q=f['candidate'];m=f['Main_review'];n=f['current48_normalization'];a=f['author_confirmation'];p=f['package_normalization']
    require(m['proposal']==n['original_proposal']==a['candidate']==spec['bindings']['candidate'] and n['frozen_original_proposal']==q and a['distinct_Main_review']==spec['bindings']['Main_review'] and a['current48_normalization']==spec['bindings']['current48_normalization'],'MilkContainer unchanged original proposal and current48 bindings')
    require(q['owner_thread_id']==m['author_thread_id']==a['owner_thread_id']==r['author_thread_id'] and m['reviewer_thread_id']==r['independent_reviewer_thread_id'] and q['semantic_key']==m['semantic_key']==n['semantic_key']==a['semantic_key']==r['semantic_key'],'MilkContainer all identity and historical semantic-key bindings')
    require(q['proposed_maximum_credit']==m['maximum_related_whole_credit']==1 and q['accepted_credit']==q['applied_credit']==n['accepted_credit']==n['applied_credit']==m['formal_credit_applied_by_this_receipt']==0 and q['formal_candidate_id'] is m['formal_id'] is n['formal_candidate_id'] is None,'MilkContainer no prior formal ID or applied credit')
    for mk,qk,ak,count in [('author23observations_preserved_verbatim','observed_chain','original23_observations',23),('author15mandatory_constraints_preserved_verbatim','mandatory_constraints','original15_constraints',15),('author8limits_preserved_verbatim','limits','original8_limits',8),('original20observations_preserved_verbatim','original20_observations','checkpoint20_observations',20),('original7limits_preserved_verbatim','original7_limits','checkpoint7_limits',7)]:
        require(m[mk]==q[qk]==a[ak] and len(q[qk])==count,'MilkContainer all original observations and limitations '+qk)
    require(m['independent_findings']==a['Main22_findings']==r['observation'] and len(m['independent_findings'])==22 and m['mandatory_limits']==a['Main11_limits'] and len(m['mandatory_limits'])==11 and r['limits']==q['limits']+m['mandatory_limits'],'MilkContainer entire independent Main22/11 retained')
    require(r['original_author_observations']==q['observed_chain'] and r['mandatory_constraints']==q['mandatory_constraints'] and r['mandatory_corrections']==[a['whole_scope_qualification']] and a['whole_scope_qualification']==p['whole_scope_qualification'] and p['entire_Main_judgment_confirmed']==a and r['mandatory_package_constraints']==p,'MilkContainer explicit narrowed whole scope not new cure')
    strong=m['existing_TConstruct_complete_Main103_judgment_reused0'];sd=m['existing_TConstruct_Main103_binding'];b=snap.read(local_path(sd['path'],ROOT));prior=json.loads(b)
    require(sha(b)==sd['sha256'] and len(b)==sd['bytes'] and [x for x in prior['ten_complete_old_judgments_read_and101_Main_own_judgment_reused0'] if x['id']==strong['id']]==[strong] and strong['credit_from_comparator']==0 and strong['full_object_canonical_sha256']==m['existing_TConstruct_current500_row_canonical_sha256'],'MilkContainer entire prior TConstruct milk-curative/equipment-release owner0')
    require(r['cross_domain_already_owned_curative_comparison']==strong and r['cross_domain_already_owned_curative_binding']==sd and a['whole_scope_qualification']['complete_TConstruct_owner']==strong and a['whole_scope_qualification']['owner_binding']==sd and a['whole_scope_qualification']['exact_Main_finding']==m['independent_findings'][17] and a['whole_scope_qualification']['generic_cure_policy_credit']==a['whole_scope_qualification']['equipment_replacement_policy_credit']==0,'MilkContainer cross-domain owner cannot create second cure/immunity credit')
    require(p['baseline_observation']==dict(count=48,master_sha256='55f69b141c7f428b0106702a736977af0f3db326f8dcb8d7c9498ca8e1bcff7b',not_ongoing_master_authority=True),'MilkContainer historical48 not live authority')
    index=n['current48_accepted_semantic_index'];require(len(index)==48 and index==p['all_old48_accepted_index'] and index[:-1]==q['current47_accepted_semantic_index'],'MilkContainer unchanged47 plus accepted fishing identity index')
    for desc in index:
        b=snap.read(local_path(desc['batch'],ROOT));matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']];require(sha(b)==desc['batch_sha256'] and len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and matches[0]['semantic_key']==desc['semantic_key'],'MilkContainer old48 complete records unchanged')
    require(r['current_ecology_comparison_bindings']==q['current_complete_selected_judgments_actually_read']==m['four_complete_current_judgments']==n['original_four_complete_selected_judgments_retained'] and len(r['current_ecology_comparison_bindings'])==4,'MilkContainer four complete ecology owners')
    for desc in r['current_ecology_comparison_bindings']+[n['newly_formal_fishing_complete_owner_reused0']]:
        b=snap.read(local_path(desc['source']['path'],ROOT));matches=[x for x in json.loads(b)['records'] if x['id']==desc['id']];require(sha(b)==desc['source']['sha256'] and len(matches)==1 and sha(canonical(matches[0]))==desc['canonical_record_sha256'] and {k:matches[0][k] for k in desc['actual_complete_selected_judgment_fields_read']}==desc['actual_complete_selected_judgment_fields_read'] and desc['new_credit']==0,'MilkContainer complete old or fishing whole comparison unchanged0')
    seal=q['prior_complete_Seal_judgment_reused0'];b=snap.read(local_path(seal['path'],ROOT));require(sha(b)==seal['sha256'] and {k:json.loads(b)[k] for k in seal['actual_complete_decision_fields']}==seal['actual_complete_decision_fields'] and seal==m['complete_Seal_saved_decision_reused0']==n['prior_complete_Seal_judgment_reused0'] and seal['new_credit']==0,'MilkContainer complete Seal saved decision0')
    fish=m['current_fishing_Main_complete_judgment_reused0'];b=snap.read(local_path(fish['source']['path'],ROOT));fd=json.loads(b);require(sha(b)==fish['source']['sha256'] and fd['independent_findings']==fish['independent_findings']==n['fishing_entire_Main20_findings'] and fd['mandatory_limits']==fish['mandatory_limits']==n['fishing_entire_Main12_limits'] and fish['new_credit']==0,'MilkContainer complete Main fishing20/12 retained0')
    require(r['prior_whole_decision_bindings']==[seal,n['newly_formal_fishing_complete_owner_reused0'],fish],'MilkContainer full prior owner bindings')
    lb=q['current_migration_ledger_binding'];b=snap.read(local_path(lb['path'],ROOT));require(lb==m['migration_binding']==n['current_migration_ledger_binding'] and sha(b)==lb['sha256'] and len(b)==lb['bytes'],'MilkContainer exact migration ledger');rows=[json.loads(x) for x in b.decode().splitlines() if x.strip()]
    require(r['migration_owner']==q['current_whole_migration_owners_support_only']==m['three_complete_migration_decisions_read']==n['original_three_complete_migration_judgments_retained'] and len(r['migration_owner'])==3,'MilkContainer three complete migration owners')
    for owner in r['migration_owner']:
        matches=[x for x in rows if x.get('candidate_id')==owner['candidate_id']];require(len(matches)==1 and sha(canonical(matches[0]))==owner['canonical_complete_row_sha256'] and {k:matches[0][k] for k in owner['actual_current_non_evidence_decision_fields']}==owner['actual_current_non_evidence_decision_fields'] and owner['new_credit']==0,'MilkContainer whole migration owner0')
    for desc in [q['original_read_checkpoint'],q['prior_native_pickup_admission_support_reused0']['source'],n['newly_formal_fishing_closure']]:
        b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'],'MilkContainer exact original or closed source proof')
    for support in q['prior_native_pickup_admission_support_reused0']['descriptors']:
        for key in ('binding','actual_own_verification'):
            if key in support:
                desc=support[key];b=snap.read(local_path(desc['path'],ROOT));require(sha(b)==desc['sha256'] and len(b)==desc['bytes'],'MilkContainer reused original native support0')
    refs=p['all_actual_ref_descriptors'];require(len(refs)==len(r['chain'])==28 and refs[:25]==q['actual_native_read_ranges']==m['Main_actual_reading']['primary_source_ranges'] and refs[25:]==[x['descriptor'] for x in q['prior_native_pickup_admission_support_reused0']['descriptors']],'MilkContainer primary25 reused3 exact source chain')
    ar=snap.read(local_path(spec['artifact']['path'],ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'));require(sha(ar)==spec['artifact']['sha256'],'MilkContainer exact mapped source archive')
    with zipfile.ZipFile(io.BytesIO(ar)) as z:
        for ref,e in zip(refs,r['chain']):
            b=z.read(ref['entry']);lo,hi=ref['lines'];part=b''.join(b.splitlines(keepends=True)[lo-1:hi]);require(ref['archive']==spec['artifact']['path'] and ref['archive_sha256']==spec['artifact']['sha256'] and ref['coordinate']==spec['coordinate'] and sha(b)==ref['entry_sha256'] and 1<=lo<=hi<=len(b.splitlines()) and part.decode()==ref['raw_excerpt_utf8'] and sha(part)==ref['raw_excerpt_sha256']==e['raw_excerpt_sha256'] and ref['full_file']==((lo,hi)==(1,len(b.splitlines()))) and ref['entry']==e['path'] and ref['lines']==[e['line'],e['end_line']],'MilkContainer exact typed raw source range')
    for key in ('global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit'):
        require(type(d.get(key)) is int and d[key]==0,'MilkContainer no unsupported credit '+key)
    decision=d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and type(d.get('accepted_credit')) is int and d['accepted_credit']==0,'MilkContainer explicit nonacceptance0');return dict(state='non_accepting',role='general',id=spec['id'],decision=decision,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit']==1,'MilkContainer exactly1 related provider-container whole, not new cure')
    checks=d.get('source_checks');require(isinstance(checks,list) and len(checks)==28,'MilkContainer exact28 typed source checks');verified=[]
    for check,e in zip(checks,r['chain']):
        require(check.get('evidence')==e and all(check.get(k) is True for k in ('archive_sha256_match','entry_bytes_match','fixed_coordinate_match','excerpt_exact')),'MilkContainer actual typed flags');verified.append(validate_milk_container_native_source(e,snap))
    require(d.get('resource_checks')==[],'MilkContainer no invented raw resource membership')
    return dict(state='validated_acceptance',id=spec['id'],role='general',reviewer=d['reviewer'],decision=decision,semantic_key=r['semantic_key'],accepted_credit=1,receipt=str(path.relative_to(ROOT)),receipt_sha256=sha(raw),batch=str(bp.relative_to(ROOT)),batch_sha256=sha(snap.read(bp)),source_checks_recomputed=verified,base_resource_checks_recomputed=[],supporting_ranges_credit=0,limitations=r['limits'],observed_chain=r['observation'],complete_chain_support_proof=dict(bindings=spec['bindings'],scope=r['evidence_scope'],independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'],General_perspective='actual original source author, not self-independent',generic_curative_whole_credit=0,equipment_replacement_whole_credit=0,native_gameplay_credit=0,runtime_material_payment_credit=0,global_novelty_credit=0,new_migration_credit=0))


AXOLOTL_RECOVERY_V34_SPEC = {'id': 'EA-0051', 'canonical_record_sha256': '6b8e9e550144df28029558eccc076fd00e89c866655fc9123856efbd8e17b82c', 'batch': 'batch-042.json', 'bindings': {'candidate': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-axolotl-injury-recovery-whole-policy-candidate-20261110.json', 'sha256': '85d452de473ed4e7cb1f28db8b033f0e7274bb5d97953f2d949de1c8ac7843d9', 'bytes': 251019}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-axolotl-recovery-whole-review-20261110.json', 'sha256': '047c7a8fe3e6ab5372498947b4a7de1328f494161e9f8a36b3ef4da514ece3e7', 'bytes': 236314}, 'author_acknowledgment': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-axolotl-Main21-12-original-author-acknowledgment-20261110.json', 'sha256': 'b8779f14139dbe9ab6d292520e0a077a7d45fa1dbd220283e19862a15560f497', 'bytes': 132262}, 'minimum_plan': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-axolotl-current49-minimum-research-package-plan-20261110.json', 'sha256': '652ee748f99d2ce572c56667512d33c7a774fe44ef33d1d11e19621ac51c2055', 'bytes': 314797}, 'Main_plan_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-axolotl-current49-minimum-plan-review-20261110.json', 'sha256': 'b31a31170f074317f5f7c6ce2d0d64bd91015e00d6883252eb826f4c64b54875', 'bytes': 4849}, 'preinstall_rejection': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-axolotl-v34-preinstall-rejection-20261110.json', 'sha256': 'a10fe0db1cacb4492a81324e8880854f8d63237d3b3b53ff03fcdfcc3c774cde', 'bytes': 5001}, 'package_normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-axolotl-v34-package-normalization-20261110.json', 'sha256': '9f0db3ad5b1e5fe3ad4e8270d9dbaa5363f3ead94299e4e6a35144b1138d4c4f', 'bytes': 462448}}, 'native_source_hashes': ['5f0bbed90c84bf9c2619503ee91a2d915412157759069e6c16f515b571a2857c', 'f43335b2b04b96cab7627512ff336f9bafdfab9913a115fe70d2b96448cc126f', '5728b1eb21833457585572ff01ab56fc5ec7199875ec448d84f7a76ab0833c42', '618891e17c20fbb96ad1c3d65fd1a6adea59bf07c5123cf7642c5ffb157ee757', 'c7cad73b08194b27981ed15e6386643d42b30945cb14c95eb467e78fc9585f86', '356ab916497151082713895d399e84238cb9761fc3885cfb18c663f526ae292b', '3b4d38f88ec9e7af7c82567f22cc2f579166919034580dfb898a151a1d3bf29b', '200f358980994bc07ad1aaba970fbd1ff1376e23c4ade25e9f16380a3671b33d', 'fba25bbfb59e5c2dc2dde99257adc19affb76538614f968793e23757915e5608', '3e21b9b192116a852bde7fa6900710afeb2228ba1fca45d222b5aac2bb206249', 'ca6279efd9e73e9b9ba6a48952f7d496b55e6ffba58d2c13be00499e049f0407', '53727c3acf9ffbdc061c000993a0869680320f6f8f178f9fe11310b072c194b9', '78409d94b63ea9cbcba13f87fe45409db6e80e5453cef68f7e072c37ea795a67', '6cfc8df3ac088cb752d48a64e9d8f04300f6f4a54f92df43e3d8a53610648b1a', '8a72196f702de39f4d9e0e2b8caccc6fb0169328b6df17b9e969529cb5e08c01', '41e68c69a8a4d34969a19cd6e315742edc7afa69b5f35e5eefae339b271c0cd6', 'f637536315aa65041b8620c283762f4700e4ed158fc048572e99a4cfd8d942cf', '5234e6bf843d8cf7c66f388c985d4893e55065cbd4dd6ff66383393ff03bca42', 'b130386f5343e1b3b3e762d5deccf5ef6a2e396bb66b1777c91ec59253c24df2', '39e121f6b830cde826c1ea1bf175ae7de795e41b087b482af8b9b732e24cebbd', '9934adb669357c972f537ca7fb7e8ed6cb98665e61d6a015e7d08d77095fc3d4', '36b6f527d9ebf2d48317d449ef19d3f712cf4af396f5ca9d53d059895433e503', '48addd2cab36d0b8b7ff5b6cf26ebf46f479243ee012bdf95e7d22f44de6f89b', '958d4a90f53c635930a0864ed0fe5ab3b5056e9c801519717aa19ebbf6f9bb33', 'b7b72fb4041ff4322ce0ce157198424c02b0ef0e1c3d887453b24890ee0253e5', '23fd3ff00f319225e8d7820035d247dbcb8111170f56297f126d1ddf51abb6e5', 'e744068c4177e4adc0941556836318fedb2e2f879f4008fbe066a1d05bdb88d4', '11d0699557e8b1c4998ff5e5b80983645e249fb161fb2f2432473efa42ea1c12', '8075c02467b111ba04470e89ca048221780b8a80aeb27679a286f3659c21e8e0', '35baf1f206251e29e09aa74ff3ed55f9f5cba74c64cfed7474f96711178dc719', '512c71a74cc5f9f0c33ce2fb2c8dc1b92628b5c84ada1ea11a20e69d6a733512', '14c325d3a51e974e991438666548c70684a8328443fa50d89ba06dd3495d94b0', '44da53eaa403754c42b146b9876e681aa9382554f06a03db33b41b9eef43dd08', 'e2423b1248165f0dc39f5316596cd1c414bbfb187ff4a45d73ef43382e5285bf', 'a2c99010c2b8988d403859b3f46ec9601ac6e32c75e979f82da30ee9c458b4f7', 'ce0d7955f22b81c4b6adc39287f9aad49bfaac02b33909d76641c27a8e7025f0', 'ad904783b8c8881b8c499e08475b788e3d963868480b1814e264e1f015498ecf', '0ee3195ff14cb4ecf1015f3c50bb4766c99d8692593dfa0323ba314ceade49e7'], 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'exact_ranges': 38, 'historical_baseline': {'count': 49, 'master_sha256': '70f6e4fc629947aa59f7d54badef38a6fb9e712ad632e42fcb246609580a982a', 'not_ongoing_master_authority': True}, 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete axolotl recovery review'}

def validate_axolotl_recovery_native_source(e, snap):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical(e)) in AXOLOTL_RECOVERY_V34_SPEC['native_source_hashes'], 'AxolotlRecovery native outside exact38-range contract')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo','revision','git_blob_sha1','tree_metadata','source_metadata')), 'AxolotlRecovery native cannot impersonate Git')
    artifact = AXOLOTL_RECOVERY_V34_SPEC['artifact']
    require(e.get('source_artifact') == artifact and e.get('source_coordinate') == AXOLOTL_RECOVERY_V34_SPEC['coordinate'], 'AxolotlRecovery native artifact identity mismatch')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'AxolotlRecovery native archive changed')
    with zipfile.ZipFile(io.BytesIO(archive)) as z: raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    lo, hi = e['line'], e['end_line']
    require(raw == copied and sha(raw) == e['source_sha256'], 'AxolotlRecovery native entry/copy mismatch')
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'AxolotlRecovery native range invalid')
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'] and sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'AxolotlRecovery native excerpt mismatch')
    return {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}


def validate_axolotl_recovery_receipt(path, raw, batches_by_id, snap):
    spec = AXOLOTL_RECOVERY_V34_SPEC
    path = Path(path)
    d = json.loads(raw)
    canonical = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    zero = lambda v: type(v) is int and v == 0
    require(path.resolve() == (DOCS / 'independent-reviews/general-EA0051.json').resolve(), 'AxolotlRecovery exact original-author namespace')
    require(d.get('id') == spec['id'] and d.get('reviewer') == spec['receipt_label'] and d.get('reviewer_thread_id') == AUTHORIZED['general']['thread_id'], 'AxolotlRecovery actual original author identity')
    require(spec['id'] in AUTHORIZED['general']['allowed_ids'] and spec['id'] in batches_by_id, 'AxolotlRecovery exact authorized ID and actual batch')
    bp, r = batches_by_id[spec['id']]
    require(bp.resolve() == (DOCS / spec['batch']).resolve() and sha(canonical(r)) == spec['canonical_record_sha256'] and snap.json(bp)['records'] == [r], 'AxolotlRecovery exact complete frozen single record')
    require(d.get('reviewed_batch') == str(bp.relative_to(ROOT)) and d.get('reviewed_batch_sha256') == sha(snap.read(bp)), 'AxolotlRecovery actual batch bytes')
    for key, value in r.items():
        if key != 'accepted_credit':
            require(canonical(d.get(key)) == canonical(value), 'AxolotlRecovery entire record context ' + key)
    require(r['general_context_schema'] == 'axolotl-recovery-v34' and r['author_thread_id'] == d['reviewer_thread_id'] and r['independent_reviewer_thread_id'] == '01a16364-cac0-7ca2-a042-a5312781ca34' and r['author_thread_id'] != r['independent_reviewer_thread_id'], 'AxolotlRecovery exact schema and distinct actual Main')
    require(type(r['proposed_credit']) is int and r['proposed_credit'] == 1 and zero(r['accepted_credit']) and r['upstream_code_executed'] is False and d.get('observed_chain') == r['observation'], 'AxolotlRecovery one pending whole and full observed chain')
    f = r['frozen_mechanism_context']
    require(set(f) == set(spec['bindings']) and r['immutable_bindings'] == spec['bindings'], 'AxolotlRecovery exact immutable binding set')
    for key, desc in spec['bindings'].items():
        b = snap.read(local_path(desc['path'], ROOT))
        require(sha(b) == desc['sha256'] and len(b) == desc['bytes'] and json.loads(b) == f[key], 'AxolotlRecovery immutable full context ' + key)
    q, m, a, p, v, n = (f[k] for k in ('candidate', 'Main_review', 'author_acknowledgment', 'minimum_plan', 'Main_plan_review', 'package_normalization'))
    require(m['proposal'] == a['candidate'] == spec['bindings']['candidate'] and a['distinct_Main_review'] == spec['bindings']['Main_review'] and v['plan'] == spec['bindings']['minimum_plan'] and v['actual_original_author_ack'] == spec['bindings']['author_acknowledgment'], 'AxolotlRecovery unchanged proposal, actual author and plan-review bindings')
    require(v['reviewer_thread_id'] == m['reviewer_thread_id'] == r['independent_reviewer_thread_id'] and q['owner_thread_id'] == a['owner_thread_id'] == p['owner_thread_id'] == r['author_thread_id'], 'AxolotlRecovery all author and independent reviewer identities')
    require(v['decision'] == 'PLAN_CONTRACT_ACCEPTED_DRAFT_ONLY_PARAMETERS_GRANTED_SEPARATE_EXACT_BYTES_REVIEW_REQUIRED' and v['draft_only_parameters'] == n['Main_granted_draft_parameters'] and v['draft_only_parameters'] == dict(id=spec['id'], batch_path=str(bp.relative_to(ROOT)), schema_version='v34', batch_general_context_schema='axolotl-recovery-v34', receipt_path='docs/cod4/audit-20261022/ecology-availability-research/independent-reviews/general-EA0051.json'), 'AxolotlRecovery private parameter grant is not installation or real receipt proof')
    require(q['semantic_key'] == a['semantic_key'] == r['semantic_key'] and q['proposed_maximum_credit'] == m['proposed_maximum_whole_credit'] == 1 and zero(q['accepted_credit']) and zero(q['applied_credit']) and q['formal_candidate_id'] is a['formal_id'] is None and zero(a['formal_applied_credit']) and zero(m['formal_applied_credit']), 'AxolotlRecovery original history unchanged and unapplied')
    for mk, qk, ak, nk, count in [
        ('original17_checkpoint_observations_preserved', 'original17_checkpoint_observations_preserved', 'original17_checkpoint_observations_preserved', 'original17_checkpoint_observations', 17),
        ('original15_supplement_observations_preserved', 'original15_supplement_observations_preserved', 'original15_supplement_observations_preserved', 'original15_supplement_observations', 15),
        ('original24_candidate_observations_preserved', 'observed_chain', 'original24_candidate_observations_preserved', 'complete_original24_observations', 24),
        ('original15_mandatory_constraints_preserved', 'mandatory_constraints', 'original15_mandatory_constraints_preserved', 'complete_original15_constraints', 15),
        ('original10_candidate_limits_preserved', 'limits', 'original10_candidate_limits_preserved', 'complete_original10_limits', 10),
    ]:
        require(m[mk] == q[qk] == a[ak] == p[nk] and len(q[qk]) == count, 'AxolotlRecovery full original observations and limits ' + qk)
    require(m['Main_findings'] == a['entire_Main21_findings_actually_read'] == p['complete_Main21_findings'] == r['observation'] and len(m['Main_findings']) == 21 and m['Main_limits'] == a['entire_Main12_limits_actually_read'] == p['complete_Main12_limits'] and len(m['Main_limits']) == 12, 'AxolotlRecovery complete independent Main21/12')
    require(r['limits'] == q['limits'] + m['Main_limits'] and r['original_author_observations'] == q['observed_chain'] and r['mandatory_constraints'] == q['mandatory_constraints'] and r['mandatory_corrections'] == [a['whole_scope_qualification']] and r['mandatory_package_constraints'] == n, 'AxolotlRecovery original and additive scope limits')
    require(len(a['original_author_itemized_findings_acknowledgments']) == 21 and len(a['original_author_itemized_limits_acknowledgments']) == 12, 'AxolotlRecovery real author read entire Main judgment')
    for field, originals, key in [('original_author_itemized_findings_acknowledgments', m['Main_findings'], 'complete_Main_finding'), ('original_author_itemized_limits_acknowledgments', m['Main_limits'], 'complete_Main_limit')]:
        for i, (ack, original) in enumerate(zip(a[field], originals), 1):
            require(ack['number'] == i and ack[key] == original and isinstance(ack['actual_author_acknowledgment'], str) and bool(ack['actual_author_acknowledgment']), 'AxolotlRecovery complete itemized original author acknowledgment')
    require(n['entire_original_author_acknowledgment'] == a and n['whole_scope_qualification'] == a['whole_scope_qualification'] and n['complete_Main21_findings'] == m['Main_findings'] and n['complete_Main12_limits'] == m['Main_limits'], 'AxolotlRecovery package full original author and independent context')
    index = q['current_accepted_semantic_index']
    require(len(index) == 49 and index == p['historical_old49_index_not_source_rereading'] == n['all_old49_accepted_semantic_index'], 'AxolotlRecovery complete historical49 index, not ongoing master authority')
    require(n['baseline_observation'] == spec['historical_baseline'] and n['historical_master_binding'] == p['bindings']['current49_master'] == m['current_ecology_ledger'] == a['current49_historical_baseline'], 'AxolotlRecovery fixed historical49 observation, no live master comparison')
    for desc in index:
        b = snap.read(local_path(desc['batch'], ROOT))
        matches = [x for x in json.loads(b)['records'] if x['id'] == desc['id']]
        require(sha(b) == desc['batch_sha256'] and len(matches) == 1 and sha(canonical(matches[0])) == desc['canonical_record_sha256'] and matches[0]['semantic_key'] == desc['semantic_key'], 'AxolotlRecovery unchanged old49 complete canonical records')
    comparisons = r['current_ecology_comparison_bindings']
    require(comparisons == m['complete_selected_ecology_comparisons'] == a['complete_selected_ecology_comparisons_preserved'] == p['entire_selected_ecology_comparisons'] and len(comparisons) == 3, 'AxolotlRecovery complete three ecology comparisons')
    for desc, original in zip(comparisons, q['current_complete_selected_ecology_judgments_actually_read']):
        require({k: desc[k] for k in original} == original and zero(desc['new_credit']), 'AxolotlRecovery original whole comparison and Main addendum retained0')
        b = snap.read(local_path(desc['source']['path'], ROOT))
        matches = [x for x in json.loads(b)['records'] if x['id'] == desc['id']]
        require(sha(b) == desc['source']['sha256'] and len(b) == desc['source']['bytes'] and len(matches) == 1 and sha(canonical(matches[0])) == desc['canonical_record_sha256'] and {k: matches[0][k] for k in desc['actual_complete_selected_judgment_fields_read']} == desc['actual_complete_selected_judgment_fields_read'], 'AxolotlRecovery complete stored ecology owner context')
        if desc['id'] == 'EA-0050':
            milk = matches[0]['frozen_mechanism_context']['Main_review']
            require(len(milk['independent_findings']) == 22 and len(milk['mandatory_limits']) == 11 and desc['actual_complete_selected_judgment_fields_read']['observation'] == milk['independent_findings'] and all(x in desc['actual_complete_selected_judgment_fields_read']['limits'] for x in milk['mandatory_limits']), 'AxolotlRecovery complete milk Main22/11 reused0')
    w = r['complete_Witch_comparison']
    require(w == m['complete_Witch_saved_comparison'] == q['complete_existing_Witch_original_and_distinct_Main_judgments_actually_read'] == a['complete_Witch_saved_comparison_preserved'] == p['entire_Witch_saved_comparison'] and zero(w['new_credit']), 'AxolotlRecovery full Witch comparison reused0')
    for desc in (w['source'], w['Main_whole_review']):
        b = snap.read(local_path(desc['path'], ROOT))
        require(sha(b) == desc['sha256'] and len(b) == desc['bytes'], 'AxolotlRecovery full Witch binding')
    original_witch = snap.json(local_path(w['source']['path'], ROOT))
    main_witch = snap.json(local_path(w['Main_whole_review']['path'], ROOT))
    require({k: original_witch[k] for k in w['complete_original_four_substantive_fields_actually_read']} == w['complete_original_four_substantive_fields_actually_read'] and len(original_witch['observations']) == 16 and len(original_witch['limitations']) == 9 and main_witch['independent_findings'] == w['complete_Main17_findings_actually_read'] and len(main_witch['independent_findings']) == 17 and main_witch['mandatory_limits'] == w['complete_Main10_limits_actually_read'] and len(main_witch['mandatory_limits']) == 10, 'AxolotlRecovery original16/9 and independent Witch17/10')
    strong = r['complete_TConstruct_comparison']
    require(strong == q['complete_existing_TConstruct_curative_owner_reused0'] == m['complete_TConstruct_saved_comparison'] == a['complete_TConstruct_saved_comparison_preserved'] == p['entire_TConstruct_saved_comparison'] and zero(strong['credit_from_comparator']) and [x for x in main_witch['ten_complete_old_judgments_read_and101_Main_own_judgment_reused0'] if x['id'] == strong['id']] == [strong], 'AxolotlRecovery complete already-owned TConstruct whole0')
    require(r['TConstruct_binding'] == q['existing_TConstruct_comparison_binding'] == w['Main_whole_review'] and len(strong['complete_substantive_judgment']) == 4 and strong['full_object_canonical_sha256'] == '247163f29788f2539a842962fae7cb8a3f859ba31fd07694126441128ddcd3c3', 'AxolotlRecovery exact full curative/equipment owner binding')
    owners = r['migration_owner']
    require(owners == q['current_complete_global_judgments_actually_read'] == m['complete_global_saved_comparisons'] == a['complete_global_saved_comparisons_preserved'] == p['entire_global_saved_comparisons'] and len(owners) == 2, 'AxolotlRecovery complete two global owners reused0')
    lb = q['current_migration_ledger_binding']
    b = snap.read(local_path(lb['path'], ROOT))
    require(sha(b) == lb['sha256'] and len(b) == lb['bytes'], 'AxolotlRecovery exact migration ledger bytes')
    rows = [json.loads(line) for line in b.decode().splitlines() if line.strip()]
    for owner in owners:
        matches = [x for x in rows if x.get('candidate_id') == owner['candidate_id']]
        require(len(matches) == 1 and sha(canonical(matches[0])) == owner['canonical_complete_row_sha256'] and {k: matches[0][k] for k in owner['actual_complete_non_evidence_decision_fields']} == owner['actual_complete_non_evidence_decision_fields'], 'AxolotlRecovery whole global saved judgment')
    require(len(q['actual_read_checkpoints']) == 2, 'AxolotlRecovery two actual original checkpoints')
    originals = []
    for desc in q['actual_read_checkpoints']:
        b = snap.read(local_path(desc['path'], ROOT))
        require(sha(b) == desc['sha256'] and len(b) == desc['bytes'], 'AxolotlRecovery exact original actual reading checkpoint')
        originals.append(json.loads(b))
    require(originals[0]['observed_so_far'] == q['original17_checkpoint_observations_preserved'] and originals[1]['additional_observations'] == q['original15_supplement_observations_preserved'], 'AxolotlRecovery original17 and15 actual checkpoint claims retained')
    refs = n['all_actual_ref_descriptors']
    require(len(refs) == len(r['chain']) == spec['exact_ranges'] == 38 and refs == p['exact_read_descriptor_order'] and refs[:37] == q['actual_native_read_ranges'] == m['actual_Main_saved_ranges_read'], 'AxolotlRecovery original37 and explicit additive parent151')
    extra = m['extra_Main_complete_parent_hurt_read']
    source_fields = ('entry', 'entry_sha256', 'lines', 'raw_excerpt_sha256', 'raw_excerpt_utf8')
    require(a['additional_parent_hurt_actually_read_now']['raw_descriptor'] == extra and {k: refs[37][k] for k in source_fields} == {k: extra[k] for k in source_fields} and zero(extra.get('credit')) and zero(refs[37].get('range_or_helper_credit')) and extra['entry'] == 'net/minecraft/world/entity/LivingEntity.java' and extra['lines'] == [1057, 1207], 'AxolotlRecovery actual Main and author five parent hurt fields and separate strict zero credits')
    ar = snap.read(local_path(spec['artifact']['path'], ROOT / 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(ar) == spec['artifact']['sha256'], 'AxolotlRecovery fixed native source archive')
    line_set = set()
    with zipfile.ZipFile(io.BytesIO(ar)) as z:
        for ref, e in zip(refs, r['chain']):
            b = z.read(ref['entry'])
            lo, hi = ref['lines']
            require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(b.splitlines()), 'AxolotlRecovery strict descriptor range')
            part = b''.join(b.splitlines(keepends=True)[lo-1:hi])
            require(ref['archive'] == spec['artifact']['path'] and ref['archive_sha256'] == spec['artifact']['sha256'] and ref['coordinate'] == spec['coordinate'] and sha(b) == ref['entry_sha256'] and part.decode() == ref['raw_excerpt_utf8'] and sha(part) == ref['raw_excerpt_sha256'] == e['raw_excerpt_sha256'] and type(ref['full_file']) is bool and ref['full_file'] == ((lo, hi) == (1, len(b.splitlines()))) and ref['entry'] == e['path'] and [lo, hi] == [e['line'], e['end_line']] and e['whole_file_read'] == ref['full_file'], 'AxolotlRecovery exact typed source descriptor/full flag')
            line_set.update((ref['entry'], i) for i in range(lo, hi+1))
    require(len({ref['entry'] for ref in refs}) == 22 and sum(ref['full_file'] for ref in refs) == 14 and sum(ref['lines'][1]-ref['lines'][0]+1 for ref in refs) == 2437 and len(line_set) == 2402 and n['source_range_file_inventory_credit'] == 0, 'AxolotlRecovery bookkeeping38/22/14/2437/2402 provides0 credit')
    for key in ('global_novelty_credit', 'new_migration_credit', 'supporting_ranges_credit', 'native_gameplay_credit', 'runtime_material_payment_credit', 'native_birth_kill_pickup_credit', 'generic_immunity_credit', 'generic_cure_credit', 'player_support_context_credit'):
        require(zero(d.get(key)), 'AxolotlRecovery no unsupported credit ' + key)
    decision = d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and zero(d.get('accepted_credit')), 'AxolotlRecovery explicit nonacceptance0')
        return dict(state='non_accepting', role='general', id=spec['id'], decision=decision, receipt=str(path.relative_to(ROOT)), receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit'] == 1, 'AxolotlRecovery exactly1 related whole, no immunity or player-support subdivision')
    checks = d.get('source_checks')
    require(isinstance(checks, list) and len(checks) == 38, 'AxolotlRecovery exact38 actual typed checks')
    verified = []
    for check, e in zip(checks, r['chain']):
        require(check.get('evidence') == e and all(check.get(k) is True for k in ('archive_sha256_match', 'entry_bytes_match', 'fixed_coordinate_match', 'excerpt_exact')), 'AxolotlRecovery actual typed source-check flags')
        verified.append(validate_axolotl_recovery_native_source(e, snap))
    require(d.get('resource_checks') == [], 'AxolotlRecovery no invented resource or runtime membership')
    return dict(state='validated_acceptance', id=spec['id'], role='general', reviewer=d['reviewer'], decision=decision, semantic_key=r['semantic_key'], accepted_credit=1, receipt=str(path.relative_to(ROOT)), receipt_sha256=sha(raw), batch=str(bp.relative_to(ROOT)), batch_sha256=sha(snap.read(bp)), source_checks_recomputed=verified, base_resource_checks_recomputed=[], supporting_ranges_credit=0, limitations=r['limits'], observed_chain=r['observation'], complete_chain_support_proof=dict(bindings=spec['bindings'], scope=r['evidence_scope'], independent_semantic_acceptance_thread=r['independent_reviewer_thread_id'], General_perspective='actual original source author, not self-independent', existing_global_capture_and_Brain_owners_credit=0, TConstruct_curative_owner_credit=0, generic_immunity_credit=0, generic_cure_credit=0, player_support_context_credit=0, native_gameplay_credit=0, runtime_material_payment_credit=0, global_novelty_credit=0, new_migration_credit=0))


GRAVESOIL_V35_SPEC = {'id': 'EA-0052', 'parameters': {'id': 'EA-0052', 'batch_path': 'docs/cod4/audit-20261022/ecology-availability-research/batch-043.json', 'schema_version': 'v35', 'batch_general_context_schema': 'gravesoil-source-v35', 'receipt_path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-reviews/general-EA0052.json'}, 'batch_path': 'docs/cod4/audit-20261022/ecology-availability-research/batch-043.json', 'receipt_path': 'docs/cod4/audit-20261022/ecology-availability-research/independent-reviews/general-EA0052.json', 'canonical_record_sha256': '822dddc44251e0f4b7da361751b44014830406e742c591367b1d604549d662e4', 'bindings': {'candidate': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-goety-grave-soil-whole-source-policy-candidate-20261110.json', 'sha256': 'f9f26428da99d2758c39e39011fb9a83c927aff7d425dcc76d53815f63c78842', 'bytes': 83188}, 'Main_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-goety-grave-soil-whole-source-review-20261110.json', 'sha256': 'fb9fbc9f7d1ccd960901c857ede8336c7e2b56fcb6ba43fe33c9ae0305d19ee1', 'bytes': 97424}, 'author_ack': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-goety-grave-soil-Main20-10-author-ack-private-version-plan-20261110.json', 'sha256': 'e99916319e63ffed38e978d7ad8223c2594edd8e09f9a71876c4aa96a9ad14f2', 'bytes': 24631}, 'Main_ack_plan_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-goety-gravesoil-author-ack-plan-review-20261110.json', 'sha256': 'b32b144df6c1b3bc31cd542274f32aaf743dfa020551352a785a1d1f0fe3f624', 'bytes': 4956}, 'tree_format_addendum': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-goety-grave-soil-tree-serialization-discrepancy-resolution-20261110.json', 'sha256': '73ed8f833e577c8d6362969cccdc7db4a773684c64a651bb3c8bf7c4479c79c4', 'bytes': 2467}, 'private_proposal': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-goety-grave-soil-private-whole-policy-proposal-20261110.json', 'sha256': 'c5ff9e564d6f1beace1f3297a087fd5cc7f809bfc05083f900b30448ab4fcf11', 'bytes': 300679}, 'Main_private_proposal_review': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-goety-gravesoil-private-proposal-review-20261110.json', 'sha256': '684020331323a306c3b21c8ebcc09196d6dea137cd563732c581e9e0bcffeb26', 'bytes': 4233}, 'minimum_plan': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/general-goety-grave-soil-next-minimum-private-install-delta-plan-20261110.json', 'sha256': 'e552126f98fd3cc17dc760d363e3b9ad168846d01527c6dda60552b42812e72b', 'bytes': 8941}, 'Main_parameter_grant': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-gravesoil-current50-minimum-plan-review-20261110.json', 'sha256': 'ecf46c41d6d0e17402cae4d20df14eea42d923061f27f217cb8dfd1c7ecce9d0', 'bytes': 6283}, 'normalization': {'path': 'docs/cod4/audit-20261022/ecology-availability-research/package-normalization-gravesoil-source-v35.json', 'sha256': '75143a96b17eff3f68176b4d2f79e94d257eb93fb6bb9e07c4557abaec949758', 'bytes': 1820044}}, 'pin': '02adbe7491767210f63857fa763a6f1de1262cbd', 'artifact': {'path': 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar', 'sha256': '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'}, 'coordinate': 'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources', 'author': '01a12516-2eaf-73e2-b615-20f8b422158c', 'Main': '01a16364-cac0-7ca2-a042-a5312781ca34', 'native_source_hashes': ['b02fe74750be7ad72705f5bb96ee45047d5e4d0db0a21b7615e70fe9d2c3ceba', '4881eb3162a582be4fb36c7f3c4d2ac165babca60b6de0ee58efa0fc3b961b71', 'a6ed056897698c91ba5e968f82be63bda16ad3956d8df3b03c1b81c45e658b31', 'e2fdc5f28934a91c5d0f6440648c5c629a70da3507b4b5cf4af4e04facbe3ba0', '1ffe2bbcac5c8fc663ce463ea1bb6edc43348d681564e087fa83e6ffe1c4cc37', '765632db33edcc8e6f25849a06edccaaab7f90bf5a8ad75c3a94ee6ece0cb74a', 'ae2566171fa87a0e1e896585ecc781664121d49e53eac067ada6a7c75491eda4', '47f25094779f9ec2682946a2546cdefbf1c5179a3c4adc8558ac1c43262dd7db', '58810c37db144355cbab7a1460f7515a1a93dc315602856d018c8d27a849f028', 'd655d2451c5598d1916942211fc28422a1cb08e4ea39bc6d2973700cb303663d', 'e8574420ddafe4819eeaa6e4161009c3b77b4fa7639e3edc0fc49666e732c3a2', '60556138f92b94937491c66e97fb751127ffd80721e46ad50aafa28248e2b98c'], 'receipt_label': 'general existing-chat original-source-author confirmation after distinct Main independent complete grave-substrate source review', 'future_Main_execution_grant': 'docs/cod4/audit-20261022/ecology-availability-research/coordinator-gravesoil-v35-real-author-execution-grant-20261110.json'}

def validate_gravesoil_native_source(e, snap):
    spec = GRAVESOIL_V35_SPEC
    canonical = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    require(sha(canonical(e)) in spec['native_source_hashes'], 'GraveSoil exact native context range')
    require(e.get('source_kind') == 'artifact_native' and not any(k in e for k in ('repo', 'revision', 'git_blob_sha1', 'source_metadata', 'tree_metadata')), 'GraveSoil context cannot impersonate Git source')
    artifact = spec['artifact']
    require(e['source_artifact'] == artifact and e['source_coordinate'] == spec['coordinate'], 'GraveSoil native coordinate')
    archive = snap.read(local_path(artifact['path'], ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches'))
    require(sha(archive) == artifact['sha256'], 'GraveSoil native archive bytes')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        raw = z.read(e['path'])
    copied = snap.read(local_path(e['source_local'], TOOLS/'sources/native-artifact-forge-1.20.1-47.4.10'))
    require(copied == raw and sha(raw) == e['source_sha256'], 'GraveSoil native entry copy')
    lo, hi = e['line'], e['end_line']
    require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(raw.splitlines()), 'GraveSoil native range bounds')
    raw_excerpt = b''.join(raw.splitlines(keepends=True)[lo-1:hi])
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    require(e['excerpt'] == excerpt and e['excerpt_sha256'] == sha(excerpt.encode()) and e['raw_excerpt_sha256'] == sha(raw_excerpt), 'GraveSoil native exact range including LF')
    return {k: e[k] for k in ('source_kind', 'source_coordinate', 'source_artifact', 'path', 'source_local', 'source_sha256', 'line', 'end_line', 'excerpt_sha256', 'raw_excerpt_sha256')}


def validate_gravesoil_receipt(path, raw, batches_by_id, snap):
    """Exact reviewed research context; local authorization is not cryptographic identity.

    No grants/markers are written or consumed here. Real author execution still
    requires Main's separate exact-byte review, install and fresh execution grant.
    Synthetic fixture acceptance cannot publish (Snapshot.stable rejects overrides).
    """
    spec = GRAVESOIL_V35_SPEC
    canonical = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    zero = lambda v: type(v) is int and v == 0
    path = Path(path)
    d = json.loads(raw)
    require(path.resolve() == (ROOT/spec['receipt_path']).resolve(), 'GraveSoil exact author receipt namespace')
    require(d.get('id') == spec['id'] and d.get('reviewer') == spec['receipt_label'] and d.get('reviewer_thread_id') == spec['author'], 'GraveSoil actual original author identity')
    require(spec['id'] in AUTHORIZED['general']['allowed_ids'] and spec['id'] in batches_by_id, 'GraveSoil authorized reserved ID')
    bp, r = batches_by_id[spec['id']]
    require(bp.resolve() == (ROOT/spec['batch_path']).resolve() and sha(canonical(r)) == spec['canonical_record_sha256'] and snap.json(bp)['records'] == [r], 'GraveSoil exact complete single record')
    require(d.get('reviewed_batch') == spec['batch_path'] and d.get('reviewed_batch_sha256') == sha(snap.read(bp)), 'GraveSoil actual batch bytes')
    for key, value in r.items():
        if key != 'accepted_credit':
            require(canonical(d.get(key)) == canonical(value), 'GraveSoil entire record context ' + key)
    require(r['general_context_schema'] == 'gravesoil-source-v35' and r['author_thread_id'] == spec['author'] and r['independent_reviewer_thread_id'] == spec['Main'] and spec['author'] != spec['Main'], 'GraveSoil distinct source author and Main')
    require(type(r['proposed_credit']) is int and r['proposed_credit'] == 1 and zero(r['accepted_credit']) and r['upstream_code_executed'] is False, 'GraveSoil one pending whole')
    f = r['frozen_mechanism_context']
    require(set(f) == set(spec['bindings']) and r['immutable_bindings'] == spec['bindings'], 'GraveSoil immutable binding set')
    for key, desc in spec['bindings'].items():
        b = snap.read(local_path(desc['path'], ROOT))
        require(sha(b) == desc['sha256'] and len(b) == desc['bytes'] and json.loads(b) == f[key], 'GraveSoil complete immutable context ' + key)
    q, m, a, p, n, grant = (f[k] for k in ('candidate', 'Main_review', 'author_ack', 'private_proposal', 'normalization', 'Main_parameter_grant'))
    require(q['owner_thread_id'] == a['author_thread_id'] == p['owner_thread_id'] == spec['author'] and m['reviewer_thread_id'] == grant['reviewer_thread_id'] == spec['Main'], 'GraveSoil actual context role boundaries')
    require(grant['decision'] == 'PLAN_CONTRACT_ACCEPTED_DRAFT_ONLY_PARAMETERS_GRANTED_SEPARATE_EXACT_BYTES_REVIEW_REQUIRED' and grant['draft_only_parameters'] == spec['parameters'] == n['Main_granted_draft_parameters'], 'GraveSoil draft grant does not authorize actual receipt')
    require(q['observed_chain'] == p['complete_original24'] == m['all_original24_observations_preserved'] == r['original_author_observations'] and len(q['observed_chain']) == 24, 'GraveSoil full original24')
    require(q['mandatory_constraints'] == p['complete_original8'] == m['all_original8_constraints_preserved'] == r['mandatory_constraints'] and len(q['mandatory_constraints']) == 8, 'GraveSoil full original8')
    require(q['limits'] == p['complete_original6'] == m['all_original6_limits_preserved'] and len(q['limits']) == 6 and q['application'] == p['complete_original_application'] == r['application'], 'GraveSoil original6 and application')
    require(m['Main_findings'] == p['complete_Main20'] == r['observation'] == d.get('observed_chain') and len(m['Main_findings']) == 20 and m['Main_limits'] == p['complete_Main10'] and len(m['Main_limits']) == 10 and r['limits'] == q['limits'] + m['Main_limits'], 'GraveSoil full Main20/10')
    require(a['acknowledgments'] + a['acknowledged_limits'] == p['complete_author_ack30'] and len(a['acknowledgments']) == 20 and len(a['acknowledged_limits']) == 10, 'GraveSoil actual30 author acknowledgments')
    for acknowledgments, originals in ((a['acknowledgments'], m['Main_findings']), (a['acknowledged_limits'], m['Main_limits'])):
        for i, (ack, original) in enumerate(zip(acknowledgments, originals), 1):
            require(ack['index'] == i and ack['verbatim'] == original and ack['author_acknowledged'] is True, 'GraveSoil unchanged itemized author acknowledgment')
    require(p['complete_seven_old_EA_whole_owners'] == m['complete_seven_old_ecology_fields'] == r['complete_ecology_owners'] and len(r['complete_ecology_owners']) == 7, 'GraveSoil full seven ecology owners including EA36')
    for owner in r['complete_ecology_owners']:
        desc = owner['source']; b = snap.read(local_path(desc['path'], DOCS))
        matches = [x for x in json.loads(b)['records'] if x['id'] == owner['id']]
        require(sha(b) == desc['sha256'] and len(b) == desc['bytes'] and len(matches) == 1 and {k: matches[0][k] for k in owner['complete_fields']} == owner['complete_fields'], 'GraveSoil unchanged complete old ecology decision')
    require(p['complete_two_Global_whole_owners'] == m['complete_two_Global_substantive_judgments'] == r['complete_Global_owners'] and len(r['complete_Global_owners']) == 2, 'GraveSoil full two Global owners')
    lb = q['global_ledger']; b = snap.read(local_path(lb['path'], ROOT))
    require(sha(b) == lb['sha256'] and len(b) == lb['bytes'], 'GraveSoil original Global ledger bytes')
    row_hashes = {sha(canonical(json.loads(line))) for line in b.decode().splitlines() if line.strip()}
    require(all(o['whole_row_canonical_sha256'] in row_hashes for o in r['complete_Global_owners']), 'GraveSoil whole Global rows')
    baseline = n['historical_current50_master']
    require(baseline == p['formal_baseline']['master'] and len(n['all_current50_complete_master_rows']) == 50 and sha(canonical(n['all_current50_complete_master_rows'])) == p['formal_baseline']['all50_complete_rows_canonical_sha256'], 'GraveSoil complete historical50 rows, not ongoing master authority')
    require(n['complete_EA51_current_version_binding'] == p['accepted_EA51_current_version_complete_binding'] and n['complete_EA51_current_version_binding']['context_schema'] == 'axolotl-recovery-v34', 'GraveSoil complete accepted EA51v34 binding')
    for desc in n['all_old50_proposal_record_bindings']:
        b = snap.read(local_path(desc['batch'], DOCS)); matches = [x for x in json.loads(b)['records'] if x['id'] == desc['id']]
        require(sha(b) == desc['batch_sha256'] and len(matches) == 1 and sha(canonical(matches[0])) == desc['canonical_record_sha256'] and matches[0]['semantic_key'] == desc['semantic_key'], 'GraveSoil unchanged complete old50 proposal records')
    require(len(n['all_old50_proposal_record_bindings']) == 50 and {x['id'] for x in n['all_old50_proposal_record_bindings']} == {x['id'] for x in n['all_current50_complete_master_rows']}, 'GraveSoil old50 ID inventory complete')
    require(len(r['chain']) == 25 and r['chain'] == n['normalized_chain'], 'GraveSoil exact13mod12native chain')
    raw_meta = snap.read(local_path(n['source_format']['original_source_metadata']['path'], ROOT))
    raw_tree = snap.read(local_path(n['source_format']['original_tree_metadata']['path'], ROOT))
    require(sha(raw_meta) == n['source_format']['original_source_metadata']['sha256'] and sha(raw_tree) == n['source_format']['original_tree_metadata']['sha256'], 'GraveSoil preserve original metadata bytes')
    require(snap.read(local_path(n['source_format']['private_source_metadata']['path'], TOOLS/'sources')) == raw_meta and snap.read(local_path(n['source_format']['private_tree_metadata']['path'], TOOLS/'sources')) == raw_tree, 'GraveSoil metadata copies preserve historical discrepancy')
    tree = json.loads(raw_tree); meta = json.loads(raw_meta)
    reconstructed = json.dumps(tree, ensure_ascii=False).encode()
    require(tree['sha'] == spec['pin'] and tree['truncated'] is False and sha(raw_tree) == 'b71104b3316c531a5b580caac8bdb486098152b5dda5f2394478f2a17e730b7d' and len(reconstructed) == 5376875 and sha(reconstructed) == meta['tree_sha256'] == '761a683b619da26322604506f515758f34fd6c3357be9fe66ce7869028c3a197', 'GraveSoil same parsed tree exact default JSON explanation only')
    checks = d.get('source_checks')
    require(isinstance(checks, list) and len(checks) == 25, 'GraveSoil complete actual source checks')
    verified = []
    for i, (e, check, mapping) in enumerate(zip(r['chain'], checks, n['source_mapping'])):
        require(check.get('evidence') == e and all(check.get(k) is True for k in ('source_bytes_match', 'fixed_source_identity_match', 'excerpt_exact')), 'GraveSoil actual typed check flags')
        require(e['source_local'] == mapping['private_path'] and e['raw_excerpt_sha256'] == mapping['original_range_sha256'], 'GraveSoil exact original-to-private mapping')
        if i < 13:
            original = snap.read(local_path(mapping['original_path'], ROOT))
            copied = snap.read(local_path(e['source_local'], TOOLS/'sources'))
            require(original == copied and sha(copied) == e['source_sha256'], 'GraveSoil original source authority retained')
            require(sha(b''.join(copied.splitlines(keepends=True)[e['line']-1:e['end_line']])) == e['raw_excerpt_sha256'], 'GraveSoil mod terminal LF retained')
            verified.append(validate_source(e, snap))
        else:
            verified.append(validate_gravesoil_native_source(e, snap))
    for key in ('global_novelty_credit', 'new_migration_credit', 'supporting_ranges_credit', 'native_gameplay_credit', 'runtime_material_payment_credit', 'native_birth_kill_pickup_credit', 'building_credit', 'art_credit'):
        require(zero(d.get(key)), 'GraveSoil unsupported credit ' + key)
    require(d.get('resource_checks') == [], 'GraveSoil no invented loot/source generation or collector checks')
    decision = d.get('decision')
    if decision not in AUTHORIZED['general']['decisions']:
        require(decision not in ALL_ACCEPT_DECISIONS and zero(d.get('accepted_credit')), 'GraveSoil explicit nonacceptance0')
        return dict(state='non_accepting', role='general', id=spec['id'], decision=decision, receipt=str(path.relative_to(ROOT)), receipt_sha256=sha(raw))
    require(type(d.get('accepted_credit')) is int and d['accepted_credit'] == 1, 'GraveSoil one whole only')
    # Required future Main grant is intentionally absent from this draft package.
    confirmation = d.get('actual_author_confirmation')
    require(isinstance(confirmation, dict) and confirmation.get('author_thread_id') == spec['author'], 'GraveSoil real author confirmation required')
    desc = confirmation.get('Main_execution_grant')
    require(isinstance(desc, dict) and desc.get('path') == spec['future_Main_execution_grant'], 'GraveSoil separate exact Main grant namespace')
    auth_bytes = snap.read(local_path(desc['path'], DOCS))
    require(sha(auth_bytes) == desc.get('sha256'), 'GraveSoil fresh execution grant bytes')
    auth = json.loads(auth_bytes)
    require(auth.get('reviewer_thread_id') == spec['Main'] and auth.get('real_author_receipt_authorized') is True and auth.get('parameters') == spec['parameters'] and auth.get('canonical_record_sha256') == spec['canonical_record_sha256'], 'GraveSoil Main actual author scope, not draft/fixture permission')
    token = auth.get('fresh_execution_id')
    require(isinstance(token, str) and re.fullmatch(r'gravesoil-v35-[a-f0-9]{32,64}', token) is not None and confirmation.get('fresh_execution_id') == token, 'GraveSoil cannot replay other-policy marker')
    require(auth.get('synthetic_or_fixture') is False and auth.get('old_proofs_reused') is False, 'GraveSoil real grant not synthetic proof')
    expected_tools = {'tools/cod4/ecology-availability-research/' + name for name in ('evidence.py', 'receipt_validation.py', 'audit_receipt_validation.py', 'summarize.py')}
    require(isinstance(auth.get('installed_tool_sha256'), dict) and set(auth['installed_tool_sha256']) == expected_tools, 'GraveSoil exact separately installed tool set')
    for name, digest in auth['installed_tool_sha256'].items():
        require(sha(snap.read(local_path(name, TOOLS))) == digest, 'GraveSoil installed version differs from independent execution grant')
    return dict(state='validated_acceptance', id=spec['id'], role='general', reviewer=d['reviewer'], decision=decision, semantic_key=r['semantic_key'], accepted_credit=1, receipt=str(path.relative_to(ROOT)), receipt_sha256=sha(raw), batch=str(bp.relative_to(ROOT)), batch_sha256=sha(snap.read(bp)), source_checks_recomputed=verified, base_resource_checks_recomputed=[], supporting_ranges_credit=0, limitations=r['limits'], observed_chain=r['observation'], complete_chain_support_proof=dict(bindings=spec['bindings'], scope=r['evidence_scope'], independent_semantic_acceptance_thread=spec['Main'], actual_original_author_thread=spec['author'], native_gameplay_credit=0, runtime_material_payment_credit=0, global_novelty_credit=0, new_migration_credit=0, authorization_identity_boundary='User-authorized local namespace and independently reviewed actual workflow, not cryptographic identity or fixture proof.'))


def validate_receipt(path, raw, batches_by_id, snap):
    if Path(path).name == 'general-EA0054.json':
        from sunbird_v37 import validate_receipt as validate_sunbird_v37
        try:
            return validate_sunbird_v37(path, raw, batches_by_id, snap, ROOT)
        except ValueError as error:
            raise InvalidReceipt(str(error)) from error
    if Path(path).name == 'general-EA0053.json':
        from maned_wolf_v36 import validate_receipt as validate_maned_wolf_v36
        try:
            return validate_maned_wolf_v36(path, raw, batches_by_id, snap, ROOT)
        except ValueError as error:
            raise InvalidReceipt(str(error)) from error
    if Path(path).name == 'general-EA0052.json':
        return validate_gravesoil_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0051.json':
        return validate_axolotl_recovery_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0050.json':
        return validate_milk_container_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0049.json':
        return validate_fishing_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0048.json':
        return validate_charged_trophy_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0047.json':
        return validate_zombie_reinforcement_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0046.json':
        return validate_evoker_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0045.json':
        return validate_peer_sharing_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0044.json':
        return validate_snow_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0043.json':
        return validate_cat_rest_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0042.json':
        return validate_farmer_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0041.json':
        return validate_shulker_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0040.json':
        return validate_hero_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0039.json':
        return validate_natural_budget_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0038.json':
        return validate_golem_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0037.json':
        return validate_gorilla_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0036.json':
        return validate_silverfish_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0035.json':
        return validate_enderpearl_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0034.json':
        return validate_patrol_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0033.json':
        return validate_phantom_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0032.json':
        return validate_siege_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0031.json':
        return validate_cat_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0030.json':
        return validate_allay_receipt(path, raw, batches_by_id, snap)
    if Path(path).name == 'general-EA0029.json':
        return validate_tasmanian_receipt(path, raw, batches_by_id, snap)
    closed_match = NAME.fullmatch(Path(path).name)
    if closed_match is not None and 'EA-'+closed_match.group(2) in CLOSED_SERVICE_SPECS:
        return validate_closed_service_receipt(path, raw, batches_by_id, snap)
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
    if role=='general':
        require(identifier in policy['allowed_ids'],'general reviewer scope not authorized for this id')
        require(d.get('reviewer_thread_id')==policy['thread_id'],'general reviewer thread mismatch')
    require(identifier in batches_by_id,'unknown/candidate identifier')
    batch_path,r=batches_by_id[identifier]
    require(r.get('status')=='reviewed_proposed' and r.get('proposed_credit')==1,'record not an eligible reviewed proposal')
    require(d.get('semantic_key')==r['semantic_key'],'semantic key mismatch')
    batch_raw=snap.read(batch_path)
    expected_sha=d.get('reviewed_batch_sha256')
    require(isinstance(expected_sha,str) and HEX64.fullmatch(expected_sha) is not None and sha(batch_raw)==expected_sha,'reviewed batch SHA mismatch')
    # Carson names the path reviewed_batch; coordinator originally binds by SHA only.
    require(role not in ('carson','general') or 'reviewed_batch' in d,'strong reviewer schema missing reviewed_batch path')
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
    complete_proof=(general_actor_service_context(d,r,snap,policy,identifier,role) if identifier in ('EA-0023','EA-0024') else ((general_hummingbird_context(d,r,snap,policy,identifier,role) if identifier=='EA-0022' else ((general_raccoon_context(d,r,snap,policy,identifier,role) if identifier=='EA-0021' else ((coordinator_tusklin_context(d,r,snap,policy,identifier,role) if identifier=='EA-0020' else ((general_ferrouslime_context(d,r,snap,policy,identifier) if identifier=='EA-0019' else general_terrapin_context(d,r,snap,policy,identifier) if identifier=='EA-0018' else general_skreecher_context(d,r,snap,policy,identifier) if identifier=='EA-0016' else general_context(d,r,snap,policy,identifier)) if role=='general' else None))))))))
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
            if role!='coordinator' or k in c: require(c.get(k)==e[k],'receipt source value mismatch: '+k)
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
    if complete_proof: result['complete_chain_support_proof']=complete_proof
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
    return accepted,{'schema':'ecology-independent-receipt-validation-v4',
        'authorized_reviewers':{k:{'exact_labels':sorted(v['labels']),'accept_decisions':sorted(v['decisions'])} for k,v in AUTHORIZED.items()},
        'general_reviewer_scope':{'thread_id':AUTHORIZED['general']['thread_id'],
                                  'allowed_ids':sorted(AUTHORIZED['general']['allowed_ids']),
                                  'proposal_author_thread_id':AUTHORIZED['general']['proposal_author_thread_id']},
        'identity_boundary':'local user-authorized role/filename/exact label; not cryptographic identity authentication',
        'receipt_inputs':rows,'conflicts':conflicts,
        'counts':{'inspected_receipts':len(rows),'validated_acceptance_receipts':sum(x['state']=='validated_acceptance' for x in rows),
                  'invalid_or_nonaccepting':sum(x['state']!='validated_acceptance' for x in rows),
                  'unique_accepted_ids':len(accepted)},
        'upstream_execution':False,'production_or_runtime_credit':0},snap
