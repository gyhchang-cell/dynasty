"""Native fangs refusal/accepted-hit settlement versus prehit entity-event sound."""
from ledger import B,O,record,verify
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/'
def f(s,a,z):return p+s,a,z
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='goety-native-master-fang-prehit-snap-event-versus-qualified-damage-settlement'
record(k,r,[w('common/entities/projectiles/MasterFangs.java'),w('common/entities/projectiles/Fangs.java'),
    w('common/magic/spells/FangSpell.java'),w('common/items/magic/MagicFocus.java'),
    f('common/items/ModItems.java',276,276),f('common/items/ModItems.java',443,443),f('common/magic/ModSpells.java',19,19),
    f('common/items/magic/DarkWand.java',548,568),f('common/items/magic/DarkWand.java',762,845),
    f('common/magic/Spell.java',92,107),f('utils/WandUtil.java',147,149),f('utils/WandUtil.java',904,1049),
    f('utils/MobUtil.java',122,145),f('utils/SEHelper.java',692,703),f('utils/SEHelper.java',723,744),
    f('common/entities/ModEntityType.java',248,258),w('client/render/MasterFangRenderer.java')],
    'BITING_FOCUS→MagicFocus/ModSpells.BITING FangSpell，原生DarkWand.finishUsingItem→MagicResults服务端SpellResult，正确ILL staff进入WandUtil图案/环形MasterFang生产，createMasterFang落地检查后入world。Fangs.native tick虚调用Master.fangTick：warmup<0发送entity event4并放大碰撞尺寸，<=-19发送一次event5闭合声；恰-21才在方块位置inflate1.4查询活体结算，<-33 discard。每实体damage producer明确拒owner、非目标Enemy、trueOwner盟友、双向盟友及isInvulnerable；实际hurt成功才强制iframe11和knockback，Player来源成功才火/灵魂收益。',
    '计1：真实魔法攻击预告/闭合声音先于最终目标资格与hurt成功，后置控制/收益只在成功后结算；整条Master/base家族合并，不将图案、base/子类、event4/5另加数。Fangs.handleEntityEvent虚调用Master.toClientHandle，4开attackAnimationState/本地spawn声，5仅本地snap声，均无目标ID/拒绝原因；即使空挥、盟友/无敌目标被过滤仍可发。warmup精确相等-21，重载存档只保存warmup等，sentSpike/sentSnap未存，重载可重播预告；读取<-21的warmup不会补一次伤害。基类普通fang的totem分支忽略hurt结果却加火，Master路径不走该分支；不能用父类注释代替实际虚调用。',
    'Boss免疫文字/微光/嗡声应在服务端明确拒控后发，不能直接复用攻击的spawn/snap事件。受控目标、成功追加击退、普通播放声须分开；新发回执需按目标身份与实际拒绝节流，不能因动画事件已发而判已显示拒绝。',
    'Master/Fangs/FangSpell全文、真实focus和原生finish/MagicResults、Wand图案与createMasterFang完整方法、最终盟友谓词、renderer全文已读。平台EntityEvent包实现/原版声音路由未审；SEHelper的EntityFinder/能力内部作为已调用外部支持未全审，不声称跨维度盟友行为。renderer调用模型setupAnim未展开骨骼，不能证明身体动作/深度/实际PNG。无游戏、资产或正式修改。',
    'native_preimpact_sound_and_final_refusal_success_control_settlement')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch116-goety-native-master-base-fang-prehit-cue-and-settlement','credited_chains':[k],'rationale':'One actual final victim admission/success-only control settlement separated from earlier snap entity event; base/master, pattern wrappers, sound events and renderer are one family, not separate credits.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
