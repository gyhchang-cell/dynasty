"""Seal old D002 source supplementation and a separate old291 correction."""
import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
binding=ld(P/'source-binding.json');d=ld(P/'source-original.json');counts=ld(P/'source-counts.json');correction=ld(P/'prior-reading-correction.json')
ck('source archive fixed',bind(binding['archive']['path'])==binding['archive'])
with ZipFile(binding['archive']['path'])as z:
 raw=z.read(binding['member']);ck('original source exact',hashlib.sha256(raw).hexdigest()==binding['raw_sha256']and read(raw)==d)
 for row in ld(P/'source-context.json')['resources']:
  raw=z.read(row['member']);ck('full context exact '+row['member'],hashlib.sha256(raw).hexdigest()==row['sha256']and raw.decode()==row['text']and json.loads(raw)==row['json'])
ck('source accounting',counts['stored']==1914 and counts['nonair']==1344 and counts['explicit_air']==570 and counts['omitted']==5286 and 1914+5286==18*20*20)
ck('complete source palette ten',len(d['palette'])==10 and counts['BE']==1 and counts['entities']==0)
fp=ld(P/'historical-fingerprint-check.json');ck('exact old D002 machine match',len(fp['matches'])==1 and fp['current']==fp['matches'][0]['fingerprints'])
for item in correction['prior_records']:ck('old actual-reading evidence immutable '+item['candidate_id'],bind(item['binding']['path'])==item['binding'])
ck('old ledger immutable',bind(correction['oldD002_visual_ledger_binding']['path'])==correction['oldD002_visual_ledger_binding'])
ck('old291 sealed immutable',bind(correction['old291_receipt']['path'])==correction['old291_receipt']and bind(correction['old291_manual']['path'])==correction['old291_manual'])
excluded=ld(P/'excluded-already-credited-chapels.json');ck('two already credited chapels retained',len(excluded['entries'])==2 and bind(excluded['binding']['path'])==excluded['binding'])
ck('eight actual source images',len(list(P.glob('*.png')))==8)
status='SEALED_OLD_D002_FULL_LAYER_SUPPLEMENT_AND_291_PRIOR_VIEW_CORRECTION_ZERO_NEW_BUILDING'
review=dict(batch=293,status=status,source=binding,source_url='https://modrinth.com/mod/explore-ruins-aether',source_url_boundary='Historical candidate attribution only; not a new network visit.',new_distinct_whole_buildings=0,new_complete_whole_studies=0,old_whole_source_supplements=1,new_qualifying_reference_proposals=0,formal_credit_added=0,tasks_deleted=0,
 actual_reading=dict(current_images=[bind(p)for p in sorted(P.glob('*.png'))],images_actually_viewed=8,all_plan_layers_actually_viewed=20,full_height_section_planes=2,palette_states_actually_read=10,special_states_actually_read=9,central_source_probe_cells_actually_read=100,whole_context_resources_actually_read=3,oldD002_whole_view_reused_zero_credit=True,old_images_reopened=False),
 observations=dict(
  layout='旧D002单体云基祭亭，六柱分列x5/13、z5/9/13，中央 raised stone pedestal与唯一source chest(9,7,9)，南北中轴开敞入口，四周同一不规则云基。不是一组多岛寺院，也不是有战斗大平台的露天祭坛。',
  proportion='保存18×20×20，底部云基约y0..5，祭亭floor y5、源箱基座y6、箱y7，柱头y12，厚顶y14..18，y19未存。小亭是单层功能空间；20格存储高度不是20层、屋盖厚度不是上楼空间。',
  facade='两侧各三柱；前后中间留开口、无门，入口上方局部实心石梁，柱头与屋檐分层。原柱和云的形状未原生查看，不把来源分类灰色当真实材质色。',
  roof='四坡阶梯状实体顶逐层内收，中心剖面y14..18为连续实块。该亭有完整覆盖屋顶，不能为了匹配露天祭坛需求而忽略屋盖。八slab位于南北开口两侧y10 top/y11 bottom，未当作室外台阶。',
  materials='angelic_stone725、holystone325、cold_aercloud245、pillar32、pillar_top6、ambrosium_torch2、angelic_slab8、chest1；还有570显式air，5286未存。全部10palette原属性已读；云是实际原方块ID，不是普通石地板或保证可行走的透明装饰。',
  circulation='已读全20层与两整高剖面，并逐读中轴x9、z0..19、y4..8共100原单元。北侧z4/5 floor y5上y6/7 air而y8有梁；南侧z13/14相似；中心y6祭台占z8..10，箱在其上，需要绕台接近。原无门、阶梯、梯、jigsaw；云外沿与世界进场、柱旁净宽/碰撞、箱盖与自然实抽未验。',
  terrain='原#aether:is_aether、uniform start height absolute40至below_top25、none适配，单一rigid根模板、不接其他房间；单候选weight20不是20个祭亭。没有地表heightmap字段，仅读配置不证明实际维度生成高度/悬空落脚或跨岛进出。'
 ),
 processor='完整原规则实际读：angelic_stone以.05变light_angelic_stone，holystone以.2变mossy_holystone；未执行随机规则，不把1344原nonair材料统计当最终处理后数量。唯一箱引用aether bronze dungeon loot，未读表或原生领取。',
 prior_reading_correction=bind(P/'prior-reading-correction.json'),
 correction_effect='旧D002在2026-10-29 manual-visual-ledger与review-batch004已实际看完整双向/中层并明确不计相关参考。293只是全层/入口补证0。另证旧B002在review-batch002也已实际看完整体量/中切，291不可作新增不同建筑，sealed291原文件保持历史原样，靠本独立纠错明确source supplement0。formal两批原0均不变。',
 applicability='云基—小型祭亭—中央祭台/箱的单体比例可作为DUN07附属祭祀小亭组织原则；与cod1天绝雷泽露天战场（无顶、四引雷柱）和DUN07三岛炼丹主殿规模/路线不同，HOLD0，不借换范围自动入账。旧森林礼堂/沙漠礼堂已有完整信用不再计。',
 applications=['云基形状与有效步行面、祭台/箱周边余量分开核查；云方块行为和现场入口未验不能当安全地板。','按有效室内净空、梁下通路和顶盖实体厚度分配比例，不按存储上限放大房间。','去重先解析旧candidate-ID键、review-batch及manual-visual-ledger，再查新manual/原member；不把候选status未更新当未看过的证据。'],
 limits=['本批新增不同完整建筑0、有效相关参考0，旧参考不重算。此前只搜直接member字段的边界不足已显式纠正。','8PNG是原作者存储分类图，不是native texture/mesh/collision；未运行Java/游戏/随机处理器、落脚测试或外部来源访问。','只写293目录，不改旧sealed文件、主清单、pending、ownership、session、专业资产或共享Jar；无声音亮度/唤醒/用户实例操作。','未达到1000有效完整相关参考，不制作、不删除任何任务；Main收到元数据不等实际看图、读源或验收。'],
 COD4_accepted_old_observation=153,COD4_gap_old_observation=847,NPC_cumulative=None,all_tasks_complete=False)
