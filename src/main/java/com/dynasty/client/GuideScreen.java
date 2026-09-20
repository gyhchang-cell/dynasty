package com.dynasty.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.List;

/**
 * 王朝说明书界面：左边是分组目录（可折叠 / 点击跳页），右边是正文，像一本真正的书。
 * 五个分组：开始 · 上车 / 王朝 · 仕途 / 兵甲 · 装备 / 世界 · 探索 / 收尾。
 *
 * Dynasty manual screen: a collapsible section sidebar on the left (click to jump),
 * page body on the right — laid out like a real quest book.
 * 包含：开局流程、维度旅行、兵器与护甲进化链、建筑、科举、军队、神兽、Boss、饰品、便利操作。
 */
@SuppressWarnings("null")
public class GuideScreen extends Screen {

    private static final String[][] PAGES = {
            {"王朝图鉴 · Dynasty Codex", "§7本模组加入了一个完整的东方王朝：",
             "§7世界、建筑、科举、军队、神兽、节日与神兵。",
             "§7使用 §f← →§7 或下方按钮翻页，滚轮也可翻页。",
             "", "§8右键手中的《王朝说明书》随时打开。"},
            {"目录 · 这本手册怎么用", "§7左侧栏按 §f五个分组§7 排好了（点分组标题可以折叠 / 展开）：",
             "§6【开始 · 上车】§7 开局路线、物品怎么看、60 分钟上手",
             "§6【王朝 · 仕途】§7 科举升官、功名来源、虎符调兵、饰品与槽位",
             "§6【兵甲 · 装备】§7 兵器与甲胄进化链、数值一览、附魔与词条",
             "§6【世界 · 探索】§7 四个维度、Boss 与信物、建筑宝箱、节日、附录",
             "§7点左侧任意一行直接跳页；也可以用 §f← →§7、滚轮或下方按钮翻页。",
             "§8第一次玩：先看「开始 · 上车」的前三页，照着做就行。"},
            {"一、开局指南", "§f0.§7 打开 §dFTB 任务书§7，在「主线旅程」选择「01 · 安家与第一把兵器」。",
             "§f1.§7 先建工作台、储物箱、火把与熔炉，再做 §f木矛§7（木棍×2 + 橡木木板）。",
             "§f2.§7 按 §f木矛→石戈→铜刀→铁剑§7 一路升级（见「兵器进化链」页）。",
             "§f3.§7 玉来自地下玉矿；朱砂来自神庙/法阵/帝陵宝箱。备好材料做 §f兵器图纸§7。",
             "§f4.§7 做 §f科举试卷§7 答题升官，用 §f虎符§7 调兵。",
             "§f5.§7 造 §f天朝传送门§7 去天朝、§f地府传送门§7 去地府（见「去其他维度」页）。"},
            {"二、怎么看物品信息", "§7把鼠标悬停在物品上：",
             "§7• §f物品名下面§7会直接显示一行简介：攻击力/护甲/套装减伤。",
             "§7• 按住 §eShift§7 展开：用法、配方、攻击力、耐久、套装加成。",
             "§8不按 Shift 时只显示一行，不占屏幕。",
             "§8饰品请放进 Curios 对应分类槽，或「§d万能饰品§8」槽。"},
            {"三、去其他维度（完整教程）", "§6【第一步】§7 收集材料：",
             "§7• §f天朝传送门§7：玉石块×8 + 龙晶×1（3×3 中间放龙晶）",
             "§7• §f地府传送门§7：玉石块×8 + 朱砂×1（同上）",
             "§7• §f九霄传送门§7：玉石块×4 + 龙晶 + 凤凰羽　§f龙宫传送门§7：玉石块×4 + 龙晶 + 龙鳞×2",
             "§6【第二步】§7 把传送门放在地上，§f右键§7即可传送。",
             "§6【第三步】§7 配方产出两座门；第二座带到对面，放下后右键回主世界。",
             "§8对面不会自动生门。归乡符可回主世界出生点，出发前请备好。"},
            {"三·续、维度生存要点", "§7• 天朝·龙庭：天光大亮、宫殿牌坊成片，地表多白玉与玉石。",
             "§7• 地府：没有顶棚、没有岩浆海，抬头是暗色星空；刷烈焰人/恶魂/僵尸猪灵。",
             "§7• 四个维度都有玉矿与龙晶矿，龙晶是好装备的关键。",
             "§7• §f回城符§7（return_talisman）可以随时回主世界。",
             "§8/Locate structure dynasty:palace 可以定位皇家宫殿。"},
            {"四、天朝·龙庭", "§7真实的噪声地形与 4 个自定义群系：",
             "§a天朝平原§7 / §a玉林§7 / §a龙脊山脉§7 / §a碧海云海§7",
             "§7地表以汉白玉为基岩，玉石与龙晶藏于地下。",
             "§7空气中弥漫着龙气：怪物在白天也会出现。",
             "§8宫殿、宝塔、长城与牌坊都会在这里生成。"},
            {"五、地府", "§7黑石与岩浆的世界，天顶封闭、永无天日。",
             "§5幽冥荒原§7 与 §5忘川河畔§7 两大群系。",
             "§7敌对生物：兵马俑、刺客、叛军、九尾狐。",
             "§7深处仍可寻得玉矿与龙晶矿。",
             "§8小心：脚下就是岩浆海，记得带方块。"},
            {"六、兵器进化链（总攻击力）", "§f木矛5 → 石戈9 → 铜刀14 → 铁剑20§7（基础期）",
             "§6青铜剑34 → 唐刀46 → 环首刀62 → 长枪82",
             "§6→ 玉笛105 → 官银剑132 → 玉剑170 → 巨阙重剑500",
             "§c破军战斧650★ → 龙晶剑1400★ → 方天画戟1900★★",
             "§c→ 玄天钺2500★★ → 天子剑3200★★★",
             "§8★ = 需要 Boss 掉落信物（见「Boss 与信物」页）。"},
            {"六·续、弓系（两条支线）", "§f猎弓§7：箭矢 ×1.5 + 4（开局，木棍 + 线即可）",
             "§f长弓§7：箭矢 ×2 + 20 —— 弓系在这里分叉，往下走两条支线：",
             "§b速射流§7：§f神臂弓§7(×2.8+70) → §f落雁弓§7(×3.3+120) → §f天狼弓§7(×3.8+200 穿透1)",
             "§c穿透流§7：§f龙吟弓§7(×3.5+200 穿透3，需凤凰羽+龙鳞) → §f射日弓§7(×4.5+280)",
             "§7奇兵：§f鱼肠剑§7(刺客掉) §f青釭剑§7(宦官掉) §f倚天剑§7(叛将掉) §f龙胆亮银枪§7(始皇掉)",
             "§6御赐：官阶到尚书得§f御赐金锏§7，到丞相得§f尚方宝剑§7。",
             "§8后期每一把都要「上一把 + 稀有材料 + Boss 信物」。"},
            {"七、护甲进化链（共 17 套）", "§f布衣 → 竹甲 → 皮甲 → 织锦袍 → 青铜甲 → 白银铠",
             "§f朱砂符甲 → 凤凰羽衣 → 麒麟鳞甲§7（每件减伤 §f5% → 25%§7）",
             "§f将军铠 → 玉甲 → 龙鳞甲 → 鲛绡甲 → 玄铁重铠§7（每件减伤 §f16% → 30%§7）",
             "§6天将云铠（29%）→ 龙王鳞铠（32%，全模组最硬）",
             "§7玄天真龙甲减伤略低，但血量最厚（每件 +380）。",
             "§8升级方式：上一套同部位 + 材料 → 这一套同部位（逐件往上换）。"},
            {"八、宏伟建筑", "§6皇家宫殿§7：48×48 完整宫殿群（台基、城墙、角楼、太和殿）",
             "§6帝陵地宫§7：墓道、耳室、主墓室与陪葬宝箱",
             "§6长城§7：连绵城墙 + 垛口 + 城楼（登顶有宝箱）",
             "§6宝塔§7：七层收分塔，每层都有宝箱",
             "§6天坛§7：三层圆坛与玉柱；§6驿站§7：屋舍水井；§6牌坊§7：路边最常见",
             "§8用 /locate structure dynasty:palace 定位宫殿。"},
            {"九、科举与官阶", "§7右键 §f科举试卷§7 打开答题界面（三选一）。",
             "§7答对获得功名与增益；官阶门槛递增，不是每 100 点升一阶。",
             "§7用 §e/dynasty stats§7 查看当前官阶、功名及下阶差额。",
             "§7官阶给属性，永久万能槽由五项任务里程碑提供。",
             "§7达到尚书获御赐金锏，达到丞相获尚方宝剑（各授予一次）。",
             "§8装备按任务书中的真实配方制作，科举不会直接发龙帝玉玺。"},
            {"十、军队与阵型", "§7右键 §f虎符§7 打开调兵界面，选择阵型与人数：",
             "§f方阵§7 均衡推进  §f锋矢阵§7 突破敌阵",
             "§f雁行阵§7 两翼包抄  §f横阵§7 正面拒敌  §f圆阵§7 四面固守",
             "§7禁军会跟随你、攻击怪物，并自动传送归队。",
             "§7忠诚越高，军队士气越高。",
             "§8潜行右键虎符 = 威慑周围生物。"},
            {"十一、神兽与妖魔", "§a麒麟§7：喂食仙桃可获民心。",
             "§6凤凰§7：浴火飞行，掉落 §f凤凰羽§7（做龙吟弓）。",
             "§d九尾狐§7：受击瞬移，掉落丝绸。",
             "§c年兽§7：春节现身，惧爆竹；掉落 §f精钢§7。",
             "§7小怪：大臣、刺客、弓兵、锦衣卫、叛军、兵马俑。",
             "§8锦衣卫有几率掉落 §f兵器图纸§7。"},
            {"十二、Boss 与信物（很重要）", "§4龙帝§7（天朝）：掉落 §f龙帝玉玺§7 + 帝骸骨 + 龙晶",
             "§c叛将§7：掉落 §f叛将首级§7",
             "§5宦官首脑§7：掉落 §f内廷令牌§7",
             "§5不死始皇§7（帝陵）：掉落 §f帝骸骨§7",
             "§7这些信物就是后期神兵的「特定条件」，没有就打不动终盘。",
             "§8Boss 有士气减伤：先用破军战斧破甲再上。"},
            {"十三、节日与丹药", "§7按现实日期自动开启节日：",
             "§f春节§7(2/1-2/20) §f端午§7(6/1-6/10) §f中秋§7(9/15-9/25)",
             "§f重阳§7(10/1-10/10) §f除夕§7(12/31-1/2)",
             "§7节日发放食物、烟花与祝福效果。",
             "§7药水：龙威 / 铁壁 / 疾风 / 民心 / 天命；丹药：长寿丹、凝神丹。",
             "§8节令灯可以手动开启当令节日。"},
            {"十三·续、符箓（一次性但很强）", "§c火符§7：前方爆炎，4.5 格内 §c600+攻击×3§7 火焰伤害 + 点燃",
             "§b雷符§7：三道落雷，5 格内 §b800+攻击×4§7 伤害 + 缓慢 II + 虚弱 II",
             "§5摄魂符§7：6 格内 §5500+攻击×3§7 伤害 + 失明 + 虚弱 II",
             "§f御风符§7：8 格内敌人全部击飞，自身疾风 III + 缓降",
             "§7隐身符：隐身 60 秒并清除仇恨；金刚符：抗性 III + 力量 II（不回血）",
             "§8归乡符：回出生点并净化负面。符箓用一张少一张，别舍不得用。"},
            {"十四、数值一览（重制）", "§7武器：木矛 §f5§7 → 天子剑 §f3200§7（共 28 把；原版 2048 上限已解除）",
             "§7护甲：布衣 §f10§7 → 龙王鳞铠（共 §f17 套§7，每套 4 件）",
             "§7套装减伤：布衣 12% → 龙王鳞铠 128%（四件封顶 §f92%§7）",
             "§7套装生命：§f+120 / +600 / +880 / +1200 / +1520§7",
             "§7小怪血量已下调，前期基础武器就能打；Boss 依旧是硬骨头。",
             "§8所以武器数字是「慢慢变大」，不是一上来就上千。"},
            {"十五、饰品与槽位（只用 Curios）", "§7饰品不再有第二个存放界面，全部放进 §dCurios 的饰品槽§7：",
             "§7打开背包 → Curios 面板：头部 / 项链 / 戒指 / 手镯 / 手部 / 身体 / 背部 / 腰带 / 护符。",
             "§7把玉佩、玉璧等拖进去才生效；开局各分类槽 + §f1 个万能槽§7，五项任务里程碑各再加 1。",
             "§f玉佩§7 减伤 8%  §f玉璧§7 生命 +150  §f护心镜§7 护甲 +8 减伤 4%",
             "§f玉冠§7 生命 +220  §f金印§7 功名 +25%  §f龙鳞护符§7 护甲 +12",
             "§6共 169 件分类饰品§7：任务书按实际槽位分成九页，按需选配，不必集齐。",
             "§7入门：§f玉佩§7(减伤8%) §f玉璧§7(生命+150) §f锦囊§7(水下呼吸+夜视) §f铜镜§7(净化负面)",
             "§7通灵：§f玉龟符§7(水战) §f狐尾坠§7(跳跃II) §f麒麟角坠§7(再生+护甲) §f龙须穗§7(攻速+15%)",
             "§7功名：§f金印§7(功名+25%) §f御玺佩§7(功名+40%) §f功牌§7(生命+200) §f砚台§7(攻速+12%)",
             "§7战阵：§f护心镜§7(护甲+8) §f玄铁腰牌§7(生命+150 护甲+6) §f雷纹护符§7(雨天强化)",
             "§6传世：§f龙珠§7(攻击+25%) §f龙骨戒§7(护甲+10) §f海螺§7(水下攻+30%) §f龙王逆鳞§7(攻+20%)",
             "§8安装 Curios 时必须佩戴才生效；背包和副手不提供饰品效果。"},
            {"十六、便利操作与整合包", "§6连锁采掘（本体自带，不需要装模组）：",
             "§7按住 §e潜行§7 破坏 §f矿石§7 / §f原木§7 → 连成一片的同类方块一起采（最多 64 块、4 格内）",
             "§7每多采一块消耗 1 点工具耐久；掉落与原版一致（时运/精准照常生效）。",
             "§7整合包还附带（只优化、不改玩法）：Embeddium/FerriteCore/ModernFix/EntityCulling",
             "§7ImmediatelyFast/Clumps/MemoryLeakFix/Jade/AppleSkin/Mouse Tweaks/Crafting Tweaks",
             "§7Corpse(死亡不掉装备)/Waystones(传送石)/双指南针/小地图/Comforts/右键收割/伤害数字/火把大师"},
            {"十七、法阵·祭坛（召唤 Boss）", "§7新方块 §6法阵·祭坛§7：用 §eBoss 信物§7对着它使用即可召唤对应 Boss。",
             "§7摆放：祭坛四周的 3×3 环里放 §f4 块玉石块§7 → 法阵成形（手持信物右键）。",
             "§7信物对照：§f龙帝玉玺§7→龙帝  §f叛将首级§7→叛将",
             "§7          §f内廷令牌§7→宦官首脑  §f帝骸骨§7→不死始皇",
             "§7信物就是 Boss 自己的掉落物，所以每个 Boss 都能反复挑战（刷装备）。",
             "§8召唤时会落三道雷并烧起灵火；附近 80 格内已有同种 Boss 时会拒绝召唤。"},
            {"十八、新建筑与新饰品", "§7九种建筑都会在地表随机生成：",
             "§6长城 / 宝塔 / 天坛 / 驿站 / 牌坊§7 + §6法阵 / 神庙 / 兵营 / 烽火台",
             "§7其中 §6法阵§7 与 §6神庙§7 中央自带 §6法阵·祭坛§7（直接就能召唤 Boss）。",
             "§7新饰品（放 Curios 槽）：玉蝉(残血抗性) 龙珠(攻击+25%) 凤凰指环(抗火灭火)",
             "§7雷纹护符(雷雨力量II) 明月佩(夜间夜视+幸运) 虎符残片(威慑退敌)",
             "§8Boss 已加强：更硬更痛，龙帝会爆龙焰、始皇带尸毒光环。"},
            {"十九、任务与图鉴怎么用", "§6任务全部在 §dFTB 任务书§6 里（整合包自带）：",
             "§fA.§7 右键「任务书」或按 §eOpen Quests§7 键打开",
             "§7   先看 §f主线旅程§7 的八个小章节；§f支线 / 装备 / 饰品§7 分组按需查询，",
             "§7   主线按编号与连线前进，每个节点说明为什么做、怎么做、下一步去哪。",
             "§7   安家 → 工坊 → 平叛 → 天朝 → 幽冥 → 九霄 → 龙宫 → 龙帝；不要求清空图鉴。",
             "§fB.§7 物品、击杀、维度、成就自动检测；少量阅读提示手动勾选，不发奖励。",
             "§7   任务给物品、经验和功名；§6六边形里程碑§7额外永久解锁万能饰品槽。",
             "§c模组内不再另有一套任务界面§7，只看 FTB 任务书这一处。",
             "§7图鉴：右键《王朝说明书》看手册，或看 §f王朝图鉴§7 物品栏页签。"},
            {"二十、第一段旅程", "§f1.§7 建据点、照明和熔炉，再把木矛逐步升级到铁剑，补盾牌。",
             "§f2.§7 铜锭×3 + 铁锭 → 青铜锭×4；遗迹宝箱找朱砂，做图纸和青铜剑。",
             "§f3.§7 按需制作防具、佩戴饰品；科举答对一次，领取第一个永久万能槽。",
             "§f4.§7 虎符调兵，在主世界找叛将；宦官首脑留到进入天朝后再找。",
             "§f5.§7 主世界深层找龙晶，先备归乡符和两座传送门，再入天朝。",
             "§8不设限时，不强迫收集所有武器。卡住时看当前节点的获取路线。"},
            {"二十一、功名怎么来的（升官全靠它）", "§6功名 = 官阶经验§7，官阶提升属性；万能槽通过任务解锁。",
             "§f① 打怪§7：Boss 最多（龙帝 +300 / 天将 +260 / 始皇 +240 / 叛将·宦官 +220），",
             "§7   神兽 +40~60，锦衣卫与刺客 +12，杂兵 +5（杂兵 10 分钟最多 +120，防刷）。",
             "§f② 与 NPC 交互§7：科举答对 +30、与大臣交谈 +15、虎符列阵 +12、喂麒麟 +10。",
             "§f③ 第一次获得新物品§7：龙晶/玄天玉/帝骸骨 +25，玉/凤羽/信物 +12，印章·圣旨 +8。",
             "§f④ 任务§7：只给一点点（+12~+40），别指望靠任务升满。",
             "§7查进度：§e/dynasty stats§7（会显示「升下一阶还需多少功名」）。"},
            {"二十二、饰品与槽位规则", "§7开局各分类 1 格，戒指 2 格，另外有 §d1 个万能饰品槽§7。",
             "§7完成科举中第、首次击败叛将、踏入天朝、斩帝、沧海定波，各永久 §d+1 万能槽§7。",
             "§7五项全部完成共 6 个万能槽；重复领取不叠加，死亡或重进不丢失。",
             "§f饰品怎么来§7：合成（玉佩/护心镜/玉冠…）、建筑宝箱、Boss 掉落、任务奖励。",
             "§7重点推荐：§f龙珠§7(攻击+25%)、§f金印§7(功名+25%)、§f护心镜§7(减伤+护甲)、",
             "§7§f朱砂囊§7(解毒)、§f虎符残片§7(威慑退敌)、§f瑞兽铃§7(攻速+驱散)。"},
            {"二十三、Boss 怎么打（预警机制）", "§6所有大招都会提前 1 秒预警§7（粒子 + 吼声），看到就躲：",
             "§f龙帝§7：火球 + 龙焰爆发(6 格) + 召禁军；残血会瞬移追你 → 别放风筝。",
             "§f叛将§7：冲锋撞飞 + 掷矛；残血狂暴，注意侧移躲矛。",
             "§f宦官首脑§7：阴毒(虚弱+失明) + 毒雾 + 召刺客/弓兵；被贴身会闪开。",
             "§f始皇§7：尸毒光环 + 凋零之首 + 你跑远就落雷 → 近身换血更安全。",
             "§f九霄天将§7：落雷 + 冲锋 + 掷矛 + 召云兵（先清小兵再打主将）。",
             "§8打法要点：带金创药/长生丹，穿一整套甲（套装减伤 60~80%），别空手。",
             "§8想反复打：把 Boss 信物拿到 §6法阵·祭坛§8（四角放玉石块）右键即可召唤。"},
            {"二十四、资源在哪 & 卡住了怎么办", "§f玉矿§7：y 30 以下，常见于山地；§f深层玉矿§7 更低。",
             "§f朱砂§7：神庙、法阵、帝陵宝箱；§f铜/铁§7：矿洞；§f竹子§7：丛林。",
             "§f龙晶矿§7：主世界 Y=-60 至 -5 也有，铁镐可采；不要误以为必须先入天朝。",
             "§f蟠桃§7：天朝树；§f凤凰羽§7：凤凰掉落；§f麒麟角§7：喂麒麟后掉落。",
             "", "§6卡住常见原因§7：",
             "§7• 主线锁着 → 查看连线指向的上一项；支线/图鉴不锁主线。",
             "§7• 打不过 Boss → 检查护甲、饰品佩戴和恢复品；官阶靠功名，槽位靠里程碑。",
             "§7• 找不到维度 → 造传送门：天朝传送门(天朝) / 地府传送门(地府) / 九霄传送门(九霄)。",
             "§7• 打不开任务书 → 右键「任务书」物品，或到 §e选项→控制→FTB Quests§7 绑定按键。"},
            {"二十五、快捷键与操作（附录）", "§fE§7 打开背包：左上角可看到 §dCurios 饰品槽§7，万能槽由任务里程碑解锁。",
             "§fShift + 悬停§7：看武器/道具的用法与数值（护甲词条则是直接显示）。",
             "§f右键§7：用手中的道具（试卷、虎符、玉玺、圣旨、符箓、药水…）。",
             "§f潜行 + 右键§7：部分道具的第二功能（虎符威慑、玉玺赐福）。",
             "§fJ§7：打开任务书（若没绑定，去 选项 → 控制 → FTB Quests 里设）。",
             "§fM§7：大地图 / 小地图（按住可放大）。§fZ§7：缩放（Just Zoom）。",
             "§fF3§7：调试信息（装了 BetterF3，排版更清爽）。"},
            {"二十六、食物、药水与丹药（附录）", "§7王朝食物不只是回饱食度，很多带 §d增益§7：",
             "§f饺子/汤圆/粽子/月饼§7：饱食度更高、吃完短暂抗性。",
             "§f茶§7：短时间提神（速度）；§f美酒/白酒§7：力量但会醉（缓慢）。",
             "§f火锅/烤鸭§7：回血最多的两类，打 Boss 前吃。",
             "§f王朝药水§7：龙威(攻击+300) / 铁壁(护甲+20、减伤30%) / 疾风 / 民心(生命+100) / 天命(幸运)。",
             "§f喷溅·滞留药水§7：右击投掷，给范围单位上增益；团队战很好用。",
             "§f凝神丹§7 恢复状态；§f长生丹§7 大幅回血并给抗性；§f金创药§7 便宜好用。"},
            {"二十七、附魔与词条怎么看（附录）", "§7装备上的属性分三类，看懂就能选对装备：",
             "§f① 基础护甲/韧性§7：直接影响减伤，护甲越高越好（词条直接显示）。",
             "§f② 套装加成§7：四件同套叠加（布衣 12% → 玄铁重铠 120% 上限收口 90%）。",
             "§f③ 词条/特效§7：例如「受击获得力量」「命中回气」「水下增伤」，看装备说明即可。",
             "§7武器只显示攻击力 + 机制一句话（按 Shift 展开完整说明）。",
             "§7饰品放在 Curios 槽里生效，说明书每件都写清效果。",
             "§8建议：先凑齐一套装备再生级，套装加成比单件数值更重要。"},
            {"二十八、常见问题（FAQ）", "§fQ：任务锁着做不了？§7 A：看主线编号和连线；配方材料说明不是额外锁定条件。",
             "§fQ：打不过 Boss？§7 A：补防具与恢复品，确认饰品已佩戴；先躲预警，再打输出。",
             "§fQ：找不到玉矿？§7 A：y 30 以下，山地/丘陵更密；深层玉矿更低。",
             "§fQ：怎么去别的维度？§7 A：造传送门——天朝传送门(天朝) / 地府传送门(地府) / 九霄传送门(九霄) / 龙宫传送门(龙宫)。",
             "§fQ：功名怎么涨？§7 A：打怪（Boss 最多）、与 NPC 交互、第一次获得新物品；任务只给一点。",
             "§fQ：万能槽怎么增加？§7 A：找任务书中的金色里程碑，五项各加 1 格，开局 1 格 → 6 格。",
             "§fQ：卡顿怎么办？§7 A：按 Spark 分析（/spark profiler），或降低渲染距离、关光影。",
             "§8还有问题就按 F3 看日志，或把 latest.log 发给我。"},
            {"王朝图鉴 · 完", "§7愿你的王朝长治久安。",
             "§8—— 制作：Dynasty Mod ——", "", "§8本指南为模组内置，无需 Patchouli。", ""},
            {"二十九、饰品的三种新玩法",
             "§f① 命中触发§7：部分饰品是「打的时候」生效 —— 吸血 / 斩杀（低血线了结）/ 会心 / 突袭（只在目标满血，也就是第一刀）/ 连击（3 秒内最多 6 层）/ 雷罚。",
             "§7悬浮说明最后一行会写「命中时：…」，概率不到 100% 的会标出概率。",
             "§f② 连携§7：同系饰品一起戴才有额外加成，2 / 3 / 4 件各一档（§f取最高档、不叠层§7）——",
             "§7昼夜双生（移速 → 攻击+移速 → 攻击+移速加强）、生死代价（攻击递增，4 件补生命）、",
             "§7天朝敕令（幸运 → 幸运+生命 → 常驻龙威+攻击）、幽冥献祭（攻击递增，4 件补生命）、巧匠边塞（攻速 → …+移速 → …+攻击距离）。",
             "§8换上一件时聊天栏会提示「[连携] … 生效中」，取下立刻回退。",
             "§f③ 伤势§7：单次挨到 §f15%§7 生命以上的重击就累积伤势（按伤害比例，单次最多 +12），死亡额外 +25。",
             "§7每 10 点伤势扣 §f3%§7 生命上限（最多 −30%）；到 §f34 / 67§7 点会挂上模组效果【内伤】I / II。",
             "§7治疗：喝王朝丹药（含喷溅版）一次 −40、睡一觉 −40、其余时间每 10 秒自然恢复 1 点。",
             "§8搭配建议：代价型饰品（拿生命上限换伤害）要配合丹药与睡觉轮换，别一路硬扛。"},
    };

