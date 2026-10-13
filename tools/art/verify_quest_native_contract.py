"""Check QA plan against deployed book and exact local FTB class ABI, without Java.

This is source preparation, never native acceptance or a compilation result.
--write-plan refreshes the QA-only resource plan after a deliberate book update.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/quests-journey-v3'
QA=ROOT/'tools/art/quest-integration-qa'
PLAN=QA/'resources/dynasty-quest-qa-plan.json'

def class_abi(data):
    """Read JVM member descriptors only. Does not load or execute class bytecode."""
    assert data[:4]==b'\xca\xfe\xba\xbe'
    pos=8
    def number(n):
        nonlocal pos
        result=int.from_bytes(data[pos:pos+n],'big');pos+=n;return result
    pool=[None]*number(2);i=1
    while i<len(pool):
        tag=number(1)
        if tag==1:
            n=number(2);pool[i]=data[pos:pos+n].decode('utf-8',errors='replace');pos+=n
        elif tag in (3,4):pos+=4
        elif tag in (5,6):pos+=8;i+=1
        elif tag in (7,8,16,19,20):pool[i]=number(2)
        elif tag in (9,10,11,12,17,18):pos+=4
        elif tag==15:pos+=3
        else:raise ValueError(f'Unsupported class constant tag: {tag}')
        i+=1
    number(2);number(2);number(2)
    interfaces=number(2);pos+=2*interfaces
    def members():
        nonlocal pos
        result={}
        for _ in range(number(2)):
            number(2);name=pool[number(2)];descriptor=pool[number(2)]
            for _ in range(number(2)):
                number(2);n=number(4);pos+=n
            result.setdefault(name,[]).append(descriptor)
        return result
    return {'fields':members(),'methods':members()}

def make_plan(book):
    quests={q['id']:q for c in book for q in c['quests']}
    plan={'book_sha256':hashlib.sha256((DOC/'last-deployed-book.json').read_bytes()).hexdigest(),
          'quests':len(quests),'chapters':len(book),'inline':[],'links':[],'cards':[],'hover':[]}
    for c in book:
        for q in c['quests']:
            for i,line in enumerate(q['description']):
                if line.startswith('{image:'):
                    image=re.search(r'^\{image:([^ ]+) width:220 height:110 align:center fit:true\}$',line)
                    assert image,line
                    plan['inline'].append({'quest':q['id'],'line':i,'image':image[1]})
    pairs=[('1000000000041002','1000000000030000'),
           ('1000000000010026','10d3ed95df54c36f'),
           ('10d379d49ab6889c','10000000000000bc'),
           ('10d379d49ab6889c','1000000000030303'),
           ('10d36abe86ae6899','1000000000030001'),
           ('100000000003030b','1000000000030300')]
    healing=next(q for q in quests.values() if q.get('journey_potion')=='minecraft:healing')
    pairs.extend([('1000000000c40029',healing['id']),(healing['id'],'1000000000c40029')])
    for item,visit in [('old_weapon_rack','1000000000072000'),('herb_spot','1000000000072010'),('abandoned_armory','1000000000072020')]:
        site=next(q for q in quests.values() if q.get('cod4_item')==item)
        pairs.append((site['id'],visit))
    for source,target in pairs:
        jumps=[json.loads(s).get('clickEvent',{}) for s in quests[source]['description'] if s.startswith('{"')]
        assert {'action':'change_page','value':target} in jumps,(source,target)
        plan['links'].append({'quest':source,'target':target})
    for c in book:
        for image in c.get('images',[]):
            if image.get('click') and (image['image'].rsplit('/',1)[-1] in {f'charm_{i}.png' for i in range(4)}
                                      or c['file']=='dynasty_home' and image['image'].endswith('/dynasty_story_01.png')):
                target=image['click'].removeprefix('#')
                plan['cards'].append({'chapter':c['id'],'image':image['image'],'x':image['x'],'y':image['y'],
                                      'target':target,'target_type':'quest' if target in quests else 'chapter'})
    for key in ['10d36abe86ae6899','100000000003030b','1000000000090020']:
        q=quests[key];assert q['hide_dependency_lines']
        plan['hover'].append({'quest':key,'deps':q['deps']})
    assert len(plan['inline'])==67 and len({x['image'] for x in plan['inline']})==26
    assert len(plan['cards'])==5 and len(plan['links'])==11
    return plan

# Exact descriptors of every non-Minecraft reflected API used by the new probe.
API={
 'library':{
  'ui/Widget':{'fields':{'parent':'Ldev/ftb/mods/ftblibrary/ui/Panel;'},'methods':{k:'()I' for k in ['getX','getY','getWidth','getHeight']}|{'isMouseOver':'()Z'}},
  'ui/Panel':{'methods':{'getWidgets':'()Ljava/util/List;','getScrollX':'()D','getScrollY':'()D'}},
  'ui/TextField':{'fields':{'component':'Lnet/minecraft/network/chat/Component;'}},
  'ui/ScreenWrapper':{'methods':{'render':'(Lnet/minecraft/client/gui/GuiGraphics;IIF)V','mouseClicked':'(DDI)Z','mouseReleased':'(DDI)Z','mouseScrolled':'(DDD)Z'}},
  'util/client/ImageComponent':{'fields':{'image':'Ldev/ftb/mods/ftblibrary/icon/Icon;','width':'I','height':'I','fit':'Z'}},
  'config/ImageResourceConfig':{'methods':{'getResourceLocation':'(Ldev/ftb/mods/ftblibrary/icon/Icon;)Lnet/minecraft/resources/ResourceLocation;'}}
 },
 'quests':{
  'client/ClientQuestFile':{'methods':{'getQuestScreen':'()Ljava/util/Optional;','openBookToQuestObject':'(J)V'}},
  'client/gui/quests/QuestScreen':{'fields':{'chapterPanel':'Ldev/ftb/mods/ftbquests/client/gui/quests/ChapterPanel;','questPanel':'Ldev/ftb/mods/ftbquests/client/gui/quests/QuestPanel;','viewQuestPanel':'Ldev/ftb/mods/ftbquests/client/gui/quests/ViewQuestPanel;','selectedChapter':'Ldev/ftb/mods/ftbquests/quest/Chapter;'},'methods':{'closeQuest':'()V','getZoom':'()I','addZoom':'(D)V'}},
  'client/gui/quests/ChapterPanel':{'methods':{'setExpanded':'(Z)V'}},
  'client/gui/quests/ViewQuestPanel':{'fields':{'panelContent':'Ldev/ftb/mods/ftblibrary/ui/BlankPanel;','panelText':'Ldev/ftb/mods/ftblibrary/ui/BlankPanel;'},'methods':{'getViewedQuest':'()Ldev/ftb/mods/ftbquests/quest/Quest;'}},
  'client/gui/ImageComponentWidget':{'fields':{'index':'I'},'methods':{'getComponent':'()Ldev/ftb/mods/ftblibrary/util/client/ImageComponent;','draw':'(Lnet/minecraft/client/gui/GuiGraphics;Ldev/ftb/mods/ftblibrary/ui/Theme;IIII)V'}},
  'client/gui/quests/QuestPanel':{'methods':{'scrollTo':'(DD)V','renderConnection':'(Ldev/ftb/mods/ftblibrary/ui/Widget;Ldev/ftb/mods/ftbquests/client/gui/quests/QuestButton;Lcom/mojang/blaze3d/vertex/PoseStack;Lcom/mojang/blaze3d/vertex/BufferBuilder;FIIIIIFLcom/mojang/blaze3d/vertex/Tesselator;)V'}},
  'client/gui/quests/QuestButton':{'fields':{'quest':'Ldev/ftb/mods/ftbquests/quest/Quest;'}},
  'client/gui/quests/ChapterImageButton':{'fields':{'chapterImage':'Ldev/ftb/mods/ftbquests/quest/ChapterImage;'}},
  'quest/ChapterImage':{'methods':{'getClick':'()Ljava/lang/String;'}},
  'quest/Quest':{'methods':{'shouldHideDependencyLines':'()Z'}}
 }
}

def verify_abi():
    report=[];count=0
    for group,stem,version in [('library','ftb-library-forge','2001.2.13'),('quests','ftb-quests-forge','2001.4.22')]:
        mapped=f'{version}_mapped_official_1.20.1'
        jar=Path.home()/f'.gradle/caches/forge_gradle/deobf_dependencies/dynasty_local_qa/{stem}/{mapped}/{stem}-{mapped}.jar'
        prefix='dev/ftb/mods/'+('ftblibrary/' if group=='library' else 'ftbquests/')
        with zipfile.ZipFile(jar) as archive:
            for cls,contract in API[group].items():
                data=archive.read(prefix+cls+'.class');actual=class_abi(data)
                for kind,names in contract.items():
                    for name,descriptor in names.items():
                        assert descriptor in actual[kind].get(name,[]),(cls,kind,name,descriptor,actual[kind].get(name))
                        count+=1
                report.append({'class':prefix+cls,'sha256':hashlib.sha256(data).hexdigest(),'members':contract})
    return count,report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-plan',action='store_true');parser.add_argument('--report',type=Path)
    args=parser.parse_args();book=json.loads((DOC/'last-deployed-book.json').read_text());expected=make_plan(book)
    if args.write_plan:PLAN.write_text(json.dumps(expected,ensure_ascii=False,indent=2)+'\n')
    assert json.loads(PLAN.read_text())==expected,'QA resource plan differs from deployed book; deliberate --write-plan required'
    count,classes=verify_abi()
    report={'scope':'Static QA-only resource/API contract; no Java compilation or native execution',
            'plan_sha256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),'api_members_verified':count,
            'inline_placements':len(expected['inline']),'unique_figures':26,'text_clicks':len(expected['links']),
            'image_clicks':len(expected['cards']),'hover_samples':len(expected['hover']),'classes':classes,
            'native_status':'pending; do not treat these contract checks as game acceptance'}
    if args.report:args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='classes'},ensure_ascii=False))

if __name__=='__main__':main()
