"""Original, additive boss atlas. Stable IDs; never replace legacy completions/rewards."""
import json
from pathlib import Path
from quest_routes import node, code, add_recipe

def add_boss_ascent(chapters, recipes, name):
    rows=[]
    def add(i,title,kind,target,x,y,deps=(),how='',icon=None,major=False):
        q=node(0x90000+i,title,kind,target,'从凡间动乱追索四象之力，最后进入龙口镇渊仪式。',how,xp=40 if kind=='kill' else 0)
        q.update(route='boss_ascent',x=float(x),y=float(y),deps=[code(1,0x90000+d) for d in deps],size=1.4 if major else 1.0,
                 subtitle='主 Boss · 实际击杀' if major else '实际进度 · 四象与探索')
        if icon:q['icon']='{ id: "'+icon+'" }'
        add_recipe(q,recipes,name);rows.append(q);return i
    add(0,'乱世初征 · 叛将','kill','dynasty:rebel_general',0,0,how='在主世界寻找叛将。先做好防具与恢复品，绕开冲锋预警。真实击杀计数，不消耗关键掉落。',icon='dynasty:bronze_chestplate',major=True)
    add(1,'入天朝 · 留下回程','dimension','dynasty:celestial_dynasty',2,0,(0,),how='沿原主线制作天朝传送门；随身携带回程门，建立据点。',icon='dynasty:blueprint')
    add(2,'宫阙暗影 · 宦官首脑','kill','dynasty:eunuch_mastermind',4,0,(1,),how='在天朝寻找宦官首脑，先清援兵并躲开毒雾。',icon='dynasty:talisman_pouch',major=True)
    add(3,'龙庭之巅 · 龙帝','kill','dynasty:dragon_emperor',6,0,(2,),how='天朝高阶挑战。准备抗火、恢复和高阶防具，观察龙焰与护盾阶段。保留龙族材料用于四象贡品。',icon='dynasty:dragon_crystal',major=True)
    branches=[
        (10,'青龙','dragon_palace','dragon_king','dragon_scale','qinglong_scale','ritual_qinglong',-6,'东海龙宫；准备水下呼吸与回程门，击败龙王后保留龙鳞、龙晶。'),
        (20,'白虎','jiuxiao','nine_heaven_general','dragon_crystal','baihu_fang','ritual_baihu',-2,'九霄天界；准备缓降与搭路方块，避开落雷，收集龙晶并制作精钢。'),
        (30,'朱雀','celestial_dynasty','phoenix','phoenix_feather','zhuque_feather','ritual_zhuque',2,'凤凰支线；先在现有凤凰出没区域寻找，准备抗火。收集凤凰羽和朱砂，不把朱砂误当矿石。'),
        (40,'玄武','underworld','undead_first_emperor','emperor_bone','xuanwu_shell','ritual_xuanwu',6,'地府幽冥；先设置安全回程据点，挑战不死始皇，保留帝骨；玄武壳另需龙鳞、精钢与图纸。')]
    # Four visible horizontal branches converge, rather than another row of indistinguishable bosses.
    for base,theme,dimension,boss,material,offering,adv,y,how in branches:
        add(base,theme+' · 远行准备','dimension','dynasty:'+dimension,8,y,(3,),how=how,icon='dynasty:'+offering)
        add(base+1,theme+' · '+{'dragon_king':'龙王','nine_heaven_general':'九霄天将','phoenix':'凤凰支线','undead_first_emperor':'不死始皇'}[boss],
            'kill','dynasty:'+boss,10,y,(base,),how=how,icon='dynasty:'+offering,major=boss!='phoenix')
        add(base+2,theme+' · 神话材料','item','dynasty:'+material,12,y,(base+1,),how=how+' 材料节点仅检测持有，做成贡品前先完成检测。')
        add(base+3,theme+' · 备齐贡品','item','dynasty:'+offering,14,y,(base+2,),how='按 JEI 制作'+name('dynasty:'+offering)+'，保留它前往龙口祭坛。检测持有，不收走贡品。')
        add(base+4,theme+' · 真实归位','advancement','dynasty:'+adv,16,y,(base+3,),how='找到自然生成的巨型龙口，右键对应供台，等待贡品动画完成。元素小球亮起后由服务器记录，不是阅读勾选。多人由实际投放者记录，FTB 队伍可共享任务。',icon='dynasty:'+offering)
    add(50,'四象汇聚 · 天命玉','item','dynasty:tianming_jade',19,0,(14,24,34,44),how='四条分支完成后，备好天命玉、装备和补给。中央金球完成汇聚后才能献上最终贡品。',major=False)
    add(51,'天门开启 · 中央献祭','advancement','dynasty:ritual_final_offering',21,0,(50,),how='右键中央供台献上天命玉，完成最终献祭。动画期间仍可自由移动，不要离开仪式范围。',icon='dynasty:tianming_jade')
    add(52,'镇渊战场','dimension','dynasty:zhenyuan_arena',23,0,(51,),how='仪式结束后自动传送进入密闭战场。登场期间可正常移动、跳跃和使用物品。',icon='dynasty:zhenyuan_node')
    add(53,'终章 · 镇渊帝君','kill','dynasty:zhenyuan_sovereign',25,0,(52,),how='击败镇渊帝君。按现有胜利流程返回龙口，奖励在归来后生成的箱子中；此任务不会重复发放 Boss 掉落。',icon='dynasty:tianming_jade',major=True)
    add(60,'异兽支线 · 年兽','kill','dynasty:nian_beast',2,4,(0,),how='可选异兽挑战，不阻塞四象与终章。按原异兽图鉴寻找年兽，准备恢复与撤退路线。',icon='dynasty:dragon_scale')
    add(61,'妖狐支线 · 九尾狐','kill','dynasty:nine_tailed_fox',4,4,(0,),how='可选妖兽挑战，不阻塞主 Boss 路线。先沿原探索任务寻找九尾狐。',icon='dynasty:jade')
    for q in rows:q['x']=(q['x']-12.5)*.72;q['y']*=.72
    chapters.append(dict(file='dynasty_boss_ascent',id=code(4,0x590),title='四象镇渊 · Boss 征途',goal='主线在上，异兽支线独立；四象归位汇聚终章。',group=1,main=False,order=9,quests=rows,quest_links=[],layout='boss_ascent'))
    out=Path(__file__).resolve().parents[2]/'src/main/resources/data/dynasty/advancements'
    for key in ['ritual_qinglong','ritual_baihu','ritual_zhuque','ritual_xuanwu','ritual_final_offering']:
        path=out/(key+'.json')
        text=json.dumps({'criteria':{'performed':{'trigger':'minecraft:impossible'}}},indent=2)+'\n'
        if not path.is_file() or path.read_text()!=text:
            path.write_text(text)