    /**
     * 左侧栏分组：{组名, 组内页序号…}（顺序就是阅读顺序）。
     * Sidebar sections: {title, page indexes…} — the order here is the reading order.
     */
    private static final Object[][] SECTIONS = {
            {"开始 · 上车", new int[]{0, 1, 2, 3, 24}},
            {"王朝 · 仕途", new int[]{12, 13, 25, 26, 19, 17}},
            {"兵甲 · 装备", new int[]{8, 9, 10, 18, 31, 34}},
            {"世界 · 探索", new int[]{4, 5, 6, 7, 11, 14, 22, 15, 27, 21, 16, 28, 20, 23, 29, 30, 32}},
            {"收尾", new int[]{33}},
    };

    /** 全书翻页顺序 / page order used by ← → and the wheel */
    private static final int[] ORDER = buildOrder();

    private static int[] buildOrder() {
        List<Integer> list = new ArrayList<>();
        for (Object[] section : SECTIONS) {
            for (int page : (int[]) section[1]) {
                list.add(page);
            }
        }
        int[] out = new int[list.size()];
        for (int i = 0; i < out.length; i++) {
            out[i] = list.get(i);
        }
        return out;
    }

    private int page = 0;
    private int scroll = 0;
    private final boolean[] expanded = new boolean[SECTIONS.length];

