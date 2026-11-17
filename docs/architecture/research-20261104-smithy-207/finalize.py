import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-206';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];g={tuple(b['pos']):b for b in n['blocks']}
check('sizeDV',n['size']==[7,15,8] and n['DataVersion']==3105)
check('source counts',len(pal)==31 and len(g)==840 and r['air']==739 and r['nonair']==101 and sum('nbt'in b for b in n['blocks'])==7 and n['entities']==[])
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:
 check('NBT member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 contexts=read(P/'source-context.json')
 for a in contexts['metadata']:
  b=z.read(a['member']);check('metadata '+a['member'],b.decode()==a['original_text'] and hashlib.sha256(b).hexdigest()==a['sha256'])
 literal=[]
 for name in z.namelist():
  if name.endswith('.json') and b'jungle_village_19' in z.read(name):literal.append(name)
 put('source-pool-literal-search.json',dict(fixed_archive=bind(r['source_archive']),literal='jungle_village_19',JSON_mentions=literal,other_runtime_packs_unchecked=True,semantic_credit=0))
check('no context JSON',len(contexts['candidates'][0]['contexts'])==0)
check('8 generated only1 viewed',len(list(P.glob('*.png')))==8)
put('manual-review.json',dict(batch=207,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},status='BOUNDED_INITIAL_WHOLE_RELEVANCE_HOLD_ZERO_NOT_A_COMPLETE_SPATIAL_STUDY',observations=[
'7×15×8 DV3105；840全部保存=101非air739显式air。31palette/7BE/entities[]实际读，1张whole四视角PNG实际看；另7PNG只是生成，未看，不作完整研究或额外参考。',
'当前所见是小型开放柱/薄板/活板/工作块构件组合，不能由名称和声明15高证明一座完整可用多层工坊。先保留用途/整栋完整性HOLD0，不用设备密度补足整栋参考。',
'palette含各向loom、cartography_table、stonecutter、grindstone、green powder/terracotta/melon/wetsponge原状态，没有furnace/blastfurnace/bed/ladder；不因工作块而命名铁匠铺或连续锻造链。',
'7BE为两个接头/四个未燃空营火/一个空桶；接头south/north互名且finalair，选池原minecraft:village/jungle/jungle_village_19当前Jar未找到。不替换namespace或把socket当居民。',
'3metadata全文实际读，context0；当前literal搜索仅固定Jar，不推运行世界缺失。无完整原15层索引阅读、无完整路径/屋盖/近族七维研究，不加已读范围。',
'不作为NPC01/NPC06新合格提议、不加入活跃whole待审；已有研究不会因这里不合格而抹除。未1000不制作。'],actual_reading=dict(palette=31,BE=7,entities=0,PNG_actual_viewed=1,PNG_generated=8,full_metadata=3,full_context_JSON=0,whole_RLE_read=False,complete_whole_spatial_study=False),new_reference_proposal=0,formal_credit_added=0))
ack=read(P/'203-preack-author-ack.json');mp=ack['Main_review_binding'];main=read(mp['path']);check('Main binding',bind(mp['path'])==mp);check('Main full unchanged',ack['full_Main_judgment_preserved_exact']==main)
check('203 original seven plus13 exact',ack['original_author_judgment_preserved_exact']==read(P.parent/'research-20261104-smithy-203/manual-review.json')['cases'][1])
check('9 findings plus8limits exact',len(ack['Main_finding_responses'])==9 and len(ack['Main_limit_responses'])==8 and [a['finding'] for a in ack['Main_finding_responses']]==main['Main_findings'] and [a['limit'] for a in ack['Main_limit_responses']]==main['Main_limits'])
check('3 added whole judgments preserved',len(main['complete_prior_saved_comparisons']['additional_close_whole_judgments'])==3)
check('203 awaiting final zero',ack['formal_credit_added']==0 and ack['case203_still_pending_until_Main_final'])
check('157 first206 only current0',read(P/'latest-independent-admissions.json')['157W01_first206_current207_increment']==0)
check('active203 unchanged',[(x['batch'],x['id']) for x in read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals']]==[(203,'F02')])
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current206'];now=bind(old['path']);protected.append(dict(last206_checkpoint=old,current207=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved206 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True,local_script_issue='First ack script parse failed on numeric-start keyword before any script writes. Renamed to case203_still_pending_until_Main_final; successful rerun. Not source defect or semantic credit.'))
s=dict(batch=207,status='203_ACTUAL_AUTHOR_ACK_AND_BOUNDED_NEW_SOURCE_HOLD',formal_credit_added=0,accepted157_first206_current_increment=0,case203_current_increment=0,active_pending=['203F02'],new_qualifying_reference_proposals=0,new_complete_whole_studies=0,bounded_original_sources=1,PNG_generated=8,PNG_actual_viewed=1,palette=31,BE=7,full_metadata=3,full_context_JSON=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Continue fresh whole sources, avoid components/rotations; Main203 final pending. No new credit before final acceptance. Old157 first206 later0.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
