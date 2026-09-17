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

    /** 国子监 / Imperial Academy（科举联动）*/
    public static final RegistryObject<StructureType<AcademyStructure>> ACADEMY =
            STRUCTURE_TYPES.register("academy", () -> () -> AcademyStructure.CODEC);

    /** 长城关隘 / Great Wall Gate */
    public static final RegistryObject<StructureType<WallGateStructure>> GREAT_WALL_GATE =
            STRUCTURE_TYPES.register("great_wall_gate", () -> () -> WallGateStructure.CODEC);

    /** 皇陵石刻 / Imperial Stone Grove */
    public static final RegistryObject<StructureType<StoneGroveStructure>> STONE_GROVE =
            STRUCTURE_TYPES.register("stone_grove", () -> () -> StoneGroveStructure.CODEC);

    /** 观星台 / Star Altar */
    public static final RegistryObject<StructureType<StarAltarStructure>> STAR_ALTAR =
            STRUCTURE_TYPES.register("star_altar", () -> () -> StarAltarStructure.CODEC);

    public static final RegistryObject<StructurePieceType> PALACE_PIECE =
            PIECE_TYPES.register("palace_piece", PalacePieceType::new);

    public static final RegistryObject<StructurePieceType> PALACE_TOWER_PIECE =
            PIECE_TYPES.register("palace_tower", PalaceTowerPieceType::new);

    public static final RegistryObject<StructurePieceType> MAIN_HALL_PIECE =
            PIECE_TYPES.register("main_hall", MainHallPieceType::new);

    public static final RegistryObject<StructurePieceType> TOMB_PIECE =
            PIECE_TYPES.register("tomb_piece", TombPieceType::new);

    public static final RegistryObject<StructurePieceType> ACADEMY_PIECE =
            PIECE_TYPES.register("academy_piece", AcademyPieceType::new);

    public static final RegistryObject<StructurePieceType> WALL_GATE_PIECE =
            PIECE_TYPES.register("wall_gate_piece", WallGatePieceType::new);

    public static final RegistryObject<StructurePieceType> STONE_GROVE_PIECE =
            PIECE_TYPES.register("stone_grove_piece", StoneGrovePieceType::new);

    public static final RegistryObject<StructurePieceType> STAR_ALTAR_PIECE =
            PIECE_TYPES.register("star_altar_piece", StarAltarPieceType::new);

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

    static final class AcademyPieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new AcademyPiece(DynastyStructures.ACADEMY_PIECE.get(), tag);
        }
    }

    static final class WallGatePieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new WallGatePiece(DynastyStructures.WALL_GATE_PIECE.get(), tag);
        }
    }

    static final class StoneGrovePieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new StoneGrovePiece(DynastyStructures.STONE_GROVE_PIECE.get(), tag);
        }
    }

    static final class StarAltarPieceType implements StructurePieceType {
        @Override
        public net.minecraft.world.level.levelgen.structure.StructurePiece load(
                net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                net.minecraft.nbt.CompoundTag tag) {
            return new StarAltarPiece(DynastyStructures.STAR_ALTAR_PIECE.get(), tag);
        }
    }
}
