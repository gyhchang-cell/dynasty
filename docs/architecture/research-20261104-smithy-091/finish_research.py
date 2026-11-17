import json,hashlib,math
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
sources=json.loads((OUT/'sources.json').read_text())['candidates'];raw=json.loads((OUT/'raw-source-audit.json').read_text())['candidates'];functional=[]
for a in raw:
 d=a['nbt_decoded_original'];pal=d.get('palette')or d['palettes'][0]
 functional.append({'id':a['id'],'stored_records':len(d['blocks']),'declared_volume':math.prod(d['size']),'omitted_positions':math.prod(d['size'])-len(d['blocks']),'explicit_air':a['air'],'nonair':a['nonair'],'entities_original':d.get('entities',[]),'functional_states':[{'pos':b['pos'],'state':pal[b['state']],'original_block_entity':b.get('nbt')}for b in d['blocks']if b.get('nbt')or any(w in pal[b['state']]['Name']for w in ['door','furnace','smithing','grindstone','bed','lava','water','stairs'])]})
put('functional-evidence.json',{'candidates':functional,'sparse_omission_not_air':True,'native_function_not_verified':True})
observations=[
{'layout':'8×7单体泥/根围护小冷工屋，西门入北横段、向东再折南进入工具台窄端，是同层短L形连续室，不是两个独立房。既有068F02长L冷室及084F02高低L工作翼已覆盖主要空间组织，当前短臂/泥根不提新信用。',
'proportion':'8×11×7/DV3465，声明616格仅423records=381非air+42显式air，另193省略；entities空。实际地板y2、使用y3，底部y0/1为实泥根基，不是悬空吊脚生活层，11高大部分是高屋盖。',
'facade':'mud141/muddy_mangrove_roots157/mangrove_roots56/packed_mud5围护和基裙，通用灰图不是石墙。西门(1,3/4,2)east/right/closed，西侧三bottom mangrove阶在x0,y2,z1..3，门位z2，不把west入口socketz4当实际门。',
'roof':'主盖是逐级收进泥/红树根方块高盖；6spruce bottomstairs位于y6/8、两组各3作屋面细部，无室内连续登楼路径，不因bottom属性就叫楼梯。无床梯或上层地板，高盖空腔不是阁楼。',
'materials':'唯一smithing_table(5,3,4)在东南小端，无箱/loot、炉、砂轮、岩浆、水、火或床。两lantern分别低/高悬挂不是两人物；原根方块含孔隙的碰撞/观感未由整格示意图证明。',
'circulation':'门内(2/3/4/5,3,2)显式air，东折(5,3,3)air到台北服务面；西socket(0,2,4)empty/finalstructure_void，和门前台阶不同位。室内(4,3,3)up_north接实际swamp/vines feature池/finalair，是装饰接口不是NPC/第二入口/待补室翼。',
'terrain':'底泥根整体纳入原体，未必还原世界水位/承托。选屋weight1/single_pool_element/rigid/mossify5rules+structurevoidprocessor。藤蔓feature额外生长未执行，完整屋体不等山脚生态、雨避或任务接入验收。'},
{'layout':'9×10单体，南露天泥砖热作业台/双熔岩槽接北封闭小冷工储室；南门分内外，内外各1砂轮，北西箱。属既有057前热棚后冷室和067F02外热台接冷室组织近族；根形屋盖、无上阁和转门方向不独立增信用。',
'proportion':'9×11×10/DV3465，声明990格仅646records=549非air+97显式air，另344省略；entities空。地板y2/使用y3，同层热台和冷室，下y0/1实泥根基非架空工作层，11高不当11层或睡层。',
'facade':'泥201/带泥红树根150/红树根94包北室，南泥砖57/墙5/阶5形成热台。南门(2,3/4,5)north/right/closed通北室，未把door facingnorth说成北立面门；无玻璃板/床/NPC。',
'roof':'北高泥根收进盖完整，南东泥砖炉构上突且无独立完整遮棚；3bottom mudbrickstairs在(3,5,7)/(3,6,6)/(4,6,6)为高炉构细部，不是可走楼梯。5mangroveslab细部非整木楼层，源示意无实际纹理/碰撞。',
'materials':'南台两原level0lava(4,3,7)/(4,3,8)为同一长热槽，不拆两铺。南外floor/east砂轮(1,3,8)，北室floor/east砂轮(5,3,3)，箱(2,3,2)south/single/dry/原weaponsmithloot/seed-7350936850883811685。无炉/铁砧/锻造台/水，不编完整热锻或淬火获取链。',
'circulation':'西socket(0,2,4)empty/finalgrassblock不等实际门；西南两mudbrickbottom阶(0,2,7/8)east进南台，沿(2,3,8..6)air到南门，再北室(2,3,4/3)air抵箱/内砂轮。室内(4,3,3)up_west同接vines/finalair，非村民池。熔岩/铁栏/泥砖净空及NPC避险未验。',
'terrain':'南热台与北高根屋共用实基，不欠独立房翼；藤蔓为实际featuredecor而非第二建筑。根tag/structure参数只读，未实测泥根防火、世界水位、山脚承托或原生任务付款。与067外热前场/冷室/箱区及057基本家族相近，hold0。'}]
numbers=['057','061','067','068','070','084','087'];bindings=[bind(next((ROOT/'docs/architecture').glob(f'research-*smithy-{n}/manual-review.json')))for n in numbers]
comparisons=['与068F02双门入L冷室、084F02南高宽室接北低窄工具翼的保存判断比较：本例短L、单门、无箱只一台仍是同层连续折向冷室，不凭高泥根盖/缩短两臂/无箱提出独立。与061F03高石基/南栏台不同，但差异不足改变L族。','与057F01统一盖前热后储及057F03前热棚/主室/阁层、067F02西凹口北热端接长冷室/南箱比较：本例南热槽/北小冷室/同层内外磨工没有新空间组织；去上阁/换泥根/门朝向不单独计。与070F02架空热层和上生活层、087F01相邻错层并闭两室不同，但不能据此脱离前热后冷家族。']
cases=[]
for a,obs,comparison in zip(sources,observations,comparisons):
 cases.append({**a,'observations':obs,'images_actually_viewed':[bind(p)for p in sorted(OUT.glob(a['id']+'-*.png'))],'whole_boundary':'单源完整围护屋盖/地板及使用区；vines是装饰feature接口非缺房，省略格与显式air分开。','semantic_family_comparison':{'comparison':comparison,'saved_existing_judgments_reused_not_reaccepted':bindings,'proposal_maximum':0},'credit_proposal_maximum':0,'formal_credit_added':0,'status':'HELD_ZERO_EXISTING_COLD_L_OR_FRONT_HEAT_REAR_ROOM_FAMILY','native_acceptance':False})
