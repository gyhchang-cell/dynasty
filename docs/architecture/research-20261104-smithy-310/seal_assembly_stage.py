import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
protected=[R/'docs/cod4/audit-20261022'/s for s in ['active-workstreams.json','pending-tasks.json','continuation-20261028/session.json']]+[R/f'docs/architecture/{n}/RECEIPT.json'for n in ['research-20261102-dungeons-034','research-20261104-smithy-306','research-20261104-smithy-307','research-20261104-smithy-308','research-20261104-smithy-309']]+[Path('/Users/a15356015027/Desktop/code x提示词')/n for n in ['cod1.txt','cod2.txt','cod3.txt','cod4.txt']]
before=[bind(f)for f in protected]
root=ld(P/'StructureGuling-static.json');piece=ld(P/'StructureGuling$Piece-static.json');source=ld(P/'source-binding.json')
checks=[]
def ck(n,v):
 assert v,n
 checks.append(dict(check=n,passed=True))
def meth(d,name):return next(m for m in d['methods']if m['name']==name)
def constnum(r):
 if r['op']=='iconst_m1':return -1
 if r['op'].startswith('iconst_'):return int(r['op'][-1])
 return r['signed_value']
def position_constructors(m):
 out=[];ins=m['instructions']
 for i,r in enumerate(ins):
  if r.get('constant')=='net/minecraft/core/BlockPos.<init>(III)V':out.append(dict(constructor_pc=r['pc'],vector=[constnum(v)for v in ins[i-3:i]]))
 return out
vectors=position_constructors(meth(root,'start'));offsets=position_constructors(meth(root,'<clinit>'))
ck('start_four_actual_BlockPos_constructor_vectors', [v['vector']for v in vectors]==[[27,1,27],[1,1,27],[1,1,1],[27,1,1]])
ck('allfour_final_OFFSET_vectors', [v['vector']for v in offsets]==[[0,1,0]]*4)
ck('normal_generation_rotation_NONE',any(v.get('constant','')=='net/minecraft/world/level/block/Rotation.NONELnet/minecraft/world/level/block/Rotation;'for v in meth(root,'generatePieces')['instructions']))
ck('bootstrap0_targets_generation_lambda',root['bootstrap_methods'][0]['arguments'][1]['target'].startswith(root['class_name']+'.lambda$findGenerationPoint$0'))
ck('base_negative32_literal_present',any(v.get('signed_value')==-32 for v in meth(root,'m_214086_')['instructions']))
ck('makePosition_calls_additive_offset',any(v.get('constant','')=='net/minecraft/core/BlockPos.m_121955_(Lnet/minecraft/core/Vec3i;)Lnet/minecraft/core/BlockPos;'for v in meth(piece,'makePosition')['instructions']))
merged=ld(P/'merged-original-reference.json');pal=merged['palette'];bs={tuple(b['pos']):b for b in merged['blocks']}
ck('one53x45x53_declared_volume_all126405cells_stored_no_overlap',merged['size']==[53,45,53]and len(merged['blocks'])==len(bs)==53*45*53)
for part in source['parts']:
 d=ld(part['original']['path']);off=part['normalized_origin']
 for b in d['blocks']:
  q=tuple(b['pos'][i]+off[i]for i in range(3));v=bs[q]
  assert pal[v['state']]==d['palette'][b['state']]and v.get('nbt')==b.get('nbt')
ck('all_four_originals_state_Properties_BE_preserved_after_translation',True)
layers=ld(P/'merged-full-layers-RLE.json')['layers'];ck('45layers2385rows',len(layers)==45 and sum(len(v['rows_z'])for v in layers)==2385)
for ly in layers:
 for z,row in enumerate(ly['rows_z']):
  x=0
  for state,count in row:
   assert count>0
   for xx in range(x,x+count):assert bs[xx,ly['y'],z]['state']==state
   x+=count
  assert x==53
ck('all126405RLEdecodedstates_match_merged_original',True)
ck('308palette113BE_11source_entities',len(pal)==308 and len(ld(P/'merged-all-BE.json'))==113 and len(merged['entities'])==11)
for v in merged['entities']:
 part=next(p for p in source['parts']if p['part']==v['part']);off=part['normalized_origin']
 assert v['entity']in part['entities']
 assert v['normalized_pos']==[v['entity']['pos'][i]+off[i]for i in range(3)]
 assert v['normalized_blockPos']==[v['entity']['blockPos'][i]+off[i]for i in range(3)]
