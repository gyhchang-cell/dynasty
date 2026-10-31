"""Main manual semantic review of native equipment control and owner admission; helper counts stay0."""
from ledger import B,O,record,verify
import json,hashlib
h=O/'helpers/herschel-immune'
def refs(n):
 d=json.loads((h/f'batch-{n:03}.json').read_text());return [(x['source_key'].split('/',1)[1],*x['lines']) for x in d['rows'][0]['source_refs']]
keys=[]
k='wizardry-native-direct-mainhand-disarm-admission-before-inventory-mutation';keys.append(k)
record(k,'Electroblob77/Wizardry',refs(22),
 'Spells真实注册Telekinesis→ItemWand.onItemRightClick/canCast/cast→SpellRay.cast/shootSpell射线→onEntityHit玩家且config允许且anchoring未活跃且主手非空→服务端entityDropItem并写掉落速度→两侧直接setHeldItem MAIN_HAND EMPTY；requiresPacket false，非维度施法包重放。拒绝false且onMiss false，未发spell.resist。',
 '一个真正直接库存控制生产点1。与已账anchoring位移拒绝共用资格函数但最终受控对象不同：此处将装备从玩家主手移走而非更改身体运动，拒绝必须早于掉落/清槽。与PNC首非空Mob槽按掉率可销毁不同，此处玩家主手drop先行、未检查返回null即解引用，因此异常分支不得推导已经清槽。完整拒绝路径无灰字/抵抗文本，不能套用GreaterTelekinesis文字。EntityItem吸引、右键方块、artefact事件/Baubles/热栏选择、Ray/Wand共享流程均支持0，不能按装备槽/包装另计。',
 'Boss最终拒控语义需放在实际控制提交之前，不能只在药水或位移门处理；静默false不自动等于免疫。灰字只从明确Boss拒绝原因发送。普通阴阳无灰字要求。',
 '主岗读取全部候选完整方法及实际注册、共有资格上下文；原版掉落/装备同步底层与射线引擎未运行，不证明任意Boss或运行时双端一致。灰字/像素未验，通用施法资源不计独立实现。','native_inventory_control_final_admission')
k='pnc-native-first-nonempty-slot-disarm-commit-independent-of-drop';keys.append(k)
record(k,'TeamPneumatic/pnc-repressurized',refs(23),
 '正式addDefaultEntries注册MobDisarm→原生key触发→EntityTracker/RenderEntityTarget.hack检查初始化和视向→C2S Start当前世界ID/upgrade可用→HackHandler服务器tick重取hackable并计时→alive且到阈值调用onHackFinished→首非空装备槽doDisarm→清槽后void完成流程track/Finish广播；客户端currentworld ID/hackable→client no-op完成体/完成声；HUD按本地hackTime与tracked显示完成。',
 '真实装备移除的最终生产点1：掉率只决定是否spawn及耐久扰动，不决定最后setItemSlot EMPTY，首非空返回true立即退出；不假定槽枚举顺序、不保证必有落地拾取物。与Wizardry玩家主手drop后清槽不同，这里服务器枚举Mob槽且掉落失败也清除。canHack初次/每大于60tick prune检查，缓存返回不逐次检查；最终doDisarm再检空槽，不检Boss/药水/HP。完成包只entityID无槽/结果，声/finished文字不能当已掉落收据。已有PNC持久hack拒传送/主人投射物生成门、共享缓存与收发/HUD均0额外。',
 '拒控必须在实际装备清空入口给出理由；通用operation-complete不能充当Boss免疫回执。按真实目标与原因限频，丢包/查不到目标应静默丢弃，不把失败当免疫。',
 '主岗完整读取候选全类、key/start/server tick/finish/cache/HUD包含方法和实际注册。现代NeoForge固定版本仅参考，不推导1.20.1可直接复制；引擎槽位同步/掉落事件/GUI实际渲染未执行，不能称网络或视觉验收通过。','native_equipment_control_commit_and_result_receipt_boundary')
k='pnc-native-owner-identity-qualified-permanent-retame-control';keys.append(k)
record(k,'TeamPneumatic/pnc-repressurized',refs(24),
 '注册TamableAnimal/Horse→同023原生key/C2S/服务器计时链→AbstractTameableHack.canHack以请求玩家UUID不等原owner为资格→最终onHackFinished服务器停止导航/清目标/设HP20/改ownerUUID/广播7/设tame；客户端Finish调用handleEntityEvent7，HUD用共用时间结果。',
 '直接永久改写归属及同主人资格拒绝政策1，区别Wizardry临时UUID控心/效果到期解除，也不是守卫旧账迁移。null或其他主人均满足不等，不称仅未驯服可用；本override未调用默认alive，但最终服务器tick另查alive。缓存会暂存资格，最终改owner前不重复检查身份；success7在server setTame之前且client finish也调用，无旧新owner结果负载。Horse/Tamable/Cat变体、成功7及共享hack全部合并，不按动物种类/包装加数。',
 '控制免疫覆盖直接归属变更的最终生产点而不只addEffect；缓存准入不代替最终确认，反馈应在明确拒绝后带目标与原因发出。普通阴阳不新增Boss灰字。',
 '主岗完整读取资格/两种完成体及023共用真实链、注册行；实际宠物AI/原版owner同步/双端粒子没运行，不能声称全部生物可控或Boss自然免疫。通用API和原版成功7消费底层只支持0。','native_owner_control_admission_and_permanent_commit')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch139-herschel022-024-native-final-control-producers','credited_chains':keys,'rationale':'Direct player mainhand drop-before-clear differs from body displacement and PNC Mob first-nonempty clear-independent-of-drop. Permanent owner overwrite with same-owner rejection differs from temporary effect-based mindcontrol. Shared anchoring/hacking and animal/slot variants0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
for n,k in zip((22,23,24),keys):
 f=h/f'batch-{n:03}.json';q={'helper_batch_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'promoted':1,'decisions':[{'helper_id':f'herschel-{n:03}-01','master_id':k,'credit':1}],'scope':'Main read actual complete candidate methods/native chain; semantic comparison manually made. Original helper credit remains0.'}
 if n==22:q['support_only']=[{'helper_id':'herschel-022-02','credit':0,'reason':'Explicit repeated013 Decoy family; additional renderer/radius observations not promoted; this batch did not claim full main reread of Decoy support.'}]
 (O/f'HERSCHEL-{n:03}-REVIEW.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
verify()
