# 生态研究接续 008

协调收据已绑定接受 **EA1/2/3/7/8/9 共6整机制/1000**，差994。共13条已读整机制，其余7条仍待审；5条未闭合候选信用0。EA4/5/6交Carson独立审阅，本岗未自授这些信用，也未重复独立审阅。原批次保留，master-acceptance-ledger.json只按完整匹配收据计1/整链，不按16/24/22等支持范围计数。

收据限制分别写入review-addenda-002.json（EA7/8）与review-addenda-003.json（EA9）。EA7 metadata字段更正过程按收据保留；收据未落盘前没有先计。EA9额外DataGenerators完整文件也重核SHA256、Git blob、固定tree/revision与全文，额外支持信用0。

本轮新增真实全文阅读并封装的两项待审来源均为 BobMowzie/MowziesMobs-Public 固定commit 7aa17309337cbd4102efc418cba12a4983b1540c：

- batch-007.json / EA-0012，34范围合1待审：自然地下洞室有界噪声列搜索，非solid层→solid地板→四向4高solid墙→方向旋转锚点→实际addPiece。实际structure_set/datagen/biome集合消费者、父生成入口一起读，区别于EA9地表cohort。非solid不等于空气；父avoidStructures未消费；settings指定SURFACE而类step返回UNDERGROUND，最终native调度未证；template marker空，template NBT未读，不能宣称铁守卫/箱子出生或现实世界场景已生成。无建筑参考信用。
- batch-008.json / EA-0013，38范围合1待审：真实seed useOn→MOB_SUMMONED幼苗→掉落肉消耗→三段饥饿平台和20tick成长→新成体持久性→discard幼苗。种子入口与成熟交接都忽略add结果，成熟无条件discard旧实体，无同UUID继承；仅位置复制，不宣称幼苗名字等全数据继承。读取growth/flag序列化和完整父checkDespawn，保留EventHooks/Peaceful先于距离分支。不是自然野外出生或种子自然获取验证。

candidates-003.json / EA-C005：已全文读LandmarkGridPlacement/AvoidLandmarkGridPlacement/LegacyLandmarkPlacements并核getOverworldSeed；未找到固定自然structure_set部署引用，维持0。格心只依坐标，variety另取全局当前server overworld seed；候选格、加权表、原生有效start不能互相替代。与EA-C003装饰避让的共享helper不得重复包装。

另完整读EntityLantern，只有浮游运动/碰撞/动画/死亡视觉，本轮排除0，见excluded-readings-001.json。物种ID、参数行与一般AI不能补数。

EA7限制：UMVUTHANA_CRANE不在SPAWN_CONFIGS；null config跳过configured分支。missing holder跳过不证明tryParse非法字符串fail-safe。EA8限制：custom predicate用未offset origin早返回；同entity在CREATURE先删后加，schema类别不能代表消费类别；requireAll/exclusion、未加载、replaceable/NBT、温度缓存边界保留。EA9限制：5–9为target并非成功加入；无seeded/bbox仅重入风险；持久性非不死；datagen/template未部署/读取，不计建筑。

下一号EA-0014。继续新语义源码与候选缺口，不等待每批验收；1000之前不改生产或cap/概率/category，不新增随机挂机。运行基线仍24/30与9/10，未回填成功。未编译/测试/启动游戏或GUI、未唤醒屏幕、未改QA/资产/共享Jar/待办，只有自有研究目录的证据文本与打包脚本写入。
