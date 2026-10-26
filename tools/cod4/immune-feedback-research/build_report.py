"""Render a human-auditable progress report from curated records; grants zero research credit."""
from ledger import O,B,R,verify
import json,hashlib,datetime
verify()
rows=json.loads((O/'reviewed.json').read_text());sources=json.loads((O/'sources.json').read_text())
header='''# Boss Immune / 受击文本：实现研究进度

状态：**研究进行中，未达到1000处，尚未完成本项研究。**

本报告只汇总已经实际读取全文方法及自有调用链的记录。下载项目数、Java文件数、候选方法数、同链包装、平台移植、相同渲染链的颜色/数字/动画变体均不自动计数。机器校验只检查引用哈希和语义键唯一，语义去重仍由逐条人工式源码审阅承担，不能靠键不同自证独立。

原需求依据：本项目 `docs/cod4/request.txt:348` 的 Boss Immune 行要求“免疫”灰字、弹开微光、嗡鸣、不受此次控制影响、不刷屏；`:351` 要求服务端决定类型和目标、客户端播放。`:270–271` 普通阴阳体质免疫没有灰字要求，保留现有 type9 回执边界。不要把“纹丝不动”扩展为冻结Boss正常AI、走路或所有原生动作。

授权边界：仅本研究docs/tools目录；未启动游戏、未运行上游源码、未改正式Java/资产/原清单或待办。本文静态观察不能证明画面可辨识、声音合适或两端实际同步。文字及语义接入由协调岗承担，不转交模型制作；声音优先已有原版合适资源，不强制新录音。

'''
count=f'**有效语义去重：{len(rows)}/1000；缺口：{1000-len(rows)}。** 固定版本已取得完整或选定源码的项目{sum(bool(x.get("commit")) for x in sources)}个，项目数量不计研究数。正式最小设计与静态验收条件尚未交付，待足额后综合，不提前实施。\n\n'
observations='''## 已获得的具体认识（研究观察，未定案设计）

- 血量差值数字只能看到变化；零伤、抵抗、拒控需有明确语义生产点。Mine and Slash 有明确 nullified 回执，Dummy 则展示“无限血但仍可有实际伤害事件数字”的不同情形。
- `hurt=false` 不能单独等同于Boss免控：共享伤害桶、边界/阶段、方向盾、自源排除各不同；Harbinger与Ignis还能在最终拒绝前生产动作或声音。减到0.1、减半等不应标作完全免疫。
- 动作栏本地化提示不是目标头顶浮字。Leviathan直接攻击者/投射物owner的差别会改变是否得到提示。
- 出生点快照、跟随目标、屏幕投影是不同锚定实现；包里有entityId不等于有维度/代际防护。缺失实体、换世界和实体ID复用仍须逐链核查。
- 粒子总容量、数字横向分槽、累加伤害和按目标节流/事件去重不是一件事。当前样本不能凭总上限宣称“不刷屏”。
- 深度必须看实际提交模式和GL状态。M&S RenderUtils强制GL_ALWAYS，HUD投影链也无世界深度；Damage Engine的注释不能覆盖实际SEE_THROUGH/NORMAL提交分支。
- GUI渲染时钟不能替代独立tick寿命。Simple Combat Indicators使用partialTick差值递增age，静态不足以保证低帧率真实到期时间。
- 已发现死代码/未接活路径，明确0计数；普通玩家体质不因Boss需求而新增灰字门槛。

## 有效记录索引

| 序号 | 语义键 | 项目 / 固定提交 | 首个来源（完整引用见下文） |
|---|---|---|---|
'''
lines=[header,count,observations]
for i,row in enumerate(rows,1):
 ref=row['source_refs'][0]
 lines.append(f'| {i} | `{row["id"]}` | {row["repo"]} / `{row["commit"][:12]}` | [{ref["source_path"]}:{ref["lines"][0]}]({ref["url"]}) |\n')
lines.append('\n## 逐项观察与边界\n\n')
for i,row in enumerate(rows,1):
 lines.append(f'### {i}. {row["id"]}\n\n')
 for label,key in [('全文调用链','full_chain_observation'),('实际观察','concrete_observation'),('与本任务的关系','application_to_boss_immune'),('覆盖边界','limitations')]:lines.append(f'**{label}：** {row[key]}\n\n')
 lines.append('固定来源：\n\n')
 for ref in row['source_refs']:
  a,b=ref['lines'];lines.append(f'- [{ref["source_path"]}:{a}–{b}]({ref["url"]})；SHA256 `{ref["file_sha256"]}`。\n')
 for ref in row.get('auxiliary_refs',[]):lines.append(f'- 辅助（0计数）：[{ref["repo"]}/{ref["source_path"]}]({ref["url"]})；{ref["note"]}\n')
 lines.append('\n')
lines.append('''## 继续研究入口

`reviewed.json` 为有效台账；`candidate-index.json` 为词法筛选线索，全部0计数，不能将其总量当已研读；`candidates.json` 记录实际读过但未满足完整/相关/独立门槛的候选与排除原因。`semantic-dedup.json` 记录合并依据。`sources.json` 保存固定版本及逐文件SHA；源码全文位于对应tools/sources目录。

后续优先补明确的Boss拒控/拒伤回执、已有世界文字组件的世界切换/实体销毁处理、逐目标或逐事件节流实现。Goety monolith 已读拒绝→原生entity event→shieldTime→渲染，但empowered赋值入口尚未核实，仍0计数；不把它直接报成可运行范例。不会用纯图形/基础网络库或同链包装补足1000。
''')
(O/'REPORT.md').write_text(''.join(lines))
print(json.dumps({'report':str(O/'REPORT.md'),'effective':len(rows),'formal_gate':False},ensure_ascii=False))
