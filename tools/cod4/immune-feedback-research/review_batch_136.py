"""Independent multi-anchor transfer and cleanup policy, shared resolution is not new credit."""
from ledger import B,O,record,verify
import json
r='AlexModGuy/Ice_and_Fire';root=B/'sources'/r.replace('/','__');p='src/main/java/com/github/alexthe666/iceandfire/'
ns=['item/ItemChain.java','entity/props/ChainProperties.java','entity/EntityChainTie.java','client/render/entity/RenderChain.java']
refs=[(p+x,1,len((root/p/x).read_text().splitlines())) for x in ns]+[(p+'item/IafItemRegistry.java',284,285),(p+'entity/IafEntityRegistry.java',71,71),(p+'IceAndFire.java',89,133),(p+'IceAndFire.java',184,213),(p+'CommonProxy.java',125,127),(p+'client/ClientProxy.java',53,57),(p+'event/ServerEvents.java',442,473),(p+'event/ServerEvents.java',624,639),(p+'event/ClientEvents.java',209,222)]
k='icefire-native-multi-anchor-chain-transfer-and-knot-scoped-release'
record(k,r,refs,
 '注册普通/黏性chain及ChainTie→物品interactLivingEntity实际attach；黏性蹲下清目标链并解除附近指向目标的其他链，非蹲下转接玩家现带目标到点击实体；Wall useOn服务端attachToFence将当前玩家链转挂真实新建或已有ChainTie。ChainProperties以owner UUID列表防重复、存运行ID；LivingUpdate对每个解析owner在距离>7加非线性拉力，各owner贡献相加。ChainTie交互转接或无待转时移除；remove遍历30格解开关联并掉chain；客户端PostRenderLiving循环每个owner画插值锁链。',
 '实际多锚点迁移/叠加控制与锚点删除范围释放政策1，和已计AlexsMobs单owner藤索不同在于列表关系、转挂/蹲解闭包、多个owner力相加以及knot原生删除清理；共用UUID/server ID/client fallback解析及guardians式锁链顶点不计新信用。attach检查解析结果，失效旧列表可保留；客户端ID命中不核UUID，server只当前ServerLevel UUID查询，缺owner跳过不主动移除。knot.remove仅30格，黏性清理60格，不能声称所有关联均释放；item普通绑定无Boss或抗性门，直接deltaMovement而不hurt。knot拒非玩家伤源只来源保护，作为支持0，不另计Boss拒伤。新tie addFreshEntity返回未检验，placement链声不等于成功生成/控制接纳。',
 '拒控机制须覆盖实际多锚点直接加速度入口，不能只拦hurt或药水；反馈去重按真实目标与事件，不能把每个owner每tick都转灰字。清理需考虑所有关联和失效来源，不以渲染解析失败当服务器释放。普通阴阳无灰字要求。',
 '完整原生item/tie/props/render和实际注册、tick/渲染调用已读；Citadel收包未闭合支持0，原版HangingEntity移除派发与事件双端时序未运行。只是控制来源/归属/可见锚定参考，不宣称Boss控免、TCP同步或锁链实际观感通过，不制作资产。','native_multi_source_control_ownership_and_release_lifecycle')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch136-multi-anchor-transfer-and-knot-removal','credited_chains':[k],'rationale':'Only multi-owner relation transfer, accumulated control and native knot-scoped cleanup is independent of prior single-owner lasso. Same serverUUID/clientID resolver and guardian-derived vertex renderer support0, source damage filter0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
