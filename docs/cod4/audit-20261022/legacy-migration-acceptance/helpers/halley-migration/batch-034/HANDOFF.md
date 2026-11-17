# Halley → Kepler：第034批，credit0

复用Roots官方27dc32ecf4dfffbc67790bc69ed0b405137dee2f（032来源）。1条旧Staff格式/已移除独立法术转换→实际配置施法→UUID永久法术库合并资格完整连接家族。258完整方法+25字段、31文件仅283支持节点，不是283信用；所有候选credit0/accepted=false。

真实读取旧spell_holder；内部旧spell_0存在时读0…4映到当前slot1…5。7个旧独立法术转新法术和已applied/enabled修饰器，全部不拆计。现spell_storage/spells优先，未知spell可能变null/空compound，旧字段无原样隔离；slot读取仅日志总数没有逐key范围校验。所有具体边界有完整方法和hash。

永久库在维度0 SpellData-玩家UUID。通过Imbuer学习和Imposer/SpellUtil合并，只提升obtained与applied；回到法杖的新配置不复制cooldown、stopTime、slot、当前enabled。没有Player Clone回调，不能宣称死亡/末地验收通过。派生actual LightDrifter cast会临时disableDamage/旁观/root计时与位置维度，EventManager到期清理；不能因旧法术解锁而把这些临时字段加入永久Clone。

库加载未知spell丢弃、重复后项覆前项、内存UUID可被NBT覆盖但不校验存储名；Imbuer离线UUID先加资格再查在线player消息可能null，未运行复现。源码各个Container文件有独立版权声明，保留供研究，不抄实现。MappingEvent纯表/变体及音效ignore另记不计，不以别名数量加数。

固定Git/tree/blob、source/excerpt/normalized哈希及完整AST范围错误0。主账primary机械匹配0仍需语义去重。032为包库存对象，此处为旧法术及永久资格；共有UUID架构/GUI支持不多计。所有原生/三方保存网络时序只声明静态范围，不作游戏验证结论。

继续033 NaturesAura实际持久对象研究；十小时尚未完成。没有游戏、编译、测试、GUI/屏幕，未写主账生产待办或用户原档。
