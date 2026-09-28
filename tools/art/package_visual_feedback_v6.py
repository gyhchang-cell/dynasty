"""Reproduce inspected imagegen assets; mechanical cropping only, never modifies saves."""
import hashlib, json, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/art/visual-feedback-v6'
GEN = Path('/Users/a15356015027/.codex/generated_images/01a0b3cd-a8f4-7620-8174-d631c852f383')
SETS = {'general':'af83e8e3-8506-44d6-9259-2ae31bb6cea4', 'jade':'99b01bf0-02b7-4836-a97f-49b09709ecd1', 'sky':'98e73fa0-146c-4aac-88eb-3f92eee38fb8'}
BLOCKS = {'palace_bricks':'25aceb55-e638-4492-abed-546ed692ea76','jade_ore':'88a3def3-719e-46ed-9bf7-7b1777019609','dragon_crystal_ore':'d133eaa0-dfd8-436f-af33-b1d343800cd7'}
def main():
    for folder in ('sources','before','item','block'): (DOC/folder).mkdir(parents=True,exist_ok=True)
    records=[]
    def publish(name,kind,args):
        target=ROOT/f'src/main/resources/assets/dynasty/textures/{kind}/{name}.png'
        backup=DOC/'before'/f'{name}.png'
        if not backup.exists(): shutil.copy2(target,backup)
        output=DOC/kind/f'{name}.png'
        subprocess.run(['magick',*args,'PNG32:'+str(output)],check=True)
        shutil.copy2(output,target)
        records.append({'id':name,'kind':kind,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
    for name,source_id in {**SETS,**BLOCKS}.items():
        source=DOC/'sources'/f'{name}.png'
        if not source.exists(): shutil.copy2(GEN/f'exec-{source_id}.png',source)
        if name in SETS:
            w,h=map(int,subprocess.check_output(['magick','identify','-format','%w %h',str(source)]).split())
            for slot,(x,y) in zip(('helmet','chestplate','leggings','boots'),((0,0),(w//2,0),(0,h//2),(w//2,h//2))):
                publish(name+'_'+slot,'item',[str(source),'-crop',f'{w//2}x{h//2}+{x}+{y}','+repage','-trim','+repage','-filter','point','-resize','116x116','-background','none','-gravity','center','-extent','128x128'])
        else: publish(name,'block',[str(source),'-filter','point','-resize','32x32!','-alpha','off'])
    (DOC/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    cards=''.join(f'<figure><img src="{r["kind"]}/{r["id"]}.png"><figcaption>{r["id"]}</figcaption></figure>' for r in records)
    (DOC/'gallery.html').write_text('<!doctype html><meta charset="utf-8"><title>王朝 · 平面盔甲与像素方块</title><style>body{background:#19242b;color:#eee;font:16px system-ui;max-width:1100px;margin:40px auto}section{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}figure{margin:0;padding:16px;background:#33434e}img{width:100%;image-rendering:pixelated}figcaption{font-size:13px}</style><h1>平面盔甲与像素方块</h1><p>三套12张正面盔甲图标；宫砖、玉矿、龙晶矿三种32像素方块。资源预览，不是游戏实拍。</p><section>'+cards+'</section>')
    print(f'Published {len(records)} inspected assets')
if __name__=='__main__': main()
