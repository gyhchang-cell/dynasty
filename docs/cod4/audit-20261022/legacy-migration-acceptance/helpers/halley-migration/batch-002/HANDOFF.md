Kepler：Halley 新批002含10条全文研究建议，helper credit0。不是30条新增已接受实现，也不是10小时完成声明；本轮从2026-10-28T10:10:21Z持续，最低时段目标到20:10:21Z，后续仍推进新批。

来源先于审查直接通知你保留：henkelmax/corpse 84b47598b553b0ac9afe229b65bbd48589ca01c3，CyclopsMC/EvilCraft 28c380da541df8cef15a3d51ebfcf1ffb2a2e85a。官方依赖支持：henkelmax/corelib dd94c9ab79485cfb25083694c1ac5cedaf126af9（与Corpse声明1.20.1-1.1.3 tag精确相符）；CyclopsMC/CyclopsCore d0d435178700bcdcc674e9738a237d2c3cbdf0cd（声明1.20.0的同版本tag，build750二进制对应未独立证明）。后两仓库通用库方法仅支持实际玩法链，不能另计。

batch-002.json / reviewed-suggestions.jsonl 含兼容主账字段和用户指定别名。verification.json检查209个完整AST节点、44个证据文件：commit→tree→blob、本地文件SHA256、完整方法摘录SHA256与AST规范化指纹一致；0解析/哈希错误。1206下载文件与7426未审索引节点均不作信用。主方法对当前主账候选ID/摘录/规范化指纹命中0，只是机械排重，不能替代语义判断。

10个建议家族：尸体旧格式恢复；独立死亡历史文件恢复；狼人村民选择性双向转换；ExaltedCrafter旧index/Slot；扫帚部件属性重建与实体持久化；环境收集器延迟配方任务；群系萃取注册表Holder到区块保存；天气瓶枚举兜底；纠缠圣杯世界共享内容；灵魂盒选择性捕获保存释放。历史/尸体、魂容器/旧horn、共享内容/其他UUID库有明确重复家族风险，允许合并降级。

需要特别保留的限制：外层Death新格式优先，但内部UUID旧Most/Least优先；扫帚Count强制1与缓存未显式失效；环境机器产出与清槽跨tick且待解析recipeId不在writer中保存；天气瓶头注释仍说damage但实际reader只看string，不存在已证实ordinal迁移；圣杯cache只按amount判断更新；魂盒release不检查addFreshEntity成功，不能当一次消费事务。

仅写Halley两个专属helper目录；无主账/生产/待办修改，无游戏/服务器，无上游代码执行。新批会另开003保持这份可复核。
