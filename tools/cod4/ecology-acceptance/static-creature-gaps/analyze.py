"""Read-only source/save/log research. Writes only this dedicated evidence subdirectory. No game/Gradle calls."""
from pathlib import Path
import json,hashlib,zipfile,collections,re,struct,gzip,zlib,uuid,datetime,math
R=Path(__file__).resolve().parents[4];D=R/'docs/cod4/audit-20261022/ecology-acceptance';O=D/'static-creature-gaps';T=R/'tools/cod4/ecology-acceptance';F=T/'.work/frozen';L=D/'live-run1';O.mkdir(exist_ok=True)
IDS=['famished_refugee','herb_picker','jingwei_bird','night_watchman','snail_maiden','swindler'];inputs={}
def read(p):
 p=Path(p);b=p.read_bytes();inputs[str(p.relative_to(R))]=hashlib.sha256(b).hexdigest();return b
def js(p):return json.loads(read(p))
def txt(p):return read(p).decode()
def write(name,v):
 (O/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n' if not isinstance(v,str) else v)
def nbt(b):
 if b[:2]==b'\x1f\x8b':b=gzip.decompress(b)
 i=0
 def take(n):
  nonlocal i
  v=b[i:i+n];i+=n;return v
 def num(f):return struct.unpack('>'+f,take(struct.calcsize('>'+f)))[0]
 def string():return take(num('H')).decode('utf8',errors='replace')
 def value(t):
  if 1<=t<=6:return num({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
  if t==7:return list(take(num('i')))
  if t==8:return string()
  if t==9:
   kind=num('b');return [value(kind) for _ in range(num('i'))]
  if t==10:
   out={}
   while True:
    kind=num('b')
    if not kind:return out
    key=string();out[key]=value(kind)
  if t in [11,12]:return [num('i' if t==11 else 'q') for _ in range(num('i'))]
  raise ValueError(t)
 kind=num('b');string();return value(kind)
# Hash original frozen sources and current formal read-only counterparts.
sources={};source_manifest=[]
for rel in ['expansion/SecondaryMobs.java','expansion/SecondarySpawnHooks.java','expansion/SecondaryMob.java','expansion/ExpansionContent.java','blueprint/LoadedStructureRegions.java','blueprint/EcologyManager.java','blueprint/EcologyRules.java','entity/DynastySpawnPlacement.java']:
 p=F/'src/main/java/com/dynasty'/rel;sources[rel]=txt(p);q=R/'src/main/java/com/dynasty'/rel;cur=read(q);source_manifest.append({'path':str(q.relative_to(R)),'frozen_sha256':inputs[str(p.relative_to(R))],'current_read_only_sha256':hashlib.sha256(cur).hexdigest(),'equal':read(p)==cur})
for name in ['EcologyLiveAcceptance.java','EcologyNaturalClient.java']:sources['QA/'+name]=txt(T/'src'/name)
jar=next((T/'.work/cross-build/gradle-home/caches/forge_gradle/minecraft_user_repo').rglob('*sources.jar'));read(jar);vanilla={};excerpts=[]
with zipfile.ZipFile(jar) as z:
 for name,ranges in {'net/minecraft/world/level/NaturalSpawner.java':[(67,97),(103,120),(198,226),(244,249),(275,325),(330,380),(455,505)],'net/minecraft/server/level/ServerChunkCache.java':[(328,359)],'net/minecraft/world/entity/MobCategory.java':[(6,30),(41,50)],'net/minecraft/world/level/LocalMobCapCalculator.java':[(29,60)],'net/minecraft/world/entity/Mob.java':[(690,736),(830,842)],'net/minecraft/world/entity/EntityType.java':[(678,685)],'net/minecraftforge/common/world/ForgeBiomeModifiers.java':[(150,180)],'net/minecraftforge/event/ForgeEventFactory.java':[(208,226)]}.items():
  raw=z.read(name);s=raw.decode();vanilla[name]=s;lines=s.splitlines();out=[]
  for a,b in ranges:out+=['']+[f'{i+1}: {lines[i]}' for i in range(a-1,min(b,len(lines)))]
  label=Path(name).stem+'.excerpt.txt';write(label,'\n'.join(out)+'\n');excerpts.append({'entry':name,'entry_sha256':hashlib.sha256(raw).hexdigest(),'source_jar_sha256':inputs[str(jar.relative_to(R))],'excerpt':label})
base=js(D/'normal-run2-observations.json');registered={x['id']:x for x in base['observations'] if x['kind']=='registered_species'};positions=[x for x in base['observations'] if x['kind']=='normal_world_position'];events=[]
for n,line in enumerate(txt(L/'events.jsonl').splitlines(),1):
 try:e=json.loads(line)
 except json.JSONDecodeError:continue
 e['line']=n;events.append(e)
summary=js(L/'summary.json');source=js(D/'source-audit.json');original={x['id']:x for x in source['species']};snapshots=[]
for p in sorted(L.glob('*state*.json')):
 s=js(p);c=s.get('native_category_counts');chunks=s.get('native_spawnable_chunks')
 if c is None:continue
 match=re.search(r'CREATURE\s*=>\s*(\d+)',c);count=int(match.group(1)) if match else None;cap=10*chunks//289 if chunks is not None else None
 snapshots.append({'file':str(p.relative_to(D)),'game_tick':s.get('current_game_tick'),'native_spawnable_chunks':chunks,'CREATURE':count,'derived_native_global_cap':cap,'global_gate_closed_at_this_snapshot':count>=cap if count is not None and cap is not None else None,'caveat':'Not a per-attempt trace; 0 spawnable chunks means no player-driven natural spawning. Local player cap not recorded.'})
rows=[]
for ident in IDS:
 spec_line=next(x for x in sources['expansion/SecondaryMobs.java'].splitlines() if 'new Spec("'+ident+'"' in x);flags=spec_line.rsplit(',',3);flying=ident=='jingwei_bird';aquatic=ident=='snail_maiden';biome=js(F/f'src/main/resources/data/dynasty/tags/worldgen/biome/secondary/{ident}.json');modifier=js(F/f'src/main/resources/data/dynasty/forge/biome_modifier/secondary_{ident}.json');reg=registered[ident]
 for resource in [f'tags/worldgen/biome/secondary/{ident}.json',f'forge/biome_modifier/secondary_{ident}.json']:
  fp=F/'src/main/resources/data/dynasty'/resource;cp=R/'src/main/resources/data/dynasty'/resource;fb=read(fp);cb=read(cp);source_manifest.append({'path':str(cp.relative_to(R)),'frozen_sha256':hashlib.sha256(fb).hexdigest(),'current_read_only_sha256':hashlib.sha256(cb).hexdigest(),'equal':fb==cb})
 positive=[e for e in events if e['kind']=='positive_native_position' and e.get('species')==ident];births=[e for e in events if e['kind']=='confirmed_natural_spawn' and e.get('species')=='dynasty:'+ident and not e.get('loaded_from_disk',True)];bp=[p for p in positions if ident in p['native_placement_callback_pass']];habitat={'famished_refugee':['blueprint/ghost_sites','secondary/ruins'],'night_watchman':['ecology/roads','blueprint/military_sites'],'swindler':['ecology/roads']}.get(ident,[])
 tags={t:js(F/f'src/main/resources/data/dynasty/tags/worldgen/structure/{t}.json') for t in habitat}
 row={'id':ident,'requested_habitat':original[ident]['spawn'],'spec_source_line':spec_line.strip(),'registered_category':reg['category'],'neutral':True,'placement':'NO_RESTRICTIONS' if flying or aquatic else 'ON_GROUND','heightmap':'MOTION_BLOCKING_NO_LEAVES','biome_tag':biome,'modifier':modifier,'native_resolved_biomes':reg['biomes'],'native_resolved_biome_count':len(reg['biomes']),'injection_status':'CONFIGURED_AND_PRIOR_NATIVE_REGISTRY_OBSERVED_NONEMPTY','dimension':'Overworld only; dragon_palace exception is crab_soldier, not these6','height':'minBuildHeight < y < maxBuildHeight-3; no per-species absolute mountain/depth bound','loaded_chunks':'Server thread; central FULL chunk and entire body+margin already FULL; margin4 for snail,1 otherwise; structure uses loaded references/start only, does not ticket chunks','light':'No numerical brightness constraint for these6; no Animal grass/brightness rule inherited (SecondaryMob extends PathfinderMob/Mob.checkSpawnRules true)','time':'level.isDay must be false' if ident=='night_watchman' else 'No time restriction','weather':'No weather restriction for these6','fluid_support':'Connected water:7x7x3 BFS>=12water blocks in>=9columns; water at position; aquatic obstruction override permits water' if aquatic else 'Empty fluid and full body noCollision; up-face sturdy support for ground types' if not flying else 'Empty fluid and noCollision; no support or minimum flight-height condition; generic obstruction rejects liquids','structure_tags_OR':tags,'structure_bounds':'Expanded XYZ structure bbox by16 and loaded start/ref lookup; exact boundary not whole biome' if habitat else None,'shared_native_gates':['spawn-animals/spawnFriendlies enabled','doMobSpawning true','CREATURE isFriendly=true,isPersistent=true -> once per400 game ticks','global count < floor(10 * spawnableChunks /289)','per-player local CREATURE count <10','distance to nearest player >24, shared spawn exclusion24; entity Mob distance/despawn check and active natural chunks','weighted biome choice weight1,group1, not deterministic selection','Forge PositionCheck DEFAULT calls Mob.checkSpawnRules and checkSpawnObstruction','shared SecondaryMob within32: total<20 and this species<3 (summoner-tagged excluded)'],'chunk_generation':'Explicitly rejected even though CREATURE can be considered in worldgen spawn list; only ordinary runtime NATURAL remains as natural evidence','native_callback_baseline':{'positions_tested':len(positions),'callback_true':len(bp),'callback_false':len(positions)-len(bp),'not_actual_birth_attempts':True,'positive_examples':bp[:1]},'live_callback_positive_count':len(positive),'live_callback_positive_examples':positive[:3],'fresh_actual_birth_count':len(births),'no_fresh_birth_is_not_global_impossibility':True,'extra_global_ecology_deny':'EcologyManager PositionCheck loops EcologyRules.members; none of these six identifiers are members. Its other regional night/light/caps are not silently inherited. Arena deny is irrelevant to normal Overworld.','finding':'NO_INTRINSIC_EMPTY_CONDITION_INTERSECTION_FOUND; no birth observed; shared native cap/cadence is a confirmed gate at recorded snapshots, not proven reason for every failed attempt'}
 assert reg['category']=='creature' and reg['biomes'] and not births
 assert ident not in sources['blueprint/EcologyRules.java']
 rows.append(row)
for resource in ['ecology/roads','blueprint/military_sites','blueprint/ghost_sites','secondary/ruins']:
 fp=F/f'src/main/resources/data/dynasty/tags/worldgen/structure/{resource}.json';cp=R/f'src/main/resources/data/dynasty/tags/worldgen/structure/{resource}.json';fb=read(fp);cb=read(cp);source_manifest.append({'path':str(cp.relative_to(R)),'frozen_sha256':hashlib.sha256(fb).hexdigest(),'current_read_only_sha256':hashlib.sha256(cb).hexdigest(),'equal':fb==cb})
write('species-reachability.json',rows);write('cap-snapshots.json',snapshots);write('source-manifest.json',{'frozen_vs_current':source_manifest,'cached_primary_sources':excerpts})
# Oil: exact actual drop UUID presence/recovery, never infer historical slot state from the terminal save.
oil=next(x for x in summary['material_proofs'] if x['id']=='lantern_oil');recovery=collections.defaultdict(list)
for e in events:
 reason=e.get('reason','')
 if reason.startswith('recover_existing_unpicked_natural_ItemEntity_'):recovery[reason.rsplit('_',1)[-1]].append(e)
throws=[]
for line in txt(L/'client-junk-throws.jsonl').splitlines():
 try:throws.append(json.loads(line))
 except json.JSONDecodeError:pass
player=T/'.work/live-run1/world/playerdata/817f74c6-1403-3509-b336-db7c734bf8f6.dat';playerdata=nbt(read(player));level=nbt(read(T/'.work/live-run1/world/level.dat'))['Data'];inventory=[x for x in playerdata['Inventory'] if 0<=x['Slot']<=35];oil_rows=[]
for p in oil['proofs']:
 rec=recovery[p['actual_drop_entity_uuid']];oil_rows.append({**p,'existing_live_item_recovery_count':len(rec),'first_existing_item_recovery':{'line':rec[0]['line'],'tick':rec[0]['game_tick']} if rec else None,'last_existing_item_recovery':{'line':rec[-1]['line'],'tick':rec[-1]['game_tick']} if rec else None,'no_identity_pickup':not p['pickup_event_lines'],'client_issued_junk_throws_within200_ticks':sum(p['death_game_tick']<=x['tick']<=p['death_game_tick']+200 for x in throws),'historical_empty_slots':'NOT_RECORDED','item_expiry_or_removal_event':'NOT_RECORDED; recovery ends near vanilla lifetime, compatible but not proof of expiry'})
# Saved entity-region census of the same unchanged private world, including the nine oil UUIDs.
entity_counts=collections.Counter();saved_items={};region_chunks=0;errors=[]
for p in sorted((T/'.work/live-run1/world/entities').glob('r.*.mca')):
 b=read(p)
 for i in range(1024):
  off=int.from_bytes(b[i*4:i*4+3],'big')*4096
  if not off:continue
  try:
   size=int.from_bytes(b[off:off+4],'big');compression=b[off+4];payload=b[off+5:off+4+size]
   if compression&128:raise ValueError('external entity chunk not handled')
   raw=zlib.decompress(payload) if compression==2 else gzip.decompress(payload) if compression==1 else payload if compression==3 else None
   if raw is None:raise ValueError('unknown compression')
   data=nbt(raw);region_chunks+=1
   for e in data.get('Entities',[]):
    entity_counts[e['id']]+=1
    if e['id']=='minecraft:item' and 'UUID' in e:
     u=str(uuid.UUID(int=sum((v&0xffffffff) <<(96-k*32) for k,v in enumerate(e['UUID']))));saved_items[u]={'pos':e.get('Pos'),'Age':e.get('Age'),'Item':e.get('Item')}
  except Exception as ex:errors.append({'file':str(p.relative_to(R)),'header_index':i,'error':str(ex)})
for p in oil_rows:p['present_in_saved_entity_regions']=p['actual_drop_entity_uuid'] in saved_items
write('lantern-oil-evidence.json',{'actual_player_kill_attempts':summary['material_species_death_attempts']['dynasty:lantern_ghost'],'positive_native_drop_events':len(oil_rows),'exact_pickups':sum(p['pickup_exact_uuid_verified'] for p in oil_rows),'proofs':oil_rows,'saved_inventory':inventory,'saved_inventory_occupied':len(inventory),'native_save_tick':level['Time'],'last_client_status':txt(L/'client-status.txt').strip(),'causality':'Final36/36 snapshot does not establish inventory occupancy at any of the9 historical drops. Junk-throw logs are issued client actions, not confirmed free-slot telemetry. Existing-item recovery proves UUID was alive in server world at those times. No removal/expire event recorded.','saved_region_scan':{'entity_chunks_decoded':region_chunks,'errors':errors,'target_UUIDs_found':sum(p['present_in_saved_entity_regions'] for p in oil_rows),'entity_counts':dict(entity_counts),'all_saved_lantern_oil_items':[{'uuid':u,**v} for u,v in saved_items.items() if v.get('Item',{}).get('id')=='dynasty:lantern_oil'],'not_runtime_cap':'All saved chunks, including unloaded chunks; cannot substitute these counts for active loaded native cap.'},'spawn_point':{k:level.get(k) for k in ['SpawnX','SpawnY','SpawnZ']},'gamerules':{k:level.get('GameRules',{}).get(k) for k in ['doMobSpawning','doDaylightCycle','doWeatherCycle']}})
# Logs: only actual native call evidence and known QA failures, no invented per-attempt CREATURE rejection trace.
log_rows=[]
for p in sorted(L.glob('server*.log')):
 text=txt(p);lines=text.splitlines();examples=[{'line':i+1,'text':x} for i,x in enumerate(lines) if any(v in x for v in ['error:','Cannot find symbol','cannot find symbol','ECOLOGY','EcologyQA left the game','lost connection','NoClassDefFoundError'])]
 log_rows.append({'file':str(p.relative_to(D)),'line_count':len(lines),'selected_records':examples[:20],'full_log_sha256':inputs[str(p.relative_to(R))]})
write('raw-log-index.json',{'logs':log_rows,'CREATURE_per_attempt_global_local_gate_trace':'NOT_RECORDED','native_BiomeEntry_and_positive_predicate_not_equal_to_full_attempt':'They omit the global/local category gates,400 cadence, weighted selection, natural ON_GROUND body checks, closest-player/shared-spawn exclusion, Forge PositionCheck and final obstruction.','known_fixture_failures':['phase7 compile failure getRainTime on LevelData; repaired before actual runtime; not a species failure','early unloaded heightmap observation bug fixed with exact FULL load; old coordinates/failures preserved','client disconnected at tick716479; world tick1579880 is not a valid player-driven observation duration','QA competitor selection includes only NATURAL-provenance MONSTER: cannot reduce the CREATURE cap that blocks six missing species']})
write('species-matrix.tsv','id\tcategory\tplacement\tresolved_biomes\tbaseline_callback_true\tlive_positive_callbacks\tactual_fresh_birth\ttime\tstructure_tags\n'+''.join('\t'.join(str(v) for v in [x['id'],x['registered_category'],x['placement'],x['native_resolved_biome_count'],x['native_callback_baseline']['callback_true'],x['live_callback_positive_count'],0,x['time'],','.join(x['structure_tags_OR'])])+'\n' for x in rows))
read(Path(__file__))
server_properties=txt(T/'.work/live-run1/server.properties')
write('saved-server-properties.txt',server_properties)
write('input-sha256.json',{'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_files':inputs,'game_client_server_or_gradle_invocations':0,'formal_java_asset_todo_writes':0,'outputs_only':str(O),'tool':str(Path(__file__).relative_to(R))})
print(json.dumps({'six_injected':all(x['native_resolved_biome_count']>0 for x in rows),'zero_birth_six':all(x['fresh_actual_birth_count']==0 for x in rows),'cap_snapshots':snapshots,'oil9_alive_recoveries':sum(bool(x['existing_live_item_recovery_count']) for x in oil_rows),'saved_oil_uuid_count':sum(x['present_in_saved_entity_regions'] for x in oil_rows),'entity_region_decode_errors':len(errors)},ensure_ascii=False))
write('report.txt','''剩余6种CREATURE：静态可达性复核（本次零客户端/服务器/Gradle启动）

结论：六种均有真实注册和原生biome注入证据，未发现互相排斥到空集的条件；六种实际自然出生仍0，不能因回调阳性或少量阴性改成通过/全局不可能。
当前正式8份相关Java、12份六种biome标签/注入配置及4份结构标签与旧QA冻结来源哈希相同（source-manifest.json）。注册→ExpansionContent.bootstrap→SecondaryMobs.bootstrap/SpawnPlacementRegisterEvent、Forge ADD biome modifier→type.getCategory()→真实CREATURE刷怪表链完整。原生normal-run2运行时各已解析12或15个非空biome条目，权重1、单体组。

逐种结论（每种完整条件、标签内容、真实biome列表、坐标及源证据在species-reachability.json）：
1 famished_refugee/流民：CREATURE/ON_GROUND；废墟ghost_sites或secondary/ruins扩展XYZ各16格；主世界有效古战场plains/草方块点(-2696,63,-1360)有回调阳性。无需夜间/数值暗度。ruined_villages空标签不能证明荒村，但流民本身用的是另外两个非空结构标签，不因此无入口。
2 herb_picker/采药人：CREATURE/ON_GROUND；forest或mountain群系，无药田结构、绝对高山高度、草方块或亮度>=9条件；(-88,103,-104)真实forest/stone点回调阳性。继承PathfinderMob而非Animal，不继承普通动物的草地/日光规则。
3 jingwei_bird/精卫：CREATURE/NO_RESTRICTIONS；forest/mountain/beach/snowy_beach/stony_shore，无最低飞行高度、不强求支撑地块；空液体、无碰撞，默认Mob obstruction仍拒绝液体。(-88,103,-104)回调阳性。飞行并不把category变成AMBIENT。
4 night_watchman/更夫：CREATURE/ON_GROUND；roads或military_sites扩展XYZ16，要求!level.isDay；无额外数值暗度。normal-run2白天0/270阳性符合夜间限制，不是注入失败；后续tick12600在真实驿站(728,118,-664)回调阳性。主世界驿站道路标签和plains注入有交集。
5 snail_maiden/田螺姑娘：CREATURE/NO_RESTRICTIONS；river/ocean/swamp，连通7x7x3水域至少12水块且9个XZ水列，身体无碰撞；自身checkSpawnObstruction覆写允许水。真实cold_ocean(488,50,488)回调阳性。虽水生却共享陆生被动CREATURE cap和400tick节奏，不走WATER_CREATURE cap；这可导致饥饿但不是条件矛盾。浅水/滩涂是设计文字，代码无专属浅水深度上限，不能虚构此约束。
6 swindler/骗子：CREATURE/ON_GROUND；roads扩展XYZ16，驿站/沙漠商队标签非空，无夜间或市集专属门槛；真实驿站(728,118,-664)回调阳性。不得因尚未找到鬼市而判此物种无自然入口。

共同真实生成链与容易混淆的限制：
- 明确拒绝MobSpawnType.CHUNK_GENERATION：原生世界生成阶段即使抽中CREATURE条目也不能靠该路径生成六种；仍有正常运行时NATURAL路径，不能说完全没有注入。
- MobCategory.CREATURE=(10,friendly=true,persistent=true,despawn128)。ServerChunkCache以gameTime%400==0为persistent类别机会；global cap=floor(10*spawnableChunkCount/289)，另需某个相关玩家local CREATURE<10。persistent类别标志不是实体isPersistenceRequired；后者及requiresCustomPersistence会被计数器排除，二者不能混为一谈。
- 已保存tick55566：289个native spawnable chunks，CREATURE66，实际global门槛10，故该瞬间共享类别门槛关闭。不是推断六种缺入口，也不是证明整个历史每一tick都满cap。末状态tick1579766只有0个spawnable chunks、CREATURE51、cap0；客户端早已断开，该段无人世界tick不能拿来扩大有效自然刷怪分母。
- 当前旧QA清理竞争怪只选择NATURAL-provenance MONSTER。清70怪物cap对六种所需的CREATURE空位没有作用，是已确认的夹具策略错位，不是Java自然生成实现已证实不可达。
- source NativeSpawner.createState统计所有可计数的已加载实体；原生世界生成的猪羊鸡牛等也可占被动cap，不必先是该QA记录过NATURAL的实体。全存档实体统计包含卸载区块，不能等同当时已加载cap或每玩家local计数。
- 生产eligible要求主线程、Overworld、中央与身体边界margin已FULL、minY<y<maxY-3、doMobSpawning、群系标签、支撑/水体/碰撞。六种中立，eligible不以Peaceful排除它们；无雨限制，仅更夫有昼夜限制。
- 运行时NaturalSpawner.getRandomPosWithin按WORLD_SURFACE高度+1到minBuildHeight之间抽取候选Y；登记的MOTION_BLOCKING_NO_LEAVES高度图不等于运行时只能刷地表，也不使水下田螺入口为空。候选所在实际3D biome仍须有该刷怪条目。
- 另一层原生ON_GROUND.isValidSpawn/isValidEmptySpawnBlock、离玩家>24、出生点24格排除、Forge PositionCheck、Mob obstruction和自然随机选种都不包含在既有单独SpawnPlacements回调阳性中。
- CREATURE Builder默认canSpawnFarFromPlayer=true，不能写成该flag=false；后面的Mob距离/自然活跃区块与despawn门槛仍作用。下次观察选30~64格、不过近玩家/共享出生点，避免依赖远距边界。
- EcologyManager PositionCheck的其它区域夜间/亮度/精英条件仅匹配EcologyRules.members，源码不包含这六种，因此不能把其“废墟夜间7光照”等误套在流民上。未见项目额外PositionCheck针对六种DENY。
- 已有日志没有逐次全局/每玩家cap、CREATURE入选species、PositionCheck Result或最终失败原因。phase7编译修复及早期未加载高度夹具错误是运行夹具记录，不能当物种代码缺陷。source/runtime门槛只能解释已保存时刻，不能反演整段历史。

灯油（lantern-oil-evidence.json）：18次真实玩家死亡事件，9次目标正掉落；9个原ItemEntity UUID各被现有server.getEntity查为存活并恢复观察148~150次，约6000tick内反复尝试，0个同UUID拾取。读取403个已保存实体chunk无解码错误，9原UUID均未留存；未记录expire/remove事件，不能证明它们具体如何消失，也不能重建/补发当自然物品。
当前保存背包36/36，不能回推9次掉落当时均满。旧客户端只丢固定10类原版杂物，无法保证总有空位；发出THROW日志也不等于服务器已腾位。未记录每次漏拾取时完整Inventory、PickupDelay、Owner、碰撞、拾取事件取消结果，原因仍未确认。

下一次必要运行方案见minimum-next-run.txt：只在全部静态准备完成且主协调认为有必要时一次启动；先判定cap和背包能否工作，条件不满足就停止。不会现在启动，也不会无限挂机追六种低权重随机出生。
''')
write('minimum-next-run.txt','''最小必要运行方案（仅方案；本次不执行）

目标：一次有界诊断区分六种“原生类别未获机会/未被选中/条件拒绝/出生成功”，并仅在真实自然灯油出现时验同实体拾取；不承诺一次随机窗口必凑齐六种。无需复跑Wangsi、全客户端套件或Hegel的C2S。

运行前静态准备：
1 使用已保存自己QA世界的全新APFS副本和独立编译/缓存，保留当前checkpoint不变；不读写用户原档，不新增建筑、setBiome、调时间/天气、cap、概率、spawn蛋/创建实体。冻结相关源码并核对版本；一份headless Forge服务器，只有需要真实原生玩家距离/拾取的同一次运行才启动一个自动化真实客户端，关闭计划外自动重连/无限重试。若提供既有武器、无敌/飞行和观察/拾取传送，须继续明示为QA夹具，不称完整生存路线或真人双人。
2 已保存世界Time1579880，DayTime余数19880（自然夜间），可优先更夫+灯油两个夜间点，避免新世界再等一夜。不改时钟；若载入后真实isNight不满足，就记录窗口不满足并跳过夜间项，不挂机等下一夜。
3 先核对本分析的原UUID实体扫描结果（现均不在已保存实体中）；不得补发旧灯油。若未来快照仍有可验证同源的存活实体才先做原UUID拾取；若没有，唯一自然闭环路线是本次原生自然刷出的灯笼鬼/更夫真实玩家击杀后原概率掉落，未出现就保持PENDING。
4 夹具准备日志方案，不修改正式Java：每个原生400tick机会记录真实spawnableChunkCount、global CREATURE count/计算上限、实际native global/local gate、玩家在线/非旁观/active chunk、全部本地参与计数实体及persistence排除理由。读取原生判定，不调用公开debug spawnCategoryForPosition（它可绕过cap），不自选种、不多抽RNG。
5 对真正自然选中的目标，记录species、biome实际spawn list、source type=NATURAL、支撑/水体/碰撞、loaded footprint、结构start/ref/实际bbox、time/light、与玩家/出生点距离、placement/native/Forge PositionCheck默认或取消结果、FinalizeSpawn及EntityJoinLevel UUID。从入选前到入世的阶段计数不得用纯回调冒充实际尝试。

先决条件与有界预算：
A 初始最多200正常ticks核对native global/local gate与背包。若CREATURE被cap关闭，停止计入六种机会；不继续清MONSTER来“解决”被动cap。若允许准备，只在该QA副本以真实客户端正常攻击已存在、确实计入CREATURE的原生动物，排除六目标及命名/驯养等不计数实体，不用kill/discard/改cap。上限64个计数竞争实体或1200ticks，先到即止；仍无法native gate打开就结束该项并交付实体/cap快照，不重复开游戏或无限清怪。准备击杀不算六目标验收。
B 只有global count<实际cap且相关player local count<10才进入场景采样；无玩家/chunks0立刻停止计时。四个已有场景，原则每个最多800正常ticks（2个400tick周期）；总自然窗口<=3200ticks，另准备<=1400ticks。若cap被竞争出生填满，当前窗口记cap关闭并停止该项，不加时碰运气。墙钟上限约5分钟（启动/加载另设60秒超时），仅一次服务器/客户端会话。

场景顺序（用已生成区块，不造夹具地面，先运行时验证真实FULL/biome/结构条件）：
1 驿站(752,101,-640)附近已有草方块合格点(728,118,-664)：更夫+骗子；先保持自然夜间。观察位置以合格自然点30~64格为准，不塞入房间、不在出生排除圈；先实际查询bbox/ref和native ON_GROUND，而非直接沿用Y101作地面。
2 古战场(-2672,66,-1344)附近草点(-2696,63,-1360)：流民；仍为自然夜间时顺带观察灯笼鬼/灯油（MONSTER分母单独记）。不把流民当荒村现场，不跑地府坏城。
3 已有森林(-64,93,-80)，如(-88,103,-104)支撑stone：采药人+精卫。避共享出生点(-64,93,-80)24格排除；用实际地形决定玩家距离，不以“山地”文字新建高台/草皮，精卫无需最低飞行高度。
4 已有cold_ocean(512,62,512)附近原水点(488,50,488)：田螺姑娘。水体连通和全body margin4的FULL区块先查；普通水生Mob入口cap不替代CREATURE cap。观察点与水点距离30~64，确保水点在实际自然活动区。

灯油拾取验证（同一场景同一客户端，不另开一次）：
- 以真实客户端把非目标杂物放入QA箱/正常丢出，必须服务器回读Inventory确认>=8个空主背包槽且有接纳一叠灯油的容量；保留10目标材料、武器、书。最终旧36格满不是这里通过的证据。
- 若自然玩家死亡原概率产出灯油，立即记录真实ItemEntity UUID、pos、stack/count、Owner、PickupDelay、age、无碰撞/可达位置及背包容量；短时每tick或每5tick记录pickup尝试，原生PlayerEvent.ItemPickupEvent同UUID/同玩家/同物品才PASS。记录ItemExpire、remove原因和merge/目标UUID更替，不因合并偷换成另一实体身份。
- 同一UUID最多200正常ticks拾取窗口，死亡后停止竞争怪清理，防背包再次填满；未拾取即交付原因快照并结束，不反复传送约6000ticks等自然消失。未自然产出则PENDING_NO_NATURAL_DROP_IN_BOUND，不调seed或概率。

完成/停止标准：
逐物种四类：CAP_OR_TIME_NOT_OPEN、NO_NATIVE_WEIGHTED_SELECTION_WITHIN_BOUND、NATIVE_ATTEMPT_REJECTED_WITH_REASON、FRESH_NATURAL_BIRTH_UUID_PASS。只有最后一类增加24/30。每种给出实际400机会、gate开放次数、自然选中次数及最终入世次数；分母为0就写0，不把总世界tick/总生物数当机会。
灯油只有同一原ItemEntity UUID拾取才能由9/10提升。所有场景完或任一故障/壁钟预算耗尽即保存QA副本游标、native world save tick与日志，正常关闭自己的进程，保留所有阴性。一次没选中不证明全局无自然入口，也不授权无限挂机/再次启动。
''')
# Immutable read-input checks and result checks; no test/game process.
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in inputs.items())
assert all(x['equal'] for x in source_manifest), 'Current formal relevant sources differ; review stale-version claim before delivery'
assert len(rows)==6 and all(x['registered_category']=='creature' and x['native_resolved_biomes'] and x['fresh_actual_birth_count']==0 for x in rows)
assert len(oil_rows)==9 and all(x['existing_live_item_recovery_count']>0 and not x['pickup_event_lines'] for x in oil_rows)
write('verification.json',{'status':'STATIC_RESEARCH_VERIFIED','six_species':6,'injection_missing_species':[],'intrinsic_empty_condition_intersections_proven':[],'fresh_births_added':0,'unchanged_evidence_all_inputs':True,'oil_positive_drop_UUIDs':9,'oil_all9_proven_existing_alive_by_recovery':True,'oil_same_UUID_pickup':0,'saved_entity_chunks_decoded':region_chunks,'entity_region_errors':errors,'old_oil_UUIDs_currently_saved':0,'new_game_client_server_gradle_launches':0,'formal_java_assets_todo_writes':0,'write_scope':str(O)})
write('output-sha256.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.iterdir()) if p.is_file() and p.name!='output-sha256.json'})
