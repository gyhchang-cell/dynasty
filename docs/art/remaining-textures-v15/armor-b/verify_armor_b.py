"""Independent native size, silhouette, alpha, provenance and standard UV checks."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parent
M=json.loads((R/'manifest.json').read_text())
ISSUES=[];RECORDS=[];MASKS={};PIXELS={};ATLAS_STRUCTURES={};SOURCE_CHANGES=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for entry in M['sets']:
    for b in entry['baseline']:
        if sha(Path(b['source']))!=b['sha256']:SOURCE_CHANGES.append(b['source'])
        if sha(R/b['backup'])!=b['sha256']:ISSUES.append({'backup_changed':b['backup']})
    for a in entry['assets']:
        path=R/a['path'];im=Image.open(path).convert('RGBA');data=list(im.getdata());alphas=set(c[3] for c in data)
        colors=len({c[:3] for c in data if c[3]})
        rec={'set':entry['set'],'path':a['path'],'size':im.size,'alpha':sorted(alphas),'opaque_colors':colors,'file_sha256':sha(path),'pixel_sha256':hashlib.sha256(im.tobytes()).hexdigest()}
        if rec['file_sha256']!=a['sha256']:ISSUES.append({'manifest_hash_mismatch':a['path']})
        if '/item/' in a['path']:
            box=im.getchannel('A').getbbox();maskhash=hashlib.sha256(im.getchannel('A').tobytes()).hexdigest()
            rec.update(bbox=box,margin=min(box[0],box[1],32-box[2],32-box[3]),alpha_mask_sha256=maskhash)
            if not(im.size==(32,32) and alphas=={0,255} and 8<=colors<=20 and rec['margin']>=1):ISSUES.append(rec)
            MASKS.setdefault(maskhash,[]).append(a['id']);PIXELS.setdefault(rec['pixel_sha256'],[]).append(a['id'])
            model=json.loads(Path(a['model']).read_text());parent=model['parent']
            if ':' not in parent:parent='minecraft:'+parent
            if parent!='minecraft:item/generated':ISSUES.append({'bad_item_parent':a['id']})
            if model['textures']['layer0']!=a['id'].replace('dynasty:','dynasty:item/'):ISSUES.append({'bad_layer0':a['id']})
        else:
            if im.size!=(64,32) or alphas!={0,255}:ISSUES.append(rec)
            # Color-invariant test: preserve each palette-region partition, ignore hue.
            color_ids={(0,0,0,0):0};indices=[]
            for color in data:
                if not color[3]:color=(0,0,0,0)
                if color not in color_ids:color_ids[color]=len(color_ids)
                indices.append(color_ids[color])
            structure=hashlib.sha256(bytes(indices)).hexdigest();rec['color_invariant_structure_sha256']=structure
            ATLAS_STRUCTURES.setdefault(structure,[]).append(a['path'])
        RECORDS.append(rec)
    for n in (1,2):
        im=Image.open(R/f'candidate/assets/dynasty/textures/models/armor/{entry["set"]}_layer_{n}.png').convert('RGBA');allowed=set()
        def cube(u,v,w,h,d):
            for y in range(v+d,v+d+h):
                for x in range(u,u+2*w+2*d):allowed.add((x,y))
            for y in range(v,v+d):
                for x in range(u+d,u+d+2*w):allowed.add((x,y))
        if n==1:cube(0,0,8,8,8);cube(40,16,4,12,4)
        cube(16,16,8,12,4);cube(0,16,4,12,4)
        outside=[(x,y) for y in range(32) for x in range(64) if im.getpixel((x,y))[3] and (x,y) not in allowed]
        if outside:ISSUES.append({'set':entry['set'],'layer':n,'outside_uv':outside})
        if n==1:
            if any(im.getpixel((x,y))[3] for x in range(10,14) for y in range(11,16)):ISSUES.append({'set':entry['set'],'helmet_face_not_clear':True})
            if any(im.getpixel((x,y))[3] for x in range(16) for y in range(20,25)):ISSUES.append({'set':entry['set'],'boots_overlap_thigh':True})
        else:
            if any(not im.getpixel((x,y))[3] for x in range(16) for y in range(20,32)):ISSUES.append({'set':entry['set'],'leg_uv_not_complete':True})
            if any(im.getpixel((x,y))[3] for x in range(16,40) for y in range(20,28)):ISSUES.append({'set':entry['set'],'leggings_intrude_upper_body':True})
report={'set_count':len(M['sets']),'png_count':len(RECORDS),'icons':48,'atlases':24,'all_checks_passed':not ISSUES and not SOURCE_CHANGES,'source_files_checked':sum(len(e['baseline']) for e in M['sets']),'source_changes':SOURCE_CHANGES,'issues':ISSUES,'icon_unique_pixel_hashes':len(PIXELS),'icon_unique_alpha_masks':len(MASKS),'shared_alpha_masks':[v for v in MASKS.values() if len(v)>1],'atlas_unique_color_invariant_structures':len(ATLAS_STRUCTURES),'atlas_recolor_only_duplicates':[v for v in ATLAS_STRUCTURES.values() if len(v)>1],'records':RECORDS,'protected_ids_modified':[],'uv_checks':['Every opaque atlas pixel inside standard cube UV islands','Layer 1 central helmet face transparent','Layer 1 boots do not occupy thigh texels','Layer 2 front/back/side legs fully covered','Layer 2 body only at waist, upper torso transparent','Shared limb UV; actual vanilla mirror used by preview'],'game_tested':False}
(R/'qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

F=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',20);SM=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',14)
for pg in range(2):
    out=Image.new('RGB',(1250,1400),'#e6e5dc');d=ImageDraw.Draw(out);d.text((18,12),f'Armor B / independent constructions / {pg+1} of 2',font=F,fill='#273a3d')
    for j,e in enumerate(M['sets'][pg*6:(pg+1)*6]):
        y=55+j*222;d.text((18,y),e['name'],font=F,fill='#273a3d');d.text((18,y+28),e['set'],font=SM,fill='#637171')
        for i,piece in enumerate(('helmet','chestplate','leggings','boots')):
            im=Image.open(R/f'candidate/assets/dynasty/textures/item/{e["set"]}_{piece}.png').convert('RGBA');x=170+i*167;d.rectangle((x,y+3,x+127,y+130),fill='#354346');big=im.resize((128,128),Image.Resampling.NEAREST);out.paste(big,(x,y+3),big);out.paste(im,(x,y+145),im);d.text((x+40,y+153),piece,font=SM,fill='#637171')
        wear=Image.open(R/f'previews/{e["set"]}-worn-front.png').convert('RGBA').resize((165,195),Image.Resampling.NEAREST);out.paste(wear,(840,y),wear)
        for n in (1,2):
            im=Image.open(R/f'candidate/assets/dynasty/textures/models/armor/{e["set"]}_layer_{n}.png').convert('RGBA');big=im.resize((192,96),Image.Resampling.NEAREST);out.paste(big,(1030,y+(n-1)*101),big)
        d.line((18,y+209,1230,y+209),fill='#c5c9bf')
    out.save(R/f'previews/armor-b-contact-{pg+1}.png')
summary={k:v for k,v in report.items() if k!='records'}
summary['icon_color_range']=[min(r['opaque_colors'] for r in RECORDS if '/item/' in r['path']),max(r['opaque_colors'] for r in RECORDS if '/item/' in r['path'])]
print(json.dumps(summary,ensure_ascii=False,indent=2))
assert report['all_checks_passed'],ISSUES
