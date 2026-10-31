import json
from review_batch import accepted,record,O
cs=[c for c in map(json.loads,(O/'candidates.jsonl').read_text().splitlines()) if c['repo']=='ldtteam/minecolonies']
def get(f,m):return next(c['candidate_id'] for c in cs if c['path'].endswith('/'+f+'.java') and c['method']==m)
def support(fs,r):return [c['candidate_id'] for c in cs if any(c['path'].endswith('/'+f+'.java') for f in fs) and c['candidate_id']!=r]
rows=[]
def add(f,m,fam,t,i,o,p,l,fs):
 r=get(f,m);rows.append(accepted(r,fam,t,i,o,p,l+' 固定官方Minecolonies61292848b81ee4a7a33443beb52aabdc446355b8静态源码研究；无游戏/原档操作、不宣称运行验收，框架/网络支持0。',support(fs,r)))
add('TravellingManager','deserializeNBT','minecolonies-paid-nether-expedition-cargo-timer-and-deferred-entity-reconstruction','完整TravellingManager含TravelerData、JobNetherWorker、EntityAIWorkNether全文，Colony读写/tickTravellers、CitizenData.updateEntityIfNecessary。','traveler列表citizenId/target/initial/remainingTime；job craftedResults/processedResults完整栈队列、citizenInNether Bool。','manager清map重建事实；实际旅行中禁止生成NPC，计时归零保留target供消费，消费finishTravellingFor移记录后重建隐藏实体再跑远征；已付材料生成待处理结果队列随后逐步变产物。','整条虚拟远征1，不将timer、两个队列、NPC引用重建或log各算1。区别Grave259死者货物复活：此是活NPC旅程中移除实体、持久工作队列和预计返回地；不是仅NBT同构。真实动态引用重新从CitizenManager取得，借鉴Clone应转事实不搬旧entity引用。','job reader不clear两队列，同对象复读重复；计时递减没markDirty，剩余负值不会==0故永久travel，initial0进度除0。finishTravel在实际spawn成功前删receipt，若失败可能失目的地；实际产物入背包失败后仍clear全部processed队列。缺jobflag不清旧值。父AbstractJob reader未本批全读，未运行材料扣取或spawn；不移植其惩罚/回血。',['TravellingManager','JobNetherWorker','EntityAIWorkNether'])
add('CitizenData','isRelatedTo','minecolonies-citizen-kinship-durable-identities-inheritance-and-deceased-edge-pruning','完整ReproductionManager创建新孩子，CitizenData完整serialize/deserialize与全部关系方法、CitizenManager.updateCitizenMourn既有完整；真实防近亲/伴侣查找和死亡边修剪。','parents两个姓名STRING、children/siblings INT列表、partner INT，CitizenData构造分配identity；出生设置父母/兄弟/配偶双向关系。','writer保存当前存活关系；reader把列表加到集合、partner缺0；实际繁殖通过isRelatedTo筛候选并按父母技能/名字初始化孩子，死亡调用onDeath清ID边但保父母姓名谱系。','独立亲属关系owner1，不是CitizenSkill能力/Quest完成/Mourn失亲等待同一字段拆计；Mourn仅本关系消费结果，其队列有另生命周期。姓名与ID混存必须按源语义迁移；不把NPC关系系统或繁殖机制移植到本项目。','children/siblings read未clear，重复加载旧数据会残留，关系setter不直接dirty；网络serialize某方法会修剪无效关系但本批没完整审该网络writer不据此声称磁盘定期清洗。姓名改动/同名可影响亲属判定；partner比较ID而isRelatedTo非完全对称，父母字段不因死亡消失是实际策略，不是一律copy所有字段。Reproduction无单独持久reader，其timer不计信用。',['ReproductionManager'])
for row in rows:
 for f,ms in {'Colony':['read','write','tickTravellers'],'CitizenData':['serializeNBT','deserializeNBT','updateEntityIfNecessary','getPartner','getChildren','getSiblings','getParents','addSiblings','addChildren','setPartner','onDeath','setParents','isRelatedTo'],'CitizenManager':['updateCitizenMourn']}.items():
  for m in ms:
   q=get(f,m)
   if q!=row['candidate_id'] and q not in row['supporting_candidates']:row['supporting_candidates'].append(q)
record(270,rows)