put('manual-review.json',review)
protected=[]
for row in ld(P/'protected-before.json')['files']:
 b=row['before293'];a=bind(b['path']);protected.append(dict(before=b,after=a,unchanged=a==b,this_chat_wrote_file=False))
put('protected-current.json',dict(files=protected,boundary='Read only shared-state observation; concurrent differences are never overwritten.'))
ck('shared Jar unchanged',all(x['unchanged']for x in protected if x['before']['path'].endswith('.jar')))
cp=ld(P/'active-checkpoint.json');cp.update(status=status,images_actually_viewed=8,new_distinct_whole_buildings=0,new_complete_whole_studies=0,old_whole_source_supplements=1,formal_credit_added=0,next='先查所有旧review-batch与ID键/ledger，再继续别的未实际完整阅读建筑；旧D002和291旧B002不再作新增整栋。');put('active-checkpoint.json',cp)
put('verification.json',dict(passed=True,checks=checks,count=len(checks),java_run=False,game_run=False,independent_acceptance=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=293,status=status,files=files,checks=len(checks),new_distinct_whole_buildings=0,new_complete_whole_studies=0,old_whole_source_supplements=1,new_qualifying_reference_proposals=0,formal_credit_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_unchanged=sum(x['unchanged']for x in protected)),ensure_ascii=False))
