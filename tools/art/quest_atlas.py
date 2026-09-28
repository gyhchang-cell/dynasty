"""Native FTB chapter decoration/layout; geometry only, independent of progression."""
import math
import re
from pathlib import Path

from gen_curios import SLOT_NAMES
from quest_routes import ROUTES, code, node, jump

ASSET = "dynasty:textures/gui/quests/"
SLOT_STYLE = {"head":"crown", "necklace":"pendants", "ring":"rings", "bracelet":"diamond",
              "hands":"fan", "body":"shield", "back":"wings", "belt":"ribbon", "charm":"archive"}
CHARM_SECTIONS=("进攻与命中增益","防护机动与功能","条件触发 · 先看环境","代价取舍 · 先看负面")


def charm_sections():
    """Classify actual numeric mechanics, not item-name aesthetics or equal page sizes."""
    text=(Path(__file__).resolve().parents[2]/"src/main/java/com/dynasty/DynastyTrinkets.java").read_text()
    table=text.split("private static final Object[][] EXTRA_TABLE = {")[1].split("\n    };")[0]
    specs={item:[float(v.strip().rstrip("DdFf")) for v in values.split(",")]
           for item,values in re.findall(r'\{"([a-z_]+)",([^}]+)\}',table)}
    # Audited legacy switch cases in DynastyTrinkets.apply (not the numeric table).
    legacy_conditional={"storm_charm","jade_cicada","sea_pearl","sea_conch"}
    legacy_offense={"dragon_pearl","war_drum_charm","star_compass","inkstone","auspicious_bell"}
    from gen_trinkets7 import ITEMS
    from gen_curios import classifications
    result={}
    for item,slot in classifications().items():
        if slot!="charm": continue
        spec=specs.get(item)
        if spec:
            attrs=[(spec[0],spec[1]),(spec[2],spec[3])]+([(spec[7],spec[8])] if len(spec)>9 else [])
            if any(code>=0 and value<0 for code,value in attrs) or spec[4]==27: section=3
            elif spec[6] or (len(spec)>9 and spec[9]): section=2
            elif (len(spec)>10 and spec[10]) or any(code in (4,5,6,7) and value>0 for code,value in attrs) or spec[4] in (21,24): section=0
            else: section=1
        else: section=2 if item in legacy_conditional else 0 if item in legacy_offense else 1
        if item in ITEMS and ITEMS[item]['bonus_kind']!='none': section=0
        result[item]=section
    return result


