#!/usr/bin/env python3
"""Fixed-source current-stack durability refusal/recovery proposal, no master writes."""
import hashlib
import json
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda raw:hashlib.sha256(raw).hexdigest()
priorp=H/'immune-reference-batch-034.json';prior=json.loads(priorp.read_text())
assert sha(priorp.read_bytes())=='294cbff57eae34cdcb7314542f1f0c1e50305aa6b72263acaba6b01df3c7bf24'
mp=R/prior['provenances'][0]['manifest_path'];ms={x['repo']:x for x in json.loads(mp.read_text())}
refs=[]
def add(repo,prefix,specs):
    m=ms[repo];entries={e['path']:e for e in m['files']}
    for name,bounds in specs:
        e=entries[prefix+name];raw=(R/e['source']).read_bytes();n=len(raw.decode().splitlines())
        for lines in bounds or [[1,n]]:
            refs.append({'repo':repo,'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],
             'lines':lines,'file_sha256':sha(raw),'git_blob_sha1':e['source_blob'],
             'reading_context':'new_actual_source_read036',
             'purpose':'Whole refusal/current-state recovery path or explicit0 registered repair/ticker support; no class/helper/constant credit.'})
add('CyclopsMC/EvilCraft','src/main/java/org/cyclops/evilcraft/',[
 ('enchantment/EnchantmentUnusing.java',None),('enchantment/EnchantmentUnusingConfig.java',None),
 ('blockentity/tickaction/bloodchest/DamageableItemRepairAction.java',None),
 ('blockentity/tickaction/bloodchest/BloodChestRepairActionRegistry.java',None),
 ('blockentity/tickaction/bloodchest/RepairItemTickAction.java',None),
 ('core/blockentity/tickaction/TickComponent.java',None),('core/blockentity/BlockEntityTickingTankInventory.java',None),
 ('blockentity/BlockEntityBloodChest.java',None),('block/BlockBloodChest.java',None),
 ('blockentity/BlockEntityBloodChestConfig.java',None),('block/BlockBloodChestConfig.java',None),
 ('core/blockentity/BlockEntityTankInventory.java',None)])
add('CyclopsMC/CyclopsCore','src/main/java/org/cyclops/cyclopscore/',[
 ('helper/EnchantmentHelpers.java',None),('config/extendedconfig/EnchantmentConfig.java',None),
 ('config/configurabletypeaction/EnchantmentAction.java',None),('blockentity/BlockEntityTickerDelayed.java',None),
 ('inventory/SimpleInventory.java',[[1,109]]),('config/extendedconfig/BlockEntityConfig.java',None),
 ('config/extendedconfig/BlockConfig.java',None),('config/configurabletypeaction/BlockAction.java',None),
 ('config/configurabletypeaction/BlockEntityAction.java',None)])
newrefs=list(refs)
reuse_names={'EvilCraft.java','init/ModBase.java','init/ModBaseVersionable.java','config/ConfigHandler.java',
 'config/ConfigurableType.java','config/extendedconfig/ExtendedConfig.java','config/extendedconfig/ExtendedConfigForge.java',
 'config/configurabletypeaction/ConfigurableTypeAction.java','config/configurabletypeaction/ConfigurableTypeActionForge.java',
 'helper/MinecraftHelpers.java'}
