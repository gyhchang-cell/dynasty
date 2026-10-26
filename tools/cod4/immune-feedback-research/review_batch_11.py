from ledger import record,verify,B
r='GenuineSounds/Battle-Text';p='src/main/java/ninja/genuine/battle/';root=B/'sources'/r.replace('/','__')
files=['BattleText.java','system/System.java','text/Text.java','render/Renderer.java']
record('battletext-native-events-caption-reroute-and-worldtime-lifecycle',r,[(p+x,1,len((root/(p+x)).read_text().splitlines())) for x in files],
 '固定提交四Java全文已读：FML init注册System到FML/Forge总线→LivingHurt/LivingHeal正数事件→本玩家且ClosedCaption已加载则IMC DirectMessage重定向并return；否则synchronized textList生成Text→RenderWorldLastEvent调用System.tick按world.totalWorldTime每个观测时间值只更新一次→到期回收、距离排序、immutable快照→Renderer相机朝向+font五次绘制。伤害/治疗/颜色/字幕路由全合并1条，ClosedCaption库内部0计数。',
 '文字从事件amount生成而非客户端血差；LivingHurt所处阶段不能当最终护甲后实损。正数门排除零伤，链没有明确免疫原因。单玩家字幕重定向避免本分支同时显示浮字，其他实体仍世界字。Text保存出生世界坐标无实体持续关联；Renderer在Y额外+2并24格剔除，深度测试关闭，按距离远先画，alpha最低5；40次onUpdate生命周期但只在world render观察worldTime变化时递减一次，跨过多个tick不补步，没有自有维度epoch/换世界清空/总量上限/逐目标节流。整数截断使0<amount<1会显示0；配置sideVariance字段未参与已读move，不能凭配置注释称已有侧移开关效果。wither灰色0x505050仅伤害类型配色，不是Boss灰色“免疫”字。',
 '战斗文字可以因自我视角/字幕集成选择单一路由，但路由兼容不能冒充网络权威免控。实际GL状态、低帧率生命周期、总量和小数显示要看执行方法，不能由特性说明推断。',
 '源码年代为cpw FML API；虽有注册及完整实现，未编译/启动确认本项目兼容或专服加载安全。事件方法未自检side，亦未见自有S2C结果包，不能当作已验多人服务端权威链。ClosedCaption是否消费该IMC止于外部契约，主浮字分支不依赖它。','floating_combat_text')
verify()
