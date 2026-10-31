from pathlib import Path
from datetime import datetime,timezone
import json,html
B=Path(__file__).resolve().parent; R=B.parent
now=datetime.now(timezone.utc).isoformat()
def save(name,data): (B/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
native=json.loads((B/'native-reconstruction.json').read_text())['files']
framework=json.loads((B/'framework-source-acquisition.json').read_text())
gecko=json.loads((B/'geckolib-source-provenance.json').read_text())
E=[]
def ev(id,claim,kind,version,name,ranges,qualification='源码静态核查；没有运行验证。'):
 if kind=='native':f=next(f for f in native if f['version']==version and Path(f['path']).name==name);local=f['reading_view']
 elif kind=='framework':f=next(f for f in framework if f['version']==version and Path(f['path']).name==name);local=f['local']
 else:f=next(f for f in gecko['files'] if Path(f['path']).name==name);local=f['path']
 E.append({'id':id,'claim':claim,'kind':kind,'version':version,'local':local,'read_ranges':ranges,'qualification':qualification,'independent_reference_credit':0})
ev('N01','原生CrossbowItem已具有Charged/compound弹仓、首枚消耗和多重射击额外复制、0/±10度及发射后清仓。这些共用子步骤不再拆为独立实现。','native','vanilla-mcp-1.20.1','CrossbowItem.java',[[45,284]])
ev('N02','getList要求列表元素类型匹配；非空compound列表用元素类型9读取时返回新的空ListTag。','native','neoforge-47.1.64','CompoundTag.java',[[394,409]])
ev('N03','原生clearChargedProjectiles也执行getList(ChargedProjectiles,9)→clear→put。因此Ars同写法会以空列表替换存储；不能将其误报为弹药复制。','native','vanilla-mcp-1.20.1','CrossbowItem.java',[[178,186]])
ev('N04','Ballista调用的Level版getEntityHitResult只在传入线段内挑最近实体，不替调用方再做方块截断。AABB.inflate是候选筛选，不等于额外命中距离。','native','forge-47.3.0','ProjectileUtil.java',[[89,110]])
ev('N05','Forge准确版本ServerLevel.addFreshEntity转addEntity：已移除或管理器拒绝均返回false；成功加入后同步onAddedToWorld。','native','forge-47.3.0','ServerLevel.java',[[813,815],[854,866]])
ev('N06','EntityJoinLevelEvent可取消；UUID重复也可令管理器拒绝添加。事件取消时不进入正常成功路径。','native','forge-47.3.0','PersistentEntitySectionManager.java',[[55,105]])
ev('N07','准确Forge事件声明取消后实体不加入Level，两逻辑侧可触发；不能把生成请求当作必定生成成功。','framework','forge-47.3.0','EntityJoinLevelEvent.java',[[16,64]])
ev('N08','耐久消费者在服务端/非创造分支伤害、达到阈值调用破损回调并shrink；返回void，不替发射调用方提供生成成功/回滚保证。','native','vanilla-mcp-1.20.1','ItemStack.java',[[301,347]])
ev('N09','Forge47.3.0耐久另经过Item.damageItem钩子；仍是破损消费者，不能以其调用推断addFreshEntity成功。','native','forge-47.3.0','ItemStack.java',[[330,377]])
ev('N10','原生箭的实体命中实际hurt、成功/失败分支和非穿透移除已定位；入地life达到1200会移除。这里只是Fabric实现所依赖的引擎基线，未生成实际Mixin合并结果。','native','vanilla-mcp-1.20.1','AbstractArrow.java',[[259,386],[390,488]])
ev('N11','Neo版原生碰撞循环在ProjectileImpactEvent被取消时break；穿透命中在hurt之前登记实体ID，后续findHitEntity会排除已登记目标。','native','neoforge-47.1.64','AbstractArrow.java',[[174,201],[286,391],[422,427]])
ev('N12','Ars自有tick的取消分支未采用父类break。若监听器持续取消同一可命中目标，忽略集合也未更新，静态上可能反复查询该目标；普通已处理命中则会通过父类登记ID推进。不是无条件死循环或实机复现。','native','neoforge-47.1.64','AbstractArrow.java',[[174,201],[286,310],[422,427]],'须与Ars EntitySpellArrow自有tick联合阅读；有条件风险，未运行复现。')
ev('N13','准确Neo事件工厂onProjectileImpact返回事件总线取消结果；onArrowLoose被取消返回-1，否则返回charge。','framework','neoforge-47.1.64','ForgeEventFactory.java',[[673,693]])
ev('N14','ProjectileImpactEvent取消只阻止该次impact处理，后续如何处理由模组负责；不能拿Forge47.3.0新版同名事件替代Neo47.1.64接口。','framework','neoforge-47.1.64','ProjectileImpactEvent.java',[[1,45]])
ev('N15','原生AbstractArrow持久化life/ground/pickup/damage/PierceLevel/声音/crossbow，父Projectile另存Owner/LeftOwner/HasBeenShot；这些不包含Ars resolver/pierceLeft/lastHit。','native','neoforge-47.1.64','AbstractArrow.java',[[430,468]])
ev('N16','Projectile持有ownerUUID/缓存并可按ServerLevel查找；tick负责leftOwner过渡。Ars覆写tick且不调用super，不能自动套用父类tick生命周期与TTL。','native','neoforge-47.1.64','Projectile.java',[[27,99],[170,176]])
ev('N17','Arrow没有onHitEntity覆写，实体命中落到AbstractArrow；Arrow追加药水和NBT。原版MCP Arrow阅读副本与本Neo副本逐字节相同，仅作同源佐证，不计第二次参考。','native','neoforge-47.1.64','Arrow.java',[[1,226]])
ev('N18','普通LivingEntity释放通过实际useItem.releaseUsing后停止并清空使用状态；这不证明Fabric网络包排序、其他Mixin或左右手HUD正确。','native','vanilla-mcp-1.20.1','LivingEntity.java',[[2802,2849],[2940,3001]])
ev('N19','Neo释放路径可经ForgeEventFactory.onUseItemStop阻止releaseUsing，随后停止使用；Ars自有charged与弹仓的回滚仍须看自身调用。','native','neoforge-47.1.64','LivingEntity.java',[[3044,3069]])
ev('N20','DamageSource三参构造第一个Entity是directEntity，第二个是causingEntity；getDirectEntity/getEntity各返回对应字段。只闭合字段语义，不证明伤害标签和最终数值。','native','neoforge-47.1.64','DamageSource.java',[[14,66]])
ev('G01','GeoItemRenderer.actualRender先handleAnimations再递归输出模型；GeoRenderer.defaultRender在输出、层与post之后才调用renderFinal。Ars renderFinal改弩臂不会修改已经输出的该帧顶点。','gecko','4.4.4','GeoRenderer.java',[[120,152],[172,180],[237,315]])
ev('G02','具体item父类以当前栈提供实例ID和数据，在actuallyRender中处理动画后进入递归；不能仅凭子类名字声称修复持握。','gecko','4.4.4','GeoItemRenderer.java',[[167,183],[219,255]])
ev('G03','GeoModel缓存baked模型，handleAnimations可能对同实例同时间直接返回；否则经过AnimationProcessor。没有每次renderFinal后自动统一复位的接口保证。','gecko','4.4.4','GeoModel.java',[[82,94],[133,168]])
ev('G04','AnimationProcessor仅在rotationChanged为false时插值复位，并在tickAnimation末重置改变标志；setRotY会重新置标志。因此存在后续绘制/多次渲染时序问题需要实机检查，不能断言永久不复位。','gecko','4.4.4','AnimationProcessor.java',[[71,107],[130,209]])
ev('G05','GeoBone.setRotX/Y/Z写入值并标记rotationChanged，resetStateChanges清标志；这是G04时序判断的实际消费者。','gecko','4.4.4','GeoBone.java',[[133,152],[254,299]])
reports=['batch-06/ballista-world-emplacement.json','batch-06/ars-spell-crossbow-stored-volley.json','batch-07/crossbow-multicharge-lifo.json']
old=[json.loads((R/p).read_text()) for p in reports]
assert sum(len(d['evidence']) for d in old)==102
save('native-consumer-review.json',{'updated_utc':now,'status':'STATIC_CONTEXT_REVIEW_NOT_RUNTIME','evidence':E,'prior_scope_evidence_records':102,'prior_scope_evidence_not_semantic_credit':True,'new_source_studies':0,'new_accepted_gate_credit':0,'method':'官方准确版本source/userdev归档；复用现有MCP源码基底并精确应用补丁，再保留SRG与阅读映射副本。源代码仅提取阅读，没有执行。','limitations':['MCP基底未独立重新生成，不等于完整运行时。','未标阅读行号的还原文件仍未研究。','PNG未实际看过，不能计模型+贴图视觉参考。','多次hurt调用不等于两倍伤害，未穷尽无敌帧/外部事件。']})
def prior(report,ids):return {'report':'../'+report,'evidence_ids':ids}
def proposal(id,title,scope,report,ids,signature,fail,pending,context=False):
 d=old[reports.index(report)]
 return {'id':id,'title':title,'scope':scope,'status':'ADJACENT_CONTEXT_NOT_DIRECT_SCOPE_PROPOSAL' if context else 'PROPOSED_PENDING_INDEPENDENT_AND_GLOBAL_SEMANTIC_REVIEW','repo':d['repo'],'commit':d['commit'],'semantic_signature':signature,'source_evidence':prior(report,ids),'native_evidence':fail,'pending':pending,'new_accepted_gate_credit':0,'direct_proposed_units_max':0 if context else 1,'human_creature_model_texture_reference_credit':0}
P=[proposal('P-BALLISTA','世界施工弩：分次拉弦、装弹、控制与损坏退出','siege_crossbow',reports[0],['ballista-world-emplacement-'+str(i).zfill(2) for i in [4,5,6,8,9,11,13,14,16,17,18,19,20,21,23]],'world_emplacement|construction17|draw_pulses20x.02|load_entity|controller_uuid|launch8|damage_break_recover',['N04','N05','N06','N07','N09'],['跨项目/整合包同源包装全局去重及独立验收。','实际磁盘重载顺序、owner恢复与非装填飞行箭清理；不以onAdded推定全部成立。','原segment穿墙后实体查询及owner最先相交的实际场景未复现。','PNG/真实游戏持握与光照均未验收。']),
proposal('P-MULTICHARGE','原生弩续装：6/10弹仓、LIFO每次用一枚','repeating_crossbow',reports[2],['CM-'+str(i).zfill(2) for i in [3,4,6,8,10,11,13,14,15,16,18,19,20,21,22,23,24,27,29,30]],'vanilla_crossbow_mixin|sneak_recharge|capacity6or10|append|shoot_last|decrement_one|keep_charged_while_nonempty',['N01','N08','N10','N17','N18'],['跨包装和已有多装填原生弩家族全局语义去重与独立验收。','Fabric实际Mixin合并/冲突、原生网络与实际客户端双侧行为未验证。','混弹速度、取消续装锁仓、空列表不一致是静态边界，未实机。','客户端HUD只读mainHand与NBT空值边界未实际验收。','本批闭合的是原生箭分支；原生烟火爆炸消费者未读，不能宣称所有弹种世界作用均闭合。']),
proposal('C-ARS','装填扣魔的法术储存齐射：仅邻接上下文','repeating_crossbow',reports[1],['ars-spell-crossbow-stored-volley-'+str(i).zfill(2) for i in [3,5,6,7,8,9,10,11,21,27,28,29,30,31,32,35,39,40,41,42]],'spell_crossbow|pay_on_load|stored_volley_one_call|custom_arrow_resolver|post_draw_bone_changes',['N02','N03','N11','N12','N13','N14','N15','N16','N17','N19','N20','G01','G02','G03','G04','G05'],['储存齐射不是顺序连发；不作为连发弩范围的直接候选。','全局相关性/同族验收待外部决定，本地不自评通过。','impact持续取消条件风险、跨手工具语义、渲染复位与重载法术状态未运行验证。'],True)]
D=[
 {'group':'原生Charged与ChargedProjectiles协议','members':['Ars','Multicharge','vanilla'],'decision':'共用基础协议，不按字段/每枚弹药拆信用。'},
 {'group':'消耗首枚、额外弹药复制与0/±10多重射击','members':['Ars','Multicharge','vanilla'],'decision':'同源原生子机制，0新增独立案例。Ars glyph增加齐射数量不按glyph拆计。'},
 {'group':'Arrow/Firework弹种、pierce/crit、耐久、声音、criterion/stat','members':['Ars','Multicharge','vanilla'],'decision':'消费者或配置，不各自拆族。'},
 {'group':'Ars储存法术齐射','members':['Ars'],'decision':'一个源码家族，仅邻接上下文；不是隔tick/逐次连发。'},
 {'group':'Multicharge逐次LIFO弹仓','members':['CrossbowMixin','Storage enchant','HUD','firework predicate'],'decision':'一个整合家族；附魔/槽数/显示不是新族。'},
 {'group':'NewCrossbow旧类','members':['NewCrossbow.java'],'decision':'已选入口与全部自有Java无构造/注册消费，不能把未生效旧齐射另计。'},
 {'group':'Ballista施工拉弦装箭瞄准拆除','members':['Ballista','BallistaSpawnItem','BallistaBolt','renderers'],'decision':'一个世界器械操作链；阶段/箭/渲染不各拆族。'},
 {'group':'同一实现的整合包/平台包装与版本','members':['三个固定提交的可能下游包装'],'decision':'未完成全局跨包装清单核对；本地不同repo≠自动独立验收。'}]
scopes=['repeating_crossbow','siege_crossbow','rope_dart','meteor_hammer','mandarin_duck_axe','flying_claw']
save('semantic-review-proposals.json',{'updated_utc':now,'status':'PROPOSAL_ONLY_NO_SELF_ACCEPTANCE','earlier_evidence_records':102,'evidence_records_are_not_reference_units':True,'reviewed_source_families':3,'direct_proposed_units_max':2,'adjacent_context_families':1,'new_accepted_gate_credit':0,'global_accepted_totals':None,'dedup_groups':D,'proposals':P,'scope_matrix':[{'scope':s,'direct_proposed_units_max':int(s in scopes[:2]),'accepted_new_gate_credit':0,'required':1000,'global_accepted_total':None,'gate_met':False} for s in scopes],'gate_action':'每范围1000未达到；不制作、不修改已认可模型、不操作共享Jar。'})
progress={'updated_utc':now,'batch':'batch-08','status':'REVIEW_PACKET_SAVED_PENDING_INDEPENDENT_ACCEPTANCE','existing_family_context_extensions':3,'new_source_studies':0,'prior_evidence_records':102,'reviewed_source_families':3,'direct_proposed_units_max':2,'adjacent_context_families':1,'new_accepted_gate_credit':0,'global_accepted_totals':None,'all_six_1000_gates_met':False,'human_creature_reference_credit':0,'production_changes':False,'shared_jar_touched':False,'java_build_game_started':False,'ui_focus_sound_brightness_or_wake_changed':False,'prompts_deleted':False,'published':False,'deadline':'2026-10-31T09:00:00+08:00','next':['独立审查P-BALLISTA与P-MULTICHARGE；全局语义去重未完成，不自行通过。','Ars留邻接上下文，不向连发弩1000门槛加分。','必要未闭合生命周期/渲染边界见提案pending；不为充数重复研究本族。','09:00保存未完成并停止该夜间分工；恢复前检查期限。']}
save('progress.json',progress)
save('checkpoint-20261031.json',{'saved_utc':now,'scope':'准确引擎消费者与三链局部语义去重；没有新增武器或生物制作。','completed':['准确Forge47.3.0与Neo47.1.64补丁上下文匹配及选定消费者阅读。','Gecko4.4.4官方源码父类与复位实际消费阅读。','102条历史证据按机制家族局部合并；2直接提案＋1邻接上下文，0验收信用。'],'unfinished':[p['pending'] for p in P],'night_stop_deadline':progress['deadline'],'status':'SAVED_UNFINISHED_PENDING_INDEPENDENT_REVIEW'})
esc=html.escape
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第八批 · 消费者与语义去重</title><style>body{font:16px/1.7 system-ui;max-width:1050px;margin:35px auto;padding:0 20px;background:#f5f3eb;color:#28372f}article{background:white;padding:20px;margin:20px 0;border-left:4px solid #6b8c79}a{color:#285e87}code{overflow-wrap:anywhere}li{margin:7px 0}.pending{color:#765b22}</style><h1>第八批：消费者与局部语义去重</h1><p><b>102条历史证据 ≠ 102个参考。</b>本批补读3个既有家族，提出至多2项直接候选、保留1项邻接上下文。新增独立验收信用0，各范围1000门槛仍未达到。</p><p>这是源码研究，未查看PNG，不是生物建模/贴图参考；没有生产资源、共享Jar、Java/游戏、声音或焦点操作。</p><p><a href="../index.html">总断点</a> · <a href="semantic-review-proposals.json">待审提案与去重</a> · <a href="native-consumer-review.json">消费者证据</a> · <a href="progress.json">进度</a> · <a href="local-verification.json">本地静态核查</a></p>']
for p in P:
 parts+=['<article><h2>'+esc(p['title'])+'</h2><p class="pending">'+esc(p['status'])+'</p><p><code>'+esc(p['repo']+'@'+p['commit'])+'</code></p><p>主要机制：<code>'+esc(p['semantic_signature'])+'</code></p><p><a href="'+esc(p['source_evidence']['report'])+'">原始选定实现与逐条证据</a>；新补读消费者：'+esc(', '.join(p['native_evidence']))+'</p><ul>'+''.join('<li>'+esc(s)+'</li>' for s in p['pending'])+'</ul></article>']
parts+=['<h2>实际修正的判断</h2><ul><li>Ars的列表元素类型差异不是弹药复制：返回空列表后会写回。</li><li>普通穿透已处理命中会登记目标；只有持续取消impact等条件下才保留循环风险，未实机。</li><li>Ars覆写tick不调用super，不能自动继承原生入地TTL与leftOwner更新。</li><li>renderFinal在该帧顶点输出后才执行；存在标记/插值复位路径，不能称永久残留。</li><li>生成调用可能失败；耐久、弹药消耗与实体加入不是原子事务，不冒称已复现丢弹。</li></ul><h2>新补读的精确位置</h2>']
for e in E:
 parts+=['<article id="'+e['id']+'"><b>'+e['id']+'</b> '+esc(e['claim'])+'<p><a href="'+esc(e['local'])+'">'+esc(e['version']+' / '+Path(e['local']).name)+'</a> · '+esc(str(e['read_ranges']))+'</p><small>'+esc(e['qualification'])+'</small></article>']
parts+=['<p>未完成：全局语义去重、独立验收、实际运行边界。09:00截止前保存，不以文档条数代替参考数量。</p></html>']
(B/'index.html').write_text('\n'.join(parts))
print('Saved',len(E),'context evidence records; 2 direct proposals + 1 adjacent context; accepted credit 0.')
