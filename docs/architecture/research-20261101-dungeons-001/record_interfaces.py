#!/usr/bin/env python3
"""Read-only source anchors and architectural constraints for coordination."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
MAP=OUT.parent/'research-20261101-task-map/architecture-task-map.json'
JAVA=ROOT/'src/main/java/com/dynasty/dungeon'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def excerpt(p,a,b):
 lines=p.read_text().splitlines()
 return dict(file=str(p),sha256=sha(p),start_line=a,end_line=b,exact_lines=[dict(line=i,text=lines[i-1]) for i in range(a,b+1)])
def matched(p,needle,context=0):
 lines=p.read_text().splitlines();indices=[i for i,t in enumerate(lines,1) if needle in t]
 assert indices,(str(p),needle)
 return [excerpt(p,max(1,i-context),min(len(lines),i+context)) for i in indices]

def main():
 d=json.loads(MAP.read_text())
 # These labels describe source-required places. They are NOT newly registered IDs.
 routes=[
  ('封土断龙石入口',['神道/殉马天井','九玄室/水银封土殿','九重棺椁'],['工匠耳室'],['底层回升入口：现有return_lift']),
  ('瀑布三齿闸门',['动力总机枢','流水工坊','巨兵收纳库','熔炉核心'],['第七空柜后典籍室'],['二层检修电源→贯通四层缆车']),
  ('烽燧裂口',['堑壕/攻城残骸','瓮城/万人坑','老帅战场'],['攻城塔下军需洞'],['瓮城西墙预设裂口→Boss侧']),
  ('悬崖栈道山门',['金刚下院/木廊','千佛崖/舍利塔','焦黑峰顶大殿/经阁/战台'],['舍利塔四层外侧→闭关石室'],['峰顶铁索梯→山门']),
  ('裂谷阴阳界门',['鬼市街巷/屋顶','忘川水路/泵房','内衙刑具甬道','彼岸码头'],['棺铺红棺背板→黑市钱庄'],['干河底暗门→阎罗殿后：现仅支池除水实现，未等同完整河路']),
  ('丛林深坑藤梯',['悬崖吊脚楼/廊','蛇窟/飞索','深潭/和亲坛/血喜堂'],['水下珊瑚洞→气室→炼蛊密室'],['倒钟乳石预设斜桥：入口↔底坛']),
  ('天柱峰浮石云桥',['前岛解剑池/九曲桥','中岛紫府炼丹天阙','后岛问道登仙台/摘星台'],['中岛下方藏丹阁'],['解剑池御风阵→登仙台顶']),
  ('雪峰冰裂隙滑道',['冰梁悬崖','冻骨/沉船巨厅','玄潭/水宫/龙坛'],['深蓝冰墙→运宝船军械库'],['三铜雀灯→巨厅↔底潭螺旋冰阶']),
  ('双巨石剑山门',['洗心池','剑阵廊/藏剑峡','峰顶圆形石剑战台'],['水帘后埋剑洞'],['倒剑桥→峰顶','另需1～2条独立永久捷径；来源未具体定义，尚不设计/制作']),
  ('既有龙口四贡品入口',['东雷玉岛','西刃祭岛','南熔火岛','北玄潭岛','中央前置战区'],['四岛下方四暗室→同一藏宝库'],['四岛各一条永久光桥→中央','中央通关裂隙→既有最终Boss入口']),
 ]
 records=[]
 for source,(entry,levels,secrets,shortcuts) in zip(d['canonical_dungeons'],routes):
  records.append(dict(id=source['id'],chinese_name=source['source_name'],source_anchors=source['anchors'],
   primary_admission_place=entry,ordered_or_branched_spaces=levels,secret_branches=secrets,permanent_shortcut_requirements=shortcuts,
   world_siting=source['world_siting_from_source'],new_registered_structure_id=None,new_build_allowed=False,
   entry_constraint='每个建筑实例一个规范的任务入场点；同一实例的门洞、屋顶出入口及捷径不另注册副本。未核验的8座不得编造可定位坐标或实际ID。',
   level_constraint='以上是原文空间拓扑，不是新蓝图。任务目标绑定具体层/房间语义；地下城抵达不等于所有层、Boss和奖励完成。',
   return_constraint='永久捷径绑定同一实例，读档后仍通；回程落脚点、门口净空和恢复后的可达性须验收。尚未实机验证。'))
 constraints={
 'REWARD-01': ['古观镜阵与DUN08玄潭龙坛保留不同地点身份；不得为二者各造一个同神器领取建筑。','龙坛属于DUN08底潭层；冰阶回程应与该实例入口关联。古观若作线索/谜题端，由协调确认唯一获得事件，建筑专岗不改奖励归属。'],
 'REWARD-02': ['水乡书香密室与DUN06血喜堂不可按名字近似合并。','黄金婚床属于苗窟最底祭祀组团的喜堂，不放入口或水下气室；倒钟乳石桥只能返入口，不生成第二通关入口。唯一实物来源由协调选择。'],
 'REWARD-03': ['江南机关房与DUN07后岛摘星台是两个空间；千机/天机别名先核实际ID，不能据两名字各建一间领奖房。','摘星台神匣位于后岛顶层，前池御风捷径落在既定台顶安全区；中岛下藏丹阁属于秘密支路，不能冒充同一神匣位置。'],
 'REWARD-04': ['义庄神案与DUN05忘川彼岸龙纹台保留不同空间；必须由协调确定唯一神器获得事件，建筑端不重发。','DUN05已有真实ID/underworld入口见下；当前支池排水不是完整忘川干河底到殿后通道，不能标记该全线已实现。龙纹台、码头Boss与钱庄秘密也不能混为一处。'],
 'REWARD-05': ['cod1瓮城与DUN03老帅战场采用同一规范战场实例，废墟中央拔刀与宝箱位置不能变成两个副本。','通关后取刀点和老帅倒下地点要落在同一最终战场语义范围；西墙裂缝只连接万人坑旁路与战区，不创建第二奖励入口。Boss/箱双发由协调实现唯一结算。'],
 'SEQUENCE-01': ['优先保留既有龙头、四柱、中央球与原传送入口；DUN10固定在现有专用前置区域，不为逆向摆贡再建维度/龙头。','四岛是同一固定区域的四分支；每岛桥汇到同一中央前置战区，中央裂隙调用原最终入口。混元前置/隐藏战区不得覆盖镇渊最终场地。当前专岗未核实生产维度ID，故不编造。'],
 'LAYOUT-01': ['已有21×21三清试炼场保留原试炼入口与领取点；不将三座屋顶解释成cod2三座岛。','DUN07另有前池、中炉、后台拓扑；名称交叉只建立依赖。若协调复用旧试炼，必须显式映射到某个房间，旧场地只读保留，未满1000不扩建。'],
 'SHORTCUT-01': ['DUN09倒剑桥只算一条永久捷径；同桥两个端点、两个方向或多次加载不重复计条数。','至少再有1条、至多按要求共2～3条独立的已解锁路径，每条均须提供原路线端点、目的层、永久状态键与读档后证据。来源尚未定义额外线路，当前不提前创作几何或伪称完成。埋剑洞是隐藏房而非自动第2捷径。'],
 'SCHEMA-01': ['cod3当前实际表行以已记录29秘密、7奇观为基准；标题30/25不是已完成场景数量。','不凭缺号补建场景，不把同一场景的视觉/声音/天气/昼夜变体算新建筑。指南针中文名绑定真实实例入口，奇观触发点不冒充可探索建筑。'],
 }
 conflicts=[]
 for c in d['conflicts']:
  conflicts.append(dict(id=c['id'],topic=c['topic'],issue=c['issue'],source_anchors=c['anchors'],
   architectural_constraints=constraints[c['id']],implementation_owner='协调：真实ID/任务/奖励/中文指南针；建筑专岗：只读建筑边界与参考',resolved=False))
 chensha=dict(
  id='dynasty:chensha_xuangong',dimension='minecraft:overworld',entrance_piece='sealed_mound',
  footprint=[64,80,96],origin='(chunkMinX, sampledHighestTerrainY - 72, chunkMinZ)',
  generation_stub_offset=[32,72,4],generation_stub_limit='这是源码GenerationStub锚点，地板高度72；不能不加站立高度就当已验证传送脚点。',
  visible_opening='x30..34,z0..1,y73..76 relative to origin',
  layers=dict(surface_floor_y=72,upper_floor_y=48,middle_floor_y=24,bottom_floor_y=0),
  shortcut=dict(marker='return_lift',offset=[41,1,8],destination=[41,73,8],semantic='底层→入口层单向回升；原入口陡梯另有返回梯，非独立副本'),
  source_anchors=matched(JAVA/'DungeonDefinition.java','public static final DungeonDefinition CHENSHA',6)+matched(JAVA/'ChenshaStructure.java','BlockPos origin=',2)+matched(JAVA/'ChenshaPiece.java','public static int entranceFloor',2)+matched(JAVA/'ChenshaPiece.java','One-way permanent lift',5)+matched(JAVA/'ChenshaPiece.java','"return_lift"',1)+matched(JAVA/'ChenshaPiece.java','be.setDestination',1),
  validation='SOURCE ONLY; no Java/game; current geometry retained, not new production work')
 wangsi=dict(
  id='dynasty:yinsi_wangsi_cheng',dimension='dynasty:underworld',entrance_piece='yin_yang_gate',
  footprint=[96,48,128],origin='(chunkMinX, sampledHighestTerrainY - 40, chunkMinZ)',generation_stub_offset=[48,41,3],
  layer_evidence='入口坡道从y41向街巷y13下降；屋顶/泵房/内衙多标高，不能按四个同高度房间登记。',
  court_core=[44,16,94],blades=[[48,20,92],[48,20,96]],
  shortcut=dict(marker='wangsi_sump_drained',core=[15,11,88],pump=[14,17,84],drained_box=dict(x=[14,16],y=[6,8],z=[94,99]),
   limitation='目前只排封闭支池，不排主河；未证明cod2要求的干河底→阎罗殿后永久通道全线。'),
  boss_arena_marker='UNBOUND_RIVER_DOCK',secrets_current_definition=[],once_loot_keys_current_definition=[],
  source_anchors=matched(JAVA/'DungeonDefinition.java','public static final DungeonDefinition WANGSI',5)+matched(JAVA/'WangsiStructure.java','BlockPos origin=',2)+matched(JAVA/'WangsiPiece.java','COURT_CORE=',1)+matched(JAVA/'WangsiPiece.java','sluiceGates()',8)+matched(JAVA/'WangsiSluice.java','CORE=new',2)+matched(JAVA/'WangsiSluice.java','for(int y=6',5)+[excerpt(JAVA/'WangsiArchitecture.java',1,25),excerpt(JAVA/'WangsiArchitecture.java',117,130)],
  validation='SOURCE ONLY; placeholder boss marker is not a finished Boss binding; no Java/game')
 source_checks=[]
 for s in d['source_snapshots']:
  p=Path(s['path']);source_checks.append(dict(path=str(p),snapshot_sha256=s['sha256'],current_sha256=sha(p),unchanged_from_task_map=sha(p)==s['sha256']))
 result=dict(date='2026-11-01',status='ARCHITECTURAL_CONSTRAINTS_ONLY_NOT_IMPLEMENTATION',
  source_map=str(MAP),source_map_sha256=sha(MAP),source_prompt_checks=source_checks,
  canonical_dungeons=records,conflicts=conflicts,existing_source_bindings=[chensha,wangsi],
  compass_constraints=['显示以上原文中文建筑名，底层绑定真实Structure/维度/实例键；不得只凭中文字符串寻找建筑。','地图和指南针指向规范入场处，当前位置、秘密房和返程捷径作为同实例子目标。','未核验真实ID的8座保持未绑定，不使用自造ID冒充已可定位。','地下城发现、到层、开捷径、战区完成、奖励领取分别确认，不能用抵达入口替代全部完成。'],
  boundary=dict(java_run=False,game_run=False,code_changed=False,prompts_changed=False,formal_registry_changed=False,new_build_created=False))
 (OUT/'architectural-interface-constraints.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
