"""Read-only, line-addressed texture/UV requirements. Not a task completion audit."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
D=Path(__file__).resolve().parent;ROOT=D.parents[3];Q=Path('/Users/a15356015027/Desktop/code x提示词');A=Path('src/main/resources/assets/dynasty')
langpath=A/'lang/zh_cn.json';lang=json.loads(langpath.read_text());assets=[p for p in A.rglob('*') if p.is_file()]
terms=re.compile(r'贴图|纹理|材质|UV|图集|decal|Decal|GUI|图标|纹样|纹饰|外观|外形与体型|基础与模型特征|显圣模型|\*\*(?:头部|胸部|肩部|手臂|腿部|背部|船体|躯干|尾部|前肢/胸部|双翼/肩背|后肢/躯干)\*\*')
sources=[];rows=[];content_targets=[]
for num in [1,2,3,4,6]:
 p=Q/f'cod{num}.txt';data=p.read_bytes();lines=data.decode().splitlines();heading='';chapter=''
 sources.append(dict(file=str(p),sha256=hashlib.sha256(data).hexdigest(),lines=len(lines),all_lines_mechanically_indexed=True,not_claim_full_visual_acceptance=True))
 for i,l in enumerate(lines,1):
  if l.startswith('#'):heading=l
  if l.startswith('# '):chapter=l
  if terms.search(l):rows.append(dict(file=str(p),line=i,quote=l,section=heading,chapter=chapter,source_sha256=sources[-1]['sha256'],status='SOURCE_REQUIREMENT_INDEXED_NOT_DONE'))
  if num==1 and l.startswith('### ') and ((52<=i<329) or (524<=i<1525)):
   name=re.sub(r'^###\s*(?:Boss\s*)?\d+[.：:]\s*','',l);name=re.split('[（(]',name)[0].strip('【】 ')
   candidates=[dict(language_key=k,language_value=v,id=k.split('.')[-1]) for k,v in lang.items() if k.startswith(('item.dynasty.','entity.dynasty.')) and (v==name or (len(name)>4 and name in v))]
   asset_rows=[]
   for c in candidates:
    ident=c['id'];related=[p for p in assets if p.name in [ident+'.png',ident+'.json',ident+'.geo.json',ident+'.animation.json',ident+'.bbmodel']]
    for asset in related:asset_rows.append(dict(path=str(asset),sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),name_match_only=True))
   content_targets.append(dict(source_file=str(p),heading_line=i,name=name,category=('basic_creature' if i<329 else 'elite' if i<769 else 'boss' if i<1194 else 'artifact' if i<1450 else 'phantom'),language_candidates=candidates,exact_name_asset_candidates=asset_rows,
    status='RESOURCE_NAME_CANDIDATES_REQUIRE_BINDING_AND_VISUAL_REVIEW' if candidates else 'NO_EXACT_CHINESE_LANGUAGE_MATCH_BINDING_UNRESOLVED',
    limitation='这里只核语言和源资源同名，不证明注册/加载/缺资源；不得因旧描述或同名文件存在就重画/判DONE。'))
priority=[
 dict(priority=1,file='cod4.txt',lines=[49,50,57,121],scope='Original6pattern scopes',need='八学院身份残影、帝兵decal、已有龙纹/甲裂材质贴合；新生产门槛未足。',next='继续固定本地相关设计研究及既有图源核对，不改程序。'),
 dict(priority=2,file='cod6.txt',lines=[80,87,93,99,106,114,271,278],scope='Four-symbol/creature materials',need='四象不同鳞/牙/羽/壳纹与光路；每只生物金属/布/骨/皮鳞分材、原主色和少量发光。',next='先与现有已认可来源和模型专岗对齐；纹理存在不证明绑定，不新建几何。'),
 dict(priority=3,file='cod1.txt',lines=[7,9,608,748,772,809,1197,1208,1454,1460,1466,1472,1478,1484,1490,1496,1502,1508,1514,1520],scope='Creature/artifact/phantom UV',need='保护较新专用非人模型/原稿，逐对象确认实际atlas与有符号面UV；十二神影身份/材质不同。',next='有模型/原图的先只读核；未绑定者不凭名称建立缺图结论。'),
 dict(priority=4,file='cod3.txt',lines=[1013,1014,1015,1016,1017,1018,1019,1021,1072,1073,1074,1075,1076,1077,1078,1079],scope='Machine GUI material only',need='八机中央身份图、深底/铜玉槽/危险禁用层；真实配方与状态绑定由程序专岗。',next='现有GUI只读核，不改FTB/正文/槽位逻辑；无单独PNG可能程序绘制，不判漏图。'),
 dict(priority=5,file='cod2.txt',lines=[513,522,758,760,772],scope='Character armor UV only',need='甲层和内衣密度/接缝/左右朝向；体型与几何任务不接。',next='沿新的人类/非人要求核UV，不按早期复杂比例推翻已认可模型。'),
 dict(priority=6,file='cod3.txt',lines=[1242,1243,1244,1245,1246,1247,1248],scope='Scenic surface/material only',need='军阵/舟影/云光/星线等贴图适配；楼阁/建筑设计不接。',next='只做已有对象材质，建筑1000相关实例门槛不借PNG/组件抵数。')]
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),role='texture/pattern/UV only',sources=sources,cod5_exists=(Q/'cod5.txt').exists(),
 source_language=dict(path=str(langpath),sha256=hashlib.sha256(langpath.read_bytes()).hexdigest()),indexed_requirement_lines=rows,content_target_name_candidates=content_targets,priorities=priority,
 manual_review_boundary='Focused visual/material wording and listed sections read; mechanical all-line index is not full implementation/game acceptance. Broader task list is not completed by this index.',
 production_changes=0,prompt_changes=0,accepted_new_reference_credit=0,protected_latest_user_approved_art=True)
(D/'expanded-texture-uv-requirements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(sources=5,requirement_lines=len(rows),content_targets=len(content_targets),by_category={c:sum(r['category']==c for r in content_targets) for c in ['basic_creature','elite','boss','artifact','phantom']},language_matched=sum(bool(r['language_candidates']) for r in content_targets),production_changes=0),ensure_ascii=False))
