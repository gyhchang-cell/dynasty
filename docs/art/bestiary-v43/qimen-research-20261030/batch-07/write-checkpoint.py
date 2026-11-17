from pathlib import Path
from datetime import datetime,timezone
from html import escape
import json
B=Path(__file__).resolve().parent;R=B.parent;now=datetime.now(timezone.utc).isoformat();m=json.loads((B/'selected-source-acquisition.json').read_text());commit=json.loads((B/'selected-commit.json').read_text())['sha'];repo='ZaLa0987654321/CrossbowMulticharge';base='src/main/java/org/zala/crossbowmulticharge/';cb=base+'mixin/CrossbowMixin.java';cl='src/client/java/org/zala/crossbowmulticharge/client/'
d=dict(id='crossbow-multicharge-sneak-load-lifo',updated_utc=now,status='SELECTED_OWN_MOD_CHAIN_READ_NATIVE_AND_RUNTIME_PENDING',repo=repo,commit=commit,source_author_page='https://modrinth.com/mod/crossbowmulticharge',version=dict(minecraft='1.20.1',loader='Fabric0.16.10',api='0.92.6+1.20.1',yarn='1.20.1+build.10',mod='0.11',java='17',loom='1.13.4'),source_studies=1,proposed_independent_units_max=1,new_accepted_gate_credit=0,human_creature_model_texture_reference_credit=0,relevant_scopes=['repeating_crossbow'],conclusion='原版CrossbowItem上的潜行续装＋NBT弹仓LIFO逐次发射：最多6/10储存，射一枚减一枚，有余弹保持charged。非按住自动连射，非Ars一次存储齐射。源为Fabric，未安装到Forge。',semantic_dedup=dict(local_against_batch06='与Ballista世界器械及Ars装填付费法术齐射区别在于同一手持NBT弹仓可续装并逐次LIFO消耗；公共原版弩逻辑不另计。',unused_duplicate='NewCrossbow是同仓库未发现注册的旧实现，不另计；Storage附魔、客户端谓词、HUD、不同弹种均不拆案例。',global_independent_review='PENDING',accepted_credit=0),evidence=[],pending=[
 '原生Fabric/Yarn CrossbowItem经Mixin合并后的实际方法绑定、LivingEntity停止使用调用顺序、物品栈NBT及原版箭/烟火world伤害、拾取/移除尚未全读。',
 '本模组自有世界消费者到spawnEntity与原生projectile工厂，实际原生伤害Entity.hurt与失败清理未在本批闭合，不称完整引擎或实机验收。',
 'use与release无局部server守卫；发射spawn是server守卫，弹仓减一在外层。原版两端调用/同步顺序仍待核实，不能仅凭它宣称双倍扣弹。',
 '取消续装、满仓潜行、损坏前扣耐久/后spawn且忽略返回值、Charged与空列表不一致、主手HUD空NBT等为静态分支风险；没有实机复现。',
 'Mixins大范围Overwrite与其他crossbow改动冲突未验证。没有将FabricJar装进Forge，没有构建/运行/检查发行Jar。',
 'HUD图标PNG未看，不计生物模型+PNG参考。全局去重和独立验收尚未完成；1000门槛仍不足。'])
def ev(stage,claim,p,*ranges):
 x=next(x for x in m if x['path']==p)
 d['evidence'].append(dict(id=f'CM-{len(d["evidence"])+1:02}',stage=stage,claim=claim,source_path=p,local=str(Path(x['local']).resolve().relative_to(B)),fixed_url=f'https://github.com/{repo}/blob/{commit}/{p}#L{ranges[0][0]}',read_ranges=[list(r) for r in ranges]))
