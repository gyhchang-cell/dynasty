package com.dynasty.structure.megabuild;

import com.dynasty.Dynasty;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

import java.util.Optional;
import java.util.function.Function;

/**
 * 大型建筑的结构类型注册（独立 DeferredRegister，交给 Codex 按补丁合并）。
 */
public final class MegabuildStructures {

    private MegabuildStructures() {
    }

    public static final DeferredRegister<StructureType<?>> STRUCTURE_TYPES =
            DeferredRegister.create(Registries.STRUCTURE_TYPE, Dynasty.MODID);
    public static final DeferredRegister<StructurePieceType> PIECE_TYPES =
            DeferredRegister.create(Registries.STRUCTURE_PIECE, Dynasty.MODID);

    public static final RegistryObject<StructureType<CitadelStructure>> TIANGONG_CITADEL =
            STRUCTURE_TYPES.register("tiangong_citadel", () -> () -> CitadelStructure.CODEC);
    public static final RegistryObject<StructureType<MiningStructure>> TIANGONG_MINING_ESTATE =
            STRUCTURE_TYPES.register("tiangong_mining_estate", () -> () -> MiningStructure.CODEC);

    public static final RegistryObject<StructurePieceType> CITADEL_PIECE =
            PIECE_TYPES.register("tiangong_citadel_piece", CitadelPieceType::new);
    public static final RegistryObject<StructurePieceType> MINING_PIECE =
            PIECE_TYPES.register("tiangong_mining_piece", MiningPieceType::new);

    /** 公共生成点：地表高度 + 高度守卫；种子与朝向由坐标决定。*/
    private abstract static class MegabuildStructure extends Structure {

        private final Function<Long, Blueprint> factory;
        private final int size;
        private final int height;

        protected MegabuildStructure(StructureSettings settings, Function<Long, Blueprint> factory,
                                     int size, int height) {
            super(settings);
            this.factory = factory;
            this.size = size;
            this.height = height;
        }

        protected abstract StructurePieceType pieceType();

        @Override
        protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
            ChunkPos chunk = ctx.chunkPos();
            int x = chunk.getMiddleBlockX();
            int z = chunk.getMiddleBlockZ();
            int y = ctx.chunkGenerator().getFirstFreeHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG,
                    ctx.heightAccessor(), ctx.randomState());
            boolean flat=ctx.chunkGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource;
            if (y <= ctx.heightAccessor().getMinBuildHeight() + (flat?1:10)) {
                return Optional.empty();
            }
            // Reject water and steep footprints. Never build huge floating support columns.
            int low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;
            for(int dx:new int[]{-size/2,0,size/2-1})for(int dz:new int[]{-size/2,0,size/2-1}){
                int sample=ctx.chunkGenerator().getFirstFreeHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,ctx.heightAccessor(),ctx.randomState());
                low=Math.min(low,sample);high=Math.max(high,sample);
            }
            if(high-low>8 || (!flat && low<ctx.chunkGenerator().getSeaLevel()) || high+height>=ctx.heightAccessor().getMaxBuildHeight()) return Optional.empty();
            y=low;
            long seed = ctx.random().nextLong();
            int rot = Math.floorMod((int) seed, 4);
            BlockPos corner = new BlockPos(x - size / 2, y, z - size / 2);
            return Optional.of(new GenerationStub(corner, builder ->
                    builder.addPiece(new MegabuildPiece(pieceType(), 0, corner, factory, seed, rot, size, height))));
        }
    }

    public static final class CitadelStructure extends MegabuildStructure {
        public static final Codec<CitadelStructure> CODEC = simpleCodec(CitadelStructure::new);

        public CitadelStructure(StructureSettings settings) {
            super(settings, MegabuildStructures::citadel, TiangongCitadel.SIZE, TiangongCitadel.HEIGHT);
        }

        @Override
        protected StructurePieceType pieceType() {
            return CITADEL_PIECE.get();
        }

        @Override
        public StructureType<?> type() {
            return TIANGONG_CITADEL.get();
        }
    }

    public static final class MiningStructure extends MegabuildStructure {
        public static final Codec<MiningStructure> CODEC = simpleCodec(MiningStructure::new);

        public MiningStructure(StructureSettings settings) {
            super(settings, MegabuildStructures::mining, MiningEstate.SIZE, MiningEstate.HEIGHT);
        }

        @Override
        protected StructurePieceType pieceType() {
            return MINING_PIECE.get();
        }

        @Override
        public StructureType<?> type() {
            return TIANGONG_MINING_ESTATE.get();
        }
    }

    static Blueprint citadel(long seed) {
        return new TiangongCitadel(seed).blueprint();
    }

    static Blueprint mining(long seed) {
        return new MiningEstate(seed).blueprint();
    }

    static final class CitadelPieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                CompoundTag tag) {
            return new MegabuildPiece(CITADEL_PIECE.get(), tag, MegabuildStructures::citadel,
                    TiangongCitadel.SIZE, TiangongCitadel.HEIGHT);
        }
    }

    static final class MiningPieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                CompoundTag tag) {
            return new MegabuildPiece(MINING_PIECE.get(), tag, MegabuildStructures::mining,
                    MiningEstate.SIZE, MiningEstate.HEIGHT);
        }
    }
}