    // 版面（init 里算一次）/ layout, computed once in init()
    private int panelW;
    private int panelH;
    private int left;
    private int top;
    private int sideW;
    private int contentX;
    private int contentW;

    public GuideScreen() {
        super(Component.translatable("screen.dynasty.guide"));
        for (int s = 0; s < SECTIONS.length; s++) {
            for (int p : (int[]) SECTIONS[s][1]) {
                if (p == this.page) {
                    this.expanded[s] = true;
                }
            }
        }
    }

    @Override
    protected void init() {
        this.panelW = Math.min(this.width - 24, 540);
        this.panelH = this.height - 70;
        this.left = (this.width - this.panelW) / 2;
        this.top = 22;
        this.sideW = Mth.clamp(this.panelW / 3, 110, 168);
        this.contentX = this.left + this.sideW;
        this.contentW = this.panelW - this.sideW;

        int y = this.top + this.panelH + 6;
        this.addRenderableWidget(Button.builder(Component.literal("◀ 上一页"), b -> this.flip(-1))
                .bounds(this.width / 2 - 160, y, 100, 20).build());
        this.addRenderableWidget(Button.builder(Component.literal("关闭"), b -> this.onClose())
                .bounds(this.width / 2 - 50, y, 100, 20).build());
        this.addRenderableWidget(Button.builder(Component.literal("下一页 ▶"), b -> this.flip(1))
                .bounds(this.width / 2 + 60, y, 100, 20).build());
        this.ensureVisible();
    }

