package com.dynasty;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * 王朝·连锁采掘（内置，不依赖任何其它模组）。
 *
 * 用法：按住 §e潜行§r 破坏 §f矿石§r 或 §f原木§r，会自动把连成一片的同种方块一起采下来：
 *   * 最多 64 块、最远 4 格；
 *   * 每多挖一块消耗 1 点工具耐久（工具会正常损坏）；
 *   * 掉落物与原版一致（时运/精准采集照常生效）；
 *   * 创造模式不触发（免得误挖）。
 *
 * Built-in chain mining: sneak while breaking an ore or log to mine the whole vein/cluster.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
@SuppressWarnings({"null", "removal"})
public class DynastyChainMining {

    /** 一次最多连带多少块 / maximum blocks per chain */
    public static final int MAX_BLOCKS = 64;
    /** 连带搜索半径（格）/ search radius */
    public static final double RADIUS = 4.0D;

    @SubscribeEvent
    public static void onBlockBreak(BlockEvent.BreakEvent event) {
        if (!(event.getPlayer() instanceof ServerPlayer player)) {
            return;
        }
        if (!(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        // 潜行触发 + 创造模式不触发 / sneak to activate, off in creative
        if (!player.isShiftKeyDown() || player.getAbilities().instabuild) {
            return;
        }
        BlockState state = event.getState();
        if (!isChainable(state)) {
            return;
        }
        ItemStack tool = player.getMainHandItem();
        if (tool.isEmpty() || !tool.isCorrectToolForDrops(state)) {
            return;
        }

        BlockPos origin = event.getPos();
        Set<BlockPos> cluster = collect(level, origin, state);
        if (cluster.size() <= 1) {
            return;
        }

        int broken = 0;
        for (BlockPos pos : cluster) {
            if (pos.equals(origin)) {
                continue;                              // 原方块由原版逻辑处理
            }
            if (tool.isEmpty()) {
                break;
            }
            if (level.destroyBlock(pos, true, player)) {    // 掉落 + 经验照常
                broken++;
                if (tool.isDamageableItem()) {
                    tool.hurtAndBreak(1, player, entity -> entity.broadcastBreakEvent(EquipmentSlot.MAINHAND));
                }
            }
        }
        if (broken <= 0) {
            return;
        }
        player.displayClientMessage(Component.literal("§6[连锁] §r采掘了 §e" + (broken + 1) + "§r 块"), true);
        level.sendParticles(ParticleTypes.CRIT, origin.getX() + 0.5D, origin.getY() + 0.6D,
                origin.getZ() + 0.5D, 18, 1.4D, 1.0D, 1.4D, 0.25D);
        level.sendParticles(ParticleTypes.SMOKE, origin.getX() + 0.5D, origin.getY() + 0.6D,
                origin.getZ() + 0.5D, 10, 1.2D, 0.8D, 1.2D, 0.02D);
        level.playSound(null, origin, SoundEvents.STONE_BREAK, SoundSource.BLOCKS, 1.2F, 0.8F);
    }

    /** 是否可连锁：矿石 + 原木 / chainable blocks: ores and logs */
    public static boolean isChainable(BlockState state) {
        if (state.is(BlockTags.LOGS)) {
            return true;
        }
        ResourceLocation id = ForgeRegistries.BLOCKS.getKey(state.getBlock());
        if (id == null) {
            return false;
        }
        String path = id.getPath();
        return path.endsWith("_ore") || path.endsWith("_ores");
    }

    /** 洪水填充：同种方块、半径内、上限 64 块 / flood fill the connected cluster */
    private static Set<BlockPos> collect(ServerLevel level, BlockPos origin, BlockState state) {
        Set<BlockPos> found = new LinkedHashSet<>();
        Deque<BlockPos> queue = new ArrayDeque<>();
        found.add(origin);
        queue.add(origin);
        double limit = RADIUS * RADIUS;
        while (!queue.isEmpty() && found.size() < MAX_BLOCKS) {
            BlockPos current = queue.poll();
            for (net.minecraft.core.Direction direction : net.minecraft.core.Direction.values()) {
                BlockPos next = current.relative(direction);
                if (found.contains(next)) {
                    continue;
                }
                if (next.distSqr(origin) > limit) {
                    continue;
                }
                if (!level.getBlockState(next).is(state.getBlock())) {
                    continue;
                }
                found.add(next);
                queue.add(next);
                if (found.size() >= MAX_BLOCKS) {
                    break;
                }
            }
        }
        return found;
    }
}
