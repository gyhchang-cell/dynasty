"""Primary review of Herschel043/044. One new semantic chain, never method-count credit."""
from ledger import B,O,R,record,verify
import json,hashlib,datetime

def helper_refs(number,expected):
 h=O/f'helpers/herschel-immune/batch-{number}.json';raw=h.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
 d=json.loads(raw);refs=[]
 for row in d['rows']:
  for x in row['source_refs']:
   key,rel=x['source_key'].split('/',1);root=B/'sources'/key;p=root/rel;data=p.read_bytes();meta=json.loads((root/'source.json').read_text());tree=json.loads((root/'tree.json').read_text());blobs={v['path']:v['sha'] for v in tree['tree'] if v['type']=='blob'}
   assert meta['commit']==tree['sha']==x['fixed_commit'];assert hashlib.sha256(data).hexdigest()==x['file_sha256'];assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blobs[rel]
   a,z=x['lines'];assert 1<=a<=z<=len(data.decode().splitlines());assert x['url']==f'https://github.com/{meta["repo"]}/blob/{meta["commit"]}/{rel}#L{a}-L{z}'
   refs.append({'path':str(p.relative_to(R)),'source_path':rel,'lines':[a,z],'file_sha256':x['file_sha256'],'url':x['url'],'method':x.get('method'),'research_credit':0})
 return d,refs
