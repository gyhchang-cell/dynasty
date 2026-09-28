package com.dynasty.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.phys.AABB;

/**
 * 生成位置校验（叛将这类 2.2 格高的人形 Boss 专用）。
 *
 * 规则：
 * <ul>
 *   <li>**自然生成 / 区块生成**：脚下必须是可站立的实心面，且实体碰撞箱在落点处不与方块相交
 *       —— 挡住「生成在实心方块里」「贴着天花板卡住」「悬空」的坏位置；</li>
 *   <li>**玩家召唤 / 刷怪蛋 / 命令 / 刷怪笼 / 结构守卫**：一律放行，
 *       不因为一次坏生成就把所有入口砍掉（也保证既有的召唤与结构流程不变）。</li>
 * </ul>
 *
 * Spawn-position validation for tall humanoid bosses: strict for natural spawns
 * (solid footing + collision-free body box), permissive for player/egg/command
 * and structure spawns.
 */
public final class DynastySpawnPlacement {

    private DynastySpawnPlacement() {
    }

    /** 只有自然生成（含区块生成）才做严格校验。/ strict checks apply to natural spawns only. */
    public static boolean strict(MobSpawnType reason) {
        return reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION;
    }

    /**
     * 站立空间是否有效：脚下有可站立面 + 当前位置没有方块碰撞。
     * {@code box} 用实体类型尺寸在候选坐标上生成的碰撞箱（不要用实体当前位置的箱子）。
     */
    public static boolean hasStandingSpace(LevelAccessor level, BlockPos pos, AABB box) {
        if (level == null || pos == null || box == null) {
            return false;
        }
        BlockPos below = pos.below();
        if (!level.getBlockState(below).isFaceSturdy(level, below, Direction.UP)) {
            return false;
        }
        // 整个身体（含高个子 2.2 格）都不能与方块相交：正好挡住半砖天花板、岩浆块顶、实心夹层
        return level.noCollision(null, box);
    }
}
