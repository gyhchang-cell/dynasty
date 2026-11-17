"""Native emu projectile denial: animation window is not an all-damage invulnerability."""
from ledger import B,O,record,verify
import json
r='AlexModGuy/AlexsMobs';p='src/main/java/com/github/alexthe666/alexsmobs/';k='alexsmobs-emu-native-impact-denial-and-animation-window'
def whole(f):
 f=p+f
 return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
record(k,r,[(p+'event/ServerEvents.java',240,283),(p+'entity/EntityEmu.java',43,65),(p+'entity/EntityEmu.java',142,226),(p+'entity/AMEntityRegistry.java',81,81),(p+'AlexsMobs.java',75,114),(p+'ClientProxy.java',160,160),whole('client/render/RenderEmu.java'),whole('client/model/ModelEmu.java'),(p+'item/AMItemRegistry.java',257,257)],
 '实际Forge注册ServerEvents/EMU实体和spawn egg；native ProjectileImpactEvent仅server entityhitEmu→先箭pierce0→已有左右侧闪且animationTick<7取消；不是侧闪则按弹位置相对左右look选方向/并列random→setAnimation左右10tick→非墙碰撞先move→追加侧向velocity并取消命中→native Emu.tick调用Citadel updateAnimations→本体IAnimatedEntity字段读写→已注册RenderEmu/ModelEmu.setupAnim→完整animate左右4tick姿势+1hold+5reset。',
 '一个实际原生命中拒绝及侧闪窗口整链1，左右动作/模型骨骼/egg/动画函数0额外。若已在侧闪且tick>=7，两段if都不取消；不应把10tick动画等同10tick免疫。首次事件即使horizontalCollision阻止初move，仍加velocity/cancel，动画可与位移不一致。所有AbstractArrow在窗口判断前pierce0，包括本次未取消的后段命中，不把它误称精准只取消本次箭。native Emu.hurt仍super，成功才启动群体逃跑，侧闪并不覆盖所有伤害。Model左右姿势表达真实侧倾，但低帧像素/网络未验。',
 'Boss免控持续窗口必须按服务端实际取消条件测；动画长度不等于拒绝长度，碰撞不能用画面位移反推是否拒绝。普通body免疫无需灰字；本条是研究原生裁决时序而非给Boss新增侧闪。',
 '固定09755dade2cfbdf14839e026d3af446f9d3ff843，全包含方法及实际注册入口已观察。Citadel动画时间推进/同步框架内部未在本条补全，框架0且不声称完整S2C动画成功；确认的是本模组native cancel与显式动画调用/模型消费。左右/颜色和概率裤装不另计；未游戏/正式代码/资产/TODO修改。','native_final_projectile_refusal')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'alexsmobs-emu-batch60','credited_chains':[k],'rationale':'实际撞击时方向侧闪+原生动画段落拒绝不同于纯概率hurt取消/反弹；左右keyframes与各bone不拆。EMU裤装45%投射伤概率取消与既有概率闪避同型0，章鱼owner友伤最终取消并既有归属友伤0，RockyRoller反伤后super与ShieldOfDeep未查effect成功不当免疫。VoidWormPart replay native producer有空damageType→receiver先registry gate，保留待核0，不以方法存在假称成功同步。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
