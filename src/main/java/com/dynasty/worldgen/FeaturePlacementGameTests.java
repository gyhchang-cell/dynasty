package com.dynasty.worldgen;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkStatus;
import net.minecraft.world.level.chunk.ProtoChunk;
import net.minecraft.world.level.chunk.UpgradeData;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.List;

/** Real ProtoChunk/WorldGenRegion writes without loading or modifying any saved chunks. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class FeaturePlacementGameTests {
    private static final ChunkPos CENTER = new ChunkPos(-3, -2);

    private static final class Region extends WorldGenRegion {
        int writeAttempts;
        int permissionChecks;
        int blockEntityReads;
        boolean denyWrites;

        Region(ServerLevel level) { super(level, chunks(level), ChunkStatus.FEATURES, 1); }

        @Override public boolean ensureCanWrite(BlockPos pos) {
            permissionChecks++;
            return !denyWrites && super.ensureCanWrite(pos);
        }

        @Override public boolean setBlock(BlockPos pos, BlockState state, int flags, int recursion) {
            writeAttempts++;
            return super.setBlock(pos, state, flags, recursion);
        }

        @Override public BlockEntity getBlockEntity(BlockPos pos) {
            blockEntityReads++;
            return super.getBlockEntity(pos);
        }
    }

    private static List<ChunkAccess> chunks(ServerLevel level) {
        List<ChunkAccess> chunks = new ArrayList<>();
        for (int z = CENTER.z - 2; z <= CENTER.z + 2; z++) {
            for (int x = CENTER.x - 2; x <= CENTER.x + 2; x++) {
                var chunk = new ProtoChunk(new ChunkPos(x, z), UpgradeData.EMPTY, level,
                        level.registryAccess().registryOrThrow(Registries.BIOME), null);
                chunk.setStatus(ChunkStatus.CARVERS);
                chunks.add(chunk);
            }
        }
        return chunks;
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void validFeatureWritesAndChestLootArePreserved(GameTestHelper h) {
        var region = new Region(h.getLevel());
        int minX = CENTER.getMinBlockX() - 16;
        int maxX = CENTER.getMaxBlockX() + 16;
        int minZ = CENTER.getMinBlockZ() - 16;
        int maxZ = CENTER.getMaxBlockZ() + 16;
        for (int x : new int[]{minX, maxX}) {
            for (int z : new int[]{minZ, maxZ}) {
                for (int y : new int[]{region.getMinBuildHeight(), region.getMaxBuildHeight() - 1}) {
                    BlockPos pos = new BlockPos(x, y, z);
                    h.assertTrue(DynastyFeaturePlacement.setBlock(region, pos, Blocks.STONE.defaultBlockState(), 2),
                            "Valid feature boundary write was rejected: " + pos);
                    h.assertTrue(region.getBlockState(pos).is(Blocks.STONE), "Boundary block was not written");
                }
            }
        }
        int y = region.getMinBuildHeight() + 10;
        BlockPos first = new BlockPos(minX, y, minZ);
        BlockPos second = new BlockPos(maxX, y, maxZ);
        var loot = DynastyBuildings.loot("palace_ruin");
        DynastyBuildings.chest(region, RandomSource.create(1), first.getX(), y, first.getZ(), loot);
        DynastyBuildKit.chest(region, RandomSource.create(2), second.getX(), y, second.getZ(), "palace_ruin");
        for (BlockPos pos : new BlockPos[]{first, second}) {
            h.assertTrue(region.getBlockEntity(pos) instanceof ChestBlockEntity, "Valid chest entity missing");
            var tag = region.getBlockEntity(pos).saveWithoutMetadata();
            h.assertTrue(loot.toString().equals(tag.getString("LootTable")), "Chest loot table changed");
        }
        h.assertTrue(region.writeAttempts == 10, "Valid writes were duplicated or lost");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void outsideHeightNeverStoresDummyBlockEntities(GameTestHelper h) {
        var region = new Region(h.getLevel());
        for (int y : new int[]{region.getMinBuildHeight() - 1, region.getMaxBuildHeight(),
                region.getMaxBuildHeight() + 12}) {
            BlockPos pos = new BlockPos(CENTER.getMinBlockX(), y, CENTER.getMinBlockZ());
            h.assertTrue(!DynastyFeaturePlacement.setBlock(region, pos, Blocks.CHEST.defaultBlockState(), 2),
                    "Outside-height chest was accepted");
            DynastyBuildings.chest(region, RandomSource.create(1), pos.getX(), y, pos.getZ(),
                    DynastyBuildings.loot("palace_ruin"));
            DynastyBuildKit.chest(region, RandomSource.create(2), pos.getX(), y, pos.getZ(), "palace_ruin");
            h.assertTrue(region.getChunk(pos).getBlockEntityNbt(pos) == null, "Outside-height DUMMY NBT retained");
        }
        h.assertTrue(region.writeAttempts == 0 && region.permissionChecks == 0,
                "Outside-height writes reached vanilla worldgen");
        h.assertTrue(region.blockEntityReads == 0, "Rejected chests still queried block entities");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void distantFeatureWritesSkipVanillaErrorPath(GameTestHelper h) {
        var region = new Region(h.getLevel());
        int x = CENTER.getMinBlockX();
        int z = CENTER.getMinBlockZ();
        int y = region.getMinBuildHeight() + 10;
        for (BlockPos pos : new BlockPos[]{new BlockPos(x - 17, y, z), new BlockPos(x + 32, y, z),
                new BlockPos(x, y, z - 17), new BlockPos(x, y, z + 32)}) {
            h.assertTrue(!DynastyFeaturePlacement.setBlock(region, pos, Blocks.CHEST.defaultBlockState(), 2),
                    "Distant feature write was accepted: " + pos);
            DynastyBuildings.chest(region, RandomSource.create(1), pos.getX(), y, pos.getZ(),
                    DynastyBuildings.loot("palace_ruin"));
            DynastyBuildKit.chest(region, RandomSource.create(2), pos.getX(), y, pos.getZ(), "palace_ruin");
            h.assertTrue(region.getBlockState(pos).isAir(), "Distant chunk was modified");
            h.assertTrue(region.getChunk(pos).getBlockEntityNbt(pos) == null, "Distant DUMMY NBT retained");
        }
        h.assertTrue(region.writeAttempts == 0 && region.permissionChecks == 0,
                "Distant write reached vanilla's error-logging guard");
        h.assertTrue(region.blockEntityReads == 0, "Rejected chests still queried block entities");
        // An allowed chunk must still honor vanilla's extra permission/retrogen checks.
        region.denyWrites = true;
        h.assertTrue(!DynastyFeaturePlacement.setBlock(region, new BlockPos(x, y, z),
                Blocks.STONE.defaultBlockState(), 2), "Vanilla write restriction was bypassed");
        h.assertTrue(region.writeAttempts == 0 && region.permissionChecks == 1, "Denied write reached setBlock");
        h.succeed();
    }
}
