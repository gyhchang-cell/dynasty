#!/usr/bin/env python3
"""Whole house-court layout, distinct from a perpendicular low-wing garrison."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def main():
 s=importlib.util.spec_from_file_location('common',BASE/'research-20261101-dungeons-017/record_review.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 src=m.get(OUT/'sources.json');c=src['candidates'][0]
 obs=[
  '一座宽向长屋接端部单院，院的围墙沿两侧回接屋前；高、低房屋段及平行长屋面同向，室层有多个内部开口和门。旧010-F05为较窄高长厅与垂直其长轴的低翼／侧院，不是本例宽长屋接单端围院的平面组织；不因都用坡屋顶就强并一族。',
  '22×24×29，实占y0..22，最高y23为空。29格长轴和22格短轴与既有010-F01的29×22平面尺度同类，保存高度23格位于原中型驻防建筑范围。屋盖尖和空层不当额外房间。',
  '木骨架夹白色墙面，宽主立面以侧柱、窗洞和连续低檐分段；侧面凸出小台，前院红色围墙明显低于高房。观察平面关系与房间开口，不凭颜色判独立。',
  '较高主盖与较低长盖同向并行，盖下仍有室层而不是纯粹帽顶加高。与旧高窄长厅、横向低翼两条互相转折的体量关系不同；高檐的饰边阶块不当行走楼梯。',
  'stripped_dark_oak_wood329、granite324、dark_oak_stairs199、white_wool198、spruce_planks196、terracotta194。材质命名与分类灰色不一致，因此记录原始材料，不能拿灰色效果图声称屋顶是石砖。',
  '9个下半门分布y0/3/4/9/14；普通梯(12,4)y4..8、(13,9)y9..13在平面换位。最低门(14,0,21)不是唯一主入口；自动y0/y1图主要切地脚，另取y3/y9及x12/z9审室层。门分层与换梯并不认证全程原生可走。',
  '主建筑在单个本体模板内完整存有屋盖、室层与回接院墙；另一个22×1×29地基片仅是土、水和零星地脚，不是第二个建筑。本体向下接口与地基向上接口名字相配，但本轮未装配／运行，地形胡须处理器及地表投影不据此算已验。']
 comparisons=[(10,'F01','whole'),(10,'F02','whole'),(10,'F03','whole'),(10,'F05','whole'),(10,'F05','details')]
 entry=dict(id='F01',source=c,decision='ACCEPTED_ONE_COMPLETE_GARRISON_LAYOUT',credit=1,scope_id='DUN03-MEDIUM-GROUND-GARRISON',
  observations=dict(zip(m.ASPECTS,obs)),actual_images_viewed=[m.ev(OUT/('F01-'+n+'.png')) for n in ['whole','plan','vertical','details']],native_acceptance=False)
 m.dump('manual-review.json',dict(entries=[entry],templates_studied=1,actual_new_images_viewed=4,independent_references_added=1,
  credited_ids=['020-F01'],historical_comparison_views=[m.ev(BASE/f'research-20261101-dungeons-{b:03d}/{i}-{v}.png') for b,i,v in comparisons],
  semantic_dedup='实际对照旧长厅低翼的整体和室层剖面后，宽长屋与单端回接院／同向高低长盖关系具有不同平面组织；不按地基片、楼层、屋盖或截图分计。',
  prefix_match_issue='旧渲染工具按字符串包含查池时会误把forest_fort_ground的起始池列成forest_fort本体入口；当前sources.json只保留精确JSON值的main池，本轮四批精确值审计一致。未修改历史渲染器。',
  old_holds_reopened=False,old_holds_retained=['011-F04','012-F03','016-F01','016-F05','019-F02'],
  image_limits='整方块分类色；自动最低门切片不等于入口验收，未做原生碰撞、地形或递归拼装。',
  network_requests=0,java_run=False,game_run=False,production_changes=0,checklist_deletions=0,independent_human_reviewer_claimed=False))
 m.dump('scoped-reference-update.json',m.scope_record(20))
 # Ground is checked as source-boundary evidence only, not another reference.
 import sys
 sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
 from nbt_read import read
 with ZipFile(c['source_archive']) as z:
  name='data/simply_houses/structures/forest_fort/forest_fort_ground.nbt';raw=z.read(name);d=read(raw);pal=d['palette']
  docs=[]
  for n in ['data/simply_houses/worldgen/structure/forest_fort.json','data/simply_houses/worldgen/template_pool/forest_fort/forest_fort_main.json','data/simply_houses/worldgen/template_pool/forest_fort/forest_fort_start.json']:
   b=z.read(n);docs.append(dict(member=n,sha256=hashlib.sha256(b).hexdigest(),data=json.loads(b)))
  m.dump('ground-boundary.json',dict(source_archive=c['source_archive'],source_archive_sha256=c['source_archive_sha256'],member=name,
   sha256=hashlib.sha256(raw).hexdigest(),size=d['size'],materials=dict(Counter(pal[b['state']]['Name'] for b in d['blocks'])),
   sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw'],
   exact_definition_documents=docs,component_images_viewed=False,assembled=False,building_credit=0,
   source_boundary='Ground only, 22×1×29, never another building. Start pool chooses only ground; main pool lists body and ground. Reciprocal names/orientations recorded, not native generation proof.'))
 # Preserve the immutable old package and append a narrow metadata correction.
 old_index=BASE/'research-20261101-dungeons-016/sources.json'
 old_review=m.get(BASE/'research-20261101-dungeons-016/manual-review.json')
 def exact(v,k):
  if isinstance(v,str):return v==k
  if isinstance(v,dict):return any(exact(x,k)for x in v.values())
  if isinstance(v,list):return any(exact(x,k)for x in v)
  return False
 corrections=[]
 for old in m.get(old_index)['candidates']:
  prefix,tail=old['member'].split('/structures/');identifier=prefix.split('/')[-1]+':'+tail[:-4]
  good=[];bad=[]
  with ZipFile(old['source_archive'])as z:
   for r in old['pool_references']:
    raw=z.read(r['member']);assert json.loads(raw)==r['data']
    row=dict(member=r['member'],sha256=hashlib.sha256(raw).hexdigest(),data=r['data'])
    (good if exact(r['data'],identifier)else bad).append(row)
  corrections.append(dict(id='016-'+old['id'],body_member=old['member'],body_nbt_sha256=old['nbt_sha256'],
   original_credit=next(r['credit']for r in old_review['entries']if r['id']==old['id']),
   exact_identity=identifier,valid_exact_pool_records=good,false_prefix_pool_records=bad))
 m.dump('prior-prefix-audit.json',dict(original_index=m.ev(old_index),entries=corrections,
  previous_files_modified=False,new_visual_readings=0,new_buildings=0,credit_change=0,
  conclusion='016-F01 was already held with zero credit: four stored pool references are prefix-only and must not be used as exact selection evidence. Accepted 016-F02 retains its one exact pool. Source NBT, visual layouts and scope count 7 are unaffected.'))
 print('020: one whole house-court layout accepted after room/wing comparison. Scopes 6/7/1; ground credit 0.')
if __name__=='__main__':main()
