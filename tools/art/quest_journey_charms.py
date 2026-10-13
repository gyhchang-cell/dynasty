"""Charm catalogue navigation and concise effects from existing runtime data.

Reads game code; never writes accessory mechanics or introduces collection gates.
"""
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = ('常驻', '白天', '夜晚', '在水中', '生命低于40%', '骑乘', '满血', '雷雨')
ATTRIBUTES = {0:'生命上限', 1:'护甲', 2:'抗击退', 3:'移速', 4:'攻击',
              5:'攻速', 6:'击退', 7:'攻击距离', 9:'生命上限', 11:'幸运', 12:'护甲韧性'}
EFFECTS = {1:'夜视', 2:'水下呼吸', 3:'抗火', 4:'抗性', 5:'再生', 8:'缓降', 11:'幸运',
           12:'再生', 21:'龙威', 22:'铁壁', 23:'疾风', 24:'威慑', 25:'天命', 26:'忠诚', 27:'内伤'}

@lru_cache(maxsize=1)
def specs():
    source=(ROOT/'src/main/java/com/dynasty/DynastyTrinkets.java').read_text()
    table=source.split('private static final Object[][] EXTRA_TABLE = {')[1].split('\n    };')[0]
    return {item:[float(v.strip().rstrip('DdFf')) for v in values.split(',')]
            for item,values in re.findall(r'\{"([a-z_]+)",([^}]+)\}',table)}

def number(value):
    # Runtime additions such as +0.35 knockback must retain both decimals.
    return ('+' if value>0 else '')+f'{value:.8g}'

def stat(code,value):
    if code not in ATTRIBUTES:return None
    percent=code in (3,4,5,9)
    return ATTRIBUTES[code]+number(value*100 if percent else value)+('%' if percent else '')

def mechanical_notes(item):
    row=specs().get(item)
    if row is None:
        source=(ROOT/'src/main/java/com/dynasty/DynastyTrinketTips.java').read_text()
        match=re.search(r'Map.entry\("'+re.escape(item)+r'", new String\[\]\{([^}]+)\}',source)
        if not match:return []
        notes=[re.sub(r'§.', '', s).strip() for s in re.findall(r'"([^"\n]+)"',match[1])]
        # Runtime boundaries/timers differ from the older hand-written tooltip.
        audited={
            'jade_cicada':['生命不高于30%时：抗性II、速度I。'],
            'storm_charm':['常驻抗性I；下雨或雷雨时另有力量II、速度I。'],
            'war_drum_charm':['常驻力量I；每3秒给12格内的己方宠物、铁/雪傀儡和帝国士兵力量I。'],
            'gold_seal_charm':['功名收益+25%；每60秒忠诚+2。与御玺佩的功名加成取较高者。'],
            'imperial_seal_charm':['生命上限+100、护甲+4；功名收益+40%，与金印加成取较高者。'],
            'tomb_candle':['常驻夜视；每2秒清除凋零和灼魂。'],
        }
        return ['佩戴：'+s.rstrip('。')+'。' for s in audited.get(item,notes)]
    grouped={}
    def append(condition,text,cost=False):
        if text:grouped.setdefault((int(condition),cost),[]).append(text)
    append(row[6],stat(row[0],row[1]),row[1]<0)
    append(row[6],stat(row[2],row[3]),row[3]<0)
    effect=int(row[4])
    if effect in EFFECTS:
        level=int(row[5])+(2 if effect==12 else 1)
        append(row[6],EFFECTS[effect]+str(level)+'级',effect==27)
    if len(row)>9:append(row[9],stat(row[7],row[8]),row[8]<0)
    notes=[('&c代价：' if cost else '佩戴：')+CONDITIONS[condition]+'，'+'、'.join(values)+'。'
           for (condition,cost),values in grouped.items()]
    # OnHit.index consumes columns12–14 only, independently of attribute conditions.
    if len(row)>12 and row[10]>0:
        code,value,chance=int(row[10]),row[11],int(row[12])
        ratio=f'{value*100:.1f}'.removesuffix('.0')+'%'
        proc={1:'吸血'+ratio+'（按伤害量回血）',
              2:'目标生命不高于'+ratio+'时斩杀（仅杂兵，生命上限≤80；玩家、Boss、神兽免斩）',
              3:'会心，额外伤害+'+ratio,
              4:'满血目标突袭，额外伤害+'+ratio,
              5:'连续击中同一目标，每层伤害+'+ratio+'（3秒内，最多6层）',
              6:'雷罚，附加'+number(value).lstrip('+')+'点伤害'}[code]
        notes.append('命中：'+proc+('；概率'+str(chance)+'%' if chance<100 else '')+'。')
    return notes

