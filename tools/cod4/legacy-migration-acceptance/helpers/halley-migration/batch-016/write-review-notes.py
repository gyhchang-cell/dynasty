"""Render three manually inspected persistence families; only helper documents are written."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
old=(b.parent/'batch-013/review.py').read_text();header=old[:old.index("add('akashictome")].replace('batch-013','batch-016');footer=old[old.index('def generate():'):].replace('batch-013','batch-016')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
add('forestry-uuid-world-research-progress-and-consumable-note-restoration',
 pick('genetics/BreedingTracker.java','BreedingTracker readFromNBT writeToNBT readValuesFromNBT writeValuesToNBT encodeToNBT decodeFromNBT synchToPlayer syncToPlayer setModeName setUsername setWorld getMutationString registerMutation isDiscovered registerBirth registerSpecies researchMutation isResearched')+
 pick('apiculture/genetics/ApiaristTracker.java','ApiaristTracker readFromNBT writeToNBT getBreedingTracker speciesRootUID')+
 pick('apiculture/genetics/BeeRoot.java','getBreedingTracker')+
 pick('core/EventHandlerCore.java','handlePlayerLoggedIn handlePlayerChangedDimension syncBreedingTrackers')+
 pick('genetics/ItemResearchNote.java','ResearchNote writeToNBT getEncodedMutation registerResults createMutationNote createMutationNoteStack createSpeciesNote createSpeciesNoteStack onItemRightClick')+
 pick('utils/PlayerUtil.java','writeGameProfile readGameProfileFromNBT')+
 pick('packets/PacketGenomeTrackerSync.java','onPacketData')+
 pick('genetics/SpeciesRoot.java','getCombinations')+
 pick('alleles/AlleleRegistry.java','getAllele'),
 '实际研究笔记右键在服务端解码并登记育种研究，成功才减物品；BeeRoot通过WorldSavedData按玩家UUID取回长期研究。登录与换维度重新取相同研究对象并同步，而不是复制旧玩家实体或其全部NBT。',
 'ApiaristTracker.<UUID>或common的世界持久对象：SpeciesCount/SDn、MutationsCount/MDn、ResearchedCount/RDn字符串集合，BMS模式名及蜂后/公主/雄蜂计数。笔记TYP byte、INN compound中的ROT/AL0/AL1/可选RST，res为研究者GameProfile装饰信息。',
 'readValues只按有count的前缀项读取非空字符串加入Set，不clear，重复读取是增量并集；writer写当前集合与计数。researchMutation先判未研究、加集合并markDirty，再registerMutation并同步；isDiscovered对已发现或已研究均为真。笔记通过root+双parent alleles查实际mutation，未知root/parent/组合返回false不消费；已研究同样不消费；缺RST或RST无法解析时result=null，匹配第一个可用组合。存储按UUID隔离，显示/在线增量同步却用username.name查玩家。',
 '永久真值在world saved data，不随一次玩家实体Clone消失；这只证明本mod明确重取的登录/换维度入口，未见或不推断死亡同步触发。mutation字符串为parent0-parent1=result，父顺序/UID若变化不会自动迁移历史key。reader不查每条species/mutation仍注册，保留未知历史字符串但当前contains查询未必识别。registerSpecies本身未直接markDirty，在线syncToPlayer调用setModeName时可间接dirty；离线/无username路径不能保证这次新增持久化。',
 'Dynasty永久任务历史可按稳定玩家UUID独立保存或在Clone只迁经审定字段，并由新实例重建显示/权限；绝不为保进度复制免疫、反击、姿态、计时器或整份ForgeData。研究笔记式旧物品恢复先解析并确认最终登记成功才消费源栈，未知任务/依赖缺失应留原载荷。历史别名应同时考虑数据key与组合键，不只替换物品注册名。',
 '笔记EnumNoteType.VALUES直接索引TYP无范围校验，坏byte可能异常；SPECIES笔记有writer/tooltip但registerResults只处理MUTATION，不能说物种笔记能成功消费。研究者res不作为使用者ACL。onItemRightClick从handIn取笔记，但成功时减inventory.currentItem主手槽，未按handIn，副手路径只做静态风险提示。World.loadData/setData原生刷盘、GameProfile底层解析和网络调度未全部深审，不宣称可靠事务；Set无count上限，writer复用compound不清旧多余前缀项。',
 '物品笔记解析/一次消费、UUID长期tracker、各集合、登录同步与计数都为一研究进度家族，不按物种/计数key/蜂树蝶wrapper多计。与其他UUID研究存储相似但对象/控制流实际不同，Kepler最终判定；credit0。')

add('forestry-genetic-bee-item-chromosome-validation-to-real-production',
 pick('genetics/Genome.java','Genome getChromosomes writeToNBT getActiveAllele getInactiveAllele checkChromosomes')+
 pick('genetics/Chromosome.java','create validateAllele Chromosome writeToNBT getPrimaryAllele getSecondaryAllele getActiveAllele getInactiveAllele')+
 pick('alleles/AlleleRegistry.java','getAllele registerDeprecatedAlleleReplacement')+
 pick('genetics/SpeciesRoot.java','getTemplate')+
 pick('apiculture/genetics/BeeGenome.java','BeeGenome fromNBT load getSpeciesRoot getPrimary getSecondary getSpeed getFlowerProvider')+
 pick('apiculture/genetics/BeeRoot.java','getMember getMemberStack isMember getType getDefaultTemplate getKaryotype')+
 pick('apiculture/genetics/Bee.java','Bee writeToNBT getGenome getMate mate produceStacks')+
 pick('genetics/Individual.java','Individual writeToNBT analyze')+
 pick('genetics/IndividualLiving.java','IndividualLiving writeToNBT isAlive getHealth getMaxHealth setHealth age decreaseHealth')+
 pick('apiculture/BeekeepingLogic.java','readFromNBT writeToNBT doWork queenWorkTick doProduction canWork addPendingProducts'),
 '真实蜂物品由BeeRoot读取tag，基因从Genome/Chromosomes恢复；蜂箱重载queenStack后重新构建Bee，实际工作周期produceStacks用恢复的物种/速度/花源决定产品，再将年龄和基因写回queen物品。非纯tooltip或getter候选。',
 'Bee物品Genome与Mate各含Chromosomes compound-list；每项Slot byte、UID0/UID1字符串。Individual父类IsAnalyzed、Health/MaxH，Bee可选NA/GEN；BeeGenome从NBT经容量128/访问1分钟的cache构建。',
 'getChromosomes按合法Slot范围放入数组，Chromosome.create解析双allele并检查与该染色体要求的class是否相容；坏/未知allele优先从已读取物种模板取该槽，物种模板无效则取root默认模板。物种UID只有处理物种Slot后才记录，因此列表顺序会影响后续缺值fallback。重复Slot后项覆盖；缺失整个Slot不填充，NBT构造不走checkChromosomes完整校验，后续getActiveAllele可解引用null。',
 'AlleleRegistry先查当前alleleMap再查deprecatedAlleleMap，替代注册先到先得；本固定源码全文搜索未找到实际调用registerDeprecatedAlleleReplacement填表的内部实现，因此不能按旧allele表条目或API存在宣称已有实际别名迁移。真实fallback是上述class/template校验。缺整个Genome时Bee用FOREST genome；存在空/坏Genome则走数组reader，不等价于缺键fallback。writer把解析后有效UID和已恢复字段写到新compound，未保存未知原始allele/未知额外tag，默认替换后无法凭新栈找回旧值。',
 'Dynasty旧任务册/长期标记恢复应区分缺键、空compound、未知注册、类型错和缺单项；可用明确白名单fallback但保留原始id/Count/tag与未知字段，不能以默认模板成功构造为无损恢复。先恢复稳定标识上下文，再处理依赖它的字段，避免NBT列表顺序影响迁移结果；只复制审定永久任务字段，机器样本health/年龄不是玩家Clone白名单。',
 '本批完整阅读mod codec与实际生产消费者，不深审每物种productchance、住房/模式modifier和花源affectProducts实现，不能宣称产物完全等价。缓存仅构造支持，不是独立通用cache信用；未执行Guava/上游源码或游戏。未以速查tooltip的getSpeciesDirectly当完整Genome恢复；其路径不作为本候选消费证据。旧health值由构造直接读而非setHealth裁剪，Gen写入只在>0时，复用原NBT会保留条件外旧键；实际queenWorkTick用新compound写回。',
 '所有染色体/UID双份/Genome与Mate/蜂种/health/缓存/读写和真实生产为同一遗传蜂物品恢复链一条。树/蝶同父codec wrapper不追加，alias API不额外计；与batch015能量分析机只共享普通库存载体，研究对象是遗传内容本身，仍交Kepler裁定，credit0。')

add('forestry-player-mailbox-letter-payload-restoration-and-processed-transfer',
 pick('mail/POBox.java','POBox readFromNBT writeToNBT storeLetter markDirty getPOBoxInfo setInventorySlotContents decrStackSize getStackInSlot')+
 pick('mail/Letter.java','Letter writeToNBT isMailable isPostPaid requiredPostage getPostage getAttachments invalidatePostage setProcessed isProcessed hasRecipient getRecipient countAttachments decrStackSize setInventorySlotContents')+
 pick('mail/MailAddress.java','MailAddress writeToNBT isValid equals hashCode toString getPlayerProfile getName getType')+
 pick('utils/PlayerUtil.java','isSameGameProfile writeGameProfile readGameProfileFromNBT getPlayer')+
 pick('api/mail/EnumAddressee.java','fromString toString')+
 pick('mail/PostRegistry.java','getPOBox getOrCreatePOBox getPostOffice getMailAddress getLetter isLetter createLetterStack getCarrier registerCarrier')+
 pick('mail/PostOffice.java','readFromNBT writeToNBT lodgeLetter collectPostage setWorld refreshActiveTradeStations registerTradeStation')+
 pick('mail/PostalCarrier.java','deliverLetter storeInPOBox')+
 pick('mail/tiles/TileMailbox.java','getOrCreateMailInventory tryDispatchLetter openGui')+
 pick('mail/gui/ContainerMailbox.java','ContainerMailbox slotClick')+
 pick('mail/inventory/ItemInventoryLetter.java','ItemInventoryLetter decrStackSize setInventorySlotContents onLetterClosed onLetterOpened')+
 pick('mail/LetterProperties.java','createStampedLetterStack closeLetter openLetter getState getSize encodeMeta')+
 pick('mail/SaveEventHandlerMail.java','onWorldLoad')+
 pick('mail/ModuleMail.java','setupAPI getSaveEventHandler')+
 pick('core/EventHandlerCore.java','handleWorldLoad')+
 pick('modules/InternalModuleHandler.java','registerHandlers')+
 pick('core/inventory/InventoryAdapter.java','InventoryAdapter readFromNBT writeToNBT setInventorySlotContents decrStackSize')+
 pick('core/inventory/InventoryPlain.java','InventoryPlain setInventorySlotContents decrStackSize readFromNBT writeToNBT')+
 pick('utils/InventoryUtil.java','readFromNBT writeToNBT tryAddStack'),
 '玩家真实投信→PostOffice检查邮资/processed→PostalCarrier保存收件箱；邮箱WorldSavedData重载Letters库存，玩家菜单按自己profile重取；取出/打开信后附件变更写回信物品NBT，处理标记阻止再次投递。',
 'POBox_<MailAddress.toString()>命名世界持久对象保存address与Letters列表；信物品PRC/SDR/RC/TXT/UID及INV 22槽（18附件+4邮票）；地址TP枚举字符串与profile(Name/Id)；PostOffice另存各CPS邮票统计。',
 'MailAddress无效TP或缺profile回invalidGameProfile，Letter读取即构造sender/recipient对象；POBox读取address存在则替换并加载库存，不复核文件名/玩家UUID与内嵌address一致。真实玩家投递从现有邮箱取出，复制letterStack，先PRC=true/清邮票并新compound写回，再tryAddStack，成功后上层收邮票、dirty，TileMailbox成功才shrink源1。玩家菜单从当前profile取getOrCreatePOBox，附件减少/写槽均立即letter.writeToNBT回parent。',
 '身份规则不一致：PlayerUtil.isSameGameProfile在双有效UUID时仅比UUID，否则比名字；MailAddress.equals使用此规则，但hashCode只名字，toString文件名含小写名字+UUID。因此改名同UUID可能cache哈希不同且取不同文件名，未见旧名文件查找/迁移。缓存静态且key不带世界/维度；World.Load事件清缓存，不能推断世界隔离始终安全。POBox库载荷与目录key是两个真值，读取不校验相符。',
 'Dynasty永久任务/物品目录应用稳定UUID身份，显示名字单独更新；恢复数据必须校验来源路径/内嵌owner/最终玩家一致。一次迁移消费要在目标完整写入成功后标记并扣源，保留Count/tag和未知附件载荷，防重复/丢失；不能把PRC默认false或新目录空对象当历史不存在的充分证据。',
 'PostalCarrier玩家分支忽略doDeliver参数，storeInPOBox始终写，故false模拟不应被当只读；本实际TileMailbox入口传true，未测试false调用场景。Letter.PRC缺失默认false；isMailable仅recipient非null，不验证isValid。reader Slot范围问题沿用batch015 codec但不另计。新compound写PRC时未知额外信tag不保留；copy保原Count，若非单件源无法据此保证一次投递恰好单件，未运行样本。TradeStation交易/删除分支未深入，本候选只玩家邮箱；原生NBTUtil profile和WorldSavedData磁盘事务未重读；LetterProperties界面meta只恢复外观状态，不当额外实现。',
 '地址、邮箱worlddata、信件payload、邮资与processed转移/附件写回合一玩家邮件恢复链一条，不按84槽/22附件邮票槽/枚举/地址缓存支持拆计。与其他持久目录有模式相似，Kepler语义审核；TradeStation与CPS单独对象不另凑候选，credit0。')
'''
attach='''\ndef attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    targets=[('apiculture/genetics/BeeGenome.java',['beeGenomeCache ='])] if 'genetic-bee' in row['family'] else ([('mail/PostRegistry.java',['cachedPostOffice','cachedPOBoxes','cachedTradeStations']),('mail/MailAddress.java',['invalidGameProfile ='])] if 'player-mailbox' in row['family'] else [('genetics/BreedingTracker.java',['static final String'])])
    decl=[]
    for suffix,needles in targets:
        sample=next(r for r in INDEX if r['path'].endswith('/'+suffix));raw=(ROOT/sample['source']).read_bytes()
        for node in walk(PARSER.parse(raw).root_node):
            if node.type!='field_declaration':continue
            fragment=raw[node.start_byte:node.end_byte].decode()
            if not any(t in fragment for t in needles):continue
            e=dict(sample,node_type=node.type,name=fragment.split('=')[0].split()[-1],start=node.start_point.row+1,end=node.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(node,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(node.start_byte)).encode())[:20])
            e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);decl.append(e)
    row['source_declarations']=decl
'''
footer=footer.replace('        rows.append(row)','        attach_declarations(row)\n        rows.append(row)')
(b/'review.py').write_text(header+notes+attach+footer)
print('Authored3 reviewed objects, helper credit0')