ev('version','固定提交90c26a9；MC1.20.1/Yarn build10/loader0.16.10/FabricAPI0.92.6/mod0.11。不是Forge依赖。','gradle.properties',(1,14))
ev('version','Loom1.13.4、main/client拆分source sets与Java17声明；未运行Gradle。','build.gradle',(1,105))
ev('entry','fabric.mod.json声明main/client/datagen入口与Mixin；改的是原版CrossbowItem。','src/main/resources/fabric.mod.json',(1,35))
ev('entry','common Mixin配置required与CrossbowMixin；client Mixin列表为空，不能凭client文件名声称有额外持握注入。','src/main/resources/crossbowmulticharge.mixins.json',(1,15))
ev('entry','客户端Mixin空列表。','src/client/resources/crossbowmulticharge.client.mixins.json',(1,14))
ev('registration','主入口静态new ModContent触发其类初始化，onInitialize空；不要把空onInitialize误判为Storage未注册。',base+'Crossbowmulticharge.java',(1,15))
ev('registration','ModContent静态STORAGEUP调用注册；onInitialize虽调用initialize，但该类本身未直接列为entrypoint，静态字段已足以触发注册链。',base+'moditems/ModContent.java',(1,15))
ev('registration','注册Enchantment到命名空间storageup；有overrideItem helper但全部选定Java中无调用。',base+'moditems/ModItems.java',(1,29))
ev('enchantment','Storage目标Crossbow，稀有度在ModContent传入；canAccept排斥Multishot，其他交由父类；6/10由调用侧决定。',base+'moditems/enchantments/CrossbowStorageEnchantment.java',(1,25))
ev('state','Mixin目标CrossbowItem；charged/loaded两个字段为Item实例上的临时装填声音门控，真正上膛是stack NBT Charged，两者不混淆。',cb,(46,55),(173,182),(344,364))
ev('entry','use实际hand栈：潜行且弹仓未满先取消Charged，再进入装填；已charged则shootAll，有剩余弹不清charged。',cb,(85,104))
ev('capacity','容量仅在玩家use入口用附魔级别0/非0分6/10；release/load本地方法没有重复容量检查，不推断外部AI调用一定安全。',cb,(85,104),(116,149))
ev('timing','release用maxUseTime-remaining与pullProgress>=1才装一枚；pullTime=25或25-5×QuickCharge，max=pull+3；无tick自动连发。',cb,(116,149),(372,409))
ev('resource_consumer','非创造普通装弹split1并移除空弹栈；创造/模拟分支copy；每次loadProjectiles仅调用一次loadProjectile。',cb,(136,169))
ev('persistence','Charged布尔与ChargedProjectiles compound列表存在ItemStack；附加writeNbt记录弹药完整栈。未检验原生网络与磁盘编解码。',cb,(173,215))
ev('queue','decProjectiles取size-1并删除；新弹append，发射同样取last，因此是后进先出；不是先进先出或全列表一次发完。',cb,(185,225),(293,312))
ev('mixed_ammo','getSpeed查询整个列表任一烟火决定1.6或3.15；实际发射last，故混装时射速判断不只看即将发射弹种。只记录静态逻辑。',cb,(107,109),(229,231),(293,312))
ev('world_consumer','server-only shoot：烟火原生构造或ArrowItem.createArrow，设置旋转速度；CrossbowUser交给其shoot，玩家用view/up四元数。',cb,(234,266),(275,290))
ev('failure','先crossbow.damage后world.spawnEntity，不检查spawn布尔；未见该分支失败回滚；不宣称实际生成失败已复现。',cb,(268,271))
ev('multishot','shot仅从last取一枚，有multishot1则额外±10两箭；消耗储存项一次，额外箭pickup创造成员；不是3个独立实现。',cb,(252,255),(293,312),(327,337))
ev('post_consumer','server玩家criterion/stat后，外层decProjectiles；无独立退出包或持久tick连射状态。spawn服务端守卫不等于整个外层都服务端守卫。',cb,(327,337),(85,104))
ev('empty_failure','shootAll即使列表空仍将id夹为0再list.get(0)，没有本地空列表退出。只能标Charged/entries不一致的边界，不报游戏已崩溃。',cb,(293,312))
ev('cancel_failure','潜行续装先清charged；release不足pullProgress1不重设，也不清原弹仓。若随后已无外部弹药，use会fail而非发射已有列表；这是源码状态推演，未实机。',cb,(85,104),(116,133),(173,182))
ev('full_capacity','满仓潜行不执行清charged，随后charged分支照常发射；并非满仓潜行静默拒绝续装。',cb,(85,104))
ev('visual_timing','usageTick只server更新20%/50%两个声音门控；不当成额外弹仓状态或自动发射器。',cb,(344,365))
ev('tooltip','tooltip显示第0枚而非即将LIFO发射last；烟火高级提示addAll重复3次。不得混称显示目标完全一致。',cb,(415,435),(293,312))
ev('client_consumer','client入口注册predicate/HudRenderCallback；HUD取本地玩家mainHand，不取offhand；容量和列表长度画8px槽。',cl+'CrossbowmultichargeClient.java',(24,60))
ev('client_failure','HUD仅assert玩家非空，且CrossbowItem分支requireNonNull(stack.getNbt())，不先getOrCreateNbt。原生默认NBT和事件时机未核实，不直接断言必崩。',cl+'CrossbowmultichargeClient.java',(39,55))
ev('predicate','覆盖原版CROSSBOW firework predicate，用last弹是否烟火，与LIFO目标一致；没看到新自有crossbow模型JSON。',cl+'ModModelPredicate.java',(14,32))
ev('not_reachable_duplicate','全部main/client Java及入口已读，NewCrossbow无构造/注册引用；其旧齐射并一次清列表不等于实际生效Mixin逐发，不能另计。',base+'moditems/NewCrossbow.java',(1,392))
ev('datagen_boundary','datagen入口仅createPack，不生成模型或注册新弩；这个空骨架不计实现。',cl+'CrossbowmultichargeDataGenerator.java',(1,12))
d['static_trace_not_runtime']=[
 dict(input='空仓false→完整装一枚',result='Charged=true，列表1'),
 dict(input='有弹且未满→潜行完整续装',result='先false，追加1再true；不是清空再装'),
 dict(input='列表2且charged→不潜行使用',result='last发射，删last，列表1，保留charged'),
 dict(input='最后一枚射完',result='列表0→use外层清charged'),
 dict(input='满仓charged→潜行使用',result='不满足size<capacity清charged条件，转发射'),
 dict(input='有旧弹→潜行续装提前松开',result='可能保留旧弹列表但charged=false；没有退出时重置原有上膛状态代码')]
