"""Two short, useful side routes per journey chapter; stable IDs and no mandatory grind."""
from quest_routes import node,add_recipe

# Anchor index, branch label, two actual inventory objectives and their practical purpose.
ROUTES=[
 [(2,'安家',('minecraft:white_bed','落脚 · 一张床','在安全屋安放床并设置重生点；任务检测持有白色床，不检测睡眠。'),('minecraft:bread','补给 · 自己的麦田','种植小麦制作面包，建立可补充的出行食物。')),
  (5,'洞穴',('minecraft:ladder','下矿 · 留一条回路','用木棍制作梯子，进深坑前准备返程通道。'),('minecraft:bucket','采矿 · 收纳熔岩','准备第二只空桶，将水桶留在快捷栏；需要熔岩燃料时再装取，任务不要求冒险取岩浆。'))],
 [(6,'玉器',('dynasty:jade_pendant','玉器 · 第一件佩饰','用工坊材料制作玉佩，放入对应 Curios 槽位试用。'),('dynasty:heart_mirror','护身 · 护心镜','制作护心镜，查看属性后决定替换或搭配；不要求穿低阶装备。')),
  (8,'修造',('minecraft:grindstone','修造 · 清理旧附魔','砂轮可以清除多数附魔；不要把需要保留的附魔武器随意放进去。'),('minecraft:anvil','修造 · 铁砧工位','铁砧用于修理与流派饰品淬炼；原装备进化仍在锻造台完成。'))],
 [(1,'朝堂',('dynasty:official_seal','入仕 · 官印','制作官印，查看朝堂与官阶图鉴，展开科举之外的养成。'),('dynasty:jade_seal','朝堂 · 玉玺工艺','按实际配方制作玉玺，把已有玉料投入朝堂器物。')),
  (2,'军备',('minecraft:arrow','军备 · 准备箭袋','带上32支箭，远处敌人可以先用弓处理；普通合成可用燧石、木棍和羽毛。'),('dynasty:zhuxing_bow','军备 · 射术起步','制作逐星弓，射术与近战可以切换，不必重练角色。'))],
 [(5,'落脚',('minecraft:barrel','天朝据点 · 储物','携带木桶，在传送门附近建立补给点，任务不检测放置。'),('dynasty:festival_lantern','天朝据点 · 灯火','用王朝灯饰点亮自己的据点；建筑材料也可以用于你的家。')),
  (7,'战利品',('dynasty:pickaxe_jade','玉器工具 · 玉镐','把王朝材料投入工具，补充战斗以外的成长。'),('dynasty:sword_dragon_crystal','内廷战后 · 龙晶剑','保留内廷战利品，按配方升级兵器；想保留练过的武器等级，使用对应锻造进化配方。'))],
 [(1,'探索',('dynasty:tomb_candle','探陵 · 墓烛','制作墓烛，按物品说明选择佩戴，补充帝陵探索配装。'),('dynasty:bone_chill_pendant','探陵 · 寒骨佩','根据掉落与配方收集材料，制作幽冥主题饰品；比较属性再替换。')),
  (5,'帝骸',('dynasty:emperor_bone','战后备料 · 帝骸骨','确认捡起帝骸骨，再查看下一件装备需要多少；本节点不消耗材料。'),('dynasty:dragon_bone_ring','战后锻造 · 龙骨戒','用战利品制作龙骨戒，给下一次远征准备饰品。'))],
 [(1,'登高',('minecraft:scaffolding','登高 · 脚手架','带上16个脚手架搭设可拆卸通道；高处施工注意支撑距离。'),('minecraft:spyglass','观天 · 先看再走','制作望远镜，从安全平台观察建筑入口与周围地形。')),
  (6,'天将工艺',('dynasty:sky_token','天将战后 · 留下令牌','令牌用于后续配方，也用于高阶淬炼；先看用途再花掉。'),('dynasty:tiangang_talisman','天将工艺 · 天罡符','把天将令牌、符纸与朱砂合成天罡符，将战利品转化成流派饰品。'))],
 [(2,'水下营造',('minecraft:magma_block','水路 · 气泡柱材料','带一块岩浆块，可在完整水源柱下建立向下气泡柱；接触会烫伤，先在安全水池试搭。'),('minecraft:sea_lantern','水路 · 水下照明','准备海晶灯照亮自己的水下据点，任务只检测持有。')),
  (7,'海藏',('dynasty:sea_pearl','龙宫材料 · 海珠','查看海珠配方与来源，选择一条水族饰品路线。'),('dynasty:sea_conch','海藏工艺 · 海螺','制作海螺并查看佩戴槽位；把探索战利品变成长期装备。'))],
 [(4,'剑道终点',('dynasty:dragon_emperor_seal','问鼎 · 帝印备料','龙帝首杀后留好帝印；先看毕业兵器配方，再决定投入。'),('dynasty:tianzi_sword','问鼎 · 天子剑','按真实配方打造天子剑；这是近战毕业选择之一。')),
  (4,'射术终点',('dynasty:tianlang_bow','射术 · 天狼弓备料','后羿弓的合成需要天狼弓；先查看完整配方，备齐另一把弓、凤羽与图纸。'),('dynasty:houyi_bow','射术 · 后羿弓','沿弓的配方或锻造路线制作后羿弓，已练过的弓优先使用保留等级的进化方式。'))],
]

