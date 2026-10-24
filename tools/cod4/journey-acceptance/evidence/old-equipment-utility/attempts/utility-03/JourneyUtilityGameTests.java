package com.dynasty;

import com.dynasty.expansion.*;
import com.dynasty.blueprint.artifact.*;
import com.google.gson.*;
import com.mojang.authlib.GameProfile;
import java.nio.file.*;
import java.util.*;
import java.util.function.Consumer;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameType;
import net.minecraftforge.gametest.*;
import net.minecraftforge.registries.ForgeRegistries;

/** QA only. Original school/weapon conditions, actual native damage and kills; no new product contracts. */
@GameTestHolder("dynasty_journey_utility_qa")
@PrefixGameTestTemplate(false)
public final class JourneyUtilityGameTests {
    private static final JsonArray RESULTS = new JsonArray();
    private static final Map<String, JsonObject> METRICS = new HashMap<>();
    private static int sequence;

    private static void metric(String key, String field, Number value) {
        METRICS.computeIfAbsent(key, k -> new JsonObject()).addProperty(field, value);
    }
    private static void observe(GameTestHelper h, String key, String[] items, boolean artifact) {
        try {
            var field = GameTestHelper.class.getDeclaredField("testInfo");
            field.setAccessible(true); // Observe the existing runner outcome, never manufacture a passed callback.
            ((GameTestInfo) field.get(h)).addListener(new GameTestListener() {
                public void testStructureLoaded(GameTestInfo info) { }
                public void testPassed(GameTestInfo info) { finish(info, true); }
                public void testFailed(GameTestInfo info) { finish(info, false); }
                private void finish(GameTestInfo info, boolean pass) {
                    var row = new JsonObject(); row.addProperty("case", key); row.addProperty("native_test", info.getTestName());
                    var ids = new JsonArray(); for (String item : items) ids.add("dynasty:" + item);
                    row.add("items", ids); row.addProperty("pass", pass);
                    row.addProperty("curios_loaded", DynastyCuriosSetup.isLoaded());
                    row.add("measurements", METRICS.getOrDefault(key, new JsonObject()));
                    if (!pass) {
                        row.addProperty("failure", String.valueOf(info.getError()));
                        var diagnostic = new JsonArray();
                        for (var p : h.getLevel().players()) {
                            var d = new JsonObject(); d.addProperty("player", p.getScoreboardName());
                            d.addProperty("position", p.position().toString()); d.addProperty("health", p.getHealth());
                            d.addProperty("on_ground", p.onGround()); d.addProperty("using", p.isUsingItem());
                            d.addProperty("loaded", ArtifactAbility.loaded(h.getLevel(), p.getBoundingBox().inflate(5)));
                            d.addProperty("surrounded", ArtifactCombat.surrounded(p));
                            d.addProperty("artifact_session", String.valueOf(ArtifactAbility.USES.get(p.getUUID())));
                            d.addProperty("nearby", h.getLevel().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(6)).stream().map(e ->
                                e.getType()+":"+e.position()+":hp="+e.getHealth()+":visible="+p.hasLineOfSight(e)+":hands="+e.getMainHandItem()+","+e.getOffhandItem()).toList().toString());
                            diagnostic.add(d);
                        }
                        row.add("failure_diagnostic", diagnostic);
                    }
                    RESULTS.add(row);
                    try { Files.writeString(Path.of(System.getProperty("dynasty.journey.utility.report")),
                        new GsonBuilder().setPrettyPrinting().create().toJson(RESULTS) + "\n"); }
                    catch (Exception error) { throw new RuntimeException(error); }
                    if (artifact) ArtifactGameTests.release(h.getLevel());
                }
            });
        } catch (ReflectiveOperationException error) { throw new RuntimeException(error); }
    }
    private static TestFunction test(String name, String[] items, int timeout, boolean artifact, Consumer<GameTestHelper> body) {
        return new TestFunction("utility_" + name, "oldutility." + name,
            "dynasty_journey_utility_qa:" + (artifact ? "cauldron_pit_test" : "bow_ritual_test"), timeout, 20, true,
            h -> { observe(h, name, items, artifact); body.accept(h); });
    }

    @GameTestGenerator
    public static Collection<TestFunction> cases() {
        var cases = new ArrayList<TestFunction>();
        for (String id : new String[]{"zhanma_dao", "yuchang_dagger", "qinggang_sword", "yitian_sword", "gilded_mace", "sea_trident"}) {
            String key = "school_" + id;
            cases.add(test(key, new String[]{id}, 100, false, h -> school(h, id, key)));
        }
        for (String id : new String[]{"qinggang_sword", "yitian_sword"}) {
            String key = "faction_" + id;
            cases.add(test(key, new String[]{id}, 100, false, h -> faction(h, id, key)));
        }
        for (String id : new String[]{"qilin_war_axe", "baihu_glaive", "thunder_spear", "ziwei_saber"}) {
            String key = "imperial_" + id;
            cases.add(test(key, new String[]{id}, 100, false, h -> imperial(h, id, key)));
        }
        cases.add(test("siege", new String[]{"siege_crossbow"}, 100, false, JourneyUtilityGameTests::siege));
        cases.add(test("tether", new String[]{"rope_dart", "flying_claw"}, 100, false,
            WeaponCueNativeGameTests::actualNativeRopeAndClawContactKeepOnePullWallCollisionCooldownAndNoMissCue));
        cases.add(test("hammer", new String[]{"meteor_hammer"}, 100, false,
            WeaponCueNativeGameTests::actualNativeHammerChargeAndReleasePreserveOriginalAreaDamageAndSingleDurabilityPayment));
        cases.add(test("paired_axes", new String[]{"mandarin_duck_axe"}, 100, false,
            PerfectBlockNativeGameTests::actualFrontBlockedDamageClearsStaggerOnShieldGuardBladeAndPairedAxesWithoutSuitGate));
        cases.add(test("longyin", new String[]{"longyin_zhanma_duanyue_dao"}, 135, true,
            ArtifactGameTests::nativeFrontClashThenSurroundReductionWithRearException));
        cases.add(test("zhanlu", new String[]{"zhanlu_rendao_bamian_jian"}, 115, true,
            ZhanluGameTests::twentyTickWindupFourSecondDisarmAndThirtyPercentHeal));
        String selection = System.getProperty("dynasty.journey.utility.cases", "");
        return selection.isEmpty() ? cases : cases.stream().filter(c -> Arrays.asList(selection.split(",")).contains(c.getTestName().substring("oldutility.".length()))).toList();
    }

    private static ItemStack item(String id) { return new ItemStack(ExpansionContent.item(id)); }
    private static void siege(GameTestHelper h) {
        var p = player(h, "siege_crossbow"); p.setYRot(0); p.setXRot(0);
        var base = p.blockPosition();
        for (var cell : BlockPos.betweenClosed(base.offset(-3, 0, -1), base.offset(3, 4, 14)))
            h.getLevel().setBlock(cell, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 2);
        for (var cell : BlockPos.betweenClosed(base.offset(-3, 0, 12), base.offset(3, 4, 12)))
            h.getLevel().setBlock(cell, net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(), 2);
        var first = target(h, p, "minecraft:zombie", false); first.setPos(p.position().add(0, 0, 4));
        var second = target(h, p, "minecraft:zombie", false); second.setPos(p.position().add(0, 0, 8));
        first.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
        second.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
        var weapon = p.getMainHandItem(); p.getInventory().setItem(10, item("heavy_bolt"));
        h.onEachTick(() -> { if (!p.isRemoved()) p.doTick(); });
        p.gameMode.useItem(p, h.getLevel(), weapon, InteractionHand.MAIN_HAND);
        h.runAfterDelay(32, () -> {
            p.releaseUsingItem();
            h.assertTrue(CrossbowItem.isCharged(weapon) && p.getInventory().getItem(10).isEmpty(), "Actual native loading consumes exactly one original heavy bolt");
            p.gameMode.useItem(p, h.getLevel(), weapon, InteractionHand.MAIN_HAND); p.doTick();
            var arrows = h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.projectile.AbstractArrow.class,
                p.getBoundingBox().inflate(20), a -> a.getOwner() == p);
            h.assertTrue(arrows.size() == 1, "One actual native shot before impact");
            var arrow = arrows.get(0); metric("siege", "spawn_pierce_level", arrow.getPierceLevel());
            h.assertTrue(arrow.getPierceLevel() == 2 && com.dynasty.cod3.EquipmentFeedback.firingWeapon(arrow,p).is(weapon.getItem()),
                "Original piercing and firing identity are checked before physical wall impact resets vanilla piercing");
            h.runAfterDelay(16, () -> { try {
                metric("siege", "first_target_damage", 100000 - first.getHealth());
                metric("siege", "second_target_damage", 100000 - second.getHealth());
                metric("siege", "after_wall_pierce_level", arrow.getPierceLevel());
                metric("siege", "durability_payment", weapon.getDamageValue());
                h.assertTrue(first.getHealth() < 100000 && second.getHealth() < 100000,
                    "One physical native projectile actually damages two collinear hostile targets");
                h.assertTrue(weapon.getDamageValue() == 1 && !CrossbowItem.isCharged(weapon)
                    && weapon.getOrCreateTag().getList("cod4Magazine",10).isEmpty(), "One shot costs one durability and exhausts original magazine");
                h.succeed();
            } finally { arrows.forEach(Entity::discard); first.discard(); second.discard(); close(p); } });
        });
    }
    private static ServerPlayer player(GameTestHelper h, String id) {
        var p = new ServerPlayer(h.getLevel().getServer(), h.getLevel(), new GameProfile(UUID.randomUUID(), "old-utility"));
        p.connection = new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),
            new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND), p);
        p.setGameMode(GameType.SURVIVAL);
        p.setPos(h.absolutePos(new BlockPos(6, 2, 6)).offset(2048 + (++sequence) * 32, 100, 2048).getCenter());
        h.getLevel().getChunkAt(p.blockPosition()); p.setNoGravity(true); p.setOnGround(true);
        p.setItemInHand(InteractionHand.MAIN_HAND, item(id)); p.getFoodData().setFoodLevel(20);
        p.getAttribute(Attributes.ARMOR_TOUGHNESS).setBaseValue(10);
        h.getLevel().addNewPlayer(p);
        return p;
    }
    private static void close(ServerPlayer p) {
        DynastySchoolCombat.forget(p); DynastyTrinkets.forget(p);
        net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));
        p.discard();
    }
    private static void ornaments(ServerPlayer p, String school) {
        String[] ids = school.equals("guard") ? new String[]{"zhenguan_mirror", "huben_bracer"}
            : school.equals("sword") ? new String[]{"liancheng_tassel", "tayun_pendant"} : new String[]{"", ""};
        if (DynastyCuriosSetup.isLoaded()) {
            for (String slot : new String[]{"body", "bracelet", "charm", "back"}) SchoolCombatGameTests.equip(p, slot, ItemStack.EMPTY);
            if (!school.isEmpty()) {
                SchoolCombatGameTests.equip(p, school.equals("guard") ? "body" : "charm", item(ids[0]));
                SchoolCombatGameTests.equip(p, school.equals("guard") ? "bracelet" : "back", item(ids[1]));
            }
        } else {
            p.getInventory().setItem(9, ids[0].isEmpty() ? ItemStack.EMPTY : item(ids[0]));
            p.getInventory().setItem(10, ids[1].isEmpty() ? ItemStack.EMPTY : item(ids[1]));
        }
        DynastyTrinkets.forget(p);
    }
    private static LivingEntity target(GameTestHelper h, ServerPlayer p, String type, boolean small) {
        var entity = (LivingEntity) ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(type)).create(h.getLevel());
        if (entity instanceof Mob mob) mob.setNoAi(true);
        entity.setNoGravity(true); entity.setPos(p.position().add(0, 0, 2));
        entity.getAttribute(Attributes.MAX_HEALTH).setBaseValue(small ? 20 : 100_000);
        entity.setHealth(entity.getMaxHealth()); entity.getAttribute(Attributes.ARMOR).setBaseValue(0);
        h.getLevel().addFreshEntity(entity); return entity;
    }
    private static float strike(GameTestHelper h, ServerPlayer p, String type) {
        var target = target(h, p, type, false);
        try {
            p.setSprinting(false); p.setOnGround(true); p.fallDistance = 0;
            for (int tick = 0; tick < 40; tick++) p.doTick();
            float before = target.getHealth(); p.attack(target); float damage = before - target.getHealth();
            h.assertTrue(damage > 0 && target.isAlive(), "Actual Player.attack must hurt without overkill: " + damage + "/" + before);
            return damage;
        } finally { target.discard(); }
    }
    private static void school(GameTestHelper h, String id, String key) {
        var p = player(h, id);
        try {
            ornaments(p, ""); float plain = strike(h, p, "minecraft:zombie");
            ornaments(p, "guard"); h.assertTrue(DynastySchoolProgression.equippedSynergy(p, "guard"), "Original two-piece guard predicate active");
            float guard = strike(h, p, "minecraft:zombie");
            ornaments(p, "sword"); h.assertTrue(DynastySchoolProgression.equippedSynergy(p, "sword"), "Original sword pair active");
            float sword = strike(h, p, "minecraft:zombie");
            ornaments(p, ""); float revoked = strike(h, p, "minecraft:zombie");
            metric(key, "plain_damage", plain); metric(key, "guard_damage", guard);
            metric(key, "sword_damage", sword); metric(key, "unequipped_damage", revoked);
            h.assertTrue(guard > plain * 1.1F && sword > plain * 1.1F && Math.abs(revoked - plain) < .05F,
                "Actual old weapon keeps both existing school synergies and loses bonus on unequip: " + plain + "/" + guard + "/" + sword + "/" + revoked);
            ornaments(p, "guard");
            for (int i = 0; i < 10; i++) {
                var victim = target(h, p, "minecraft:zombie", true);
                try { for (int tick = 0; tick < 40; tick++) p.doTick(); p.setOnGround(true); p.attack(victim);
                    h.assertTrue(victim.isDeadOrDying(), "Actual old weapon kills hostile fixture " + i); }
                finally { victim.discard(); }
            }
            metric(key, "weapon_level_after_real_kills", DynastyWeaponProgression.level(p.getMainHandItem()));
            metric(key, "guard_rank_after_real_kills", DynastySchoolProgression.rank(p, "guard"));
            h.assertTrue(DynastyWeaponProgression.level(p.getMainHandItem()) >= 2 && DynastySchoolProgression.rank(p, "guard") >= 1,
                "Existing per-stack and selected school growth are earned through actual deaths; no XP/NBT fixture injection");
            h.succeed();
        } finally { close(p); }
    }
    private static void faction(GameTestHelper h, String id, String key) {
        var p = player(h, id);
        String source = id.equals("yitian_sword") ? "rebel_general" : "eunuch_mastermind";
        String target = id.equals("yitian_sword") ? "dynasty:rebel_soldier" : "dynasty:royal_guard";
        try {
            float plain = strike(h, p, target);
            p.getPersistentData().putBoolean("dynasty_firstkill_" + source, true); // Original first-kill condition fixture, not acquisition proof.
            float eligible = strike(h, p, target);
            float other = strike(h, p, "minecraft:zombie");
            p.getPersistentData().remove("dynasty_firstkill_" + source);
            float otherControl = strike(h, p, "minecraft:zombie");
            metric(key, "unqualified_damage", plain); metric(key, "matching_faction_damage", eligible);
            metric(key, "other_faction_damage", other); metric(key, "other_control_damage", otherControl);
            h.assertTrue(eligible > plain * 1.1F && Math.abs(other - otherControl) < .05F,
                "Only original source/faction condition increases real health loss: " + plain + "/" + eligible + "/" + other + "/" + otherControl);
            h.succeed();
        } finally { close(p); }
    }
    private static void imperial(GameTestHelper h, String id, String key) {
        var p = player(h, id);
        try {
            float plain = strike(h, p, "minecraft:zombie");
            p.setItemInHand(InteractionHand.OFF_HAND, item("taiyi_sword")); DynastyTrinkets.forget(p);
            float paired = strike(h, p, "minecraft:zombie");
            p.setItemInHand(InteractionHand.OFF_HAND, item(id)); DynastyTrinkets.forget(p);
            float duplicate = strike(h, p, "minecraft:zombie");
            metric(key, "plain_damage", plain); metric(key, "different_imperial_offhand_damage", paired); metric(key, "same_item_offhand_damage", duplicate);
            h.assertTrue(paired > plain && Math.abs(duplicate - plain) < .05F,
                "Actual primary attack retains original distinct imperial pair benefit, not a duplicate pair: " + plain + "/" + paired + "/" + duplicate);
            h.succeed();
        } finally { close(p); }
    }
}
