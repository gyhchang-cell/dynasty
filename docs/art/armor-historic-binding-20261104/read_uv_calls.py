"""Read constant UV/addBox statements from static javap; not an executing model or renderer."""
from pathlib import Path
import json,re,math
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2];PRE=R/'docs/art/armor-historic-compact-reference-20261104'
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def number(line):
    m=re.search(r': (?:iconst_|fconst_)(m1|\d)\s*$',line)
    if m:return -1 if m[1]=='m1' else int(m[1])
    m=re.search(r': (?:bipush|sipush)\s+(-?\d+)\s*$',line)
    if m:return int(m[1])
    m=re.search(r'// (?:float|int) (-?[0-9.Ee+]+)f?\s*$',line)
    if m:return float(m[1])
    return None
def faces(u,v,w,h,d):
    return {'DOWN':[u+d,v,u+d+w,v+d],'UP':[u+d+w,v,u+d+2*w,v+d],
            'WEST':[u,v+d,u+d,v+d+h],'NORTH':[u+d,v+d,u+d+w,v+d+h],
            'EAST':[u+d+w,v+d,u+2*d+w,v+d+h],'SOUTH':[u+2*d+w,v+d,u+2*d+2*w,v+d+h]}
def main():
    ctx=json.loads((D/'class-provenance.json').read_text());src=json.loads((PRE/'provenance.json').read_text());models=[]
    for a in ctx['classes']:
        if a['scope']!='GEOMETRY_UV_CONTEXT':continue
        text=(D/a['disassembly']).read_text();family=a['entry'].split('/models/')[1].split('/')[0];slot=next(s for s in ['Head','Chest','Legs','Feet'] if Path(a['entry']).name.startswith(s))
        blocks=re.findall(r'  public static net.minecraft.client.model.geom.builders.LayerDefinition (create(?:Slim)?LayerDefinition)\(\);(.*?)(?=\n  (?:public|private|protected)|\n\})',text,re.S)
        for method,block in blocks:
            code=block.split('Code:',1)[1].split('LineNumberTable:',1)[0];lines=[l for l in code.splitlines() if re.match(r'\s+\d+: ',l)]
            assert not any(re.search(r': (?:if\w*|goto|fload\w*|fadd|fmul|fsub)\b',l) for l in lines)
            sizes=[];calls=[];uv=None;name=None;mirror=False;pending=False
            for i,l in enumerate(lines):
                if '// String ' in l:name=l.split('// String ',1)[1]
                if 'CubeListBuilder.m_171558_:' in l:mirror=False
                if 'CubeListBuilder.m_171480_:' in l:mirror=True
                if 'CubeListBuilder.m_171555_:' in l:
                    n=number(lines[i-1]);assert n in [0,1];mirror=bool(n)
                if 'CubeListBuilder.m_171514_:' in l:
                    uv=[number(x) for x in lines[i-2:i]];assert all(x is not None for x in uv);pending=True
                    nums=[];raw=[]
                    for nxt in lines[i+1:]:
                        if 'CubeListBuilder.m_171488_:' in nxt or 'CubeListBuilder.m_171481_:' in nxt:break
                        raw.append(nxt);n=number(nxt)
                        if n is not None:nums.append(n)
                    assert len(nums) in [6,7,9],(a['entry'],method,uv,nums)
                    origin=nums[:3];dims=nums[3:6];assert all(n>=0 for n in dims)
                if 'CubeListBuilder.m_171488_:' in l or 'CubeListBuilder.m_171481_:' in l:
                    assert pending and uv is not None,(a['entry'],method,l);pending=False
                    calls.append({'bytecode_offset':int(l.strip().split(':')[0]),'part_label_nearby':name,'uv_offset':uv,'origin':origin,'dimensions':dims,'mirror':mirror,'faces_in_uv_units':faces(*uv,*dims),'source_instruction_excerpt':lines[max(0,i-len(raw)-3):i+1]})
                if 'LayerDefinition.m_171565_:' in l:
                    sizes.append([number(x) for x in lines[i-2:i]])
            assert not pending and len(sizes)==1 and all(n for n in sizes[0]);assert len(calls)==sum('CubeListBuilder.m_171488_:' in l or 'CubeListBuilder.m_171481_:' in l for l in lines)
            # A slim method may inherit then replace children. Report its raw source calls, never claim the final cube count.
            inherited=any('createLayerDefinition:' in l and 'invokestatic' in l for l in lines)
            has_slim=len(blocks)>1;normal=next(x for x in src['worn_textures'] if x['case_key']=='armoroftheages:'+family and x['variant']=='normal');slim=next(x for x in src['worn_textures'] if x['case_key']=='armoroftheages:'+family and x['variant']=='slim')
            tex=slim if 'Slim' in method else normal
            im=Image.open(PRE/tex['local']).convert('RGBA');assert list(im.size)==sizes[0]
            issues=[]
            for call in calls:
                probes={}
                for face,rect in call['faces_in_uv_units'].items():
                    x0,y0,x1,y1=rect;bounds=(x0>=-1e-5 and y0>=-1e-5 and x1<=im.width+1e-5 and y1<=im.height+1e-5)
                    if not bounds:issues.append({'offset':call['bytecode_offset'],'face':face,'rect':rect})
                    # Integer envelope only; fractional/degenerate UV has no exact area/visibility assertion.
                    box=[max(0,math.floor(x0)),max(0,math.floor(y0)),min(im.width,math.ceil(x1)),min(im.height,math.ceil(y1))]
                    if box[2]>box[0] and box[3]>box[1]:histo=im.getchannel('A').crop(box).histogram();nonzero=sum(histo[1:])
                    else:nonzero=0
                    probes[face]={'uv_within_declared_grid':bounds,'pixel_envelope':box,'alpha_nonzero_in_envelope':nonzero,'degenerate_or_fractional':any(n!=int(n) for n in rect) or x0==x1 or y0==y1,'render_visibility_claim':False}
                call['source_alpha_envelope_probes']=probes
            models.append({'family':family,'slot':slot,'method':method,'source_class':a,'declared_grid':sizes[0],'texture_source':tex,'source_addbox_calls':calls,'source_addbox_call_count':len(calls),'inherits_normal_then_replaces_children':inherited,'has_separate_slim_method':has_slim,'out_of_grid_uv_rectangles':issues,'all_final_model_geometry_or_runtime_visibility_proven':False})
    assert len(models)==15
    out={'models':models,'complete_families':3,'slot_classes':12,'methods_read':15,'raw_addbox_calls':sum(m['source_addbox_call_count'] for m in models),'out_of_grid_uv_rectangles':sum(len(m['out_of_grid_uv_rectangles']) for m in models),'new_design_credit':0,'limits':['原始addBox调用不是最终mesh体块数；细臂方法可能复用普通模型并替换子节点','源码UV范围/alpha包围框不等于最终可见、接缝正确或实机穿戴验收','小数/零厚面仅记录UV，不以整数包围框面积冒充真实UV覆盖','外部专用模型只作学习，不复制模型、图集或透明遮罩至Dynasty']}
    save('uv-call-study.json',out)
    print(json.dumps({k:v for k,v in out.items() if k!='models'},ensure_ascii=False))
if __name__=='__main__':main()
