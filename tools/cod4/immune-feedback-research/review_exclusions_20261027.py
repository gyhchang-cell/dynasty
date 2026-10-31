"""Append inspected zero-credit evidence, never auto-promote candidates."""
from ledger import B,O,R
import hashlib,json
p=O/'candidates.json';rows=json.loads(p.read_text())
def add(key,repo,files,state,reason,remaining):
 assert key not in {x['id'] for x in rows}
 root=B/'sources'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());refs=[]
 for path,a,z in files:
  f=root/path;assert 1<=a<=z<=len(f.read_text().splitlines());refs.append({'path':str(f.relative_to(R)),'source_path':path,'lines':[a,z],'file_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'url':f'https://github.com/{repo}/blob/{meta["commit"]}/{path}#L{a}-L{z}'})
 rows.append({'id':key,'repo':repo,'commit':meta['commit'],'status':state,'research_credit':0,'reason':reason,'remaining_for_promotion':remaining,'source_refs':refs})
r='lehjr/ModularPowerArmor';q='src/main/java/com/github/lehjr/modularpowerarmor/'
add('mpa-damage-placeholder-not-implemented',r,[(q+'event/EntityDamageEvent.java',1,37),(q+'basemod/ModularPowerArmor.java',65,83)],'excluded_inactive_placeholder','实际EntityDamageEvent全类仅打印entity type；取消火伤代码在注释中，构造中的相关EVENT_BUS.addListener也注释。注释声称cancel仍播伤害动画/声音不是实际实现证据。','固定提交不晋级；不能以Todo或注释为有效游戏机制。')
r='CammiesCorner/Arcanus';q='src/main/java/dev/cammiescorner/arcanus/'
add('arcanus-stun-native-producer-consumer-not-yet-linked',r,[(q+'common/component/entity/StunComponent.java',1,47),(q+'common/registry/ArcanusComponents.java',238,248),(q+'client/gui/overlay/StunOverlay.java',1,49)],'reviewed_zero_pending_producer_activation','已完整看StunComponent serverTick/NBT/setTimer同步、isStunned/getset和StunOverlay。现有选定缓存没有证明谁实际设置正计时、谁调用屏幕渲染或最终动作拦截；计时组件/屏幕函数存在不能证明原生接活。','须补实际施加/拦截生产和UI注册，不从只下载52个选定Java推断整个项目无功能；DangerSense和Bounce同既有无条件闪避/弹跳族0。')
r='BluSunrize/ImmersiveEngineering';q='src/main/java/blusunrize/immersiveengineering/'
add('ie-shield-shock-pre-damage-phase-reachability-pending',r,[(q+'common/EventHandler.java',242,294),(q+'common/items/IEShieldItem.java',98,187),(q+'common/util/Utils.java',368,382),(q+'ImmersiveEngineering.java',195,195)],'reviewed_zero_pending_native_phase_reachability','完整native LivingDamage.Pre→active shield/original>=3/canBlockDamageSource→hitShield读过；shock会丢弃投射物并newDamage0，40 cooldown在非使用时支付每tick10能量缩短；flash addEffect忽略接纳仍清target。因全额原版盾挡后此Pre是否仍派发，尚缺对应NeoForge生产管线佐证，不把仅注册函数当真实盾命中已可达。','补固定版本原生伤害事件生产、盾吸收先后与部分伤害可达分支后再评估；client闪白不是免疫反馈，暂0。')
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print({'zero_credit_candidates_total':len(rows),'new':3,'credit':0})
