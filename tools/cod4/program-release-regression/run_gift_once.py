"""Check COD4-7 phase offsets and the released one-time gift routine offline."""

import argparse
from hashlib import sha256
from io import BytesIO
import json
from zipfile import ZipFile

from release_program import CompiledClass, Evaluator, Method, Object, read_decoder
from run_fixture import AUDIT, MC, PARSER, SERVER_PLAYER, pin, release_jar


EVENTS = "com/dynasty/DynastyWorldEvents"
GIFTS = "com/dynasty/DynastyWeaponGifts"
LEGACY = "com/dynasty/LegacyPlayerProgression"
RANK = "com/dynasty/DynastyStats"
COMPOUND = MC + "nbt/CompoundTag"
PLAYER_INVENTORY = MC + "world/entity/player/Inventory"
ITEM = MC + "world/item/Item"
STACK = MC + "world/item/ItemStack"
LOCATION = MC + "resources/ResourceLocation"
LEVEL = MC + "world/level/Level"
REGISTRY = "net/minecraftforge/registries/IForgeRegistry"
COMPONENT = MC + "network/chat/Component"
TICK = Method(GIFTS, "tick", f"(L{SERVER_PLAYER};)V")
SERVER_TICK = Method(EVENTS, "onServerTick", "(Lnet/minecraftforge/event/TickEvent$ServerTickEvent;)V")
COORDINATOR = AUDIT / "resume-20261126/coordinator-cod4-7-gift-polling-and-smithing.json"
GIFT_SHA = "5c34528e8e1e894eda312cd9fb5817d646b5321a990be4fddbc5b0cd52306ee7"
EVENT_SHA = "b9029bf563489dd6427e503f51a99e8a111f59dc3ad3f8061a6ffa8e1222b5e9"


def release_inputs():
    data, binding = release_jar()
    decoder = read_decoder(PARSER)
    classes = {}
    with ZipFile(BytesIO(data)) as jar:
        migration_present = LEGACY + ".class" in jar.namelist()
        for owner, digest in ((EVENTS, EVENT_SHA), (GIFTS, GIFT_SHA)):
            blob = jar.read(owner + ".class")
            if sha256(blob).hexdigest() != digest:
                raise ValueError(f"Wrong release class: {owner}")
            classes[owner] = CompiledClass.read(decoder, blob)
    rows = {r["offset"]: r for r in classes[EVENTS].method_body(SERVER_TICK)}
    for offset, opcode, term in (
        (4, "getstatic", " / END /"), (10, "return", ""),
        (17, "putstatic", "tickCounter"), (20, "op_11", ""),
        (23, "op_a2", ""), (26, "return", ""), (28, "putstatic", "tickCounter"),
        (343, "getfield", "f_19797_"), (346, "op_10", ""), (348, "op_70", ""),
        (349, "op_9a", ""), (354, "invokestatic", "checkDerived"),
        (359, "invokestatic", "DynastyWeaponGifts / tick"), (362, "op_a7", ""),
    ):
        row = rows[offset]
        if row["op"] != opcode or term not in row.get("constant", ""):
            raise ValueError(f"Published polling path diverged at offset {offset}")
    def value(offset):
        return int.from_bytes(bytes.fromhex(rows[offset]["operands_hex"]), "big", signed=True)

    if 7 + value(7) != 11 or 23 + value(23) != 27 or 349 + value(349) != 362:
        raise ValueError("Polling branch targets do not reach the expected path")
    periods = value(20), value(346)
    existing = json.loads(COORDINATOR.read_text())
    if [EVENT_SHA, *periods] != [existing[k] for k in ("sha256", "outer_period", "player_modulus")]:
        raise ValueError("Independent instruction readback disagrees with coordinator")
    return classes, periods, binding | {
        "classes": {EVENTS: EVENT_SHA, GIFTS: GIFT_SHA},
        "legacy_clone_listener_in_release": migration_present,
        "prior_polling_receipt": pin(COORDINATOR),
    }


