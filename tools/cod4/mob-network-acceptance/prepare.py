from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[3]; T=R/'tools/cod4/mob-network-acceptance'; O=R/'docs/cod4/audit-20261022/mob-network-acceptance'
s=(R/'src/main/java/com/dynasty/expansion/SecondaryMobs.java').read_text(); request=(R/'docs/cod4/request.txt').read_text().split('## 1.1 30 只表')[1].split('## 1.2')[0]
ids=re.findall(r'new Spec\("([^"]+)"[^\n]+',s)[:30]; req=re.findall(r'\| (\d+) \| ([^|]+) \| ([a-z_]+) \|',request)
assert len(ids)==len(req)==30 and set(ids)=={r[2] for r in req}
neutral={'famished_refugee','night_watchman','swindler','herb_picker','snail_maiden','jingwei_bird'}
special={'famished_refugee':'食物首次扣一并友好；第二客户再次喂食不重复扣款','herb_picker':'铜钱换2茶叶；全体共享200tick冷却，双客户隔离核对','swindler':'受伤开场→付铜钱→带实体UUID假药；非客户不能识破，原客户潜行持原假药识破；死亡还币一次','snail_maiden':'中立采集/受击40tick缩壳；铜钱交易原需求不适用，真实交互无结果仅记录探测','red_fox':'自然攻击偷走一份可食物；死亡返还一次（当前实现为存储，非消费吃完）','paper_money_ghost':'自然攻击偷铜钱一枚；死亡返还一次','clockwork_rat':'原生客户端Q丢掉物→自然拾取偷一件；死亡返还一次','wooden_magpie':'钢索维修20生命，满血不扣款'}
rows=[]
for num,name,id in req:
 rows.append({'number':int(num),'name':name.strip(),'id':id,'neutral':id in neutral,'baseline':'不主动选敌' if id in neutral else '自然选中较近host，host旁观后转选peer','attacked':'受击逃跑且不反击' if id in {'famished_refugee','herb_picker','snail_maiden','swindler'} else '中立受击逃跑并允许反击' if id in neutral else '原生受击/仇恨；低血逃跑通用逻辑','special':special.get(id,'不适用特殊物品交互'),'death':'双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒'})
(O/'applicability.json').write_text(json.dumps({'denominator':30,'neutral':6,'hostile':24,'sources':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'docs/cod4/request.txt',R/'src/main/java/com/dynasty/expansion/SecondaryMob.java',R/'src/main/java/com/dynasty/expansion/SecondaryMobs.java']},'matrix':rows},ensure_ascii=False,indent=2))
(O/'applicability.md').write_text('# COD4-1 实际双客户端适用矩阵\n\n分母30：6中立、24敌对。虾兵为召唤额外实体，不计入30。夹具提供初始实体、装备/原料、平台与位置，不修改产品行为。\n\n|序号|生物|registryId|自然仇恨|受击|特殊输入|死亡/拾取|\n|---|---|---|---|---|---|---|\n'+'\n'.join('|'+ '|'.join(str(r[k]) for k in ['number','name','id','baseline','attacked','special','death'])+'|' for r in rows))
