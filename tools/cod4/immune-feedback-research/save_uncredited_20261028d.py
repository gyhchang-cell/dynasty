"""Persist bounded support observations; never promote helper proposals by file count."""
from ledger import B,O,R
import json,hashlib,datetime
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'research_credit':0,'scope':'Static source reading only; no gameplay/production/TODO changes','groups':[]}
def add(repo,paths,reason):
 root=B/'sources'/repo.replace('/','__');m=json.loads((root/'source.json').read_text());refs=[]
 for p in paths:
  f=root/p;b=f.read_bytes();refs.append({'path':str(f.relative_to(R)),'file_sha256':hashlib.sha256(b).hexdigest(),'lines':[1,len(b.decode().splitlines())],'commit':m['commit'],'url':f'https://github.com/{repo}/blob/{m["commit"]}/{p}','research_credit':0})
 out['groups'].append({'repo':repo,'source_refs':refs,'observation':reason,'research_credit':0})
p='src/main/java/com/github/alexthe666/iceandfire/'
add('AlexModGuy/Ice_and_Fire',[p+'entity/EntityGhost.java'],'全类已读。固定毒/凋零/环境伤源拒绝、不可推/石化是既有来源/资格过滤家族；日光NoAI/silent/100tick隐身不是拒控收据。未补原生跳吓粒子/动画消费者，不把一般环境状态或事件调用计新增有效。')
p='source/'
add('Tslat/Advent-Of-Ascension',[p+'content/entity/boss/RockRiderEntity.java',p+'content/entity/boss/CottonCandorEntity.java',p+'content/entity/boss/HiveKingEntity.java'],'三完整文件均从开头/*到末尾*/全注释，检索命中不代表实际激活的Boss免疫。全部排除0，阶段/实体/投射物种类不加数。')
add('Tslat/Advent-Of-Ascension',[p+'content/entity/boss/tyrosaur/TyrosaurEntity.java',p+'integration/tes/TESIntegration.java',p+'integration/IntegrationManager.java'],'Tyrosaur full hurt/updateArmour/save/load和全类、TESIntegration全类及IntegrationManager已读。armor有值时预先按来源算armorDamage；发送灰色0xFFAAAAAA数字/crit调用和扣armor后仍super.hurt原amount，不是拒伤或BossImmune字样。不同armor stage才crumble声/尘。已有TES缓存包名net.tslat.tslatentitystatus而此集成net.tslat.tes，不能把不同版本接成已闭合S2C/文字消费链；暂0，未额外计装甲值/颜色/库包装。注册/对应版本消费者未闭合。')
(O/'uncredited-observations-20261028d.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
q=O/'helpers/herschel-immune/batch-020.json';d=json.loads(q.read_text());receipt={'batch_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'helper_credit':0,'promoted':0,'main_review_scope':'Read helper four semantic observations/missing-chain assertions, checked listed local availability; NOT a claim main independently reread all seventeen source files. No candidates promoted.','decisions':[{'helper_id':x['id'],'credit':0,'reason':x['semantic_dedup']} for x in d['rows']],'external_error':'Helper certificate failure preserved, no request to retry/disable verification; no main acquisition attempted for missing Aether files.'};(O/'HERSCHEL-020-REVIEW.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'support_groups':len(out['groups']),'helper020_promoted':0,'credit':0}))
