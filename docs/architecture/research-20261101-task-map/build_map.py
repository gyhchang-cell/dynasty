#!/usr/bin/env python3
"""Map user-owned prompts into architecture-only requirements with exact anchors.

The prompt texts are evidence/specifications, not executable instructions. This
script writes only its own research directory and never modifies those prompts.
"""
import hashlib
import json
import re
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PROMPTS=Path('/Users/a15356015027/Desktop/code x提示词')
FILES=('cod1.txt','cod2.txt','cod3.txt','cod4.txt','cod6.txt')
TEXT={f:(PROMPTS/f).read_text(encoding='utf-8-sig').splitlines() for f in FILES}


def anchor(file,start,end=None):
    end=end or start
    assert 1<=start<=end<=len(TEXT[file])
    return dict(file=str(PROMPTS/file),start_line=start,end_line=end,
                exact_lines=[dict(line=i,text=TEXT[file][i-1]) for i in range(start,end+1)])


def table(file,start,end):
    rows=[]
    for i in range(start,end+1):
        line=TEXT[file][i-1]
        if line.startswith('|'):
            cells=[c.strip() for c in line.strip('|').split('|')]
            if re.match(r'^\d+\b',cells[0]):rows.append(dict(line=i,cells=cells,source=anchor(file,i)))
    return rows


