import json,hashlib,itertools,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=P.parent/'research-20261104-smithy-230';BASE=P.parent/'research-20261104-smithy-225'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];cells={tuple(b['pos']):b for b in n['blocks']}
def st(q):return pal[cells[q]['state']]
ck('eligible bounded229screen with delta',read(P/'pre-render-history-screen.json')['rows'][0]['eligible_for_new_source_study'])
ck('10x10x5 DV3578 41palette12BE0entities',n['size']==[10,10,5] and n['DataVersion']==3578 and len(pal)==41 and sum('nbt'in b for b in n['blocks'])==12 and n['entities']==[])
ck('all500source330solid170air',len(cells)==500 and r['nonair']==330 and r['air']==170)
lines=['Original palette-index RLE; rows z, columns x; all source positions stored.']
for y in range(10):
 lines.append(f'y={y}')
 for z in range(5):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([cells[(x,y,z)]['state']for x in range(10)])))
ck('10layers50RLE exact',(P/'F18-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
ck('7PNG actual viewed',len(list(P.glob('*.png')))==7)
with zipfile.ZipFile(r['source_archive'])as z:
 ck('source archive/member exact',bind(r['source_archive'])['sha256']==r['source_archive_sha256'] and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json')['candidates'][0]['contexts'];ck('4 full current context exact',len(ctx)==4 and all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in ctx))
ck('empty unlit stove not production',st((5,1,3))['Name']=='minecraft:furnace'and st((5,1,3))['Properties']['lit']=='false'and cells[(5,1,3)]['nbt']['Items']==[] and cells[(5,1,3)]['nbt']['BurnTime']==0)
ck('no actual smith devices',not any(p['Name']in ['minecraft:anvil','minecraft:chipped_anvil','minecraft:damaged_anvil','minecraft:smithing_table','minecraft:grindstone','minecraft:blast_furnace','minecraft:lava']for p in pal))
ck('north stove service foot air head plate',st((5,1,2))['Name']=='minecraft:air' and st((5,2,2))['Name']=='minecraft:air' and st((5,2,3))['Name']=='minecraft:stone_pressure_plate')
ck('upper door outside sign not air',st((6,5,3))['Name']=='minecraft:spruce_door' and st((7,5,3))['Name']=='minecraft:birch_wall_sign')
reason='整栋是狭长双层家居：底床位/厨房空炉及食物桶，北内木阶上第二床室与向东露台。原设备只有空未燃炉，主要loot食物/家居，未见工具维护、锻造或材料处理专用空间；不能仅凭furnace名称把住宅提为NPC01铁匠参考。231作者HOLD0，保留完整建筑方法证据用于后续适用性比较，不向不明NPC05/06或COD4挪信用。'
comparisons=[]
for num in [225,229]:
 f=P.parent/f'research-20261104-smithy-{num}/manual-review.json';o=read(f);comparisons.append(dict(binding=bind(f),seven_dimensions=o['seven_dimensions'],limits=o['limits']))
put('saved-complete-family-comparison.json',dict(comparisons=comparisons,judgment=reason,old_NBT_or_PNG_reopened=False))
seven=dict(layout='原10×10×5完整狭长二层住宅：下部一体室西灰床、南墙中空炉/台面/食桶，东南地门入；北内墙向西上升直木阶接上西床/箱室，东隔门外是上露台。两房/两床不是两栋；无另profession模块。',proportion='DV3578/41palette/12BE/0entities，500格330非air170air，无省略；10层50RLE500格/7PNG全读。floor0/use1与floor4/use5两使用层，高10非十层；图源三jigsaw未final替换，非最终成屋非air数。',facade='178 quartz_bricks围护/基座为白色石英砖，不是图中棕砖；2bricks及46brick_slab构成红砖屋盖，42spruceplanks作双楼板，7cyanpane采光。两sprucedoor上下4块是两门，两个空白birch墙牌不当中文牌。狭深长边封墙、东西开窗，不将分类颜色认作真实外观。',roof='西部主二层体上y8砖slab多double/局部top、y9中脊bottomslab，x8/9东露台上敞。白quartzstairs8围露台边，砖主盖不覆盖整10长bbox；上无第三层通路。上露台lantern7,7,1hanging及盆杜鹃9,6,4只布置，不当承重构。',materials='底灰床1,1,1head/1,1,2footnorth，上灰床1,5,2foot/1,5,3headsouth。底炉5,1,3north/litfalse，Items[]/CookTime0/BurnTime0/RecipesUsed{}，顶5,2,3stonepressureplate非第二炉。桶4,2,3north为foodloot/seed-1807518448088190358；上箱4,6,3north为medhouse/seed-3297533041382979511，随机候选非现存食材或金属库存。无砧/锻造台/磨石/高炉/lava，不能叫热锻工住。',circulation='底门9,1/2,3east/left/closed，内8,1/2,3air，旁8,1,2top/outerrightnorthbirchstairs非air；中x7..5,1/2,2air为床/厨房通路，炉北5,1/2,2air但无原生互动验收。北木阶5,2,1west/bottom→4,3,1west/bottom→3,4,1west/bottom，分别下top eaststair支承，向西2,4,1sprucefloor/use5上air；只是静态连续高差。上箱northfront4,5/6,2air，箱top4,7,3air；上门6,5/6,3east/rightclosed，外7,5,3southbirchwall_sign非air、7,6,3air，东8,4,3板上8,5/6,3air；不声称标牌/门/楼梯碰撞/NPC或箱盖已通过。',ground_support='floor0外围quartz实基/内spruce整铺，底9,0,3andesiteslabtype double保留Properties。两个up_east/rollable村民socket3,0,2与3,4,2finalspruce板，东9,1,2east_up/aligned入口finalquartz不是air，不据此封死门或称连接已通。housesregular19项各weight1/legacyrigid/emptyfallback只是候选池，不测实放概率；street三0.25andesiteslab替换未执行不当75%。vanillasavanna村民池原Jar缺失，复用224已读证据仅背景不新计读；本研究未重建root/tag/townscenter/road，街/地形接合未知。')
limits=['新整栋源研究完成但作者HOLD0/新提议0：用途主要住宅与食物厨房，不以炉名凑NPC01铁匠相关参考，也不挪计NPC05/06或COD4。','本批41palette全props/12BE/entities[]、10层50RLE500位置、7PNG/4来源上下文全文实际读。旧历史screen只固定证据加229/230增量，hash排exact不是语义唯一。','分类源格图非原MC纹理/碰撞，三jigsaw未final，330源nonair非最终生成数；石英砖图棕色不代表brick实际材料。','北直梯静态、上下床对/两villager socket非实际NPC，炉north前air和上箱topair不等互动/箱盖通过；上门外birchsign非air、薄件/阶/门/头部未实机验。','炉为空未燃、桶箱仅带固定seed的loot候选，非食物/金属真实库存或制作/付款/交易获取回执，无中文任务指南针接入。','legacy/rigid与三0.25processor未运行；本地来源非远端最新，root/tag/道路/地形和DV3578升级未原生验。modJar缺失vanilla村民表不编补新read；仅精确旧224支持复用不新计credit。','本231另对225最终接受整栋首次carry NPC011，保存完整final/ACK/原7维8限；后续0。224first228/221first224及157/203以后不重复，226/229仍pending、228HOLD0。COD4153/847，NPC累计未知，1000未达不制作。','不运行Java游戏联网UI，不改声音亮度焦点唤醒/实例原档共享Jar专业资产主清单Git；不删未验提示词，不声明全部任务完成或工时达标。']
put('manual-review.json',dict(batch=231,case='F18_MED_LARGE_HOUSE3',seven_dimensions=seven,limits=limits,status='COMPLETE_WHOLE_STUDY_HOLD0_INSUFFICIENT_SMITHY_RELEVANCE',new_reference_proposal=0,formal_credit_added=0,native_acceptance=False,semantic_hold_reason=reason,actual_reading=dict(new_palette=41,new_BE=12,new_entities=0,new_layers=10,new_RLE_rows=50,new_positions=500,new_PNG_viewed=7,current_full_JSON=4,old_PNG_reopened=0)))
f=ROOT/'docs/cod4/audit-20261022/coordinator-architecture225-actual-author-ACK-final-acceptance-20261111.json';final=read(f);ack=read(PRE/'actual-author-ACK-225.json');old=read(BASE/'manual-review.json')
ck('final225 exact max1 pending firstcarry',bind(f)['sha256']=='38db3aba2ba2ad68c6237c7666ba7f54c6231da2a1aa2f39f421dac0a77bf1e7' and bind(f)['bytes']==25301 and final['formal_carry_pending']and final['current_accepted_NPC01_whole_maximum']==1)
ck('original225seven/eight exact',final['original_seven_dimensions']==old['seven_dimensions']and final['original_eight_limits']==old['limits'])
ck('20actual author responses exact',final['actual_finding_responses']==ack['finding_responses']and final['actual_limit_responses']==ack['limit_responses'])
ck('ACK receipt Main bindings exact',bind(PRE/'actual-author-ACK-225.json')==final['actual_author_ACK']and bind(PRE/'RECEIPT.json')==final['author230_receipt']and bind(final['Main_whole_review']['path'])==final['Main_whole_review'])
carry=dict(case='225F01_HOST_PLUS_REUSED224F04',first_bound_batch=231,increment=1,scope='NPC01 complete related cold-work dwelling/library architecture only',COD4_increment=0,NPC01_cumulative_total=None,final_acceptance_binding=bind(f),original_whole_manual_binding=bind(BASE/'manual-review.json'),original_whole_receipt_binding=bind(BASE/'RECEIPT.json'),actual_author_ACK_binding=bind(PRE/'actual-author-ACK-225.json'),actual_author_receipt_binding=bind(PRE/'RECEIPT.json'),final_acceptance_entire_object=final,original_ACK_entire_object=ack,not_production_or_TODO_authority=True)
put('first-carry-225.json',carry)
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous230_binding=bind(PRE/name),older_history_retained=True,accepted225_first231=carry,current_batch_formal_credit_added=1,accepted224_first228_current231_increment=0,accepted221_first224_current231_increment=0,accepted157_first206_current231_increment=0,accepted203_first209_current231_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
 if name.startswith('carried'):o.update(resolved225_accepted_first231=True,active_pending_including_earlier=['226F01_HOST_PLUS_TWO_REUSED224F04','229F50_PIGLIN_STORAGE1'],current_batch_new_pending=0,current231_HOLD0=True,not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current230'];now=bind(b['path']);protected.append(dict(last230_checkpoint=b,current231=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('8protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected))
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=231,status='225_FIRST_CARRY1_AND_NEW_MED_HOUSE3_WHOLE_HOLD0',formal_credit_added=1,formal_credit_scope='225 previously finally accepted NPC01 only;new231 HOLD0',accepted225_first231_current_increment=1,accepted224_first228_current_increment=0,accepted221_first224_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=['226F01_HOST_PLUS_TWO_REUSED224F04','229F50_PIGLIN_STORAGE1'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='226/229 pendingMain,231 wholeHOLD0 residential relevance;225first231 only future0,224first228/221first224 later0. Continue different related complete organization with genuine work/material role.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
