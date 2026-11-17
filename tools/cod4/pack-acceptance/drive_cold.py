from drive import *
wait_file('READY.json',600);print('English cold-start world ready',flush=True)
command('cold-en-talismans','talismans')
a=load(O/'cold-en-talismans-audit.json')
for id in a:
 s=command('cold-en-'+id+'-output','jei',item='dynasty:'+id,role='OUTPUT')
 layouts=s.get('jeiScreen',{}).get('layouts',[])
 slots=[slot for row in layouts for slot in row.get('slots',[]) if 'dynasty:talisman_paper' in slot.get('items',[]) and slot.get('role')=='INPUT']
 if slots:
  slot=slots[0];s=command('cold-en-'+id+'-paper-click','mouse',x=slot['x'],y=slot['y'],button=0)
  print(id,'native input click:',s.get('jeiScreen',{}).get('layouts',[{}])[0].get('recipe'),flush=True)
  command('cold-en-'+id+'-back','key',key=259)
 command('cold-en-'+id+'-input','jei',item='dynasty:'+id,role='INPUT')
 command('cold-en-'+id+'-info','info',item='dynasty:'+id)
 command('cold-en-'+id+'-escape','key',key=256)
 print(id,'cold English rendered',flush=True)
command('paper-seven-uses','jei',item='dynasty:talisman_paper',role='INPUT')
command('after-jei-world','close')
# Native production use; state and framebuffer must agree on frames actually drawn.
cases=[('rapid-'+id,'dynasty:'+id,{}) for id in ['lie_gong','chang_gong','shenbi_bow','luoyan_bow','tianlang_bow']]
cases += [('standard-dragon','dynasty:dragon_bow',{}),('standard-zhuxing','dynasty:zhuxing_bow',{}),('standard-fengling','dynasty:fengling_bow',{}),('offhand','dynasty:lie_gong',{'offhand':True}),('third-back','dynasty:lie_gong',{'camera':'THIRD_PERSON_BACK'}),('third-front','dynasty:dragon_bow',{'camera':'THIRD_PERSON_FRONT'}),('gui-covered','dynasty:lie_gong',{'variant':'gui'}),('hide-gui','dynasty:lie_gong',{'variant':'hideGui'}),('swap-cancel','dynasty:lie_gong',{'variant':'swap'}),('negative-vanilla','minecraft:bow',{}),('negative-no-ammo','dynasty:lie_gong',{'noAmmo':True})]
for name,item,opts in cases:
 command('start-bow-'+name,'bow',name='bow-'+name,item=item,**opts)
 wait_file('bow-'+name+'-result.json');print('Bow',name,'completed',flush=True)
command('final-world-hud','close')
(O/'DRIVER-COMPLETE.json').write_text(json.dumps({'actual_inputs_complete':True,'cases':cases,'note':'Raw captures require verification; this file alone does not declare acceptance.'},indent=2))
print('Completed input sequence; leaving own client ready for follow-up.',flush=True)
