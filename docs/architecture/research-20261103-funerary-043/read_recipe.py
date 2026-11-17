"""Fixed-source byte inspection, no Java/class loading or asset extraction."""
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from read_class import OUT, parse, decode, sha
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read

def main():
    primary=json.loads((OUT/'class-evidence.json').read_text())
    jar=Path(primary['source_archive'])
    report={'source_archive':str(jar),'source_archive_sha256':sha(jar.read_bytes()),'classes':[], 'templates':[], 'primary_metadata':{}}
    with ZipFile(jar) as z:
        for suffix in ('GraveType','WebTemplateProcessor'):
            member='twilightforest/world/components/feature/templates/GraveyardFeature$'+suffix+'.class'
            raw=z.read(member);data,resolve=parse(raw);lines=[]
            for m in data['methods']:
                if 'code_hex' not in m:continue
                m['instructions']=decode(bytes.fromhex(m['code_hex']),resolve)
                lines.append('\n'+m['name']+m['descriptor'])
                lines.extend(f"{e['pc']:4d} {e['mnemonic']:18s} {str(e['operands']):18s} {e['reference'] or ''} {'->'+str(e['branch_targets']) if e['branch_targets'] else ''}" for e in m['instructions'])
            report['classes'].append(dict(member=member,sha256=sha(raw),data=data))
            (OUT/(suffix+'-reading.txt')).write_text('\n'.join(lines)+'\n')
        for name in ('graveyard','grave_full','grave_upper','grave_lower','grave_trap'):
            member='data/twilightforest/structures/feature/graveyard/'+name+'.nbt'
            raw=z.read(member);n=read(raw);p=n.get('palette') or n['palettes'][0]
            report['templates'].append(dict(member=member,sha256=sha(raw),size=n['size'],palette=p,
                blocks=len(n['blocks']),material_counts=dict(Counter(p[b['state']]['Name'] for b in n['blocks'])),
                block_entities=[b for b in n['blocks'] if b.get('nbt')],entities=n.get('entities',[]),
                palette_variants=len(n.get('palettes',[p]))))
        for member in ('META-INF/mods.toml','data/twilightforest/worldgen/configured_feature/graveyard.json','data/twilightforest/worldgen/placed_feature/graveyard.json'):
            if member in z.namelist():
                raw=z.read(member);report['primary_metadata'][member]={'sha256':sha(raw),'text':raw.decode()}
    report.update(java_run=False,classes_loaded=False,game_run=False,credit_added=0)
    (OUT/'recipe-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('templates','primary_metadata')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
