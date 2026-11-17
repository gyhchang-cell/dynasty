"""Stage corrected single-cohort evidence and strict EA19-only review protocol."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'tools/cod4/ecology-availability-research'
DOCS = ROOT / 'docs/cod4/audit-20261022/ecology-availability-research'
STAGE = TOOLS / '.work/ferrouslime-v6-draft'
sha = lambda data: hashlib.sha256(data).hexdigest()


def main():
    assert not STAGE.exists(), 'Immutable stage already exists; do not rerun.'
    bindings = {
        'complete_chain_proposal': {'path':str((DOCS/'coordinator-ferrouslime-cohort-transfer-proposal-20261103.json').relative_to(ROOT)), 'sha256':'c422b5a6ffa94d6c9da58cc1b79bffb1797e0dc9449dc3e42363e938c20f58bb'},
        'complete_chain_review': {'path':str((DOCS/'independent-ferrouslime-cohort-transfer-review-20261103.json').relative_to(ROOT)), 'sha256':'7802f8ddd2878763342397afbd66d6ce532c9bdfed01ab085d25f9054525c751'},
        'complete_chain_corrections': {'path':str((DOCS/'coordinator-ferrouslime-peer-corrections-20261103.json').relative_to(ROOT)), 'sha256':'b04e3313b8c605088490912c7efe2fedb58c51d98299e2ede3da3b371d7e5199'},
    }
    documents = {}
    for field, descriptor in bindings.items():
        raw = (ROOT/descriptor['path']).read_bytes()
        assert sha(raw) == descriptor['sha256']
        documents[field] = json.loads(raw)
    p, peer, corrections = [documents[k] for k in bindings]
    assert corrections['corrected_observations'] == peer['observed_chain']
    assert corrections['mandatory_corrections'] == peer['proposal_corrections_and_conditions']
    base = TOOLS/'sources/AlexModGuy__AlexsCaves'
    original_refs = list(p['source_refs'])
    h = corrections['additional_mod_header_binding']
    header = {**original_refs[2], 'path':h['source_local'], 'source_path':h['source_path'], 'lines':h['lines'],
              'excerpt_sha256':h['raw_excerpt_sha256'], 'role':h['role']}
    header['url'] = f'https://github.com/AlexModGuy/AlexsCaves/blob/{h["revision"]}/{h["source_path"]}#L1-L20'
    refs = original_refs+[header]
    chain, copies = [], {}
    for index, ref in enumerate(refs):
        raw = (ROOT/ref['path']).read_bytes()
        assert sha(raw) == ref['file_sha256']
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert blob == ref['git_blob_sha1']
        metadata, tree_path = base/'source.json', base/'tree.json'
        for destination, original_field, digest_field in [
                (metadata,'source_metadata','source_metadata_sha256'),
                (tree_path,'tree_metadata','tree_metadata_sha256')]:
            original_raw=(ROOT/ref[original_field]).read_bytes()
            assert sha(original_raw)==ref[digest_field]
            if destination.exists():assert destination.read_bytes()==original_raw
            else:copies[str(destination.relative_to(ROOT))]={'original':ref[original_field],'sha256':sha(original_raw)}
        tree = json.loads((ROOT/ref['tree_metadata']).read_bytes())
        assert tree['sha'] == ref['revision'] and tree['truncated'] is False
        assert next(x['sha'] for x in tree['tree'] if x['path']==ref['source_path']) == blob
        target = base/ref['source_path']
        if target.exists():assert target.read_bytes() == raw
        else:copies[str(target.relative_to(ROOT))]={'original':ref['path'],'sha256':sha(raw)}
        lo, hi = ref['lines']
        excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
        chain.append({'repo':'AlexModGuy/AlexsCaves','revision':ref['revision'],'path':ref['source_path'],
                      'source_local':str(target.relative_to(ROOT)),'source_sha256':sha(raw),'git_blob_sha1':blob,
                      'source_metadata':str(metadata.relative_to(ROOT)),'tree_metadata':str(tree_path.relative_to(ROOT)),
                      'provenance':'Same fixed cached Git tree and original source bytes; no new acquisition credit.',
                      'line':lo,'end_line':hi,'excerpt':excerpt,'excerpt_sha256':sha(excerpt.encode()),'url':ref['url'],
                      'evidence_kind':'complete_file' if index==0 else 'supporting_range'})
    assert len(chain) == 7
    record = {**chain[0], 'id':'EA-0019','status':'reviewed_proposed','proposed_credit':1,'accepted_credit':0,
              'supporting_ranges_credit':0,'semantic_key':p['proposed_semantic_key'],'author_thread_id':p['author_thread_id'],
              'general_context_schema':'ferrouslime-cohort-transfer-v1','chain':chain,
              'native_auxiliary_artifact':{'source_archive':peer['provenance']['archive'],'sha256':peer['provenance']['archive_sha256']},
              'native_auxiliary_ranges':corrections['native_raw_binding_checks'],
              'observation':corrections['corrected_observations'],'application':p['proposed_distinction'],
              'limits':corrections['limitations']+[x['mandatory_correction'] for x in peer['proposal_corrections_and_conditions']],
              'deduplication':peer['decision_rationale'],**bindings}
    batch = {'schema':'ecology-reviewed-proposals-v6','status':'PENDING_REAL_GENERAL_RECEIPT_ZERO_CREDIT',
             'records':[record],'candidate_identifier_invented':False,
             'publication_scope':'One next actual cohort implementation identifier after actual accepted EA18; staged only.'}
    code = (TOOLS/'receipt_validation.py').read_text()
    assert sha(code.encode()) == '9f74dfe036e40d22ae22096ba93afa93a076985fb3d55d3ee17838460e8822e5'
    old_scope = "'allowed_ids': {'EA-0016', 'EA-0017', 'EA-0018'},"
    assert code.count(old_scope) == 1
    code = code.replace(old_scope, "'allowed_ids': {'EA-0016', 'EA-0017', 'EA-0018', 'EA-0019'},")
    old_route = "general_terrapin_context(d,r,snap,policy,identifier) if identifier=='EA-0018'"
    assert code.count(old_route) == 1
    code = code.replace(old_route,"general_ferrouslime_context(d,r,snap,policy,identifier) if identifier=='EA-0019' else "+old_route)
    context = '''
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
            identities.add((entry,lo,hi));excerpt=''.join(lines[lo-1:hi]).encode();normalized=('\\n'.join(raw.decode().splitlines()[lo-1:hi])+'\\n').encode()
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

'''
    assert code.count('def validate_receipt(')==1
    code=code.replace('def validate_receipt(', 'GENERAL_EA19_BINDINGS = '+repr(bindings)+'\n\n'+context+'def validate_receipt(')
    summary=(TOOLS/'summarize.py').read_text()
    assert sha(summary.encode())=='d3eaccc6ec872ba20a12898b37306de6a7cdf3bcca3856480c85b840c0c2c67b'
    assert summary.count('ecology-master-acceptance-v5')==1
    summary=summary.replace('ecology-master-acceptance-v5','ecology-master-acceptance-v6')
    STAGE.mkdir()
    for name,obj in [('batch-014.json',batch),('source-copies.json',copies)]:
        (STAGE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    (STAGE/'receipt_validation.py').write_text(code)
    (STAGE/'summarize.py').write_text(summary)
    manifest={'status':'STAGED_EA19_ONLY_PENDING_INDEPENDENT_DELTA_REVIEW_NO_FORMAL_RECEIPT_OR_CREDIT',
              'baseline_validator_sha256':sha((TOOLS/'receipt_validation.py').read_bytes()),
              'baseline_summary_sha256':sha((TOOLS/'summarize.py').read_bytes()),
              'baseline_ledger_sha256':sha((DOCS/'master-acceptance-ledger.json').read_bytes()),
              'files':{p.name:sha(p.read_bytes()) for p in STAGE.iterdir()},'bindings':bindings,
              'formal_batch_target':str((DOCS/'batch-014.json').relative_to(ROOT)),
              'credit':0,'game_starts':0,'production_changes':0}
    (STAGE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'stage':str(STAGE.relative_to(ROOT)),'manifest_sha256':sha((STAGE/'manifest.json').read_bytes()),
                      'formal_source_copies_pending':len(copies),'accepted_credit':0}))


if __name__=='__main__':
    main()
