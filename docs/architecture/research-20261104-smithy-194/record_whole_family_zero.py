import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent/'research-20261104-smithy-193';R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def rd(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=p.resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
a=rd(P/'raw-source-audit.json')['candidates'][0];r=a['nbt_decoded_original'];s=rd(P/'sources.json')['candidates'][0]
mp=R/'docs/cod4/audit-20261022/coordinator-smithy186-F04-island-outdoor-coldwork-whole-review-20261110.json';main=rd(mp)
comparison={'Main186_binding':bind(mp),'Main186_complete7_observations_preserved':main['Main_observations'],'Main186_all6_limits_preserved':main['limits'],'Main186_complete_whole_comparison_preserved':main['semantic_family_disposition']['whole_comparison'],'actual_reading':'本批完整实际读此7项/6限制及wholecomparison；不重读186原NBT/PNG/context，不重新接纳186；完整Main186原对象继续在admissions/carry沿用。','current_complete_case_comparison':'186完整既有家族为公共侧露天切石、单门私室内床箱。194北侧屋外切石带、东单门入同一床箱主室，外街路口方向与工位方位不同但依旧一公共冷作侧接一私人生活室。高蘑菇形壳/书架/高砧陈设未证可达上层或新加工私密层，不以装饰密度、矿物种类、图案、床色/屋顶/职业名加分。对现有已接纳outdoorwork/private-life家族保守0，不断言NBT完全相同。','decision':'COMPLETE_RELATED_SOURCE_STUDIED_FAMILY_ZERO','proposal_maximum':0,'formal_credit_added':0}
put('saved-complete-family-comparison.json',comparison)
obs={
'layout':'北侧外部切石(8,2,2)east在主体居室北围护外，位于低棚/陈设带；东单门(11,2/3,8)east入中央约x5..10/z5..10共同主室，北侧床head6,2,5/foot7,2,5west及箱9,2,4/9,2,10，没有第二私室、工艺厅或公共穿堂。高处5,5,9箱、四书架和9,5,7损坏砧为实存陈设，不凭名字当可达加工阁楼。',
'proportion':'17×21×17/DV3465，6069声明位置=6012存1267非air+4745显式air，57省略不当air。21层357行6069原索引RLE、164palette、68完整BE、9完整entities全实际读。地基mycelium在y0、主要地板y1/使用y2；屋壳抬高至y20装饰sculk，不是21层。',
'facade':'多种白石与木/羊毛构圆钝居室脚部，东单门、东西彩玻璃小窗，北部木/营火薄盖的作业附带。17个player_head为SkullOwner纹理装饰，未联网取图；分类图按整格/类别显示，不能声称原头雕样貌、精细块形或贴图全部视觉验收。',
'roof':'cyan_terracotta226构高帽形空壳，y8木半板檐圈、y9..18逐层不规则收拢，froglight/sculk/endrod散点装饰至y20；内部y6..11白石堆叠与环状陈设不是已验证的连续二层楼板。北侧32个campfire全部litfalse/Items[]作薄盖，不能称32炉或运行热工。',
'materials':'mycelium232承底，原palette并存无namespace的smooth_quartz110与minecraft:smooth_quartz37，保留原拼写不修源或声称当前解析成功。切石只有1、损坏砧1；无炉/高炉/锻造台。32营火、17头、3箱、4存书书架和陶罐/旗/空白牌只按原文，不为装备/产出编造ID。三箱均vanilla village_mason无seed；4书架各3book，9实体全物品展示框非NPC。',
'circulation':'东16,1,8east_up原empty/finalair是唯一外街socket，经东侧低台阶到11,2,8门；北作业带与床室分置门外/门内。6,1,6up_east为villager插槽最终spruce_planks，不当缺地板或二门。上部5..6高度有书架/箱/砧但未证从主室贯通的合法楼梯和落脚，不能称上下工艺循环、第三生活区或NPC可用阁楼；所有stairs/slab仅原状态阅读，未运行碰撞。',
'terrain':'y0为原存菌丝裙，57省略仅原边角保留；工作台8,2,2下8,1,2smooth_stone、再8,0,2mycelium，床下6/7,1,5oakplanks与y0原菌丝存在。整源基底/居室/外工位/壳有承托，不以补造地面解除182HOLD。housepool精确本源权2legacy/rigid/emptyprocessor，不需要组装房翼；外居民pool引用minecraft:village/mushroom/villagers在此Jar缺失，原生解析/其他包存在性未验，必须保留。'}
imgs=[bind(P/n)for n in ['F01-whole.png','F01-cutaway.png','F01-y0.png','F01-y1.png','F01-y2.png','F01-y5.png','F01-vertical.png']]
limits=['完整源空间研究通过不等新语义家族；本批family0，不新增pending，不增加正式参考数。','原minecraft:village/mushroom/villagers pool在源Jar缺失；不能虚构成trek命名空间或已生成村民。vanilla mason loot本Jar亦无，未读取外部定义；fallback plains terminators/root未追读。','164palette/68BE/9entity已全部阅读并原样保存；头纹理仅原base64/UUID文本读取，未联网加载或原生头雕渲染。9展示框含绝对Pos/UUID与模板局部pos两套，未测重定位/掉落。','高位砧、书架和箱的可达性未证，不凭高盖或环状陈设认定上层工作/生活动线。','32营火均未点燃只读，未运行Java/游戏/音效；3原生metadata与1完整housepool已读，不代表所有包/世界生成兼容。','已有186/174/190接纳均本批carry0，190首次仅193+1；064不转接受，182HOLD，157W01待审，NPC01累计未知，COD4仍153/847、NPC05+0。']
put('manual-review.json',{'cases':[{'id':'F01','source':s,'observations':obs,'limitations':limits,'images_actually_viewed':imgs,'semantic_family_comparison':comparison,'actual_complete_original_spatial_study':True,'status':'COMPLETE_RELATED_SOURCE_STUDIED_FAMILY_ZERO','credit_proposal_maximum':0,'formal_credit_added':0,'native_acceptance':False}],'new_complete_original_spatial_studies':1,'new_qualifying_related_reference_proposals':0,'formal_credit_added':0})
put('actual-reading-boundary.json',{'original_index_RLE':{'layers':list(range(21)),'rows':357,'declared_positions':6069,'actual_all_read':True,'explicitair_index':55,'omitted_marker':'?','omitted':57},'palette_all164_actual_read_chunks':['0..81','82..163'],'BE_all68_actual_read_chunks':['0..35','36..67'],'all9entities_actual_read':True,'full_context_JSON_actual_read':1,'full_metadata_actual_read':3,'all7PNG_actual_viewed':imgs,'priorMain186_written7observations6limits_wholecomparison_actual_read':True,'priororiginal186NBT_PNG_context_replayed':False,'new_formal_reference_credit':0})
for n in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=rd(O/n)
 if n.startswith('latest'):d['current_batch_formal_credit_added']=0;d['190first193_later_carry_increment_194']=0
 else:d['previous_batch_receipt']=bind(O/'RECEIPT.json');d['190first193_later_carry_increment_194']=0
 put(n,d)
ss={'batch':194,'status':'COMPLETE_MUSHROOM_STONEWORK_PRIVATE_HOUSE_STUDIED_EXISTING_FAMILY_ZERO','formal_credit_added':0,'prior_admissions_current_increment':0,'190first193_later_carry_increment':0,'186first187_later_carry_increment':0,'actual_new_original_semantic_source_studies':1,'complete_original_spatial_studies':1,'new_qualifying_related_reference_proposals':0,'current_PNG':7,'PNG_actual_viewed':7,'COD4_accepted_baseline':153,'COD4_gap':847,'COD4_increment':0,'NPC05_increment':0,'NPC01_cumulative_not_inferred':True,'java_run':False,'game_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'195检查193机器候选中Trek jungle_village_10等较大完整工居原源，先与已存完整案例比较；不将同族外作业/内卧室和装饰屋顶凑数。157W01待审、182HOLD、190首次193+1以后0保留。'}
put('session.json',ss);checks=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
g={tuple(b['pos']):b['state']for b in r['blocks']};out={}
for l in rd(P/'original-index-rle.json')['layers']:
 for z,row in enumerate(l['rows_z0_16']):
  x=0
  for run in row.split():
   v,_,cnt=run.partition('x');cnt=int(cnt)if cnt else 1
   for _ in range(cnt):
    if v!='?':out[(x,l['y'],z)]=int(v)
    x+=1
  ck('RLE_width_y%s_z%s'%(l['y'],z),x==17)
ck('all6012_indices_exact',out==g);ck('counts',len(r['palette'])==164 and sum('nbt'in b for b in r['blocks'])==68 and len(r['entities'])==9 and len(g)==6012 and sum(r['palette'][v]['Name']=='minecraft:air'for v in g.values())==4745)
ck('sourcearchive',bind(Path(s['source_archive']))['sha256']==s['source_archive_sha256'])
with zipfile.ZipFile(s['source_archive'])as z:ck('original_NBT',hashlib.sha256(z.read(s['member'])).hexdigest()==s['nbt_sha256'])
for f in rd(P/'protected-inputs.json')['files']:ck('protected:'+f['path'],bind(Path(f['path']))==f)
ck('Main186_binding',bind(mp)==comparison['Main186_binding'])
ca=rd(P/'carried-forward-pending.json');ck('only157_activepending',[x['batch']for x in ca['carried_unresolved_whole_reference_proposals']]==[157])
for k in ['182F01_NPC01_resolved_initial_review_HOLD0_first184','174F01_NPC01_resolved_accept1_first177','186F04_NPC01_resolved_accept1_first187','190F01_NPC01_resolved_accept1_first193']:ck('carry_exact:'+k,ca[k]==rd(O/'carried-forward-pending.json')[k])
ck('190admission_exact',rd(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_190_F01']==rd(O/'latest-independent-admissions.json')['newly_notified_NPC01_admission_190_F01'])
ck('7PNG',len(list(P.glob('*.png')))==7);ck('no_increment_or_newpending',ss['formal_credit_added']==0 and not ca['current_batch_new_pending'])
v={'status':'PASS'if all(c['passed']for c in checks)else'FAIL','checks':checks,'check_count':len(checks),'machine_assertions_not_credit':True};put('verification.json',v);put('active-checkpoint.json',{**ss,'verification':v['status']})
(P/'HANDOFF.md').write_text('194Trek mushroom stonecutter完整原源研究：17×21×17/DV3465，6012存1267非air4745air、57省略。21层357行6069原索引RLE/164pal/68BE/9展示框、1完整housepool3metadata及7图全部实际读/看。北室外切石带+东单门床箱主室，对Main186完整7观察6限制wholecomparison复用后保守family0；高位书架/箱/砧和高蘑菇盖不证新可达工作楼层。保留无namespace smooth_quartz、外居民pool缺失、vanilla loot未追读/原生未验等限制。0新pending/0正式信用；190首次193+1本批0，157W01待审、182HOLD/旧接纳原样。仅194研究无Java/游戏/网络/共享Jar/主清单修改。\n')
if v['status']!='PASS':print([c for c in checks if not c['passed']]);raise SystemExit('NOT SEALED')
put('RECEIPT.json',{**ss,'files':[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(rd(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))
