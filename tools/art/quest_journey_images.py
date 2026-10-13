"""Original code-drawn FTB operation diagrams, based on local game contracts.

These are GUI instruction figures, not entity/item textures or copied pack art.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'src/main/resources/assets/dynasty/textures/gui/quests/journey'
FIGURES={
 'altar':('祭坛摆放 · 同一高度', ['玉　空　玉','空　坛　空','玉　空　玉'], ['坛＝法阵·祭坛；玉＝玉石块','手持对应信物，右键中间祭坛']),
 'qimen':('奇门机括 · 无序合成',['精钢 ×1','铜锭 ×1','红石粉 ×1'],['放进合成格 → 奇门机括 ×2','留机括做兵器，再按需补钢索']),
 'bronze':('基础青铜 · 无序合成',['铜锭 ×3','铁锭 ×1','青铜锭 ×4'],['铜与铁放入合成格','箭头右侧是产物数量']),
 'portals':('往返准备 · 门成对带走',['主世界：放第一座','右键进入目标维度','安全处：放第二座'],['对面不会自动造回程门','归乡符回主世界出生点附近']),
 'infusion':('炼物入器 · 操作示意',['装备入槽','材料 ×2','经验 3级'],['选择炼入位并确认；容量3～5','替换或移除看界面；移除耗1级经验']),
 'exam':('科举 · 从试卷到答题',['纸 + 墨囊','合成科举试卷','手持右键答题'],['答对至少一次才算科举中第','仅把试卷放背包不算答题']),
 'army':('虎符 · 从兵册到出阵',['募兵台招募兵员','右键虎符选阵型','确认出阵'],['必须实际召出部队才记录','潜行右键的威慑不算列阵']),
 'compasses':('导航 · 两种罗盘分工',['自然指南针：群系','探险者指南针：建筑','只搜当前维度'],['主手自然指南针 + /dynasty_find','追踪栖息地不保证怪物立即刷新']),
 'curios':('饰品佩戴 · 槽位示意',['打开饰品栏','选择对应分类槽','拖入已获得的饰品'],['放在背包不会生效','万能槽可放不同类别；看属性取舍']),
 'smithing':('装备进化 · 锻造台',['图纸（模板）','上一阶装备（底材）','进化材料（添加物）'],['按制作节点配方放入锻造台','升级会消耗底材；保留装备NBT']),
 'locks':('机关盒 · 朝向与等待',['北站立 → 东潜行','南站立 → 西潜行','前三段各40秒'],['末段至少半秒；总计至少2分钟','方向错会复位，按现场提示操作']),
 'sword_moves':('剑痕石壁 · 晴朗露天夜晚',['朝北向东移，挥剑','朝北向西移，挥剑','向北移，转东挥剑'],['每式间隔40秒，总计至少2分钟','持续持同一把主手剑，别远离石壁']),
 'well':('古井供水 · 一桶可以重用',['装满水桶','供水后返空桶','再装水，重复7次'],['总计至少3分钟，空桶不计','第七次完成后按现场提示取奖励']),
 'boat':('鬼市小舟 · 点香后再交付',['手持安魂香请船夫','询问渡口，等2分钟','手持朱砂再交互'],['给船边留站立空间','完成后取得旧竹简']),
 'rescue':('义庄救人 · 先辨生死',['观察微弱呼吸','等待2分钟','手持治疗药水救助'],['消耗一瓶，返还空瓶','牛奶清自身负面不能代替救人']),
 'bellows':('风箱烧炼 · 三格内',['准备熔炉与待炼物','输出留空，带木炭','等30秒，再次交互'],['也支持烟熏炉与高炉','推动实际烧炼后取得铁粒']),
 'compass_recipe':('两种罗盘 · 工作台俯视',['自然指南针：原木','探险者指南针：圆石','中间：原版指南针'],['上下左右放材料，四角留空','自然找群系；探险者找建筑']),
 'refining':('饰品淬炼 · 铁砧槽位',['左槽：单件饰品','右槽：当前材料','取出结果：等级+1'],['经验与材料按每次操作扣除','佩戴才生效；进化保留淬炼']),
 'wind_recipe':('御风符 · 普通材料无序合成',['普通羽毛 ×2','丝绸 ×1','符纸 ×1'],['三种材料放入合成格 → 御风符 ×1','普通羽毛来自鸡；神羽路线可选']),
 'academy_materials':('书院采料 · 地面与红柱',['汉白玉：白色地面','朱红柱：红色立柱','带镐采集，不必精准采集'],['示意位置，实际院落布局可能不同','装饰祭坛不能替代法阵祭坛']),
 'army_stage':('军阵关卡 · 从购兵到开战',['科举中第，募兵台买兵','虎符选关卡，入场后编队','部署至少一名，再点开战'],['通关以关卡结算为准，战损会保留','野外击杀不能替代军阵胜利']),
 'brewing':('酿造入门 · 先做粗制药水',['左槽：烈焰粉燃料','上槽：下界疣','下槽：水瓶，一瓶即可'],['等酿造完成，取出粗制的药水','燃料与酿造材料不能放反']),
 'glass_bottle':('玻璃瓶 · 工作台摆成V形',['玻　空　玻','空　玻　空','空　空　空'],['玻璃 ×3 → 玻璃瓶 ×3，留一瓶即可','熔炉烧沙取玻璃；空瓶右键水源装水']),
 'target_recipe':('标靶 · 工作台中央放干草',['空　红　空','红　草　红','空　红　空'],['红＝红石粉 ×4；草＝干草块 ×1','小麦 ×9 可合成干草块；四角留空']),
 'infusion_table':('炼入台 · 工作台摆法',['银　玉　银','青　工　青','青　青　青'],['银锭 ×2、玉 ×1、青铜锭 ×5','工＝工作台 ×1；合成后放置、右键打开']),
 'writing_recipe':('书与笔 · 三种材料无序合成',['书 ×1','墨囊 ×1','羽毛 ×1'],['三种材料放入合成格 → 书与笔 ×1','使用前先记录持有；正式科举另用试卷']),
}

CARD_COPY={
 'dynasty_story_01':('01  安家起步','工具 · 照明 · 自保'),
 'dynasty_story_02':('02  罗盘与工坊','导航 · 材料 · 配装'),
 'dynasty_story_03':('03  入仕平叛','科举 · 调兵 · 破阵'),
 'dynasty_story_04':('04  远赴天朝','备好回程 · 进入龙庭'),
 'dynasty_story_05':('05  幽冥帝陵','探陵 · 斩帝 · 战利品'),
 'dynasty_story_06':('06  九霄试炼','登高 · 御风 · 天将'),
 'dynasty_story_07':('07  东海定波','水下生存 · 龙宫远征'),
 'dynasty_story_08':('08  问鼎龙帝','终战准备 · 毕业配装'),
 'dynasty_c1':('百工与机巧','基础制作 · 工坊操作'),
 'dynasty_c3':('兵甲与锻造','兵器 · 护甲 · 升级'),
 'dynasty_c5':('科举与军旅','入仕 · 募兵 · 军阵'),
 'dynasty_c9':('山野与行旅','探访 · 采料 · 补给'),
 'dynasty_c10':('饰品与配装','槽位 · 效果 · 取舍'),
 'dynasty_c12':('九霄见闻','云上采料 · 行路准备'),
 'dynasty_build_guard':('玄武守御','正面格挡 · 抓住反击'),
 'dynasty_build_sword':('游龙剑舞','走位连击 · 留出退路'),
 'dynasty_build_archer':('逐星射艺','满蓄瞄准 · 第二箭'),
 'dynasty_build_talisman':('道门律令','控场 · 蓄势 · 释放'),
 'dynasty_boss_ascent':('四象试炼与讨伐','找栖息地 · 准备复战'),
}

def pack_gui():
    pack=ROOT/'modpack/resourcepacks/dynasty-quest-guides-v3.zip';pack.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('pack.mcmeta',json.dumps({'pack':{'pack_format':15,'description':'王朝任务 · 原创操作图示'}},ensure_ascii=False))
        for p in sorted(OUT.rglob('*.png')):z.write(p,'assets/dynasty/textures/gui/quests/journey/'+str(p.relative_to(OUT)))

def build_navigation():
    """Redraw typography only; never regenerate accepted operation diagrams."""
    from quest_story import build_book
    book=build_book();home=next(c for c in book if c['file']=='dynasty_home')
    headline=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',44)
    body=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',32)
    for image in home['images']:
        key=Path(image['image']).stem;title,note=CARD_COPY[key]
        im=Image.new('RGB',(512,128),'#142628');d=ImageDraw.Draw(im)
        d.rectangle((2,2,509,125),outline='#9dbeaa',width=3)
        for text,y,font,color in ((title,20,headline,'#e5d1a0'),(note,79,body,'#bed2c6')):
            width=d.textlength(text,font=font)
            assert width<=472,(key,text,width)
            d.text(((512-width)/2,y),text,font=font,fill=color)
        im.save(OUT/'cards'/(key+'.png'))
    labels={i['image']:i for c in book for i in c.get('images',[]) if '/labels/' in i['image']}
    for resource,image in labels.items():
        # Match each existing map rectangle, so the glyphs are not stretched.
        h=48;w=round(h*image['width']/image['height'])
        im=Image.new('RGB',(w,h),'#142628');d=ImageDraw.Draw(im)
        d.rectangle((1,1,w-2,h-2),outline='#9dbeaa',width=2)
        title=image['hover'][0]
        font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',26)
        width=d.textlength(title,font=font)
        assert width<=w-28,(resource,title)
        d.text(((w-width)/2,8),title,font=font,fill='#e5d1a0')
        im.save(ROOT/'src/main/resources/assets'/resource.replace(':','/',1))
    pack_gui()
    print('Redrew',len(home['images']),'navigation cards and',len(labels),'section labels; operation PNGs preserved')

def build(only_figures=None,only_charm_labels=False):
    OUT.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
    bold=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22)
    selected={} if only_charm_labels else FIGURES if only_figures is None else {key:FIGURES[key] for key in only_figures}
    for key,(title,cells,notes) in selected.items():
        im=Image.new('RGB',(512,256),'#142628');d=ImageDraw.Draw(im)
        d.rectangle((3,3,508,252),outline='#9dbeaa',width=2)
        d.text((20,16),title,font=bold,fill='#e5d1a0')
        if key in {'glass_bottle','target_recipe','infusion_table'}:
            pattern={'glass_bottle':[['玻','','玻'],['','玻',''],['','','']],
                     'target_recipe':[['','红',''],['红','草','红'],['','红','']],
                     'infusion_table':[['银','玉','银'],['青','工','青'],['青','青','青']]}[key]
            for row in range(3):
                for col in range(3):
                    x=198+col*40;y=54+row*40;label=pattern[row][col]
                    color={'玻':'#647c86','红':'#974f45','草':'#ad8f54','银':'#9fa9a1',
                           '玉':'#598877','青':'#ad8f54','工':'#856846'}.get(label,'#263b3c')
                    d.rectangle((x,y,x+36,y+36),fill=color,outline='#bed2c6')
                    d.text((x+8,y+8),label,font=font,fill='#e8ede2')
        elif key=='altar':
            for row in range(3):
                for col in range(3):
                    x=199+col*40;y=54+row*40
                    jade=row!=1 and col!=1;center=row==col==1
                    d.rectangle((x,y,x+36,y+36),fill='#598877' if jade else '#81647c' if center else '#263b3c',outline='#bed2c6')
                    d.text((x+8,y+8),'玉' if jade else '坛' if center else '',font=font,fill='#e8ede2')
        elif key=='compass_recipe':
            for i,label in enumerate(('原木 → 自然','圆石 → 探险者')):
                cx=113+i*252
                d.text((cx-57,48),label,font=font,fill='#bed2c6')
                for row in range(3):
                    for col in range(3):
                        x=cx-54+col*36;y=78+row*32
                        center=row==col==1;material=(row==1)!=(col==1)
                        fill='#647c86' if center else ('#856846' if i==0 else '#6a7777') if material else '#263b3c'
                        d.rectangle((x,y,x+31,y+27),fill=fill,outline='#9dbeaa')
                        if center:d.text((x+6,y+3),'针',font=font,fill='#e8ede2')
        elif key=='academy_materials':
            # A schematic courtyard elevation, not a copied building screenshot.
            d.rectangle((84,149,306,167),fill='#d8d8ce',outline='#9dbeaa',width=2)
            d.rectangle((110,82,142,148),fill='#974f45',outline='#cf9680',width=2)
            d.rectangle((252,82,284,148),fill='#974f45',outline='#cf9680',width=2)
            d.rectangle((84,67,306,82),fill='#598877',outline='#9dbeaa',width=2)
            d.line((287,105,322,105),fill='#cf9680',width=2)
            d.text((330,93),'朱红柱',font=font,fill='#e8ede2')
            d.line((307,157,322,157),fill='#d8d8ce',width=2)
            d.text((330,145),'汉白玉',font=font,fill='#e8ede2')
            d.text((95,171),'石镐采地面',font=font,fill='#bed2c6')
        elif key=='brewing':
            d.rectangle((33,87,90,145),fill='#ad8f54',outline='#9dbeaa',width=2)
            d.text((29,154),'烈焰粉',font=font,fill='#e8ede2')
            d.rectangle((247,54,296,102),fill='#96747b',outline='#9dbeaa',width=2)
            d.text((305,65),'下界疣',font=font,fill='#e8ede2')
            d.line((272,104,272,130),fill='#bed2c6',width=3)
            d.line((190,130,350,130),fill='#bed2c6',width=3)
            for i in range(3):
                x=164+i*83
                d.rectangle((x,138,x+47,179),fill='#647c86' if i==0 else '#263b3c',outline='#9dbeaa',width=2)
                if i==0:d.text((x+5,145),'水瓶',font=font,fill='#e8ede2')
            d.line((92,116,156,116),fill='#ad8f54',width=2)
        elif key=='refining':
            for i,(label,color) in enumerate((('饰品','#598877'),('材料','#96747b'),('结果 +1','#ad8f54'))):
                x=40+i*170
                d.rectangle((x,64,x+82,135),fill='#263b3c',outline='#9dbeaa',width=2)
                # Simple jewelry plaque / material block are diagram symbols.
                d.rectangle((x+26,83,x+57,113),fill=color,outline='#e8ede2',width=2)
                d.text((x,149),label,font=font,fill='#e8ede2')
                if i<2:
                    d.line((x+96,98,x+144,98),fill='#bed2c6',width=3)
                    d.polygon(((x+144,98),(x+135,92),(x+135,104)),fill='#bed2c6')
        elif key=='writing_recipe':
            for i,label in enumerate(cells):
                x=45+i*170
                d.rectangle((x,67,x+82,139),fill='#263b3c',outline='#9dbeaa',width=2)
                if i==0:
                    d.rectangle((x+18,84,x+63,121),fill='#ad8f54',outline='#e8ede2',width=2)
                    d.line((x+28,87,x+28,118),fill='#142628',width=3)
                elif i==1:
                    d.rectangle((x+32,85,x+49,96),fill='#e8ede2')
                    d.rectangle((x+22,97,x+59,122),fill='#142628',outline='#647c86',width=2)
                else:
                    d.polygon([(x+25,125),(x+29,90),(x+57,79),(x+55,114)],fill='#e8ede2')
                    d.line((x+23,131,x+54,84),fill='#9dbeaa',width=3)
                d.text((x,151),label,font=font,fill='#e8ede2')
                if i<2:d.text((x+115,91),'+',font=bold,fill='#bed2c6')
        else:
            for i,text in enumerate(cells):
                y=57+i*42
                d.rectangle((20,y,490,y+33),fill='#263b3c',outline='#598877',width=1)
                d.text((32,y+5),f'{i+1}  {text}',font=font,fill='#e8ede2')
        for i,text in enumerate(notes):d.text((20,190+i*24),text,font=font,fill='#bed2c6')
        im.save(OUT/(key+'.png'))
    if only_figures is None and not only_charm_labels:
        from quest_story import build_source_book
        from quest_journey import TITLES
        labels=OUT/'labels';labels.mkdir(exist_ok=True)
        for c in build_source_book():
            im=Image.new('RGB',(512,48),'#142628');d=ImageDraw.Draw(im)
            d.rectangle((1,1,510,46),outline='#9dbeaa',width=2)
            title=c['title'].split(' · ')[0]
            import re
            title=re.sub(r'&[0-9a-fk-or]','',title)
            d.text((15,11),title,font=bold,fill='#e5d1a0');im.save(labels/(c['file']+'.png'))
        cards=OUT/'cards';cards.mkdir(exist_ok=True)
        for c in build_source_book():
            im=Image.new('RGB',(512,128),'#142628');d=ImageDraw.Draw(im)
            d.rectangle((2,2,509,125),outline='#9dbeaa',width=3)
            title=re.sub(r'&[0-9a-fk-or]','',TITLES.get(c['file'],c['title']))
            parts=title.split(' · ')
            d.text((20,34),parts[0],font=bold,fill='#e5d1a0')
            d.text((20,73),parts[1] if len(parts)>1 else '点击进入 · 按分区选支线',font=font,fill='#bed2c6')
            im.save(cards/(c['file']+'.png'))
    if only_figures is None:
        from quest_atlas import CHARM_SECTIONS
        labels=OUT/'labels';labels.mkdir(exist_ok=True)
        for i,title in enumerate(CHARM_SECTIONS):
            im=Image.new('RGB',(512,48),'#142628');d=ImageDraw.Draw(im)
            color=('#cf9680','#9dbeaa','#96bcd0','#d7b576')[i]
            d.rectangle((1,1,510,46),outline=color,width=2)
            d.rectangle((10,10,36,36),outline=color,width=2)
            # Four signs identify functional sections, not four new quest buttons.
            if i==0:d.line((14,32,31,15),fill=color,width=3)
            elif i==1:d.rectangle((16,16,30,30),fill=color)
            elif i==2:d.line((23,13,23,24,31,29),fill=color,width=3)
            else:d.line((16,15,30,31,30,15,16,31),fill=color,width=3)
            d.text((47,11),title,font=bold,fill=color)
            im.save(labels/('charm_'+str(i)+'.png'))
        # These eight labels previously all lost the slot after splitting on ·.
        from gen_curios import SLOT_NAMES
        for slot in ('necklace','ring','bracelet','hands','body','back','belt','charm'):
            im=Image.new('RGB',(512,48),'#142628');d=ImageDraw.Draw(im)
            d.rectangle((1,1,510,46),outline='#9dbeaa',width=2)
            d.text((15,11),'饰品 · '+SLOT_NAMES[slot],font=bold,fill='#e5d1a0')
            im.save(labels/('dynasty_accessory_'+slot+'.png'))
        im=Image.new('RGB',(512,48),'#142628');d=ImageDraw.Draw(im)
        d.rectangle((1,1,510,46),outline='#9dbeaa',width=2)
        d.text((15,11),'饰品 · 头部',font=bold,fill='#e5d1a0')
        im.save(labels/'dynasty_c10.png')
    # Reloadable GUI-only pack lets existing local mod jars load the diagrams.
    pack_gui()
    if only_figures is None and not only_charm_labels:build_navigation()
    assert all((OUT/(key+'.png')).is_file() for key in FIGURES),'Missing existing operation figure'
    print('Built',len(selected),'new/updated figures;',len(FIGURES),'total in GUI resource pack')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--figures',nargs='+',choices=list(FIGURES))
    parser.add_argument('--charm-labels',action='store_true',help='Build four charm labels and repair nine slot labels; preserve other PNGs')
    parser.add_argument('--navigation',action='store_true',help='Repair only navigation typography; preserve operation diagrams')
    args=parser.parse_args();assert not(args.figures and args.charm_labels)
    if args.navigation:build_navigation()
    else:build(args.figures,args.charm_labels)
