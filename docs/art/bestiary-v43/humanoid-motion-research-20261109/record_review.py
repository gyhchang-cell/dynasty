"""Record the bounded, manually read implementation study; never edits game assets."""
from pathlib import Path
import hashlib
import json
import html
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
GOETY = ROOT / 'build/creature-reference-1000/Polarice3__Goety-2'
IRON = ROOT / 'build/bestiary-v43/references/iron431__Irons-Spells-n-Spellbooks__1.20.1-legacy'
GJAVA = 'src/main/java/com/Polarice3/Goety/client/render/'
IJAVA = 'src/main/java/io/redspace/ironsspellbooks/entity/mobs/'
IRES = 'src/main/resources/assets/irons_spellbooks/'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def source(root, rel, scope='entire file'):
    p = root / rel
    meta = json.loads((root / 'source.json').read_text())
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p),
                repo=meta['repo'], commit=meta['sha'], branch=meta['branch'],
                url=f"https://github.com/{meta['repo']}/blob/{meta['sha']}/{rel}",
                manually_read_scope=scope)

sources = [source(GOETY, GJAVA + p) for p in [
    'model/VillagerServantModel.java', 'model/ZombieVillagerServantModel.java',
    'model/SkeletonVillagerModel.java', 'model/PrisonerModel.java',
    'ZombieVindicatorRenderer.java', 'ZombieVillagerServantRenderer.java',
    'SkeletonVillagerServantRenderer.java', 'PrisonerRenderer.java']]
sources += [source(IRON, IJAVA + p) for p in [
    'abstract_spell_casting_mob/AbstractSpellCastingMobModel.java',
    'wizards/priest/PriestModel.java', 'wizards/cultist/CultistModel.java',
    'wizards/alchemist/ApothecaristModel.java',
    'wizards/alchemist/ApothecaristRenderer.java']]
sources += [source(IRON, IRES + 'geo/piglin_casting_mob.geo.json',
                   'All bones, pivots, cuboid origin/size/UV/inflate/rotation; parsed and read table'),
            source(IRON, IRES + 'animations/casting_animations.json',
                   'Only charged_throw, instant_projectile, long_cast_finish; NOT the entire animation library')]

reviews = [
    dict(id='goety-villager-body-family', role='simple body and garment layering',
         observations=[
             'VillagerServantModel retains full-length 4x12x4 arms and legs; head is villager 8x10x8, body depth6. This is NOT a Steve six-cube donor.',
             'The clothes part is hidden when chest OR leg slot holds ArmorItem. State-dependent clothing visibility is a pipeline decision, not extra joints.',
             'ZombieVindicatorRenderer resolves neutral/hostile texture by isHostile and uses ItemInHandLayer. These two textures do not define two bodies.',
             'ZombieVillagerServantModel instead consumes vanilla ZOMBIE_VILLAGER layers and calls vanilla setupAnim before zombie-arm posing. Do not silently substitute this geometry for VillagerServantModel.'
         ], applicability='For swindler/herb_picker: distinguish garment and actual arm inheritance; no new bodily segmentation is justified by this family.',
         limitations=['Vanilla zombie-villager mesh source not studied in this batch.', 'No native replay or equivalent scene render.'],
         credit='Context only. Vanilla-derived variants and state skins are not separate semantic implementations.'),
    dict(id='goety-skeleton-villager', role='body versus worn shell; handedness',
         observations=[
             'SkeletonVillager inherits VillagerServant body; narrow2x12x2 leg and arm cores are explicit, while arms also retain4x12x4 shell cubes.',
             'prepareMobModel resets both arm poses, resolves main arm, distinguishes aggressive bow/crossbow hold/charge; setupAnim orders arm posing for two-handed actions.',
             'translateToHand temporarily shifts the selected arm X by +/-1, applies its transform, then restores it. A hand interface need not be visible hand geometry.',
             'Original64px atlas actually viewed: bone/light-gray body and dark garment regions; existing card is gray geometry plus separate atlas, not textured/game proof.'
         ], applicability='Preserve held-object interface independently of the bodily mesh; inspect shell visibility before comparing face budgets.',
         limitations=['Already present in reference-review.json and marshal-reference-review.json.', 'No new silhouette/texture acceptance.'],
         credit='Existing family, zero new semantic credit; do not reset old accepted evidence.'),
    dict(id='goety-prisoner-binding-correction', role='profession motion and inherited attachment transform',
         observations=[
             'PrisonerModel: root > upper_body > arms > hold. translateToHand explicitly applies all four transforms in order.',
             'The2.75s MINING clip combines upper_body pitch, arm rotation/translation and hold rotation. It is a work cycle, NOT a verified injury/flee reference.',
             'PrisonerRenderer returns minecraft:textures/entity/villager/villager.png OR minecraft:textures/entity/wandering_trader.png, then applies profession, head, shackles and held-item layers.',
             'Existing005-Goety-2-Prisoner card shows prisoner_chain atlas: that is NOT the returned body atlas. Historical exclusion reason No literal model/renderer texture binding is too broad; body binding is explicit but outside Goety namespace.'
         ], applicability='A shared moving torso must carry both sleeves and the attachment interface. Read all layers before approving an atlas or counting visible faces.',
         limitations=['Correct vanilla1.20.1 body atlases recovered read-only from cached client.jar and viewed; profession/composite surface replay still pending.', 'The incorrect card is quarantined in this study, not silently overwritten in shared ledgers.'],
         credit='No full visual reference credit. Source-chain correction only; body and material verification still required.'),
    dict(id='iron-shared-casting-body', role='state-aware overlay instead of segmented limbs',
         observations=[
             'AbstractSpellCastingMobModel gates custom head/leg motion while authored animation is active, unless explicit always-animate flags permit it.',
             'Walk motion is resolved relative to facing and horizontal momentum, with reduced side displacement; this is not evidence to copy constants into Dynasty.',
             'Arms get walking/bob only outside authored animation; drinking selects actual handedness; casting captures/restores arm snapshots.',
             'CultistModel only overrides texture here. PriestModel selects archevoker geometry, armor-dependent texture and unhappy head movement. Two names alone do not establish two new skeleton implementations.'
         ], applicability='Do not add walk swing over a profession gesture or fake-injury loop; review controller ownership before editing a clip.',
         limitations=['Pinned branch says1.20.1-legacy; actual API/library compatibility not established by the branch name.', 'No whole caster catalog counted or claimed viewed.'],
         credit='Shared base context, not separate credit for each subclass/skin.'),
    dict(id='iron-apothecarist', role='Steve-size limbs with species-specific head and local posture',
         observations=[
             'piglin_casting_mob geometry retains8x12x4 torso and4x12x4 limb cuboids with.25 outer layer;10x8x8 head, snout and separate ears supply species identity.',
             'Armor proxy cubes with empty UV and zero-size hand/item cubes must not be mistaken for textured body detail or extra visible anatomy.',
             'Custom model layers a10degree torso tilt, limb/head offsets, ear motion tied to gait, and swingTime potion throw on top of shared casting controls.',
             'Actual apothecarist64px atlas and existing four body-only source views inspected: coherent skin-colored regions, restrained dark belt/clothing and light fastening details. This is a reference atlas, never copied to Dynasty.',
             'Inspected only three casting clips:25s charged hold, .1875s instant projectile recovery, .1875s finish. Holds, transient clips and loops must remain distinct; three clips are not three creatures.'
         ], applicability='For necessary humanoids: use restrained head-specific features and garment layers on simple limbs; separate item transform from arm body.',
         limitations=['Existing offline front/45/side/back views are body-only; they do not reproduce runtime armor layers, held objects or posture.', 'Renderer base and armor visibility need full review before visible-face comparison.', 'Not a neutral herb-gatherer budget baseline.'],
         credit='Already in reference-review.json textured_body_study: reuse applicable evidence, zero new creature credit for rereading.')
]

