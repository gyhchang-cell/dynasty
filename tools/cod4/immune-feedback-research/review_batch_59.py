"""DivineRPG actual native immunity policies; colour/constant/wrapper variants merged."""
from ledger import B,O,record,verify
import json
r='DivineRPG/DivineRPG';p='src/main/java/divinerpg/'
def whole(f):
 f=p+f
 return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
common=[whole('entities/base/EntityDivineBoss.java'),whole('entities/base/EntityDivineMonster.java'),whole('DivineRPG.java'),whole('attachments/base/ModAttachment.java'),whole('attachments/base/SynchedAttachement.java'),whole('attachments/base/ServerHandledAttachment.java'),whole('registries/AttachmentRegistry.java'),whole('network/Payloads.java'),(p+'registries/EntityRegistry.java',1226,1228),(p+'registries/EntityRegistry.java',1246,1250)]
a='divinerpg-native-spatial-companion-class-selective-immunity'
record(a,r,[whole('entities/boss/EntityAyeraco.java'),whole('blocks/vanilla/BlockAyeracoSpawn.java'),whole('block_entities/bosses/AyeracoSpawnBlockEntity.java'),whole('client/renders/entity/boss/RenderAyeraco.java'),(p+'registries/EntityRegistry.java',203,203),(p+'registries/EntityRegistry.java',1004,1004)]+common,
 '已注册Ayeraco实体/真实spawn egg与renderer；BlockAyeracoSpawn server ticker→600tick分段放beam→0tick造六实体并setVariant→原生isInvulnerableTo从当前世界32轴向AABB同类实体即时查询绿/粉variant→选择拒绝三种投射源/三种magic源；原生hurt始终先super再按自身variant和附近同类执行治疗/加速/加伤/传送。VARIANT已注册attachment和native payload，onAdded client请求→server本level查numericID回包→client本level查ID setData→renderer当前getVariant选texture。',
 '空间集合/伤害类别联合拒绝独立1，不按绿粉颜色、六实体或多个source常量加数。与SkullLord按绑定partner UUID生死决定整段无敌不同：无固定partner绑定，也不跨维度搜；同类自己也在查询集合，绿/粉可自护，附近任意同色可护其他；查询本身未显式isAlive/视线/球距离，32是AABB各轴范围。hurt的附加动作不检查super返回b，只要server且仍alive就可能发生，所以传送声/群疗不是明确拒绝回执。setVariant(0)写6蓝，但name switch仍用传入0走default蓝；setSilent constructor默认0，isGreen/isPink只读attachment而renderer getVariant另有beam fallback，不能以texture证明服务端免疫类别。',
 'Boss拒控回执必须来自明确拒绝分支，不能拿hurt后无条件的传送/声音判免疫；状态纹理和每次拒绝浮字分开。以当前世界查ID并存在检查仍没有UUID/代际/维度/事件序列校验。',
 '固定3cebbbe867d743c456106971430665ee8e1a1de2，包含方法/关键原生入口已读。通用attachment复用随本链0，不拆网络函数加credit；request server只检实体存在，无距离/类型限制；set只在data变化时update，与每目标免疫事件节流不同。上游BlockRegistry/BlockEntityRegistry未全读，方块自然获取未验，实体自身注册/egg/native gate已确认。不声称像素/声音/真实TCP通过。spawn保存pinkBeam错写greenBeam静态可见但不另计，不修上游。','native_final_damage_refusal')
b='divinerpg-luna-native-rotating-source-denial-and-state-texture'
record(b,r,[whole('entities/boss/EntityLadyLuna.java'),whole('client/renders/entity/boss/RenderLadyLuna.java'),(p+'registries/EntityRegistry.java',218,218),(p+'registries/EntityRegistry.java',1014,1014)]+common,
 '实际注册Luna/egg/renderer→constructor保护计时200至399→server原生tick递减到0→setRandomProtectionValues random.nextInt(2)→setProtectionType写VARIANT/速度→native hurt按当前protection分类最终return false或super→已注册tracking attachment同步/客户端初入请求→renderer按VARIANT选arcanic/ranged/default纹理。ImmunityCooldown通过原生save/load保存。',
 '一个轮换政策生产点及状态消费整链1，0/1/2各source条件不另计。随机只产0/1，不能声称正常轮换会进2；未有attachment时getProtection用default2，而真实attachment默认值0，读取/初次set时hasData差异不能被省略。类型2拒除MOB_PROJECTILE/MAGIC外全部源，含非魔法bypass也无例外；type1的thrown msgId、type2的非projectile分支非严格补集。恒定EXPLOSION拒绝与Karos/KingOfScorchers同型合并0。timer==0当tick切换，不含<=0；存坏负值不会由此自然恢复。render状态变化不是每次拒伤文字，hurt早return前无免疫嗡声/浮字。',
 '区分拒绝原因与护盾状态，按服务器实际政策发一次有目标身份的免疫回执；持久化与重连初态不能只验证某帧texture。Boss正常速度变化属于该上游机制，不据此要求本项目冻结Boss AI。',
 '固定版本/全文关键方法观察，仅静态。共用attachment receiver仅本level numericID存在检验，无UUID/维度代际；同值set不发包但不是免疫事件去重。未制作资产、未启动客户端/正式Java或TODO改动。模型/基础渲染未扩展研究，纹理选择消费观察不等于真实可辨识验收。','native_final_damage_refusal')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'divinerpg-native-policy-batch59','credited_chains':[a,b],'rationale':'空间同伴集合×类别政策与计时轮换×类别政策各1；绿粉/六实体、多个DamageTypes、状态纹理、网络wrapper全部随链合并。Karos/KingOfScorchers/Luna恒爆炸源拒绝0；Ancient恒fall false、Dramix隐身、Densos/Vamacheron音色与普通AI不加数。对照Goety SkullLord绑定UUID伙伴全免疫，不因同为同伴即忽略实际空间/类别联合仲裁的差别。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
