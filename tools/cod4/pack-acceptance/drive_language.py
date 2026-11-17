"""Actual full-pack hot zh/en/zh, native layout text, R/back history, scroll and negatives."""
from drive import *
import re,zipfile
ids=['fire_talisman','thunder_talisman','wind_talisman','stealth_talisman','vajra_talisman','soul_talisman','return_talisman']
jar=R/'build/cod4-pack-20261022/language-repair/dynasty-1.4.0.jar'
with zipfile.ZipFile(jar) as z:translations={lang:json.loads(z.read('assets/dynasty/lang/'+lang+'.json')) for lang in ['zh_cn','en_us']}
norm=lambda s:re.sub(r'\s+','',s)
checks=[]
PREFIX=(sys.argv[2]+'-') if len(sys.argv)>2 else ''
def check(ok,label,state=None):
 checks.append({'passed':bool(ok),'check':label,'state_file':state})
 (O/(PREFIX+'language-live-checks.json')).write_text(json.dumps(checks,ensure_ascii=False,indent=2))
 if not ok:raise AssertionError(label)
def validate_info(s,item,lang,label):
 expected=[translations[lang]['jei.dynasty.talisman.'+key] for key in ['source.'+item,'use.'+item,'single_use']]
 check(s['language']==lang and s['jeiScreen']['category']=='jei:information',label+' native selected language/category',label+'-result.json')
 layouts=s['jeiScreen']['layouts'];check(len(layouts)==1,label+' one information recipe, no duplicates')
 row=layouts[0];check(row['description']==expected,label+' description components in current language')
 wrapped=[line for box in row['actualWrappedText'] for line in box['lines']]
 check(norm(''.join(wrapped))==norm(''.join(expected)),label+' actual native cached wrapped lines match current language')
wait_file('READY.json',600);print('Repair full-pack actual world ready',flush=True)
for phase,lang in [('cold-zh','zh_cn'),('hot-en','en_us'),('hot-zh','zh_cn')]:
 stage=PREFIX+phase
 if phase!='cold-zh':command(stage+'-reload','language',lang=lang)
 command(stage+'-talismans','talismans')
 audit=load(O/(stage+'-talismans-audit.json'));check(len(audit)==7,stage+' all seven actual lookups and negative checks')
 for item in ids:
  command(stage+'-'+item+'-seed-inventory-recipe','jei',item='dynasty:'+item,role='OUTPUT')
  label=stage+'-'+item+'-info';s=command(label,'info',item='dynasty:'+item);validate_info(s,item,lang,label)
  slot=next(x for row in s['jeiScreen']['layouts'] for x in row['slots'] if 'dynasty:'+item in x['items'])
  r=command(stage+'-'+item+'-native-R','nativeKey',key=82,x=slot['x'],y=slot['y'])
  check(any(x.get('recipe') in audit[item]['recipeIds'] for x in r['jeiScreen']['layouts']),stage+' '+item+' native R original craft recipe')
  label=stage+'-'+item+'-native-back';b=command(label,'nativeKey',key=259);validate_info(b,item,lang,label)
  command(stage+'-'+item+'-scroll-bottom','nativeMouse',x=558,y=311,button=0)
  e=command(stage+'-'+item+'-escape','nativeKey',key=256);check(e['screen']=='net.minecraft.client.gui.screens.inventory.InventoryScreen',stage+' '+item+' Escape inventory')
  print(stage,item,'native description, wrapped layout, R/back/Escape OK',flush=True)
 s=command(stage+'-paper-recipe','jei',item='dynasty:talisman_paper',role='OUTPUT')
 slot=next(x for row in s['jeiScreen']['layouts'] for x in row['slots'] if x['role']=='OUTPUT' and 'dynasty:talisman_paper' in x['items'])
 s=command(stage+'-paper-native-U','nativeKey',key=85,x=slot['x'],y=slot['y']);check(s['jeiScreen']['category']=='minecraft:crafting',stage+' native paper U crafting usages')
 print(stage,'complete',flush=True)
command(PREFIX+'post-language-world','close')
for name,item,opts in [('native-gui-final','dynasty:lie_gong',{'variant':'gui'}),('chinese-full-draw20','dynasty:dragon_bow',{})]:
 command('start-'+name,'bow',name='bow-'+name,item=item,**opts);wait_file('bow-'+name+'-result.json')
(O/'LANGUAGE-COMPLETE.json').write_text(json.dumps({'checks':len(checks),'passed':sum(x['passed'] for x in checks),'sequence':['zh_cn','en_us','zh_cn'],'rendered_layout_probed':True},indent=2))
tmp=O/'command.pending';tmp.write_text(json.dumps({'id':'finish-language-run','op':'finish'}));os.replace(tmp,O/'command.json')
print('Completed language repair acceptance; normal exit requested',flush=True)