for x in prior['source_refs']:
    relative=x['upstream_path'].split('/cyclopscore/')[-1] if x['repo']=='CyclopsMC/CyclopsCore' else x['upstream_path'].split('/evilcraft/')[-1]
    if relative in reuse_names:
        assert sha((R/x['path']).read_bytes())==x['file_sha256']
        y=dict(x);y['reading_context']='unchanged034_range_reused_not_reread_or_recredited';y['purpose']='Exact accepted034 registration/factory support0; no native/binary compatibility assertion.';refs.append(y)
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();ledger=json.loads(lr);by={x['id']:x for x in ledger}
receipt=A/'immune-feedback-research/coordinator-evilcraft-necromancer-observer-acceptance-20261103.json'
assert sha(receipt.read_bytes())=='c81a6c38277fb9c29bd2947155c07201d78559a32f20c8b9b324e75024b88229'
comp={
 'enigmatic-native-cube-underlimit-random-cancel-retaliation-not-success-gated':'Existing victim equipment random damage refusal/retaliation/cue is retained. This is deterministic current source-held item wear clamp before cancel; no retaliatory damage or RNG refusal, no success sound.',
 'occultism-native-mummy-random-damage-cancellation-assignment-and-conditional-criterion':'Existing aura and direct setCanceled(random) may reset prior cancellation; Unusing only sets true after own mutable item predicate and has no criterion. Not another random chance/effect parameter.',
 'illagerinvasion-native-finite-block-budget-destructive-disarm-and-stun-release':'Existing target shield hitbudget→destructive replacement/stun has a retained counter/state. This preserves current source item by requesting damage=max-5 and refuses at boundary, with no stun/disarm counter; repaired current damage below boundary admits again.',
 'betweenlands-native-stack-ignition-new-use-refusal-with-carried-dropped-erosion-and-break-path-salvage':'Existing burningNBT state refuses NEW activation while carried/dropped erosion and salvage differ. Here current damage itself is both predicate and rewritten clamp; action events denied on source-mainhand versus usedhand, mining releases use while attack doesnot. No extra burn lease, dropped erosion, salvage or ongoing blocking policy.',
 'epicfight-native-guard-resource-break-still-denies-hit-and-cancelled-result-collapses':'Existing target guard consumes stamina and still blocks on resourcebreak. Unusing has no targetguard/payment/animation result wrapper; it clamps attacker item damage and cancels before ordinary attack or break. Same generic cancel API is support0.',
 'vampirism-native-weapon-attack-refusal-explicit-actor-faction-skill-level-result':'Existing actor faction/skill restrictions plus reason message differ from stack wear mutation and repair-mediated reentry. Both are actor eligibility, not victim immunity. No new credit just for source-held lookup, and no invented refusal message here.',
 'reskillable-native-item-refusal-receipt-reconstructs-live-client-requirements-with-independent-profile-sync-and-pause-gated-expiry':'Closest current true-source MAINHAND LivingAttack qualification is already present. New maximum candidate must be whole clamp/refuse/repair policy, not that selector. No item/category packet, live-profile explanation, HUD/lifetime or config/profile synchrony claim here.'}