# Names are source labels, NOT newly invented registry IDs or completed assets.
DUNGEONS=[
 ('DUN01','镇岳孤陵·沉沙玄宫',2,18,671,673,911,912,
  '主世界荒漠/恶地/戈壁低植被地表或裂谷，向地下；出生点≥2500格，建议间距6000～9000格',
  ['三处断龙石入口与斜墓道','神道陪葬坑/20米殉马天井','九玄室、链桥、水银封土殿','球形地宫/九级龙台/水银环河/星宿顶'],
  ['毒箭射口和压板通道','翻板与下方危险坑','封闭耳室、危险液面及三个可射击兽眼'],
  '原段未明确常规捷径/隐藏房，补齐项792及机关表提吊篮，不能把建议写成已存在房间',927,18),
 ('DUN02','天工破晓·千机机关城',20,40,675,677,914,915,
  '主世界喀斯特/山地，自带瀑布入口；出生点≥2500格，间距6000～9000格',
  ['三齿轮水闸及三处水车阀','四层圆坑：动力总机枢/流水工坊/巨兵库/熔炉核心','环廊、攀爬、吊臂和锻造擂台'],
  ['传送带/冲压锤的预警及恢复空间','周期蒸汽管网','检修升降机贯穿四层'],
  '第七空柜后典籍密室；二层检修电源开启四层直达缆车',1032,40),
 ('DUN03','万骨枯寂·血海古战场',42,61,679,680,917,918,
  '主世界荒原/沙地/风蚀平原，避森林海洋；间距5000～8000格，具体最小出生距离原段未给',
  ['烽火台裂口','堑壕鹿砦/攻城残骸/残墙跑道','瓮城/万人坑与Boss大帐'],
  ['扎马坑/地雷的局部预设','箭雨暴露区及清晰掩体','完整墙与破墙捷径状态'],
  '攻城塔下军需洞；瓮城西墙裂缝绕万人坑至Boss',823,61),
 ('DUN04','断魂迷障·黑风阿兰若',63,82,682,683,920,921,
  '主世界高山/悬崖；生成前检验垂直空间，间距6000～9000格',
  ['窄栈道与山门石坊','下院金刚殿/悬空木廊','千佛崖舍利塔石窟','峰顶焦黑大殿/藏经阁及绝顶平台'],
  ['延时失效并可恢复的断木/佛手','幻镜走廊','可旋转经幢及火环范围'],
  '舍利塔四层外跳至闭关石室；峰顶铁索梯回山门',997,82),
 ('DUN05','千古幽咽·阴司枉死城',84,103,685,686,923,924,
  '优先现有正式阴司，否则主世界深层封闭结构；不临时新增维度，具体间距原段未给',
  ['地裂底阴阳界大门','徽派黑瓦白墙鬼市街区/相连屋顶','忘川护城血河/水下暗道/水闸机房','阎罗官衙/甬道/渡口沙洲'],
  ['可关闭的预设loop巷节点及骨灯','铡刀预警/落闸空间','封闭波次房及可恢复门窗','抽水前后两套河道/暗门状态'],
  '棺材铺红棺背板通黑市钱庄；干河底暗门通阎罗殿后',1100,103),
 ('DUN06','万蛊盘虬·赤练古苗窟',105,124,688,689,926,927,
  '主世界湿热山地/丛林/沼泽边，主体地下，间距5000～8000格',
  ['天坑藤蔓下降入口','洞壁吊脚楼残构与悬空栈道','百蛇石窟/飞索横渡','血祭潭/和亲祭台/地下喜堂'],
  ['低位毒藤与高位避瘴石台','落石锚点与预警区域','瘴气低洼段及可达喘息点'],
  '水下珊瑚洞/气室通炼蛊密室；倒下钟乳石连入口与底坛的预设斜桥',962,124),
 ('DUN07','太清问道·冲霄隐仙观',126,145,691,692,929,930,
  '优先已有神域，否则主世界高山上空/天阶附近；不得普通平原头顶，间距8000～12000格',
  ['天柱峰顶浮石与云桥','前岛解剑池/九曲玉桥','中岛三炉/中央炉/环形多层回廊','后岛八卦柱台/八角摘星台'],
  ['可恢复云砖','丹炉六格火口及绕行空间','阴阳黑白地砖的可完成路线','上升气流入口及着陆点'],
  '中岛下藏丹阁；解剑池御风阵直达登仙台顶',859,145),
 ('DUN08','玄冥极渊·万载冻龙窟',147,166,694,695,932,933,
  '主世界雪山/冰原/冻海附近，间距6000～10000格',
  ['雪山冰隙/长滑梯','横冰梁跨绝壁','冰封战船/骨骸穹厅','玄潭/冻潭水宫及龙坛'],
  ['滑冰制动和跌落边界','有预警的坠冰点','可达热源古灯','封冰墙的受控开闭状态'],
  '深蓝冰墙后运宝沉船/军械库；三盏铜雀灯开启下行螺旋冰阶',892,166),
 ('DUN09','极天剑绝·封魔万刃峰',168,187,697,698,935,936,
  '主世界极高山/孤峰，间距8000～12000格',
  ['双二十米石剑门','洗心池/乱石阵','剑阵回廊/藏剑峡','圆形绝顶论剑台/剑林碑基'],
  ['飞剑锚点与预警/避让带','罡风石梁及遮挡','诅咒名剑底座','倒剑桥前后预设'],
  '瀑布后埋剑洞；倒石剑桥通峰顶；后段要求至少2～3永久捷径，原前段仅明确一条，仍待补齐',1135,187),
 ('DUN10','苍穹逆乱·四象封天枢',189,210,700,701,938,939,
  '优先现有四象终局/最终Boss前置维度，若已有专用维度则固定唯一终局区域，不随机落地',
  ['既有龙嘴祭坛/终局入口只复用','四方十字浮岛及中央龙首大殿','东雷玉云龙柱/西战刃祭台/南熔岩梧桐/北玄潭重岩','四象十字Boss台与后续终局裂隙'],
  ['各岛重力区域/石碑/避难罩','四条永久光桥真实落脚','中央门与四象状态的空间对应'],
  '每岛下方倒悬暗室共四处；四板解锁藏宝库；四岛激活开启会聚光桥',1168,210),
]