ck('11raw_entities_preserved_with_separate_normalized_template_anchors',True)
ck('61650nonair64755air',sum(pal[v['state']]['Name']=='minecraft:air'for v in bs.values())==64755)
ck('no_PNG_before_full_architectural_reading',not list(P.glob('*.png')))
oldpath=R/'docs/architecture/research-20261102-dungeons-034/manual-review.json';old=ld(oldpath)
prior=[dict(id=v['id'],observations=v['observations'],decision=v['decision'],reason=v['reason'],credit=v['credit'],complete_building_identity_confirmed=v['complete_building_identity_confirmed'])for v in old['entries']]
meta=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';fp=R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';history={v['source']['member']for v in ld(fp)['entries']}
words=['grave','cemeter','mausoleum','crypt','tomb','abandon','haunt','ruined_village','morgue','chinese','pagoda','shrine'];hits=[dict(member=e['member'],size=e['size'])for e in ld(meta)['entries']if any(w in e['member'].lower()for w in words) and e['member']not in history and min(e.get('size',[0]))>=5]
put('bounded-source-search.json',dict(metadata=bind(meta),history_cache=bind(fp),keyword_candidates_not_in_cache=hits,limits='仅名称/保存盒/历史NONAIR缓存候选过滤。431缓存含旧部分研究，不能把排除命中理解为全部整栋已读，更不能称本地穷尽。7候选未在此逐体读，0语义信用。',requalification='另查guling四已见组件，034因地面堡营/塔范围及拼接未知排除；本轮实际方法体核读支持改向地下陵墓完整候选边界研究，非旧记录错误或4新建筑。'))
analysis=dict(batch=310,status='STATIC_ORIGINAL_COMPOSITION_RESOLVED_ARCHITECTURAL_READING_NOT_COMPLETE',scope='cod2古墓地宫/废村荒镇的陵墓空间与cod1/cod3义庄墓葬动线辅助资格预研究；不把陵墓直接改称义庄或徽派住宅。',task_bindings=[bind(Path('/Users/a15356015027/Desktop/code x提示词')/n)for n in ['cod1.txt','cod2.txt','cod3.txt','cod4.txt']],source=bind(P/'source-binding.json'),mapping_crosswalk=bind(P/'mapping-crosswalk.json'),actual_static_reading=dict(root_methods=8,piece_methods=8,all16_method_instruction_bodies_read=True,all3_bootstrap_records_read=True,full_class_constant_pool_read_claimed=False,all11_raw_source_entity_payloads_read=True,complete_context_JSON_bodies_read=4,selected_localization_bodies_read=2,whole_old034_components_seven_dimension_texts_read=4,new_PNGs=0,merged_palette_308_actual_read=False,merged_BE_113_actual_read=False,all45layers_actual_read=False),manual_placement_derivation=dict(generation_base='(start chunk minBlockX, -32, minBlockZ); class m_214086_ literal -32, ChunkPos min mappings fixed.',rotation='Normal generatePieces explicitly Rotation.NONE; no mirror. Do not generalize reconstruction to saved alternate rotations.',start_vectors=vectors,final_offset_map_constructors=offsets,position_chain='start: rotate local constructor vector, additive offset(baseX,baseY,baseZ); Piece.makePosition: additive OFFSET(0,1,0). Two +1Y stages: base -32→final -30.',absolute_original_origins_relative_chunk_minXZ=[[27,-30,27],[1,-30,27],[1,-30,1],[27,-30,1]],normalized_origins=[v['normalized_origin']for v in source['parts']],normalized_size=[53,45,53],declared_source_world_Y=[-30,14],rectangular_quadrants='x,z 1..26 or27..53 concatenate without gaps/overlap; original 126405cells all stored. Complete volume is not proof of whole design qualification or traversal.',construction='Raw original state/Properties/BE and air retained; only translations + canonical identical palette merging. No wall/roof/cell added, no new NBT/model/export or game asset.'),runtime_boundaries=dict(ignore_processor='f74046 maps STRUCTURE_BLOCK, not AIR; raw marker blocks kept in reference, placement processing not executed.',protected_processor='ProtectedBlockProcessor using BlockTags FEATURES_CANNOT_REPLACE remains actual-world dependent.',keep_liquids='m163782(false)=setKeepLiquids(false), not ignoreEntities.',data_markers='Piece m213704 code has boss_spawn→NAMELESS_GUARDIAN, elite_spawn→GULING_SENTINEL_HEAVY, normal_spawn→GULING_SENTINEL; static reading only, no actual markers/AI/spawn count accepted.',declarations='JSON step underground_decoration/start_height0 and class method m226619 returning SURFACE_STRUCTURES/base literal-32 coexist in fixed source; preserve both, no runtime precedence or bug claim.'),prior034=dict(binding=bind(oldpath),reading_boundary='Only four selected seven-dimension observations/decisions and original completeness limit actually read; huge embedded source dump was truncated, not claimed fully read.',entries=prior,unchanged_boundary=old['family_and_completeness']),qualification=dict(original_underground_tomb_purpose_supported='ANCIENT_TOMB class names + underground config + original selected Chinese advancement远古陵墓/到达远古陵墓; supports further burial-space inquiry.',strict_Chinese_Hui_architecture_credit=0,cultural_limit='中文名称不是中式构造/徽派风格资格；未读完整空间前不把墓室改叫义庄/停棺厅，也不重贴旧塔/锻造商摊用途。',one_possible_composite_source_boundary=True,new_complete_whole_studies=0,new_reference_proposal_credit=0,formal_credit_added=0,whole_scope_total=None,whole_scope_gap=None,gate_met=False),next=['从已绑定merged原参考读取全308palette Properties和113完整BE，记录读过与未读范围。','按45层2385行RLE原索引逐批实际核读、看完整近族七维；在全部读完/用途与去重预判断前不生成PNG。','合格时只讨论整座陵墓最多1实例，不能给四源/层/房/陷阱额外数；另需Main独立审查，不自加旧153。'],limits=['四模板既有历史不清零；本批是拼接方法及来源准备，不是新完整建筑参考或原生生成/交通验收。','Main306有限NPC03辅助1/严格0保留；Main307新验1有界DUN05民居空间辅助，严格0/totalgapnull，只carry不迁本源。309未审；308两工坊HOLD不改用途。','未到适用1000不生产、不删任务、不触Java/Gradle/游戏/网络/UI/声音亮度/唤醒焦点/实例原档/共享Jar/专业资产/主清单/session/Git/自动化。'])
analysis['Main307_bounded_actual_review_carry']=bind(P/'Main307-bounded-review-carry.json')
analysis['own_failed_guard_then_correction']=ld(P/'source-entity-boundary-correction.json')
put('assembly-origin-analysis.json',analysis)
put('validation.json',dict(checks=checks,boundary='Static class/data checks, never semantic reference or runtime acceptance.'))
put('active-checkpoint.json',dict(batch=310,status='SEALED_STATIC_COMPOSITION_READY_FOR_FULL_ARCHITECTURAL_READING',analysis=bind(P/'assembly-origin-analysis.json'),source=bind(P/'source-binding.json'),full_properties_read=0,full_BE_read=0,full_merged_layers_read=0,new_complete_whole_studies=0,formal_credit_added=0,whole_total=None,whole_gap=None,PNGs=0,tasks_deleted=0,next='下一新目录续读308Properties/113BE/45层与完整近族；sealed310不可写/重跑。无全读不PNG，无1000不制作。'))
after=[bind(p)for p in protected];assert before==after
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=310,status='SEALED_STATIC_COMPOSITE_ORIGIN_RESEARCH_NOT_FULL_BUILDING_STUDY',files=files,data_checks=checks,protected_before=before,protected_after=after,protection_boundary='Only seal-step before/after stability, not concurrent session duration.',actual_static_method_bodies_read=16,actual_full_original_contexts_read=4,PNGs=0,new_complete_whole_studies=0,formal_credit_added=0,strict_Chinese_Hui_credit_added=0,whole_total=None,whole_gap=None,applicable_gate_met=False,tasks_deleted=0,production_changes=0,java_executed=False,native_acceptance=False,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),analysis=bind(P/'assembly-origin-analysis.json'),files=len(files),checks=len(checks),protected_stable=len(after)),ensure_ascii=False))
