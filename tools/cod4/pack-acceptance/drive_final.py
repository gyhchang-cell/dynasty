from drive import *
wait_file('READY.json',600);print('Final private production world ready',flush=True)
results=[]
for id in ['fire_talisman','thunder_talisman','wind_talisman','stealth_talisman','vajra_talisman','soul_talisman','return_talisman']:
 s=command('native-'+id+'-recipe','jei',item='dynasty:'+id,role='OUTPUT')
 slots=[slot for row in s['jeiScreen']['layouts'] for slot in row['slots'] if 'dynasty:talisman_paper' in slot['items'] and slot['role']=='INPUT'];slot=slots[0]
 click=command('native-'+id+'-click-paper','nativeMouse',x=slot['x'],y=slot['y'],button=0)
 back=command('native-'+id+'-back','nativeKey',key=259)
 key=command('native-'+id+'-R-paper','nativeKey',x=slot['x'],y=slot['y'],key=82)
 results.append({'item':id,'mouse':click,'back':back,'R':key});print(id,'mouse recipes',[x.get('recipe') for x in click.get('jeiScreen',{}).get('layouts',[])],'R recipes',[x.get('recipe') for x in key.get('jeiScreen',{}).get('layouts',[])],flush=True)
 command('native-'+id+'-escape','nativeKey',key=256)
(O/'native-navigation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
s=command('paper-recipe-for-U','jei',item='dynasty:talisman_paper',role='OUTPUT');slot=next(slot for row in s['jeiScreen']['layouts'] for slot in row['slots'] if 'dynasty:talisman_paper' in slot['items'] and slot['role']=='OUTPUT')
command('paper-U-native','nativeKey',x=slot['x'],y=slot['y'],key=85)
command('close-before-bow','close')
for name,opts in [('gui-native-close',{'variant':'gui'}),('armor-other-huds',{'armorHud':True})]:
 command('start-bow-'+name,'bow',name='bow-'+name,item='dynasty:lie_gong',**opts);wait_file('bow-'+name+'-result.json');print('Bow',name,'completed',flush=True)
command('final-active-world','close')
(O/'DRIVER-COMPLETE.json').write_text(json.dumps({'native_navigation_and_gui_close_complete':True},indent=2));print('Final input sequence completed',flush=True)
