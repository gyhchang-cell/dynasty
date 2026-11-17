import json,hashlib,itertools,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=P.parent/'research-20261104-smithy-227';BASE=P.parent/'research-20261104-smithy-224'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];c={tuple(b['pos']):b for b in n['blocks']};pal=n['palette']
ck('host source eligible',read(P/'pre-render-history-screen.json')['rows'][0]['eligible_for_new_source_study'])
ck('16x8x14 DV3578 89palette19BE3entity',n['size']==[16,8,14] and n['DataVersion']==3578 and len(pal)==89 and sum('nbt'in b for b in n['blocks'])==19 and len(n['entities'])==3)
ck('all1792positions 713nonair1079air',len(c)==1792 and r['nonair']==713 and r['air']==1079)
lines=['Original state indices; rows z columns x; all declared positions stored.']
for y in range(8):
 lines.append(f'y={y}')
 for z in range(14):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c[(x,y,z)]['state']for x in range(16)])))
ck('all8layers112RLE exact',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
reuse=read(P/'reused-component.json');b=reuse['source_binding'];ck('reused224 unique component binding',bind(b['path'])['sha256']==b['sha256'] and reuse['component']==read(b['path'])['candidates'][1]);ck('old child RLE exact',(P/'F04-full-layer-index-rle.txt').read_bytes()==(BASE/'F04-full-layer-index-rle.txt').read_bytes())
a=read(P/'derived-assembly.json');d={tuple(b['pos']):b['state']for b in read(P/'derived-source-cells.json')['cells']}
ck('parent original up_west aligned',pal[c[(11,0,9)]['state']]['Properties']['orientation']=='up_west' and c[(11,0,9)]['nbt']['joint']=='aligned')
ck('CW90 closure origin13,1,8 zero overlap716nonair',a['module_origin']==[13,1,8] and a['module_box']==[[11,1,8],[13,2,10]] and not a['overlap_nonair'] and a['derived_nonair']==716)
ck('rotated chest and anvil south',all(d[q]['Properties']['facing']=='south'for q in [(13,1,8),(13,1,10)]))
ck('work services air and chest top clear',all(d[q]['Name']=='minecraft:air'for q in [(11,1,9),(11,2,9),(12,1,9),(12,2,9),(13,1,9),(13,2,9),(13,2,8)]))
ck('four west ladder cells and sign at upper landing',all(d[(5,y,5)]['Name']=='minecraft:ladder'and d[(5,y,5)]['Properties']['facing']=='west'for y in range(1,5)) and d[(5,5,5)]['Name']=='minecraft:air' and d[(4,4,5)]['Name']=='minecraft:jungle_wall_sign')
ck('three itemframes empty not residents',all(e['nbt']['id']=='minecraft:item_frame' and 'Item'not in e['nbt']for e in n['entities']))
ck('seven source diagrams viewed',len(list(P.glob('*.png')))==7)
ctx=read(P/'source-context.json')['candidates'][0]['contexts'];oldctx={c['member']:c for row in read(BASE/'source-context.json')['candidates']for c in row['contexts']}
with zipfile.ZipFile(r['source_archive'])as z:
 ck('archive and original member fixed',bind(r['source_archive'])['sha256']==r['source_archive_sha256'] and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ck('three full context objects exact reuse',len(ctx)==3 and all(c==oldctx[c['member']] and hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in ctx))
put('support-context-reuse.json',dict(bindings=[bind(BASE/f)for f in ['source-context.json','extended-generation-context.json','vanilla-local-support-context.json']],source_contexts_reused_exact=ctx,root_tag_townsset=read(BASE/'extended-generation-context.json'),vanilla=read(BASE/'vanilla-local-support-context.json'),new_full_JSON_reads=0,old_NBT_or_PNG_reopened=False))
comparisons=[]
for num in [224,225,226]:
 f=P.parent/f'research-20261104-smithy-{num}/manual-review.json';o=read(f);comparisons.append(dict(binding=bind(f),seven_dimensions=o['seven_dimensions'],limits=o['limits']))
reason='当前东低工具间对西下床室/内竖梯上阅读小室、北双床室与南西单床室经铺地通道相接。与225东工具间/西下床/北梯上书室的功能关系接近；虽竖梯移西、北变双床且外缘加围栏坪，尚不能把这些位置/床数差异确认为独立完整空间原则。226西双工具间和错层庭院不同，224内折阶上卧室亦不同，但不能据此绕过225近族疑问。作者HOLD0，保留全栋证据而不提信用；不是断言两个源字节相同或全库已穷尽。'
put('saved-complete-family-comparison.json',dict(comparisons=comparisons,judgment=reason,old_NBT_or_PNG_reopened=False))
seven=dict(layout='原16×8×14大屋2加唯一工具匠模块为一个围铺地通道的工住整体：东南独立低盖工具间朝西门入，中北双床室朝南门，西中底床/箱室朝东门并沿内东墙竖梯到阅读小室，南西另单床室朝东门。东北外侧带低围栏/座椅坪。上阅读空间不是独立新屋，床室和工具间不拆分计数。',proportion='DV3578新宿主89palette/19BE/3entity，全1792格713非air1079air无省略；旧组件DV3105/5palette/2BE/18格完整证据复用。共1810源记录有18内部重合，bbox1792，忽略air/final后716nonair。新8层112RLE1792格与7PNG全读；底use1/上阅读use4，最高y7薄檐不等8层，四完整床对不当四居民/四建筑。',facade='155bricks墙、101andesiteslab基铺地，darkoak板31/上TOPslab，spruce木盖分主横屋和两侧低翼。19blackglass窄窗，四扇门上下8块，两个空白jungle标牌；东北junglefence两块有南北连接并非完整高墙。分类图灰棕不等源纹理。',roof='spruceplanks61/slab121/stairs30与trapdoor74构成北横长低盖、西阅读上盖、东工具低盖和南西低盖的错高搭接。西屋上使用层floor3/use4，盖y6/7；没有第三层通路。东北外坪薄件/檐边不是高工区；源itemframe不在格图渲染，不据屋顶造型编额外室。',materials='CW90后胸13,1,8south、砧13,1,10south、smithingtable12,1,8。toolsmithloot与宿主胸3,1,5east/6,1,3east的savannahouse均无seed，仅候选非实存；无炉/lava完整热锻链。四完整床对：西中cyan3,1,6foot/7headsouth，南西lightblue5,1,10foot/11headsouth，北blue6/7,1,2head/footwest与10,1,2head/3footnorth。上书架/座椅/盆花非武器机台；三entity为空item_frame无Item，不是人/钟声或素材授权。',circulation='东工具门10,1/2,10west/right/closed，内11,1/2,9、12,1/2,9、13,1/2,9air为工作横排，胸顶13,2,8air。西中门6,1/2,7east/right；梯5,y1..4,z5west，下西侧4,1/2,5air，顶5,5,5air，西上落脚4,3,5TOPdarkoakslab，但4,4,5为jungle_wall_sign而非air、4,5,5air；标牌和梯离开碰撞未验，不声称出梯无阻。北门8,1/2,4south/right，南西门7,1/2,10east/left；南socket8,0,13finalandesite上8,1,13openbottomtrapdoor非air，内8,2,12TOPclosedtrapdoor。静态分路非NPC/门/箱盖/工具交互验收。',ground_support='parentup_west/aligned11,0,9，childdown_south/aligned1,0,2以CW90(-z,y,x)变down_west，origin13,1,8，box11..13/1..2/8..10全内含无原nonair覆盖。宿主接口finaldarkoak板，其他五村民socketfinaldoubleandesiteslab属性保留，不以air清世界。原houseprocessor未执行，Legacy/Single/Jigsaw/canAttach读段与root/tag/townsset/vanilla支持复用已核固定证据。towncenter/road/optionalbiome/坡地原生未验。')
limits=['完整新源研究完成但作者HOLD0/新提议0，因与225整体功能组织近族差异尚不足，不拿梯位/床数/颜色/轮廓/同组件旋转凑独立whole。','新89palette全props/19BE/3空itemframe全文、8层112RLE1792格/7PNG实际读看；旧组件5palette/2BE/2层6RLE18格复用不新增源信用，1810记录非独立worldslots。','上梯落脚4,4,5原jungle_wall_sign不是air；nonair不自动实墙或已可穿行。门/梯/薄件/头顶/箱盖/砧台范围/NPC/街路原生未验；分类源格图非原纹理或碰撞。','houses large2权3/chance1工具权1及processor完整对象与224精确复用，新fullJSON0；其它选项、fallback、概率和Properties解释不扩大。','无炉/热锻链/实际材料/交易扣款/获取回执，四床对/五村民socket非实际居民；3空itemframe不当人物或新模型，中文任务指南针未接入。','root/tag/townsset/vanilla和源码仅既有限定证据复用；固定本地不证明远端最新或DV升级/native生成/群系注册/地形落地。','另按Main最终224文件实际读完整后仅本228首次carry NPC01整栋1，新228自身0；224原七维八限/Main12+8/实际响应完整保留，221first224及157/203之后不重复，225/226仍待Main。COD4153/847不变，NPC累计未知，1000未达不制作。','只本地建筑研究，不运行Java/游戏/联网/UI/声音亮度/焦点，不碰实例/原档/Jar/专业资产/主清单/Git，不删除未验提示词，不声称全部完成或工时。']
put('manual-review.json',dict(batch=228,case='F01_HOST_PLUS_REUSED224F04',seven_dimensions=seven,limits=limits,status='COMPLETE_WHOLE_STUDY_HOLD0_NEAR225_ORGANIZATION',new_reference_proposal=0,formal_credit_added=0,native_acceptance=False,semantic_hold_reason=reason,actual_reading=dict(new_palette=89,new_BE=19,new_entities=3,new_layers=8,new_RLE_rows=112,new_positions=1792,new_PNG_viewed=7,new_full_JSON=0,old_PNG_reopened=0)))
put('key-source-derived-route-cells.json',dict(cells=[dict(pos=q,state=s)for q,s in sorted(d.items())if (10<=q[0]<=14 and 7<=q[2]<=11 and q[1]<=3)or(3<=q[0]<=6 and 4<=q[2]<=7 and q[1]<=5)or(7<=q[0]<=10 and q[2]>=12 and q[1]<=3)],static_not_native=True))
f=ROOT/'docs/cod4/audit-20261022/coordinator-architecture224-actual-author-ACK-final-acceptance-20261111.json';final=read(f);ack=read(PRE/'actual-author-ACK-224.json');old=read(BASE/'manual-review.json')
ck('Main final224 exact and allows first later carry',bind(f)['sha256']=='c3c1596cb2015db7ae054ef3420ddd2a526957d3cffea8f269efaf7f05516ce5' and bind(f)['bytes']==30194 and final['formal_carry_pending'] and final['current_accepted_NPC01_whole_maximum']==1)
ck('original224 seven/eight exact',final['original_seven_dimensions']==old['seven_dimensions'] and final['original_eight_limits']==old['limits'])
ck('all20 author responses exact',final['actual_finding_responses']==ack['finding_responses'] and final['actual_limit_responses']==ack['limit_responses'])
ck('ACK and Main review bindings fixed',bind(PRE/'actual-author-ACK-224.json')==final['actual_author_ACK'] and bind(final['Main_whole_review']['path'])==final['Main_whole_review'])
carry=dict(case='224F01_HOST_PLUS_F04_TOOLSMITH',first_bound_batch=228,increment=1,scope='NPC01 complete related cold-work dwelling architecture only',COD4_increment=0,NPC01_cumulative_total=None,final_acceptance_binding=bind(f),original_whole_manual_binding=bind(BASE/'manual-review.json'),original_whole_receipt_binding=bind(BASE/'RECEIPT.json'),actual_author_ACK_binding=bind(PRE/'actual-author-ACK-224.json'),actual_author_receipt_binding=bind(PRE/'RECEIPT.json'),final_acceptance_entire_object=final,original_ACK_entire_object=ack,not_production_or_TODO_authority=True)
put('first-carry-224.json',carry)
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous227_binding=bind(PRE/name),older_history_retained=True,accepted224_first228=carry,current_batch_formal_credit_added=1,accepted221_first224_current228_increment=0,accepted157_first206_current228_increment=0,accepted203_first209_current228_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
 if name.startswith('carried'):o.update(resolved224_accepted_first228=True,active_pending_including_earlier=['225F01_HOST_PLUS_REUSED224F04','226F01_HOST_PLUS_TWO_REUSED224F04'],current_batch_new_pending=0,current_batch_pending_cases=[],current228_HOLD0=True,not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current227'];now=bind(b['path']);protected.append(dict(last227_checkpoint=b,current228=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('eight protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected))
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=228,status='224_FIRST_CARRY1_AND_NEW_LARGEHOUSE2_WHOLE_HOLD0',formal_credit_added=1,formal_credit_scope='224 previously finally accepted NPC01 only;new228 HOLD0',accepted224_first228_current_increment=1,accepted221_first224_current_increment=0,accepted157_first206_current_increment=0,accepted203_first209_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=['225F01_HOST_PLUS_REUSED224F04','226F01_HOST_PLUS_TWO_REUSED224F04'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not o['unchanged']for o in protected),next='225/226 remain Main pending;228 whole HOLD0 retained,224 first228 only future0,221 first224 later0. Continue different related complete organization.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),protected_unchanged=sum(o['unchanged']for o in protected)),ensure_ascii=False))
