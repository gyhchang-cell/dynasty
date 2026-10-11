"""Run the legacy generator only in an isolated fixture, with shipped art copies."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from build_models import REPO,ASSETS,OUT
parser=argparse.ArgumentParser();parser.add_argument('--batch',choices=['mechanicals','beasts-priest','armies-tree','shield-skull-guard-scout','corpse-ghost-palanquin-flag','ape-dao','child-paper','elites'],default='mechanicals');args=parser.parse_args()
IDS=['fuhun_baibu_tongzi','zhiren_jianke'] if args.batch=='child-paper' else ['shanjing_shanxiao','zuwu_daoshou'] if args.batch=='ape-dao' else ['shibian_lishi','yinbing_guizu','yinyang_zhijiao_youhun','zhenwang_zhangqiguan'] if args.batch=='corpse-ghost-palanquin-flag' else ['ludun_jiashi','muxue_feilu','pijia_panjiang_huwei','tiesuo_chihou'] if args.batch=='shield-skull-guard-scout' else ['juma_changqiangbing','kuijun_sishi','kumu_shujing','liannu_zhenzu'] if args.batch=='armies-tree' else ['baimu_mowu','bishui_xuanjiao_youzi','chimu_zhuha','fufa_jijiu'] if args.batch=='beasts-priest' else ['qingtong_shuangtoushekui','xunshan_mujiaquan','bazu_digongzhu','mingsha_shixie']
root=REPO/('build/cod2-voxel-generator-'+args.batch);root.mkdir(exist_ok=True)
if args.batch=='elites':IDS=['xianzhen_duantoujiang','qianji_bailian_yanshi','yanshi_clockwork_spider']
def copy(relative):
 p=root/relative;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/relative,p)
copy(Path('tools/blueprint/generate_template_models.mjs'));copy(Path('tools/art/cod2-voxel/owned-models.json'))
copy(Path('src/main/resources/assets/dynasty/textures/mob_effect/internal_injury.png'))
hashes={}
owned=json.loads((REPO/'tools/art/cod2-voxel/owned-models.json').read_text())['ids']
# The priest lives in the generator's default full roster. Keep its full run isolated.
if args.batch!='mechanicals':shutil.copytree(ASSETS/'textures/entity',root/'src/main/resources/assets/dynasty/textures/entity',dirs_exist_ok=True)
for name in owned if args.batch!='mechanicals' else IDS:
 from resource_paths import resource_paths
 for p in resource_paths(name):
  rel=p.relative_to(REPO);copy(rel);hashes[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
if args.batch in ['child-paper','elites']:
 # The legacy generator also reads the unchanged original paper rig after export.
 # Copy its concurrent UV corrections; assert those bytes are protected as well.
 for name in ['fuhun_baibu_tongzi','zhiren_jianke']+(IDS if args.batch=='elites' else []):
  for rel,wanted in json.loads((OUT/'source'/name/'baseline.manifest.json').read_text()).items():
   p=REPO/rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==wanted
   copy(Path(rel));hashes[rel]=wanted
outputs=[]
flags=[[]] if args.batch in ['armies-tree','shield-skull-guard-scout','corpse-ghost-palanquin-flag','ape-dao','child-paper','elites'] else [['--centipede'],['--serpent'],['--toad'],[]] if args.batch=='beasts-priest' else [['--bronze-snake'],['--dog'],['--mining-spider'],['--scorpion']]
for flag in flags:
 result=subprocess.run(['node','tools/blueprint/generate_template_models.mjs',*flag],cwd=root,check=True,capture_output=True,text=True);outputs.append(result.stdout)
for rel,wanted in hashes.items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==wanted,rel
(OUT/('generator-protection-'+args.batch+'.json')).write_text(json.dumps(dict(passed=True,check='Actual old generator preserves authored resources in isolated fixture',stdout=outputs,hashes=hashes),indent=2)+'\n')
print('PASS: actual generator preserved',len(hashes),'resources')
