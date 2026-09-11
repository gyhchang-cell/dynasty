package com.dynasty.structure;

import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/**
 * 王朝结构注册：真正的 worldgen 结构（支持 /locate structure、结构集、群系过滤）。
 * Dynasty structure registry: real worldgen structures (locatable, structure-set placed, biome filtered).
 */
public final class DynastyStructures {

    private DynastyStructures() {
    }

    public static final DeferredRegister<StructureType<?>> STRUCTURE_TYPES =
            DeferredRegister.create(Registries.STRUCTURE_TYPE, Dynasty.MODID);

    public static final DeferredRegister<StructurePieceType> PIECE_TYPES =
            DeferredRegister.create(Registries.STRUCTURE_PIECE, Dynasty.MODID);

    /** 皇家宫殿 / Imperial Palace */
    public static final RegistryObject<StructureType<PalaceStructure>> PALACE =
            STRUCTURE_TYPES.register("palace", () -> () -> PalaceStructure.CODEC);

    /** 帝陵地宫 / Imperial Mausoleum */
    public static final RegistryObject<StructureType<TombStructure>> IMPERIAL_TOMB =
            STRUCTURE_TYPES.register("imperial_tomb", () -> () -> TombStructure.CODEC);

    public static final RegistryObject<StructurePieceType> PALACE_PIECE =
            PIECE_TYPES.register("palace_piece", PalacePieceType::new);

    public static final RegistryObject<StructurePieceType> PALACE_TOWER_PIECE =
            PIECE_TYPES.register("palace_tower", PalaceTowerPieceType::new);

    public static final RegistryObject<StructurePieceType> MAIN_HALL_PIECE =
            PIECE_TYPES.register("main_hall", MainHallPieceType::new);

    public static final RegistryObject<StructurePieceType> TOMB_PIECE =
            PIECE_TYPES.register("tomb_piece", TombPieceType::new);

    // 部件反序列化器（放在独立类里，避免初始化器自引用）
    // Deserializers in separate classes to avoid static initializer self-reference.
    static final class PalacePieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new PalacePiece(DynastyStructures.PALACE_PIECE.get(), tag);
        }
    }

    static final class PalaceTowerPieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new PalaceTowerPiece(DynastyStructures.PALACE_TOWER_PIECE.get(), tag);
        }
    }

    static final class MainHallPieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new MainHallPiece(DynastyStructures.MAIN_HALL_PIECE.get(), tag);
        }
    }

    static final class TombPieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new TombPiece(DynastyStructures.TOMB_PIECE.get(), tag);
        }
    }
}
