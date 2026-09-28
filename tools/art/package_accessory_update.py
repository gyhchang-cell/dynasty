"""Verified incremental package. Stages project JAR, never touches a launcher or save."""
import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from gen_trinkets7 import ITEMS

ROOT=Path(__file__).resolve().parents[2]
def main():
    jar=ROOT/'build/libs/dynasty-1.4.0.jar'
    with zipfile.ZipFile(jar) as z:
        names=set(z.namelist())
        assert 'com/dynasty/DynastySchoolAccessories.class' in names
        assert not any('RuntimeQa' in n or 'BookRuntimeQa' in n for n in names)
        for k in ITEMS:
            assert f'data/dynasty/recipes/{k}.json' in names
            assert f'assets/dynasty/textures/item/{k}.png' in names
        for p in (ROOT/'src/main/resources').rglob('*'):
            if not p.is_file():continue
            n=p.relative_to(ROOT/'src/main/resources').as_posix()
            expected=(ROOT/'build/resources/main'/n).read_bytes() if n in ('META-INF/mods.toml','pack.mcmeta') else p.read_bytes()
            assert z.read(n)==expected,f'Rebuild changed resource: {n}'
    quest=ROOT/'modpack/config/ftbquests/quests'
    payload={f'mods/{jar.name}':jar.read_bytes()}
    payload.update({'config/ftbquests/quests/'+p.relative_to(quest).as_posix():p.read_bytes() for p in quest.rglob('*.snbt')})
    readme='''王朝 · 百炼佩章 · 2026-09-24
Minecraft 1.20.1 / Forge 现有整合包增量更新，不是完整整合包。
本轮新增8件被动饰品，累计24件、8条三阶进化链；24件均可在铁砧持续淬炼。
本轮8张新贴图，保留上一轮16张新饰品与12张旧饰品重制贴图。
35章664节点，其中主线69节点；旧488条任务身份与奖励保留。
本轮新增28个流派节点；+1/+5/+15/+30是任务里程碑，不是强化上限。
进阶饰品使用锻造台：兵器图纸+上一阶饰品+指定材料，保留淬炼、附魔和名称。

完全退出游戏后，备份实例的 mods/dynasty-1.4.0.jar 和 config/ftbquests。
替换 Dynasty JAR（不要同时保留两个版本），合并本包 config/ftbquests/quests。
不要删除 saves、任务进度或其他模组。服务端和客户端须使用相同新版JAR。
已有实例应保留 Curios、Patchouli、FTB Quests 等依赖，本包不重复附带。
饰品放入对应 Curios 槽位后生效；仅持有在背包里不会增伤。

本包是当前共同工作区的构建，包含同期其他改动，不代表DeepSeek工作已全面验收。
本工具未向启动器安装，未改存档。验证记录见项目
docs/art/accessory-refining-v3/DELIVERY.md。
'''
    payload['安装说明.txt']=readme.encode()
    manifest={'release':'accessory-refining-v3','chapters':35,'quests':664,'main_quests':69,
              'new_accessories_this_round':8,'refinable_accessories':24,'new_quests_this_round':28,
              'sha256':{n:hashlib.sha256(b).hexdigest() for n,b in payload.items()}}
    payload['update-manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    dest=ROOT/'dist/dynasty-refining-v3-2026-09-24-update.zip'
    dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in payload.items():z.writestr(n,b)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert all(z.read(n)==b for n,b in payload.items())
    staged=ROOT/'modpack/mods'/jar.name
    if staged.exists() and staged.read_bytes()!=jar.read_bytes():
        backup=ROOT/'build/backups'/('accessories-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        backup.mkdir(parents=True)
        shutil.copy2(staged,backup/staged.name)
        print('Previous project JAR:',backup/staged.name)
    shutil.copy2(jar,staged)
    print('Staged project JAR:',staged)
    print('Update:',dest)
    print('SHA256:',hashlib.sha256(jar.read_bytes()).hexdigest())
    print('No launcher instance or save changed.')

if __name__=='__main__':main()
