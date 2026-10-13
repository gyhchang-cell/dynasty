package com.dynasty.blueprint.artifact;

import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;

/** The sword is obtained by real temple trials, never a generic crafting recipe. */
public final class TaiqingContent {
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<StructureType<?>> STRUCTURES=DeferredRegister.create(Registries.STRUCTURE_TYPE,Dynasty.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES=DeferredRegister.create(Registries.STRUCTURE_PIECE,Dynasty.MODID);
    public static final RegistryObject<Block> SWORD_CASE=BLOCKS.register("taiqing_ancient_sword_case",()->new TaiqingSwordCase(BlockBehaviour.Properties.of().strength(-1,3600000).noOcclusion()));
    public static final RegistryObject<StructureType<TaiqingTempleStructure>> TEMPLE=STRUCTURES.register("taiqing_hidden_temple",()->()->TaiqingTempleStructure.CODEC);
    public static final RegistryObject<StructurePieceType> TEMPLE_PIECE=PIECES.register("taiqing_hidden_temple",()->TaiqingTemplePiece::new);
    public static void register(IEventBus bus){BLOCKS.register(bus);STRUCTURES.register(bus);PIECES.register(bus);}
    private TaiqingContent(){}
}
