#!/usr/bin/env python3
"""Accept only two independently reviewed whole lodging layouts in a new isolated scope."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=OUT.parent/'research-20261101-dungeons-004'
REF=OUT.parent/'continuation-20261022/references'
SCOPE='DUN05-URBAN-LARGE-PUBLIC-LODGING'
COMP=[
 ('research-20261101-dungeons-001/F02-whole.png','004-F01','旧ruined_castle为多高角塔、断墙和中部石层台，入口由长石桥联系；新为集中公共主楼内分室和独立低附屋，不是旧城堡旋转或换材。'),
 ('continuation-20261022/references/whole-candidates-004/D012.png','004-F01','旧tidal_tomb为近立方厚壳、四角柱和四面竖水带/集中屋盖，内部集中水面；新为多翼公共房楼加分离附屋，无此单壳水庭。'),
 ('research-20261101-dungeons-003/F12-whole.png','004-F01','旧pillager_mansion为纵长高主屋连前方较低侧翼、整块石台，主体紧凑相接；新主楼L形多层分室且另有分离低屋和泥院，差别不是仅交叉屋顶或木色。'),
 ('continuation-20261022/references/whole-candidates-002/B005.png','004-F02','旧sinking_temple为入水台阶、偏高祭塔和集中小殿群；新为三向房翼包开院、楼层连接的公共旅店，院内空地和房间翼关系不同。'),
 ('research-20261101-dungeons-002/F13-whole.png','004-F02','旧pyramide_of_anubis为大面积连续四面退台壳和内部小祭室，新为开U院、三向长坡屋房翼；几何最近不能代替建筑功能与空间比较。'),
 ('research-20261101-dungeons-003/F01-whole.png','004-F02','旧desert_outpost为并排双高塔、方形层台和狭窄塔间连接，新为不等高三向长房翼围院；不因同为数层或平面近方就归成同一设计。')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def load(p):return json.loads(p.read_text())
def image_check(e):
 p=Path(e['path']);assert sha(p)==e['sha256']
 with Image.open(p) as im:im.verify()
def main():
 sources=load(BASE/'sources.json');review=load(BASE/'manual-review.json');old_dedup=load(BASE/'dedup-evidence.json')
 receipt=BASE/'coordinator-independent-two-urban-lodging-review-20261101.json';independent=load(receipt)
 assert independent['formal_credit_added']==0 and len(independent['entries'])==2
 selected=[c for c in sources['candidates'] if c['id'] in ['F01','F02']];assert len(selected)==2
 selected_pairs={(c['source_archive'],c['member']) for c in selected}
 sp=importlib.util.spec_from_file_location('whole_dedup',OUT.parent/'research-20261101-dungeons-002/check_dedup.py')
 helper=importlib.util.module_from_spec(sp);sp.loader.exec_module(helper)
 indices=[REF/'full-buildings.json']+sorted(REF.glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ['sources.json','scope-expansion-sources.json','manual-review.json']:
   if (folder/name).is_file():indices.append(folder/name)
 historical={}
 for p in indices:helper.find_records(load(p),str(p),historical)
 self_occurrences=[historical[k] for k in selected_pairs];others=[(k,v) for k,v in historical.items() if k not in selected_pairs]
 old=[(row,helper.load(row)) for k,row in others]
 current=[(c,helper.load(dict(archive=c['source_archive'],member=c['member']))) for c in selected]
 rows=[];dups=[]
 for c,geometry in current:
  assert sha(Path(c['source_archive']))==c['source_archive_sha256']
  original_review=next(x for x in review['entries'] if x['id']==c['id'])
  coord=next(x for x in independent['entries'] if x['id']==c['id'])
  assert coord['member']==c['member'] and coord['archive_sha256_verified']==c['source_archive_sha256'] and coord['nbt_sha256_verified']==c['nbt_sha256']
  assert coord['max_scoped_credit_after_owner_dedup_acceptance']==1
  assert len(original_review['images_actually_viewed'])==len(coord['pngs_actually_viewed'])==4
  for e in original_review['images_actually_viewed']:image_check(e)
  for e in coord['pngs_actually_viewed']:image_check(dict(path=str(ROOT/e['path']),sha256=e['sha256']))
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);assert digest(raw)==c['nbt_sha256']==geometry['nbt_sha256']
   d=helper.read(raw);p=d.get('palette') or d['palettes'][0]
   assert d['size']==c['size']
   points=[b['pos'] for b in d['blocks'] if p[b['state']]['Name'] not in helper.AIR]
   bounds=[[min(v[a] for v in points),max(v[a] for v in points)] for a in range(3)]
  matches=[];nearest=[]
  for h,hd in old:
   same=[key for key in ['nbt_sha256','role_sha256','occupancy_sha256'] if geometry[key]==hd[key]]
   if same:matches.append(dict(member=h['member'],archive=h['archive'],reasons=same))
   occ=geometry['variants'][0]
   score=max(len(occ&v)/(len(occ)+len(v)-len(occ&v)) for v in hd['variants'])
   nearest.append(dict(member=h['member'],archive=h['archive'],occupancy_jaccard=round(score,5)))
  assert not matches
  dups.append(dict(id='004-'+c['id'],identity={k:v for k,v in geometry.items() if k!='variants'},historical_exact_matches=matches,
   nearest_occupancy_only=sorted(nearest,key=lambda x:-x['occupancy_jaccard'])[:6]))
  rows.append(dict(id='004-'+c['id'],scope_id=SCOPE,status='ACCEPTED_SCOPED_COMPLETE_BUILDING_LAYOUT_REFERENCE',credit=1,
   source=c,observations=original_review['observations'],actual_views=original_review['images_actually_viewed'],
   original_proposal=ev(BASE/'reference-proposals.json'),independent_coordinator_review=ev(receipt),
   independent_observations=coord['actual_independent_observations'],occupied_bounds=bounds,
   design_family='CONCENTRATED_L_MAIN_BUILDING_WITH_DETACHED_LOW_OUTBUILDING' if c['id']=='F01' else 'CONNECTED_U_WINGS_WITH_OPEN_COURTYARD',
   application='DUN05街区大型公共商住/旅店布局：地面公共入口、上层分室、主次体量与院/附屋联系。',
   not_accepted_for=['全枉死城','中式官衙/判官殿','地下落位/地形拼接','机关或任务/指南针功能','原生全房通路/碰撞','外观风格制作门槛'],native_acceptance=False))
 assert current[0][1]['role_sha256']!=current[1][1]['role_sha256'] and current[0][1]['occupancy_sha256']!=current[1][1]['occupancy_sha256']
 assert [x['occupied_bounds'][1][1] for x in rows]==[35,30]
 assert len(rows)==2 and sum(x['credit'] for x in rows)==2
 compared=[]
 for path,target,note in COMP:
  e=ev(OUT.parent/path);image_check(e);compared.append(dict(target=target,image_actually_viewed=e,semantic_comparison=note))
 semantic=dict(entries=compared,source_views_reviewed_again=8,historical_comparison_views_reviewed_again=6,
  pairwise='F01集中L形多层主楼+独立低附屋共享泥院；F02多翼连成U形围开院，上层相接。开放空地与房翼的拓扑、主体连离和高度分工均不同，不是旋转、换色或只换屋顶。',
  boundary='结合既有逐例建筑研究、旧129组合几何筛查、当前全索引几何筛查、六个历史近邻实际图及协调独立八图/原始NBT复核。没有声称本次重新目视全部历史成员；近邻分数不是独立设计证明。')
 dump('semantic-review.json',semantic)
 dump('dedup-evidence.json',dict(historical_indices_checked=[str(p) for p in indices],historical_unique_pairs_including_prior_self_records=len(historical),
  prior_self_identity_records=self_occurrences,other_unique_archive_member_pairs_checked=len(old),entries=dups,
  pairwise_exact_duplicate=False,method='Raw SHA and four-rotation canonical role/occupancy comparison; exact prior identities of004-F01/F02 excluded as self, not extra examples.',
  semantic_review='semantic-review.json',limits='Archive/member identities include components and holds; counts are not whole-building reference totals. Not universal semantic proof of unseen designs.'))
 master=REF/'full-buildings.json';outpost=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 assert sha(master)=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
 assert sha(outpost)=='2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'
 register=dict(scope_id=SCOPE,title='DUN05街区大型公共商住/旅店完整布局',target_references=1000,accepted_references=2,remaining=998,construction_allowed=False,
  scope_definition='完整公共商住/旅店组设计；相近约40–50格平面、实际约30–36格高，公共地面层+上层分室，院落/附屋是整设计的一部分。只研究这一街区子任务的用途、规模与空间组织；不是全城或中国式样的完成证明。',
  count_unit='One whole related design; detached outbuilding, room, wing, roof, view, rotation, palette variant or socket does not add credit.',
  accepted=rows,formal_credit_added_in_this_scope=2,legacy148_credit_transferred=0,other_scope_credit_transferred=0,
  evidence=dict(semantic_review=ev(OUT/'semantic-review.json'),current_dedup=ev(OUT/'dedup-evidence.json'),coordinator_review=ev(receipt)),
  unchanged_scopes=dict(legacy_registry_sha256=sha(master),legacy_count=148,legacy_remaining=852,
   outpost_registry_sha256=sha(outpost),outpost_each_accepted=1,outpost_each_remaining=999,cod6=0),
  principles=['主楼集中+分离低附屋，与多翼连院提供两种公共入口到上层分室的空间组织，整体各计一次。',
   '街面公共开口、院面入口与上层私密空间分工应清楚，不能靠门数推客房数。',
   '保存空高、细饰与屋面内腔不折算楼层；整方块分类图不当真实墙密度或贴图。',
   '应用布局原则须另做目标中式美术、地下地形和真实动线检查；未达1000不提前制作。'])
 dump('urban-lodging-scope-register.json',register)
 report=dict(status='PASS_TWO_SCOPED_LODGING_LAYOUT_REFERENCES',scope_id=SCOPE,accepted_references=2,target=1000,remaining=998,
  formal_credit_added_in_this_scope=2,production_tasks_completed=0,source_views_reviewed_again=8,historical_views_reviewed_again=6,
  prior_self_records_excluded=len(self_occurrences),other_archive_member_pairs_checked=len(old),legacy148_unchanged=True,outpost_three_scopes_unchanged=True,
  network_requests=0,java_run=False,game_run=False,production_changes=0,checklist_deletions=0)
 dump('verification.json',report)
 (OUT/'HANDOFF.md').write_text('\n'.join(['# 大型公共商住／旅店布局：限定验收','',
  '**DUN05-URBAN-LARGE-PUBLIC-LODGING：2/1000，缺998，禁止提前制作。**','',
  '结合协调独立8图及源NBT复核、专岗既有七项观察、本次8图重看、六个历史近邻图的语义比较与当前全索引字节/旋转几何筛查，接受004-F01、004-F02两套完整设计。主楼和分离附屋仍是一例；U形旅店的多翼仍是一例。','',
  '[限定账本](urban-lodging-scope-register.json) · [语义比较](semantic-review.json) · [当前去重](dedup-evidence.json) · [校验](verification.json)','',
  'F01集中L形主楼+独立低附屋，实际最高y35；F02连翼包开院，实际最高y30。相近用途和规模允许在同一大型公共商住/旅店布局子范围学习两种组织方法，不要求每个新布局另立仅一例范围。差异不限屋顶、材质或旋转。','',
  '这是完整建筑的布局参考验收，不是游戏建筑资产完成；没有覆盖全枉死城、中式官衙、地下埋深、地形接缝、全房原生通路、机关、任务或指南针。分类图不认证真实材质、光照、碰撞或地形生成。','',
  '当前索引中的004原身份仅作为自身旧记录排除，不新增第三/第四例。其余历史成员含组件和不合用途项，去重筛查数量不计参考信用。本次只实际重看六个历史近邻，并未声称本次重新目视全部历史归档。','',
  '原义庄/墓园148/1000、缺852不变；三个既有前哨范围各1/1000、缺999不变；COD6仍0。未转借信用。未运行Java/游戏/网络，未改声音、亮度、窗口、存档、专业资产或主清单，未删除提示词。','']))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in load(OUT/'RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
