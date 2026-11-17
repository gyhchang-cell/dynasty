"""Allowlisted constant declaration reader; no JVM or foreign class execution."""
from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def number(op,arg,comment):
 if op.startswith(('iconst_','fconst_')):return int(op.rsplit('_',1)[1])
 if op in ['bipush','sipush']:return int(arg.strip())
 if op in ['ldc','ldc_w'] and re.match(r'(float|int) ',comment):return float(comment.split()[1].rstrip('f'))
 return None

def decode(text):
 block=re.search(r'  public static net.minecraft.client.model.geom.builders.LayerDefinition createBodyLayer\(\);(.*?)(?=\n  (?:public|private|protected)|\n\})',text,re.S).group(1)
 stack=[];local={};nodes=[];grid=None;rawcalls=0
 def pop(n):
  if not n:return []
  out=stack[-n:];del stack[-n:];return out
 for line in block.splitlines():
  m=re.match(r'\s*(\d+): (\w+)\s*(.*?)(?:\s+// (.*))?$',line)
  if not m:continue
  offset,op,arg,comment=m.groups();comment=comment or '';v=number(op,arg,comment)
  if v is not None:stack.append(v)
  elif op in ['ldc','ldc_w'] and comment.startswith('String '):stack.append(comment[7:])
  elif op=='new':
   typ=comment.rsplit('/',1)[1];assert typ in ['MeshDefinition','CubeDeformation'],typ
   stack.append({'type':typ})
  elif op=='dup':stack.append(stack[-1])
  elif op.startswith('astore'):
   idx=int(op.split('_')[1]) if '_' in op else int(arg.strip());local[idx]=stack.pop()
  elif op.startswith('aload'):
   idx=int(op.split('_')[1]) if '_' in op else int(arg.strip());stack.append(local[idx])
  elif op in ['invokestatic','invokevirtual','invokespecial']:
   method=comment.removeprefix('Method ')
   if 'MeshDefinition."<init>":()V' in method:
    obj=stack.pop();obj['root']={'name':'root','parent':None,'pose':[0]*6,'cubes':[]}
   elif 'CubeDeformation."<init>":(F)V' in method:
    val=stack.pop();obj=stack.pop();obj['value']=val
   elif 'MeshDefinition.m_171576_:' in method:stack.append(stack.pop()['root'])
   elif 'CubeListBuilder.m_171558_:' in method:stack.append({'type':'builder','uv':None,'mirror':False,'cubes':[]})
   elif 'CubeListBuilder.m_171514_:' in method:
    uv=pop(2);stack[-1]['uv']=uv
   elif 'CubeListBuilder.m_171480_:' in method:stack[-1]['mirror']=True
   elif 'CubeListBuilder.m_171555_:' in method:val=stack.pop();stack[-1]['mirror']=bool(val)
   elif 'CubeListBuilder.m_171488_:' in method:
    a=pop(7);builder=stack[-1];assert builder['uv'] is not None
    builder['cubes'].append({'origin':a[:3],'size':a[3:6],'deformation':a[6]['value'],'uv':list(builder['uv']),'mirror':builder['mirror'],'declaration_offset':int(offset)});rawcalls+=1
   elif 'PartPose.m_171419_:' in method:stack.append(pop(3)+[0]*3)
   elif 'PartPose.m_171423_:' in method:stack.append(pop(6))
   elif 'PartDefinition.m_171599_:' in method:
    parent,name,builder,pose=pop(4);node={'name':name,'parent':parent['name'],'pose':pose,'cubes':builder['cubes']};assert not any(x['name']==name for x in nodes);nodes.append(node);stack.append(node)
   elif 'LayerDefinition.m_171565_:' in method:
    mesh,w,h=pop(3);grid=[w,h];stack.append({'grid':grid,'nodes':nodes})
   else:raise AssertionError(method)
  elif op=='areturn':
   result=stack.pop();assert not stack and result['grid']==grid
  else:raise AssertionError((offset,op,line))
 assert grid==[128,128] and rawcalls==sum(len(n['cubes']) for n in nodes)
 assert rawcalls==block.count('CubeListBuilder.m_171488_:')
 return {'declared_grid':grid,'nodes':nodes,'raw_addbox_calls':rawcalls,'declaration_instruction_count':len(re.findall(r'^\s*\d+:',block,re.M)),'scope':'Allowlisted literal constructor declarations only; not model code execution or runtime behavior.'}

