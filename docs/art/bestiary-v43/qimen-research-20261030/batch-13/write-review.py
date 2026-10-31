from pathlib import Path
import json,hashlib,datetime,html,os
B=Path(__file__).resolve().parent;R=B.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def src(id,p,rg,version):return dict(id=id,local=os.path.relpath(p,B),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reviewed_ranges=rg,version=version)
m=json.loads((B/'native-consumers.json').read_text());ranges={'ItemInHandRenderer':[[290,308],[350,500]],'ItemInHandLayer':[[1,56]],'HumanoidModel':[[230,314],[385,399]],'ItemRenderer':[[95,145],[195,231]],'ItemTransform':[[1,64]],'LivingEntity':[[1038,1193],[1245,1276],[2996,3020]],'AbstractArrow':[[111,246],[284,387]],'Projectile':[[140,185]]};sources=[]
for f in m['files']:
 f['reviewed_ranges']=ranges[f['id']];f['status']='FULL_READ' if ranges[f['id']]==[[1,f['lines']]] else 'SELECTED_RANGES_READ';sources.append(src(f['id'],B/f['reading_view'],ranges[f['id']],'Minecraft1.20.1 MCP before Forge; not Fabric merged'))
save(B/'native-consumers.json',m)
p=R/'batch-02/sources/Provismet__Dual-Swords';commit='8c306787a59990d88963e70cf293823131c59196';q='src/main/java/com/provismet/dualswords/'
for id,path,rg in [('DSLiving',q+'mixin/LivingEntityMixin.java',[[1,188]]),('DSFirstPerson',q+'mixin/HeldItemRendererMixin.java',[[1,88]]),('DSThirdPerson',q+'mixin/HeldItemFeatureRendererMixin.java',[[1,45]]),('DSItem',q+'mixin/ItemMixin.java',[[1,90]]),('DSDeflect',q+'enchantments/DeflectEnchantment.java',[[1,39]]),('DSMixins','src/main/resources/dualswords.mixins.json',[[1,16]]),('DSVersion','gradle.properties',[[1,28]])]:
 s=src(id,p/path,rg,commit);s['repo']='Provismet/Dual-Swords';s['fixed_url']='https://github.com/Provismet/Dual-Swords/blob/'+commit+'/'+path;sources.append(s)
