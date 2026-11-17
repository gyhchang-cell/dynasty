import json,hashlib,math,sys,tomllib
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not(OUT/'RECEIPT.json').exists();sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def get(n):return json.loads((OUT/n).read_text())
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def restore(v):
 if isinstance(v,dict):
  if set(v)=={'__original_nbt_byte_array_hex__'}:return bytes.fromhex(v['__original_nbt_byte_array_hex__'])
  return {k:restore(w)for k,w in v.items()}
 if isinstance(v,list):return [restore(w)for w in v]
 return v
checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
sources=get('sources.json')['candidates'];raw=get('raw-source-audit.json')['candidates'];ctx=get('source-context.json');screen=get('pre-render-history-screen.json');cases=[];functional=[];presence=[]
reasons=[{'purpose':'原witch/warlock炼药与魔法住屋，witchcauldron、两brew、书台/球和2床上房，3grind分别堆叠在5,y6/7,6与10,11,23吊挂，不因机器磨具命中就称铁匠铺。','whole_boundary':'原完整多体住屋和附棚在同source，当前只对用途进行初步视觉排除；未完成33张全部视图或逐层路径/空间家族研究，不提出完整相关建筑信用。','evidence':'23×34×28/DV3465，21786记录=5522非air16264显式air，110省略；2brownbedpair在y13，梯14,y9..18,13north，原实体witch1/warlock1/alexsmobsfly2，无smith/anvil/任何furnace。许多goety专有石木在分类图通灰，非全石房或实际贴图渲染。原2playerheads的皮肤未取图/渲染，不制作人形。'}, {'purpose':'雪地旧塔明确呈残壁/缺盖、原散置工作块、void污染装置，不能把2blast/砧/壁磨具当完整可经营铁匠铺。','whole_boundary':'当前只做毁损/用途边界初步排除，未修复源/补楼盖后冒充完整建筑，也不计残壁/火盆/房区/装置为不同建筑。保留候选原图/源，当前信用0。','evidence':'19×20×18/DV3465，6826记录=2606非air4220显式air，14省略；2blast分别11,5,13与12,6,14north空/unlit，grind15,6,9wallnorth/anvil15,6,10south；无bed/ladder/true door/entities。goety voidfluid30/voidblock40/major16/minor25/voidflame7不冒普通岩浆槽。原generator9,6,7的BE id endersent_generator_block_entity/tickCounter1不执行，不断言已生怪。'}]
for a,r,why in zip(sources,raw,reasons):
 ident=a['id'];sr=next(c for c in screen['rows']if c['id']==ident)
 check(ident+' pre-render history alias exclusion',sr['eligible_for_new_source_study']and not sr['known_history']and not sr['historical_exact_matches']and not sr['within_batch_exact_matches'])
 check(ident+' original fixed archive unchanged',bind(a['source_archive'])==sr['fixed_archive'])
 with ZipFile(a['source_archive'])as z:
  b=z.read(a['member']);d=read(b);pal=d['palette'];count=Counter(pal[b['state']]['Name']for b in d['blocks']);mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
  check(ident+' full raw and original decode incl byte arrays',hashlib.sha256(b).hexdigest()==a['nbt_sha256']==r['nbt_sha256']and d==restore(r['nbt_decoded_original']))
  check(ident+' original palette bounds and coordinates',len(mp)==len(d['blocks'])and all(0<=b['state']<len(pal)and all(0<=b['pos'][i]<d['size'][i]for i in range(3))for b in d['blocks']))
  check(ident+' exact material/explicit air counts',dict(count)==r['material_counts']and sum(count[n]for n in AIR)==r['air']and len(d['blocks'])-r['air']==r['nonair'])
  f={'id':ident,'declared_volume':math.prod(d['size']),'stored_records':len(d['blocks']),'explicit_air':r['air'],'nonair':r['nonair'],'omitted_positions':math.prod(d['size'])-len(d['blocks']),'entities_original':d['entities'],'functional_states':[{'pos':b['pos'],'state':pal[b['state']],'original_block_entity':b.get('nbt')}for b in d['blocks']if b.get('nbt')or any(w in pal[b['state']]['Name']for w in ['door','furnace','smithing','grindstone','bed','lava','water','stairs','ladder','anvil','loom','cartography','crafting','stonecutter','cauldron'])]};functional.append(f)
  for c in [m for m in ctx['metadata']if m['id']==ident]:check(ident+' original metadata '+c['member'],hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']and z.read(c['member']).decode()==c['original_text'])
  c=next(c for c in ctx['candidates']if c['id']==ident)
  for cc in c['contexts']:check(ident+' original context '+cc['member'],hashlib.sha256(z.read(cc['member'])).hexdigest()==cc['sha256']and json.loads(z.read(cc['member']))==cc['json'])
  base='pristine_shack'if ident=='F01'else'snowy_abandoned_tower';root=next(x['json']for x in c['contexts']if x['member']==f'data/goetyawaken/worldgen/structure/{base}.json');pool=next(x['json']for x in c['contexts']if x['member']==f'data/goetyawaken/worldgen/template_pool/{base}.json');processor=next(x['json']for x in c['contexts']if '/processor_list/'in x['member']);placement=next(x['json']['placement']for x in c['contexts']if '/structure_set/'in x['member'])
  check(ident+' root original -5/7/max80/false no fabricated terrain',root['start_height']=={'absolute':-5}and root['size']==7 and root['max_distance_from_center']==80 and root['use_expansion_hack']is False and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'and'terrain_adaptation'not in root)
  check(ident+' selected single1 rigid actual loot processor',len(pool['elements'])==1 and pool['elements'][0]=={'weight':1,'element':{'location':'goetyawaken:'+base,'processors':'goetyawaken:'+base+'_loot','projection':'rigid','element_type':'minecraft:single_pool_element'}}and pool['fallback']=='minecraft:empty')
  check(ident+' original placement128/32 distinct salt',placement=={'type':'minecraft:random_spread','spacing':128,'separation':32,'salt':923810292 if ident=='F01'else 918238452})
  target='goety:chests/shack_potion'if ident=='F01'else'minecraft:chests/pillager_outpost';rules=processor['processors'][1]['rules'];check(ident+' original processor custom and5appendloot configs not executed',processor['processors'][0]=={'processor_type':'goety:waterlogging_stop_processor'}and len(rules)==5 and all(x['block_entity_modifier']=={'type':'minecraft:append_loot','loot_table':target}for x in rules));ns,sub=target.split(':');member=f'data/{ns}/loot_tables/{sub}.json';presence.append({'id':ident,'member':member,'present_in_single_fixed_jar':member in z.namelist(),'environment_missing_not_inferred':True})
  check(ident+' no original jigsaw',count['minecraft:jigsaw']==0)
  if ident=='F01':
   check('F01 exact 21896volume/21786records/110omitted',math.prod(d['size'])==21896 and f['omitted_positions']==110 and r['nonair']==5522 and r['air']==16264)
   check('F01 no forge heat/smith/anvil original',all(count[n]==0 for n in ['minecraft:furnace','minecraft:blast_furnace','minecraft:smoker','minecraft:smithing_table','minecraft:anvil','minecraft:damaged_anvil']))
   check('F01 magic cauldron and2brew preserved',count['goety:witch_cauldron']==1 and count['minecraft:brewing_stand']==2 and next(b['nbt']for b in d['blocks']if pal[b['state']]['Name']=='goety:witch_cauldron')['Mode']=='IDLE')
   check('F01 original grind stack plus hanging',count['minecraft:grindstone']==3 and mp[5,6,6]['Properties']=={'face':'floor','facing':'east'}and mp[5,7,6]['Properties']=={'face':'floor','facing':'south'}and mp[10,11,23]['Properties']=={'face':'ceiling','facing':'south'})
   check('F01 entities witch warlock2flies original',Counter(e['nbt']['id']for e in d['entities'])==Counter({'minecraft:witch':1,'goety:warlock':1,'alexsmobs:fly':2}))
   check('F01 original two brown bedpairs y13',count['minecraft:brown_bed']==4 and all(mp[x,13,8]['Properties']['part']=='head'and mp[x,13,9]['Properties']['part']=='foot'and mp[x,13,8]['Properties']['facing']==mp[x,13,9]['Properties']['facing']=='north'for x in [10,11]))
  else:
   check('F02 exact6840volume/6826records/14omitted',math.prod(d['size'])==6840 and f['omitted_positions']==14 and r['nonair']==2606 and r['air']==4220)
   check('F02 no beds ladder doors/entities',not d['entities']and not any(n.endswith(('_bed','_door'))or n=='minecraft:ladder'for n in count))
   check('F02 original source2unlit empty blast',count['minecraft:blast_furnace']==2 and all(b['nbt']['Items']==[]and b['nbt']['BurnTime']==b['nbt']['CookTime']==0 and pal[b['state']]['Properties']['lit']=='false'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:blast_furnace'))
   check('F02 void source blocks not lava',count['goety:void_fluid']==30 and count['goety:void_block']==40 and count['goety:void_major_spread']==16 and count['goety:void_minor_spread']==25 and count['goety:void_flame']==7 and count['minecraft:lava']==0)
   generator=next(b for b in d['blocks']if pal[b['state']]['Name']=='goetyawaken:endersent_generator');check('F02 exact generator payload not executed',generator['pos']==[9,6,7]and generator['nbt']=={'tickCounter':1,'id':'goetyawaken:endersent_generator_block_entity'})
  images=[bind(OUT/(ident+'-'+n+'.png'))for n in ['whole','cutaway','y6']]
  for image in images:
   with Image.open(image['path'])as im:im.verify()
   check(ident+' viewed image binding valid '+Path(image['path']).name,bind(image['path'])==image)
  cases.append({**a,'screening_observations':why,'images_actually_viewed':images,'actual_full_reference_study_complete':False,'status':'SCREENED_OUT_ZERO_PENDING_RELEVANCE_OR_RUIN','credit_proposal_maximum':0,'formal_credit_added':0,'native_acceptance':False})
put('functional-evidence.json',{'candidates':functional,'original_states_preserved':True,'native_function_not_verified':True})
put('nested-loot-presence.json',{'rows':presence,'no_config_executed':True,'single_jar_only':True})
check('339 historical archive-member pairs not semanticcredit',screen['history_unique_archive_member_pairs']==339);check('prefilter prior097 unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
put('manual-review.json',{'scope':'Preliminary relevance/ruin exclusion only, not full complete related-building studies.','cases':cases,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_current_png':33,'actual_current_images_viewed':6,'unviewed_png':27,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'no_independent_self_admission':True})
viewed={x['path']for c in cases for x in c['images_actually_viewed']};put('visual-reading-boundary.json',{'viewed':[x for c in cases for x in c['images_actually_viewed']],'not_viewed_generated':[bind(p)for p in sorted(OUT.glob('*.png'))if str(p)not in viewed],'unviewed_not_references_or_observations':True,'no_claim_all_layers_reviewed':True,'generic_color_diagrams_not_actual_custom_textures_collision_or_entities':True})
put('source-context-reading.json',{'metadata':'文件名goetyawaken1.3.8内部测试，实际Forge mods version1.3.7/javafml47/Teamk1sak1/CodeLGPL2.1AssetsARR/pack15；mandatoryForge47/Minecraft1.20.1..1.21/Goety2.5.51.0+原留不推当前兼容；无Fabric元信息不编。','roots':'两root size7/max80/startabsolute-5/WORLDSURFACEWG/expansionfalse/emptyspawns，原未设terrain_adaptation不编none/beardthin。独立single1rigid/各ownlootprocessor/emptyfallback，setspacing128/separation32/salts923810292与918238452；配置不等已生成。','processors':'两表custom goety:waterlogging_stop_processor 后rule五箱/桶种类append_loot；F01goety:chests/shack_potion/F02vanillapillageroutpost，output原chestwaterloggedfalse/barrelopenfalse及3goetychest类型原留。不是只改loot而保留所有state，也不是自动发奖；两loot单Jar缺不环境缺失，processor未执行。','actual_scope':'仅各whole/cutaway/y6三张共6PNG和原用途/破损资料排除；其他27张只是生成未查看，不称33实际研究、2完整相关通过或已逐层阅。F01魔法居处不凭三个grind冒相关工坊，F02明显原残塔不补盖/改void后冒完整。0newpending/formal0，不要求Main为本批重复独立审。','prior':'097F01和098F01各最多1待独立审沿各封存收据保留；095F02已097合并接受1，099只carry不重计。不变COD4的153/gap847。','scope_limit':'不Java/Gradle/游戏/QA/唤醒/声音亮度/存档实例/Jar/产品/清单/任务/指南针/建模贴图/网络/推送。'})
prev=ROOT/'docs/architecture/research-20261104-smithy-098';put('task-scope-boundary.json',json.loads((prev/'task-scope-boundary.json').read_text()));put('carried-forward-pending.json',{'previous_batch_receipt':bind(prev/'RECEIPT.json'),'current_batch_new_pending':0,'prior_pending':[{'batch':n,'id':'F01','maximum':1,'manual':bind(ROOT/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json'),'receipt':bind(ROOT/f'docs/architecture/research-20261104-smithy-{n:03d}/RECEIPT.json')}for n in [97,98]],'095F02_already_resolved_097_not_new_admission':True,'older_pending_not_cancelled':True,'not_master_todo_backup':True})
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'));verify_bindings(get('carried-forward-pending.json'))
check('33generated6actual27unviewed counts',len(list(OUT.glob('*.png')))==33 and len(viewed)==6 and len(get('visual-reading-boundary.json')['not_viewed_generated'])==27)
check('0fullrelatedstudies0pending0credit',get('manual-review.json')['complete_whole_reference_studies']==get('manual-review.json')['pending_maximum']==get('manual-review.json')['formal_credit_added']==0)
put('verification.json',{'status':'PASS_CURRENT_PRELIMINARY_SCREENING_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'native_acceptance':False,'formal_credit_added':0,'java_run':False,'all_tasks_complete':False})
status='SEALED_TWO_PRELIMINARY_RELEVANCE_RUIN_EXCLUSIONS_ZERO_COMPLETE_STUDIES'
put('session.json',{'batch':99,'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_png':33,'actual_images_viewed':6,'unviewed_generated':27,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'prior097_098_F01_pending_preserved':True,'latest_independent_admission_binding':bind(OUT/'latest-independent-admissions.json'),'cumulative_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'100继续其他固定本地完整相关来源；不重研本批已排除魔法住屋/残塔，不把27未看图转实际研究。'})
put('active-checkpoint.json',{'batch':99,'status':status,'actual_images_viewed':6,'complete_whole_reference_studies':0,'formal_credit_added':0,'java_run':False,'all_tasks_complete':False,'verification':bind(OUT/'verification.json'),'next_batch':100})
(OUT/'HANDOFF.md').write_text('099仅初步用途/毁损筛出，不完整参考研究：两源生成33PNG，只实际查看每源whole/cutaway/y6共6，27未看图逐个标记绑定，不报33实际/2通过。F01Goetypristine_shack23×34×28/DV3465，21786记录=5522非air16264air/110省略；魔法炼药住屋，3grind分别原堆叠/吊挂、witchcauldron/两brew/书台/球/上两床，4实体witch/warlock/两fly；无furnace/smith/anvil，工坊适用未证0。F02snowy_abandoned_tower19×20×18/DV3465，6826=2606非air4220air/14省略，显式残墙缺屋盖，散两空unlitblast/砧/壁磨具，voidfluid30/voidblock40/major16/minor25/flame7不当lava；9,6,7generator原tickCounter1/id endsent_generator_block_entity不执行、不称已生怪；无床梯门/entities，毁损完整性0。不修源/补盖/搬炉冒完整建筑。\n\n339历史archive/member及同源别名/rawroleoccupancy渲染前排除，未重历史验收；原全NBT/实体/BE/材质/元信息/上下文保存核对，未称全层/519state/27未看图已人工读。两root7/max80/absolute-5/surface/expansionfalse，原未设terrain_adaptation，不编none/beardthin。独立single1rigid/各lootprocessor/emptyfallback；setspacing128/separation32/salts923810292/918238452。各processor custom waterlogging_stop+五箱桶类型rule appendloot，F01Goetyshackpotion/F02vanillapillageroutpost。配置不执行/不发奖，两loot单Jar缺不环境缺失。文件名1.3.8测试版但actualForge1.3.7/Teamk1sak1/CodeLGPL2.1AssetsARR/pack15，requiredGoety2.5.51.0+差异保留，不编Fabric或兼容。\n\n当前0完整相关研究/0newpending/formal0；097F01/098F01最多各1待Main独立审仍沿封存收据保留，095F02已097合并1只carry不重计；COD4仍153差847，不达1000、不制作/清单删除。无Java/QA/游戏/音量亮度唤醒/原存档实例/共享Jar/产品/任务/指南针/模型贴图/网络/推送。下一100继续其他固定本地完整相关来源，不反复本批0，不用未看图凑数。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'actual_current_images_viewed':6,'generated_png':33,'unviewed_png':27,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'actual_images_viewed':6,'complete_studies':0,'pending':0,'credit':0},ensure_ascii=False))