old = json.loads((ROOT/'docs/art/bestiary-v43/body-joints-20261102/receipt.json').read_text())
changed = [p for p,h in old['input_sha256'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
receipt = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
    status='source and atlas study saved; production gate still pending',
    targets=['swindler','herb_picker'], sources=sources, reviews=reviews,
    existing_dedup_ledgers=['docs/art/bestiary-v43/reference-review.json','docs/art/bestiary-v43/marshal-reference-review.json'],
    accepted_semantic_credit_added=0,
    counting_note='15 source files are evidence, not15 creatures. Old applicable credits retained; no claim of1000 completion.',
    previous_body_receipt_inputs_changed=changed,
    production_changes=[], game_or_java_started=False,
    forbidden_operations_performed=[],
    next=['Reconstruct profession/composite body view for Prisoner using recovered correct vanilla atlas; reject chain-as-skin card.',
          'Read caster renderer visibility before counting actual body/worn surfaces.',
          'Continue distinct neutral/profession/humanoid implementations and semantic dedup toward required1000; no candidate/file/frame padding.',
          'After applicable reference gate: original-scope body/motion correction only; preserve approved assets; held-object authoring remains texture specialist.'],
    unverified=['neutral baseline for herb_picker','native grounding','20-on-screen performance','fullpack acceptance'])
(OUT/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
vanilla = json.loads((ROOT/'build/bestiary-v43/prisoner-vanilla-atlas-20261109/source.json').read_text())
vanilla['binding_observation'] = 'PrisonerRenderer returns villager or trader body atlas; prisoner_chain is not a body atlas. Two skins are one model reference.'
vanilla['observed_materials'] = 'Villager: coherent muted brown robe with lighter head/hands. Trader: deep blue robe, limited gold edging and red band. Skin switching is not geometry diversity.'
(OUT/'corrected-prisoner-binding.json').write_text(json.dumps(vanilla,ensure_ascii=False,indent=2)+'\n')
anim = json.loads((IRON/IRES/'animations/casting_animations.json').read_text())['animations']
(OUT/'reviewed-animation-sections.json').write_text(json.dumps({n:anim[n] for n in ['charged_throw','instant_projectile','long_cast_finish']},ensure_ascii=False,indent=2)+'\n')
parts=['<!doctype html><meta charset="utf-8"><title>人形身体与动作参考核查</title><style>body{font:16px/1.7 system-ui;max-width:980px;margin:40px auto;background:#eeeae0;color:#232729}article{background:white;padding:24px;margin:20px 0}small{color:#555}</style>',
       '<h1>人形身体与动作：实际来源核查</h1><p>研究记录，不是新模型交付。未启动Java或游戏；未改生产模型、贴图、动画。新增有效1000门槛信用：0。</p>']
for r in reviews:
    parts.append('<article><h2>'+html.escape(r['id'])+'</h2><p>'+html.escape(r['role'])+'</p><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in r['observations'])+'</ul><p>'+html.escape(r['applicability'])+'</p><small>'+html.escape(r['credit'])+'</small></article>')
parts.append('<h2>固定来源</h2><ul>'+''.join('<li><a href="'+s['url']+'">'+html.escape(s['path'].split('/')[-1])+'</a> — '+html.escape(s['manually_read_scope'])+'</li>' for s in sources)+'</ul>')
(OUT/'index.html').write_text(''.join(parts))
print(json.dumps(dict(source_files=len(sources),study_groups=len(reviews),changed_inputs=changed,production_changes=0,accepted_new_credit=0),ensure_ascii=False))
