from pathlib import Path
import json,hashlib,datetime,html,os
B=Path(__file__).resolve().parent;R=B.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
manifest=json.loads((B/'selected-source-manifest.json').read_text());sources=[]
read={'gradle.properties':[[1,59]],'build.gradle':[[1,145]],'mods.toml':[[1,24]],'NarrowZone.java':[[1,33]],'ModItems.java':[[1,32]],'RepeatingCrossbowItem.java':[[1,380]],'UseStopHandler.java':[[1,29]],'ModClientGameplayEvents.java':[[1,39]],'ModItemProperties.java':[[1,130]],'ModClientEvents.java':[[1,101]],'ModRangedEnchantmentEffects.java':[[1,388]]}
for x in manifest['files']:
 p=B/x['local'];name=p.name;data=p.read_bytes()
 try:text=data.decode('utf-8');encoding='utf-8'
 except UnicodeDecodeError:text=data.decode('latin1');encoding='latin1'
 if name in read:x.update(status='SELECTED_SOURCE_RANGES_READ',reviewed_ranges=read[name],text_encoding=encoding)
 elif name.startswith('repeating_crossbow') and name.endswith('.json'):x.update(status='FULL_JSON_READ',reviewed_ranges=[[1,len(text.splitlines())]],text_encoding=encoding)
 elif name.startswith('repeating_crossbow') and name.endswith('.png'):x.update(status='ACTUAL_PNG_VIEWED_12X_AND_MODEL_LAYERS',reviewed_ranges=[])
 else:continue
 x['reviewed_utc']=now;sources.append(dict(id=('recipe/'+name if '/data/' in x['path'] else name),local=x['local'],sha256=x['sha256'],reviewed_ranges=x['reviewed_ranges'],status=x['status'],text_encoding=x.get('text_encoding')))
