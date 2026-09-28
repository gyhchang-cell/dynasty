package com.dynasty.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;

/** Bounds shared by the legacy building features, which run in ChunkStatus.FEATURES. */
final class DynastyFeaturePlacement {
    private DynastyFeaturePlacement() { }

    /** Reject a whole legacy feature before writing, rather than silently leave half a building. */
    static boolean fits(WorldGenLevel level, int minX, int minY, int minZ, int maxX, int maxY, int maxZ) {
        if (minY < level.getMinBuildHeight() || maxY >= level.getMaxBuildHeight()) return false;
        if (level instanceof WorldGenRegion region) {
            var c = region.getCenter();
            return SectionPos.blockToSectionCoord(minX) >= c.x - 1
                    && SectionPos.blockToSectionCoord(maxX) <= c.x + 1
                    && SectionPos.blockToSectionCoord(minZ) >= c.z - 1
                    && SectionPos.blockToSectionCoord(maxZ) <= c.z + 1;
        }
        return true;
    }

    static boolean setBlock(WorldGenLevel level, BlockPos pos, BlockState state, int flags) {
        // WorldGenRegion can store DUMMY block-entity NBT even when ProtoChunk rejects the height.
        if (level.isOutsideBuildHeight(pos)) return false;
        if (level instanceof WorldGenRegion region) {
            var center = region.getCenter();
            // FEATURES uses writeRadiusCutoff = 1. The larger read cache is not writable.
            // Filter before ensureCanWrite: that method logs an ERROR for each distant write.
            if (Math.abs(center.x - SectionPos.blockToSectionCoord(pos.getX())) > 1
                    || Math.abs(center.z - SectionPos.blockToSectionCoord(pos.getZ())) > 1) {
                return false;
            }
        }
        // Retain vanilla's additional restrictions, including old-chunk height upgrades.
        return level.ensureCanWrite(pos) && level.setBlock(pos, state, flags);
    }
}
