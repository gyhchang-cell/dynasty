"""Package stopped, existing private QA evidence; never launches Minecraft or modifies production."""
from pathlib import Path
import json,hashlib,datetime,shutil,subprocess,zipfile,collections
R=Path(__file__).resolve().parents[3];T=R/'tools/cod4/ecology-acceptance';D=R/'docs/cod4/audit-20261022/ecology-acceptance';L=D/'live-run1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Preserve one APFS clone of the already saved own QA world and its cursor.
checkpoint=T/'.work/static-handoff-20261024';checkpoint.mkdir(exist_ok=True)
if not (checkpoint/'world').exists():subprocess.run(['cp','-cR',str(T/'.work/live-run1/world'),str(checkpoint/'world')],check=True)
for name in ['state.json','control.json','coordinator.jsonl','client-status.txt','saved-cursor-static-handoff.json']:
 if not (checkpoint/name).exists():shutil.copy2(L/name,checkpoint/name)
wm={str(p.relative_to(checkpoint/'world')):sha(p) for p in (checkpoint/'world').rglob('*') if p.is_file()}
(D/'saved-world-checkpoint-manifest.json').write_text(json.dumps({'checkpoint':str(checkpoint),'method':'APFS cp -cR clone of stopped own QA world; no game launched','file_count':len(wm),'files':wm},indent=2)+'\n')
# Exact cached Minecraft/Forge sources supporting the initialization-time diagnosis.
zp=next((T/'.work/cross-build/gradle-home/caches/forge_gradle/minecraft_user_repo').rglob('*sources.jar'));out=D/'cross-dimension-run7/source-timing';out.mkdir(exist_ok=True);refs=[]
with zipfile.ZipFile(zp) as z:
 for name,start,end in [('net/minecraft/world/level/block/entity/SignBlockEntity.java',173,260),('net/minecraft/server/level/WorldGenRegion.java',202,239),('net/minecraft/world/level/chunk/LevelChunk.java',350,370)]:
  raw=z.read(name);lines=raw.decode().splitlines();p=out/(Path(name).name+'.excerpt.txt');p.write_text('\n'.join(f'{i+1}: {lines[i]}' for i in range(start-1,min(end,len(lines))))+'\n');refs.append({'source_jar':str(zp),'jar_sha256':sha(zp),'entry':name,'entry_sha256':hashlib.sha256(raw).hexdigest(),'excerpt':str(p.relative_to(D)),'excerpt_sha256':sha(p)})
F=T/'.work/cross-build/frozen'
for name in ['WangsiPiece.java','WangsiStructure.java','WangsiArchitecture.java']:
 p=F/'src/main/java/com/dynasty/dungeon'/name;dest=out/(name+'.txt');shutil.copy2(p,dest);refs.append({'frozen_source':str(p),'frozen_sha256':sha(p),'formal_current_sha256_read_only':sha(R/'src/main/java/com/dynasty/dungeon'/name),'preserved_copy':str(dest.relative_to(D))})
(D/'cross-dimension-run7/sign-initialization-timing.json').write_text(json.dumps({'status':'READ_ONLY_SOURCE_TIMING_ANALYSIS_OF_TWO_NATIVE_FAILURES','runtime_failure':'WangsiPiece.sign:75 calls SignBlockEntity.setText -> setFrontText -> markUpdated:245, where level is null','timing':'Native ChunkStatus FEATURES / WorldGenRegion may construct or return a ProtoChunk BlockEntity before it is attached to a Level. LevelChunk.setBlockEntity later calls setLevel(this.level).','other_same_timing_call':'setWaxed also calls markUpdated; changing only text or removing signs is not accepted as a fix. No fix performed here.','not_a_manual_piece_fixture':True,'not_a_design_or_layout_change':True,'repair_owner':'Original building conversation; its requested1000 relevant reference investigation is outside this read-only handoff.','sources':refs},ensure_ascii=False,indent=2)+'\n')
# Original denominators and raw fresh natural-birth events, not placement callbacks.
s=json.loads((L/'summary.json').read_text());source=json.loads((D/'source-audit.json').read_text());ids={x['id'] for x in source['species']};events=[]
for n,line in enumerate((L/'events.jsonl').read_text().splitlines(),1):
 try:e=json.loads(line)
 except json.JSONDecodeError:continue
 e['event_line']=n;events.append(e)
