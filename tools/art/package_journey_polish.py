"""Verified update payload and repeatable indexes. Does not touch the live instance."""
import hashlib,json,shutil,zipfile
from pathlib import Path
from datetime import datetime
from quest_story import build_book
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/journey-polish-v4'
NEW=['ftb-ultimine-forge-2001.1.8.jar','worldedit-mod-7.2.15.jar']
def sha(b,kind='sha256'):return hashlib.new(kind,b).hexdigest()
def main():
    jar=ROOT/'build/libs/dynasty-1.4.0.jar'
    with zipfile.ZipFile(jar) as z:
        names=z.namelist()
        assert 'com/dynasty/DynastyChainMining.class' not in names
        assert not any('RuntimeQa' in n or 'BookRuntimeQa' in n for n in names)
        for p in (ROOT/'src/main/resources').rglob('*'):
            if not p.is_file():continue
            n=p.relative_to(ROOT/'src/main/resources').as_posix()
            expected=(ROOT/'build/resources/main'/n).read_bytes() if n in ('META-INF/mods.toml','pack.mcmeta') else p.read_bytes()
            assert z.read(n)==expected,'Rebuild required: '+n
    staged=ROOT/'modpack/mods'/jar.name
    if staged.read_bytes()!=jar.read_bytes():
        backup=ROOT/'build/backups'/('journey-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
        backup.mkdir(parents=True);shutil.copy2(staged,backup/staged.name)
        shutil.copy2(jar,staged)
    records=json.loads((ROOT/'tools/art/qol_mods.json').read_text())
    index_path=ROOT/'modpack/modrinth.index.json'
    index=json.loads(index_path.read_text())
    for filename in NEW:
        data=(ROOT/'modpack/mods'/filename).read_bytes()
        r=next(r for r in records if r['filename']==filename)
        assert sha(data,'sha1')==r['sha1']
        with zipfile.ZipFile(ROOT/'modpack/mods'/filename) as z:assert z.testzip() is None
        record={'path':'mods/'+filename,'hashes':{'sha1':sha(data,'sha1'),'sha512':sha(data,'sha512')},
                'env':{side:r[side] for side in ('client','server')},'downloads':[r['url']],'fileSize':len(data)}
        index['files']=[f for f in index['files'] if f['path']!=record['path']]+[record]
    index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    payload={'mods/'+name:(ROOT/'modpack/mods'/name).read_bytes() for name in [jar.name,*NEW]}
    quests=ROOT/'modpack/config/ftbquests/quests'
    payload.update({'config/ftbquests/quests/'+p.relative_to(quests).as_posix():p.read_bytes() for p in quests.rglob('*.snbt')})
    pack=ROOT/'modpack/resourcepacks/dynasty-three-pixel-samples.zip'
    payload['resourcepacks/'+pack.name]=pack.read_bytes()
    payload['建筑搭建交接.md']=(DOC/'建筑搭建交接.md').read_bytes()
    readme='''王朝 2026-09-25 · 淬炼、弓与旅程分支
这是现有 Forge 1.20.1 整合包的增量更新，不是独立整合包。
退出 Minecraft 后合并本包 mods、config、resourcepacks。不要删 saves 或任务进度。
Dynasty JAR 替换同名旧版，不可同时保留两个版本；服务端也更新同版 Dynasty 和 Ultimine。
新增 FTB Ultimine 2001.1.8（依赖已有 Architectury 9.2.14、FTB Library 2001.2.13）和 WorldEdit 7.2.15。
内置连锁已移除；在按键设置搜索 Ultimine 查看/调整按键。
淬炼成本在各流派 +1/+5/+15/+30 任务中，物品只显示淬炼等级。
任务详情中点击任务物品图标，直接显示 JEI 配方。无配方掉落物不会凭空出现配方。
每个主线章节增两条短分支，共32个新节点；旧488条任务与奖励ID保持不变。
饰品仅提供3件像素风试样：选项→资源包，开启 dynasty-three-pixel-samples；关闭即可恢复。
创造搭建见《建筑搭建交接.md》。不会自动覆盖旧世界里的建筑。
当前共享工作区构建含同期其他修改，不代表其他开发者所有任务都已验收。
'''
    payload['安装说明.txt']=readme.encode()
    book=build_book()
    receipt={'chapters':len(book),'quests':sum(len(c['quests']) for c in book),
             'story_nodes':sum(len(c['quests']) for c in book if c['main']),'new_branches':32,
             'sha256':{n:sha(b) for n,b in payload.items()}}
    payload['update-manifest.json']=(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode()
    dest=ROOT/'dist/dynasty-journey-polish-2026-09-25-update.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in payload.items():z.writestr(name,data)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert all(z.read(n)==b for n,b in payload.items())
    print(dest);print(json.dumps({k:v for k,v in receipt.items() if k!='sha256'},ensure_ascii=False))
if __name__=='__main__':main()