for x in m:x['reviewed_ranges']=[[1,x['lines']]];x['read_status']='FULL_READ';x['counting_note']='14个配套文件只服务1个机制研究；源码全文阅读不等于原生引擎或PNG实机验收。'
(B/'selected-source-acquisition.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
(B/'crossbow-multicharge-lifo.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=dict(updated_utc=now,status='RESEARCH_CHECKPOINT_ONE_NEW_FAMILY_NATIVE_BOUNDARIES_PENDING',new_local_source_studies=1,independent_proposals_max=1,accepted_new_gate_credit=0,human_creature_model_texture_reference_credit=0,acquired_source_files=len(m),reports=['crossbow-multicharge-lifo.json'],evidence_records=len(d['evidence']),reviewed_evidence_line_ranges=sum(len(e['read_ranges']) for e in d['evidence']),production_modified=False,game_or_java_started=False,runtime_verified=False,global_1000_gates_met=False,published=False,prompt_deleted=False,night_deadline='2026-10-31T09:00:00+08:00',pending=d['pending'])
(B/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
style='body{font:16px/1.75 system-ui,sans-serif;max-width:1050px;margin:32px auto;padding:0 20px;color:#263329;background:#f6f4ed}article{padding:18px 24px;background:white;border-left:4px solid #668576}h1{font-size:26px}a{color:#245a84}li{margin:10px 0}small{color:#626960}code{overflow-wrap:anywhere}'
s=[f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>第七批：续装弹仓与逐发消耗</title><style>{style}</style><h1>第七批：续装弹仓与逐发消耗</h1><p>{escape(d["conclusion"])}</p><p><code>{repo}@{commit}</code></p><p>1个本地研究，0新增全局验收信用；独立复核/原生消费者/实机仍待完成。已认可资产和共享Jar未改，未运行Java/游戏。</p><p><a href="../index.html">总断点</a> · <a href="progress.json">本批进度</a> · <a href="crossbow-multicharge-lifo.json">完整记录</a> · <a href="selected-source-acquisition.json">固定源码</a> · <a href="local-verification.json">离线校验</a> · <a href="https://modrinth.com/mod/crossbowmulticharge">作者页面</a></p><article><ol>']
for e in d['evidence']:
 ranges=', '.join(f'{a}–{b}' for a,b in e['read_ranges'])
 s.append(f'<li><b>{escape(e["stage"])}</b> {escape(e["claim"])} <small><a href="{escape(e["fixed_url"])}">固定来源 {ranges}</a> · <a href="{escape(e["local"])}">本地源码</a></small></li>')
s.append('</ol><h2>静态状态推演，非实机结果</h2><ul>')
for t in d['static_trace_not_runtime']:s.append(f'<li>{escape(t["input"])}：{escape(t["result"])}</li>')
s.append('</ul><h2>未完成边界</h2><ul>')
for v in d['pending']:s.append(f'<li>{escape(v)}</li>')
s.append('</ul></article><p>本批没有查看原PNG、制作新模型或新增生物参考。14个源码文件、HUD、附魔与弹种不拆成14例或更多。</p></html>')
(B/'index.html').write_text('\n'.join(s)+'\n')
(B/'checkpoint-20261031.json').write_text(json.dumps(dict(updated_utc=now,deadline='2026-10-31T09:00:00+08:00',next_scope=d['pending'],resume_requires_deadline_check=True,restrictions=['仅本研究目录写入，不动认可资源/共享Jar/提示词。','不新建聊天、不启动Java/游戏、不唤醒/抢焦点、不改声音亮度。','119注册ID不算参考或实机验收；机关小蛛两处同优先级renderer加载胜者保持待验证。']),ensure_ascii=False,indent=2)+'\n')
root=json.loads((R/'progress.json').read_text());prev=root['latest_batch']['id']
if not any(v['id']==prev for v in root['previous_batches']):root['previous_batches'].append(dict(id=prev,source_studies=root['this_batch']['source_studies'],proposed_independent_units_max=root['this_batch'].get('proposed_independent_units_max',0),new_accepted_gate_credit=0,report=root['latest_batch']['report']))
root['updated_utc']=now;root['this_batch']=dict(id='batch-07',source_studies=1,proposed_independent_units_max=1,new_accepted_gate_credit=0,count_note='潜行续装＋LIFO逐发为一个本地研究；NewCrossbow未注册旧实现/HUD/附魔/弹种不拆计。全局验收0。');root['latest_batch']=dict(id='batch-07',progress='batch-07/progress.json',report='batch-07/index.html',accepted_new_gate_credit=0);root['cumulative_local_studies']=dict(source_studies=12,accepted_new_gate_credit=0,not_global_accepted_total=True);root['next'].insert(0,'Crossbow Multicharge已读全部自有Java/入口/Gradle：原生引擎消费者、跨包装去重和独立验收仍待完成；不得误计未注册NewCrossbow。')
(R/'progress.json').write_text(json.dumps(root,ensure_ascii=False,indent=2)+'\n')
nav='<!-- batch-07-latest --><article><h2>最新第七批：潜行续装与LIFO逐发</h2><p>Fabric1.20.1 Crossbow Multicharge固定版本，读完自有Java/入口/配置；有弹保留上膛、逐发减一及取消/显示边界。1个本地研究，新增验收信用0。</p><p><a href="batch-07/index.html">本批研究</a> · <a href="batch-07/progress.json">保存断点</a></p></article>\n'
s=(R/'index.html').read_text()
if '<!-- batch-07-latest -->' not in s:
 at=s.index('</h1>')+len('</h1>');(R/'index.html').write_text(s[:at]+'\n'+nav+s[at:])
print(json.dumps(dict(evidence=p['evidence_records'],ranges=p['reviewed_evidence_line_ranges'],files=len(m),accepted_credit=0)))