save(B/'selected-source-manifest.json',manifest)
e=[]
def add(id,f,refs,limit):e.append(dict(id=id,finding=f,sources=[dict(source=n,ranges=rg) for n,rg in refs],limit=limit,credit_added=0))
add('N01','作者Modrinth源码链接落到公开仓库，master读取后固定为0f4e44d。实际属性为MC1.20.1、Forge47.4.9、mod1.0-1.20.1、Java17；没有把网页兼容范围当实际构建版本。',[('gradle.properties',[[10,18],[35,57]]),('build.gradle',[[16,17],[126,132]]),('mods.toml',[[1,24]])],'只读源码归档，未运行Gradle；不升级Dynasty。归档有固定commit与本地hash，未另取Git树独立核对blob。')
add('N02','真实注册narrowzone:repeating_crossbow构造RepeatingCrossbowItem，@Mod构造注册物品；客户端setup enqueue属性注册。配方结果同一ID。',[('ModItems.java',[[14,31]]),('NarrowZone.java',[[14,31]]),('repeating_crossbow.json',[[1,44]])],'模型文件名与配方文件名相同但来源目录不同；引用表中的repeating_crossbow.json为模型，配方完整阅读另记录路径。')
add('N03','tm_magazine是ItemStack完整NBT列表；装填复制count1追加尾部，发射取index0后删除，因此是FIFO，混合附魔箭/烟花的顺序与物品NBT保留。',[('RepeatingCrossbowItem.java',[[34,94],[196,208]])],'和Multicharge最后取出LIFO的机制不同；新独立性仍待全局语义复核，不能因名字不同直接验收。')
add('N04','默认容量12，一次装填达时把副手优先、再背包items遍历的可用弹药填到上限；生存每颗扣1，创造不扣且无弹时补普通箭。',[('RepeatingCrossbowItem.java',[[28,32],[106,163]] )],'创造持副手特殊弹会反复复制到满；这不是依次轮换弹种，也不表示从所有装备槽找弹。')
add('N05','单次使用按有弹/无弹进入FIRE/RELOAD，装填80-10*QuickCharge、击发10-2*QuickCharge，各最低5tick；getUseDuration为72000只是持续使用上限。',[('RepeatingCrossbowItem.java',[[96,104],[210,269]])],'本地公式不是实际输入频率测量，也不把页面high fire rate当持续tick自动射击证明。')
add('N06','服务器达击发时长先FIFO弹出一颗，Multishot复制1或3个ChargedProjectiles，调用原生performShooting，再清临时charged列表，设置STOP并stopUsingItem。',[('RepeatingCrossbowItem.java',[[272,327]])],'每次use最多走一次此发射出口；长按是否由原版客户端重新触发使用尚未闭合。原生实际生成/扣耐久/统计后续待同版本读取。')
add('N07','服务器onUseTick是主体，非Player直接返回；UseStopHandler只处理LightCrossbow，对重复弩没有额外退出功能。releaseUsing不调用父类，只在STOP时清flag或清mode。',[('RepeatingCrossbowItem.java',[[237,251],[330,343]]),('UseStopHandler.java',[[12,29]])],'不能把这个玩家物品直接当成已有Mob射击AI，不能用另一个类的Stop订阅补它的状态链。')
add('N08','getHandHolding先按mainhand引用或ItemStack.matches，再offhand；客户端usingThis也接受matches。两栈内容相同不等于引用同一栈。',[('RepeatingCrossbowItem.java',[[186,194],[369,378]]),('ModItemProperties.java',[[78,84]])],'可能身份含混的条件已记录，未实机证明错手或反复触发；不能声称已经有唯一栈UUID约束。')
add('N09','服务端inventoryTick用magCount改charged；客户端按正在使用且MODE_FIRE累加tm_fire_anim，其他情形归零。模型fire属性采这份动画值，reload属性采实际已用tick比。',[('RepeatingCrossbowItem.java',[[357,379]]),('ModItemProperties.java',[[86,103]])],'状态NBT与客户端局部视觉同处栈上；网络同步延迟/覆盖和重登恢复未运行。')
add('N10','mode属性按是否正用及magCount返回0/1/2，type按下一发返回烟花1/箭2，loaded只在未使用且有弹时1。12个模型JSON的层叠贴图全部实际查看。',[('ModItemProperties.java',[[105,128]]),('repeating_crossbow.json',[[28,43]])],'属性mode并不直接返回tm_mode。原生阈值倒序语义与网络过渡可能影响选帧；本批没有执行烘焙。')
add('N11','贴图是16×16有组织的大形：暖木握持、冷灰弓臂、红色端饰分清。充能3帧让亮色沿机构移动；击发帧复用拉弦图加独立ammo层，不是12套独立模型。',[('repeating_crossbow_firing_0.json',[[1,7]]),('repeating_crossbow_firing_1.json',[[1,7]]),('repeating_crossbow_loaded.json',[[1,7]]),('repeating_crossbow_arrow.json',[[1,7]])],'只借鉴状态与显示对应；不复制原图，不把红色装饰称为所有Boss适用模板。pulling_3 PNG在所读JSON中未引用，不算运行帧。')
add('N12','EntityJoin事件对所有AbstractArrow按owner的“最可能”当前武器追加远射/连锁NBT；它不是发射时显式传武器身份。连锁生成箭标志避免在Join被重置深度。',[('ModRangedEnchantmentEffects.java',[[150,207],[275,310],[339,382]])],'此为重复弩的相关消费者上下文，0额外家族；火箭不走AbstractArrow这个分支，实际事件顺序与命中结果未运行。')
add('N13','连锁产生在ProjectileImpactEvent里，没等LivingHurt成功；取邻近活体并排除owner/当前/上个目标/盟友，另生成普通Arrow，保留有限origin/longshot标志。',[('ModRangedEnchantmentEffects.java',[[237,273],[312,382]])],'不是原有药箭实体完整复制，也不证明伤害必成功；不把这个附魔另计重复弩参考。')
dedup=dict(status='PRESEARCH_ONLY_GLOBAL_SEMANTIC_AND_INDEPENDENT_REVIEW_PENDING',terms=['narrowzone','Narrow Zone','lucs789/forge-1.20.1-narrowzone'],searched=['docs/cod4/audit-20261022 JSON/JSONL/remaining (excluding source caches)','docs/art selected review/ledger/accepted JSON filename patterns'],result='所检索范围没有项目名命中；不是全局语义唯一证明',proposed_family='NarrowZone FIFO mixed-ammo magazine + timed one-shot use + phased sprite layers',at_most_proposed_units=1,not_split=['12个贴图','12个模型组合','Multishot三发','充能/击发/装填帧','附魔链箭'],compared_existing=['ZaLa Multicharge：LIFO单次弹出、潜行续装','Ars：同一次调用储存齐射，仅邻接不直接计连发'],accepted_credit=0)
save(B/'dedup-presearch.json',dedup)
v=dict(saved_utc=now,status='NEW_FIXED_SOURCE_STUDY_PROVISIONAL_NOT_ACCEPTED',repo='lucs789/forge-1.20.1-narrowzone',commit='0f4e44dd4f78e550fcbdb4b85934af58b1190b22',official_pages=['https://modrinth.com/mod/narrow-zone','https://github.com/lucs789/forge-1.20.1-narrowzone'],scope='repeating_crossbow',source_studies=1,proposed_independent_units_max=1,new_accepted_gate_credit=0,human_creature_model_texture_reference_credit=0,sources=sources,evidence=e,actually_viewed=['actual-pngs-12x.png','actual-model-layers-12x.png'],dedup='dedup-presearch.json',production_changed=False,java_game_started=False,pending=['原生47.4.9 performShooting/使用tick/退出与客户端重触发未闭合','尚未独立验收与全局语义去重，不能累计为已完成1000','其他弓与全部事件/全部模组资产未审计','配方读取不代表Dynasty加入此物品'])
save(B/'fifo-magazine-study.json',v)
# Record recipe separately to prevent basename collision with model source.
p=B/'sources/lucs789__forge-1.20.1-narrowzone/src/main/resources/data/narrowzone/recipes/repeating_crossbow.json';save(B/'recipe-provenance.json',dict(local=str(p.relative_to(B)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reviewed_ranges=[[1,len(p.read_text().splitlines())]],result='narrowzone:repeating_crossbow'))
a=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>B18 FIFO重复弩真实链</title><style>body{font:16px/1.65 system-ui;background:#172027;color:#e0e6e8;max-width:1280px;margin:30px auto}a{color:#9ad4e0}img{max-width:100%;image-rendering:pixelated}article{padding:16px;border-bottom:1px solid #45515c}</style><h1>B18 · FIFO混合弹仓与真实状态贴图</h1><p>新固定源码研究1项，待全局语义/独立验收，已接受新增0。不是新生物、不是1000门槛完成，未改生产资源。</p><p><a href="fifo-magazine-study.json">实际阅读与边界</a> · <a href="dedup-presearch.json">去重边界</a> · <a href="local-verification.json">静态检查</a></p><p>参考图版权归NarrowZone作者Lucas；仅研究。</p><img src="actual-pngs-12x.png"><img src="actual-model-layers-12x.png">']
for x in e:a.append('<article><b>'+x['id']+'</b><p>'+html.escape(x['finding'])+'</p><small>'+html.escape(x['limit'])+'</small></article>')
(B/'index.html').write_text('\n'.join(a)+'\n</html>')
save(B/'progress.json',dict(saved_utc=now,status='BOUNDED_SUBRANGE_SAVED_CONTINUING',deadline='2026-10-31T12:09:23+08:00',report='index.html',new_source_studies=1,proposed_independent_units_max=1,new_accepted_credit=0,next='补同版本原生发射与使用退出消费者，不把同家族延伸再计'))
p=json.loads((R/'progress.json').read_text());old=p['this_batch']
if not any(x['id']==old['id'] for x in p['previous_batches']):p['previous_batches'].append(dict(old,report=old['id']+'/index.html'))
p.update(updated_utc=now,latest_batch=B.name,this_batch=dict(id=B.name,source_studies=1,proposed_independent_units_max=1,evidence_records=len(e),new_accepted_gate_credit=0,count_note='NarrowZone FIFO重复弩1项固定源待审研究，未独立验收，不按PNG/帧/附魔重复计数。'));p['cumulative_local_studies']['source_studies']=13;p['continuation_window'].update(last_saved_utc=now,report=B.name+'/index.html',progress=B.name+'/progress.json',status='ACTIVE_CONTINUING_AFTER_BOUNDED_BATCH');save(R/'progress.json',p);print('saved',len(e))