class GiftAdapter:
    """A single survival player's inventory and the result of a world drop attempt."""

    def __init__(self, rank, bosses, mode):
        self.tag = {"dynasty_boss_kinds": bosses}
        self.player = Object(SERVER_PLAYER, {"rank": rank})
        self.mode = mode
        self.inv = []
        self.drop_attempts = []
        self.drops = []
        self.messages = []
        self.sounds = 0

    @staticmethod
    def evaluate(method):
        return method.owner == GIFTS

    @staticmethod
    def static(owner, name, descriptor):
        return name

    @staticmethod
    def new(owner):
        return Object(owner)

    @staticmethod
    def instance_of(value, owner):
        return isinstance(value, Object) and value.type_name == owner

    def invoke(self, method, receiver, values):
        owner, name = method.owner, method.name
        if name == "<init>" and owner == LOCATION:
            receiver.fields["id"] = ":".join(values)
        elif name == "<init>" and owner == STACK:
            receiver.fields["id"] = values[0].fields["id"]
        elif owner == RANK and name == "getRank":
            return values[0].fields["rank"]
        elif owner == COMPOUND:
            if name == "m_128451_":
                return int(receiver.get(values[0], 0))
            if name == "m_128471_":
                return bool(receiver.get(values[0], False))
            if name == "m_128379_":
                receiver[values[0]] = bool(values[1])
                return None
            raise ValueError(f"Unknown fixture tag call {method}")
        elif owner == SERVER_PLAYER:
            return self.player_call(name, values)
        elif owner == REGISTRY and name == "getValue":
            return Object(ITEM, dict(values[0].fields))
        elif owner == PLAYER_INVENTORY and name == "m_36054_":
            if self.mode != "inventory":
                return False
            self.inv.append(values[0].fields["id"])
            return True
        elif owner == LEVEL and name == "m_6263_":
            self.sounds += 1
        elif owner == STACK and name == "m_41786_":
            return receiver.fields["id"]
        elif owner == COMPONENT and name == "getString":
            return receiver
        elif owner == COMPONENT and name == "m_237113_":
            return values[0]
        else:
            raise ValueError(f"Unknown gift fixture call {method}")
        return None

    def player_call(self, name, values):
        if name == "getPersistentData":
            return self.tag
        if name in {"m_150109_", "m_9236_"}:
            return self
        if name in {"m_20185_", "m_20186_", "m_20189_"}:
            return 0.0
        if name == "m_213846_":
            self.messages.append(values[0])
            return None
        if name == "m_36176_":
            gift = values[0].fields["id"]
            self.drop_attempts.append(gift)
            if self.mode == "drop_accepted":
                self.drops.append(gift)
            if self.mode == "toss_cancelled":
                return None
            # Forge may return the item from the toss even if world addition rejected it.
            return Object(MC + "world/entity/item/ItemEntity")
        raise ValueError(f"Unknown fixture player call {name}")

    def snapshot(self):
        return {
            "inventory": list(self.inv), "drop_attempts": list(self.drop_attempts),
            "world_drops": list(self.drops), "sound_count": self.sounds,
            "message_count": len(self.messages),
            "flags": sorted(k.removeprefix("dynasty_gift_") for k, v in self.tag.items()
                            if k.startswith("dynasty_gift_") and v),
        }


def gift_result(label, vm, adapter, expected, first, next_expected, known_fault=None):
    repeated = adapter.snapshot()
    status = "FAIL"
    if (first, repeated) == (expected, next_expected):
        status = "PASS"
    elif known_fault is not None and first == repeated == known_fault:
        status = "KNOWN_FAIL"
    return {"case": label, "status": status, "expected_first_tick": expected, "first_tick": first,
            "expected_next_tick": next_expected, "next_tick": repeated,
            "executed_methods": sorted(f"{a}.{b}" for a, b in vm.hits)}


