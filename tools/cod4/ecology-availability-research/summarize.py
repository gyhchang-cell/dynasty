"""Inspect own research JSON, emit independent source index and exact continuation."""
import json
import hashlib
from pathlib import Path
from collections import Counter
from evidence import ROOT, DOCS, dump, sha, verify_records

def main():
    batches=[json.loads(p.read_text()) for p in sorted(DOCS.glob('batch-*.json'))]
    records=[r for b in batches for r in b['records']]
    candidates=[r for p in sorted(DOCS.glob('candidates-*.json')) for r in json.loads(p.read_text())['records']]
    integrity=verify_records(records+candidates)
    if any(r.get('source_kind') == 'artifact_native' for r in records):
        integrity.pop('all_copied_bytes_match_pinned_git_blobs', None)
        integrity['git_provenance_scope'] = 'Git repository sources only; explicit artifact-native sources use fixed coordinate/archive/entry checks'
        integrity['artifact_native_not_inferred_to_be_git'] = True
    required=['repo','revision','path','source_local','source_sha256','line','end_line','excerpt','observation','application','limits','url']
    for r in records+candidates:
        record_required = ['source_kind','source_coordinate','path','source_local','source_sha256','line','end_line','excerpt','observation','application','limits','url'] if r.get('source_kind') == 'artifact_native' else required
        assert all(k in r and r[k] not in ('',None) for k in record_required)
        assert r['accepted_credit']==0
    assert len({r['id'] for r in records+candidates})==len(records)+len(candidates)
    from receipt_validation import aggregate, require
    batch_paths=sorted(DOCS.glob('batch-*.json'))
    by_id={}
    for batch_path in batch_paths:
        for r in json.loads(batch_path.read_text())['records']:
            require(r['id'] not in by_id, 'duplicate batch record id')
            by_id[r['id']]=(batch_path,r)
    accepted,receipt_validation,receipt_snapshot=aggregate(by_id)
    accepted_count=len(accepted)
    ledger={'schema':'ecology-master-acceptance-v35','target':1000,'independently_accepted':accepted_count,
        'shortfall':1000-accepted_count,'gate_met':accepted_count>=1000,
        'reviewed_mechanisms_including_accepted':len(records),'pending_proposals':len(records)-accepted_count,
        'candidate_zero_credit':len(candidates),'accepted':accepted,
        'policy':'Exact user-authorized reviewer identity/schema; all source and receipt bindings replayed; same id counts once; conflicts held at zero. Original receipts and proposal batches unchanged.',
        'receipt_validation':'receipt-validation.json',
        'review_addenda':[p.name for p in sorted(DOCS.glob('review-addenda-*.json'))],'production_authorized':False}
    sources={}
    for r in records+candidates:
        for e in r['chain']:
            if e.get('source_kind') == 'artifact_native':
                from receipt_validation import validate_closed_native_source, validate_tasmanian_native_source, validate_allay_native_source, validate_cat_native_source, validate_siege_native_source, validate_phantom_native_source, validate_patrol_native_source, validate_enderpearl_native_source, validate_silverfish_native_source, validate_gorilla_native_source, validate_golem_native_source, validate_natural_budget_native_source, validate_hero_native_source, validate_shulker_native_source, validate_farmer_native_source, validate_cat_rest_native_source, validate_snow_native_source, validate_peer_sharing_native_source, validate_evoker_native_source, validate_zombie_reinforcement_native_source, validate_charged_trophy_native_source, validate_fishing_native_source, validate_milk_container_native_source, validate_axolotl_recovery_native_source, validate_gravesoil_native_source
                (validate_gravesoil_native_source(e, receipt_snapshot) if r['id'] == 'EA-0052' else (validate_axolotl_recovery_native_source(e, receipt_snapshot) if r['id'] == 'EA-0051' else (validate_milk_container_native_source(e, receipt_snapshot) if r['id'] == 'EA-0050' else (validate_fishing_native_source(e, receipt_snapshot) if r['id'] == 'EA-0049' else (validate_charged_trophy_native_source(e, receipt_snapshot) if r['id'] == 'EA-0048' else (validate_zombie_reinforcement_native_source(e, receipt_snapshot) if r['id'] == 'EA-0047' else (validate_evoker_native_source(e, receipt_snapshot) if r['id'] == 'EA-0046' else (validate_peer_sharing_native_source(e, receipt_snapshot) if r['id'] == 'EA-0045' else (validate_snow_native_source(e, receipt_snapshot) if r['id'] == 'EA-0044' else (validate_cat_rest_native_source(e, receipt_snapshot) if r['id'] == 'EA-0043' else (validate_farmer_native_source(e, receipt_snapshot) if r['id'] == 'EA-0042' else (validate_shulker_native_source(e, receipt_snapshot) if r['id'] == 'EA-0041' else (validate_hero_native_source(e, receipt_snapshot) if r['id'] == 'EA-0040' else (validate_natural_budget_native_source(e, receipt_snapshot) if r['id'] == 'EA-0039' else (validate_golem_native_source(e, receipt_snapshot) if r['id'] == 'EA-0038' else (validate_gorilla_native_source(e, receipt_snapshot) if r['id'] == 'EA-0037' else (validate_silverfish_native_source(e, receipt_snapshot) if r['id'] == 'EA-0036' else (validate_enderpearl_native_source(e, receipt_snapshot) if r['id'] == 'EA-0035' else (validate_patrol_native_source(e, receipt_snapshot) if r['id'] == 'EA-0034' else (validate_phantom_native_source(e, receipt_snapshot) if r['id'] == 'EA-0033' else (validate_siege_native_source(e, receipt_snapshot) if r['id'] == 'EA-0032' else (validate_cat_native_source(e, receipt_snapshot) if r['id'] == 'EA-0031' else (validate_allay_native_source(e, receipt_snapshot) if r['id'] == 'EA-0030' else (validate_tasmanian_native_source(e, receipt_snapshot) if r['id'] == 'EA-0029' else validate_closed_native_source(e, receipt_snapshot)))))))))))))))))))))))))
                item = sources.setdefault(e['source_local'], {k:e[k] for k in ('source_kind','source_coordinate','source_artifact','path','source_local','source_sha256','provenance')})
                item.setdefault('supports', [])
                if r['id'] not in item['supports']: item['supports'].append(r['id'])
                continue
            if r['id'] == 'EA-0037' and e.get('source_kind') == 'repository_git':
                from receipt_validation import GORILLA_V20_SPEC, validate_source
                require(sha(json.dumps(e, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()) in GORILLA_V20_SPEC['mod_source_hashes'], 'EA0037 source-index requires its exact typed Git evidence')
                verified_git = validate_source(e, receipt_snapshot)
                item = sources.setdefault(e['source_local'], {
                    **{k:e[k] for k in ('source_kind','repo','revision','path','source_local','source_sha256','git_blob_sha1','source_metadata','tree_metadata')},
                    'provenance': {'kind': 'derived_from_verified_repository_git_fields',
                        'repo': e['repo'], 'revision': verified_git['revision'],
                        'source_sha256': verified_git['source_sha256'], 'git_blob_sha1': verified_git['git_blob_sha1'],
                        'source_metadata': {'path': e['source_metadata'], 'sha256': verified_git['source_metadata_sha256']},
                        'tree_metadata': {'path': e['tree_metadata'], 'sha256': verified_git['tree_metadata_sha256']},
                        'fresh_upstream_authentication': False}})
                item.setdefault('supports', [])
                if r['id'] not in item['supports']: item['supports'].append(r['id'])
                continue
            item=sources.setdefault(e['source_local'],{k:e[k] for k in [
                'repo','revision','path','source_local','source_sha256','git_blob_sha1','source_metadata','tree_metadata','provenance']})
            item.setdefault('supports',[])
            if r['id'] not in item['supports']:item['supports'].append(r['id'])
            raw=(ROOT/e['source_local']).read_bytes()
            assert sha(raw)==e['source_sha256']
            tree=json.loads((ROOT/e['tree_metadata']).read_text())
            meta=json.loads((ROOT/e['source_metadata']).read_text())
            assert tree['sha']==e['revision']==meta.get('sha',meta.get('commit'))
            assert tree['truncated'] is False
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['git_blob_sha1']
            assert next(x for x in tree['tree'] if x['path']==e['path'])['sha']==e['git_blob_sha1']
    # Publish only after actual source bytes and all inspected receipt inputs remain stable.
    receipt_snapshot.stable()
    require({p.name for p in (DOCS/'independent-reviews').glob('*.json')}==
            {Path(r['receipt']).name for r in receipt_validation['receipt_inputs']},
            'receipt directory changed during aggregation; rerun text inspection')
    aggregation_id=sha(json.dumps({'receipts':[(r['receipt'],r['receipt_sha256']) for r in receipt_validation['receipt_inputs']],
        'batches':[(str(p.relative_to(ROOT)),sha(p.read_bytes())) for p in batch_paths]},sort_keys=True).encode())
    receipt_validation['aggregation_id']=aggregation_id
    ledger['aggregation_id']=aggregation_id
    ledger['by_reviewer_validated_receipts']=dict(Counter(r['role'] for r in receipt_validation['receipt_inputs'] if r['state']=='validated_acceptance'))
    dump('receipt-validation.json',receipt_validation)
    dump('master-acceptance-ledger.json',ledger)
    dump('source-index-001.json',{'status':'PINNED_CACHE_BYTES_VERIFIED_NOT_FRESH_NETWORK_VERIFICATION',
        'repositories':sorted({(r['repo'],r['revision']) for r in records if r.get('source_kind') != 'artifact_native'}),
        'artifact_native_coordinates':sorted({r['source_coordinate'] for r in records if r.get('source_kind') == 'artifact_native'}),
        'files':list(sources.values()),'file_count_not_credit':len(sources),
        'upstream_execution':False,'integrity':integrity})

    b=ROOT/'docs/cod4/audit-20261022/ecology-native-acceptance/inputs-01/runtime-04'
    raw_counts={}
    for name in ['native-driver.jsonl','native-client-inputs.jsonl']:
        rows=[json.loads(s) for s in (b/name).read_text().splitlines() if s.strip()]
        raw_counts[name]={'rows':len(rows),'kinds':dict(Counter(r['kind'] for r in rows)), 'sha256':sha((b/name).read_bytes())}
    dump('driver-readback-001.json', {'status':'READ_ONLY_RAW_EVENT_COUNTS_NOT_NEW_GAMEPLAY_CREDIT',
        'raw_counts':raw_counts,'strict_confirmed_killed':0,'strict_zero_source':'runtime04/outcome.json; not inferred by candidate counts',
        'conclusion':'43 targets/61 server guards/61 native client attacks/37 death candidates are separate facts; no confirmed-removal credit inferred',
        'worlds_modified':False})

    dump('continuation.json',{'status':'ACTIVE_RESEARCH_INCOMPLETE_NO_IMPLEMENTATION_AUTHORIZATION',
        'aggregation_id':aggregation_id,'objective':1000,'reviewed_proposed':len(records),'pending_proposals':len(records)-accepted_count,'independently_accepted':accepted_count,
        'reviewed_proposed_shortfall':1000-len(records),'independent_gate_shortfall':1000-accepted_count,
        'unreviewed_or_incomplete_candidates':len(candidates),'gate_met':False,'runtime_credits_changed':False,
        'next_identifier':f'EA-{max(int(r["id"].split("-")[1]) for r in records)+1:04d}',
        'last_completed_batch':sorted(DOCS.glob('batch-*.json'))[-1].name,
        'master_acceptance_ledger':'master-acceptance-ledger.json',
        'next_sources':[
            {'source':'EA-0016 Skreecher alarm/attempt latch', 'independently_accepted':any(r['id']=='EA-0016' for r in accepted), 'action':'原提案、完整独立审阅和不可变floor澄清必须精确绑定；生成尝试不是成功加入，不新增原生验收'},
            {'source':'EA-0014 batch-009 parasitic host lifecycle', 'action':'已有独立接受；不重复审查或计数。EA15仅原未执行build_tenth草案，零信用；EA16只有实际batch012及三份绑定完整收据通过v4后才接受，Triops仍EA17；后续新号按实际records最大ID之后分配'},
            {'candidate_id':'EA-C005','action':'原285f固定树缺实际部署；另一9911 archive已读实际bootstrap但无Git tree，不接枝版本或覆盖旧pin；见candidate-C005-archive-addendum，仍0'},
            {'source':'cached Mowzies EntityLantern full class',
             'action':'已全文读，仅浮游运动/碰撞/动画/死亡视觉，未见新出生或种群状态交接；本次排除0，不为补数量包装AI'},
            {'candidate_id':'EA-C004','formal_proposal_id':'EA-0017',
             'independently_accepted':any(r['id']=='EA-0017' for r in accepted),
             'action':'完整Triops食物/配对/卵/原生父类整链已实际读，见batch-011及不可变提案与独立收据。只有正式校验接纳才计整链1；原候选仍0，注册/父类/每个范围不拆数'},
            {'candidate_id':'EA-C001','action':'储存/释放机制已归EA-0010，原候选不另计；自然部署JSON仍缺，不重复包装已覆盖储存链或重试失败网络'},
            {'candidate_id':'EA-C002','action':'核读Pool.replaceContext、自然结构资源和真实非空biome交集；同组jigsaw结构不重复包装'},
            {'candidate_id':'EA-C003','action':'完整距离helper与实际自然placed_feature绑定；不能仅凭codec注册计数'},
            {'source':'cached Mowzies MowzieStructure/FrostmawPieces/StructureSetHandler',
             'action':'已读地形/biome检查和模板piece，handleDataMarker为空；没有模板NBT不能声称存在实体，未计数'},
            {'source':'cached Quark Stoneling/Toretoise',
             'action':'已见Builder CREATURE/出生表MONSTER与动态getClassification；Zeta链/固定blob证据未闭合，未计数；只研究，禁止改本项目category'}],
        'constraints':['只写独立tools/docs生态研究目录','不编译/测试/开游戏/服务器/GUI','不执行上游代码',
                       '不改生产/cap/概率/category/资产/共享Jar/QA/待办','不新增挂机/清理/随机运行','不继承既有研究信用','每批继续下一实际机制，不等待runtime结果'],
        'network':'one GitHub browser request failed; preserved, no retry; cache remains usable',
        'no_automatic_launch_or_scheduled_run_created':True})
    dump('delivery-inspection.json', {'status':'TEXT_EVIDENCE_PACKAGED_NOT_COMPILED_OR_RUNTIME_VALIDATED',
        'aggregation_id':aggregation_id,'batches':len(batches),'reviewed_proposed':len(records),'candidate_zero_credit':len(candidates),'accepted':accepted_count,'target':1000,
        'all_required_fields_present':True,'all_excerpts_match_source_lines':True,
        'all_git_repository_source_bytes_match_fixed_git_tree':True,'artifact_native_sources_use_explicit_coordinate_archive_contract':True,'cross_batch_semantic_key_duplicates':[],
        'semantic_review':'Human-readable mechanism differences/merged supports in every item; unique keys alone do not prove semantic independence',
        'limits':['未完成1000门槛','仅master接受账所列收据已独立接受，其余仍待审','未做游戏/编译/测试，也未验证上游Mixin部署','旧/新API版本仅供语义借鉴'],
        'writes_confined_to':['tools/cod4/ecology-availability-research/','docs/cod4/audit-20261022/ecology-availability-research/'],
        'runtime_species_material_acceptance':'unchanged24/30+9/10',
        'evidence_files':[{ 'path':str(p.relative_to(ROOT)), 'sha256':sha(p.read_bytes())}
                          for p in sorted(DOCS.glob('*.json')) if p.name!='delivery-inspection.json']})
    print('Source/index inspection:',len(records),'reviewed mechanisms;',len(candidates),'0credit candidates;',len(sources),'source files;',accepted_count,'independently accepted')


if __name__ == '__main__':
    main()