births=collections.defaultdict(list)
for e in events:
 if e['kind']=='confirmed_natural_spawn' and not e.get('loaded_from_disk',True) and e['species'].split(':')[-1] in ids:births[e['species'].split(':')[-1]].append(e)
coordinator=json.loads((D.parent/'ecology-live-coordinator-check-nine-materials.json').read_text());old_missing=set(coordinator['not_yet_born']);new_since22=[x for x in sorted(old_missing) if births[x]]
rows=[]
for ident in sorted(ids):
 bs=births[ident];b=bs[0] if bs else None;rows.append({'species':ident,'status':'NATIVE_FRESH_BIRTH_OBSERVED' if b else 'PENDING_NO_BIRTH','fresh_birth_count':len(bs),'first_event_line':b['event_line'] if b else None,'first_game_tick':b['game_tick'] if b else None,'first_mob_uuid':b['uuid'] if b else None,'first_biome':b['biome'] if b else None,'first_pos':b['pos'] if b else None,'first_has_NaturalSpawner_stack':any('NaturalSpawner.spawnCategoryForPosition' in x for x in b.get('native_spawn_stack',[])) if b else False})
(D/'static-natural-birth-species.json').write_text(json.dumps({'original_denominator':30,'actual_fresh_birth_species':sum(bool(births[x]) for x in ids),'prior22_preserved':True,'additional_since_coordinator22':new_since22,'rows':rows,'events_sha256':sha(L/'events.jsonl'),'valid_placement_positions_are_not_births':True},ensure_ascii=False,indent=2)+'\n')
(D/'static-natural-birth-species.tsv').write_text('species\tactual_fresh_birth_count\tfirst_event_line\tfirst_game_tick\tfirst_mob_uuid\tfirst_biome\tfirst_pos\n'+''.join('\t'.join(str(x.get(k,'')) for k in ['species','fresh_birth_count','first_event_line','first_game_tick','first_mob_uuid','first_biome','first_pos'])+'\n' for x in rows))
oil=next(x for x in s['material_proofs'] if x['id']=='lantern_oil');cursor=json.loads((L/'saved-cursor-static-handoff.json').read_text())
record={'status':'STATIC_HANDOFF_NO_RESTART','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':'normal-run2 historical19/30 positions +2 natural structures retained','valid_positions':s['native_valid_position_species'],'valid_positions_denominator':30,'actual_natural_birth_species':sum(bool(births[x]) for x in ids),'actual_natural_birth_denominator':30,'additional_after_coordinator22':new_since22,'remaining_actual_birth_species':[x for x in sorted(ids) if not births[x]],'natural_material_death_drop_species':s['natural_material_death_drop_verified'],'materials_denominator':10,'exact_material_pickup_species':s['material_pickup_exact_uuid_verified'],'remaining_exact_pickup':['lantern_oil'],'lantern_oil_actual_player_death_attempts':s['material_species_death_attempts'].get('dynasty:lantern_ghost',0),'lantern_oil_positive_death_drop_events':len(oil['proofs']),'lantern_oil_exact_pickup':False,'lantern_oil_unpicked_original_UUID_proofs':oil['proofs'],'saved_inventory_slots_used':cursor['main_inventory_slots_used'],'inventory_causality_limit':'Current saved inventory is36/36, compatible with pickup obstruction; each past drop did not record contemporaneous slot occupancy, so not a demonstrated cause for every missed pickup. No replacement items supplied.','world_checkpoint':str(checkpoint),'world_manifest':'saved-world-checkpoint-manifest.json','saved_native_world_tick':cursor['native_save_Time'],'last_QA_state_tick':cursor['last_qa_state_tick'],'last_client_status':cursor['last_client_status'],'clean_server_save_shutdown_claim':False,'current_own_ports_closed':True,'games_started_for_this_handoff':0,'Wangsi_native_FULL_status':'FAIL_REPRODUCED_2_RUNS','Wangsi_exact_chunk':'[-6520,-2626]','Wangsi_failure_manifest':'cross-dimension-run7/runtime-fixture-manifest.json','Wangsi_source_timing':'cross-dimension-run7/sign-initialization-timing.json','pending_scenes':['Overworld abandoned village','complete mortuary','surface cemetery','natural Wangsi ghost-market FULL generation fails sign initialization','underworld secondary ecology0/30 dimension/biome gates'],'scope':'QA-only; no original world, formal Java/assets or TODO changed; no new clients/servers or bad-city repetition','Hegel_C2S_scope':'Unchanged; not duplicated','full_COD4_or_full_survival_pass':False,'evidence_hashes':{str(p.relative_to(D)):sha(p) for p in [L/'events.jsonl',L/'summary.json',L/'proof-review-receipt.json',D/'static-natural-birth-species.json',D/'cross-dimension-run7/runtime-fixture-manifest.json',D/'cross-dimension-run7/full-exception-stacktrace.txt']}}
(D/'static-handoff.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
text=f'''自然生态静态移交（不再启动游戏）
原normal-run2的19/30位置、2自然结构保留；30/30有效位点单独计数。
实际新鲜NATURAL出生24/30；原协调已核对22种全部保留，新增paper_money_ghost（events行23899，tick111236）与bat_demon（行32434，tick158988）。原30物种逐项证据见static-natural-birth-species.tsv/json，不能将位点回调代替出生。
10/10材料有实际自然玩家击杀掉落；9/10有同一ItemEntity UUID拾取链。灯油：18次玩家击杀、9次正向掉落、0确切拾取；原UUID逐项保留于static-handoff.json。当前原生背包36/36，但没有每次历史掉落时的背包快照，不将它判为全部漏拾取的已证实原因。
只读保存游标：原生存档tick1579880，末QA状态tick1579766，最后客户端游标tick716479；两QA端口无监听，相关进程不存在。客户端日志有Stopping/BUILD SUCCESSFUL；服务端末尾缺完整正常关闭日志，故不声称本次完成正常停机。只读原存档已APFS克隆到{checkpoint}，全文件SHA256见saved-world-checkpoint-manifest.json；停止标记保留，禁止自动续跑。
Wangsi两轮正常原生FULL生成失败，已足够复现。run7候选区域(-17,-7)、chunk[-6520,-2626]、原点XZ(-104320,-42016)，生产1/1接受、FULL0/1通过、1/1失败。异常WangsiPiece.sign:75 -> SignBlockEntity.setText:174 -> setFrontText:190 -> markUpdated:245：level=null。FEATURES/WorldGenRegion阶段BE可未附Level；setWaxed也会markUpdated。完整stacktrace、运行夹具清单、冻结源码哈希和本地原版初始化时机摘录均在cross-dimension-run7。由原建筑对话研究处理，不删牌/场景规避。625阴性仅历史有限样本；扩展run6原计划1681但136行后第137处FULL失败，不能报1681完成或全世界不存在。
剩余实际出生：{', '.join(record['remaining_actual_birth_species'])}。六种均CREATURE，现有类别cap拥堵是继续研究方向，不冒充已实测出生或全局不可能。
剩余场景：主世界荒村、完整义庄、地表墓园；地府已有实体鬼市生产链，但正常FULL招牌生成失败，另30种生态入口仍被地府维度/biome门槛拒绝。无新建筑/新游戏进程，正式Java/资产/原档/TODO均未修改；TODO由主协调同步。
'''
(D/'static-handoff.txt').write_text(text)
(D/'report.txt').write_text(text+'\n当前唯一入口：static-handoff.json / .txt；旧零材料结果见normal-run2-historical-report.txt。\n')
(D/'handoff-progress.txt').write_text(text)
(D/'live-progress.json').write_text(json.dumps({k:record[k] for k in ['status','actual_natural_birth_species','remaining_actual_birth_species','natural_material_death_drop_species','exact_material_pickup_species','remaining_exact_pickup','saved_native_world_tick','last_QA_state_tick','Wangsi_native_FULL_status','games_started_for_this_handoff']},ensure_ascii=False,indent=2)+'\n')
print({k:record[k] for k in ['status','actual_natural_birth_species','natural_material_death_drop_species','exact_material_pickup_species','games_started_for_this_handoff']})
# Retain the old625-negative snapshot, but make the root cross audit current.
for suffix in ['json','txt']:
 old=D/f'cross-dimension-bounded-history-run5.{suffix}'
 if not old.exists():shutil.copy2(D/f'cross-dimension-audit.{suffix}',old)
hist=json.loads((D/'cross-dimension-bounded-history-run5.json').read_text());urgent=json.loads((D/'handoff-urgent-native-failure.json').read_text());candidates={}
for num in [5,6]:
 obs=json.loads((D/f'cross-dimension-run{num}/observations.json').read_text())
 for x in obs['observations']:
  if x['kind']=='native_candidate_generation_point':candidates[x['candidate_chunk']]=x['production_findValidGenerationPoint_present']
point=urgent['run7']['runtime_accepted_point'];candidates[point['candidate_chunk']]=True
cross={**hist,'status':'NATIVE_WANGSI_FULL_FAIL_REPRODUCED_STATIC_HANDOFF','building_presence':'Existing Wangsi ghost-market source chain and a genuine native production-accepted location confirmed. FULL native worldgen fails sign initialization. No global absence claim.','historical_negative_sample':{'run':5,'candidate_denominator':625,'production_accepted':0,'history':'cross-dimension-bounded-history-run5.json'},'distinct_candidate_denominator':len(candidates),'production_accepted_distinct':sum(candidates.values()),'production_rejected_distinct':sum(not x for x in candidates.values()),'denominator_note':'625 historical negatives +136 further negative rows +1 accepted location =762 unique explicit generation-point results. run6 planned1681 but aborted at attempt137; run7 repeats only that accepted location. Never report1681 completed. Native locate internal candidates are not included in this explicit denominator.','runtime_accepted_point':point,'native_FULL_status':'FAIL_REPRODUCED_RUN6_RUN7','native_failure_delivery':'wangsi-native-failure-delivery.txt','runtime_fixture_manifest':'cross-dimension-run7/runtime-fixture-manifest.json','source_timing':'cross-dimension-run7/sign-initialization-timing.json','latest_native_failure':urgent,'games_started_for_static_handoff':0}
(D/'cross-dimension-audit.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2)+'\n');(D/'cross-dimension-audit.txt').write_text((D/'wangsi-native-failure-delivery.txt').read_text()+'\n当前只读移交：static-handoff.txt；762个明确去重生产判定中761阴性、1阳性，FULL生成两次失败；不再复跑。地府两biome仍各0/30标签/刷怪入口。完整鬼市自然现场待修复后验收，不能称已有625阴性证明全局不存在。\n')
pre=L/'historical-live-report-pre-static.txt'
if not pre.exists():shutil.copy2(L/'report.txt',pre)
(L/'report.txt').write_text(text+'\n逐项拾取链：proof-review-receipt.json、summary.json；后者status已标STATIC_HANDOFF_NO_RESTART。\n')
cross['historical_successful_bounded_runs']=cross['native_runs']
cross['native_failure_runs']=[{'run':f'cross-dimension-run{n}','native_acceptance_pass':False,'receipt':json.loads((D/f'cross-dimension-run{n}/receipt.json').read_text()),'runtime_manifest':f'cross-dimension-run{n}/runtime-fixture-manifest.json'} for n in [6,7]]
cross['total_native_run_count']=7
(D/'cross-dimension-audit.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2)+'\n')
