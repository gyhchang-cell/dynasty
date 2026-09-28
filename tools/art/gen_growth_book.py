#!/usr/bin/env python3
"""Kill growth/evolution resources and the real, native Patchouli two-page codex."""
import json
import re
from pathlib import Path
from boss_quest_guides import GUIDES
from gen_school_branches import BRANCHES
from gen_trinkets7 import ITEMS as ACCESSORIES

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources'
EVOLUTIONS = {
    'guard': [('zhenyue_blade','juque_sword','dragon_crystal'),('juque_sword','qinglong_dao','emperor_bone'),('qinglong_dao','xuanwu_blade','dragon_emperor_seal')],
    'sword': [('liuyun_sword','sword_dragon_crystal','dragon_crystal'),('sword_dragon_crystal','longyuan_sword','sky_token'),('longyuan_sword','tianzi_sword','dragon_emperor_seal')],
    'archer': [('zhuxing_bow','shenbi_bow','refined_steel'),('shenbi_bow','dragon_bow','sea_token'),('dragon_bow','houyi_bow','dragon_emperor_seal')],
    'talisman': [('chiling_brush','taiyi_sword','dragon_crystal'),('taiyi_sword','taiyi_whisk','emperor_bone'),('taiyi_whisk','hunyuan_staff','dragon_emperor_seal')],
}

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def main():
    from weapon_evolution_paths import PATHS, recipe_id, generate_resources
    generate_resources()
    for school, stages in EVOLUTIONS.items():
        for i, (base, result, addition) in enumerate(stages, 1):
            # Vanilla smithing preserves the base stack's complete NBT, including XP/name/enchantments.
            write(RES/f'data/dynasty/recipes/evolve_{school}_{i}.json', {
                'type':'minecraft:smithing_transform', 'template':{'item':'dynasty:blueprint'},
                'base':{'item':'dynasty:'+base}, 'addition':{'item':'dynasty:'+addition},
                'result':{'item':'dynasty:'+result}})
    write(RES/'data/dynasty/patchouli_books/imperial_codex/book.json', {
        'name':'book.dynasty.name','landing_text':'book.dynasty.landing',
        'version':1,'use_resource_pack':True,'custom_book_item':'dynasty:dynasty_manual',
        'book_texture':'patchouli:textures/gui/book_brown.png','model':'patchouli:book_brown',
        'show_progress':True,'use_blocky_font':True, 'creative_tab':'minecraft:tools_and_utilities',
        'text_color':'353326','header_color':'355b47','link_color':'247358','link_hover_color':'ac7b30',
        'i18n':True})
    categories = [('start','入世指南','Getting Started','dynasty:dynasty_manual'),
        ('schools','流派与兵器进化','Schools & Evolution','dynasty:liuyun_sword'),
        ('weapons','兵器谱','Arsenal','dynasty:qinglong_dao'),
        ('armor','甲胄与套装','Armour & Sets','dynasty:bronze_chestplate'),
        ('accessories','饰品搭配','Accessories','dynasty:jade_ring'),
        ('bosses','讨伐图鉴','Boss Guide','dynasty:dragon_emperor_seal'),
        ('exploration','山河行旅','Exploration','minecraft:compass'),
        ('empire','王朝百业','Imperial Crafts','dynasty:blueprint')]
    contract=json.loads((ROOT/'docs/content/schools-v1-contract.json').read_text())
    weapon_source=(ROOT/'src/main/java/com/dynasty/DynastyWeapons.java').read_text()
    balance=(ROOT/'src/main/java/com/dynasty/DynastyBalance.java').read_text()
    armor_bonuses={k:[float(x.strip().rstrip('DdFf')) for x in values.split(',')]
                   for k,values in re.findall(r'SET_BONUS.put\("([a-z_]+)", new double\[\]\{([^}]+)\}',balance)}
    recipes={p.stem:json.loads(p.read_text()) for p in (RES/'data/dynasty/recipes').glob('*.json')}
    from gen_curios import classifications
    slots=classifications()
    for locale in ('zh_cn','en_us'):
        zh=locale=='zh_cn'
        lang_path=RES/f'assets/dynasty/lang/{locale}.json'
        lang=json.loads(lang_path.read_text())
        lang.update({'book.dynasty.name':'王朝山河录' if zh else 'Chronicles of Dynasty',
            'book.dynasty.landing':'入世立业，百炼成锋。$(br2)选择右页图标，查找材料、成长路线、召唤地点与装备搭配。' if zh else 'Build a home. Forge your legacy.$(br2)Choose a category on the right for materials, progression, encounters and equipment.',
            'message.dynasty.weapon.level':'%s 提升至 %s 级' if zh else '%s reached level %s'})
        write(lang_path,lang)
        root=RES/f'assets/dynasty/patchouli_books/imperial_codex/{locale}'
        def name(item):
            return lang.get('item.dynasty.'+item,lang.get('block.dynasty.'+item,item.replace('_',' ').title()))
        def text(title,body):
            return {'type':'patchouli:text','title':title,'text':body}
        def entry(key,category,title,icon,pages):
            # Patchouli localizes literal page text through Java's formatter.
            # A lone ASCII percent can produce "Format error" in rendered books.
            for page in pages:
                if isinstance(page.get('text'),str):
                    page['text']=page['text'].replace('%','％')
            write(root/f'entries/{key}.json',{'name':title,'category':'dynasty:'+category,'icon':icon,'pages':pages})
        for i,(key,cn,en,icon) in enumerate(categories):
            write(root/f'categories/{key}.json',{'name':cn if zh else en,'description':cn if zh else en,'icon':icon,'sortnum':i})
        entry('welcome','start','从这里开始' if zh else 'Begin Here','dynasty:dynasty_manual',[
            text('第一步' if zh else 'First Steps','先建安全据点，准备工作台、照明与铁制工具。任务按钮给出下一步目标；本书用于查做法。$(br2)$(l:schools/growth)杀怪成长与兵器进化$(/l)$(br)$(l:exploration/compasses)制作两种罗盘$(/l)' if zh else 'Build a safe shelter, a crafting table, lights and iron tools. Quests provide objectives; this book explains how.$(br2)$(l:schools/growth)Combat growth$(/l)$(br)$(l:exploration/compasses)Navigation$(/l)')])
        entry('schools/growth','schools','杀怪、升级、进化' if zh else 'Kills, Levels & Evolution','dynasty:blueprint',[
            text('双线成长' if zh else 'Two Growth Tracks','用王朝兵器击杀敌对生物，同时获得流派熟练度和这把武器的历练。普通敌人给1点；强敌最多8点。没有走位、连击或满蓄要求。$(br2)流派属于玩家，武器等级属于物品；换武器不清空流派。' if zh else 'Kill hostile enemies with Dynasty weapons to earn school mastery and weapon XP. Normal foes award 1 point; stronger foes up to 8. No movement, combo or full-draw requirement.$(br2)Mastery belongs to you; weapon XP belongs to its stack.'),
            text('越练越强' if zh else 'Growing Stronger','流派0→1阶需8点，之后为5+3×下一阶²；武器1→2级需10点，之后为6+4×当前等级²。$(br2)熟练度与武器等级均提高伤害，不设固定毕业等级，越往后升级越慢。武器悬浮按Shift查看历练；/dynasty school 查看熟练度。' if zh else 'School rank 1 needs 8 XP; later ranks need 5+3×next rank². Weapon level 2 needs 10 XP; later levels need 6+4×current level². Both increase damage; costs grow without a fixed graduation level. Hold Shift on a weapon to see its XP.'),
            text('锻造台进化' if zh else 'Smithing Evolution','左槽放兵器图纸，中槽放已培养武器，右槽放该阶段材料。进化为另一把更强兵器，保留等级、历练、自定义名称与附魔。$(br2)例如：2级流云剑 → 2级龙晶剑。普通工作台配方不继承旧兵器历练，请使用本书进化页的锻造配方。' if zh else 'Template: blueprint. Base: trained weapon. Addition: listed stage material. Smithing evolves the weapon while preserving its level, XP, name and enchantments. Ordinary crafting does not transfer growth.')])
        for school,stages in EVOLUTIONS.items():
            title=lang.get('school.dynasty.'+school,school)
            pages=[text(title,'装备对应兵器或流派饰品，再杀怪即可提升。升级与进化可同时进行。$(br2)下面每页是实际锻造配方。' if zh else 'Equip school weapons or accessories and defeat enemies. Level and evolve in parallel. Following pages show real smithing recipes.')]
            for i,(_,result,_) in enumerate(stages,1):
                pages.append({'type':'patchouli:smithing','recipe':f'dynasty:evolve_{school}_{i}',
                              'title':name(result),'text':'等级与历练保留。' if zh else 'Level and XP are preserved.'})
            for key,base,result,material,label in PATHS[school]:
                pages.append({'type':'patchouli:smithing','recipe':'dynasty:'+recipe_id(school,key),
                              'title':name(result),'text':('兵器分支：'+name(base)+' → '+name(result)+'。保留等级、历练、淬炼、附魔与名称。') if zh else 'Weapon branch. Preserves level, XP, refinement, enchantments and name.'})
            for item in contract['items']:
                if item['school']==school and item['kind']=='accessory':
                    pages.append({'type':'patchouli:spotlight','item':'dynasty:'+item['id'],
                                  'text':item['zh_effect' if zh else 'en_effect'].replace('常驻','')})
            branch=BRANCHES[school]
            from gen_codex_all import use_line
            from gen_trinkets7 import TRINKETS
            for item in ACCESSORIES.values():
                if item['school'] != school: continue
                stats=use_line(TRINKETS[item['id']], (0,0,0), 0, zh)
                if item['zh_effect' if zh else 'en_effect']: stats.insert(0,item['zh_effect' if zh else 'en_effect'])
                pages.append({'type':'patchouli:smithing' if item['recipe'][0].split(':')[-1] in ACCESSORIES else 'patchouli:crafting','recipe':'dynasty:'+item['id'],
                    'title':item['zh' if zh else 'en'],'text':'$(br)'.join(stats)})
            pages.append({'type':'patchouli:smithing','recipe':'dynasty:branch_'+branch['id'],
                          'title':name(branch['id']),'text':branch['effect' if zh else 'effect_en']})
            pages.append({'type':'patchouli:smithing','recipe':'dynasty:branch_'+branch['id']+'_advance',
                          'title':name(branch['next']),'text':'分支兵器继续进化，等级和历练保留。' if zh else 'Continue evolving. Level and XP are preserved.'})
            entry('schools/'+school,'schools',title,'dynasty:'+stages[0][0],pages)
        entry('schools/accessory_refining','schools','饰品淬炼与进化' if zh else 'Accessory Refinement','minecraft:anvil',[
            text('淬炼' if zh else 'Refining','铁砧左槽放流派饰品，右槽放材料。取出结果消耗材料与经验，淬炼+1。各流派任务中的 +1/+5/+15/+30 节点列出逐级精确消耗。$(br2)0–9级用玉，10–24级用龙晶，25–49级用玄天玉，50级起用天将令。每4级增加1份材料，最多64份；经验从2级递增，最多39级。' if zh else 'Anvil: accessory on the left, material on the right. Taking the result consumes material and XP for +1 refinement. See the +1/+5/+15/+30 school quests for exact step-by-step costs. Jade at 0–9; dragon crystal at 10–24; celestial jade at 25–49; sky token from 50. Material cost grows to 64; XP-level cost grows from 2 to 39.'),
            text('持续培养' if zh else 'Keep Growing','淬炼额外伤害为4%×√等级：+1增加4%，+25增加20%，+100增加40%。对应近战、箭矢或律令兵器。没有固定毕业等级，后期单级收益递减。$(br2)同名饰品只取最高淬炼，不重复叠加；必须佩戴生效。锻造台进化保留淬炼、附魔、名称，普通合成不能替代。' if zh else 'Extra damage is 4% × square root of refinement level: +1 grants 4%, +25 grants 20%, +100 grants 40%. Applies to school melee, arrows or edict weapons. No fixed graduation level; marginal gains diminish. Duplicate IDs use the highest refinement. Equip to activate. Smithing evolution preserves refinement, enchantments and names.')])
        for boss,(_,cn,token,_,location,prepare,tactics) in GUIDES.items():
            entry('bosses/'+boss,'bosses',cn if zh else boss.replace('_',' ').title(),'dynasty:'+token,[
                text('在哪里' if zh else 'Location',location if zh else 'Consult the quest boss guide for this encounter. Use the matching Dynasty dimension portal.'),
                text('战前准备' if zh else 'Preparation',prepare if zh else 'Bring armour, healing and a return portal.'),
                text('战斗要点' if zh else 'Battle',tactics if zh else 'Avoid telegraphed attacks and defeat reinforcements. Break the shield before committing.'),
                text('再次召唤' if zh else 'Summoning',f'法阵·祭坛周围同一高度8格中，至少4格摆玉石块。手持{name(token)}右键祭坛，成功消耗1枚。附近已有同种Boss时不能重复召唤。' if zh else 'Place at least four jade blocks in the eight spaces around the Ritual Altar, on its level. Use the matching boss token on the altar. One token is consumed; a nearby living boss prevents duplicates.')])
        entry('exploration/compasses','exploration','罗盘与回程' if zh else 'Navigation','minecraft:compass',[
            text('两种搜索' if zh else 'Two Searches','自然指南针找生物群系；探险者指南针找建筑。先进入目标维度，再右键罗盘选名称搜索。建筑位置不等于Boss必刷位置。$(br2)出发前带回程门和归乡符。' if zh else "Nature's Compass finds biomes; Explorer's Compass finds structures in your current dimension. A structure is not a guaranteed boss spawn. Bring a return portal."),
            {'type':'patchouli:crafting','recipe':'naturescompass:natures_compass'},
            {'type':'patchouli:crafting','recipe':'explorerscompass:explorers_compass'}])
        entry('exploration/ruins','exploration','封印遗迹怎么解' if zh else 'Sealed Ruins','dynasty:ruin_gate',[
            text('先看机关' if zh else 'Read the Mechanism','音乐遗迹：先读石碑，再点击音钟输入旋律；输错可回到控制器重试。$(br2)封印宝库：点击中央控制器，会提示下一步应操作哪个方向的灯。点击一盏灯会同时改变它和顺时针下一盏灯；按提示逐步完成。' if zh else 'Music ruin: read the tablet, then play the bells in order. Return to the controller to retry. In the seal vault, use the central controller for the next lamp direction. Each click toggles that lamp and its clockwise neighbour.'),
            text('开门与宝箱' if zh else 'Door and Treasure','解开机关后，封印门打开，控制器正上方出现公共奖励箱。箱子只生成一次；请为它留出空间，若被方块挡住，清空后再次点击控制器。$(br2)后室有附魔台、书架和锻造台。封印门及后室围护在生存模式下不可挖破，必须解谜进入。' if zh else 'Solving opens the seal and creates a shared reward chest above the controller, once only. If blocked, clear that space and use the controller again. The enclosed rear workshop contains an enchanting table, bookshelves and a smithing table. Its seal and shell cannot be mined in survival.')])
        entry('exploration/waystations','exploration','旅途补给与帝陵入口' if zh else 'Waystations and Tomb Access','minecraft:lantern',[
            text('三处落脚点' if zh else 'Three Places to Rest','平原与向日葵平原：官道驿站，备有炊事和修整工具。$(br2)森林、桦木林与繁花森林：林间药庐，有药田与酿造台。$(br2)沙漠：沙海商旅院，有水井与制图桌。探险者指南针可搜索这些建筑；前三章也有对应探访任务。' if zh else 'Plains and sunflower plains: Post House, with cooking and repair stations. Forests, birch forests and flower forests: Herbal Retreat, with crop beds and brewing. Deserts: Caravan Court, with a well and cartography table. Find them with Explorer’s Compass; the first three quest chapters include visits.'),
            text('帝陵在地下' if zh else 'The Tomb Lies Below','帝陵主体埋在地下。新生成的帝陵有地面入口亭，沿照明梯井下行，进入墓道。不要只在指南针坐标的地表找大殿。$(br2)旧区块里已生成的建筑不会自动改造；新入口、新遗迹和旅途建筑需要新生成或重新放置。' if zh else 'New tombs have a surface pavilion and a lit ladder shaft leading down to the buried passage. Do not expect the burial hall on the surface at the compass marker. Existing structures are not rebuilt automatically: these changes require new generation or placement.')])
        # One indexed entry per craftable Dynasty item, with real recipes and item icons.
        grouped={}
        for rid,recipe in recipes.items():
            out=recipe.get('result',{})
            out=out.get('item','') if isinstance(out,dict) else out
            if out.startswith('dynasty:') and (recipe['type'].startswith('minecraft:crafting') or out.split(':')[1] in ACCESSORIES):
                grouped.setdefault(out.split(':')[1],[]).append(rid)
        for item,rids in grouped.items():
            category=('accessories' if item in slots else 'armor' if item.endswith(('_helmet','_chestplate','_leggings','_boots'))
                      else 'weapons' if '"'+item+'"' in weapon_source else 'empire')
            pages=[]
            if category=='armor':
                bonus=next((v for k,v in armor_bonuses.items() if item.startswith(k)),None)
                if bonus:
                    reduction,health=bonus[:2]
                    pages.append(text('护身加成' if zh else 'Protection',
                        f'每件伤害减免 +{reduction*100:g}%，生命上限 +{health:g}。$(br2)穿齐四件：伤害减免 {min(.9,reduction*4)*100:g}%，生命上限 +{health*4:g}。$(br2)混搭时按实际穿戴逐件相加；装备减伤合计最多90%。' if zh else
                        f'Per piece: +{reduction*100:g}% damage reduction, +{health:g} max health.$(br2)Four pieces: {min(.9,reduction*4)*100:g}% reduction, +{health*4:g} health. Mixed sets add per-piece bonuses; equipment reduction is capped at 90%.'))
            info=next((it for it in contract['items'] if it['id']==item),None)
            if item in ACCESSORIES:
                info=ACCESSORIES[item]
            if item in ACCESSORIES:
                stats=use_line(TRINKETS[item],(0,0,0),0,zh)
                if info['zh_effect' if zh else 'en_effect']:stats.insert(0,info['zh_effect' if zh else 'en_effect'])
                pages.append(text(name(item),'$(br)'.join(stats)))
            elif info: pages.append(text(name(item),info['zh_effect' if zh else 'en_effect'].replace('常驻','')))
            for rid in rids:
                pages.append({'type':'patchouli:smithing' if recipes[rid]['type']=='minecraft:smithing_transform' else 'patchouli:crafting','recipe':'dynasty:'+rid})
            entry(category+'/'+item,category,name(item),'dynasty:'+item,pages)
    print(f'Generated {sum(map(len,EVOLUTIONS.values()))+sum(map(len,PATHS.values()))} NBT-preserving evolutions and bilingual Patchouli categories/entries.')

if __name__=='__main__': main()
