package com.dynasty.puzzle;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

import java.util.Optional;

/**
 * 三座自然生成的解谜遗迹（结构类型 + 生成点计算）。
 *
 * 生成点：取区块中央的地表高度，把房间放在地表（地板就在地表层），
 * 虚空 / 高度不足直接放弃（沿用项目里既有结构的守卫写法）。
 * 房间朝向与难度档不在这里决定，而是在部件里按坐标哈希算 —— 这样存档重载后完全一致。
 *
 * Three naturally generated puzzle ruins; facing and difficulty are derived
 * deterministically from the origin so reloads never change the answer.
 */
public final class PuzzleRuinStructures {

    private PuzzleRuinStructures() {
    }

    /** 三座遗迹的公共逻辑 / shared logic of the three ruins */
    public abstract static class Ruin extends Structure {

        protected Ruin(StructureSettings settings) {
            super(settings);
        }

        protected abstract StructurePieceType pieceType();

        protected abstract com.dynasty.structure.DynastyStructurePiece createPiece(StructurePieceType type,
                                                                                  int depth, BlockPos corner);

        @Override
        protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
            ChunkPos chunkPos = ctx.chunkPos();
            int x = chunkPos.getMiddleBlockX();
            int z = chunkPos.getMiddleBlockZ();
            int y = ctx.chunkGenerator().getFirstFreeHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG,
                    ctx.heightAccessor(), ctx.randomState());
            if (y <= ctx.heightAccessor().getMinBuildHeight() + 5) {
                return Optional.empty();          // 虚空 / 贴底：不生成，绝不硬塞
            }
            BlockPos controller = new BlockPos(x, y + RuinLayout.CY, z);
            BlockPos corner = new BlockPos(x - RuinLayout.TREASURY_CENTER, y, z - RuinLayout.TREASURY_CENTER);
            return Optional.of(new GenerationStub(controller, builder ->
                    builder.addPiece(createPiece(pieceType(), 0, corner))));
        }
    }

    /** 九霄：观星密室（星盘归位）*/
    public static final class Star extends Ruin {
        public static final Codec<Star> CODEC = simpleCodec(Star::new);

        public Star(StructureSettings settings) {
            super(settings);
        }

        @Override
        protected StructurePieceType pieceType() {
            return com.dynasty.structure.DynastyStructures.STAR_VAULT_PIECE.get();
        }

        @Override
        protected com.dynasty.structure.DynastyStructurePiece createPiece(StructurePieceType type, int depth,
                                                                          BlockPos corner) {
            return new PuzzleRuinPiece.Star(type, depth, corner);
        }

        @Override
        public StructureType<?> type() {
            return com.dynasty.structure.DynastyStructures.STAR_VAULT.get();
        }
    }

    /** 主世界：古乐遗址（编钟回声）*/
    public static final class Bell extends Ruin {
        public static final Codec<Bell> CODEC = simpleCodec(Bell::new);

        public Bell(StructureSettings settings) {
            super(settings);
        }

        @Override
        protected StructurePieceType pieceType() {
            return com.dynasty.structure.DynastyStructures.MUSIC_RUIN_PIECE.get();
        }

        @Override
        protected com.dynasty.structure.DynastyStructurePiece createPiece(StructurePieceType type, int depth,
                                                                          BlockPos corner) {
            return new PuzzleRuinPiece.Bell(type, depth, corner);
        }

        @Override
        public StructureType<?> type() {
            return com.dynasty.structure.DynastyStructures.MUSIC_RUIN.get();
        }
    }

    /** 幽冥：四象封印室（灯阵）*/
    public static final class Seal extends Ruin {
        public static final Codec<Seal> CODEC = simpleCodec(Seal::new);

        public Seal(StructureSettings settings) {
            super(settings);
        }

        @Override
        protected StructurePieceType pieceType() {
            return com.dynasty.structure.DynastyStructures.SEAL_VAULT_PIECE.get();
        }

        @Override
        protected com.dynasty.structure.DynastyStructurePiece createPiece(StructurePieceType type, int depth,
                                                                          BlockPos corner) {
            return new PuzzleRuinPiece.Lamp(type, depth, corner);
        }

        @Override
        public StructureType<?> type() {
            return com.dynasty.structure.DynastyStructures.SEAL_VAULT.get();
        }
    }
}
