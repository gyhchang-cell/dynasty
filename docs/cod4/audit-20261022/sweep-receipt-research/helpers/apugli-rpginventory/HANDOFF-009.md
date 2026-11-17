# 第九批：前次伤害窗口与再生载荷

交Carson：2条完整待审候选，全部credit=0；另1组SlotInCharge支持明确排除，不提前增加主计数、不声称缺口闭合。延续已授权的固定匠魂来源，不扩展新仓库或外部下载。

- `batch-009.json`：完整范围/原文/文件SHA256/固定commit/来源URL、逐项观察、借鉴、限制与语义比较。
- `excluded-009.json`：装备槽聚合/选主支持不另计。
- `source-index-009.json`：10个匠魂源码文件与固定提交树Git blob核验，另附本机版本化Forge源Jar支持的方法范围与Jar哈希，无伪造原版Git提交/URL。
- `validation-009.json`：30段完整方法、4段配置声明，共34个唯一证据范围；校验errors=[]。这些不是34处独立实现，不是编译/测试/运行验收。

候选1：`recurrent-prior-hit-window-single-elected-armor-consumer`。实际recurrentProtection在MODIFY_HURT中由一个inCharge槽消费实体上前一次受击留下的momentum等级，再用减后的伤害生成短时后续窗口。SlotInCharge按槽差值聚合、防重复装备贡献，其他槽getLevel为0；装备变化先旧unequip再新equip。区别于第八批当前传送成功后取消伤害，本项是前次伤害形成的状态供后次伤害使用。特别限制：本次尚未最终扣血便可刷新未来窗口，后续取消不回滚；效果不是一次消费，原版强弱hiddenEffect还可能恢复，不能当last-write-wins。破损toolValid可能不触发清槽，未承诺所有失效都清理。

候选2：`incoming-damage-snapshot-to-nonadditive-regeneration-duration`。真实restore显式覆盖MODIFY_HURT，rebuff默认MODIFY_DAMAGE，两种配置合并为同一链。把当时amount转成REGENERATION duration，随后原版effect tick按剩余时钟触发heal；addEffect同等级优先较长效果而不叠加，治疗还能被Forge事件取消。尤其实现计算effectLevel但只调用二参构造，实际amplifier=0：不能把duration计算中的倍率当作实际治疗等级或声称预算全部兑现。区别前项未来减伤窗口，本项输出为延后逐tick治疗且合并可能丢失逐次预算。未修生产、未运行验证。

已完整补读原版addEffect、tickEffects、heal、MobEffectInstance.update/tick/递减/二参构造以及MobEffect再生调度/执行；仅作为具体模组链的父层支持，均零额外计数。已只读对比主accepted/reviewed与本岗001-008主方法/语义；同一链两种hook、多个槽、注册、dispatcher与客户端镜像不拆计。

本轮未启动游戏/服务器/GUI、未编译/测试、未改QA/正式/主待办/主账。run12由主协调处理，本研究不等待其结束。来源固定 `SlimeKnights/TinkersConstruct@f4e77d43f39ba1047bf93ae816b7e1beaab514c2`；无外部请求或循环重试。第八批3条已成功发Carson，此第九批2条仍由Carson决定是否符合相关性和语义独立门槛。

后续断点：本轮两条线已形成候选，SlotInCharge不能再单独包装；继续固定源时必须先挑新的状态持有者/消费生命周期，尚未读的新文件或方法一律0。Apugli包装与rpginventory既有404不新增信用；没有实际补足20，不声称完成十小时或全部任务。
