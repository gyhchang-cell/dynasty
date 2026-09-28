"""Install inspected imagegen outputs using only mechanical size adaptation.
Input manifest retains complete prompts and original files. Never accesses saves.
"""
import json,shutil,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/vanilla-materials-v7'
TEX=ROOT/'src/main/resources/assets/dynasty/textures'
def main():
 records=json.loads((DOC/'generation.json').read_text());published=[]
 for r in records:
  id,kind=r['id'],r['kind'];source=DOC/'sources'/f'{id}.png';source.parent.mkdir(parents=True,exist_ok=True)
  if not source.exists():shutil.copy2(r['path'],source)
  target=TEX/kind/f'{id}.png';backup=DOC/'before'/kind/f'{id}.png';backup.parent.mkdir(parents=True,exist_ok=True)
  if target.exists() and not backup.exists():shutil.copy2(target,backup)
  out=DOC/kind/f'{id}.png';out.parent.mkdir(parents=True,exist_ok=True)
  if kind=='block':args=['-filter','point','-resize','32x32!','-alpha','off']
  else:
   size=128 if id.startswith(('bronze_','xuantian_')) else int(subprocess.check_output(['magick','identify','-format','%w',str(backup)]))
   args=['-trim','+repage','-filter','point','-resize',f'{size-4}x{size-4}','-background','none','-gravity','center','-extent',f'{size}x{size}']
  subprocess.run(['magick',str(source),*args,'PNG32:'+str(out)],check=True)
  shutil.copy2(out,target)
  published.append({**r,'source':str(source.relative_to(DOC)),'target':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
 (DOC/'manifest.json').write_text(json.dumps(published,ensure_ascii=False,indent=2)+'\n')
 cards=''.join(f'<figure><img src="{r["kind"]}/{r["id"]}.png"><figcaption>{r["id"]}</figcaption></figure>' for r in published)
 (DOC/'gallery.html').write_text('''<!doctype html><meta charset="utf-8"><title>王朝 · 原版风材质与生机工坊</title>
 <style>body{background:#20272d;color:#eee;max-width:1100px;margin:32px auto;padding:24px;font:17px/1.8 system-ui}section{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}figure{margin:0;padding:16px;background:#35414a}img{width:100%;image-rendering:pixelated}figcaption{font-size:13px}a{color:#9cddd2}</style>
 <h1>原版风材质 · 生机工坊</h1><p>资源预览，非游戏截图。基础方块降低纹理噪声；青铜甲朴素实用，玄天甲金白护片、青色宝石。玄天甲使用原版动态闪光及穿戴宝石呼吸光；没有改装备数值。</p>
 <p>四种可交互方块：化髓槽、凝灵器、玉髓修补炉、养元龛。右键加工，潜行右键查看说明，材料放背包。四种均有合成配方、掉落和中英词条。</p><section>'''+cards+'''</section><p>本轮不改建筑，不写入任何存档。你建筑里的箱子留待建完后设置奖励。参考：<a href="https://github.com/TeamTwilight/twilightforest">暮色森林</a>、<a href="https://www.curseforge.com/minecraft/mc-mods/biomancy">Biomancy</a>；只研究风格与交互，不复制它们的素材或代码。</p><p><a href="release-notes.md">使用、验证与安装说明</a> · <a href="generation.json">完整生成提示词（内置 imagegen）</a></p>''')
 print('Published',len(published),'assets; no instance or save writes')
if __name__=='__main__':main()
