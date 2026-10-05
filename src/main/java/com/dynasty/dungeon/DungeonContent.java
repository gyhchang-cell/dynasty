package com.dynasty.dungeon;

import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** No craftable core or item registration; an administrator places the probe structure. */
public final class DungeonContent {
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<BlockEntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,Dynasty.MODID);
    public static final DeferredRegister<StructureType<?>> STRUCTURES=DeferredRegister.create(Registries.STRUCTURE_TYPE,Dynasty.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES=DeferredRegister.create(Registries.STRUCTURE_PIECE,Dynasty.MODID);
    private static RegistryObject<Block> mechanism(String name,DungeonMechanismBlock.Kind kind){
        return BLOCKS.register(name,()->new DungeonMechanismBlock(kind,BlockBehaviour.Properties.of()
            .strength(-1F,3600000F).noLootTable().dynamicShape()
            .lightLevel(s->s.getValue(DungeonMechanismBlock.ACTIVE)?7:0)));
    }
    public static final RegistryObject<Block> CORE=mechanism("dungeon_core",DungeonMechanismBlock.Kind.CORE);
    public static final RegistryObject<Block> SEAL=mechanism("seal_stone",DungeonMechanismBlock.Kind.SEAL);
    public static final RegistryObject<Block> EYE=mechanism("shootable_beast_eye",DungeonMechanismBlock.Kind.TARGET);
    public static final RegistryObject<Block> DOOR=mechanism("seal_door",DungeonMechanismBlock.Kind.DOOR);
    public static final RegistryObject<Block> FLOOR=mechanism("resettable_floor",DungeonMechanismBlock.Kind.FLOOR);
    public static final RegistryObject<Block> TRAP=mechanism("pressure_trap_emitter",DungeonMechanismBlock.Kind.TRAP);
    public static final RegistryObject<BlockEntityType<DungeonMechanismBlockEntity>> MECHANISM=ENTITIES.register("dungeon_mechanism",
        ()->BlockEntityType.Builder.of(DungeonMechanismBlockEntity::new,
            CORE.get(),SEAL.get(),EYE.get(),DOOR.get(),FLOOR.get(),TRAP.get()).build(null));
    public static final RegistryObject<StructureType<DungeonProbeStructure>> PROBE=STRUCTURES.register("dungeon_probe",()->()->DungeonProbeStructure.CODEC);
    public static final RegistryObject<StructurePieceType> PROBE_PIECE=PIECES.register("dungeon_probe_piece",()->DungeonProbePiece::new);
    public static void register(IEventBus bus){BLOCKS.register(bus);ENTITIES.register(bus);STRUCTURES.register(bus);PIECES.register(bus);}
    private DungeonContent(){}
}