def layout_charms(entries,chapter):
    sections=charm_sections()
    grouped=[[q for q in entries if sections[q["target"].split(":")[1]]==i] for i in range(4)]
    top_rows=max(math.ceil(len(grouped[i])/5) for i in (0,1))
    bottom_start=-8.0+(top_rows-1)*1.65+2.45
    chapter["atlas_sections"]=[]
    for index,group in enumerate(grouped):
        cx=-5.2 if index%2==0 else 5.2
        y=-8.0 if index<2 else bottom_start
        place(group,[(cx+(i%5-2)*1.8,y+(i//5)*1.65) for i in range(len(group))])
        chapter["atlas_sections"].append({"name":CHARM_SECTIONS[index],"count":len(group),"targets":[q["target"] for q in group]})
        chapter["images"].append(image("volume_"+str(index),cx,y-1.1,8.2,1.0,alpha=235,
                                       hover=[CHARM_SECTIONS[index],f"本区 {len(group)} 件；只分用途，不设前置或强弱排名"]))
        for q in group:
            q["atlas_section"]=CHARM_SECTIONS[index]
            # Old identity/rewards stay frozen; the subtitle is presentation only.
            q["subtitle"]=CHARM_SECTIONS[index]+" · 条件以悬浮说明为准"


def image(asset, x, y, width, height, *, alpha=255, order=-10, click="", hover=None):
    return {"image":ASSET+asset+".png", "x":x, "y":y, "width":width, "height":height,
            "rotation":0.0, "alpha":alpha, "order":order, "click":click, "hover":hover or []}


def place(rows, points):
    assert len(rows)==len(points)
    for q,(x,y) in zip(rows,points):
        q.update(x=round(float(x),3),y=round(float(y),3))


def route_layout(chapter):
    key=chapter["route"]
    rows=chapter["quests"]+chapter["quest_links"]
    # Twelve original journey nodes, four real mastery milestones, then five references.
    # IDs/dependencies never depend
    # on these coordinates; each style has a different silhouette and branch spaces.
    positions={
      "guard":[(-6,0),(-3.8,0),(-1.6,0),(-1.6,-2.5),(-1.6,2.5),(.6,0),(-3.8,-2.5),(2.8,0),(-6,3),(.6,3),(5.2,0),(-3.8,3),(-5.2,-5),(0,-5),(5.2,-5)],
      "sword":[(-6,-3),(-3.7,-4.2),(-1.4,-3),(1,-4.4),(3.4,-3),(.7,-.6),(-5.7,.6),(3,-.6),(-5,3.2),(.7,2.5),(5.5,1.8),(-2.8,2.5),(-6,5.6),(-1.5,5.6),(4.2,5.2)],
      "archer":[(0,-6.5),(-2.3,-4.4),(0,-2.3),(-4.6,-2.3),(4.6,-2.3),(0,0),(-6.4,.1),(0,2.3),(6.4,.1),(4.6,2.3),(0,4.6),(-4.6,2.3),(-6,5),(0,7),(6,5)],
      "talisman":[(0,-7),(-3.5,-6),(-3.5,-2),(0,0),(-6,-3.5),(0,-3.5),(-7,0),(3.5,-2),(7,0),(6,3.5),(3.5,2),(-6,3.5),(-3.5,6),(0,7),(3.5,6)],
    }
    growth={"guard":[(-5.5,6),(-2.5,8),(.5,8),(3.5,6)],
            "sword":[(-4,6.6),(-3,8.5),(0,8.5),(3,7)],
            "archer":[(-6,8),(-3.5,9.5),(0,9.5),(3.5,9.5)],
            "talisman":[(-6,8),(-3.5,9.5),(0,9.5),(3.5,9.5)]}
    extra_links={"guard":[(-5.5,-8),(5.5,-8)], "sword":[(-5.5,-7),(5.5,-7)],
                 "archer":[(6,8),(6,10.4)], "talisman":[(6,8),(6,10.4)]}
    # Straight progression lanes; decorations must never resemble quest dependencies.
    core=[(-9,-4),(-6,-4),(-3,-4),(-9,-10),(-9,-7),(0,-4),
          (-9,-1),(3,-4),(-6,-1),(-3,-1),(6,-4),(0,-1)]
    mastery=[(-9,2),(-6,2),(-3,2),(0,2)]
    evolutions=[(-9,5),(-6,5),(-3,5),(0,5),(3,5),(6,5),(3,8),(6,8)]
    accessories=[(0,-10),(0,-7),(3,-10),(3,-7),(6,-10),(6,-7)]
    refining=[(9,-10),(9,-7),(9,-4),(9,-1),(9,2)]
    extra_count=len(chapter['quests'])-35
    extra_evolutions=[(-9+i*3,8) for i in range(extra_count)]
    place(chapter["quests"],core+mastery+evolutions+accessories+refining+extra_evolutions)
    place(chapter["quest_links"],[])
    chapter["images"]=[image("title_"+key,0,-12,13,1.6)]


def catalog_points(style, n):
    if style=="archive":
        # Four balanced reading blocks. No artificial prerequisite chain among 86 charms.
        points=[]
        chunk=math.ceil(n/4)
        rows=math.ceil(chunk/5)
        half=(rows-1)*.9
        for i in range(n):
            part,local=divmod(i,chunk)
            cx=-5 if part%2==0 else 5
            cy=-(half+1.2) if part<2 else half+1.2
            row,col=divmod(local,5)
            points.append((cx+(col-2)*1.8,cy+row*1.8-half))
        return points
    if style=="crown" and n==8:
        return [(-4,-1.8),(-2,-3),(0,-3.4),(2,-3),(4,-1.8),(-3,1),(0,1.5),(3,1)]
    if style=="diamond" and n==5:
        return [(0,-3),(3,0),(0,3),(-3,0),(0,0)]
    if style in ("crown","pendants","rings","diamond"):
        # A complete necklace/ring reads as jewelry rather than a spreadsheet.
        radius=max(2.6,n*.31)
        return [(math.sin(2*math.pi*i/n)*radius,math.cos(2*math.pi*i/n)*radius*.8) for i in range(n)]
    if style=="wings":
        return [((-1 if i%2==0 else 1)*(2+(i//2)%3*1.9), -3+(i//6)*2.5+(i//2)%3*.65) for i in range(n)]
    if style=="fan":
        return [((i%5-2)*2.0, (i//5)*2.6 + abs(i%5-2)*.55-2.2) for i in range(n)]
    if style=="shield":
        return [((i%4-1.5)*2.1, (i//4)*2.2+abs(i%4-1.5)*.5-2.8) for i in range(n)]
    return [((i%6-2.5)*1.9, (i//6)*2.35+(.5 if i%2 else 0)-3.8) for i in range(n)]


def add_catalog_navigation(chapters, slots):
    allq={q["id"]:q for c in chapters for q in c["quests"]}
    new_accessories={"dynasty:"+item:code(1,spec["base"]+3+i)
                     for spec in ROUTES.values() for i,item in enumerate(spec["trinkets"])}
    for index,(slot,slot_name) in enumerate(SLOT_NAMES.items()):
        chapter=next(c for c in chapters if c["file"]==("dynasty_c10" if slot=="head" else "dynasty_accessory_"+slot))
        guide=node(0x41000+index,slot_name+" · 怎么选，怎么戴", "checkmark", "guide:slot_"+slot,
                   "同一槽位代表佩戴位置，不代表必须集齐；按当前缺的是生存、输出还是探索来选择。",
                   f"打开物品栏的 Curios 面板，放进{slot_name}槽或万能槽才生效。背包内不生效。阅读页不会检测穿戴、不给奖励；下面是保留原进度的真实收藏任务。",role="guide")
        guide.update(x=0.0,y=-10.2 if slot=="charm" else -6.0,shape="gear",size=1.2)
        guide["description"] += ["", "&e&l想按玩法搭配？选一条即可&r"]
        for key,spec in ROUTES.items():
            guide["description"].append(jump(spec["title"]+" · "+spec["slogan"],code(1,spec["base"])))
        guide["description"] += ["", "已有饰品并不需要全换新。先查物品悬浮说明中的触发条件；有代价、昼夜或生命条件的装备不一定适合所有场合。",
                                  "当前页面外形是阅读分区，不代表合成前置或强弱排名；没有连线不等于遗漏任务。"]
        chapter["quests"].insert(0,guide)
        links=[]
        for item,target in new_accessories.items():
            if slots[item.split(":")[1]]!=slot:
                continue
            links.append({"id":code(6,0x41000+list(new_accessories).index(item)),"linked_quest":target,
                          "title":"流派饰品 · "+allq[target]["title"],"shape":"diamond","size":1.05,"target":item})
        # Existing main-line accessories remain in the main spine and are represented
        # here as links so every registered accessory has a correct-slot atlas entry.
        present={q["target"] for q in chapter["quests"]}|{q["target"] for q in links}
        for q in list(allq.values()):
            short=q["target"].split(":")[-1]
            if q["kind"]=="item" and slots.get(short)==slot and q["target"] not in present:
                links.append({"id":code(6,0x42000+index*32+len(links)),"linked_quest":q["id"],
                              "title":"已有任务 · "+q["title"],"shape":"square","size":1.0,"target":q["target"]})
                present.add(q["target"])
        chapter["quest_links"]=links
        chapter["layout"]=SLOT_STYLE[slot]
        entries=chapter["quests"][1:]+links
        # Stable ID sorting preserves a recognizable position when translated titles change.
        entries.sort(key=lambda q:q["id"])
        place(entries,catalog_points(SLOT_STYLE[slot],len(entries)))
        if slot != 'charm' and entries:
            # Slot guides stay above the full catalogue as new accessories expand its radius.
            guide['y']=min(q['y'] for q in entries)-2.0
        for q in chapter["quests"][1:]:
            if q["target"] in {"dynasty:heart_mirror","dynasty:jade_ring","dynasty:arrow_quiver","dynasty:talisman_pouch","dynasty:jade_crown"}:
                q["shape"]="diamond"
                q["size"]=1.1
                q["subtitle"]="可先查的基础搭配 · 非强制"
            q["description"].insert(0,jump("返回本槽位的搭配说明",guide["id"]))
        chapter["images"]=[image("backdrop_catalog",0,0,21.5,21.5 if slot=="charm" else 14,alpha=80,order=-100),
                           image("title_"+slot,0,-11.5 if slot=="charm" else -9.0,11,1.4)]
        if slot=="charm":
            layout_charms(entries,chapter)
            guide["description"] += ["", "&b&l四区按真实效果划分&r",
                "先排有负面代价的装备，再排昼夜、水下、残血、骑乘等条件装备；其余按进攻/命中与防护/机动/功能分区。同一件只出现一次，既有进度不变。",
                "分区不代表所有效果同时生效，也不替代具体条件和概率。想低风险入门先看防护区；想追求特殊触发先读负面和条件。"]


def decorate(chapters):
    from quest_growth import clean_navigation
    clean_navigation(chapters)
    for c in chapters:
        if c.get("route"):
            route_layout(c)
        if c.get("layout")=="home":
            c["images"]=[image("backdrop_home",0,0,22,20,alpha=140,order=-100),image("title_home",0,-8.5,15,1.8)]
            for card in c["home_cards"]:
                c["images"].append(image(card["asset"],card["x"],card["y"],8.4,2.2,
                                         click="#"+card["target"],hover=card["hover"]))
        if not c["main"] and c["file"].startswith("dynasty_c") and not c.get("layout"):
            style="archive" if len(c["quests"])>35 else {"dynasty_c5":"crown","dynasty_c9":"wings","dynasty_c6":"shield"}.get(c["file"],"ribbon")
            # Dense weapon/armour references have reading blocks; small side chapters
            # use bands/fans without pretending that their positions are prerequisites.
            if style=="wings" and len(c["quests"])>12:
                style="fan"
            c["layout"]=style
            place(c["quests"],catalog_points(style,len(c["quests"])))
            c["images"]=[image("backdrop_catalog",0,0,21,20 if style=="archive" else 14,alpha=65,order=-100)]
        # All optional chapters get an explicit, safe return path (native text link).
        if not c["main"] and c["file"]!="dynasty_home":
            for q in c["quests"]:
                q["description"].append(jump("← 山河总览 · 换路线 / 找主线",code(1,0x40000)))
        c["images"] = [img for img in c.get("images", []) if "/backdrop_" not in img["image"]]