def main():
 p=json.loads((D/'provenance.json').read_text());models={};rows=[]
 registry=(D/'disassembly/SwWukongModItems.verbose.txt').read_text();boot=registry.split('BootstrapMethods:',1)[1];code=registry.split('  static {};',1)[1].split('BootstrapMethods:',1)[0]
 bs={int(k):v for k,v in re.findall(r'^  (\d+): (.*?)(?=^  \d+: |\Z)',boot,re.M|re.S)}
 for name in ['Modelwukong_reworked1','Modelwukong_reworked2']:
  source=next(x for x in p['classes'] if x['entry'].endswith('/'+name+'.class'));models[name]={'source':source,**decode((D/source['disassembly']).read_text())}
 for case in p['cases']:
  f=case['case_key'].split(':')[1];stem=''.join(s.capitalize() for s in f.split('_'))
  for part,slot,nodes in [('helmet','Helmet',['Head']),('chestplate','Chestplate',['Body','LeftArm','RightArm']),('leggings','Leggings',['LeftLeg','RightLeg']),('boots','Boots',['LeftLeg','RightLeg'])]:
   itemstem=stem+'Item$'+slot;source=next(a for a in p['classes'] if a['entry'].endswith('/'+itemstem+'.class'));client=next(a for a in p['classes'] if a['entry'].endswith('/'+itemstem+'$1.class'))
   item=(D/source['disassembly']).read_text();ext=(D/client['disassembly']).read_text();assert 'initializeClient(' in item and itemstem+'$1' in item and 'Consumer.accept:' in item and 'getHumanoidArmorModel(' in ext
   matches=re.findall(r'// String (sw_wukong:textures/[^\s]+\.png)',item);assert len(matches)==1
   texture=next(a for a in p['native_atlases'] if a['entry']=='assets/'+matches[0].replace(':','/'))
   model='Modelwukong_reworked2' if part=='boots' else 'Modelwukong_reworked1'
   fields=sorted(set(re.findall(r'Field net/mcreator/wukong/client/model/'+model+r'\.(\w+):',ext)) - {'LAYER_LOCATION'});assert fields==sorted(nodes)
   counts={n:sum(len(x['cubes']) for x in models[model]['nodes'] if n in ancestry(x['name'],models[model]['nodes'])) for n in nodes};assert all(counts.values())
   reg=re.search(r'(?P<excerpt>[^\n]*// String '+f+'_'+part+r'\n[^\n]*// InvokeDynamic #(?P<index>\d+):get:[^\n]*\n[^\n]*DeferredRegister.register:[^\n]*\n[^\n]*// Field (?P<field>\w+):[^\n]*)',code);assert reg
   factory=re.search(r'REF_invokeStatic net/mcreator/wukong/init/SwWukongModItems\.(lambda\$static\$\d+):',bs[int(reg['index'])]).group(1)
   fact=re.search(r'  private static [^\n]* '+re.escape(factory)+r'\(\);(.*?)(?=\n  (?:public|private|protected|static)|\Z)',registry,re.S).group(1)
   assert '// class net/mcreator/wukong/item/'+itemstem in fact
   rows.append({'registry_field':reg['field'],'registry_instructions':reg['excerpt'],'factory_method':factory,'factory_instructions':fact,'item_id':case['case_key']+'_'+part,'case_key':case['case_key'],'part':part,'item_class':source,'client_extension':client,'model':model,'model_fields':fields,'texture_resource':matches[0],'source_texture':texture,'root_descendant_cubes':counts,'declared_correspondence_checked':True,'live_player_render_proven':False})
 alpha=[]
 from PIL import Image
 for a in p['native_atlases']:
  im=Image.open(D/a['local']).convert('RGBA');alpha.append({'source':a,'nonzero_alpha_pixels':sum(im.getchannel('A').histogram()[1:]),'direct_custom_item_texture_users':sum(r['source_texture']==a for r in rows)})
 save('binding-and-geometry-study.json',{'models':models,'slot_chains':rows,'atlas_alpha_context':alpha,'new_design_credit':0,'game_starts':0,'runtime_acceptance':False,'limits':['解析静态常量声明，不执行模组类','16件用同一主模型和同一靴模型，四种材质不计四套独立设计','图集透明度与原始addBox不是实际最终可见性、采样或接缝证明']})
 print(json.dumps({'constant_model_definitions':len(models),'declaration_addbox_calls':sum(x['raw_addbox_calls'] for x in models.values()),'slot_chains':len(rows),'alpha':[(Path(x['source']['entry']).name,x['nonzero_alpha_pixels'],x['direct_custom_item_texture_users']) for x in alpha]}))
def ancestry(name,nodes):
 by={x['name']:x for x in nodes};out=[]
 while name and name!='root':
  assert name not in out
  out.append(name);name=by[name]['parent']
 return out
if __name__=='__main__':main()
