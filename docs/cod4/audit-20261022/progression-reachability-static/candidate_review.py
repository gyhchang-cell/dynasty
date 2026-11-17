"""Targeted proposal only. Read five findings, five existing research records and named source files.
Only writes candidate-* and minimal-candidates.md beside this script; never edits production.
"""
from pathlib import Path
import json,hashlib,re,sys,datetime
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
sys.path.insert(0,str(R/'tools/art'))
from quest_snbt import list_compounds,object_id
inputs={}
def rd(p):
 p=Path(p);b=p.read_bytes();inputs[str(p.relative_to(R)) if p.is_relative_to(R) else str(p)]=hashlib.sha256(b).hexdigest();return b.decode()
def js(p):return json.loads(rd(p))
def put(n,d):assert n.startswith('candidate-');(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def quest(chapter,qid):
 p=R/'modpack/config/ftbquests/quests/chapters'/f'{chapter}.snbt';raw=rd(p)
 block=next(x for x in list_compounds(raw,'quests') if object_id(x).lower()==qid)
 desc=re.search(r'\bdescription:\s*(\[[^\n]*\])',block)
 return {'path':str(p.relative_to(R)),'id':qid,'line':raw.count('\n',0,raw.index(block))+1,'block_sha256':hashlib.sha256(block.encode()).hexdigest(),'description':json.loads(desc[1]) if desc else None,'block':block}
reference=js(R/'docs/cod4/audit-20261022/quest-reference-1000.json');old=js(O/'findings.json');spec=rd(R/'docs/cod4/request.txt');before=rd(R/'docs/cod4/audit-20261022/cod4-before.txt')
applications={241:('Optional water bucket beside a ritual checkmark demonstrates that equipment guidance can be separated from required progress.','Not an opening wood/iron ordering example, not permission to make Dynasty water bucket optional, not timing evidence.'),304:('Existing smithing-table objective explicitly consume_items:false with a predecessor; retain equipment and distinguish detection from payment.','No silk price/stock/recipe-balance data; does not prove Dynasty implicit defaults or justify changing them.'),15:('Actual structure task and equipment task are separate in one quest; track encounter condition separately from ownership.','No proof of Dynasty encounter time, damaged-iron-sword value or NBT transfer contract.'),8:('A dimension detection task has a real prerequisite; dimension entrance and later loot ownership are separate milestones.','No evidence for72jade cost fairness or actual travel/spawn duration.'),124:('Tetra workbench upgrade is tracked via native advancement with a prerequisite and rewards.','Supports separate predecessor/progress/reward review; not proof of Dynasty recipe correctness, universal NBT retention or item balance.')}
refs=[]
for index,(applies,limits) in applications.items():
 row=reference['sites'][index];p=Path(row['file']);exists=p.is_file();current=hashlib.sha256(p.read_bytes()).hexdigest() if exists else None
 refs.append({'reference_index_zero_based':index,'record':row,'source_exists':exists,'source_current_sha256':current,'source_hash_matches_record':current==row['file_sha256'],'applies_to':applies,'does_not_support':limits})
put('candidate-reference-crosswalk.json',{'existing_research_count':reference['summary']['count'],'selected_records':len(refs),'new_research_count_claim':0,'method':'Targeted reuse of5 members of existing1000, not new1000 recipe/economy studies or playthroughs. File hashes checked; task/reward strings carried from recorded research.','records':refs})
mu=quest('dynasty_story_01','1000000000000000');recipe=js(R/'src/main/resources/data/dynasty/recipes/mu_mao.json')
old_string='两根木棍加一块橡木木板&6合成&r；当前配方指定橡木，不是任意木板。夜里先避开王朝精英怪。'
new_string='两根木棍加一块任意木板&6合成&r。夜里先避开王朝精英怪。'
assert old_string in mu['description']
assert recipe['ingredients']==[{'item':'minecraft:stick'},{'item':'minecraft:stick'},{'tag':'minecraft:planks'}]
new_desc=[new_string if v==old_string else v for v in mu['description']]
# Results from the targeted exact-phrase rg search of modpack/src/docs/tools; no second whole-content scan.
copy_paths=['docs/playtest-20261018/before-last-deployed-book.json','docs/quests-remaster/gallery.html','docs/quests-remaster/book.json','docs/quests-journey-v3/last-deployed-book.json','docs/quests-presentation-v2/before-book.json','docs/ui-fixes-20261020/baseline/modpack/config/ftbquests/quests/chapters/dynasty_story_01.snbt','docs/ui-fixes-20261020/baseline/docs/quests-remaster/book.json','docs/quests-journey-v3/before-book.json','docs/ui-fixes-20261020/install-backup/f84717a52890f30b3baeeb8e534371866e274b1435a3b4c108a0fd62d229e6ec/dynasty_story_01.snbt','docs/ui-fixes-20261020/install-backup/e71d342726acec109e93c6beba1b2c4ee236da27929cb7e7e68db61880e294f0/last-deployed-book.json','docs/bugfix-20261017/last-deployed-book-before.json','modpack/config/ftbquests/quests/chapters/dynasty_story_01.snbt','docs/blueprint-cod2/evidence/entry-20261018/before/docs/quests-remaster/book.json','docs/blueprint-cod2/evidence/wangsi-20261018/before/docs/quests-remaster/book.json','docs/blueprint-cod2/evidence/garrisons-20261018/before/book.json','docs/quests-integration-v1/before-book.json','tools/art/quest_story.py','docs/bugfix-20261018/book-before.json']
copies=[]
for rel in copy_paths:
 text=rd(R/rel);matches=[]
 for no,line in enumerate(text.splitlines(),1):
  if '当前配方指定橡木，不是任意木板' in line:
   pos=line.index('当前配方指定橡木，不是任意木板');matches.append({'line':no,'excerpt':line[max(0,pos-55):pos+60]})
 assert matches,rel
 if rel.startswith('modpack/'):kind='ACTIVE_TASK_SOURCE';action='candidate exact string substitution only, coordinated with current layout owner'
 elif rel.startswith('tools/'):kind='GENERATOR_LITERAL';action='candidate same semantic string fix to prevent regeneration; no script run or other generator change'
 elif rel in ['docs/quests-remaster/book.json','docs/quests-remaster/gallery.html']:kind='DERIVED_BOOK_PREVIEW';action='after approval, owner selectively synchronize current preview; no baseline rewrite or full regeneration authorized'
 else:kind='HISTORICAL_OR_DEPLOYMENT_RECEIPT';action='preserve historical bytes; if relevant deployment status is still current, document supersession separately, do not rewrite recorded evidence'
 copies.append({'path':rel,'kind':kind,'sha256':inputs[rel],'matches':matches,'future_handling':action})
put('candidate-mu-mao-text.json',{'id':'T01','status':'CONFIRMED_TEXT_RECIPE_CONTRADICTION_PROPOSAL_ONLY','quest':mu,'field':'description[1] (zero based)','old_string':old_string,'new_string':new_string,'full_old_description':mu['description'],'full_new_description':new_desc,'recipe_path':'src/main/resources/data/dynasty/recipes/mu_mao.json','recipe_definition':recipe,'recipe_evidence':'2sticks +1 #minecraft:planks, output1; no oak-only item. Candidate does not replace the existing tag.','native_change':False,'fields_preserved':['quest ID','all task IDs/types/counts/consume flags','all reward IDs/values/claim state','dependencies','coordinates/order/title','recipe inputs/output/count/tag','equipment stats/NBT behavior'],'economy_delta':0,'copy_inventory':copies,'scope_limits':'18 exact-phrase-hit files in modpack/src/docs/tools; not installed user packs or ignored/runtime caches. Current audit prose/snapshots excluded from copy claims.','research_reference_indices':[304,124],'research_applicability':'Only structural practice: separate objective/reward/prerequisite and preserve native detection. Direct correctness comes from actual mu_mao recipe and conflicting local strings. Existing1000 contains no claimed1000 planks-tag text-fix cases; no balance authority inferred.'})
# Candidate append text, no new prerequisites or fictional tasks/recipes. Targets come from existing named nodes.
plans=[
 ('N01','F01','ORDER_RISK_NOT_PROVEN_SPEC_FAILURE','dynasty_story_01','1000000000010000','开局防身可提前用两根木棍和一块任意木板合成木矛；下方木矛任务的领取顺序不限制配方制作。已有木矛可继续做石戈。',[241,304],'Earliest existing root guidance only. Leave wood/iron/water dependencies and10coin/6xp/12merit rewards unchanged. Does not fix or certify2–3h cadence.'),
 ('N02','F02','COST_FACT_NOT_BALANCE_DEFECT','dynasty_c3','1000000000000079','竹甲胸甲需要原布衣胸甲、竹子×2、丝绸×1；从线全量合成两件前驱合计需线×81。百宝金每个初始丝绸报价最多8次，只够布衣胸甲所需8匹；继续升级需另外取得1匹。原布衣是升级材料，先不要丢弃。',[304],'Explain predecessor and optional source limits; keep3string→rawsilk,3rawsilk→silk, merchant price/stock and armor costs unchanged. No automatic handout/restock promise.'),
 ('N03a','F03','LATE_CREDIT_NOT_PROVEN_LATE_ACQUISITION','dynasty_c9','1000000000c40026','探索途中可先使用旧兵器架，现有交互不要求先解锁本任务。配置等待600刻后再次交互可取得剩余约四分之一耐久的铁剑；领取本任务奖励仍按原前置。旧铁剑还有后续材料用途。',[15,304],'Do not make structure find mandatory, move original rewards, reset site_done or assume natural encounter time.'),
 ('N03b','F03','LATE_CREDIT_NOT_PROVEN_LATE_ACQUISITION','dynasty_c9','1000000000c40024','废弃军械的交互不要求先解锁本任务；按现有流程等待3600刻并再次交互可取得机括×1。机括也有原配方，不必先找到此处才能制作。领取任务奖励仍按原前置。',[15,304],'Keep site yield/timer, existing recipes and task rewards unchanged; no dependency cut justified by static evidence.'),
 ('N04','F04','ENTRY_COST_NOT_UNOBTAINABILITY','dynasty_story_04','100000000000018a','天朝玉门原配方为玉块×8加龙晶×1，产出玉门×2；本任务只要求取得1个。进入天朝后，凤凰与麒麟的掉落仍需找到对应群系并实际击败生物，不能只靠进入维度算取得材料。',[8],'Do not add item/kill/dimension requirements or resource payments to this existing objective; preserve2portal output and1portal target.'),
 ('N05a','F05','PREDECESSOR_NAVIGATION_NOT_BALANCE_DEFECT','dynasty_c3','1000000000000045','官银剑实际配方为玉笛×1、银锭×3、图纸×1；需要保留玉笛作材料。官银剑随后还可制作玉剑，不必把被替换的前驱直接丢弃。',[124,304],'Keep yu_di predecessor; do not substitute bronze sword or add NBT transfer contracts.'),
 ('N05b','F05','PARALLEL_BRANCH_COST_NOT_BALANCE_DEFECT','dynasty_c3','10000000000000b0','鸿蒙帝铠胸甲需要龙皇胸甲×1、混元胸甲×1、帝骨×1、帝印×1；两条旧甲分支都要保留，不能只备其中一件。原配方会实际消耗这两件前驱。',[124,304],'Keep both parallel branches and all boss resources, no discount/reward compensation or inheritance behavior.')]
rows=[]
for cid,fid,status,ch,qid,line,rr,policy in plans:
 node=quest(ch,qid)
 rows.append({'id':cid,'finding':fid,'status':status,'target':node,'operation':'APPEND_DESCRIPTION_ONLY_DRAFT','proposed_append_string':line,'reference_indices':rr,'preservation_and_limits':policy,'production_applied':False,'needs_text_owner_review':True})
put('candidate-navigation.json',{'candidates':rows,'dependency_edits':[],'recipe_edits':[],'balance_changes':[],'not_recommended_without_new_evidence':['reduce silk/string costs or increase silk stock because72/216looks high','make blueprint/currency/boss materials free','remove iron/water or story gates to force a claimed2–3h result','make interaction completion an equipment crafting prerequisite','replace yu_di or remove either hongmeng armor branch','assume quest discovery implies actual acquisition or reward eligibility'],'shared_progress_preservation':'IDs unchanged is necessary, not sufficient: proposals also preserve objective definitions, dependencies, rewards, auto/repeat/consume settings and site flags. No progress clear/migration or replay. Any future reorder needs separate new/partial/completed/unclaimed/claimed state verification.'})
put('candidate-input-sha256.json',inputs)
validation={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scans':'No new whole quest/recipe/registry enumeration. Named quest blocks only; one exact-phrase duplicate search (initial line output repeated as filenames for bounded review).','findings_reused':len(old),'existing_research_membership':all(reference['sites'][r['reference_index_zero_based']]['semantic_sha256']==r['record']['semantic_sha256'] for r in refs),'research_source_hashes_match':all(r['source_hash_matches_record'] for r in refs),'direct_recipe_ingredients_exact':True,'mu_mao_old_string_match_count':mu['description'].count(old_string),'mu_mao_changed_description_entries':sum(a!=b for a,b in zip(mu['description'],new_desc)),'copy_files':len(copies),'copy_categories':{k:sum(x['kind']==k for x in copies) for k in sorted({x['kind'] for x in copies})},'navigation_candidate_count':len(rows),'formal_changes':[],'clients_started':0,'current_source_input_drift':[p for p,h in inputs.items() if hashlib.sha256((R/p if not Path(p).is_absolute() else Path(p)).read_bytes()).hexdigest()!=h]}
put('candidate-verification.json',validation);print(json.dumps(validation,ensure_ascii=False,indent=2))
