"""Native PneumaticCraft equipment disarm producer, with whole selected ingress/receipt methods."""
from reference_evidence import Evidence,row,SOURCES,reader
import json
e=Evidence(23);R='TeamPneumatic__pnc-repressurized'
def m(f,names):return [e.ref(R,f,method=n) for n in names]
def at(f,name,start):
 p=list((SOURCES/R).rglob(f+'.java'));assert len(p)==1
 lines=p[0].read_text().splitlines(keepends=True)
 assert name.split('.')[-1]+'(' in lines[start-1]
 ref=e.ref(R,f,span=[start,reader['end_method'](lines,start)])
 ref['unit']='complete_method';ref['method']=name;return ref
refs=m('HackableMobDisarm',['canHack','getHackTime','onHackFinished','doDisarm','addHackInfo','addPostHackInfo'])
refs+=m('IHackableEntity',['canHack','_getHackTime','_onHackFinished','afterHackTick','_addHackInfo','_addPostHackInfo'])
refs+=m('HackClientHandler',['onTriggered','enabledForPlayer','getTriggerKeyBinding'])+m('EntityTrackerClientHandler',['hack'])
refs+=m('RenderEntityTarget',['hack','isInitialized','isPlayerLookingAtTarget','onHackConfirmServer','getHackTime'])+[at('RenderEntityTarget','RenderEntityTarget.tick',101)]
refs+=m('PacketHackingEntityStart',['handle'])+m('PacketHackingEntityFinish',['forEntity','handle'])
refs+=m('HackHandler',['tick','tickServerSide','tickEntityHack','setHackedEntity'])
refs+=m('HackManager',['getInstance','getHackableForEntity'])
refs+=[e.ref(R,'HackManager',method='isInDisplayCooldown',signature='IHackableEntity')]
refs+=[e.ref(R,'CommonArmorRegistry',method='getHackable',signature='Entity entity, Player player')]
refs+=m('HackTickTracker',['trackEntity'])+m('EntityTrackEntryHackable',['isApplicable','addInfo'])
refs+=[e.ref(R,'HackManager',span=[110,110]),e.ref(R,'CommonUpgradeHandlers',span=[41,41]),e.ref(R,'PneumaticCraftRepressurized',span=[167,167]),e.ref(R,'NetworkHandler',span=[176,181]),e.ref(R,'MobAccess')]
rows=[row(23,1,'pnc-native-equipment-disarm-clears-first-slot-independent-of-item-drop-receipt','pending_primary_semantic_review',refs,
 'Native addDefaultEntries registers Mob→HackableMobDisarm; class+alive+any nonempty EquipmentSlot qualify, with no Boss predicate in this game producer. Native key handler→entity targets→hack() requires client initialized and looking; sends entityID C2S. Start server checks entity-tracker upgrade usable and current-world ID exists, saves entity/resetTime then confirms; it does not itself repeat client look condition. Actual HackHandler server tick→tickServerSide→tickEntityHack resolves hackable, requires positive time, increments and on>=60 plus alive calls native _onHackFinished; completion action then tracker registration and finish broadcast, no action-result bool. HackableMobDisarm server enumerates slots; first nonempty doDisarm returns true and terminates loop. Drop chance uses raw Mob hand/armor drop array; >1 means no damage, otherwise probability controls spawn and possibly damage clamp. Regardless of drop roll or spawn return, it clears slot to EMPTY and true. Thus one real equipment removal attempt, not guaranteed one spawned pickup. Manager cache checks canHack on lookup creation and periodic prune (>60 time gap), not on every cached return. Disarm rechecks slot presence but no HP/potion gate. Finish packet only entityID; client resolves entity/current hackable, invokes client no-op finish, registers tracker, clears local hacking and plays finish sound only if those lookups succeeded. Native HUD addInfo uses local hackTime/tracked and _getHackTime to choose progress/finished text; no final slot/result data is sent.',
 'Treat equipment loss as direct control requiring a final producer-specific refusal before stack mutation. Drop absence or unchanged HP cannot identify immunity. A generic completion packet and finished HUD are operation receipts, not proof an equipment stack dropped or the intended slot remains removed. Revalidate native target/source/effect before committing or emitting an authoritative immune reason; do not copy this broad destructive action into Boss feedback.',
 'One candidate for native first-slot disarm mutation and its chance-independent commit; all slots/chance constants/durability and native key/start/tick/finish/HUD are one context chain. Existing pnc-native-persistent-hack-ender-teleport-final-cancellation and hacked-owner-projectile-spawn-suppression own the shared hacking framework and refusal families, which grant no new credit here. Compare Wizardry player Telekinesis022: policy and final producer differ (first Mob slot vs mainhand player with anchoring refusal), but Russell may still merge the equipment-control family. Helper credit0 pending review.',
 'Static pinned93d04cc52714742c4ef747eed82528d0fdbde581 (modern NeoForge), no1.20.1 copy assumption. No native runtime/C2S exploit or guaranteed slot enumeration order asserted. Global armor scheduler/upgrade registration internals, vanilla spawn/drop events and final item pickup not executed/read as full engine source. Packet registration and mod setup call are support statements; full network handlers and actual server tick methods are read. No claim fixed60 wall-clock ticks, actual successful hack, guaranteed UI sound after target changes or immutable entity identity across worlds.')]
print(json.dumps(e.finish(rows,[
 'Generic hacking packets/cache/attachment machinery already master context:0 additional. Only native equipment disarm decision proposed.',
 'Every helper and inventory slot variant is merged. No Boss status table, renderer wrapper or broad utility promoted.',
 'Local fixed cache only; no source acquisition retry, game/GUI/compile/test or production/master/TODO writes.'
]),ensure_ascii=False))