    /** 侧栏行：{0=分组标题 / 1=页面, 序号, y, 高} / sidebar rows */
    private List<int[]> buildRows() {
        List<int[]> rows = new ArrayList<>();
        int y = this.top + 6 - this.scroll;
        for (int s = 0; s < SECTIONS.length; s++) {
            rows.add(new int[]{0, s, y, 12});
            y += 12;
            if (this.expanded[s]) {
                for (int p : (int[]) SECTIONS[s][1]) {
                    rows.add(new int[]{1, p, y, 11});
                    y += 11;
                }
                y += 3;
            }
        }
        return rows;
    }

    private int sidebarHeight() {
        int h = 12;
        for (int s = 0; s < SECTIONS.length; s++) {
            h += 12;
            if (this.expanded[s]) {
                h += ((int[]) SECTIONS[s][1]).length * 11 + 3;
            }
        }
        return h;
    }

    /** 让当前页那一行始终留在可视范围里 / keep the selected row on screen */
    private void ensureVisible() {
        int rowTop = -1;
        for (int[] row : this.buildRows()) {
            if (row[0] == 1 && row[1] == this.page) {
                rowTop = row[2];
            }
        }
        if (rowTop < 0) {
            return;
        }
        int viewTop = this.top + 4;
        int viewBottom = this.top + this.panelH - 4;
        if (rowTop < viewTop) {
            this.scroll -= viewTop - rowTop;
        } else if (rowTop + 11 > viewBottom) {
            this.scroll += rowTop + 11 - viewBottom;
        }
        this.scroll = Mth.clamp(this.scroll, 0, Math.max(0, this.sidebarHeight() - this.panelH));
    }