doc={'schema_version':1,'owner':'program-feedback-review-036','repo':'CyclopsMC/EvilCraft','commit':ms['CyclopsMC/EvilCraft']['commit'],
 'provenances':prior['provenances'],'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_CURRENT_ITEM_DAMAGE_CLAMP_REFUSAL_AND_REPAIR_REENTRY_POLICY',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'evilcraft-native-source-current-stack-wear-clamp-refuses-attack-and-used-hand-break-with-repair-qualified-reentry',
 'source_refs':refs,
 'prior_read_reuse':{'path':str(priorp.relative_to(R)),'sha256':sha(priorp.read_bytes()),
  'new_ranges':len(newrefs),'new_cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in newrefs),
  'reused_ranges':len(refs)-len(newrefs),'limits':'Exact034 support hashes/ranges only.034/035 not reread or self-merged; no credit for shared registration.'},
 'baseline':{'formal_count_observed':len(ledger),'gap_to1000':1000-len(ledger),'ledger_sha256':sha(lr),
  'accepted035_receipt_path':str(receipt.relative_to(R)),'accepted035_receipt_sha256':sha(receipt.read_bytes()),
  'limits':'471 observed coordinator result.033 remains0. No master writes or count increment.'},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(ledger),
  'comparisons':[{'accepted_id':k,'full_semantic_decision_read':{a:b for a,b in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in comp.items()],
  'reading_order':'First5 complete substantive accepted decisions before Unusing source. After actual current-source hand and repair were discovered, complete Vampirism weapon and Reskillable decisions read; Reskillable initial clipped output repaired with separate full_chain and all remaining substantive fields before proposal. No prior source re-audit.'},
 'full_chain':[
  {'stage':'registered actual native handlers','observation':'Existing EvilCraft.onConfigsRegister adds actual EnchantmentUnusingConfig namedunusing. New EnchantmentConfig routes ENCHANTMENT and Forge registry through already-read shared factory/action callbacks; lazy getInstance invokes new EnchantmentUnusing, which registers this instance on MinecraftForge.EVENT_BUS. Constructor categoryBREAKABLE/mainhand, maxlevel1 and canEnchant(isDamageableItem) are acquisition declarations, not runtime event guards. Native enchanting/loot acquisition not expanded.'},
  {'stage':'actual stack qualification and attack cancellation','observation':'NORMAL LivingAttack subscriber first checks target world server and source.getEntity instanceof LivingEntity. Uses that source actor CURRENT MAINHAND, not source.directEntity or a captured attack/projectile stack. EnchantmentHelpers loops raw getEnchantmentTags, compares registry key to each id ResourceLocation and returns first index; no lvl>0 test. If matchingid and unuseTooltrue, setCanceled(true) andreturn. It doesnot stopUsingItem (commented out). No positive damage/source-type/player/creative/target-immunity gate shown; not all entities but any qualifying Living source actor. No explicit alreadycanceled check; Forge dispatch of previously canceled events not expanded.'},
  {'stage':'mutation at refusal boundary','observation':'unuseTool computes damageBorder=getMaxDamage()-5. If current getDamageValue>=border, first calls setDamageValue(border), then returns true causing actual cancel. This may request reducing damage from an overshot value to boundary, not simply prevent additional wear; later attempts at exactly boundary refuse again. If below boundary returnsfalse without modifying. No separate lock flag, elapsed timer, stored target, damage acknowledgement or retry counter. It does not check isDamageableItem in the runtime helper, so canEnchant does not prove malformed/enchant-injected stacks are excluded; lowmax negative parameter native normalization unverified.'},
  {'stage':'mining arm and asymmetric release','observation':'NORMAL BlockEvent.BreakEvent gets player.getUsedItemHand before null-player check. If handnonnull, looks at that hand stack and same raw enchantid predicate, then unuseTool. On true cancels and calls releaseUsingItem. It doesnot explicitly side-check here or use original digging tool/mainhand unconditionally. Both event overloads share one policy; no perhand/method extra credit. The checked nullplayer condition cannot protect earlier dereferences; only conditional code observation, no engine-null event reproduction.'},
  {'stage':'concrete recovery producer','observation':'Existing EvilCraft constructor installs BloodChestRepairActionRegistry; complete registry constructor registers DamageableItemRepairAction first and dispatches selected action. Blood chest/blockentity configs and actual BlockBloodChest.getTicker choose server BlockEntityTickingTankInventory.TickerServer. BlockEntityTickerDelayed.tick invokes update before optional update publication backoff. Server update reads each actual slot and, unless redstone disables ticker, passes current stack to TickComponent. Component chooses Item.class action, canTick, increments progress and invokes onTick; empty/failed qualification resets progress by configured flag. Redstone skips component call, thus doesnot itself reset progress.'},
  {'stage':'repair commits changed stack for later reentry','observation':'RepairItemTickAction canTick requires nonempty tank/item plus actions.canRepair. At required ticks, copies stack, reselects action, simulates cost then if fluid amount sufficient invokes repair doAction=true. Damageable action requires isDamaged, requests setDamageValue(current-1), may add random bad enchant, returnsmultiplier1 with stack. Caller then requests tank drain and writes resulting stack to actual slot via inventory.setItem; SimpleInventory stores it in contents then inventory-change callback. No atomic debit guarantee; native drain internals and callback consumers unexpanded. Concrete conditional recovery: if a normal max100 stack at damage95 is repaired successfully to94 and later used in checked hand, unuseTool sees94<95 and doesnot cancel. No timer/reset packet; every action reads current damage. Native inventory transfer, ItemStack normalization and engine successful action remain outside proof.'},
  {'stage':'termination and feedback boundaries','observation':'Refusal ceases when current selected stack lacks matching enchantid or current damage is below border; no retained peractor denial state to clear. Switching source mainhand also changes future attribution, including possible projectile-owned events; no originalweapon identity preserved. Source has no dedicated message/sound/particle/criterion or refusal packet. Mining releaseUsingItem is the only explicit use-state stop; native client correction/inventory synchronization not inspected. Blood chest open/close sound relates to openers, not repair success or immunity. No independent durable recovery receipt is claimed.'}
 ],
 'critical_boundaries':[
  'At most1 for whole current-stack wear clamp→two event refusals→conditional actual repair/reentry policy. Constants, helpers, two hands/events, source types and repair machine do not earn separate credit.',
  'Source-actor equipment restriction is not Boss target immunity. No Boss gray text or actual rejected-control sound implemented/proven.',
  'Clamping is before cancel; cross-mod final cancellation/side-effect ordering not executed. No rollback guarantee or native durability/inventory exploit claimed.',
  'Enchantment match only identity/index; level0 can satisfy raw tag scan condition. Invalid ID parsing/no registry key may fail; no malformed input tested.',
  'Attack currentMAINHAND versus mining getUsedItemHand, and mining-only release, are preserved as one whole policy—not extra variants.',
  'Repair callback includes optional random bad-enchant branch using nextInt(maxLevel-minLevel). Equal min/max would make zero bound if selected. Such runtime branch not reproduced; successful recovery derivation explicitly assumes normal return/no exception.',
  'Blood/tank/copy/tick/storage/creative/model registration and default parameter differences support0. GUI, textures, render resources and game untouched.',
  'Pinned Core tag is source support, no exact build750 binary equivalence; no native event dispatch, ItemStack, packet, world or GUI execution.'
 ],
 'native_gaps':[
  {'missing':'Native enchanting acquisition, raw ItemStack getters/setters and Forge LivingAttack/Break dispatch/settlement.', 'impact':'Actual registered mod handlers/parameters/cancel calls established; no survival acquisition, exact lowmax clamp result, all final outcomes or generic indestructibility claim.'},
  {'missing':'Native releaseUsingItem, inventory replication, ordinary durability bar/client messages.', 'impact':'No visible denial/recovery receipt or transport delivery claimed. Explicit local method has no dedicated cue.'},
  {'missing':'Native block placement/ticker invocation, inventory transfer and tank drain internals; all auxiliary bad-enchant producers.', 'impact':'Actual registered local tick/repair/write callback path read; no runtime machine transaction, debit or unconditional repair success. Recovery is conditional on completed normal repair and later item use.'},
  {'missing':'Exact deployment equivalence for separately pinned Core support.', 'impact':'Shared manifest/tag metadata verified only, no compiled binary matching.'}
 ],
 'static_examples_not_executed_tests':[
  {'case':'boundary and overshoot','assumptions':'Selected enchanted stack maxDamage100, current95 or98; native setter behaves ordinarily.', 'derivation':'Both request setDamageValue95 then returntrue/cancel. A later identical95 attempt refuses; no cooldown needed.'},
  {'case':'repair enables next attempt','assumptions':'Blood chest accepts stack at95, enough blood, normal successful repair callback and later uses returned stack.', 'derivation':'Repair copy requests94 then stored; next unuseTool predicate94>=95 false, so this handler doesnot cancel. Other handlers/native outcome not asserted.'},
  {'case':'projectile source current weapon mismatch','assumptions':'Delivered LivingAttack source.getEntity is living shooter who has since selected enchanted nearlybroken item.', 'derivation':'Code checks currentmainhand and may clamp/cancel, regardless item that launched projectile. Actual such event timing not demonstrated; no perprojectile boundstack.'},
  {'case':'attack versus mining release','assumptions':'Each respective event qualifies same boundary.', 'derivation':'Both cancel after clamp. Only mining callsreleaseUsingItem; attack comment has no effect. Not proof native ongoing item use persists or stops otherwise.'}
 ],
 'application':'Distinguish actor equipment refusal from target immunity, preserve the actual action stack identity, and define whether rejecting an attempt may mutate/restore resources. Reentry can be current-state-based without a retained lock, but feedback must state the real authoritative reason if added later.',
 'counting':{'formal_baseline_observed':len(ledger),'credit':0,'whole_policy_maximum_pending':1,'helpers_constants_repair_storage_credit':0},
 'next_work':'Coordinator review scope and semantic novelty against existing current-hand item refusal/ignition/guard policies. May merge0. No new production or formal credit before independent acceptance.'}
with (H/'immune-reference-batch-036.json').open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'ranges':len(refs),'new_ranges':len(newrefs),'new_lines':doc['prior_read_reuse']['new_cited_lines'],
 'reused_ranges':doc['prior_read_reuse']['reused_ranges'],'formal_baseline':len(ledger),'maximum_pending':1,'credit':0}))
