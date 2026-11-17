import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
prior=(b.parent/'batch-032/review.py').read_text();header=prior[:prior.index('def pick(')].replace('batch-032','batch-034');footer=prior[prior.index('def generate():'):].replace('batch-032','batch-034')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
def whole(path):return [(path,r['name'],r['start']) for r in INDEX if r['path'].endswith(path)]
add('roots-legacy-staff-spell-format-to-current-modifiers-and-uuid-permanent-library-whitelist',
 pick('/spell/info/storage/StaffSpellStorage.java','deserializeNBT')+whole('/spell/info/storage/StaffSpellStorage.java')+
 pick('/spell/info/storage/AbstractSpellStorage.java','AbstractSpellStorage fromStack saveToStack getSelectedSlot setSelectedSlot')+
 whole('/spell/info/StaffSpellInfo.java')+whole('/spell/info/LibrarySpellInfo.java')+whole('/spell/info/AbstractSpellInfo.java')+whole('/spell/info/AbstractSpellModifiers.java')+
 whole('/world/data/SpellLibraryData.java')+whole('/world/data/SpellLibraryRegistry.java')+whole('/world/data/UUIDRegistry.java')+
 pick('/modifiers/instance/base/BaseModifierInstance.java','BaseModifierInstance getModifier isApplied setApplied isDisabled getCore serializeNBT deserializeNBT getRegistryName')+
 whole('/modifiers/instance/base/BaseModifierInstanceList.java')+
 whole('/modifiers/instance/library/LibraryModifierInstanceList.java')+pick('/modifiers/instance/library/LibraryModifierInstance.java','LibraryModifierInstance fromNBT fromStaff toStaff')+
 whole('/modifiers/instance/staff/StaffModifierInstance.java')+whole('/modifiers/instance/staff/StaffModifierInstanceList.java')+
 pick('/spell/SpellRegistry.java','getSpell')+pick('/modifiers/ModifierRegistry.java','get')+
 whole('/util/SpellUtil.java')+whole('/util/PlayerSyncUtil.java')+
 pick('/GuiHandler.java','getStaff getServerGuiElement')+whole('/container/ContainerLibrary.java')+whole('/container/slots/SlotLibraryInfo.java')+whole('/container/slots/SlotLibraryModifierInfo.java')+
 pick('/tileentity/TileEntityImbuer.java','writeToNBT readFromNBT checkExists activate update')+
 pick('/tileentity/TileEntityImposer.java','updateInSlot getSpellStorage getModifier addModifier activate')+
 pick('/container/ContainerImposer.java','getPlayer transferStackInSlot')+pick('/container/slots/SlotImposerModifierInfo.java','putStack')+
 pick('/item/ItemStaff.java','onItemRightClick onUsingTick onPlayerStoppedUsing onUpdate')+
 pick('/spell/SpellBase.java','costsMet enactCosts enactTickCosts cast')+pick('/spell/SpellAugment.java','SpellAugment cast')+
 pick('/EventManager.java','onEntityTick onEndLightDrifter'),
 '真实ItemStaff.fromStack读旧spell_holder/旧spell_0…4升级；旧独立法术解析成当前Spell+解锁modifier；实际施法消费这些配置，打开法术库/Imposer把已获得资格按玩家UUID合并进世界SpellData。该连接链合1，不把旧键、7别名、writer、世界库支持再拆参考。',
 'ItemStack根spell_storage优先，其次spell_holder；当前spells compound数字slot→StaffSpellInfo(s registry ID,m modifier compound,c cooldown,l stopTime)、selectedSlot。旧spell_0存在时读0…4字符串→slot1…5。世界维度0 SpellData-UUID保存spells列表LibrarySpellInfo(s,m,o obtained)+uuid。Root实体light_drifter计时/位置/维度/模式另存临时运行效果。',
 'AbstractSpellStorage.fromStack对现键先读，旧spell_holder分支反序列化后remove旧键并saveToStack，当前和旧同时存在时只选当前且不删旧。StaffSpellStorage当前spells优先于旧spell_0；旧仅spell_0作为入口，缺0但有1…4不会迁移。旧resolveSpell对7已删除独立法术选新Spell，必要时给指定modifier.setApplied/setEnabled，其他直接当前registry名查找；不属于每个别名的独立算法。AbstractSpellInfo支持带namespace及bare名字，bare归Roots命名空间；这不等于任意namespace重定向。未知spell返回null，Staff当前writer以空compound写null槽、世界library reader忽略未知spell，下次保存无原始未知payload旁存。',
 '当前Staff解析Integer.parseInt任意key，只对key总数>5日志，没限制读取slot范围/selectedSlot，也不clear既有map；getSpells仅枚举1…5但serialize写所有map entry，因此越界槽可留在NBT却不参与实际循环。缺m.s或错误ResourceLocation/Modifier registry等路径无局部逐条异常隔离；BaseModifierList先按当前Spell生成defaults，再加载并以core替换，未知modifier用AIR core后写出时被过滤，末尾mismatch只日志且other可能null。旧格式save会覆盖spell_storage，而旧别名载荷的未知字段没有隔离保存；原物品其他根键、Count/tag未被重建整栈，不保证未知内层字段无损。',
 'Dynasty可借鉴显式旧结构优先级/合法枚举边界/旧资格到新可用入口的语义转换，既要保留Count/tag和未知ID，也要在新对象解析与可用性确认前保留原载荷，不把null解析当空档成功。永久Clone白名单只合并审定历史任务/功名等资格；本例world库updateSpell逐项只提升obtained与applied，不复制cooldown、cooldownStop、selectedSlot、当前enabled或light_drifer实体效果。历史healing_talisman→vajra既定行为不得由此恢复回血。把世界UUID真值与客户端/物品运行配置分开核实，必要时保持可逆旧载荷隔离以防重试重复授予。',
 'SpellLibraryData.generateMap从当前registry设默认未获得，read先重建再按列表覆盖，重复Spell后项覆盖前项；uuid从NBT覆盖构造名UUID却无一致性校验。UUIDRegistry用维度0 lookup缺失新建、clear显式new/dirty/saveAllData；没有Player Clone入口，世界存储同UUID可跨玩家实例查询只是源码结构，不是死亡/末地实际验收。Imbuer持久inserter/progress/完整库存，完成时给该UUID库addSpell，再在线查player发消息未判null；离线授予可能先成功后消息异常而未消费dust，未运行不能称已复现。Imposer与SpellUtil将item资格合并world库，再把world已applied资格补回法杖；未获得条目缺少额外server通用签名验证的安全效果未验。ContainerLibrary有true canInteractWith/可变hand supplier、未展开原生网络槽位校验，不保证客户端任意值可信。独立文件版权文字保留，只借鉴语义不复制。',
 '旧Staff格式、具体removed-spell转换、UUID法术库持久读写、Imbuer学习/Imposer解锁、GUI装填、实际施法与临时LightDrifter清理是同一连接家族合1。LightDrifter实际cast设置disableDamage/allowFlying/noClip与root计时，并切旁观；EventManager递减到期恢复gameType/清root字段，此暂态不是永久库，不能整体copyForgeData。物品冷却本身有意NBT持久不等于永久玩家资格；StaffInfo.tick/validate双机制未运行验证时钟重置语义。032包UUID世界库存不同对象但共享维度0样式，shared支持不算；其它批次spell永久知识有广义相似，Kepler最终按完整对象语义去重。映射表/音效ignore/runic别名关键词另只记排除不单独信用。credit0。')

def attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    out=[]
    for suffix,needles in [('/spell/info/storage/StaffSpellStorage.java',None),('/spell/info/StaffSpellInfo.java',None),('/spell/info/LibrarySpellInfo.java',None),('/world/data/SpellLibraryData.java',None),('/modifiers/instance/base/BaseModifierInstance.java',None),('/modifiers/instance/staff/StaffModifierInstance.java',None),('/spell/SpellAugment.java',['LIGHT_DRIFTER','spellName','instance'])]:
        sample=next(r for r in INDEX if r['path'].endswith(suffix));raw=(ROOT/sample['source']).read_bytes()
        for n in walk(PARSER.parse(raw).root_node):
            if n.type!='field_declaration':continue
            fragment=raw[n.start_byte:n.end_byte].decode()
            if needles and not any(v in fragment for v in needles):continue
            e=dict(sample,node_type=n.type,name=fragment.split('=')[0].split()[-1],start=n.start_point.row+1,end=n.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(n,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(n.start_byte)).encode())[:20]);e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);out.append(e)
    row['source_declarations']=out
'''
(b/'review.py').write_text(header+notes+footer)