def describe(q):
    if q.get('section')!='dynasty_accessory_charm' or q['kind']!='item' or q.get('for_quest'):return
    notes=mechanical_notes(q['target'].split(':',1)[1])
    assert notes,'Missing charm effect reference: '+q['target']
    rest=[s for s in q['description'][1:] if s!='&d&l佩戴方法&r'
          and '必须实际佩戴，背包/副手不生效' not in s]
    goal=q['description'][0].replace('，背包持有即可。','；护符/万能槽佩戴生效。')
    q['description']=[goal,*notes,*rest]
    q['journey_effect_notes']=True

def arrange(section,center,top,header,allq,images):
    from quest_atlas import charm_sections,CHARM_SECTIONS
    from quest_journey import ASSET
    from quest_journey_layout import prerequisite_rows
    from boss_quest_guides import jump
    classes=charm_sections();byid={q['id']:q for q in section['quests']}
    guides=[q for q in section['quests'] if q['target']=='guide:slot_charm']
    groups=[[] for _ in range(4)]
    def group(q):
        if q.get('for_quest'):return group(byid[q['for_quest']])
        return classes[q['target'].split(':',1)[1]]
    for q in section['quests']:
        if q not in guides:
            i=group(q);q['journey_charm_group']=i;groups[i].append(q)
    for i,q in enumerate(guides):
        q.update(x=center+i*1.65,y=top,section=section['file']);allq.append(q)
    height=0.;start=top+3.5
    links=[]
    for band in range(2):
        band_height=0.
        for i in range(band*2,band*2+2):
            cx=center+(-4.95 if i%2==0 else 4.95)
            rows=prerequisite_rows(groups[i],columns=6)
            actual=[q for q in groups[i] if not q.get('for_quest')]
            anchor=actual[0]
            for row,quests in enumerate(rows):
                for col,q in enumerate(quests):
                    q.update(x=cx+(col-(len(quests)-1)/2)*1.65,y=start+row*1.8,section=section['file'])
                    allq.append(q)
            label=CHARM_SECTIONS[i].split(' · ')[0]
            images.append({'image':ASSET+'labels/charm_'+str(i)+'.png','x':cx,'y':start-1.4,
                'width':7.9,'height':.74,'rotation':0.,'alpha':255,'order':-1,
                'click':'#'+anchor['id'],'hover':[CHARM_SECTIONS[i],f'{len(actual)}件；点击查看本区首件饰品']})
            links.append(jump(label+' · '+str(len(actual))+'件',anchor['id']))
            band_height=max(band_height,len(rows)*1.8)
        start+=band_height+1.4;height=start-top
    header['description']=['按用途挑一件；收藏只检测持有，无须收齐。',*links,
        '道门的四件专属护符在修习页：',
        jump('司天印','1000000000030303'),jump('雷部印','1000000000030391'),
        jump('太清符匣','1000000000030393'),jump('玉虚符匣','1000000000030395')]
    for q in guides:
        q['description']=[s for s in q['description'] if not s.startswith('{"')]
        q['description'].extend(links)
    return height
