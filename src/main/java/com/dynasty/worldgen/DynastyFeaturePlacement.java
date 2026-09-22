package com.dynasty.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;

/** Bounds shared by the legacy building features, which run in ChunkStatus.FEATURES. */
final class DynastyFeaturePlacement {
    private DynastyFeaturePlacement() { }

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
