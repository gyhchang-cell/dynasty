"""Preserve primary review of helper040; no automatic promotion."""
from ledger import B,O,R
import json,hashlib,datetime
h=O/'helpers/herschel-immune/batch-040.json';data=json.loads(h.read_text());refs=[]
for row in data['rows']:
 for r in row['source_refs']:
  repo_key,rel=r['source_key'].split('/',1);root=B/'sources'/repo_key;p=root/rel;raw=p.read_bytes();meta=json.loads((root/'source.json').read_text());tree=json.loads((root/'tree.json').read_text());blobs={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
  assert meta['commit']==r['fixed_commit']==tree['sha']
  assert hashlib.sha256(raw).hexdigest()==r['file_sha256']
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[rel]
  a,z=r['lines'];assert 1<=a<=z<=len(raw.decode().splitlines())
  refs.append({'path':str(p.relative_to(R)),'source_path':rel,'lines':[a,z],'file_sha256':r['file_sha256'],'url':r['url'],'method':r['method'],'research_credit':0})
out={'helper_file_sha256':hashlib.sha256(h.read_bytes()).hexdigest(),'main_review_new_effective':0,'helper_original_credit':0,'main_full_listed_methods_read':True,'main_entire_classes_read':False,'state':'reviewed_support_only','source_refs':refs,'observations':[
 'Gloomper hurtServer完整方法先50%分支生成600tick半径3云/100tick病毒并响声，再无条件return parent hurtServer；没有amount>0 guard，不能当最终成功伤害或拒绝后的免疫收据。own VIRULENCE拒绝是已覆盖静态effect策略，物种/云ID不另计。',
 'AbstractBolloom六个完整方法：玩家skipAttackInteraction调用hurt(playerAttack,0)；own无敌gate失败才false；否则即使客户端或已死亡也true，但只有server+alive执行discard/markHurt/onBroken。零量交互成功≠HP掉血；隐藏火动画≠火免疫，本类非Living特殊对象不新增Boss机制。',
 'Booflo hurt和actuallyHurt两方法完整：parent前可重置攻击目标；IN_WALL0.5后PuffBug2.5更高优先。parent true且无既有endimation才播放受击动画；false仍可能已改目标。动画缺失不能反推免疫。未展开NetworkUtil/完整父级，不把源内调用宣称双端画面。'],
 'semantic_decision':'三组均为已覆盖结算前副作用/静态拒绝/交互布尔与HP不等价的反例支持；无独立新拒控语义或新闭合反馈生产消费链，0。未按11方法/3文件加信用。', 'production_changes':False,'game_started':False,'compile_run':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(O/'HERSCHEL-040-REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'support_units':3,'method_ranges':len(refs),'new_credit':0}))
