"""Ice and Fire final native gates; all caste/element/part wrappers merged."""
from ledger import B,O,record,verify
import json
r='AlexModGuy/Ice_and_Fire';p='src/main/java/com/github/alexthe666/iceandfire/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
base=[(p+'IceAndFire.java',95,119),(p+'entity/IafEntityRegistry.java',25,40),(p+'entity/IafEntityRegistry.java',60,65),(p+'entity/IafEntityRegistry.java',84,92)]
def add(k,refs,c,o,l):
 for f,a,z in base+refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines()),(f,a,z)
 record(k,r,base+refs,c,o,l,'固定02b2922003cbce3c67dad55dfea79acf1721e0db，老版本API独立观察，不和现代Forge代码拼接；完整关键自有方法与实际registry/modbus启用已读。未运行/未证观感和音效/未改正式Java资产待办。', 'native_final_denial_and_side_effect_order');keys.append(k)
add('icefire-hydra-native-multihead-lethal-floor-after-sever-receipt',[(p+'entity/EntityHydra.java',75,112),(p+'entity/EntityHydra.java',120,238),(p+'entity/EntityHydra.java',240,287),(p+'entity/EntityHydra.java',324,344),(p+'entity/EntityHydra.java',354,371),(p+'entity/EntityHydra.java',429,443),(p+'entity/EntityHydra.java',466,472),w(p+'entity/EntityHydraHead.java')],
 '实际Hydra/HydraHead注册→constructor resetParts与阈值→native tick重建/添加头颈parts→head.hurt先onHitHead再parent.hurt→Hydra.hurt累计对应头伤、超过阈值先断头/播放GUARDIAN_FLOP，之后health<=amount+5且多头且非bypassInvul才置amount0再super；native aiStep100tick火烧扣头/非火再生。',
 '多头存活阶段的最后致命伤归零点1，部位转发/阈值/头数常量不拆。拒伤前仍可改断头状态并播放声音，所以零伤/false不是无事件；没有清除附加控制，也无Boss灰字/按目标拒绝节流。实际aiStep保持正常攻击、吐息和regrow；一头未着火会回两头并只补一头，火阻止额外头，tick去掉原生再生。原damage未clamp finite，head index仅>count矫正不是>=，本条只记录静态边界不宣称运行错误。head wrapper没有调用普通MultipartPart.hurt，因而不能把后者C2S玩家包误接到这个覆盖方法；原生multipart碰撞完整路由内部未运行。断头/再生音不是每次免疫嗡声，parts Blood粒子属于断头不是拒控闪光。',
 '当前攻击未扣血仍可能先触发断头/音效；Boss拒控灰字必须由控制裁决点发出，并保证拒控前没有位置/姿态副作用。')
add('icefire-dragon-native-corpse-and-rider-relation-final-damage-filter',[(p+'entity/EntityFireDragon.java',43,80),(p+'entity/EntityDragonBase.java',889,898),(p+'entity/EntityDragonBase.java',985,998),(p+'entity/EntityDragonBase.java',572,590),(p+'entity/EntityDragonBase.java',1672,1702)],
 '真实FireDragon注册+constructor继承DragonBase→native hurt按modelDead、控制乘客关系、被骑载状态及来源过滤→拒绝时returnfalse先于roar/唤醒/设目标→剩余super.hurt；native tickDeath设modelDead并驱离乘客，模型尸体状态entityData与server字段同步。',
 '一套尸体/骑乘关系最终裁决1，三龙元素、各环境source值不拆。getControllingPassenger只匹配驯服owner UUID且不是当前攻击目标的Player，不等同任何乘客；被载时箭判定使用msgId.contains而非projectile类型，或source.entity等于vehicle则拒伤。modelDead允许OUT_OF_WORLD，其后规则仍可能拒；尸体保护不代表活体Boss免控。接受路径有25%roar且睡眠唤醒/仇恨在super返回前，不能将声音当hurt成功。此链没有目标拒控文字/微光/嗡声/节流。tickDeath全部方法已读，cloud与骨骼死亡不是本项拒控特效，不复制资产。',
 '明确目标当前生命周期和攻防关系；拒控反馈绑定活体Boss本体与当前世界，不能对尸体/坐骑保护误发IMMUNE。')
add('icefire-myrmex-native-growth-window-inwall-final-refusal',[(p+'entity/EntityMyrmexBase.java',183,191),(p+'entity/EntityMyrmexBase.java',221,272),(p+'entity/EntityMyrmexBase.java',340,346),(p+'entity/EntityMyrmexWorker.java',280,291),(p+'entity/EntityMyrmexSentinel.java',273,282),(p+'entity/EntityMyrmexEgg.java',104,165)],
 '真实Myrmex各caste注册→native Egg.tick孵化构造实体并setGrowthStage0→EntityMyrmexBase native hurt：stage<2且IN_WALL直接false，其他来源仍先蛹wiggle再super；native tick成长计时stage++，到2不再享受门。',
 '随实际成长生命周期关闭的最终拒伤点1，五caste/阈值/伤害source不拆。defineSynchedData默认2，但真实egg生产0已读，避免只读default误认门不可达。native tick成长未加server-only门，动画由Citadel推进，未把本地wiggle当原生网络像素证据。Worker hurt会在super门之前按amount掉手物并stopRiding，Sentinel会解hide/设visibleTicks且可能放乘客，所以基类拒伤不回滚子类副作用。不是Boss控制免疫，不生灰字。与恒定来源清单不同在于原生生长事实控制有效窗口；没有跨世界缓存/拒绝回执节流。',
 '从真实生产点核对免疫资格生命周期；最终拒绝之前已执行的动作不能靠上层返回false自动撤销。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'icefire-batch47','credited_chains':keys,'rationale':'多头致命伤保护、龙尸体/骑乘关系保护、真实成长窗口拒窒息各1；各头/元素/caste/包装不拆。Ghost/Scuttler/Hydra poison list只是普通效果常量清单，未另信用；worker/sentinel副作用为基类辅助0；普通Multipart网络是同转发链辅助不算新实现。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
