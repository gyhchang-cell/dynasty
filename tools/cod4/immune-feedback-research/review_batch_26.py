"""Manually reviewed game feedback sites; shared graphics/sync helpers earn zero."""
from ledger import B,O,record,verify,attach_auxiliary
import json
r='TeamLapen/Vampirism';v='projects/vampirism/src/main/java/de/teamlapen/vampirism/';f='projects/faction/src/main/java/de/teamlapen/';keys=[]
def whole(q):return q,1,len((B/'sources'/r.replace('/','__')/q).read_text().splitlines())
def s(q,a,z):return q,a,z
def add(k,refs,chain,obs,lesson):
 record(k,r,refs,chain,obs,lesson,'固定83c220f47cd030eed4c779c90f5786b261075869；逐项完整方法与实际注册/生产上下文观察。未运行，不证明画面、TCP或音效；普通阴阳体质不要求灰字。共享图形/同步包装与常量变体0。','native_game_feedback_lifecycle');keys.append(k)
client=[whole(v+'client/VampirismModClient.java'),whole(v+'client/ClientServices.java'),whole(f+'faction/Services.java')]
d=v+'common/world/entity/dracula/Dracula.java'
add('vampirism-mist-native-boss-target-envelope-and-motion-lifecycle',client+[s(d,126,174),s(d,188,220),s(d,237,242),s(d,348,371),s(d,560,629),s(v+'client/core/ModEntitiesRender.java',72,111),whole(v+'client/renderer/entities/DraculaRenderer.java'),whole(v+'client/renderer/MistStateTracker.java'),whole(v+'client/renderer/MistRenderer.java')],
 '实际Boss burst转MIST→FIGHT_STAGE实体同步回调启动/停止mistAnimationState→已注册DraculaRenderer提取状态并复制动画→submit只在MIST时替换实体显示，按原生100tick窗口与300ms入/出计算fade；独立已注册ClientTick tracker用实体UUID取实际位置差估算远端速度/flow，提交Boss云雾使用它。',
 '远端getDeltaMovement近0故用相邻位置差，差平方>4当传送归零再0.12平滑；暂停不推进，null level/WorldLoad清Map。注释称卸载会自行衰减，但只遍历entitiesForRendering内的实体tick：卸载实体正fade状态不再衰减，removeIf<=0不能清它，可留到换世界。Boss包络来自原生状态动画而非tracker的getFade，不能混写。逐目标位置/寿命这一职责计1；通用VolumetricBillboards未计，shader深度未读不声称遮挡正确。',
 'Boss回执目标锚定应以真实客户端实体位置和插值为准，传送与普通移动区别处理；卸载/失踪须实际淘汰，注释或一个removeIf不等于完整生命周期。')
add('vampirism-native-aura-feedback-nearest-target-budget',client+[whole(v+'common/world/entity/player/vampire/actions/VampireActions.java'),whole(v+'common/world/entity/player/vampire/actions/AuraOfDarknessAction.java'),whole(v+'client/core/ModEntityRenderStates.java'),whole(v+'client/renderer/AuraOfDarknessStateTracker.java'),whole(v+'client/renderer/AuraOfDarknessRenderer.java'),s(v+'client/renderer/RenderHandler.java',124,156),s(v+'client/renderer/RenderHandler.java',203,226)],
 '实际已注册持续Aura动作onUpdate每40tick向附近吸血鬼addEffect100tick→全LivingEntity render modifier读取状态tracker fade→RenderLivingPost提交相机相对中心→已注册AfterWeather按中心距离从远到近排序，仅取最后最近12个且32格内的实例；finally清本帧队列。',
 '真正相关的游戏状态反馈可见性预算，不把每次绘制/包装计数。目标center来自其poseStack与实体高度，不含entityUUID序号，因此同帧重复提交无显式去重；12总量上限也不是按目标免疫事件限流。Aura在Mist后注册，多个同阶段透明批次按注册次序；未读shader不以注释宣称完整depth。Aura与Mist共有逐UUID淡变结构合并0额外，卸载不衰减问题同样存在。invisible/bat/mist取消player原生render可避光环暴露，其它取消者行为未实测。',
 'Boss灰字需区分每帧最大显示数、距离裁剪、每目标节流与同事件去重；可保留最近目标预算而不把简单上限称不刷屏。')
vp=v+'common/world/entity/player/vampire/VampirePlayer.java'
add('vampirism-native-dbno-client-presentation-edge-and-authority-recheck',
 [s(vp,593,609),s(vp,961,999),s(vp,1061,1089),s(vp,1347,1353),whole(v+'common/core/ModAttachments.java'),whole(v+'common/core/ModRegistryManager.java'),whole(v+'common/CommonServices.java'),whole(v+'VampirismMod.java'),whole(v+'common/network/ModPacketDispatcher.java'),whole(v+'common/network/packets/server/ServerboundSimpleInputEvent.java'),s(v+'common/network/ServerPayloadHandler.java',79,113),s(v+'client/ClientProxy.java',104,109),s(v+'client/ClientProxy.java',149,155),whole(v+'client/gui/screens/DBNOScreen.java'),whole(v+'client/gui/components/CooldownButton.java')],
 '实际原生拒死进入DBNO并sync→已注册VampirePlayer attachment使用具体序列化/同步options→dbno_timer属性loadDBNOTimer按进出边沿打开本地存活玩家屏幕/设置睡姿/refreshDimensions；DBNOScreen禁Esc、不暂停，20tick后give-up启用；timer/总时长决定复活按钮，点复活本地tryResurrect后C2S，服务端原生handler再次tryResurrect。',
 '接收的timer先于具体展示，只有进DBNO边沿开屏；离DBNO只重置pose，不在loadDBNOTimer直接关屏。复活以权威timer==0为准；客户端不为0也会本地timer=-1，服务端不为0仅sync意图纠正，但AttachmentSync只在属性dirty时发，未运行不能保证未dirty时真的重发。propertiesMap HashMap没有timer/message原子顺序保证，初次屏幕保存causeOfDeath后不自动刷新。全部具体拒死反馈/客户端边沿/重确认合1，协议包装0额外；不把此UI当Boss头顶文字。',
 '免控回执应为服务端已完成拒绝后的结果，客户端显示不能反向决定控制成功；同一目标的语义与文本应原子传递，重复状态同步不反复开新提示。')
aux=[whole(f+'sync/BaseAttachmentSyncHandler.java'),whole(f+'sync/AttachmentSync.java'),whole(f+'sync/PropertySync.java'),whole(f+'sync/properties/Property.java'),whole(f+'sync/properties/SimpleProperty.java'),whole(f+'sync/properties/DataApply.java'),whole(f+'faction/common/util/AttachmentSynchronization.java')]
attach_auxiliary(keys[-1],r,aux,'完整读取以验证DBNO实际属性装载及dirty同步限制；通用同步实现仅辅助，0计数。')
p=O/'semantic-dedup.json';data=json.loads(p.read_text());data['groups'].append({'family':'vampirism-feedback-lifecycle-batch26','credited_chains':keys,'rationale':'3个独立具体游戏职责：Boss原生雾态目标运动/生命周期、实际状态Aura最近目标预算、拒死DBNO展示边沿/权威重确认。两个tracker公共淡变结构/通用同步/通用渲染0额外；未把每个方法独立计。'});p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');verify()