e=[]
def add(id,text,refs,limit):e.append(dict(id=id,finding=text,sources=[dict(source=s,ranges=r) for s,r in refs],limit=limit,credit_added=0))
add('D01','固定源为Dual Swords1.1.2，MC1.20.1、Yarn build10、Fabric loader0.15.6。声明的client Mixins包括第一/第三人称持物；此处原版MCP仅用于对照同版本控制流。',[('DSVersion',[[6,21]]),('DSMixins',[[1,16]])],'未构建或导出Fabric合并类，不认证目标ordinal和Local注入成功，也不套用Forge的工具能力补丁。')
add('D02','Parry读取当前activeItemStack的附魔；ItemMixin使其返回BLOCK，并在use时设置使用手。原版BLOCK默认5tick，该Mixin到对应调用点后将此门槛改为2tick。',[('DSLiving',[[54,82]]),('DSItem',[[23,64]]),('LivingEntity',[[3001,3011]])],'仍须本来处于使用状态、物品不空并走到BLOCK分支；不是任何双持都被动格挡。')
add('D03','格挡还受原版伤害方向、BYPASSES_SHIELD和穿透箭规则限制；模组只在原判定为true时再排除BYPASSES_PARRY与非间接、能破盾的攻击者。',[('LivingEntity',[[1245,1267]]),('DSLiving',[[85,90]])],'严格双持联防没有在这段成立；Daisho、反击和Parry不可合并宣传。')
add('D04','反弹入口是damage尾部的blocked局部值+Parry+玩家。仅直接伤害实体为PersistentProjectileEntity且DEFLECT等级大于0时乘速度；不是通用反弹所有Projectile。',[('DSLiving',[[99,129]])],'@Local ordinal0与TAIL须在Fabric真实合并后验证；不声称已注入/实际触发。')
add('D05','原版完全格挡把伤害置0，最终return flag2为false。箭的onHitEntity在hurt返回false后才将当前速度乘-0.1。结合本模组的3L，条件式是v_hit=-0.3L*v_in，L最高3。',[('LivingEntity',[[1053,1069],[1165,1182]]),('AbstractArrow',[[328,386]]),('DSLiving',[[120,124]]),('DSDeflect',[[12,22]])],'前提为该注入确实执行、完全格挡、无其他速度改写；不是实测，也不能把中间3L说成最终3L。')
add('D06','箭tick在onHit后重新读取getDeltaMovement，再计算本tick位置，并施加空气/水阻力与重力；没有继续使用碰撞前缓存速度覆盖反弹。',[('AbstractArrow',[[167,201],[201,242]])],'普通空气、重力启用且其它条件不变时，反弹后的下一存储速度约为0.99*v_hit+(0,-.05,0)。不假定水中/NoGravity/第三方箭子类相同。')
add('D07','这一反弹分支仅改速度，没有setOwner；原版命中以原owner构造DamageSource。原生canHitEntity也仍用owner/leftOwner。',[('DSLiving',[[120,125]]),('AbstractArrow',[[311,320],[375,386]]),('Projectile',[[170,176]])],'不表示服务器世界中归属已转给格挡者；不能宣称反弹击杀会计给反弹者。其它Mixins/实体子类仍可能另改。')
add('D08','近战反击只有距离≤4.5时调用attacker.damage；其后的charged回调、附魔回调和耐久扣除位于距离if之外，也不检查伤害返回值。',[('DSLiving',[[102,118]])],'这是源结构边界，不将回调执行等同成功造成反击伤害；没有改游戏平衡。')
add('D09','第一人称Parry装备偏移将y中的equip项由-.6改为+.6，并按左右手叠加横移和Z倾角；swingProgress==0时还在push后预先翻转X180。',[('DSFirstPerson',[[30,55],[70,87]]),('ItemInHandRenderer',[[299,302],[357,361]])],'不是单个物品display rotation；不可只调剑模型角度来复制此效果。')
add('D10','同版本原版方法中applyItemArmTransform共有9个调用：377/403/418/423/426/429/453/479/490。getUseAnimation之后按源顺序的ordinal2对应BLOCK，ordinal4对应SPEAR；全方法ordinal8对应非使用的普通挥动分支。',[('ItemInHandRenderer',[[357,499]]),('DSFirstPerson',[[42,77]])],'这是源码控制流对应，不是Fabric字节码ordinal校验；同名映射和源顺序不足以证明Mixins运行成功。')
add('D11','第三人称先translateToHand、X-90、Y180并移动到手位，再进入物品renderer。模组在renderItem前对Parry物品另平移+X180；只有实际使用且activeItem==stack时加Z±45。',[('ItemInHandLayer',[[26,53]]),('HumanoidModel',[[391,396]]),('DSThirdPerson',[[23,44]])],'reference equality与Lunge的equals条件不同；第一/第三人称并非同一个矩阵或相同触发条件。')
add('D12','第一/第三人称选用各自ItemDisplayContext；ItemRenderer解析override后应用该display transform，再居中-.5。ItemTransform左手反向Y/Z旋转与X位移。最终角度须连手臂、Mixin和物品display一起判读。',[('ItemInHandRenderer',[[411,411],[494,494]]),('ItemInHandLayer',[[38,39],[47,52]]),('ItemRenderer',[[100,114],[202,227]]),('ItemTransform',[[32,46]])],'未读取此模组全部具体武器模型JSON/PNG，不把这项机制研究计成角色贴图参考或新武器外观完成。')
v=dict(saved_utc=now,status='SAVED_EXISTING_DUAL_SWORDS_POST_HURT_AND_HELD_POSE_CONSUMERS',source_family='既有Dual Swords/CombatPlus家族；原版支持消费者不另计',sources=sources,evidence=e,new_source_families=0,new_accepted_gate_credit=0,global_accepted_total=None,production_changed=False,java_game_started=False,pending=['Fabric合并字节码与实际Mixin应用未验证','反弹伤害归属/同步与第一第三人称实际画面未运行','严格双持联防仍非本段已证能力','每生物100个模型+PNG参考与六项各1000门槛独立保留'])
save(B/'post-hurt-pose-review.json',v)
parts=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>B13 格挡后箭消费者与持物矩阵</title><style>body{font:16px/1.65 system-ui;background:#141c20;color:#dbe3e5;max-width:1040px;margin:30px auto}a{color:#8ed1de}article{border-bottom:1px solid #43525a;padding:18px}</style><h1>B13 · 格挡后箭消费者与持物矩阵</h1><p>既有家族补读，0个新参考计数。没有修改生产模型、武器、任务或Java；不是实机验证。</p><p><a href="post-hurt-pose-review.json">固定来源与逐项边界</a> · <a href="native-consumers.json">原版基线/阅读范围</a> · <a href="local-verification.json">静态一致性检查</a></p>']
for a in e:parts.append('<article><b>'+a['id']+'</b><p>'+html.escape(a['finding'])+'</p><small>'+html.escape(a['limit'])+'</small></article>')
parts.append('</html>');(B/'index.html').write_text('\n'.join(parts))
save(B/'progress.json',dict(saved_utc=now,status='BOUNDED_SUBRANGE_SAVED_CONTINUING',deadline='2026-10-31T12:09:23+08:00',report='index.html',new_source_families=0,new_accepted_credit=0,production_changed=False,game_or_java_started=False,next='缓存的IE流体/供弹与渲染等真实未读消费者；不重试403端点。'))
p=json.loads((R/'progress.json').read_text());old=p['this_batch']
if not any(x['id']==old['id'] for x in p['previous_batches']):p['previous_batches'].append(dict(old,report=old['id']+'/index.html'))
p.update(updated_utc=now,latest_batch='batch-13',this_batch=dict(id='batch-13',source_studies=0,existing_family_context_extensions=1,evidence_records=len(e),new_accepted_gate_credit=0,count_note='同家族持物矩阵与post-hurt原版箭消费者，不新增生物/武器参考。'))
p['continuation_window'].update(last_saved_utc=now,report='batch-13/index.html',progress='batch-13/progress.json',status='ACTIVE_CONTINUING_AFTER_BOUNDED_BATCH');save(R/'progress.json',p)
print('saved',len(e),'bounded findings')
