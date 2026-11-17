from pathlib import Path
import json,datetime
B=Path(__file__).resolve().parent
# Actual reviewed selections only; reconstructed copies are not automatically reviews.
R={
'forge-47.3.0':{'ProjectileUtil.java':[[1,160]],'CompoundTag.java':[[375,420]],'ServerLevel.java':[[800,880]],'PersistentEntitySectionManager.java':[[55,135]],'ItemStack.java':[[325,385]]},
'neoforge-47.1.64':{'AbstractArrow.java':[[115,230],[255,485]],'ArrowItem.java':[[1,23]],'CrossbowItem.java':[[300,345]],'LivingEntity.java':[[3012,3071]],'CompoundTag.java':[[394,409]],'Arrow.java':[[1,226]],'Projectile.java':[[1,220]],'DamageSource.java':[[1,153]]},
'vanilla-mcp-1.20.1':{'CrossbowItem.java':[[45,290]],'AbstractArrow.java':[[119,203],[259,386],[390,488]],'LivingEntity.java':[[2802,2849],[2940,3001]],'ArrowItem.java':[[1,18]],'ServerLevel.java':[[802,848]],'ItemStack.java':[[290,352]]}}
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=B/'native-reconstruction.json';d=json.loads(p.read_text())
for f in d['files']:
 ranges=R.get(f['version'],{}).get(Path(f['path']).name,[])
 f['reviewed_ranges']=ranges
 f['read_status']='REVIEWED_FULL' if ranges==[[1,f['lines']]] else 'REVIEWED_SELECTED' if ranges else 'RECONSTRUCTED_NOT_REVIEWED'
 # Byte identity is useful corroboration, but is not independent reading or credit.
 if f['version']=='vanilla-mcp-1.20.1' and Path(f['path']).name=='Arrow.java':
  other=B/'native/neoforge-47.1.64/reading-view'/f['path']
  assert (B/f['reading_view']).read_bytes()==other.read_bytes()
  f['corroboration']={'byte_identical_to_reviewed':'native/neoforge-47.1.64/reading-view/'+f['path'],'independent_reference_credit':0}
d['review_updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(p,d)
p=B/'framework-source-acquisition.json';d=json.loads(p.read_text())
for f in d:
 n=Path(f['path']).name;v=f['version'];r=[]
 if v=='neoforge-47.1.64':r=[[673,693]] if n=='ForgeEventFactory.java' else [[1,f['lines']]]
 elif n=='EntityJoinLevelEvent.java':r=[[1,64]]
 f['reviewed_ranges']=r;f['read_status']='REVIEWED_FULL' if r==[[1,f['lines']]] else 'REVIEWED_SELECTED' if r else 'EXTRACTED_NOT_REVIEWED'
save(p,d)
p=B/'geckolib-source-provenance.json';d=json.loads(p.read_text())
for f in d['files']:
 n=Path(f['path']).name;r={'GeoBone.java':[[119,155],[250,306]],'BoneSnapshot.java':[[1,90],[140,205]]}.get(n,[[1,f['lines']]])
 f['reviewed_ranges']=r;f['read_status']='REVIEWED_FULL' if r==[[1,f['lines']]] else 'REVIEWED_SELECTED'
save(p,d)
print('Recorded native/framework/Gecko actual selections; unreviewed copies remain unreviewed.')
