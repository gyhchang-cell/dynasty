#!/usr/bin/env python3
"""Collect verified native render/transaction evidence; optionally remove only fulfilled prompt lines."""
import argparse,difflib,gzip,hashlib,json,shutil,zipfile
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from remains_resources import ROOT,ASSETS,DOC
from validate_remains import main as validate

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='memorial-final');p.add_argument('--frozen',default='remains-memorial-final');p.add_argument('--clean-prompts',action='store_true');a=p.parse_args()
    validate()
    run=ROOT/'build/cod3-remains-20261011/results'/a.run
    frozen=ROOT/'build/blueprint-client/frozen'/a.frozen
    assert (run/'PASS.txt').exists() and not (run/'FAIL.txt').exists()
    jar=ROOT/'build/cod3-remains-20261011/compiled/libs/dynasty-1.4.0.jar';assert jar.exists()
    report=json.loads((DOC/'resource-validation.json').read_text());manifest=json.loads((frozen/'runtime-manifest.json').read_text())
    resources={}
    for name in report['files']:
        path=ROOT/name
        if path.is_relative_to(ASSETS):resources[path]=path.relative_to(ROOT/'src/main/resources').as_posix()
    for name in ['blockstates/rebel_general_statue.json','models/item/rebel_general_statue.json']:
        path=ASSETS/name;resources[path]=path.relative_to(ROOT/'src/main/resources').as_posix()
    loot=ROOT/'src/main/resources/data/dynasty/loot_tables/blocks/rebel_general_statue.json';resources[loot]=loot.relative_to(ROOT/'src/main/resources').as_posix()
    resource_sha={}
    with zipfile.ZipFile(jar) as z:
        assert not any('RemainsQa' in name or 'Cod3NpcArtQa' in name for name in z.namelist())
        for path,name in resources.items():
            data=path.read_bytes();assert z.read(name)==data,(name,'jar mismatch')
            matches=[tree for tree in manifest['trees'] if any(e['path']==name for e in tree['entries'])]
            assert len(matches)==1 and (Path(matches[0]['runtime'])/name).read_bytes()==data,(name,'tested runtime mismatch')
            resource_sha[name]=sha(data)
        for name in ['com/dynasty/cod3/RebelStatueBlock.class','com/dynasty/cod3/RebelStatueBlock$Statue.class','com/dynasty/cod3/LootableRemains.class','com/dynasty/cod3/LootableRemains$Remains.class','com/dynasty/cod3/BossDeathState.class','com/dynasty/DynastyContent.class','com/dynasty/DynastyTabs.class']:
            assert name in z.namelist()
            matches=[tree for tree in manifest['trees'] if any(e['path']==name for e in tree['entries'])]
            assert len(matches)==1 and (ROOT/'build/cod3-remains-20261011/compiled/classes/java/main'/name).read_bytes()==(Path(matches[0]['runtime'])/name).read_bytes(),name
        for lang in ('zh_cn','en_us'):
            key=f'assets/dynasty/lang/{lang}.json';packed=json.loads(z.read(key));source=json.loads((ROOT/'src/main/resources'/key).read_text())
            for entry in ('block.dynasty.rebel_general_statue','cod3.dynasty.statue.inventory_full','cod3.dynasty.statue.sword_pulled'):assert packed[entry]==source[entry]
    evidence=DOC/'evidence';evidence.mkdir(exist_ok=True)
    measurements=[]
    for name in ('statue','coffer'):
        for suffix in ('180','135','90','0','silhouette'):
            image=Image.open(run/f'{name}-{suffix}.png').convert('RGB');bg=image.getpixel((0,0));mask=ImageChops.difference(image,Image.new('RGB',image.size,bg)).convert('L');bounds=mask.getbbox();assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<600 and bounds[3]<600,(name,suffix,bounds)
            foreground=[v for v in image.get_flattened_data() if v!=bg];assert len(foreground)>1000
            if suffix=='silhouette':assert set(foreground)=={(0,0,0)}
            measurements.append(dict(model=name,view=suffix,bounds=bounds,foreground_pixels=len(foreground)))
    before=Image.open(run/'statue-180.png').convert('RGB');after=Image.open(run/'statue-after-reload.png').convert('RGB');reload_difference=ImageChops.difference(before,after)
    # Minecraft updates its native lightmap while the temporary world ticks. Require identical
    # coverage and record the small RGB lighting drift, rather than claim identical screenshots.
    reload_max=max(max(v) for v in reload_difference.get_flattened_data());assert reload_max<=3,'Reload caused a material/render change beyond native lighting drift'
    assert [v!=before.getpixel((0,0)) for v in before.get_flattened_data()]==[v!=after.getpixel((0,0)) for v in after.get_flattened_data()],'Reload changed model coverage'
    empty=Image.open(run/'statue-empty.png').convert('RGB');difference=ImageChops.difference(before,empty);changed=sum(v!=(0,0,0) for v in difference.get_flattened_data());assert changed>1000,'Weapon never disappeared'
    for path in run.glob('*.png'):shutil.copy2(path,evidence/path.name)
    shutil.copy2(run/'PASS.txt',evidence/'PASS.txt')
    with gzip.open(evidence/'client.log.gz','wb') as f:f.write((run/'client.log').read_bytes())
    board=Image.new('RGB',(1500,668),'#e6e1d7');draw=ImageDraw.Draw(board)
    for row,name in enumerate(('statue','coffer')):
        for col,suffix in enumerate(('180','135','90','0','silhouette')):
            board.paste(Image.open(run/f'{name}-{suffix}.png').convert('RGB').resize((300,300),Image.Resampling.NEAREST),(col*300,row*334+30))
            draw.text((col*300+8,row*334+9),name+' / '+('Front','45 degrees','Side','Back','Black silhouette')[col],fill='#26231d')
    board.save(DOC/'overview.png')
    atlas_board=Image.new('RGB',(512,300),'#ffffff');draw=ImageDraw.Draw(atlas_board)
    for n,name in enumerate(('rebel_general_statue','lootable_remains')):
        atlas_board.paste(Image.open(ASSETS/f'textures/block/{name}.png').convert('RGB').resize((256,256),Image.Resampling.NEAREST),(n*256,24));draw.text((n*256+4,4),name,fill='#000000')
    atlas_board.save(DOC/'textures-review.png')
    delivery=ROOT/'build/cod3-remains-20261011/dynasty-1.4.0-cod3-memorial.jar';shutil.copy2(jar,delivery)
    checks=(run/'PASS.txt').read_text().splitlines();assert all(line.startswith('PASS ') for line in checks)
    distinct=list(dict.fromkeys(checks));(evidence/'distinct-checks.txt').write_text('\n'.join(distinct)+'\n')
    result=dict(date='2026-10-11',run=a.run,frozen=a.frozen,checks=len(distinct),check_records=len(checks),client_launches=2,scope='Final integrated Forge client, real server transactions with two FakePlayers; not a new two-client network test',render_frames=len([p for p in run.glob('*.png') if p.name!='reload-difference.png']),five_views=measurements,weapon_changed_pixels=changed,resource_reload_coverage_identical=True,resource_reload_max_rgb_drift=reload_max,resources=resource_sha,jar=str(delivery.relative_to(ROOT)),jar_sha256=sha(delivery.read_bytes()),qa_classes_packaged=False)
    (DOC/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if a.clean_prompts:
        original=Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt');mirror=ROOT/'docs/cod3/remaining-tasks.txt'
        data=original.read_bytes();assert mirror.read_bytes()==data,'Prompt mirror diverged; do not overwrite'
        lines=data.decode().splitlines(keepends=True)
        targets=[
            '- 遗留：**死亡后永久雕像不保留 Boss 实体**；Sequence 结束在 anchor 放 StatueBlock/Structure piece，Boss 再 remove；其插地武器玩家可拔出（LootableRemains）。\n',
            '- `Statue`：[NOT_VERIFIED] 当前无专用雕像块。**两种实现选一**：\n',
            '  - (a) 复用现有结构 piece（`structure/DynastyStructures` 新增一个无 AI 的雕像 piece，[PROPOSED]）；\n',
            '  - (b) 新增 `StatueBlock`（[PROPOSED]，`BaseEntityBlock` + 数据保存朝向/类型）。\n',
            '  推荐 (a)：死亡遗留物优先走「结构 piece / 预设 Block state」，不保留死 Boss 实体。\n',
        ]
        if not any(target in lines for target in targets):print('Already cleaned exact fulfilled requirements');return
        assert all(lines.count(target)==1 for target in targets),'Partial/unexpected prompt cleanup'
        removed=[dict(line=i+1,text=line) for i,line in enumerate(lines) if line in targets];kept=[line for line in lines if line not in targets]
        assert all(tag in ('equal','delete') for tag,*_ in difflib.SequenceMatcher(None,lines,kept,autojunk=False).get_opcodes())
        backup=ROOT/'build/cod3-remains-20261011/prompt-before-cleanup.txt';assert not backup.exists();backup.write_bytes(data)
        updated=''.join(kept).encode();logfile=ROOT/'docs/cod3/deletions-20261010.json';log=json.loads(logfile.read_text());assert log['current_sha256']==sha(data)
        log['batches'].append(dict(date='2026-10-11',tasks=['C3-DEATH-REBEL-MEMORIAL','C3-DEATH-STATUE-BLOCK'],evidence='docs/art/cod3-remains-v1/verification.json; actual block placement/withdrawal/reload/death journal and five-view checks',before_sha256=sha(data),after_sha256=sha(updated),removed=removed))
        log['current_sha256']=sha(updated)
        # Complete all verification before applying the requested local prompt deletion.
        original.write_bytes(updated);mirror.write_bytes(updated);logfile.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
        print(f'Deleted {len(removed)} fulfilled lines; {len(lines)} -> {len(kept)}; mirror matches')
    print(f'PASS {len(distinct)} distinct runtime checks / {result["render_frames"]} saved frames; jar/resource/frozen-runtime parity')
if __name__=='__main__':main()
