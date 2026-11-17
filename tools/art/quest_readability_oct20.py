"""A final presentation-only pass. Quest identity, progress and layout remain byte-for-byte equal."""
import re,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPLACE={
 '取得并持有':'获得','，放入背包；不收走物品。':'。','，放入背包。':'。',
 '不收走物品。':'','等待自动记录；任务不收走物品。':'',
 '服务器保存探索/击杀进度；提前完成也会记录，任务解锁后自动检测。':'提前完成也会记录。',
 '原任务与奖励 ID 保留，旧档已领取不会重复增加。':'',
 '老玩家已完成节点保留，不必重领。':'',
 '阅读页手动勾选且没有奖励，其余任务按实际行为检测。':'阅读页可手动勾选。',
 '使用本流派王朝兵器击杀敌对生物，或给其他王朝兵器搭配本流派饰品。':'使用本流派兵器，或佩戴本流派饰品击杀敌对生物。',
 '普通怪给1点历练，强敌最多8点；同一敌人只结算一次。':'普通怪历练+1，强敌最多+8。',
 '流派阶数属于玩家，切换装备、死亡不清零。每阶提高伤害，升级所需历练递增；10阶以后仍可继续成长。':'流派阶数提高伤害，换装、死亡保留；10阶后仍可成长。',
 '探险者指南针':'结构罗盘','背包持有即可。':'','持有一份即可':'获得材料',
 '取得':'获得','留意概率与工具条件':'留意掉落条件','（概率取得）':'（概率）',
 '点击查看 · ':'','（地点 / 打法 / 召唤）':'',
 '保留原武器等级、历练、附魔与名称。普通合成不继承历练。':'继承等级、历练、附魔和名称；普通合成不继承历练。',
 '不要攻击自己的军队。':'','选择阵型与人数':'选择兵员和阵位',
 '右键虎符选阵型':'右键虎符编队','仅把试卷放背包不算答题':'需实际答题',
 '放入 Curios 的':'放入','必须实际佩戴，背包/副手不生效':'佩戴生效',
 '；护符/万能槽佩戴生效':'','，背包持有即可':'','，持有即可':'',
 '不是仅获得试卷，也不要求先升到天子。':'','不用一口气清空所有支线。':'',
 '任务检测龙晶，不要求精准采集矿石；':'挖矿掉龙晶；',
 '每位玩家只授予一次':'每人限一次','每位玩家一次':'每人限一次',
}
def plain(s):return re.sub(r'[&§][0-9a-fk-or]','',s,flags=re.I)
def shorten(s):
    for a,b in REPLACE.items():s=s.replace(a,b)
    return s.strip().replace('，。','。').replace('；。','。').replace('。。','。')
def paint(s,first=False):
    s=plain(s)
    if first and (m:=re.match(r'获得(.+?×\d+)(.*)',s)):
        return '&6获得 &e'+m[1]+'&r'+paint(m[2])
    # Colour short semantic phrases, never an entire multi-line paragraph.
    tokens={};counter=0
    def mark(pattern,color):
        nonlocal s,counter
        def put(m):
            nonlocal counter
            key=f'\ue000{counter}\ue001';counter+=1;tokens[key]='&'+color+m[0]+'&r';return key
        s=re.sub(pattern,put,s)
    mark(r'[^，。；：\s＋+→]+×\d+','a')
    mark(r'(?<=搜索[“「])[^”」]+','e')
    mark(r'右键|潜行右键|左键|佩戴|击败|合成|采集|进入|获得|放置|召唤|答题|部署|开战','6')
    mark(r'不能|无法|不继承|不生效|会复位|危险|战损|消耗|先收阵','c')
    mark(r'(?<![\w])[XYZY]=-?\d+(?:\s*至\s*-?\d+)?|\d+(?:～|~|至)\d+\s*格|\d+秒|\d+分钟','b')
    mark(r'^(?:宝箱|掉落|合成|锻造台|佩戴|命中|提示|材料|目标|位置|操作|代价|返回|前往|完成条件)(?=：)','e')
    for key,value in tokens.items():s=s.replace(key,value)
    if first and '&' not in s:s='&e'+s+'&r'
    return s
def apply(chapters):
    from quest_story import recipe_index
    recipes=recipe_index()
    immutable=lambda q:{k:v for k,v in q.items() if k not in {'description','subtitle','display_title','readability_oct20'}}
    before={q['id']:copy.deepcopy(immutable(q)) for c in chapters for q in c['quests']}
    report=[]
    for c in chapters:
        for q in c['quests']:
            old=q['description'];new=[];seen=set();recipe_seen=False
            for s in old:
                if s.startswith('{image:'):
                    new.append(s);continue
                if s.startswith('{"'):
                    d=json.loads(s)
                    if isinstance(d.get('text'),str):d['text']=shorten(d['text'])
                    new.append(json.dumps(d,ensure_ascii=False));continue
                s=shorten(s)
                # An evolution already has its own correct smithing recipe in “how”.
                # A later generic alternate recipe is redundant on that same page.
                if '→' in s and ('×' in s or plain(s).startswith(('合成：','锻造台：'))):
                    if recipe_seen:
                        tail=s.split('。',1)[1] if '。' in s else ''
                        if not tail.strip():continue
                        s=tail
                    else:recipe_seen=True
                if plain(s).startswith('合成：') and q.get('recipe_ids'):
                    candidates=recipes.get(q.get('target'),[])
                    if candidates and candidates[0]['type']=='minecraft:smithing_transform':s=s.replace('合成：','锻造台：',1)
                if not s or plain(s) in {'持有即可。','备料','佩戴方法','获得材料'}:continue
                normalized=re.sub(r'\s+','',plain(s)).rstrip('。')
                if normalized in seen:continue
                seen.add(normalized)
                new.append(paint(s,not new))
            # Both source and actual drop text existed for the guaranteed first-kill tokens.
            if q.get('target') in {'dynasty:sky_token','dynasty:sea_token'}:
                new=[s for s in new if not (plain(s).startswith('掉落：') and '概率' in s)]
            if not new:new=['&e查看目标与奖励。&r']
            q['description']=new
            if '探险者指南针' in q.get('display_title',q['title']):q['display_title']=q.get('display_title',q['title']).replace('探险者指南针','结构罗盘')
            subtitle=shorten(plain(q.get('subtitle','')))
            q['subtitle']=subtitle.replace('主线 · 实地探索与战斗','主线').replace('主线 · 按连线前进','主线').replace('备料 · 获得材料','备料')
            q['readability_oct20']=True
            assert before[q['id']]==immutable(q),'Gameplay or layout changed: '+q['id']
            report.append({'id':q['id'],'before_chars':sum(map(len,old)),'after_chars':sum(map(len,new))})
    out=ROOT/'docs/ui-fixes-20261020';out.mkdir(exist_ok=True)
    (out/'quest-presentation-audit.json').write_text(json.dumps({'quests':len(report),'all_gameplay_and_layout_fields_equal':True,'nodes':report},indent=2))
