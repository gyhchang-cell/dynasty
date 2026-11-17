"""One durable player skill profile, not one credit per skill/trait/support."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-027/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-027','batch-028');footer=prior[prior.index('def generate():'):].replace('batch-027','batch-028')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('reskillable-playerpersisted-skill-profile-key-encoding-rehydration-and-real-unlock-gates',
 pick('/api/data/PlayerDataHandler.java','getDataCompoundForPlayer')+whole('/api/data/PlayerDataHandler.java')+
 whole('/api/data/PlayerData.java')+whole('/api/data/PlayerSkillInfo.java')+whole('/api/skill/Skill.java')+whole('/api/unlockable/Unlockable.java')+
 whole('/network/MessageLevelUp.java')+whole('/network/MessageUnlockUnlockable.java')+whole('/network/MessageDataSync.java')+whole('/network/PacketHandler.java')+
 pick('/ReskillableModAccess.java','syncPlayerData')+pick('/api/ReskillableAPI.java','syncPlayerData getRequirementRegistry')+
 pick('/base/CommonProxy.java','preInit postInit getClientPlayer')+
 whole('/base/LevelLockHandler.java')+whole('/api/data/RequirementHolder.java')+whole('/api/requirement/SkillRequirement.java')+whole('/api/requirement/RequirementRegistry.java')+
 whole('/skill/defense/TraitUndershirt.java')+whole('/skill/agility/TraitHillWalker.java')+whole('/api/unlockable/Trait.java')+
 whole('/base/ExperienceHelper.java')+whole('/ReskillableRegistryHandler.java'),
 '官方技能玩法：登录/每玩家tick获取PlayerData，首次从PlayerPersisted/SkillableData载入；服务器升级/解锁后saveAndSync，重读数据由装备/方块/攻击等级锁和真实特性事件消费。不是声明Clone成功，也不按8技能/17trait分计。',
 'player.entityData[EntityPlayer.PERSISTED_NBT_TAG][SkillableData].SkillLevels[skill.getKey()]={level:int,skillPoints:int,unlockables:compound keyed by unlockable.getKey→boolean}。PlayerData运行cache按int hash和WeakReference区分实例；客户端网络NBT同步同格式。',
 'getDataCompoundForPlayer仅缺键时建compound，保留历史样式SkillableData键名；未见把别的旧namespace数据映射到reskillable技能名的代码，不能把沿用名字或dot→colon编码声称旧版本迁移保证。Skill/Unlockable构造name把ResourceLocation冒号改点，writer用getKey；unlockables读时全部点替冒号再registry查询，是现行反编码。未知registry返回null忽略、非法ResourceLocation无逐项catch；只按键存在收集，不读取布尔true/false，因此false键也作为解锁。保存用全新SkillLevels和unlockables compound，未知技能/trait不旁存，将在对应重写时丢出活动格式。',
 'PlayerData构造为每注册Skill建默认level1并respec，load仅对存在的skill键加载，缺整组保留构造或旧内存值，不主动清未出现技能；PlayerSkillInfo加载整数直接赋值、clear解锁后重建，不调用onUnlock。getLevel消费时将<=0校正1、>cap校正cap，但getRank/isCapped/saveToNBT可直接用原值，skillPoints无对应clamp。getKey表达式实际是hashCode << (1+sideOffset)，不是UUID或保证唯一ID；同key缓存WR不是本player就save旧数据→remove→递归get新对象并load→用旧快照load覆盖。cleanup仅每END移除weakref已空项目，未见全会话清理/显式Clone事件，原生PlayerPersisted重生如何复制未在本源验证。',
 'Dynasty可借鉴将审定永久字段放进明确子compound，记录schema和合法旧键别名，而不复制全ForgeData或仅靠同名容器宣称兼容。任务册未知Count/tag/注册项应保留原载荷，避免重写注册表已知集合时静默抹掉；技能未知项的这里策略只能作限制案例。死亡永久进度先定义白名单，再明确缺键重读的默认/清理策略；TraitUndershirtCD位于根entityData而永久unlock位于PlayerPersisted，恢复时不能连临时防致死CD一起带过。缓存key应真实玩家UUID/side/生命周期分开，勿把哈希冲突重绑当Clone方案。',
 '真实服务器MessageLevelUp用ctx玩家、registry技能、等级/XP/cancel event，再扣XP/levelUp/saveAndSync；unlock包校验未解锁/点数/requirements和可取消事件，但未显式验证传入skill是unlockable.parentSkill，未知skill/trait缺少完整null隔离。LevelLockHandler在可取消实际右击/攻击/破坏/装备事件通过SkillRequirement.getLevel判断；Undershirt对已解锁特性分派hurt(血>=6且致死且可阻挡时改health-1并设200CD)与tick减CD，永久解锁和临时状态可明确区分。原生事件、PlayerPersisted Clone、Forge registry缺失行为、客户端UI/原生网络未运行；没有宣称获得进度必跨死亡保留或恶意包已复现。ExperienceHelper注释来自OpenModsLib，仅支持消耗路径，无额外外部研究credit。',
 '完整PlayerPersisted技能档对象一族：cache换实例、skillPoints/level/unlockables、8技能、多trait、注册、同步/消费全部支持，不按键/循环条目计数。Skillable母项目和后续不同版本/移植不另计；官网Source旧Lanse505/Skillable-2链接实际重定向本仓，官方延续不是另一个独立信用。与003PassiveSkillTree/ScalingHealth、011Astral玩家资料等同属永久进度但具体数据真值/缓存/编码/消费者不同，最终由Kepler合并拒绝；helper credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix in ['/api/data/PlayerDataHandler.java','/api/data/PlayerData.java','/api/data/PlayerSkillInfo.java','/skill/defense/TraitUndershirt.java']:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode();e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