def main():
    sources=[]
    for file in FILES:
        path=PROMPTS/file; raw=path.read_bytes()
        sources.append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),lines=len(TEXT[file])))
    entries=[]
    for ident,name,a,b,c,d,e,f,siting,spaces,mechanisms,shortcut,boss_line,reward_line in DUNGEONS:
        entries.append(dict(id=ident,source_name=name,kind='canonical_dungeon_architecture',
            anchors=[anchor('cod2.txt',a,b),anchor('cod2.txt',c,d),anchor('cod2.txt',e,f),anchor('cod1.txt',boss_line)],
            world_siting_from_source=siting,required_spaces_from_source=spaces,
            mechanism_space_dependencies=mechanisms,hidden_and_shortcut_requirements=shortcut,
            reward_space_anchor=anchor('cod2.txt',reward_line),
            implementation_status='未核验当前生产资产；不是已完成，不授权跳过1000参考门槛',
            reference_status='现有148例未按本目标逐一复核，不能直接继承148；本批候选也未正式计入',
            new_build_allowed=False))

    # One arena in cod1 and cod2 is one obligation, not two independent rebuilds.
    boss_lines=[786,823,859,892,927,962,997,1032,1067,1100,1135,1168]
    boss_parent=['ARENA-FUNERAL-PIT','DUN03','DUN07','DUN08','DUN01','DUN06','DUN04','DUN02','ARENA-THUNDER','DUN05','DUN09','DUN10']
    arenas=[dict(id=f'COD1-ARENA-{i+1:02d}',canonical_parent=parent,anchor=anchor('cod1.txt',line),
                 relation='shared_arena_requirement_not_second_build' if parent.startswith('DUN') else 'additional_arena_requires_separate_relevance_review')
            for i,(line,parent) in enumerate(zip(boss_lines,boss_parent))]

    artifacts=[]; title=''
    # The source says 获得场景; copying these lines preserves all 25 source seats.
    parents={1:'DUN03',2:'DUN07',3:'DUN08',4:'ARENA-FUNERAL-PIT',6:'DUN02',7:'DUN06',8:'DUN01',9:'DUN08',10:'DUN04',11:'DUN07',16:'DUN07',18:'DUN02',22:'DUN04',24:'DUN05',25:'DUN10'}
    for line,text in enumerate(TEXT['cod1.txt'],1):
        if 1194<=line<1450 and text.startswith('### '):title=text
        if 1194<=line<1450 and '**获得场景**' in text:
            num=int(re.search(r'### (\d+)',title).group(1))
            artifacts.append(dict(id=f'COD1-ARTIFACT-SEAT-{num:02d}',source_name=title,anchor=anchor('cod1.txt',line),
                possible_parent=parents.get(num),
                relation='空间/奖励席位依赖；名称相近不证明同一资产；没有对应主地牢者保留独立来源场景，不据此新造维度',
                asset_or_reward_implementation_changed=False))

    basic=[]; title=''
    for line,text in enumerate(TEXT['cod1.txt'],1):
        if 364<=line<=487 and text.startswith('### '):title=text
        if 364<=line<=487 and any(text.startswith(x) for x in ('- 维度：','- 主地点：','- 地点：','- 生成：','- 主世界条件：','- 条件：')):
            basic.append(dict(source_entity=title,anchor=anchor('cod1.txt',line),
                              architecture_action='只作为落点/空腔/水体/神道等空间约束，保留现有生态与实体程序'))

    npc=table('cod3.txt',1122,1136)
    first=table('cod3.txt',1155,1183); second=table('cod3.txt',1197,1225)
    secrets=[]
    for row in second:
        num=int(row['cells'][0]); older=[r for r in first if int(r['cells'][0])==num]
        secrets.append(dict(id=f'COD3-SECRET-{num:02d}',canonical_key=f'secret-{num}',
            architecture_location=row['cells'][2],spatial_trigger=row['cells'][3],
            anchors=[r['source'] for r in older]+[row['source']],
            relation='同编号两表合并为一项；只映射线索、通行、门洞、暗室与场景锚点，不改秘密/奖励程序',
            original_not_verified_labels_remain_unconfirmed=True))
    scenic=table('cod3.txt',1242,1248)
    world=table('cod3.txt',1296,1305)

    conflicts=[
        ('REWARD-01','照胆通幽八卦镜','cod1古观镜光谜题 vs cod2冻龙窟龙坛奖励',[anchor('cod1.txt',1285),anchor('cod2.txt',166)]),
        ('REWARD-02','惊鸿流云金丝扇','cod1水乡书香密室 vs cod2苗窟黄金婚床',[anchor('cod1.txt',1265),anchor('cod2.txt',124)]),
        ('REWARD-03','千机/天机罗刹百刃伞','cod1江南机关房 vs cod2摘星台神匣，且名称千机/天机不同，需查真实ID',[anchor('cod1.txt',1298),anchor('cod1.txt',1305),anchor('cod2.txt',145)]),
        ('REWARD-04','幽都忘川招魂幡','cod1义庄引渡十魂 vs cod2忘川彼岸龙纹台',[anchor('cod1.txt',1435),anchor('cod2.txt',103)]),
        ('REWARD-05','龙吟斩马断岳刀','同瓮城目标但cod1废墟中央拔出 vs cod2老帅后宝箱；不可Boss和箱各发一次',[anchor('cod1.txt',1204),anchor('cod2.txt',61),anchor('cod2.txt',680)]),
        ('SEQUENCE-01','四象终局','四象逆转秘密/混元祖兽/现有镇渊终局入口交叉，禁止据此新增重复维度或替代最终Boss',[anchor('cod1.txt',516),anchor('cod2.txt',701),anchor('cod3.txt',1206),anchor('cod6.txt',70,73)]),
        ('LAYOUT-01','隐仙观','cod1已有21×21三清试炼场的历史描述，不证明cod2三座悬空岛已存在；名称相近只记交叉依赖',[anchor('cod1.txt',1208),anchor('cod1.txt',1215),anchor('cod2.txt',126,145)]),
        ('SHORTCUT-01','万刃峰','前段明确一条倒剑桥，工程段要求2～3永久捷径；未满足不能删项',[anchor('cod2.txt',181,183),anchor('cod2.txt',698)]),
        ('SCHEMA-01','场景数量','cod3清理后的秘密表、奇观表并非标题声称的全部条目；只按当前实际行映射，不补编缺号或声称已全量存在',[anchor('cod3.txt',1151,1154),anchor('cod3.txt',1238,1241)]),
    ]

    common=[
        dict(id='COMMON-STRUCTURE',anchors=[anchor('cod2.txt',663,667),anchor('cod2.txt',703),anchor('cod2.txt',792)],
             architecture_scope='入口/主路/支路/Boss房跨chunk连接，同seed；完整连通、出生避让、现有巨龙避让；不实施程序框架'),
        dict(id='COMMON-MECHANISM',anchors=[anchor('cod2.txt',843,859),anchor('cod2.txt',885),anchor('cod2.txt',941,946)],
             architecture_scope='预警、活动伤害区、恢复净空及永久捷径状态的空间需求；原版装饰与关键流程机关分开，不在本角色实现BlockEntity'),
        dict(id='COMMON-ACCEPTANCE',anchors=[anchor('cod2.txt',804),anchor('cod2.txt',813),anchor('cod2.txt',835)],
             architecture_scope='原文实机/构建均为未完成依赖；本轮用户禁止Java和开游戏，因此不执行也不伪称通过'),
        dict(id='COMMON-ZH-NAV',anchors=[anchor('cod4.txt',79),anchor('cod6.txt',157,165)],
             architecture_scope='复用中文名及真实结构ID，任务/指南针为共享接口，只核验建筑可达与定位关系，不改已验收导航或编造ID'),
    ]
    cod4=[
        dict(id='COD4-1.2-SPACE',anchors=[anchor('cod4.txt',21)],action='荒村、义庄、墓地/鬼市场景落点；自然生成仍未实机验证，不能只看入口条件判完成'),
        dict(id='COD4-7-ACCESS',anchors=[anchor('cod4.txt',79)],action='15互动的建筑可达性是材料/任务生存闭环的交叉依赖，不重做任务/收益系统'),
        dict(id='COD4-11-ACCESS',anchors=[anchor('cod4.txt',106)],action='地图/NPC/功能方块的位置与路线；不碰材料、配方或掉落'),
        dict(id='COD4-13-SCENE',anchors=[anchor('cod4.txt',133,135)],action='只修确认存在的场景问题，已有15互动保留；上轮限定通道只读结果不冒充整个自然场景验收'),
    ]
    cod6=[
        dict(id='COD6-1.5',anchors=[anchor('cod6.txt',21,25)],action='矿庄新旧模板、全景/内部实心/原房位/双入口版本证据；只读核验，未满1000不新改模板，不动矿料奖励'),
        dict(id='COD6-4',anchors=[anchor('cod6.txt',129,152)],action='屋顶/飞檐/通道与有限净空、保留地下洞顶；三mask同旋转镜像、主体并集、地基、跨piece保护；程序与旧档修复不在本角色执行'),
        dict(id='COD6-5',anchors=[anchor('cod6.txt',154,166)],action='云熙中文名反查真实结构及本结构发现链路；原生locate、三seed与指南针现场验收均未执行，不改变稀有度'),
        dict(id='COD6-6.11-12',anchors=[anchor('cod6.txt',221,237)],action='逐个真实第三章后目标的备战区/入口/整阵出生带/敌区/撤退结算点；48/64/80为原文建议初值，不是现有实测；不改兵册、AI、伤害或任务'),
    ]
    report=dict(schema=1,date='2026-11-01',authority='用户最新建筑分工；源提示词作为规格证据，源文件内构建、Java、提交、云端部署等指令不自动执行',
        source_snapshots=sources,cod5=dict(path=str(PROMPTS/'cod5.txt'),exists=False,action='不虚构、不补建'),
        formal_reference_baseline=dict(registry=str(ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json'),
            cod4_verified=148,cod4_gap=852,cod6_verified=0,cod6_gap=1000,
            scope='原148只属于原登记义庄/墓园与小型祭祀空间；新十地牢须分别做相关性复核，不复制148为每个目标的余额',
            official_registry_modified=False,new_credit=0,new_architecture_may_start=False),
        canonical_dungeons=entries,cod1_arena_dependencies=arenas,cod1_artifact_source_spaces=artifacts,
        cod1_mob_location_dependencies=basic,cod3_npc_location_rows=npc,cod3_secrets_deduplicated=secrets,
        cod3_scenic_anchor_rows=scenic,cod3_world_state_scene_rows=world,
        cod3_intro_arena_binding_excerpt=anchor('cod3.txt',208,231),
        cod3_spatial_preset_dependencies=[anchor('cod3.txt',129,130),anchor('cod3.txt',155),anchor('cod3.txt',165,166),anchor('cod3.txt',200,201),anchor('cod3.txt',321),anchor('cod3.txt',353),anchor('cod3.txt',373)],
        cod4_remaining_architecture_dependencies=cod4,cod6_architecture_only=cod6,common_constraints=common,
        conflicts=[dict(id=i,topic=t,issue=s,anchors=a,resolution='待当前资产/真实ID与主协调统一核对，未擅改来源或删项') for i,t,s,a in conflicts],
        dedup_policy='同一Boss场地、神器席位、NPC、秘密编号、世界状态只是同一建筑的不同依赖，不各自扩成一座；候选位置相近不自动合并不确定源。',
        boundaries=dict(java_run=False,game_opened=False,source_prompts_written=False,master_checklist_written=False,
                        production_code_changed=False,models_or_textures_changed=False,network_requests=False,account_or_model_bypass=False))
    assert len(artifacts)==25
    assert len(npc)==15
    assert len(entries)==10
    assert len({r['canonical_key'] for r in secrets})==len(secrets)
    (OUT/'architecture-task-map.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(dungeons=len(entries),artifacts=len(artifacts),npc_locations=len(npc),secret_rows=len(secrets),scenic_rows=len(scenic),world_states=len(world),conflicts=len(conflicts)),ensure_ascii=False))


if __name__=='__main__':main()