put('manual-review.json',{'cases':cases,'source_bodies_studied':2,'whole_smithy_bodies_studied':2,'generated_current_png':18,'actual_current_images_viewed':18,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'no_independent_self_admission':True})
ctx=json.loads((OUT/'source-context.json').read_text())
put('source-context-reading.json',{'metadata':'固定RS7.1.19+1.20.1-forge/TelepathicGrunt/GNULGPLv3实际mods.toml全文，secondary原pack.mcmeta/format15保存，未复制作者资产制作。','pre_render':'重用090预筛证据并针对当前2源更新到323历史archive/member+全同源字节别名，均无旧精确及轮内精确才渲染；不是对旧接受重新验收。','selected_elements':'两选屋weight1/minecraft:single_pool_element/rigid，不是其他RS多为legacy。实际选屋mossify有5rules：moss_carpet .05air，dirtpath .1mud，muddyroots .2mud，mud .1muddyroots(axisy)，packedmud .02muddyroots(axisy)，之后RSstructure_void_processor。全部实际读/保存、未运行，概率不是最终占比。','root':'实际RSgeneric_jigsaw_structure/startswamptowncenters/size6/validbiomeradius1/terrainheightradius2/allowedrange22/WORLDSURFACEWG/startabsolute0/beardthin/useboundingboxhacktrue，无显式maxdistance不挪116。','biomes':'根tag仅collectionswamps，展开原swamp/mangroveswamp2mandatory+2optionaltag(#forge:is_swamp/#c:swamp)；tag不是2栋/2安装证明。','vines':'实际swamp/vines池fallback指自身、1weight1 rigidfeature_pool_element，feature同名placed_feature placement[]→configured typeRSstructure_vines/configattempts10,length3,xz_range4,height_range10。两室内jigsaw是藤蔓而非villager；未运行不声称10条已生或原屋体已有藤。','towncenter_processor':'六个towncenter元素源码保存不当6参考；实际中心path_randomizer只上下文不替代housemossify。原顺序3ruleprocessors(2+9+2rules)，再post_process delegates[air对worldroots/moss carpet写bedrock两rule、ignoreair、bedrock回air一rule、RSairprocessor/removefloating/ignoreair+void]。原dirt→mud仍带snowyfalse异常原样保存不修源。','path_randomizer_details':'第一mudbrick→mud/mud→dirtpath；第二path .3mud/.05muddyroots/.2grass、水中path .985planks/回water，水中grass .015water/其余planks，水中dirtwater、通用dirtmud snowyfalse；第三grass在grass位置.95mud/mud在mud位置.95grass。只是完整配置阅读，不推执行顺序的最终概率或世界碰撞。','actual_missing':{a['id']:a['missing']for a in ctx['candidates']},'missing_boundary':'F01无missing，F02vanillaweaponsmithloot不在单RSJar，不等环境缺失；箱原seed保留。','view_limits':'18本批PNG均实际查看，灰mud/roots不是石，roots/门/台阶/半格全格示意非精确碰撞，未运行processor/feature/实体/原生地形。sparse未存193/344不同42/97显式air。','runtime':'无Java/Gradle/游戏/QA/声音亮度唤醒；无用户实例/原存档/共享Jar/产品或清单改动。'})
put('applicable-principles.json',{'principles':['泥根材质变化与高盖不让既有冷L/前热后冷布局重复计数。','原feature_pool接口必须沿真实placed/configured资源读，不当NPC或缺翼。','底部实泥根和高包覆盖不能误称架空二层；高处bottomstairs要看实际路径。','火台独立立面/冷工服务面可借鉴，但原火源相邻根材防火和净空仍须以后实机验证。'],'implemented_product':False})
previous=ROOT/'docs/architecture/research-20261104-smithy-090'
put('task-scope-boundary.json',json.loads((previous/'task-scope-boundary.json').read_text()))
latest=json.loads((previous/'latest-independent-admissions.json').read_text());latest['previous_binding']=bind(previous/'latest-independent-admissions.json');latest['current_batch_formal_credit_added']=0;put('latest-independent-admissions.json',latest)
put('session.json',{'batch':91,'status':'MANUAL_STUDY_COMPLETE_VERIFICATION_PENDING','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'generated_png':18,'actual_images_viewed':18,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'latest_independent_admission_binding':bind(OUT/'latest-independent-admissions.json'),'cumulative_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'092继续固定本地真实完整且空间不同来源；不要重复079/080/087接受，不提前制作或删清单。'})
print('18actually viewed PNG;14observations;2whole held0;no production or Java')
