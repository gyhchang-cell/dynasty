# 同一动画重复选择：4.8.4源码核对

当前 SecondaryMob 每帧构造同名 `thenLoop` 链，在没有 forceAnimationReset 时不会因 builder 是新对象而重启。setAnimation 对相等链跳过队列与 tick 重置。

这是选定调用路径的静态结论，不是完整过渡混合、存档读回或实机验收。原模型、动作、PNG、物件均未修改；新增生物参考信用为0，适用整项累计和缺口仍未核定。

源码观察、范围与SHA见 receipt.json；延续骗子状态链收据。
