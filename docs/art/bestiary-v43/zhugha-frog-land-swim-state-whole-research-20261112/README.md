# 赤目朱蛤：陆地/游泳动作分流与复位

现有RedToad停止普通导航，技能控制跳跃/舌头；有真实落地/入水触发、6tick拉扯与重击喷毒门槛。旧WarpedToad整体研究处理舌头与跳跃，此批只补水陆动画选择/复位机制，不能把同一朱蛤当新物种。

实际TemplateMob.travel对TOAD活体水中走SELF移动并乘0.8阻尼；visualAnimation当前仅death/hurt/技能/水平速度选择walk/run/idle，没有独立游泳选择。实际图集中8条动画没有swim或water-idle；这是读源发现的待补覆盖，不是宣称实机故障。

后续只能在合格研究门槛后让现有骨架响应水/陆状态、保留技能优先与落地伤害。现有tongue_reach缩放包装不可被全身复位误清；不新增水上攻击、不换AI。

没有完整阅读ShootTongue、LongJumpToRandomPos、Brain执行器或AmphibiousNodeEvaluator；本闭环只对水态感知→AI活动选择、客户端水态→模型→关键帧/复位成立。

无死亡翻腹/脓包塌陷参考覆盖；没有查看新PNG、逐面UV或游戏。

本批1项完整机制候选，独立已验适用0；累计与真实缺口未建立，不能拿候选或文件数代替。旧适用记录保留，不清零。没有正式资源改动。