def add_branches(chapters,recipes,name):
    for ci,c in enumerate([c for c in chapters if c['main']]):
        spine=list(c['quests'])
        # Horizontal story spine plus two outward lanes. No decorative background lines.
        for i,q in enumerate(spine): q.update(x=-8+i*1.5,y=0.0)
        for lane,(anchor,label,*steps) in enumerate(ROUTES[ci]):
            parent=spine[anchor]
            for si,(target,title,how) in enumerate(steps):
                count={'minecraft:arrow':32,'minecraft:scaffolding':16,'minecraft:bread':8,'minecraft:ladder':12}.get(target,1)
                q=node(0x70000+ci*16+lane*4+si,title,'item',target,how,how,count=count,xp=15,role='chapter_branch')
                q.update(deps=[parent['id']],subtitle=label+'支路',x=spine[anchor]['x']+si*1.5,y=-3.0 if lane==0 else 3.0)
                add_recipe(q,recipes,name)
                c['quests'].append(q)
                parent=q
        c['images']=[]
        # Small exploration loops: a real structure visit, then one useful craft.
        # Separate vertical lane preserves the established story IDs and links.
        explorations={
            0:('post_house','官道驿站','平原或向日葵平原','minecraft:smoker','驿站伙房','备一座烟熏炉，旅途中也能快速烹饪食物。'),
            1:('herbal_retreat','林间药庐','森林、白桦林或繁花森林','dynasty:healing_salve','药庐备药','采集药庐农田作物，另按配方准备金创药，出门前留一份恢复品。'),
            2:('desert_caravan','沙海商旅院','沙漠','minecraft:map','商旅地图','利用商旅院的制图工位整理探索地图；先制作空地图，再选择记录远征区域。'),
        }
        if ci in explorations:
            site,title,biome,target,craft,how=explorations[ci]
            base=0x72000+ci*16
            visit=node(base,'探访 · '+title,'advancement','dynasty:visit_'+site,
                '寻找能实际使用的野外补给与工坊。',f'在主世界{biome}寻找{title}，也可用探险者指南针选择它。进入建筑范围即完成；只在新生成区块出现。',xp=20,role='exploration_branch')
            visit.update(deps=[spine[2]['id']],subtitle='野外探访',x=spine[2]['x'],y=6.0,icon='{ id: "explorerscompass:explorerscompass" }')
            craftq=node(base+1,craft,'item',target,how,how,xp=15,role='exploration_branch')
            craftq.update(deps=[visit['id']],subtitle='探索后备料',x=visit['x']+2,y=6.0)
            add_recipe(craftq,recipes,name)
            c['quests'] += [visit,craftq]
        if ci in (1,2):
            site,title= ('tiangong_mining_estate','山麓采矿庄园') if ci==1 else ('tiangong_citadel','天工山城')
            base=0x73000+ci*16
            visit=node(base,'远行 · '+title,'advancement','dynasty:'+site,
                '在主世界寻找可采料的大型建筑。','用探险者指南针选择'+title+'；进入自然生成建筑范围完成探访。管理员放置仅供搭建，不保证触发探访。',xp=20,role='exploration_branch')
            visit.update(deps=[spine[2]['id']],subtitle='大型建筑',x=-5,y=9.0,icon='{ id: "minecraft:stone_bricks" }')
            c['quests'].append(visit)
            steps=[('minecraft:raw_iron','矿场备料','采矿庄园有露天矿台；开采并持有8个粗铁。任务只检测物品，不限定采集位置。',8),
                   ('dynasty:bronze_ingot','工坊再加工','带铜与锡到工坊，按实际配方制作青铜锭。',4)] if ci==1 else [
                   ('dynasty:refined_steel','城中锻造','沿中街寻找工坊，利用材料箱和现有配方备好精钢。任务只检测持有。',4),
                   ('dynasty:jade','密库备玉','主殿后室与各楼上层有材料箱；收集玉料留作装备强化。任务只检测持有，不会要求清空所有宝箱。',4)]
            for i,(target,label,how,count) in enumerate(steps):
                q=node(base+i+1,label,'item',target,how,how,count=count,xp=15,role='exploration_branch')
                q.update(deps=[visit['id']],subtitle='探索材料',x=-2+i*3,y=9.0)
                add_recipe(q,recipes,name);c['quests'].append(q)
