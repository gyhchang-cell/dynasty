from pathlib import Path
from datetime import datetime, timezone
import json, html
B=Path(__file__).resolve().parent
R=B.parent
manifest=json.loads((B/'selected-source-acquisition.json').read_text())
now=datetime.now(timezone.utc).isoformat()

def record(name,repo,commit,version,scope,conclusion,pending):
 return dict(id=name,updated_utc=now,status='SELECTED_SOURCE_CHAIN_READ_INDEPENDENT_ACCEPTANCE_PENDING',repo=repo,commit=commit,version=version,relevant_scopes=scope,new_local_source_studies=1,proposed_independent_units_max=1,new_accepted_gate_credit=0,human_creature_model_texture_reference_credit=0,semantic_counting='整个选定机制家族最多1候选；版本、方法、弹药、左右手、阶段、配套类、同族包装不重复计数。尚未执行全局独立验收。',conclusion=conclusion,evidence=[],pending=pending)
ball=record('ballista-world-emplacement','dercodeKoenig/marvins-minecraft-mods','20d02ec1300ff6011683d9fd43ef76fd47256234',dict(minecraft='1.20.1',forge='47.3.0',module='aw_vehicles',declared_mod_version='1.0.6',java='17'),['siege_crossbow'],'世界器械：施工→分次拉弦→独立箭实体装填→UUID控制瞄准→释放箭实体→损坏/维修/拆除。不是手持连弩，不拆成多个案例。',[
 '正常玩家交互可达性、原生ProjectileUtil最近碰撞筛选、addFreshEntity回调顺序和失败语义未闭合。',
 '区块卸载/重载的双向onAddedToWorld重关联，控制者死亡/断线/跨维，已发射箭实体外部清理和原版Entity存档仍待核实。',
 '点形状检查与未截断entity射线的先后仅为源码观察，不据此宣称穿墙实测或完整伤害漏洞。',
 'PNG未下载/查看；几何与渲染代码不是生物模型+PNG视觉参考。未运行原作者Jar或Dynasty游戏。',
 '未检验跨整合包包装的全局语义重复，独立验收信用0；本地研究不证明1000门槛。'])
ars=record('ars-spell-crossbow-stored-volley','baileyholl/Ars-Nouveau','2c74064bc753600d9b6600f102f8163e2d6764dd',dict(minecraft='1.20.1',declared_mod_version='4.12.7',java='17',geckolib='4.4.4',forge_property='47.1.64',actual_build_coordinate='net.neoforged:forge:1.20.1-47.1.64',build_note='读取Gradle声明，不等于验证目标Forge运行兼容；未安装或升级依赖。'),['repeating_crossbow'],'装填时付费并存储齐射；选定普通ARROW＋法术Harm路径读至Entity.hurt及箭移除。非定时逐发连弩；只能作为装填/齐射状态管理的相关案例。',[
 'GeckoLib4.4.4父类实际渲染调用顺序、原版CrossbowItem装填计时、NBT getList元素类型行为、AbstractArrow碰撞/存档/伤害父类和事件监听仍未全读。',
 '取消发射后外层仍取消charged、清理列表9/10类型差异、多个resolve和hurt调用点均为控制流观察；不能直接宣称复制弹药、双倍伤害或已复现实机缺陷。',
 '普通ARROW＋Harm为选定路径；SpellArrow特殊弹药类虽已保存但未逐行研究，其他glyph/毒/烟火分支、配置和扩展监听未完整闭合。',
 '法术上下文的主手引用与实际持弩手不同，渲染读取本地玩家，FP右手粒子不代表左手/远端/第三人称效果。',
 '飞行实体未声明自身resolver/pierceLeft/lastHit的NBT覆盖；不能由此推断原版所有实体字段都不保存，读档效果仍待实机。',
 '实际PNG未查看，不计生物模型＋贴图参考；无构建、Jar检查、Java或游戏。',
 '全局语义去重及独立验收待完成，0信用；不是把一个法术框架的glyph拆成很多实现。'])

def ev(doc,stage,claim,path,*ranges):
 row=next(x for x in manifest if x['repo']==doc['repo'] and x['path']==path)
 doc['evidence'].append(dict(id=f"{doc['id']}-{len(doc['evidence'])+1:02}",stage=stage,claim=claim,source_path=path,local=str(Path(row['local']).resolve().relative_to(B)),fixed_url=f"https://github.com/{row['repo']}/blob/{row['commit']}/{path}#L{ranges[0][0]}",read_ranges=[list(x) for x in ranges]))