    private int orderIndex() {
        for (int i = 0; i < ORDER.length; i++) {
            if (ORDER[i] == this.page) {
                return i;
            }
        }
        return 0;
    }

    private void setPage(int target) {
        this.page = Mth.clamp(target, 0, PAGES.length - 1);
        for (int s = 0; s < SECTIONS.length; s++) {
            for (int p : (int[]) SECTIONS[s][1]) {
                if (p == this.page) {
                    this.expanded[s] = true;
                }
            }
        }
        this.ensureVisible();
    }

    private void flip(int delta) {
        this.setPage(ORDER[Mth.clamp(this.orderIndex() + delta, 0, ORDER.length - 1)]);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_LEFT || keyCode == GLFW.GLFW_KEY_A) {
            this.flip(-1);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_RIGHT || keyCode == GLFW.GLFW_KEY_D) {
            this.flip(1);
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        for (int[] row : this.buildRows()) {
            if (!inside(mouseX, mouseY, this.left + 2, row[2], this.sideW - 4, row[3])) {
                continue;
            }
            if (row[0] == 0) {
                this.expanded[row[1]] = !this.expanded[row[1]];      // 折叠 / 展开分组
            } else {
                this.setPage(row[1]);
            }
            return true;
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        if (mouseX >= this.left && mouseX <= this.left + this.sideW
                && mouseY >= this.top && mouseY <= this.top + this.panelH) {
            int max = Math.max(0, this.sidebarHeight() - this.panelH);
            this.scroll = Mth.clamp(this.scroll + (delta > 0 ? -24 : 24), 0, max);
            return true;
        }
        this.flip(delta > 0 ? -1 : 1);
        return true;
    }

    private static boolean inside(double mouseX, double mouseY, int x, int y, int w, int h) {
        return mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h;
    }

    /** 去掉 §x 颜色代码，用于量宽度 / strip legacy colour codes before measuring */
    private static String plain(String text) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c == '§' && i + 1 < text.length()) {
                i++;
                continue;
            }
            out.append(c);
        }
        return out.toString();
    }

    /** 按像素宽度折行，换行后自动补上颜色代码 / wrap to a pixel width, keeping colours */
    private List<String> wrap(String line, int maxWidth) {
        List<String> out = new ArrayList<>();
        if (line == null || line.isEmpty()) {
            out.add("");
            return out;
        }
        String active = "";
        StringBuilder cur = new StringBuilder();
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == '§' && i + 1 < line.length()) {
                active = line.substring(i, i + 2);
                cur.append(active);
                i++;
                continue;
            }
            cur.append(c);
            if (this.font.width(plain(cur.toString())) > maxWidth) {
                cur.deleteCharAt(cur.length() - 1);
                out.add(cur.toString());
                cur = new StringBuilder(active);
                cur.append(c);
            }
        }
        out.add(cur.toString());
        return out;
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);

        // 书页底 + 左侧栏底色 / book page + sidebar background
        graphics.fill(this.left - 2, this.top - 2, this.left + this.panelW + 2,
                this.top + this.panelH + 2, 0xFF2A2118);
        graphics.fill(this.left, this.top, this.left + this.panelW, this.top + this.panelH, 0xD0121014);
        graphics.fill(this.left, this.top, this.left + this.sideW, this.top + this.panelH, 0xE01A1720);

        // ---- 左侧栏 / sidebar ----
        for (int[] row : this.buildRows()) {
            if (row[2] + row[3] < this.top || row[2] > this.top + this.panelH) {
                continue;
            }
            int x = this.left + 2;
            int w = this.sideW - 4;
            boolean hover = inside(mouseX, mouseY, x, row[2], w, row[3]);
            if (row[0] == 0) {
                String arrow = this.expanded[row[1]] ? "▼ " : "▶ ";
                graphics.drawString(this.font, arrow + SECTIONS[row[1]][0], this.left + 8,
                        row[2] + 2, hover ? 0xFFE9B8 : 0xC8A860);
                graphics.fill(x, row[2] + row[3] - 1, x + w, row[2] + row[3], 0x50E9B8);
            } else {
                boolean selected = row[1] == this.page;
                if (selected) {
                    graphics.fill(x, row[2] - 1, x + w, row[2] + row[3] - 1, 0x60E9B8);
                } else if (hover) {
                    graphics.fill(x, row[2] - 1, x + w, row[2] + row[3] - 1, 0x30FFFFFF);
                }
                graphics.drawString(this.font,
                        this.font.plainSubstrByWidth(PAGES[row[1]][0], w - 10),
                        this.left + 12, row[2] + 2, selected ? 0xFFFFFF : 0xA8A8A8);
            }
        }

        // ---- 正文 / page body ----
        String[] content = PAGES[this.page];
        int cx = this.contentX + 8;
        int cw = this.contentW - 16;
        int bodyTop = this.top + 32;
        int footerY = this.top + this.panelH - 14;
        graphics.drawCenteredString(this.font, content[0], this.contentX + this.contentW / 2,
                this.top + 10, 0xFFE9B8);
        graphics.fill(cx, this.top + 24, cx + cw, this.top + 25, 0x50E9B8);

        // 先折行再按可用高度收紧行距：GUI 缩放开大时也不会被底部页脚盖掉
        // Wrap first, then tighten line spacing if the page is taller than the panel.
        List<List<String>> wrapped = new ArrayList<>();
        int lines = 0;
        for (int i = 1; i < content.length; i++) {
            List<String> part = this.wrap(content[i], cw);
            wrapped.add(part);
            lines += part.size();
        }
        int lineHeight = 11;
        int available = footerY - 8 - bodyTop;
        if (lines > 0 && lines * lineHeight > available) {
            lineHeight = Math.max(8, available / lines);
        }
        int y = bodyTop;
        for (List<String> part : wrapped) {
            for (String line : part) {
                graphics.drawString(this.font, line, cx, y, 0xFFFFFF);
                y += lineHeight;
            }
        }
        graphics.drawCenteredString(this.font,
                "§7第 " + (this.orderIndex() + 1) + " / " + ORDER.length
                        + " 页 §8| §7滚轮翻页 · 点左侧跳页",
                this.contentX + this.contentW / 2, this.top + this.panelH - 14, 0x9A9A9A);

        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
