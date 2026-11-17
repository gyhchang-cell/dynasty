"""Verify the existing isolated build; never build, install or edit runtime files."""
from pathlib import Path
import hashlib
import html
import json
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/art/bestiary-v43/build-verification-20261030'
digest = lambda b: hashlib.sha256(b).hexdigest()


def main():
    snapshot = json.loads((OUT / 'snapshot-inputs.json').read_text())
    work = Path(snapshot['snapshot'])
    jar = work / 'build/libs/dynasty-1.4.0.jar'
    log = (OUT / 'gradle-build.log').read_text()
    assert 'BUILD SUCCESSFUL in 29s' in log
    paths = set()
    protected = {}
    for group in ('marshal', 'taoyan'):
        protected.update(json.loads((ROOT / f'docs/art/bestiary-v43/{group}/protected-before.json').read_text()))
    paths.update(protected)
    for name in ('gongsun_wuwang', 'gongsun_wuwang_foot', 'taoyan_zhishi', 'taoyan_zhishi_phase2'):
        for rel in (f'geo/blueprint/boss/{name}.geo.json',
                    f'animations/blueprint/boss/{name}.animation.json',
                    f'textures/entity/blueprint/boss/{name}.png',
                    f'textures/entity/blueprint/boss/{name}_body.png'):
            paths.add('src/main/resources/assets/dynasty/' + rel)
    resources, classes = [], []
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), 'Duplicate Jar entries'
        for rel in sorted(paths):
            entry = rel.removeprefix('src/main/resources/')
            content = (work / rel).read_bytes()
            assert z.read(entry) == content, entry
            resources.append({'entry': entry, 'sha256': digest(content)})
        expected = {
            'BlindMarshalRenderer', 'BlindMarshalRenderer$1',
            'BlindMarshalRenderer$ProjectileRenderer', 'BlindMarshalRenderer$ProjectileRenderer$1',
            'BlindMarshalRenderer$StormFog', 'TaoyanCauldronRenderer', 'TaoyanCauldronRenderer$1',
            'TaoyanCauldronRenderer$SpellRenderer', 'TaoyanCauldronRenderer$SpellRenderer$1',
        }
        for name in sorted(expected):
            entry = f'com/dynasty/blueprint/boss/client/{name}.class'
            classes.append({'entry': entry, 'sha256': digest(z.read(entry))})
    changes = [rel for rel, sha in snapshot['sha256'].items()
               if not (ROOT / rel).is_file() or digest((ROOT / rel).read_bytes()) != sha]
    pre = json.loads((OUT / 'preflight.json').read_text())
    assert all(row['matches_accepted_art'] and row['path'] not in changes for row in pre['accepted_art'])
    for rel, sha in protected.items():
        assert digest((ROOT / rel).read_bytes()) == sha, rel
    bytecode = (OUT / 'renderer-bytecode.txt').read_text()
    sections = bytecode.split('Classfile ')[1:]
    assert len(sections) == 4
    for section in sections:
        actor = '$ProjectileRenderer$1' not in section and '$SpellRenderer$1' not in section
        assert ('\\u0001_body' in section) == actor
    assert 'long 32l' in sections[2], 'Existing 32tick transition missing'
    report = {
        'status': 'BUILD_AND_PACKAGE_PASS_GAME_PENDING',
        'snapshot_files': len(snapshot['sha256']),
        'build': {'result': 'PASS', 'command': './gradlew build --offline --no-daemon --max-workers=2 --console=plain',
                  'java': 'Temurin 17', 'duration_seconds': 29, 'log': 'gradle-build.log',
                  'tasks': ['compileJava', 'processResources', 'jar', 'reobfJar', 'build'],
                  'test_task': 'NO-SOURCE; no gameplay tests executed'},
        'artifact': {'path': str(jar), 'sha256': digest(jar.read_bytes()), 'bytes': jar.stat().st_size,
                     'installed': False, 'pushed': False},
        'packaged_resources': resources, 'packaged_renderer_classes': classes,
        'actor_body_binding_and_legacy_effect_binding': 'PASS_COMPILED_BYTECODE',
        'existing_32tick_transition': 'PRESENT_IN_BYTECODE; not a gameplay observation',
        'accepted_art_matches_prior_delivery': True, 'protected_resources': len(protected),
        'production_input_changes_during_build': changes,
        'old_modpack_target_resource_matches': 0, 'old_modpack_target_resources_checked': 8,
        'new_modpack_artifact_installed': False, 'production_files_edited_by_this_check': False,
        'prior_native_checks_repeated': False, 'game_launched': False, 'game_test': 'PENDING',
        'sound_brightness_user_world': 'UNTOUCHED',
        'remaining': ['Actual client loading, lighting and gameplay observation',
                      'Release coordination with the current multiplayer-accepted Jar; isolated build not installed'],
    }
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    jar_link = html.escape(jar.as_uri(), quote=True)
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>两Boss四形态 · 构建与封装核验</title>
<style>body{{margin:32px auto;padding:0 24px;max-width:1100px;background:#eef0eb;color:#263335;font:16px/1.7 system-ui}}img{{max-width:100%}}a{{color:#245d79}}article{{padding:18px;background:#fff;margin:20px 0;border-radius:10px}}code{{overflow-wrap:anywhere}}</style>
<h1>两Boss四形态 · 构建与封装核验</h1>
<p>2026-10-30：保留已认可形体、贴图、动作和玩法，本轮没有新建或重做生物。</p>
<article><h2>发现并补齐的交付缺口</h2><p>源码四形态与10月28日交付摘要一致；现有整合包Jar的4个模型仍为旧版，4张新身体图集缺失。
现在已从5884个输入文件的独立快照完成正式构建，编译、资源处理、Jar封装与reobfJar全部通过。</p>
<p>新Jar中逐字节核对{len(resources)}项模型、动画、贴图及保护资源；9个Renderer相关类存在。
编译后字节码确认本体使用_body图集，弹射物与地面法术保留原贴图，陶魇原有32tick过渡条件仍在。</p></article>
<article><h2>验证边界</h2><p>本轮是构建和封装检查。test任务没有测试源；没有启动游戏，没有重复旧联机测试。
旧实例与已通过联机验收的Jar没有被替换。游戏加载、正常光照与战斗观感仍待验证。</p>
<p><a href="{jar_link}">独立构建Jar</a> · <a href="report.json">完整核验结果</a> · <a href="gradle-build.log">构建日志</a> · <a href="renderer-bytecode.txt">绑定字节码</a></p>
<p>Jar SHA-256：<code>{report['artifact']['sha256']}</code></p></article>
<p><a href="../continuation-20261028.html">模型、贴图、近景与完整动作预览</a></p>
<p>以下为已有离线预览，非游戏截图。</p><img src="../continuation-overview.png" alt="两Boss四形态与玩家比例参照">
</html>'''
    (OUT / 'index.html').write_text(page)
    print(json.dumps({k: report[k] for k in ('status', 'protected_resources', 'production_input_changes_during_build')}, ensure_ascii=False))
    print(f'{len(resources)} packaged resources; {len(classes)} renderer classes; no installation.')


if __name__ == '__main__':
    main()
