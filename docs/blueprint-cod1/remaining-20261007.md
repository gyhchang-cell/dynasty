# cod1 当前缺口核对 · 2026-10-07

输入：用户上传 cod1_new(5).txt，与仓库 cod1_new.txt 逐字节相同。
代码基线：main 6feb7f140bfb0884d34f8b1d4e9e0f3732efa053。交付分支：cod1。
原 cod1 6df2048 是 main 的祖先，本次快进接入 main 已有成果，保留强化系统及最新完整 FTB 导出。
本次没有新实现怪物、精英、Boss、神器或神影，也没有完成 cod1 剩余部分。

## 当前状态

**0 DONE / 18 PARTIAL / 76 NOT_STARTED。** 18只基础怪有运行代码和资源，但最新构建的单机、双人及性能验收待完成。
待开发12基础怪、15精英、12Boss、25神器、12神影；下一内容条目是第19只碧水玄蛟幼崽。
DungeonDefinition 中的 pilin_zhijinwu/juchui_jinjia_lishi 是设计引用，不是实体注册，不因此标已实现。相似旧实体、Boss和装备也不替代蓝图精确条目。镇渊帝君保持最终Boss。

## 先决条件

输入第40—49行要求先验证青龙黑屏修复再继续，第1636—1643行禁止以构建或GameTest代替最新单机及双人。
ImperialWeaponRenderer / ImperialRenderState 已有渲染阶段分离、状态恢复和旁观世界空间逻辑；不删除神影、缩模型或关效果。
ArmyBehaviors.Powder / TimedAttack 已有引信取消/重载修复；旧测试记录保留，不重复重写。
仓库272/272及已有客户端截图是历史证据，不算本次重新运行通过。当前环境验证结果见本文末尾。

## 已实现但待验收的18项

实现类均在 src/main/java/com/dynasty/blueprint：BlueprintEntities + TemplateMob；技能在 TemplateSkills 或 ArmySkills/ArmyBehaviors。
生成：TemplateContentDefinitions、BlueprintSpawns及结构/生态数据。资源前缀为 src/main/resources/assets/dynasty。
掉落表均在 data/dynasty/loot_tables/entities/<ID>.json；材料用途在 BlueprintSalvage 和 recipes。

