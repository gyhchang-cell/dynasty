"""Verify exact production bytes, native equipment/load evidence and scope preservation."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
OUT=REPO/'docs/art/guard-art-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 run=sys.argv[1];native=OUT/'native'/run
 assert (native/'PASS.txt').read_text().splitlines()[-1].startswith('PASS:')
 manifest=json.loads((native/'runtime-manifest.json').read_text());production=manifest['production']
 jar=REPO/'build/libs/dynasty-1.4.0.jar';assert sha(jar.read_bytes())==production['jarSha256']
 assert jar.read_bytes()==(REPO/'build/reobfJar/output.jar').read_bytes()
 for path,digest in production['sources'].items():assert sha((REPO/path).read_bytes())==digest,path
 classes={row['path']:row['sha256'] for row in manifest['trees'][1]['files']}
 for f in (REPO/'build/classes/java/main/com/dynasty/client/character').glob('*.class'):
  assert sha(f.read_bytes())==classes[str(f.relative_to(REPO/'build/classes/java/main'))]
 base=Path('/Users/a15356015027/Desktop/dynasty/build/maintenance-artifacts/art-cod6-5-lifecycle/dynasty-1.4.0.jar')
 with zipfile.ZipFile(base) as a,zipfile.ZipFile(jar) as b:
  assert set(a.namelist())==set(b.namelist())
  changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
  assert set(changed)=={'META-INF/MANIFEST.MF','com/dynasty/client/character/DynastyCharacterModel.class'},changed
  assert not any('GuardArtClientQa' in n or 'QuietWindowAgent' in n for n in b.namelist())
 path='src/main/java/com/dynasty/client/character/DynastyCharacterModel.java'
 old=subprocess.check_output(['git','-C',str(REPO),'show','98f8bb68:'+path]).decode();new=(REPO/path).read_text()
 assert old.split('@Override public void setupAnim')[0]==new.split('@Override public void setupAnim')[0],'Geometry changed'
 def body(s):return s.split('/** Also used by deterministic studio QA')[1].split('private void armTarget')[0]
 assert body(old)==body(new),'Original four-role animation changed'
 states=[json.loads((native/f'{i:02d}-state.json').read_text()) for i in range(15)]
 assert all(s['entities']==1 and s['renderedCountMax']==1 for s in states[:12])
 assert len({s['boxes'] for s in states[:12]})==1
 assert all(s['joints']==states[0]['joints'] for s in states[:12])
 baseline=OUT/'native/guard-equipped-baseline-02'
 before=json.loads((baseline/'00-state.json').read_text())
 assert before['joints']==states[0]['joints'] and before['boxes']==states[0]['boxes'],'Added geometry/joints'
 grip=json.loads((native/'grip-sweep.json').read_text());assert grip['samples']==128 and grip['worstSeparationErrorBlocks']<.0001
 for s in states[4:8]:assert abs(s['supportGripSeparationBlocks']-.175)<.0001
 for s in states[13:]:
  assert s['entities']==18 and s['frames']>=120 and s['all18RenderedFraction']>=.8
  assert s['renderedCountMin']==18 and s['renderedCountMax']==18
  assert s['medianFrameMs']<50 and s['p95FrameMs']<100
  assert s['nativeGripSamples']>120 and s['nativeGripMaxSeparationErrorBlocks']<.0001
 live=states[14];assert live['guardsMovedOver1Block']>=12 and live['guardsWithKneeMotion']>=12 and live['guardsNavigatingAtFirstSample']>0
 for sample in live['movementSamples']:assert len(sample['entities'])==18 and all(not m['noAi'] for m in sample['entities'])
 result={'acceptedNative':run,'production':production,'changedJarEntries':changed,'geometryPreserved':True,'originalFourRoleAnimationPreserved':True,'newJoints':0,'newCubes':0,'guardJoints':len(before['joints']),'guardBoxes':before['boxes'],'gripSweep':grip,'load':[{k:s[k] for k in ['stage','medianFrameMs','p95FrameMs','serverAverageTickMs','renderedCountMin','renderedCountMax','frames']} for s in states[12:]],'realFollowing':{k:live[k] for k in ['guardsMovedOver1Block','guardsNavigatingAtFirstSample','guardsWithKneeMotion','nativeGripSamples','nativeGripMaxSeparationErrorBlocks']},'pending':['Paid roster slots/formation scenarios (18 ordinary followers are not 18 paid formation troops)','Natural shooting/reload and combat timing','Two real human clients','Other developers latest primary changes absent from frozen isolated build']}
 (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Verified guard art:',run,'new joints/cubes 0/0, 15 native stages and 128 grip states; JAR',production['jarSha256'])
if __name__=='__main__':main()
