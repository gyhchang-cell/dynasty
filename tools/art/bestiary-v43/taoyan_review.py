"""Explicit notes from24 actually viewed model/atlas cards; not production or tests."""
from pathlib import Path
import json,hashlib,html,os
ROOT=Path(__file__).resolve().parents[3];CACHE=ROOT/'build/bestiary-v43/taoyan-reference';DOC=ROOT/'docs/art/bestiary-v43'
NOTES='''
外层浅蓝与内部深蓝、鱼形小区是分层材质；只研究半透明内容与内部明度关系，不把透明效果说成PNG贴回后已验证。
主块由几只短足承托，黑红纹路用粗行组织；借鉴主躯与支撑分工，不复制迷宫纹，也不因它是方块就给鼎身铺满纹路。
低壳、前伸夹颚与外展足从胸部接出，黄褐甲壳和暗腹分开；借鉴鼎口、躯壳、腿根不同材质密度。
背壳褐橙、腹部浅色横层、口与足更暗；借鉴内外壳色区不同，器皿内壁不应与外壁一样亮。
背上抬高的一块与低前躯分工，绿色壳面明暗有限，腹面成行；借鉴附属体块不靠每边包框来连接。
低躯壳连外展薄足，棕色图集沿长轴有大段色带；借鉴甲壳的长轴方向，不把纹理平均撒到每根足上。
三节主体、细连接与前颚明确，红褐面只有几档色簇；借鉴骨鞭和足根要有连接且不必满高光；持叶不是本目标装备。
后腹体积大、头胸小而前足有承重；暗红褐壳面保留干净大面，借鉴主体与攻击口的体量分工。
独立前击肢和眼柄在头端集中，绿壳、红连接与腹面分区；仅借鉴攻击器官与支撑肢不同职责，不沿用配色。
长壳、前螯与扇尾一条轴，橙红关节有较深收束；借鉴连接部位的暗面与外壳大面，不新增尾部。
仅查看到原始主体图集，未完整研究外层透明壳和装备显示；不将局部图集当成完整相关参考计数。
壳背与外展肢相接，绿背横向纹理较密、腿部简洁，亮眼只在前；借鉴鼎壳与八支足不同密度。
暗蓝铁质块有口鼻层次与蓝色局部，小色阶使硬表面读得清；借鉴可动器物要先有观察中心，不复制表情。
焦糖软体的凸出面与黄褐纹不对应骨、铜、铁和受力连接；仅辅助观察，不计入饕餮的相关门槛。
虽然名称带Cauldron，实际是鱼形来源；不能仅靠名字相近计数，排除，不把发光鱼嘴当作铸鼎材质。
低宽壳体、左右钳与侧足相接，红壳和浅腹分明；借鉴铜铸外壳与腹下支撑之间有材质边界。
大壳盖住腿根，暗背中央和红侧面分区；借鉴上躯重量由多足分摊，不靠放大脚板。
足从胸腹横向展开，暗红壳面与局部橙色有主次；借鉴八足外围安静，前口保留识别区。
长腹与弯腿构成拱形，暗壳里紫色点只集中于头、腹少数区域；借鉴目光和内核重点不向每条足复制。
当前构造卡只显出头与部分平面，完整身体/腿的继承尚未可靠还原；排除，不拿贴图名宣称已看完整蜘蛛。
抬起的大腹、低头胸和前牙形成方向，绿暗壳与少量紫色分区；借鉴抬升主体与攻击端仍有明暗主次。
厚腹连到多节长足，图集暗红大面与浅关节有限；借鉴足根、节间与末端不同明度，不全身画节线。
前钳粗、侧足多节而头更小，白橙壳与少量蓝眼清楚；借鉴攻击肢与支撑肢分工，不把所有部件同样提亮。
壳上青灰、钳足橙色，关节压暗且壳面横向组织；借鉴铜壳、暗铁足根和骨端分区有位置依据。
'''.strip().splitlines()
EXCLUDED={11:'未完整研究外层与装备显示',14:'软体材质与本目标不相近',15:'仅名字相近，实际鱼形不足以支撑本目标研究',20:'未完整还原身体继承，不能当完整模型'}
def main():
 d=json.loads((CACHE/'candidates.json').read_text());rows=[]
 if len(d['items'])!=len(NOTES):raise RuntimeError('Manual notes do not cover all candidate cards')
 for r,note in zip(d['items'],NOTES):
  p=CACHE/r['card']
  if hashlib.sha256(p.read_bytes()).hexdigest()!=r['card_sha256']:raise RuntimeError('Candidate changed after viewing')
  rows.append({**r,'viewed':True,'accepted_for_target':r['number'] not in EXCLUDED,'observation':note,'excluded_reason':EXCLUDED.get(r['number']),'limits':'Source constructor + original atlas, not a fully textured native screenshot or animation study; repeated skins not extra references.'})
 if len(rows)!=len(NOTES):raise RuntimeError('Incomplete manual notes')
 out={'target':'dynasty:taoyan_zhishi','viewed_candidates':len(rows),'accepted_for_target':sum(r['accepted_for_target'] for r in rows),'required':100,'gate':'INCOMPLETE_NO_ART_PRODUCTION','items':rows,'unprepared':d['excluded'],'source_reading_exclusions':[{'source':'Polarice3/Goety-2:EternalCauldron','reason':'Source extends HumanoidModel and is registered viaCuriosRenderer/WearRenderer: it is a wearable item, not a creature. It is NOT included in the100-creature gate.'}],'runtime_changed':False,'compile_tests_or_game_run':False}
 (DOC/'taoyan-reference-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 page='<!doctype html><html lang="zh"><meta charset="utf-8"><title>饕餮之食 · 参考研究进行中</title><style>body{max-width:1100px;margin:30px auto;background:#e9ebe4;color:#23312d;font:17px/1.65 system-ui}article{margin:24px 0;padding:18px;background:#f7f7ef}img{max-width:760px;width:100%;image-rendering:pixelated}a{color:#256b65}</style><h1>多足铸鼎：模型与原始贴图参考</h1><p>本批实际看过24份候选，采用20份、排除4份。门槛仍为20/100，尚缺80份，不开始模型或贴图制作。Goety的EternalCauldron是穿戴物，未算作生物。</p><p>以下为源码静态构造与原始图集并排研究，不是已贴图实机截图。现有主体、武器、骨架、动画和服务器时序未修改。暂停期间未启动编译、测试或游戏。</p>'
 for r in rows:
  page+=f'<article><h3>#{r["number"]:03} {html.escape(r["identity"])} · {"采用" if r["accepted_for_target"] else "排除"}</h3><img loading="lazy" src="{html.escape(os.path.relpath(CACHE/r["card"],DOC))}"><p>{html.escape(r["observation"])}</p><a href="{r["model_source"]}">固定版本模型源码</a> · <a href="{r["texture_source"]}">原始贴图</a></article>'
 (DOC/'taoyan-reference.html').write_text(page+'</html>')
 p=ROOT/'tools/art/bestiary-v43/progress.json';d=json.loads(p.read_text());d['reference_gate_by_target']['taoyan_zhishi']=out['accepted_for_target'];d['taoyan_research_current']={'status':out['gate'],'viewed':out['viewed_candidates'],'accepted':out['accepted_for_target'],'required':100,'remaining':80,'record':'docs/art/bestiary-v43/taoyan-reference-review.json','binding_inspection':'docs/art/bestiary-v43/taoyan-binding-inspection.json','runtime_changed':False};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 p=DOC/'unfinished-registered.json';d=json.loads(p.read_text());d.setdefault('research_progress',{})['taoyan_zhishi']={'reference_gate':20,'required':100,'art_started':False,'record':'docs/art/bestiary-v43/taoyan-reference-review.json'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 p=DOC/'research-resume-20261028.json';d=json.loads(p.read_text());d['current_reference_gates']['taoyan_zhishi']=20;entry='Taoyan24 source/atlas cards viewed;20 adopted,4 excluded; EternalCauldron separately rejected as a wearable item'
 if entry not in d['completed_this_session']:d['completed_this_session'].append(entry)
 d['next'][0]='Taoyan references20/100;80 applicable creature studies still required before art'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print('Research saved:24 viewed /20 adopted /80 remaining; no runtime resources, builds or tests.')
if __name__=='__main__':
 # Once the manually reviewed continuation exists, this original entry point
 # must not silently roll the cumulative ledger back to the first20 studies.
 continuation=Path(__file__).with_name('taoyan_review_continued.py')
 caches=ROOT/'build/bestiary-v43'
 if continuation.exists() and all((caches/p/'candidates.json').exists() for p in ('taoyan-reference-more','taoyan-reference-bound')):
  import importlib.util
  spec=importlib.util.spec_from_file_location('continued_review',continuation)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.main()
 else:main()