| 名称 / ID | geo / animation | texture | 技能、生成、掉落 | 最新单机 | 最新双人 | 性能 |
| --- | --- | --- | --- | --- | --- | --- |
| 卒伍刀手 / `zuwu_daoshou` | `geo/blueprint/zuwu_daoshou.geo.json`；`animations/blueprint/zuwu_daoshou.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 拒马长枪兵 / `juma_changqiangbing` | `geo/blueprint/juma_changqiangbing.geo.json`；`animations/blueprint/juma_changqiangbing.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 连弩阵卒 / `liannu_zhenzu` | `geo/blueprint/liannu_zhenzu.geo.json`；`animations/blueprint/liannu_zhenzu.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 橹盾甲士 / `ludun_jiashi` | `geo/blueprint/ludun_jiashi.geo.json`；`animations/blueprint/ludun_jiashi.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 符法祭酒 / `fufa_jijiu` | `geo/blueprint/fufa_jijiu.geo.json`；`animations/blueprint/fufa_jijiu.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 铁索斥候 / `tiesuo_chihou` | `geo/blueprint/tiesuo_chihou.geo.json`；`animations/blueprint/tiesuo_chihou.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 溃军死士 / `kuijun_sishi` | `geo/blueprint/kuijun_sishi.geo.json`；`animations/blueprint/kuijun_sishi.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 阵亡掌旗官 / `zhenwang_zhangqiguan` | `geo/blueprint/zhenwang_zhangqiguan.geo.json`；`animations/blueprint/zhenwang_zhangqiguan.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 披甲叛将护卫 / `pijia_panjiang_huwei` | `geo/blueprint/pijia_panjiang_huwei.geo.json`；`animations/blueprint/pijia_panjiang_huwei.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 阴兵鬼卒 / `yinbing_guizu` | `geo/blueprint/yinbing_guizu.geo.json`；`animations/blueprint/yinbing_guizu.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 尸变力士 / `shibian_lishi` | `geo/blueprint/shibian_lishi.geo.json`；`animations/blueprint/shibian_lishi.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 缚魂白布童子 / `fuhun_baibu_tongzi` | `geo/blueprint/fuhun_baibu_tongzi.geo.json`；`animations/blueprint/fuhun_baibu_tongzi.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 纸人剑客 / `zhiren_jianke` | `geo/blueprint/zhiren_jianke.geo.json`；`animations/blueprint/zhiren_jianke.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 墓穴飞颅 / `muxue_feilu` | `geo/blueprint/muxue_feilu.geo.json`；`animations/blueprint/muxue_feilu.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 山精山魈 / `shanjing_shanxiao` | `geo/blueprint/shanjing_shanxiao.geo.json`；`animations/blueprint/shanjing_shanxiao.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 赤目朱蛤 / `chimu_zhuha` | `geo/blueprint/chimu_zhuha.geo.json`；`animations/blueprint/chimu_zhuha.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 枯木树精 / `kumu_shujing` | `geo/blueprint/kumu_shujing.geo.json`；`animations/blueprint/kumu_shujing.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |
| 鸣沙石蝎 / `mingsha_shixie` | `geo/blueprint/mingsha_shixie.geo.json`；`animations/blueprint/mingsha_shixie.animation.json` | 共享图集，见TemplateMobModel | 已有运行实现，最终质量待验 | 未验收 | 未验收 | 未测 |

## 剩余76项

以下条目未见对应的完整运行实现。实现类、geo、animation、texture、技能、运行落点和奖励接口待实施；单机、双人、性能均待验收。

| 类别 | 编号 | 名称 | 拟定ID | 状态 |
| --- | --- | --- | --- | --- |
| BASIC | 19 | 碧水玄蛟幼崽 | `dynasty:bishui_xuanjiao_youzi` | NOT_STARTED |
| BASIC | 20 | 巨臂石敢当 | `dynasty:jubi_shigandang` | NOT_STARTED |
| BASIC | 21 | 巡山木甲犬 | `dynasty:xunshan_mujiaquan` | NOT_STARTED |
| BASIC | 22 | 青铜双头蛇傀 | `dynasty:qingtong_shuangtoushekui` | NOT_STARTED |
| BASIC | 23 | 八足地工蛛 | `dynasty:bazu_digongzhu` | NOT_STARTED |
| BASIC | 24 | 幽灯鬼面蝠 | `dynasty:youdeng_guimianfu` | NOT_STARTED |
| BASIC | 25 | 穴居盲骨鱼 | `dynasty:xueju_mangguyu` | NOT_STARTED |
| BASIC | 26 | 煞水浮溺鬼 | `dynasty:shashui_funigui` | NOT_STARTED |
| BASIC | 27 | 巨力赑屃傀儡 | `dynasty:juli_bixi_kuilei` | NOT_STARTED |
| BASIC | 28 | 百目魔蜈 | `dynasty:baimu_mowu` | NOT_STARTED |
| BASIC | 29 | 铜臂飞天夜叉 | `dynasty:tongbi_feitian_yecha` | NOT_STARTED |
| BASIC | 30 | 阴阳纸轿游魂 | `dynasty:yinyang_zhijiao_youhun` | NOT_STARTED |
| ELITE | 1 | 陷阵断头将 | `dynasty:xianzhen_duantoujiang` | NOT_STARTED |
| ELITE | 2 | 鬼车九首鸟 | `dynasty:guiche_jiushouniao` | NOT_STARTED |
| ELITE | 3 | 千机百炼偃师 | `dynasty:qianji_bailian_yanshi` | NOT_STARTED |
| ELITE | 4 | 披鳞执金吾 | `dynasty:pilin_zhijinwu` | NOT_STARTED |
| ELITE | 5 | 白面狐仙姑 | `dynasty:baimian_huxiangu` | NOT_STARTED |
| ELITE | 6 | 巨锤金甲力士 | `dynasty:juchui_jinjia_lishi` | NOT_STARTED |
| ELITE | 7 | 蛊毒天蛛女 | `dynasty:gudu_tianzhunv` | NOT_STARTED |
| ELITE | 8 | 阴阳炼丹方士 | `dynasty:yinyang_liandan_fangshi` | NOT_STARTED |
| ELITE | 9 | 伏波巡海夜叉 | `dynasty:fubo_xunhai_yecha` | NOT_STARTED |
| ELITE | 10 | 搬山甲胄尸狂 | `dynasty:banshan_jiazhou_shikuang` | NOT_STARTED |
| ELITE | 11 | 墨家绝影刺客 | `dynasty:mojia_jueying_cike` | NOT_STARTED |
| ELITE | 12 | 撼山铜甲巨猿 | `dynasty:hanshan_tongjia_juyuan` | NOT_STARTED |
| ELITE | 13 | 青灯判官鬼差 | `dynasty:qingdeng_panguan_guichai` | NOT_STARTED |
| ELITE | 14 | 烈风金雕羽士 | `dynasty:liefeng_jindiao_yushi` | NOT_STARTED |
| ELITE | 15 | 镇墓狻猊铜吼 | `dynasty:zhenmu_suanni_tonghou` | NOT_STARTED |
| BOSS | 1 | 断代凶镬·饕宴之尸 | `dynasty:taoyan_zhishi` | NOT_STARTED |
| BOSS | 2 | 殉节盲帅·公孙无妄 | `dynasty:gongsun_wuwang` | NOT_STARTED |
| BOSS | 3 | 九霄木鸢·鲁班遗煞 | `dynasty:luban_yisha` | NOT_STARTED |
| BOSS | 4 | 沉渊骨龙·烛阴残蜕 | `dynasty:zhuyin_cantui` | NOT_STARTED |
| BOSS | 5 | 金阙尸仙·昭明帝 | `dynasty:zhaoming_di` | NOT_STARTED |
| BOSS | 6 | 赤练红罗·蛇母娘娘 | `dynasty:shemu_niangniang` | NOT_STARTED |
| BOSS | 7 | 无相孽火·黑风法王 | `dynasty:heifeng_fawang` | NOT_STARTED |
| BOSS | 8 | 镇国机关偶·刑天遗卫 | `dynasty:xingtian_yiwei` | NOT_STARTED |
| BOSS | 9 | 九天玄刹·雷泽巨灵 | `dynasty:leize_juling` | NOT_STARTED |
| BOSS | 10 | 幽冥引渡·彼岸冥舟 | `dynasty:bian_mingzhou` | NOT_STARTED |
| BOSS | 11 | 封魔剑冢·玄天剑煞 | `dynasty:xuantian_jiansha` | NOT_STARTED |
| BOSS | 12 | 四象逆脉·混元祖兽 | `dynasty:hunyuan_zushou` | NOT_STARTED |
| ARTIFACT | 1 | 龙吟斩马断岳刀 | `dynasty:longyin_zhanma_duanyue_dao` | NOT_STARTED |
| ARTIFACT | 2 | 湛卢仁道八面剑 | `dynasty:zhanlu_rendao_bamian_jian` | NOT_STARTED |
| ARTIFACT | 3 | 九曲透骨红缨枪 | `dynasty:jiuqu_tougu_hongying_qiang` | NOT_STARTED |
| ARTIFACT | 4 | 方天乱世破军戟 | `dynasty:fangtian_luanshi_pojun_ji` | NOT_STARTED |
| ARTIFACT | 5 | 逐日流金落星弓 | `dynasty:zhuri_liujin_luoxing_gong` | NOT_STARTED |
| ARTIFACT | 6 | 天机匣式神机弩 | `dynasty:tianji_xiashi_shenji_nu` | NOT_STARTED |
| ARTIFACT | 7 | 惊鸿流云金丝扇 | `dynasty:jinghong_liuyun_jinsi_shan` | NOT_STARTED |
| ARTIFACT | 8 | 镇岳九龙受命印 | `dynasty:zhenyue_jiulong_shouming_yin` | NOT_STARTED |
| ARTIFACT | 9 | 照胆通幽八卦镜 | `dynasty:zhaodan_tongyou_bagua_jing` | NOT_STARTED |
| ARTIFACT | 10 | 惊世太古晨钟 | `dynasty:jingshi_taigu_chenzhong` | NOT_STARTED |
| ARTIFACT | 11 | 千机罗刹百刃伞 | `dynasty:qianji_luosha_bairen_san` | NOT_STARTED |
| ARTIFACT | 12 | 广陵遗响九霄琴 | `dynasty:guangling_yixiang_jiuxiao_qin` | NOT_STARTED |
| ARTIFACT | 13 | 绝笔春秋判官笔 | `dynasty:juebi_chunqiu_panguan_bi` | NOT_STARTED |
| ARTIFACT | 14 | 缚龙索魂玄铁链 | `dynasty:fulong_suohun_xuantie_lian` | NOT_STARTED |
| ARTIFACT | 15 | 夸父逐日追光杖 | `dynasty:kuafu_zhuri_zhuiguang_zhang` | NOT_STARTED |
| ARTIFACT | 16 | 八卦紫金飞龙葫 | `dynasty:bagua_zijin_feilong_hu` | NOT_STARTED |
| ARTIFACT | 17 | 伏羲连山归藏易 | `dynasty:fuxi_lianshan_guizang_yi` | NOT_STARTED |
| ARTIFACT | 18 | 破阵轰雷生铁铳 | `dynasty:pozhen_honglei_shengtie_chong` | NOT_STARTED |
| ARTIFACT | 19 | 斩业诛邪双柳叶 | `dynasty:zhanye_zhuxie_shuangliuye` | NOT_STARTED |
| ARTIFACT | 20 | 辟邪白玉镇魂箫 | `dynasty:bixie_baiyu_zhenhun_xiao` | NOT_STARTED |
| ARTIFACT | 21 | 翻江倒海混天绫 | `dynasty:fanjiang_daohai_huntian_ling` | NOT_STARTED |
| ARTIFACT | 22 | 驱邪伏魔金刚杵 | `dynasty:quxie_fumo_jingang_chu` | NOT_STARTED |
| ARTIFACT | 23 | 青蚨聚宝金错刀 | `dynasty:qingfu_jubao_jincuo_dao` | NOT_STARTED |
| ARTIFACT | 24 | 幽都忘川招魂幡 | `dynasty:youdu_wangchuan_zhaohun_fan` | NOT_STARTED |
| ARTIFACT | 25 | 乾坤阴阳两界环 | `dynasty:qiankun_yinyang_liangjie_huan` | NOT_STARTED |
| PHANTOM | 1 | 巨灵开山神手 | `dynasty:juling_kaishan_shenshou` | NOT_STARTED |
| PHANTOM | 2 | 明镜照世法身 | `dynasty:mingjing_zhaoshi_fashen` | NOT_STARTED |
| PHANTOM | 3 | 三坛海会三头六臂法相 | `dynasty:santan_haihui_santou_liubi_faxiang` | NOT_STARTED |
| PHANTOM | 4 | 玄武磐石覆地真影 | `dynasty:xuanwu_panshi_fudi_zhenying` | NOT_STARTED |
| PHANTOM | 5 | 太白剑仙器灵出窍 | `dynasty:taibai_jianxian_qiling_chuqiao` | NOT_STARTED |
| PHANTOM | 6 | 九天玄女引天刑 | `dynasty:jiutian_xuannv_yintianxing` | NOT_STARTED |
| PHANTOM | 7 | 凶煞白虎裂天影 | `dynasty:xiongsha_baihu_lietianying` | NOT_STARTED |
| PHANTOM | 8 | 伏羲八卦开天指 | `dynasty:fuxi_bagua_kaitianzhi` | NOT_STARTED |
| PHANTOM | 9 | 上古夸父逐日奔影 | `dynasty:shanggu_kuafu_zhuri_benying` | NOT_STARTED |
| PHANTOM | 10 | 忘川摆渡幽冥客 | `dynasty:wangchuan_baidu_youmingke` | NOT_STARTED |
| PHANTOM | 11 | 墨家巨子千手天工枢 | `dynasty:mojia_juzi_qianshou_tiangongshu` | NOT_STARTED |
| PHANTOM | 12 | 烈火祝融九龙绕体神像 | `dynasty:liehuo_zhurong_jiulong_raoti_shenxiang` | NOT_STARTED |

## 本次环境验证结果

- 工作区维护清理了原构建缓存，重新克隆代码成功。
- Gradle wrapper直连下载失败（Network is unreachable）；用当前环境已有代理下载Gradle 8.8成功，并开始恢复Forge/Minecraft依赖。
- 现有bundled dependencies已通过tools/art/make_local_repo.py恢复到本地仓库。
- 当前只有Java运行时、缺少javac和Xvfb。系统包安装因setgroups/seteuid权限错误失败；没有禁用系统安全限制。
- loopback socket检查通过，不沿用过去的socket禁用结论。
- 无法完成要求的图形客户端验收，因此中止本次仍在依赖准备阶段的构建（退出130）；没有本轮compileJava/build/GameTest通过结果，没有本轮客户端截图。
- 本次只同步已有main成果并核对缺口；未越过用户文件规定的实机门槛开发新条目。

继续条件：在可运行游戏的环境完成最新构建单机/双人验收；或者用户明确同意先实施后续代码、把实机验收留给本地，同时继续保留PARTIAL状态。
