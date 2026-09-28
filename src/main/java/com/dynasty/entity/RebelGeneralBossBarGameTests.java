package com.dynasty.entity;

import com.dynasty.Dynasty;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.UUID;

/**
 * 叛将血条订阅 + 自然生成落点校验的 GameTest（与 ImperialSoldierGameTests 同一套脚手架）。
 *
 * 注意：这里**不会**真的给 FakePlayer 订阅血条（FakePlayer 没有网络连接，发血条包会 NPE），
 * 所以只断言「进入跟踪范围不会立刻给条」「退订 / 清空不抛异常」这两条真实可达的路径；
 * 逐玩家的显示判定由 {@code tools/eqdev/EqDevLogicTest}（纯逻辑）覆盖。
 *
 * 运行：./gradlew --offline runGameTestServer
 */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class RebelGeneralBossBarGameTests {

    private static DynastyBosses.RebelGeneral rebel(GameTestHelper h) {
        DynastyBosses.RebelGeneral boss = DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());
        boss.setNoAi(true);
        boss.setNoGravity(true);
        return boss;
    }

    private static void place(GameTestHelper h, DynastyBosses.RebelGeneral boss, int x, int y, int z) {
        BlockPos pos = h.absolutePos(new BlockPos(x, y, z));
        boss.setPos(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D);
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void trackingRangeAloneMustNotShowTheBar(GameTestHelper h) {
        DynastyBosses.RebelGeneral boss = rebel(h);
        place(h, boss, 3, 2, 3);
        DynastyBossBarSubscriptions subscriptions =
                new DynastyBossBarSubscriptions(boss, boss.dynastyBossBar());
        FakePlayer player = new FakePlayer(h.getLevel(), new GameProfile(UUID.randomUUID(), "bar-qa"));

        subscriptions.startSeenByPlayer(player);
        h.assertTrue(subscriptions.shownCount() == 0,
                "进入实体跟踪范围（14 区块）不该立刻给血条，要等可见性判定");

        subscriptions.stopSeenByPlayer(player);
        h.assertTrue(subscriptions.shownCount() == 0, "退订后不该留下任何订阅");

        subscriptions.startSeenByPlayer(player);
        subscriptions.clear();
        h.assertTrue(subscriptions.shownCount() == 0, "死亡 / 移除清空后不该留下任何订阅");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void naturalSpawnRejectsBuriedAndCrampedSpots(GameTestHelper h) {
        DynastyBosses.RebelGeneral boss = rebel(h);

        // A) 埋在实心方块里：脚下与身体所在的方块都是石头 → 自然生成必须被拒绝
        h.setBlock(new BlockPos(3, 1, 3), Blocks.STONE.defaultBlockState());
        h.setBlock(new BlockPos(3, 2, 3), Blocks.STONE.defaultBlockState());
        h.setBlock(new BlockPos(3, 3, 3), Blocks.STONE.defaultBlockState());
        place(h, boss, 3, 2, 3);
        h.assertTrue(!boss.checkSpawnRules(h.getLevel(), MobSpawnType.NATURAL),
                "生成在实心方块里必须被拒绝");

        // B) 同一处用刷怪蛋 / 命令：玩家主动召唤仍然放行（不一刀切）
        h.assertTrue(boss.checkSpawnRules(h.getLevel(), MobSpawnType.SPAWN_EGG),
                "刷怪蛋召唤不该被落点校验拦掉");

        // C) 只有两格净空：2.2 格高的 Boss 会被卡住 → 自然生成被拒绝
        h.setBlock(new BlockPos(3, 2, 3), Blocks.AIR.defaultBlockState());
        h.setBlock(new BlockPos(3, 3, 3), Blocks.AIR.defaultBlockState());
        h.setBlock(new BlockPos(3, 1, 3), Blocks.STONE.defaultBlockState());
        h.setBlock(new BlockPos(3, 4, 3), Blocks.STONE.defaultBlockState());
        place(h, boss, 3, 2, 3);
        h.assertTrue(!boss.checkSpawnRules(h.getLevel(), MobSpawnType.NATURAL),
                "净空不足（贴天花板）必须被拒绝");

        // D) 开阔地面：脚下实心、头顶通畅 → 自然生成放行
        h.setBlock(new BlockPos(3, 4, 3), Blocks.AIR.defaultBlockState());
        place(h, boss, 3, 2, 3);
        h.assertTrue(boss.checkSpawnRules(h.getLevel(), MobSpawnType.NATURAL),
                "站在实心地面且身上无碰撞时自然生成应当放行");
        h.succeed();
    }
}
