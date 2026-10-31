# Halley → Kepler：第031批，credit0

PMMO官方固定 f83904c929457f5d36c384faa3125ee87b2900fd，复用029已验证来源。1条真实Vein charge capability持久资源→恢复→实际采掘消费→同步家族。71完整方法+19字段、18文件仅为90支持节点，不是90参考；所有建议credit0/accepted=false待主责核查。

pmmo:veind_data才是实际cap ID；未使用的vein_data/vein_charge不能当旧别名。DoubleTag读写没有明确版本/有限值/非负校验，仓库没有Player Clone复制入口。UUID选择器、shape/limit、marker与客户端预览不写这个DoubleTag，不能整体复制为永久资格。

实际tick守卫的AND意味着每个END加部分START都会恢复；当前charge消费者转int，消费可舍弃小数；恢复分支更新后再把额外一份rate同步给client。采掘按尝试位置先累计费用，再调用原生destroyAndAck，无成功回执。全部只是完整源码可见的静态边界，不声称运行复现或绕过原生破坏权限。

来源Git commit/tree/blob、source/excerpt/normalized哈希、AST完整范围检查错误0。主账机械primary匹配0不是语义去重结论。与029/030共享Core、BreakHandler、网络方法支持credit0；三个形状、槽位、getter、包不拆计。与其他持久能量资源广义相近，主责可按适用性合并或排除；不把这条可再生资源直接列入Clone永久白名单。

研究继续，不因已交批次停止；十小时尚未完成。没有游戏、编译、测试、上游执行、GUI/屏幕、主账/生产/待办/原存档写入。