def be(stage,claim,file,*ranges):ev(ball,stage,claim,'aw_vehicles/'+file,*ranges)
def bj(stage,claim,file,*ranges):be(stage,claim,'src/main/java/Vehicles/'+file,*ranges)
def ae(stage,claim,file,*ranges):ev(ars,stage,claim,file,*ranges)
def aj(stage,claim,file,*ranges):ae(stage,claim,'src/main/java/com/hollingsworth/arsnouveau/'+file,*ranges)

be('version','MC1.20.1、Forge47.3.0、模块1.0.6；构建Java17。','gradle.properties',(1,60))
be('version','Java和ForgeGradle声明是源码配置，不是发行Jar或兼容性验收。','build.gradle',(1,211))
be('version','模组元数据与依赖范围保存固定版本。','src/main/resources/META-INF/mods.toml',(1,70))
bj('entry','构造器注册实体/物品/声音与客户端渲染；没有本模块独立交互C2S包。','Main.java',(18,50))
bj('entry','Ballista和Bolt是MISC实体，尺寸分别1×2及0.25²，存在生成/修复物品。','Registry.java',(18,66))
bj('entry','生成物品恢复施工/损坏标签后addFreshEntity并消耗；本方法无显式服务端守卫且忽略生成返回值。未据此宣称双生实测。','BallistaSpawnItem.java',(19,39))
bj('persistence','物品标签copy及异常回退，与器械存档通路对应。','Utils.java',(1,21))
bj('state','同步拉弦/施工/损坏；控制者UUID、装填箭引用、重载余tick未作同等同步声明；life用于破坏概率，不是普通扣血生命池。','Ballista.java',(29,61))
bj('association','器械onAdded查询自身AABB内未shotEnd的箭，引用并设owner/无重力/位置；另由箭onAdded反向联系。无持久箭UUID键。','Ballista.java',(64,93))
bj('association','箭onAdded在重叠器械中回调，不同加载顺序或旧实体误关联仍未实测。','BallistaBolt.java',(27,68))
bj('state_consumer','server恢复负拉弦；每次20tick拉弦脉冲+0.02/tick，非20tick完整装填。UUID控制者为空或距离>4清除，否则yaw/pitch限速追随。','Ballista.java',(96,145))
bj('client_state','客户端插值拉弦与角度；draw<=0驱动afterShoot计时，不是独立唯一发射事件。','Ballista.java',(146,184))
bj('fire','施工17且未损坏才使用；满弦有箭以look+散布归一化×8发射、恢复重力、解除装填引用、draw=-1。owner仍是器械，不是玩家。','Ballista.java',(212,224))
bj('load_and_aim','满弦无箭先扣1弹药再创建实体；空手点击拉弦每次20tick；Shift设置或解除控制者UUID，可以覆盖另一人。','Ballista.java',(225,245))
bj('construction_and_repair','锤施工至17；修复物品清除损坏并消耗。不得把施工阶段作为多个独立武器研究。','Ballista.java',(246,273))
bj('exit','拆除先施工减1并掉落/移除当前装填箭，至0掉落带状态生成物品并discard；只针对当前装填引用。','Ballista.java',(191,210))
bj('failure','hurt随机amount/life判坏，清控制和当前装填箭；不扣普通HP、不主动清reloadTicksRemaining。已射箭不在当前bolt引用内。','Ballista.java',(276,289))
bj('persistence','自有NBT仅拉弦/施工/损坏；控制UUID/重载剩余/箭UUID不在这些写读字段中。无自己的remove覆盖。','Ballista.java',(291,334))
bj('world_consumer','server点形状检查可设shotEnd；blockclip命中先停位置，但该分支不直接设shotEnd；entity检测仍使用原segment。','BallistaBolt.java',(69,119))
bj('world_consumer','非owner且owner存在，未shotEnd/未命中过才hurt50；命中集合在hurt之前更新、声音不取决hurt结果。inflate10是宽相包围盒，不是10格额外攻击距离。','BallistaBolt.java',(119,132))
bj('exit','飞行重力和位置推进；在地超过6000tick本类discard，未看到独立空中TTL。不能由本类断言外部无清理。','BallistaBolt.java',(134,183))
bj('persistence','箭自己的NBT仅shotEnd；owner/hit集合/ground计数未自有保存；原版Motion等基础字段尚未审完。','BallistaBolt.java',(186,196))
bj('render_consumer','拉弦实际驱动臂、弦、扳机，构建隐藏及破坏姿态；最后ModelPart.render使用packedLight。','BallistaRenderer.java',(29,143))
bj('render_resource','实际纹理资源路径及256²几何层；未查看PNG，不当视觉参考。','BallistaRenderer.java',(147,476))
bj('render_consumer','箭插值平移/朝向、scale0.2与实际ModelPart.render，指定192×36层及arrow_wood纹理。','BallistaBoltRenderer.java',(29,228))

