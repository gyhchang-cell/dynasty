"""Generate pack-wide bilingual/pinyin search metadata and verified chest-source hints."""
from pathlib import Path
import sys,json,re,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build/ui-python'))
from pypinyin import lazy_pinyin
ASSETS=ROOT/'src/main/resources/assets'
DOC=ROOT/'docs/ui-fixes-20261020'

def write(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    for locale in ('zh_cn','en_us'):
        p=ASSETS/'dynasty/lang'/f'{locale}.json';d=json.loads(p.read_text())
        names={'dragon_might':('龙威','Dragon Might'),'iron_wall':('铁壁','Iron Wall'),
          'swift_wind':('疾风','Swift Wind'),'intimidation':('威慑','Intimidation'),
          'loyalty':('民心','Loyalty'),'mandate_of_heaven':('天命','Mandate of Heaven')}
        for item,prefix,en in [('dynasty_potion','',''),('dynasty_splash_potion','喷溅型','Splash '),('dynasty_lingering_potion','滞留型','Lingering ')]:
            for effect,(zh,english) in names.items():d[f'item.dynasty.{item}.effect.{effect}']=prefix+zh+'药水' if locale=='zh_cn' else en+english+' Potion'
            for effect,(zh,english) in {'empty':('药水','Potion'),'water':('水瓶','Water Bottle'),'awkward':('粗制药水','Awkward Potion'),'thick':('浑浊药水','Thick Potion'),'mundane':('平凡药水','Mundane Potion')}.items():
                d[f'item.dynasty.{item}.effect.{effect}']=prefix+zh if locale=='zh_cn' else en+english
        # Source labels refer to the actual chest loot table identity.
        zh_sources={'imperial_tomb':'帝陵地宫','imperial_mausoleum':'帝王陵','ritual_circle':'法阵遗迹','temple':'神庙','palace_ruin':'宫殿遗迹','watchtower':'烽火台','barracks':'兵营','palace':'宫殿','pagoda':'宝塔','academy':'书院','great_wall':'长城','inn':'驿站'}
        for key,zh in zh_sources.items():d['tooltip.dynasty.chest.'+key]=zh if locale=='zh_cn' else key.replace('_',' ').title()
        d['block.dynasty.star_dial']='观星盘' if locale=='zh_cn' else 'Astronomical Dial'
        write(p,d)
    for locale,name in [('zh_cn','结构罗盘'),('en_us','Structure Compass')]:
        write(ASSETS/'explorerscompass/lang'/f'{locale}.json',{'item.explorerscompass.explorerscompass':name})
    # Keep guide vocabulary consistent with creative/JEI item names.
    for p in (ASSETS/'dynasty/patchouli_books').rglob('*.json'):
        s=p.read_text();n=s.replace('探险者指南针','结构罗盘').replace("Explorer’s Compass",'Structure Compass').replace("Explorer's Compass",'Structure Compass')
        if n!=s:p.write_text(n)
    languages={'zh_cn':{},'en_us':{}}
    base=Path('/Users/a15356015027/Public/.minecraft')
    with zipfile.ZipFile(base/'versions/Dynasty/Dynasty.jar') as z:
        languages['en_us'].update(json.loads(z.read('assets/minecraft/lang/en_us.json')))
    index=json.loads((base/'assets/indexes/5.json').read_text())
    entry=index['objects'].get('minecraft/lang/zh_cn.json')
    if entry:
        h=entry['hash'];p=base/'assets/objects'/h[:2]/h
        if p.exists():languages['zh_cn'].update(json.loads(p.read_text()))
    for jar in sorted((ROOT/'modpack/mods').glob('*.jar')):
        if 'helper' in jar.name or 'audit' in jar.name:continue
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                m=re.fullmatch(r'assets/[^/]+/lang/(zh_cn|en_us)\.json',n)
                if m:
                    try:languages[m[1]].update(json.loads(z.read(n)))
                    except (ValueError,UnicodeDecodeError):pass
    for p in sorted(ASSETS.glob('*/lang/*.json')):
        if p.stem in languages:languages[p.stem].update(json.loads(p.read_text()))
    aliases={}
    for key in sorted(set(languages['en_us'])|set(languages['zh_cn'])):
        if not key.startswith(('item.','block.')):continue
        zh=languages['zh_cn'].get(key,'');en=languages['en_us'].get(key,'')
        if not isinstance(zh,str) or not isinstance(en,str):continue
        syllables=lazy_pinyin(re.sub(r'§.','',zh)) if zh else []
        words=[zh,en,''.join(syllables),' '.join(syllables),''.join(s[0] for s in syllables if s),key.split('.',2)[-1].replace('_',' ')]
        aliases[key]=list(dict.fromkeys(w.lower().strip() for w in words if w.strip()))
    aliases['item.explorerscompass.explorerscompass']+=['探险者指南针',"explorer's compass",'explorers compass','结构指南针','jiegouluopan','jg lp']
    aliases['item.dynasty.creature_compass']+=['生物指南针','mob compass','entity compass']
    write(ASSETS/'dynasty/search_aliases.json',aliases)
    # Traverse nested loot-table references and only include actual item entries.
    tables={p.relative_to(ROOT/'src/main/resources/data/dynasty/loot_tables').with_suffix('').as_posix():json.loads(p.read_text()) for p in (ROOT/'src/main/resources/data/dynasty/loot_tables').rglob('*.json')}
    def items(obj,seen):
        if isinstance(obj,dict):
            if obj.get('type')=='minecraft:item':yield obj['name']
            if obj.get('type')=='minecraft:loot_table' and obj.get('name','').startswith('dynasty:'):
                ref=obj['name'][8:]
                if ref not in seen:yield from items(tables.get(ref,{}),seen|{ref})
            for v in obj.values():yield from items(v,seen)
        elif isinstance(obj,list):
            for v in obj:yield from items(v,seen)
    sources={}
    for table,obj in tables.items():
        if table.startswith('chests/'):
            for item in sorted(set(items(obj,{table}))):sources.setdefault(item,[]).append('tooltip.dynasty.chest.'+table.split('/')[-1])
    write(ASSETS/'dynasty/accessory_sources.json',sources)
    own=json.loads((ASSETS/'dynasty/lang/zh_cn.json').read_text())
    duplicates={}
    for k,v in own.items():
        if k.startswith(('item.dynasty.','block.dynasty.')):duplicates.setdefault(v,[]).append(k)
    duplicates={v:ks for v,ks in duplicates.items() if len(ks)>1}
    write(DOC/'item-name-audit.json',{'searchable_translation_keys':len(aliases),'chest_source_items':len(sources),'duplicate_display_names':duplicates,'note':'Language keys include block/item aliases and potion variants; runtime registry audit distinguishes real duplicate items.'})
    print('Search aliases:',len(aliases),'item/block keys; chest sources:',len(sources))
if __name__=='__main__':main()