sha43='c3437333c758922a30a64371322aa69abde9f2ed7bfa36ea4e86f6867add52a9'
sha44='995012e22733dc121a527d26c5e8b2167bd989d35ca85fe8f237246b69cbca0a'
d43,refs43=helper_refs('043',sha43);d44,refs44=helper_refs('044',sha44)
(O/'HERSCHEL-043-REVIEW.json').write_text(json.dumps({'helper_file_sha256':sha43,'helper_original_credit':0,'main_review_new_effective':0,'state':'reviewed_support_only','main_all_listed_complete_methods_read':True,'main_full_potion_module_events_packets_and_commented_class_read':True,'source_refs':refs43,'observations':[
 'TimeSlow amplifier>=19时scale0，否则1/(amp+1.5)，absent-1。拟定LivingUpdate取消native更新前手动递减hurtTime/hurtResistantTime和本控制到期，server移除到期效果；实例handler是否实际注册仍未闭合，外部PotionMod未在缓存，不能宣称确定生效或死代码。静态自动subscriber不证明实例方法可达。',
 'CommonProxy.preInit实际注册ModuleEffectTimeSlow和CLIENT PacketFreezePlayer；skipTick按三个NBT键分间隔递减/取消/清键。全缓存rg只见包类与注册，未找到其实际生产调用，不把包字段当真实服务器冻结收据。',
 'onSpell替换event.spellData，但internalCastSpell在post后以原spell参数run，并未读取event替换值。ItemStaff自身timeScale0即PASS，不能据event setter声称所有施法均阻断。',
 'runOnStart先taxCaster再addPotionEffect且未确认最终准入；非活体/已有状态也true。cast成功或ignoreResults可发通用render包，consumer仅调模块render，不能从粒子推出状态准入或免疫原因。实际ModuleInstanceEffect adapter未缓存，完整绑定不声称已闭合。',
 'TimeLock整类处于块注释，排除。解除noAI未保存旧值且依赖解除时当前timeScale；未复现真实状态。'],
 'semantic_decision':'选择性冻结及保留自身截止期与既有Electroblob SlowTime家族相近；准入/渲染真假反例已有覆盖，且注册/adapter/packet producer存在缺口。整批0，不按33范围、方法、字段或作者区别凑数。','production_changes':False,'game_started':False,'compile_run':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n')
repo='AlexModGuy/AlexsMobs';root=B/'sources/AlexModGuy__AlexsMobs';p='src/main/java/com/github/alexthe666/alexsmobs/'
refs=[(x['source_path'],*x['lines']) for x in refs44]
for rel in [p+'entity/EntityMurmurHead.java',p+'entity/EntityMurmur.java',p+'client/render/RenderMurmurHead.java',p+'client/render/RenderMurmurBody.java']:
 refs.append((rel,1,len((root/rel).read_text().splitlines())))
k='alexsmobs-native-linked-body-refusal-falls-back-to-independent-head-damage'
record(k,repo,refs,
 '实际Mod/实体注册已在旧VoidWorm研究闭合；具体MURMUR/MURMUR_HEAD两个EntityType与两者属性注册、ClientProxy renderer绑定本批核对。body native tick发现head缺失即createHead构造独立Monster并调用addFreshEntity、写UUID与同步ID；head native hurt先自身isInvulnerableTo(super或IN_WALL)拒绝，再对解析到的body以同source半伤调用hurt。只有body true才返回true；body false或不存在则对独立head调用super.hurt原始全伤。服务端head tick维护链接、缺body>20tickdiscard；客户端parent hurt/death计时复制到head，head/neck渲染读head overlay，body临时fakehead另读body overlay。',
 '条件转交失败后改用另一实体结算，是一整条实际最终伤害准入家族1。与Hydra父级专用attackEntityFromPart统一结算、Endergetic弱点绕body override、随机child转伤且原父恒false、Wizardry附身无条件cancel、Bewitchment替身true才归零不同：同一source先试body半伤，明确false后再试head全伤。故body拒伤并不是整次目标免疫；head自身IN_WALL先行拒绝则不试body。两个均30最大血但独立Monster，不由倍率或两实体各加数。head有body引用时hurt/death sound为null，即使fallback可能本地承伤；client拷贝body计时也不能证明伤落在哪个血池。头攻击声在target.hurt前且忽略结果，只作0额外反例。',
 'Boss免疫字只能由明确最终拒控语义生产，委托接收者的false不等于整次事件最终拒绝；若有fallback要观察最终分支/归属。受击声有意抑制或红闪共享不能替代权威结果。不引入多部件机制或改变普通阴阳type9反馈，不借用模型资产。',
 '主岗全文501行Head、211行Body及两renderer和所有helper所列完整方法/具体注册语句已实际阅读，fixed09755dade2cfbdf14839e026d3af446f9d3ff843 tree/blob/SHA/URL已核。原版Monster/LivingEntity hurt、SynchedEntityData网络和具体pipeline继承内部未按该版本全展开；不声称实测HP或双端像素/音效。hurt对body仅非null，不验类型/互指UUID/alive/generation；tick另有EntityMurmur类型门，不能虚构所有入口校验。当前ServerLevel UUID/client本world整数查找，无维度epoch校验。body createHead忽略spawn boolean、错误类型非null未自动重建；缺body有20tick清理，不能说永久孤儿。拷贝计时/renderer早已VoidWorm覆盖0，不重复计数。','native_conditional_damage_delegation_and_final_refusal_semantics')
(O/'HERSCHEL-044-REVIEW.json').write_text(json.dumps({'helper_file_sha256':sha44,'helper_original_credit':0,'main_review_new_effective':1,'promoted_key':k,'main_full_head_body_and_renderers_read':True,'all_helper_reference_ranges_verified':len(refs44),'source_refs_in_promoted_chain':len(refs),'semantic_comparisons':['tf-hydra-root-and-part-authority','endergetic-native-exposed-egg-sack-route-bypasses-body-arrow-refusal','endergetic-native-random-child-damage-transfer-with-bidirectional-link-revalidation','wizardry-possession-native-damage-redirect-settlement','bewitchment-native-bound-living-substitute-success-gates-damage-nullification','vampirism-native-immobile-boss-vulnerability-proxy-versus-rejected-source','alexsmobs-native-multipart-hurt-receipt-target-pair-validation'],'semantic_decision':'只有转交body false之后改head full hurt的最终拒绝/回退政策新增1；身份/生命周期/叠加/声音包装合并0额外。','production_changes':False,'game_started':False,'compile_run':False,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n')
s=json.loads((O/'semantic-dedup.json').read_text());s['groups'].append({'family':'batch162-herschel044-conditional-head-body-refusal-fallback','credited_chains':[k],'rationale':'Conditional body hurt(false) retries original full damage on independently living head. Distinct final receiver policy from unconditional parent forwarding, accepted-only substitution and static weakpoint bypass; timer replay/render/registration/support0430.'});(O/'semantic-dedup.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');verify()