ae('version','版本属性MC1.20.1、forge47.1.64、Gecko4.4.4；Gradle实际使用net.neoforged:forge，未混称已验证Forge运行。','gradle.properties',(1,11))
ae('version','mod4.12.7、Java17、Parchment及实际依赖坐标；本文件只读1–195，不宣称全文审完。','build.gradle',(1,195))
aj('entry','物品DeferredRegister与spell_crossbow注册及通用包装；未审完整其他物品表。','setup/registry/ItemsRegistry.java',(60,60),(220,227))
aj('entry','注册名常量spell_crossbow。','common/lib/LibItemNames.java',(126,126))
aj('entry','use使用实际hand物品；charged时调用齐射后无条件取消charged；否则有弹药startUsingItem。','common/items/SpellCrossbow.java',(50,91))
aj('resource_gate','装填先解析实际crossbow栈，modifier hand却写MAIN_HAND。玩家canCast通过或非玩家才先expendMana，失败则仍可装非spell弹；分裂增加齐射数量。','common/items/SpellCrossbow.java',(93,127))
aj('resource_consumer','首枚非创造弹药split1，额外复制；随后追加ChargedProjectiles compound与整栈isSpell。若循环失败，本方法无前面资源/entries回滚。','common/items/SpellCrossbow.java',(129,162))
aj('persistence','读列表元素类型10；clear调用getList类型9再clear/put。记录字面差异，不在未读native getList时宣称弹药复制。','common/items/SpellCrossbow.java',(164,188))
aj('fire','shootOne限server：普通ARROW+isSpell替换自定义箭，真实瞄准/射速、持久消耗、addFreshEntity及声音。未检验生成失败补偿。','common/items/SpellCrossbow.java',(196,235))
aj('cancel_and_volley','Forge onArrowLoose取消可早退；否则一次遍历存储箭并设0/-10/+10等角，最后onCrossbowShot清列表。不是隔tick连发。取消与外use取消charged合看。','common/items/SpellCrossbow.java',(254,289),(56,64))
aj('ownership','buildSpellArrow resolver上下文工具取shooter.getMainHandItem，而非参数actual crossbow；标注副手语义边界，不断言全副手不可用。','common/items/SpellCrossbow.java',(296,301))
aj('spell_entry','抄写排除castmethod，setSpell前插MethodProjectile，保留自身折扣；初始化专用物品renderer、无动画controller。','common/items/SpellCrossbow.java',(310,365))
aj('caster_binding','ICasterTool实际构造SpellCaster(stack)并store，CasterUtil分派ICasterTool。','api/item/ICasterTool.java',(84,101))
aj('caster_binding','普通caster回退，不当独立机制计数。','api/util/CasterUtil.java',(1,16))
aj('persistence','SpellCaster从ItemStack caster tag读取spell，写回ars_nouveau:caster；法术序列化按glyph注册ID。','api/spell/SpellCaster.java',(23,37),(164,221))
aj('persistence','法术首castmethod/相邻augments规则与序列化，非把每个glyph拆案例。','api/spell/Spell.java',(71,122),(128,159),(186,187))
aj('event_boundary','generic castSpell事件路径不等于crossbow直接调用canCast/expend的路径，避免把未经过的事件强加进来。','api/spell/ISpellCaster.java',(122,171))
aj('context','context复制casterTool并支持cancel/delay/reset；reset会取消cancel标记；owner或FakePlayer回退是活引用，不是持久UUID协议。','api/spell/SpellContext.java',(57,60),(87,104),(130,164),(170,170),(201,235),(257,271))
aj('caster_owner','LivingCaster.from实际Player用PlayerCaster，其他living用包装；不据此宣称非玩家也总有mana capability。','api/spell/wrapped_caster/LivingCaster.java',(1,51))
aj('caster_owner','PlayerCaster持有玩家引用；不是单独武器案例。','api/spell/wrapped_caster/PlayerCaster.java',(1,37))
aj('resource_consumer','canCast检查valid与mana/creative，expend经事件调整cost再cap.removeMana；足量检查创造豁免不等于移除方法也豁免。','api/spell/SpellResolver.java',(54,83),(197,210))
aj('resource_provider','cap获取，attach事件只给Player；clone revive/copy/invalidate。login/respawn维度同步PLAYER_DATA_CAP不证明本处mana同步。','setup/registry/CapabilityRegistry.java',(44,48),(75,110))
aj('resource_provider','provider持有ManaCap，getCapability提供LazyOptional并转交NBT；本文件有invalidate方法但attach未在此注册invalidation listener，生命周期外部边界保留。','common/capability/ManaCapAttacher.java',(18,51))
aj('resource_consumer','ManaCap set夹0/max、remove减法、保存当前上限/bonus/tier；这是实际资源消费者。','common/capability/ManaCap.java',(27,64),(88,104))
aj('resource_api','接口只声明资源操作和NBT，不把接口当作已执行扣费。','api/mana/IManaCap.java',(1,33))
aj('spawn_registration','自定义实体DeferredRegister及spell箭client factory/追踪；尚未审vanilla spawn包处理。','setup/registry/ModEntities.java',(38,44),(123,126))
aj('world_consumer','自有tick不super.tick；先block clip截断，再实体筛选与Forge impact可取消，手写物理推进及客户端trail。','common/entity/EntitySpellArrow.java',(33,191))
aj('effect_dispatch','onHit先resolve，再ENTITY或新BLOCK分支再次resolve；重复block仍走首resolve。记录调用点，不当成伤害倍数结论。','common/entity/EntitySpellArrow.java',(277,297))
aj('damage_consumer','onHitEntity先父方法后自己的hurt；hurt成功才击退/附魔等，失败恢复着火tick。原生无敌帧/事件未全读，不宣称两倍伤害。','common/entity/EntitySpellArrow.java',(209,266))
aj('exit','pierceLeft先减至<0再server广播3并DISCARDED；getPierceLevel固定12；不是固定12次真实有效伤害。','common/entity/EntitySpellArrow.java',(193,207))
aj('spawn_and_save_boundary','getType/Forge spawn packet/custom factory；本类全文未实现resolver/pierceLeft/lastHit自有NBT覆盖，原生箭基础NBT待核实。','common/entity/EntitySpellArrow.java',(1,318))
aj('effect_consumer','resolve重设context→Pre→循环可用effect→effectPre→实际effect.onResolve→Post；此处没有再次expendMana。','api/spell/SpellResolver.java',(150,195))
aj('effect_consumer','AbstractEffect分派Entity/Block及Player/FakePlayer上下文。','api/spell/AbstractEffect.java',(52,64),(90,92))
aj('harm','Harm对非Item目标按配置/增幅构造伤害；duration>0走poison，选定的是直接Harm分支。配置默认不是实机固定伤害。','common/spell/effect/EffectHarm.java',(27,94))
aj('damage_consumer','排除dead/allied；SpellDamagePre取消/<=0退出，实际entity.hurt失败退出；成功设置lastHurtMob及Post。','api/spell/IDamageEffect.java',(21,22),(36,82),(94,98))
aj('damage_source','DamageUtil从registry取damage type；单实体SpellDamageSource将其作为父构造两个entity参数；完整native DamageSource字段语义未审，不倒置命名推断。','api/util/DamageUtil.java',(18,54))
aj('damage_source','generic spell damage registry key为ars_nouveau:spell；未打开其数据JSON，不杜撰护甲/魔法标签。','setup/registry/DamageTypesRegistry.java',(1,19))
aj('stats','builder从augments、装备/Curios和SpellModifierEvent构造stats；不将默认值当所有扩展最终数值。','api/spell/SpellStats.java',(138,195))
aj('render_binding','物品renderer资源路径、gem用输入色其他white；actual stack颜色、alpha.75与translucent。','client/renderer/item/SpellCrossbowRenderer.java',(25,38),(116,128))
aj('render_consumer','renderFinal读取Minecraft本地玩家使用计时，驱动左右bow与gem；本方法无完整else复位，是否影响本帧须读Gecko父类。','client/renderer/item/SpellCrossbowRenderer.java',(41,65))
aj('render_hand','FP_RIGHT且未暂停才计算聚集粒子；不能冒称FP_LEFT/TP/远端相同效果。','client/renderer/item/SpellCrossbowRenderer.java',(69,113))
aj('render_parent_boundary','FixedGeoItemRenderer只是继承GeoItemRenderer并传model；没有本地自有修复逻辑；Gecko父层未读。','client/renderer/item/FixedGeoItemRenderer.java',(1,13))
aj('render_resource','ANGeoModel返回构造注入资源路径，未自动改到其他PNG。','client/renderer/ANGeoModel.java',(1,36))
ae('render_resource','geo声明32²，gem/bow_right/base/bow_left实际存在；原始逐面UV及负uv_size仅声明读，不是PNG视觉验收。','src/main/resources/assets/ars_nouveau/geo/spell_crossbow.geo.json',(1,235))
ae('render_resource','builtin/entity物品JSON与ground/gui/head/fixed变换，没有显式FP/TP项；父renderer仍可能变换，不能推断实际持握为单位矩阵。','src/main/resources/assets/ars_nouveau/models/item/spell_crossbow.json',(1,53))
aj('projectile_render_binding','CLIENT MOD总线RegisterRenderers将spell箭绑定TippableArrowRenderer；引擎renderer内部未读，不能称粒子就是全部箭渲染。','client/registry/ClientHandler.java',(61,66),(123,129))