def gift_checks(classes):
    mace = "dynasty:gilded_mace"
    all_gifts = [mace, "dynasty:supreme_sword", "dynasty:seven_star_saber"]
    for label, rank, bosses, mode, inventory, drops, refused in (
        ("below_both_thresholds", 11, 4, "inventory", [], [], False),
        ("rank_and_boss_thresholds_then_repeat", 17, 5, "inventory", all_gifts, [], False),
        ("full_inventory_successful_toss_then_repeat", 12, 0, "drop_accepted", [], [mace], False),
        ("cancelled_toss_then_next_poll_can_drop", 12, 0, "toss_cancelled", [], [mace], True),
        ("rejected_world_entity_then_next_poll_can_drop", 12, 0, "spawn_rejected", [], [mace], True),
    ):
        adapter = GiftAdapter(rank, bosses, mode)
        vm = Evaluator({GIFTS: classes[GIFTS]}, adapter)
        vm.invoke(TICK, None, [adapter.player])
        first = adapter.snapshot()
        flags = sorted(g.split(":")[1] for g in inventory + drops)
        expected = {"inventory": inventory, "drop_attempts": drops, "world_drops": drops,
                    "sound_count": len(flags), "message_count": len(flags), "flags": flags}
        if refused:
            known = expected | {"world_drops": []}
            next_expected = expected | {"drop_attempts": drops * 2}
            expected = known | {"sound_count": 0, "message_count": 0, "flags": []}
            adapter.mode = "drop_accepted"
        else:
            next_expected, known = expected, None
        vm.invoke(TICK, None, [adapter.player])
        yield gift_result(label, vm, adapter, expected, first, next_expected, known)


def same_uuid_after_rank_is_eligible(classes):
    old = GiftAdapter(12, 0, "inventory")
    vm = Evaluator({GIFTS: classes[GIFTS]}, old)
    vm.invoke(TICK, None, [old.player])
    assert old.snapshot()["inventory"] == ["dynasty:gilded_mace"]
    for retained in (True, False):
        successor = GiftAdapter(12, 0, "inventory")
        if retained:
            successor.tag = old.tag.copy()
        vm = Evaluator({GIFTS: classes[GIFTS]}, successor)
        vm.invoke(TICK, None, [successor.player])
        first = successor.snapshot()
        vm.invoke(TICK, None, [successor.player])
        expected = {"inventory": [], "drop_attempts": [], "world_drops": [],
                    "sound_count": 0, "message_count": 0, "flags": ["gilded_mace"]}
        mode = "retained" if retained else "lost"
        yield gift_result(f"same_uuid_requalified_after_clone_{mode}_root_receipt",
                          vm, successor, expected, first, expected, None if retained else old.snapshot())


def phase_checks(period, modulus):
    # Use phase offsets at the first eligible server poll. A clone restarts entity age.
    # These ticks model steady play and do not model the exact timing of a login packet.
    join_rows = []
    for age in range(period):
        poll_ages = tuple(age + period * index for index in range(3))
        active = tuple(index + 1 for index, sample in enumerate(poll_ages) if sample % modulus == 0)
        join_rows.append({"age_at_first_poll": age, "eligible_poll_indices": active})
    respawn = []
    for original_age, next_age in ((0, 1), (1, 0), (39, 40), (40, 39)):
        respawn.append({
            "same_uuid": True, "old_age_at_first_poll": original_age,
            "new_age_at_first_poll": next_age,
            "old_checked": bool(join_rows[original_age]["eligible_poll_indices"]),
            "new_checked": bool(join_rows[next_age]["eligible_poll_indices"]),
        })
    return {"period": period, "modulus": modulus, "join_and_rejoin_offsets": join_rows,
            "simulated_clone_offsets": respawn}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--strict", action="store_true", help="Exit 1 for known release defects too")
    args = cli.parse_args()
    classes, periods, binding = release_inputs()
    phase = phase_checks(*periods)
    checks = [*gift_checks(classes), *same_uuid_after_rank_is_eligible(classes)]
    totals = {status: sum(r["status"] == status for r in checks) for status in ("PASS", "KNOWN_FAIL", "FAIL")}
    output = {
        "task": "COD4-7 lines 79–80, scheduled weapon gifts",
        "release": binding, "phase_model": phase, "gift_checks": checks, "totals": totals,
        "limits": [
            "Server and player ages are modeled using the fixed release branch operands.",
            "Released gift tick and grant bytecode run against a mock inventory, registry, and world drop result.",
            "Clone controls model both receipt states at future eligibility. Clone execution and NBT restoration are not part of those controls.",
            "No Forge event, native clone, packet, inventory, item pickup, or save was used.",
        ],
        "native_game_status": "NOT_RUN", "game_starts": 0, "production_writes": 0,
    }
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return int(totals["FAIL"] > 0 or (args.strict and totals["KNOWN_FAIL"] > 0))


if __name__ == "__main__":
    raise SystemExit(main())
