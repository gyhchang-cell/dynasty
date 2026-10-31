from pathlib import Path
import json,hashlib,datetime,re
B=Path(__file__).resolve().parent;root=B
while root.name!='dynasty':root=root.parent
read=lambda p:(root/p).read_text()
def sha(p):return hashlib.sha256((root/p).read_bytes()).hexdigest()
chapter='modpack/config/ftbquests/quests/chapters/dynasty_c1.snbt';lines=read(chapter).splitlines()
entries=[('mandarin_duck_axe','1000000000c40008',1528,1544),('repeating_crossbow','1000000000c40003',1545,1561),('flying_claw','1000000000c40006',1562,1578),('rope_dart','1000000000c40005',1579,1595),('siege_crossbow','1000000000c40004',1613,1629),('meteor_hammer','1000000000c40007',1630,1646)]
rows=[]
for name,qid,a,b in entries:
 recipe='src/main/resources/data/dynasty/recipes/cod4/'+name+'.json';ad='src/main/resources/data/dynasty/advancements/cod4_obtain_'+name+'.json';r=json.loads(read(recipe));adv=json.loads(read(ad));text='\n'.join(lines[a-1:b]);assert 'id: "'+qid+'"'in text and r['result']['item']=='dynasty:'+name and adv['criteria']['code']['trigger']=='minecraft:impossible';deps=re.search(r'dependencies: \[(.*?)\]',text)[1]
 rows.append(dict(item='dynasty:'+name,recipe=recipe,recipe_sha256=sha(recipe),ingredients=r['ingredients'],produced=r['result'],advancement='dynasty:cod4_obtain_'+name,advancement_definition=ad,advancement_sha256=sha(ad),trigger='minecraft:impossible criterion code, programmatically awarded',quest_id=qid,task_id='2000000000c400'+qid[-2:],chapter=chapter,reviewed_lines=[a,b],chapter_excerpt=text,dependencies=re.findall(r'"([0-9a-f]+)"',deps),status='STATIC_MAPPING_READ_NOT_RUNTIME_ACCEPTANCE'))
reports=['src/main/java/com/dynasty/expansion/ExpansionContent.java','src/main/java/com/dynasty/expansion/ContentProgress.java','src/main/java/com/dynasty/DynastyAdvancements.java']
historic_path='docs/art/bestiary-v43/cod4-budget-readonly-20261030/report.json';h=json.loads(read(historic_path))
v=dict(saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='READ_ONLY_ID_NODE_RECEIPT_NO_QUEST_MUTATIONS',chapter_sha256=sha(chapter),rows=rows,code_evidence=[dict(path=reports[0],sha256=sha(reports[0]),reviewed_lines=[[14,24]],finding='六件武器各自真实注册；不在所读SUPPLIES列表。'),dict(path=reports[1],sha256=sha(reports[1]),reviewed_lines=[[1,83]],finding='reconcile扫描背包/手/护甲/饰品；排除SUPPLIES后授cod4_obtain；每100tick END及登录。41–45仅解锁配方书，不能当合成限制/真实合成回执。'),dict(path=reports[2],sha256=sha(reports[2]),reviewed_lines=[[14,33]],finding='查询存在advancement后award code；missing返回。')],historic_asset_snapshot=dict(path=historic_path,sha256=sha(historic_path),timestamp=h['timestamp'],newly_revalidated=False,status=h['status'],runtime_modified=h['runtime_assets_or_source_modified'],asset_item_quest_links=h['asset_item_quest_links'],note='仅登记历史只读结果：swindler32cuboids/192quads，herb_picker30/180，仍超当时lightSteve156quads基准；abacus是内嵌几何，不虚构ItemStack ID。并非本批重新烘焙/生产hash核查。'),limitations=['不修改FTB任务/任务判定/主协调账/外部提示词','没有自然合成、持握截图或游戏FTB完成回执','quest节点存在不等于模型实机验收；code criterion存在不等于事件已经触发','六武器任务对应只读登记，不计新模型、新参考或独立验收'],accepted_credit=0,production_mutations=False)
(B/'task-item-node-links.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print('saved',len(rows),'static links')