# Human-reviewed ranges: full only when actually read, never equate acquisition/hash with review.
partial={
 'build.gradle': [[1,195]],
 'src/main/java/com/hollingsworth/arsnouveau/setup/registry/ItemsRegistry.java':[[60,60],[121,123],[210,275]],
 'src/main/java/com/hollingsworth/arsnouveau/setup/registry/ModEntities.java':[[35,45],[75,140],[310,365]],
 'src/main/java/com/hollingsworth/arsnouveau/common/lib/LibItemNames.java':[[126,126]],
 'src/main/java/com/hollingsworth/arsnouveau/client/registry/ClientHandler.java':[[54,78],[116,140]],
 'src/main/java/com/hollingsworth/arsnouveau/common/items/SpellArrow.java':[]
}
for row in manifest:
 ranges=partial.get(row['path'],[[1,row['lines']]]) if row['repo']==ars['repo'] else [[1,row['lines']]]
 row['reviewed_ranges']=ranges
 row['read_status']='FULL_READ' if ranges==[[1,row['lines']]] else ('SELECTED_RANGES_READ' if ranges else 'ACQUIRED_NOT_REVIEWED')
 row['counting_note']='配套源码，不单独计独立案例；原PNG未查看。'
(B/'selected-source-acquisition.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for name,doc in [('ballista-world-emplacement.json',ball),('ars-spell-crossbow-stored-volley.json',ars)]:
 (B/name).write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')

progress=dict(updated_utc=now,status='RESEARCH_CHECKPOINT_TWO_SELECTED_NEW_FAMILIES',new_local_source_studies=2,independent_proposals_max=2,accepted_new_gate_credit=0,human_creature_model_texture_reference_credit=0,reports=['ballista-world-emplacement.json','ars-spell-crossbow-stored-volley.json'],acquired_source_files=len(manifest),evidence_records=sum(len(d['evidence']) for d in [ball,ars]),reviewed_evidence_line_ranges=sum(len(e['read_ranges']) for d in [ball,ars] for e in d['evidence']),global_1000_gates_met=False,production_modified=False,game_or_java_started=False,runtime_verified=False,published=False,prompt_deleted=False,night_deadline='2026-10-31T09:00:00+08:00',pending=[dict(family=d['id'],items=d['pending']) for d in [ball,ars]],registered_creature_boundary='119已注册ID核查是既有制作记录清点；不计新模型、参考或实机验收。机关小蛛两处NORMAL renderer注册胜者仍未验证，保留不启动游戏。',counts_note='本批2个源码机制研究，不是已接受的1000参考数量；本目录累计11个本地研究，0新增全局验收信用。')
(B/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
style='body{font:16px/1.75 system-ui,sans-serif;max-width:1080px;margin:32px auto;padding:0 20px;background:#f6f4ed;color:#263329}article{padding:18px 24px;margin:22px 0;background:white;border-left:4px solid #668576}h1{font-size:26px}h2{font-size:21px}h3{font-size:17px}a{color:#245a84}code{overflow-wrap:anywhere}li{margin:8px 0}small{color:#626960}'
parts=[f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>第六批：世界弩与法术弩</title><style>{style}</style><h1>第六批：世界弩与法术弩</h1><p>2个选定源码机制，至实际资源/世界/显示消费者；全局独立验收待完成，新增信用0。未修改生产资产、共享Jar，未运行Java/游戏。</p><p>原始PNG未看，不计生物模型＋贴图参考。<a href="../index.html">总断点</a> · <a href="progress.json">进度</a> · <a href="selected-source-acquisition.json">固定源码与阅读范围</a> · <a href="local-verification.json">本批离线校验</a></p>']
for name,doc,title in [('ballista-world-emplacement.json',ball,'Ballista：世界器械全流程'),('ars-spell-crossbow-stored-volley.json',ars,'Ars Nouveau：装填付费与存储齐射')]:
 parts.append(f'<article><h2>{title}</h2><p>{html.escape(doc["conclusion"])}</p><p><code>{doc["repo"]}@{doc["commit"]}</code></p><p><a href="{name}">结构化研究记录</a></p><ol>')
 for e in doc['evidence']:
  spans=', '.join(f'{x[0]}–{x[1]}' for x in e['read_ranges'])
  parts.append(f'<li><b>{html.escape(e["stage"])}</b> {html.escape(e["claim"])} <small><a href="{html.escape(e["fixed_url"])}">固定来源 {spans}</a> · <a href="{html.escape(e["local"])}">已保存源码</a></small></li>')
 parts.append('</ol><h3>仍未验证</h3><ul>')
 parts.extend(f'<li>{html.escape(p)}</li>' for p in doc['pending'])
 parts.append('</ul></article>')
parts.append('<p>每个家族最多1候选；不把方法、版本、弹种和同源包装拆开凑数。六机巧的1000门槛仍未满足；生物逐只100个参考门槛独立保留。</p></html>')
(B/'index.html').write_text('\n'.join(parts)+'\n')
(B/'checkpoint-20261031.json').write_text(json.dumps(dict(updated_utc=now,deadline='2026-10-31T09:00:00+08:00',resume='先检查是否超过夜间截止；不启动游戏，不新建聊天，不修改认可资产/共享Jar。继续只找新的相关完整实现，先固定版本，再读入口/状态/消费者/失败退出；全局去重后留独立验收。',uncompleted=progress['pending'],unchanged='用户认可生物模型/贴图、游戏状态、音量与亮度、共享Jar、提示词、生产逻辑。'),ensure_ascii=False,indent=2)+'\n')
root=json.loads((R/'progress.json').read_text())
prev=root['latest_batch']['id']
if not any(x['id']==prev for x in root['previous_batches']):
 root['previous_batches'].append(dict(id=prev,source_studies=root['this_batch']['source_studies'],existing_family_context_extensions=root['this_batch'].get('existing_family_context_extensions',0),new_accepted_gate_credit=0,report=root['latest_batch']['report']))
root['updated_utc']=now
root['this_batch']=dict(id='batch-06',source_studies=2,existing_family_context_extensions=0,proposed_independent_units_max=2,new_accepted_gate_credit=0,count_note=progress['counts_note'])
root['latest_batch']=dict(id='batch-06',progress='batch-06/progress.json',report='batch-06/index.html',accepted_new_gate_credit=0)
root['cumulative_local_studies']=dict(source_studies=11,accepted_new_gate_credit=0,not_global_accepted_total=True)
root['next']=[*['Ballista与Ars选定链已保存：独立验收/跨包装语义去重，原生碰撞/存档/左右手及渲染父类边界仍保留；不将齐射当连发。','下一批优先未读相关新实现；不复读同族上下文充数。'],*root['next']]
root['registered_creature_boundary']=progress['registered_creature_boundary']
(R/'progress.json').write_text(json.dumps(root,ensure_ascii=False,indent=2)+'\n')
nav='<!-- batch-06-latest --><article><h2>最新第六批：世界弩与法术弩</h2><p>Ballista建造/分次拉弦/装弹/瞄准/破坏退出，以及Ars Nouveau装填扣费、齐射、法术命中与渲染边界。2个本地源码研究，0新增全局验收信用；无生产修改或Java/游戏。</p><p><a href="batch-06/index.html">本批研究</a> · <a href="batch-06/progress.json">保存断点</a></p></article>\n'
s=(R/'index.html').read_text()
if '<!-- batch-06-latest -->' not in s:
 at=s.index('</h1>')+len('</h1>');s=s[:at]+'\n'+nav+s[at:];(R/'index.html').write_text(s)
print(json.dumps(dict(reports=2,evidence=progress['evidence_records'],ranges=progress['reviewed_evidence_line_ranges'],sources=len(manifest),accepted_credit=0),ensure_ascii=False))
