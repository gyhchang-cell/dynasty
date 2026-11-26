"""Replay known armor generation functions in memory, with no generator mains."""
import ast
from collections import Counter
import hashlib
from io import BytesIO
import json
from pathlib import Path
import subprocess
from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ART = ROOT / 'tools/art'
ASSET = ROOT / 'src/main/resources/assets/dynasty/textures/models/armor'
GENERATORS = ('artlib.py','palette.py','gen_armor_layers.py','gen_dynasty3.py','gen_armor2.py','gen_armor3.py')

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def select(tree, names):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            yield node
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            yield node

def run(nodes, env):
    exec(compile(ast.Module(body=list(nodes), type_ignores=[]), '<fixed local art script>', 'exec'), env)

def tint(source, rgb):
    result = source.copy()
    ratio = [v/255.0 for v in rgb]
    result.putdata([tuple(int(pixel[i]*ratio[i]) for i in range(3))+(pixel[3],) if pixel[3] else pixel
                    for pixel in source.get_flattened_data()])
    return result

def replay(versions):
    trees = {name:ast.parse(code) for name,code in versions.items()}
    globals_ = {}
    run(trees['artlib.py'].body, globals_)
    run(select(trees['palette.py'],{'JADE','GOLD'}),globals_)
    images = {}
    globals_['Cv'].save = lambda canvas,path: images.__setitem__(Path(path).stem,canvas.im.copy())
    globals_['OUT'] = globals_['ARMOR_OUT'] = '/unused-in-memory'
    globals_['os'] = __import__('os')
    run(select(trees['gen_armor_layers.py'],{'armor_layer'}),globals_)
    for family, palette in [('jade',globals_['JADE']),('general',globals_['ramp'](globals_['hx']('5A6472'),5))]:
        for layer in (1,2):
            globals_['armor_layer'](f'{family}_layer_{layer}',palette,globals_['GOLD'],
                                     globals_['hx']({'jade':'A9E8BC','general':'C0392B'}[family]),plate_lines=layer==1)
    run(select(trees['gen_dynasty3.py'],{'armor_layer','XUAN_MAIN','XUAN_TRIM'}),globals_)
    for layer in (1,2):
        globals_['armor_layer'](f'xuantian_layer_{layer}', globals_['XUAN_MAIN'], globals_['XUAN_TRIM'],
                                 globals_['hx']('7FE8D0'),plate_lines=layer==1)
    run(select(trees['gen_armor2.py'],{'SETS'}),globals_)
    bronze=globals_['SETS']['bronze']
    assert bronze[2]=='general'
    run(select(trees['gen_armor3.py'],{'MISSING_LAYERS'}),globals_)
    sky=globals_['MISSING_LAYERS']['sky']
    assert sky[0]=='xuantian'
    for layer in (1,2):
        images[f'bronze_layer_{layer}']=tint(images[f'general_layer_{layer}'],bronze[4])
        images[f'sky_layer_{layer}']=tint(images[f'xuantian_layer_{layer}'],sky[1])
    return images

def main():
    git_paths={name:str((ART/name).relative_to(ROOT)) for name in GENERATORS}
    scripts={}
    for revision in ('d00079658',):
        commit=git('rev-parse',revision).decode().strip()
        scripts[commit]={name:git('show',f'{commit}:{path}') for name,path in git_paths.items()}
    results={commit:replay(versions) for commit,versions in scripts.items()}
    records=[]
    for name in sorted(next(iter(results.values()))):
        path=ASSET/(name+'.png')
        relative=str(path.relative_to(ROOT))
        earliest,*_=git('log','--follow','--reverse','--format=%H','--',relative).decode().splitlines()
        first=git('show',f'{earliest}:{relative}')
        current=path.read_bytes()
        with Image.open(BytesIO(current)) as im:
            pixels=im.convert('RGBA')
            matches={commit:im2[name].tobytes()==pixels.tobytes() for commit,im2 in results.items()}
            opaque=pixels.getchannel('A').histogram()[255]
        records.append({'path':relative,'current_sha256':sha(current),'earliest_asset_commit':earliest,
                        'earliest_asset_sha256':sha(first),'earliest_asset_bytes_match':first==current,
                        'founding_generator_pixel_match':matches,'opaque_pixels':opaque})
    payload={'generator_hashes':{commit:{n:sha(b) for n,b in files.items()} for commit,files in scripts.items()},'rows':records}
    (OUT/'origin-comparison.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(Counter((row['earliest_asset_bytes_match'],any(row['founding_generator_pixel_match'].values())) for row in records))
    for row in records:
        print(Path(row['path']).stem, list(row['founding_generator_pixel_match'].values()),row['opaque_pixels'])
if __name__=='__main__':
    main()
