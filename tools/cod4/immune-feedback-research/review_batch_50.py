"""Tetra native projectile refusal and reflected-owner result, one gameplay chain."""
from ledger import B,O,record,verify
import json
r='Mickelus/tetra';p='src/main/java/se/mickelus/tetra/'
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
key='tetra-native-howling-projectile-impact-refusal-reflection-and-self-hud'
refs=[(p+'TetraMod.java',82,100),(p+'TetraMod.java',247,255),(p+'TetraRegistries.java',166,176),(p+'TetraRegistries.java',385,389),(p+'effect/ItemEffectHandler.java',331,334),(p+'effect/ItemEffectHandler.java',360,383),(p+'effect/EffectHelper.java',72,80),(p+'items/modular/IModularItem.java',874,888),(p+'ClientSetup.java',135,153)]+[w(p+'effect/howling/'+f+'.java') for f in ['HowlingEffect','HowlingPacket','HowlingPotionEffect','HowlingOverlay','HowlingProgressGui','HowlingIndicatorGui']]
for f,a,z in refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
record(key,r,refs,
 '真实TetraMod登记ItemEffectHandler与effect registry/HowlingPacket→native client attack MISS而modularhandheld/howling>0发送空C2S→handle从server主手重读attackScale/effect→trigger stacking effect(持续效率*20,amp最高11)→实际ProjectileImpact转Howling.deflect，实体有effect且roll达标才改箭方向/或owner再cancel原生impact；原生client effecttick环绕POOF，真实已登记HowlingOverlay在START tick取本地effectamp画12格HUD。',
 '独立最终弹源反射/拒撞点整链1，C2S/状态/每档概率/POOF/HUD绘制包装不拆。willDeflect使用原生零基amp*.125，amp0不挡；tooltip用amp+1且声称每级12.5/2.5%，与实际最终门零基及owner转换amp*.02有差异，不能拿HUD满格/文字宣称拒绝概率。普通反射取弹速关于目标中心法线反射，owner仍旧；反向分支乘-.8方向后shoot(speed=原速度length)归一化，.8不等于实际降速，改owner为目标并对原shooter setLastHurtMob(entity)，不能误当真实当前伤害。该事件没有server-only gate，双方若都产生event会各自roll，不能静态声称服务端权威一致；无明确Boss IMMUNE/逐目标节流/拒绝声灰字。空C2S handle未instanceof modular校验而EffectHelper强转IModularItem，原生发送筛选不保证收包安全；未读Mutil外部AbstractPacket底层派发side/线程，辅助0不推测可远程复现。HUD为本地状态，不证明每次impact拒绝；只有原版effect状态同步，没有自有拒绝S2C。',
 'Boss反馈必须由server明确当前控制拒绝触发，收包独立校验目标/世界/事件理由；状态HUD/概率配置/箭回弹外观不能代替真实拒控回执。',
 '固定d212377491eaf2ef58ea841f0e45d532d5e69f95，789本地源码仅下载/缓存0。本条全部关键完整方法已读；modular effect数据cache内部与通用GUI仅辅助，未读具体装备JSON获取链，不宣称自然获取或运行画面。未启动游戏、未改正式源码/资产/待办。','native_projectile_refusal_and_feedback_state')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'tetra-batch50','credited_chains':[key],'rationale':'原生howling状态→impact最终方向/owner拒绝→本地HUD整链1，不拆wrapper/档位；单独onLivingAttack反伤未取消当前攻击，不误记免疫。Mutil通用基建0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
