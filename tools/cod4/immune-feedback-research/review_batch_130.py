"""Main native review of Herschel016/017; no credit copied from helper proposals."""
from ledger import B,O,record,verify
import json,hashlib
r='Infamous-Misadventures/Dungeons-Mobs';p='src/main/java/com/infamous/dungeons_mobs/'
def f(x,a,z):return p+x,a,z
common=[f('DungeonsMobs.java',47,80),f('mod/ModEntityTypes.java',582,589)]
# Resume-safe after range validation; existing rows never count again.
_original_record=record
def record(key,*args,**kwargs):
 rows=json.loads((O/'reviewed.json').read_text())
 if any(x['id']==key for x in rows):return next(x for x in rows if x['id']==key)
 return _original_record(key,*args,**kwargs)
k1='dungeonsmobs-native-shared-shield-overflow-tick-cascade-versus-regeneration'
record(k1,r,common+[f('entities/blaze/WildfireEntity.java',68,251),f('entities/blaze/WildfireEntity.java',265,332),f('mod/ModEntityTypes.java',397,404),f('client/models/blaze/WildfireModel.java',17,93),f('client/renderer/blaze/WildfireRenderer.java',29,32)],
 '固定注册实体→finalizeSpawn置四盾/60共享盾血→真实hurt有盾且非OUT_OF_WORLD/DROWN时记录Living仇恨、全额减共享shieldHP、阈值最多breakShield一次或hurt声，并false。baseTick剩盾且共享血<=0每tick再break一次；每break重置150tick重生计时。计时到0补一盾且共享血+15，并重设150。NBT仅盾数/血未存计时；synced count在WildfireModel同一函数控制四盾骨隐藏。',
 '计1的是实际共享累积负债与后续tick级联/逐个补库存的结算策略，不按四盾、模型、声音拆分。Goety Wildfire已计且AI代码注明参考本项目；主岗因此逐一重读Goety hurt419–456/aiStep474–551/break332–347/add349–356：其每次break将盾HP重置单盾上限，rearm也重置，非此处保留负数+add15累积；故保留这一真正不同最终结算位点，而不因另一个项目/移植包装计数。此处即便hurt=false也已经耗盾资源；大伤一次仅破一个，后续<=0才级联。负值足够大时刚补的盾同tick再次破；无server限定，不能称仅服务端改资源。',
 'Boss拒控不能依据hurt=false决定；反馈须绑定明确控制拒绝而非资源吸收。补库存/破盾tick和每次拒绝声的节奏不是每目标回执节流，不能靠四骨可见性推断逻辑身份。',
 '只静态完整方法/注册和一个模型消费者；缓存未找到WildfireRenderer实际注册，故模型方法存在不证明实机显示。NBT失计时与负数级联是条件静态推演，未复现存档问题；没有TCP、像素、声或灰字通过结论。Goety对比只支持0，不再加已计credit。','native_shared_shield_overflow_lifecycle')
k2='dungeonsmobs-native-orb-overlap-ingress-and-root-passenger-control-after-denied-damage'
record(k2,r,common+[f('mod/ModEntityTypes.java',119,126),f('mod/ModEntityTypes.java',492,498),f('entities/projectiles/StraightMovingProjectileEntity.java',1,343),f('entities/projectiles/NecromancerOrbEntity.java',1,252),f('entities/undead/NecromancerEntity.java',89,102),f('entities/undead/NecromancerEntity.java',173,213),f('entities/undead/NecromancerEntity.java',384,447),f('utils/PositionUtils.java',13,16)],
 '实际注册Necromancer的ShootAttackGoal在攻击动画动作点构建已注册Orb、设延迟成形并addFreshEntity。父baseTick真实server AABB实体列表→canHitEntity→Entity形参重载；该入口没有另一个tick射线分支的Forge onProjectileImpact门。Orb排除undead Mob后native伤害，成功只约束附魔附效；无论false仍对目标rootVehicle.ejectPassengers、加弹速度*2、播声、vanish40并event1。客户端event1设vanish计时，predicate消费成形/消失/idle。',
 '计1合并备用原生碰撞入口与骑乘根拓扑控制的完整独立副作用点；非通用hurt后push模板单独加分。父tryToDealDamage先于Orb自己的减计时/停速；canHitEntity不按forming/vanishing排除，重复合格接触可重设vanish计时，但父200+40寿命仍封顶。父onHitEntity(Entity)先声，Orb又声，只有hurt=true且alive才附魔，不限制强制下乘。射线事件取消不证明AABB入口也取消；继承super.canHitEntity仍可能拒绝部分候选。',
 '控制免疫要覆盖每个真实控制入口并在root乘骑拓扑变化前裁决；不要以生命伤害拒绝/消失事件当控制拒绝。Boss灰字应来自最终拒控语义，合并同次多入口回执但保留正确目标归属与生命期。',
 '父/子完整文件、原生goal和注册全文所引范围已读；原版Projectile内部onHit(EntityHitResult)派发未展开，结论只限明确AABB→Entity重载，不称所有原生事件皆可绕过。addFreshEntity结果忽略，不保证每次实际spawn；event1非灰字，无UUID/代际或去重。未运行、未证明实机可辨/声音/双端。','native_alternate_control_ingress_and_receipt_lifetime')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch130-herschel016017-native-main-review','credited_chains':[k1,k2],'rationale':'Wildfire exact overflow preservation/cascade differs from already counted Goety HP-reset settlement, no per-project/port credit. Orb alternate AABB ingress plus root passenger topology is independent of prior stomp and paired-attempt-history. Squall dormant damage gate downgraded support0 as phase-denial pattern; shockwave side effects and bool reflection support0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
review={'research_credit_promoted':2,'helper_credit_remains':0,'support_credit':0,'decisions':[{'helper':'herschel-016-01','master_id':k1,'credit':1},{'helper':'herschel-016-02','credit':0,'reason':'Phase denial/wake policy retained support, no extra for activation sounds/animation. Helper Squall tick ref207–215 incomplete; main read containing206–246 including raid wake and timeout.'},{'helper':'herschel-016-03','credit':0,'reason':'hurt then fire/motion generic negative already covered; main source read.'},{'helper':'herschel-017-01','master_id':k2,'credit':1},{'helper':'herschel-017-02','credit':0,'reason':'Constant false override / vanilla-style reflection already covered; no live reflected Orb claim.'}],'source_integrity':'All016/017 manifest file SHA256 plus fixed tree Git blob checked locally before admission; source count/file/methods do not credit.','batches':[]}
for b in ['016','017']:
 q=O/f'helpers/herschel-immune/batch-{b}.json';review['batches'].append({'path':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
(O/'HERSCHEL-016-017-REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n');verify()
