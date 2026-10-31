"""Reassess existing pending owner with concrete registration, producer and inherited custody chain; no new root duplicate."""
import json,hashlib
from pathlib import Path
from review_batch import accepted,record,O
cs=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()));root='4e7a5bb03828425ab966';f=O/'reviews/batch-148.json';rows=json.loads(f.read_text());old=next(r for r in rows if r['candidate_id']==root)
s=[c['candidate_id'] for c in cs if c['repo']=='GregTechCEu/GregTech-Modern' and c['path'].endswith(('/GTChestBoat.java','/GTBoatItem.java')) and c['method'] in {'addAdditionalSaveData','readAdditionalSaveData','GTChestBoat','use'}]
s += [c['candidate_id'] for c in cs if c['repo'].startswith('Minecraft+') and c['path'].endswith(('/ChestBoat.java','/ContainerEntity.java')) and c['method'] in {'addAdditionalSaveData','readAdditionalSaveData','addChestVehicleSaveData','readChestVehicleSaveData','getItem','setItem','createMenu','interact'}]
a=accepted(root,'gtceu-custom-chest-boat-subclass-cargo-save-bridge-loss-negative','固定GTCEu6ac6cdcf源完整GTChestBoat/GTBoatItem及实体/物品注册片段，重读native1.20.1完整ChestBoat/ContainerEntity','GT CHEST_BOAT注册工厂GTChestBoat::new；rubber/treated Item use生成并消耗实物；继承27格货物与lootTable实际菜单/读写','GT addAdditionalSaveData仅写Type；read仅设置type且不super。原生父类恰在这两个callback调用add/readChestVehicleSaveData，后者写Items或LootTable/LootTableSeed；GT覆盖跳过此桥接','从原pending补明实际业务注册与物品生成consumer，确认不是未接入的示例类；静态完整物品库存丢失机制研究1，不称该实现能恢复成功。两材质共用类只1，native保存支持早已研究不重复计，真正区别是mod派生override截断链而非普通原版箱船重新计。借鉴限定新增handler必须保留已有Clone/持久所有者职责，不能覆盖其容器。','仅上游固定源码静态证据，未编译/游戏/原生实体实际load，不能断言所有发布版或当前Dynasty有该缺陷。GT pinned源1.20接口与已供native1.20.1匹配不替代具体pack loader版本运行证明；Item use addFreshEntity未查后consume，另外不作独立credit。native drop/menu/loot内联已读，ContainerHelper与Forge注册底层不另作全文/运行声明。',s)
a['reassessment']={'prior_status':'pending','prior_batch':148,'reason':'补齐实际注册/物品生产/继承菜单库存→磁盘桥接；本轮研究范围允许具体负例，无需以未运行上游为研究前置，但保留未运行限制。','support_batch':222}
rows[rows.index(old)]=a;f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
extra=[c['private_file'] for c in cs if c['candidate_id'] in set(s)]
base='tools/cod4/legacy-migration-acceptance/.work/sources/GregTechCEu__GregTech-Modern/src/main/java/com/gregtechceu/gtceu/common/data/'
record(222,[],extra+[base+'GTEntityTypes.java',base+'GTItems.java'])
(O/'semantic-reassessment-20261029-002.json').write_text(json.dumps({'candidate_id':root,'prior_status':'pending','new_status':'accepted','credit_change':1,'family':a['family'],'scope':'Full fixed-source negative mechanism, not runtime reproduction or new production implementation. Rerun record222 after earlier record148 if regenerated.','gui_started':False,'production_modified':False},ensure_ascii=False,indent=2)+'\n')
