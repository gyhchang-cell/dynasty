package com.grim3212.assorted.damagenumbers.gametest;

import com.grim3212.assorted.damagenumbers.client.damage.DamageKind;
import com.grim3212.assorted.damagenumbers.client.damage.DamagePopup;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageSources;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.monster.zombie.Zombie;

import java.util.function.BiConsumer;
import java.util.function.Consumer;

/** How a damage number names and writes what hit, which a dedicated server can still check. */
final class DamageNumbersTests {

    private DamageNumbersTests() {
    }

    static void register(BiConsumer<String, Consumer<GameTestHelper>> out) {
        out.accept("damage_numbers_name_their_source", DamageNumbersTests::damageNumbersNameTheirSource);
        out.accept("modded_damage_types_are_sorted", DamageNumbersTests::moddedDamageTypesAreSorted);
    }

    private static void damageNumbersNameTheirSource(GameTestHelper helper) {
        DamageSources sources = helper.getLevel().damageSources();
        Zombie zombie = helper.spawn(EntityTypes.ZOMBIE, new BlockPos(4, 1, 4));

        helper.assertValueEqual(DamageKind.of(sources.inFire()), DamageKind.FIRE, "in fire");
        helper.assertValueEqual(DamageKind.of(sources.lava()), DamageKind.FIRE, "lava");
        helper.assertValueEqual(DamageKind.of(sources.fall()), DamageKind.FALL, "fall");
        helper.assertValueEqual(DamageKind.of(sources.drown()), DamageKind.DROWNING, "drowning");
        helper.assertValueEqual(DamageKind.of(sources.starve()), DamageKind.STARVATION, "starving");
        helper.assertValueEqual(DamageKind.of(sources.cactus()), DamageKind.CACTUS, "cactus");
        helper.assertValueEqual(DamageKind.of(sources.magic()), DamageKind.MAGIC, "magic");
        helper.assertValueEqual(DamageKind.of(sources.mobAttack(zombie)), DamageKind.MELEE, "a zombie's hit");
        helper.assertValueEqual(DamageKind.of(sources.explosion(null, null)), DamageKind.EXPLOSION, "an explosion");
        helper.assertValueEqual(DamageKind.of(sources.generic()), DamageKind.GENERIC, "generic");
        helper.assertValueEqual(DamageKind.of(null), DamageKind.GENERIC, "no known source");

        helper.assertValueEqual(DamagePopup.amount(3.0F), "3", "three");
        helper.assertValueEqual(DamagePopup.amount(2.5F), "2.5", "two and a half");
        helper.succeed();
    }

    // test_spell is in the gametest data's neoforge:is_magic tag, test_curse in nothing.
    private static void moddedDamageTypesAreSorted(GameTestHelper helper) {
        DamageSource spell = testDamage(helper, "test_spell");
        DamageSource curse = testDamage(helper, "test_curse");
        Zombie zombie = helper.spawn(EntityTypes.ZOMBIE, new BlockPos(4, 1, 4));

        helper.assertValueEqual(DamageKind.of(spell), DamageKind.MAGIC, "a modded spell");
        helper.assertValueEqual(DamageKind.of(helper.getLevel().damageSources().thorns(zombie)), DamageKind.MELEE, "thorns, which NeoForge calls magic");

        helper.assertValueEqual(DamageKind.of(curse), DamageKind.GENERIC, "an untagged modded type");
        // Pinned, so a change to the hashing that would recolour every modded type on update fails here.
        helper.assertValueEqual(DamageKind.GENERIC.color(curse), 0xDC8353, "an untagged modded type's own colour");
        helper.assertValueEqual(DamageKind.GENERIC.color(helper.getLevel().damageSources().generic()), DamageKind.GENERIC.color(), "vanilla generic stays grey");
        helper.assertValueEqual(DamageKind.GENERIC.label(curse).getString(), "Test Curse", "an untagged modded type's name, from its id");
        helper.assertValueEqual(DamageKind.GENERIC.label(helper.getLevel().damageSources().generic()), DamageKind.GENERIC.label(), "vanilla generic keeps its label");
        helper.assertValueEqual(DamageKind.nameOf(Identifier.fromNamespaceAndPath("mymod", "hazards/acid__splash")), "Acid Splash", "a nested, double-underscored id");
        helper.succeed();
    }

    private static DamageSource testDamage(GameTestHelper helper, String name) {
        ResourceKey<DamageType> key = ResourceKey.create(Registries.DAMAGE_TYPE, Identifier.fromNamespaceAndPath("assorteddamagenumbers", name));
        return new DamageSource(helper.getLevel().registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(key));
    }
}
