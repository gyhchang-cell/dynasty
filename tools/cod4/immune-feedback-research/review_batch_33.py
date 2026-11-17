"""Cyclic native refusal/receipt boundaries; helper projects remain separate."""
from ledger import B,O,record,verify
import json
r='Lothrazar/Cyclic';p='src/main/java/com/lothrazar/cyclic/';keys=[]
def whole(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
shared=[whole(p+'ModCyclic.java'),whole(p+'registry/EventRegistry.java')]
def add(k,refs,chain,obs,lesson):
 if k in {x['id'] for x in json.loads((O/'reviewed.json').read_text())}:
  keys.append(k);return
 record(k,r,shared+refs,chain,obs,lesson,'固定b2213600474fa088702dec68a783549e44dfa6ae；实际完整方法及原生事件调用全文观察，非运行/TCP/像素/声音验收。通用外部library调用只记调用事实，不假定其内部效果/耐久扣除成功；不改正式代码、资产、待办，不给普通阴阳加灰字。','native_control_denial_and_attack_receipt_validation');keys.append(k)
add('cyclic-native-antibeacon-cached-region-effect-refusal', [whole(p+'block/antipotion/BlockAntiBeacon.java'),whole(p+'block/antipotion/TileAntiBeacon.java'),whole(p+'capabilities/livingentity/LivingEntityCapabilityStorage.java'),whole(p+'registry/AttachmentRegistry.java'),(p+'potion/PotionEventHandler.java',18,59),(p+'registry/BlockRegistry.java',345,345),(p+'registry/TileRegistry.java',186,186),(p+'block/TileBlockEntityCyclic.java',284,286),(p+'config/ConfigRegistry.java',501,509)],
 '实际注册BEACON_SPONGE方块/BE与Living附件；原生ticker非红石供电时周期清理并标记最近方块；已注册Applicable监听直接调BlockAntiBeacon.isPotionApplicable，服务端再检实体所在chunk、缓存位置曼哈顿距离、方块身份和红石，DO_NOT_APPLY。',
 '真实区域拒绝与周期清理同家族计1，非所有HARMFUL效果/配置键逐条加数。标记用轴向box而最终用曼哈顿距离，边角范围不等价；缓存只有BlockPos，附件无序列化/死亡拷贝、无维度和过期戳，事件再验证可过滤多数过期值。旧最近方块只检类型，不查供电；近处被供电的旧点可挡住稍远有效点更新。周期timer设TICKS后逐tick减，到0才执行，约TICKS+1；新放置onPlace直接清理无供电判断。removeEffect返回未查，不能把debug cured当成功；运行beam不是逐目标拒绝回执，无文字/节流派发。',
 'Boss免控必须在最终服务端原因明确处生产回执，区域配置拒绝不应冒充Boss；缓存锚点的世界/生命周期需要单独约束。')
charm=[whole(p+'util/CharmUtil.java'),whole(p+'item/bauble/ItemBaseToggle.java'),(p+'registry/ItemRegistry.java',222,244)]
add('cyclic-native-knockback-charm-final-event-cancellation',charm+[(p+'event/ItemEventHandler.java',136,152)],
 'Mod构造注册setup→原生LivingKnockBackEvent→Player且实际CharmUtil找到启用抗击退charm→event.cancel并调用damageItem。已读toggle存CUSTOM_DATA与Curios/库存/双手首个启用物查找。',
 '确实最终拒绝击退，非仅属性接近1；不推导伤害也免疫。物品默认ON，服务端use切换、库存即生效非必须穿戴；canUse耐久阈值未在此handler调用，扣耐久由外部函数仅记录尝试。盾分支旧onKnockback注释掉0计数。此处无主动文字/声音，不扩展普通体质反馈。',
 '拒控应按控制类别和原生事件确认，不能从未移动画面或hurt布尔推断。')
add('cyclic-native-potion-refusal-versus-recursive-replacement',charm+[(p+'event/ItemEventHandler.java',87,87),(p+'event/ItemEventHandler.java',189,228)],
 '实际Applicable监听先启用antiPotion→DO_NOT_APPLY并耐久调用；否则stealth/boost装备决定拒绝原实例、设置递归guard、重新addEffect修改粒子可见性/时长，finally清guard。',
 '同最终监听与重入保护语义合并1，不将三个charm名字多计。antipotion拦所有效果含有益；相同DO_NOT_APPLY也可能是隐藏粒子/延时替换而非免疫。重入guard是监听实例全局bool而非目标/线程局部，同步嵌套其它玩家请求可绕过本监听。replacement addEffect返回未查，其它监听仍可拒绝，因此不能把原事件拒绝当新效果已接纳。',
 'Boss灰字仅明确Boss拒控分支触发；普通重写/替换/资源失败不显示免疫。')
add('cyclic-native-render-produced-laser-server-target-validation', [whole(p+'net/PacketEntityLaser.java'),whole(p+'item/LaserItem.java'),whole(p+'registry/PacketRegistry.java'),(p+'render/OutlineRenderer.java',73,241),(p+'registry/ItemRegistry.java',278,278),(p+'registry/CapabilityRegistry.java',41,47),(p+'registry/CapabilityRegistry.java',132,135)],
 '实际Laser.use startUsing→原生AFTER_ENTITIES渲染回调手持且using/能量足够，近目标或远射线+遮挡通过→每worldTime%4==0发C2S实体id与近远bool并本地音；原生注册playToServer→enqueue当前世界查实体/主手物→canShoot→hurt返回真才真实提取能量。',
 '一条真实C2S攻击结果/验证链计1，未将codec/近远模式/音频包装拆数。服务端target未判null就.isAlive，丢失id可能NPE；isInvulnerable是通用标志非实际DamageSource拒绝。服务端不重检距离/LOS/实际using、信任近远bool；渲染worldTime取模不是once-per-tick，单tick多帧会多包。resetStackDamageCool写EMPTY.copyTag临时副本、getter也读EMPTY，不持久保存cooldown，且此链没有读取getter；不能声称5tick节流。声音在客户端请求时发、不依赖hurt结果；false不等于Boss免疫，也不能将可听声当击中成功。',
 '正式反馈需服务端语义决定和独立按目标/事件节流，不能把渲染帧当tick或把请求音当拒控回执；S2C目标需处理实体缺失。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'cyclic-native-batch33','credited_chains':keys,'rationale':'区域缓存拒附加；原生击退取消；拒绝与递归替换语义；真实激光C2S验证/结果链共4。方法、装备常量、粒子及注册均非额外信用。守卫旧账0，助手来源未占。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
