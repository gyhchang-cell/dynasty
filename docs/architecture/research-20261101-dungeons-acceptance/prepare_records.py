#!/usr/bin/env python3
"""Export twelve individually reviewable proposals, without awarding credits."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
PARENT=OUT.parent
MASTER=PARENT/'continuation-20261022/references/full-buildings.json'
MASTER_SHA='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
LABELS={'layout':'布局','proportion':'比例','facade':'立面','roof':'屋顶','materials':'材质','circulation':'动线','terrain':'地形衔接'}
BOUNDARIES={
 '002-F01':'长院堡（20×20×41）：可借鉴狭长院落与两端厅楼、边墙短塔；不是长城、瓮城或完整古战场。',
 '002-F02':'紧凑高主堡（20×35×22）：可借鉴入口附院到高主堡的层次；不覆盖低矮城墙或大规模城池。',
 '002-F03':'低双塔堡（23×17×23）：可借鉴短塔与低主屋、双梯井分工；不覆盖高塔群或大院堡。',
 '002-F04':'大型偏置院堡（48³保存边界）：可借鉴主堡、独立门塔与开院的主次；不能直接代表中式瓮城结构。',
 '002-F05':'三圆塔桥堡（48³保存边界）：可借鉴高位桥连接不同塔室；不是三栋独立参考，也不覆盖城墙围院。',
 '002-F06':'紧凑尖塔连低厅（17×38×23）：可借鉴单高塔与低厅体量；不覆盖大型多角塔城。',
 '002-F07':'环院双高楼堡（43×40×43）：可借鉴低围廊与对角高楼的联系；不等于中式官衙或地下城全局。',
 '002-F08':'长窄并排高厅堡（30×47×17）：可借鉴双厅间中层交通；不覆盖露天战场或大院堡。',
 '002-F16':'双塔小院堡（25×43×30）：可借鉴小院、两塔和墙上通道；不是大型围城战区域。',
 '003-F01':'双塔哨站（48³保存边界）：可借鉴双高塔夹低连接体与下层分室；不按双塔拆两例，不覆盖完整城池。',
 '003-F05':'高角塔连L形低厅（27×45×35）：可借鉴角塔控向与低厅组合；不覆盖多角塔围城。',
 '003-F09':'近地四角哨棚围院（16×8×16）：可借鉴小哨堡低墙、入口与开院；不覆盖高堡、瓮城或整座战场。',
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
 before=sha(MASTER); assert before==MASTER_SHA
 rows=[]; geometry=[]
 for batch in ['002','003']:
  folder=PARENT/f'research-20261101-dungeons-{batch}'
  sources=json.loads((folder/'sources.json').read_text())
  reviews=json.loads((folder/'manual-review.json').read_text())
  dedup=json.loads((folder/'dedup-evidence.json').read_text())
  receipt=json.loads((folder/'RECEIPT.json').read_text())
  for item in receipt['files']: assert sha(folder/item['path'])==item['sha256']
  for c,v,dd in zip(sources['candidates'],reviews['entries'],dedup['entries']):
   if not v['credit_proposal']: continue
   ident=batch+'-'+c['id']; assert ident in BOUNDARIES
   assert c['id']==v['id']==dd['id']
   assert c['nbt_sha256']==v['nbt_sha256']==dd['nbt_sha256']
   assert not dd['historical_exact_matches']
   assert sha(Path(c['source_archive']))==c['source_archive_sha256']
   with ZipFile(c['source_archive']) as z:
    assert hashlib.sha256(z.read(c['member'])).hexdigest()==c['nbt_sha256']
   for image in v['images_actually_viewed']: assert sha(Path(image['path']))==image['sha256']
   pools=sorted({p['data'].get('pool','') for p in c['sockets']})
   assert all(':terrain' in p or ':mobs/' in p for p in pools)
   geometry.append((ident,dd['role_sha256'],dd['occupancy_sha256']))
   row=dict(id=ident,source_batch=str(folder),member=c['member'],size=c['size'],
    source_archive=c['source_archive'],source_archive_sha256=c['source_archive_sha256'],
    nbt_sha256=c['nbt_sha256'],publisher_url=c['publisher_url'],publisher_url_access='Provenance only; not requested online',
    target_boundary=BOUNDARIES[ident],
    target='DUN03 万骨枯寂·血海古战场：仅对应具体城防节点的空间组织参考',
    image_origin='Local original NBT rendered for inspection; these are NOT original-author screenshots or native game screenshots.',
    images_actually_studied=v['images_actually_viewed'],observations=v['observations'],
    independent_design_basis=v['independent_design_basis'],dedup_evidence=dd,
    outgoing_pool_ids=pools,
    review_checks=dict(source_bytes_and_original_nbt=True,four_previously_viewed_image_hashes=True,
     seven_semantic_aspects=True,whole_stored_building_or_courtyard=True,
     no_unassembled_room_pool_at_template_sockets=True,historical_exact_duplicate=False,
     native_collision_terrain_and_playthrough_accepted=False,scope_credit_accepted=False),
    status='READY_FOR_INDIVIDUAL_SCOPE_REVIEW_NOT_ACCEPTED_CREDIT',formal_credit_added=0,
    requirement='The 1000 references must be verified for the actual building purpose and scale. Twelve proposals do not automatically add twelve to any target scope. Existing COD4 148 and COD6 0 remain separate.',
    record=ident+'.md')
   rows.append(row)
   lines=[f'# {ident}｜{c["member"].rsplit("/",1)[-1]}','',
    '**状态：证据已整理，具体用途/规模的信用尚待协调逐例验收；未增加正式参考数。**','',
    BOUNDARIES[ident],'',
    '仅用于DUN03相应城防节点的空间组织学习。不是已制作资产，不是整座古战场方案；不能跨用途、跨规模自动累计。此处尺寸为保存边界，包含屋尖、台脚及空余，不等于功能净尺寸。','',
    '## 来源与完整建筑范围','',
    f'- 原始归档：`{c["source_archive"]}`',f'- 归档SHA256：`{c["source_archive_sha256"]}`',
    f'- 成员：`{c["member"]}`',f'- NBT SHA256：`{c["nbt_sha256"]}`',
    f'- [来源项目]({c["publisher_url"]})：仅历史出处，本次未请求网络。',
    f'- 保存边界：`{c["size"]}`；模板外接池：`{pools}`。这些接口没有待组装房间池；地形/实体接口仍非生成验收。','',
    '下图由本地原始NBT生成，是已经实际查看过的结构研究图；不是作者原始截图或游戏实景。阶梯、栅栏等采用整格近似，不能证明原生碰撞、贴图、落地地形或安全通关。','']
   for e in v['images_actually_viewed']:
    image=Path(e['path']); rel='../'+folder.name+'/'+image.name
    lines += [f'![{ident} {image.stem}]({rel})',f'图像SHA256：`{e["sha256"]}`','']
   lines+=['## 七方面语义观察','']
   for key,label in LABELS.items(): lines += [f'- **{label}**：{v["observations"][key]}']
   lines+=['','## 去重与验收边界','',v['independent_design_basis'],'',
    f'去重核对了{dedup["historical_unique_local_archive_member_pairs"]}个历史本地归档/成员组合，含组件、待核资料，不等于有效建筑参考数。原文、旋转归一角色几何和纯占用几何均未发现完全匹配；相似度仅作辅助，不证明设计独立。',
    f'角色几何SHA256：`{dd["role_sha256"]}`；纯占用几何SHA256：`{dd["occupancy_sha256"]}`。','',
    f'[完整去重证据](../{folder.name}/dedup-evidence.json) · [原逐例研究](../{folder.name}/manual-review.json)','',
    '来源、四张既有图与七方面记录已核验；完整建筑范围按整栋或整个院堡限定，塔、屋顶、楼层不能拆计。协调仍需按待制具体建筑的用途、规模审核相关性，决定是否纳入对应范围。未到该范围1000不开始制作，不因本记录删除主清单。','']
   (OUT/(ident+'.md')).write_text('\n'.join(lines))
 assert len(rows)==12
 assert len({r['nbt_sha256'] for r in rows})==12
 assert len({g[1] for g in geometry})==len({g[2] for g in geometry})==12
 assert sha(MASTER)==before
 dump(OUT/'acceptance-index.json',dict(entries=rows,proposal_count=12,formal_credit_added=0,
  formal_registry_sha256=before,native_acceptance=False,new_architecture_started=False,
  main_checklist_modified=False,java_run=False,game_run=False,network_requests=0))
 lines=['# 12例城防参考逐例验收入口','',
  '本目录将第二、三批的12例提案分别整理，未给予正式信用。每例含四张已查看研究图的链接/哈希、原始来源、完整建筑范围、七方面观察、历史去重证据、具体用途/规模限制。源图是NBT研究渲染，不是作者实景截图。','',
  '**12是提案数，不是任一具体建筑范围已增加12例。** 各目标仍须独立审查相关性及累计至1000；不得移用义庄/墓园148，不能把小围院、尖塔连厅、圆塔桥堡互相替代。正式台账原范围148/1000、COD6 0/1000，均未改动。','',
  '| 逐例记录 | 对应范围 |','|---|---|']
 lines += [f'| [{r["id"]}]({r["record"]}) | {r["target_boundary"]} |' for r in rows]
 lines += ['','[机器可读逐例证据](acceptance-index.json)','',
  '仅写独立研究目录；未改生产资产、主清单，未运行Java、游戏或网络请求；未开始建筑制作。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump(OUT/'RECEIPT.json',dict(files=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in files],
  status='PASS_EVIDENCE_PACKAGE_ONLY',formal_credit_added=0))
 print('Twelve per-building records verified; zero scope credits or checklist changes.')

if __name__=='__main__': main()
