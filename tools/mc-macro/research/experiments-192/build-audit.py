"""Reproduce one isolated 192 candidate; never writes dist or Desktop apps."""
from pathlib import Path
import argparse,subprocess,shutil
ROOT=Path(__file__).resolve().parents[2]
a=argparse.ArgumentParser();a.add_argument('candidate');a.add_argument('--prepare-only',action='store_true');args=a.parse_args()
patch=Path(__file__).parent/(args.candidate+'.patch')
assert args.candidate.startswith('192-') and '/' not in args.candidate and patch.is_file()
dest=ROOT/'.build/reproduced-192'/args.candidate
dest.mkdir(parents=True,exist_ok=False)
prefix='tools/mc-macro/'
names=subprocess.check_output(['git','ls-tree','-r','--name-only','fe474a227','--',prefix],cwd=ROOT.parents[1],text=True).splitlines()
assert any(n.endswith('/Sources/TellyController.swift') for n in names), 'Baseline tree is empty'
for name in names:
 rel=name.removeprefix(prefix)
 if rel!='build.sh' and not rel.startswith(('Sources/','telemetry/','Tests/')):continue
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(subprocess.check_output(['git','show','fe474a227:'+name],cwd=ROOT))
for change in ['baseline-top-window.patch',args.candidate+'.patch']:
 with (Path(__file__).parent/change).open('rb') as f:
  subprocess.run(['patch','--batch','-p1'],cwd=dest,stdin=f,check=True,stdout=subprocess.DEVNULL)
compat=ROOT/'.build/candidates/191-top-window/.build/sdk-compat'
if compat.is_dir():shutil.copytree(compat,dest/'.build/sdk-compat')
if not args.prepare_only:subprocess.run(['bash','build.sh'],cwd=dest,check=True)
print(dest)
