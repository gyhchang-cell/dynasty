"""School accessory expansion: gameplay metadata only; artwork is authored separately.

The two upgrade chains in each school consume their predecessor, never unlock the
main story, and use ordinary existing materials. Keep IDs stable across rebuilds.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources'
# id, zh, en, school, slot, two vanilla stats, passive kind/value, ingredients, art subject
ROWS = [
 ('pojun_ring','破军戒','Army-Breaker Ring','sword','ring',[5,.04,-1,0],'melee',.12,['refined_steel','jade','silk'], 'angular dark steel ring with a single red sword-shaped ruby, restrained bronze dragon claws'),
 ('wuqu_sword_knot','武曲剑结','War-Star Sword Knot','sword','belt',[1,4,-1,0],'melee',.20,['refined_steel','silk','bronze_ingot','blueprint'], 'crimson woven Chinese sword knot, bronze crossed-sword plaque, two flowing red silk tassels'),
 ('baizhan_ring','百战戒','Hundred-Battles Ring','sword','ring',[0,120,5,.06],'melee',.28,['pojun_ring','dragon_crystal','refined_steel','jade'], 'heavy battle-worn black steel signet ring with sculpted golden tiger face and deep garnet eyes'),
 ('qixing_sword_knot','七星剑结','Seven-Star Sword Knot','sword','belt',[5,.08,-1,0],'melee',.36,['wuqu_sword_knot','xuantian_jade','silk','dragon_crystal'], 'seven-star silver and gold openwork sword pendant, seven small sapphire studs, intricate midnight blue Chinese knot and tapered silk tassels'),
 ('xuanjia_clasp','玄甲扣','Black-Armour Clasp','guard','body',[12,8,-1,0],'melee',.10,['refined_steel','bronze_ingot','jade'], 'square overlapping black iron armour clasp, prominent bronze mountain ridge relief, strong beveled corners'),
 ('shanyue_bracelet','山岳镯','Mountain Bracelet','guard','bracelet',[12,14,0,120],'none',0,['jade','jade','refined_steel','silk'], 'thick jade stone bracelet carved into mountain ridges, dark green polished stone with restrained brass bindings'),
 ('beichen_heartguard','北辰护心镜','North-Star Heartguard','guard','body',[12,20,-1,0],'melee',.24,['xuanjia_clasp','dragon_crystal','refined_steel','blueprint'], 'round convex heavy armour heartguard, central icy north star, layered dark iron plates and silver radial engravings, two leather straps'),
 ('xuanyue_armlet','玄岳臂环','Mystic-Mountain Armlet','guard','bracelet',[12,30,-1,0],'toughness',.006,['shanyue_bracelet','xuantian_jade','emperor_bone','refined_steel'], 'massive segmented dark jade armlet with sculpted gold tortoise guardian and angular mountain relief, jade and gold contrast'),
 ('yanling_thumbring','雁翎扳指','Wild-Goose Thumb Ring','archer','ring',[3,.04,-1,0],'arrow',.12,['jade','silk','minecraft:feather'], 'traditional pale green jade archery thumb ring, cylindrical open bore visible, sculpted silver goose feather on outer face'),
 ('shenji_quiver','神机箭囊','Ingenious Quiver','archer','back',[1,6,-1,0],'arrow',.18,['arrow_quiver','refined_steel','silk','blueprint'], 'complete long elegant leather archery quiver with intricate bronze mechanical clasps, three ivory-feather arrows, leather shoulder strap'),
 ('guanri_thumbring','贯日扳指','Sun-Piercer Thumb Ring','archer','ring',[12,8,-1,0],'arrow',.28,['yanling_thumbring','dragon_crystal','jade','minecraft:gold_ingot'], 'gold and amber archery thumb ring with open cylindrical bore, raised sunburst relief and a small carved soaring hawk'),
 ('zhuiri_quiver','逐日箭囊','Sun-Chaser Quiver','archer','back',[0,160,-1,0],'arrow',.36,['shenji_quiver','sky_token','dragon_crystal','silk'], 'luxurious ivory and gold archery quiver, fiery phoenix-wing shell panels, three red-gold feather arrows and crimson shoulder strap'),
 ('lingwen_pendant','灵纹佩','Spirit-Script Pendant','talisman','necklace',[0,80,-1,0],'edict',.15,['jade','talisman_paper','silk'], 'translucent mint jade circular Taoist pendant with inset cinnabar geometric seal, fine gold frame, silk necklace cord'),
 ('leibu_seal','雷部印','Thunder-Ministry Seal','talisman','charm',[12,8,-1,0],'edict',.22,['cinnabar','bronze_ingot','talisman_paper','blueprint'], 'square bronze Taoist seal block with a three dimensional coiling thunder serpent handle, deep violet inlay, carved cinnabar bottom edge'),
 ('ziwei_talisman_chain','紫微符链','Purple-Star Talisman Chain','talisman','necklace',[0,220,-1,0],'edict',.32,['lingwen_pendant','xuantian_jade','silk','dragon_crystal'], 'elegant violet jade talisman necklace on looped gold chain, central star-shaped purple crystal, three hanging white jade seal tablets'),
 ('taiqing_talisman_case','太清符匣','Supreme-Purity Talisman Casket','talisman','charm',[12,16,-1,0],'edict',.40,['leibu_seal','sky_token','xuantian_jade','silk'], 'open ivory and gold Taoist talisman casket with blue jade corners, three neatly nested cinnabar seal scrolls, delicate cloud relief and small purple silk cord'),
 ('wanjun_ring','万钧戒','Ten-Thousand-Force Ring','sword','ring',[0,260,5,.10],'melee',.44,['baizhan_ring','xuantian_jade'], 'massive silver ring with sculpted gold thunder lion and faceted crimson central stone'),
 ('tianheng_sword_knot','天衡剑结','Heaven-Balance Sword Knot','sword','belt',[5,.12,12,10],'melee',.52,['qixing_sword_knot','sky_token'], 'white silk sword knot bearing a suspended gold balance-shaped crossguard and cyan crystal, flowing white tassels'),
 ('zhenhai_heartguard','镇海护心镜','Sea-Calming Heartguard','guard','body',[12,30,0,300],'melee',.38,['beichen_heartguard','xuantian_jade'], 'bronze and turquoise heavy circular chest mirror with sculpted sea serpent rim and wave relief, leather fixing straps'),
 ('buzhou_armlet','不周臂环','Buzhou Armlet','guard','bracelet',[12,30,0,400],'melee',.76,['xuanyue_armlet','sky_token'], 'angular black meteor iron armlet with a towering gold mountain crest, inset emerald stone and articulated links'),
 ('sheyue_thumbring','射月扳指','Moon-Shooter Thumb Ring','archer','ring',[12,16,3,.06],'arrow',.44,['guanri_thumbring','xuantian_jade'], 'translucent midnight blue jade archer thumb ring with silver crescent moon relief and tiny pearl inlay, cylindrical open bore'),
 ('jinwu_quiver','金乌箭囊','Golden-Crow Quiver','archer','back',[0,320,1,10],'arrow',.52,['zhuiri_quiver','sky_token'], 'black lacquer quiver with elaborate gold three-legged sun crow relief, three dark red arrow feathers, complete crimson shoulder strap'),
 ('sanqing_talisman_chain','三清符链','Three-Purities Talisman Chain','talisman','necklace',[0,400,12,12],'edict',.48,['ziwei_talisman_chain','xuantian_jade'], 'fine silver Taoist necklace with three ivory jade cloud-shaped tablets and a brilliant emerald center, pale gold chain'),
 ('yuxu_talisman_case','玉虚符匣','Jade-Void Talisman Casket','talisman','charm',[12,24,0,240],'edict',.56,['taiqing_talisman_case','sky_token'], 'ornate green jade Taoist scroll casket with hinged dragon-cloud golden lid, open showing three violet silk scrolls, complete isolated object'),
]
LABELS = {'melee':('近战伤害','Melee damage'),'arrow':('箭矢伤害','Arrow damage'), 'edict':('律令兵器伤害','Edict weapon damage')}
ITEMS = {}
for ident,zh,en,school,slot,stats,kind,value,recipe,art in ROWS:
    zh_effect,en_effect = ('','') if kind=='none' else (
        ('每点护甲韧性转为 +0.6% 近战伤害（最多 +60%）','Each toughness point grants +0.6% melee damage (max +60%)')
        if kind=='toughness' else (f'{LABELS[kind][0]} +{value:.0%}',f'{LABELS[kind][1]} +{value:.0%}'))
    ITEMS[ident] = dict(id=ident,zh=zh,en=en,school=school,slot=slot,kind='accessory',
        spec=stats+[0,0,0],bonus_kind=kind,bonus=value,recipe=[x if ':' in x else 'dynasty:'+x for x in recipe],
        zh_effect=zh_effect,en_effect=en_effect,art=art)
TRINKETS = {k:(v['zh'],v['en'],k,(255,255,255),v['recipe'],tuple(v['spec'])) for k,v in ITEMS.items()}
TEXTURE_SIZE = {k:128 for k in ITEMS}

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def main():
    for school in ('sword','guard','archer','talisman'):
        for rank in (1,5,15,30):
            write(RES/f'data/dynasty/advancements/refine_{school}_{rank}.json',{
                'criteria':{'refined':{'trigger':'minecraft:impossible'}}})
    write(ROOT/'docs/content/school-accessories-v2.json',{'version':2,'items':list(ITEMS.values())})
    for k,v in ITEMS.items():
        upgraded=v['recipe'][0].split(':')[-1] in ITEMS
        recipe=({'type':'minecraft:smithing_transform','template':{'item':'dynasty:blueprint'},
                 'base':{'item':v['recipe'][0]},'addition':{'item':v['recipe'][1]},'result':{'item':'dynasty:'+k}}
                if upgraded else {'type':'minecraft:crafting_shapeless','category':'equipment',
                 'ingredients':[{'item':x} for x in v['recipe']], 'result':{'item':'dynasty:'+k}})
        write(RES/f'data/dynasty/recipes/{k}.json',recipe)
        write(RES/f'assets/dynasty/models/item/{k}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+k}})
        write(RES/f'data/dynasty/advancements/recipes/school_accessories/{k}.json',{
          'parent':'minecraft:recipes/root','criteria':{'material':{'trigger':'minecraft:inventory_changed',
          'conditions':{'items':[{'items':[v['recipe'][0]]}]}}},'rewards':{'recipes':['dynasty:'+k]}})
    for locale in ['zh_cn','en_us']:
        p=RES/f'assets/dynasty/lang/{locale}.json'; data=json.loads(p.read_text()); zh=locale=='zh_cn'
        for k,v in ITEMS.items():
            data['item.dynasty.'+k]=v['zh' if zh else 'en']
            data['tooltip.dynasty.accessory_damage.'+k]=v['zh_effect' if zh else 'en_effect']
        write(p,data)
    p=ROOT/'src/main/java/com/dynasty/DynastyTrinkets.java'; text=p.read_text()
    lines=['        // BEGIN SCHOOL ACCESSORIES V2 (gen_trinkets7.py)']
    for k,v in ITEMS.items():
        a,b,c,d,e,f,g=v['spec']
        lines.append(f'        {{"{k}", {a}, {float(b)}D, {c}, {float(d)}D, {e}, {f}, {g}}},')
    lines.append('        // END SCHOOL ACCESSORIES V2')
    block='\n'.join(lines)
    if '// BEGIN SCHOOL ACCESSORIES V2' in text:
        text=re.sub(r'        // BEGIN SCHOOL ACCESSORIES V2.*?        // END SCHOOL ACCESSORIES V2',block,text,flags=re.S)
    else:text=text.replace('private static final Object[][] EXTRA_TABLE = {','private static final Object[][] EXTRA_TABLE = {\n'+block)
    p.write_text(text)
    lines=['package com.dynasty;','','/** Generated by gen_trinkets7.py; do not edit. */',
      'final class DynastyAccessoryData {','    record Bonus(String school, String kind, double amount) {}',
      '    static Bonus get(String id) {','        return switch (id) {']
    for k,v in ITEMS.items():lines.append(f'            case "{k}" -> new Bonus("{v["school"]}", "{v["bonus_kind"]}", {v["bonus"]});')
    lines+=['            default -> null;','        };','    }','}']
    (ROOT/'src/main/java/com/dynasty/DynastyAccessoryData.java').write_text('\n'.join(lines)+'\n')
    print('School accessories: 24 items, 8 three-tier NBT-preserving upgrade chains')

if __name__=='__main__':main()
