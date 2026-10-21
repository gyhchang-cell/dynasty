package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.structure.templatesystem.*;
import java.util.Optional;

/** A newly generated, sealed lava ravine. No placement in existing player chunks or tick jobs. */
public final class ScenicFireTreeStructure extends Structure {
    public static final Codec<ScenicFireTreeStructure> CODEC=simpleCodec(ScenicFireTreeStructure::new);
    public static final ResourceLocation ID=new ResourceLocation("dynasty","scenic_fire_tree");
    public ScenicFireTreeStructure(StructureSettings settings){super(settings);}

    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){
        int x=c.chunkPos().getMiddleBlockX()-23,z=c.chunkPos().getMiddleBlockZ()-23;
        int min=Integer.MAX_VALUE,max=Integer.MIN_VALUE;
        // The footprint must be dry, gently sloped solid terrain. The NBT creates the ravine;
        // it does not assume an existing 47-block cavern or overwrite a saved construction.
        for(int dx:new int[]{0,23,46})for(int dz:new int[]{0,23,46}){
            int y=height(c,x+dx,z+dz);var ground=c.chunkGenerator().getBaseColumn(x+dx,z+dz,c.heightAccessor(),c.randomState()).getBlock(y-1);
            if(y<c.chunkGenerator().getSeaLevel()+2||!ground.getFluidState().isEmpty()||!ground.isSolid())return Optional.empty();
            min=Math.min(min,y);max=Math.max(max,y);
        }
        if(max-min>6)return Optional.empty();
        int west=height(c,x+7,z),east=height(c,x+39,z);
        if(Math.abs(west-east)>1)return Optional.empty();
        int y=Math.min(west,east)-7;
        if(y<c.heightAccessor().getMinBuildHeight()+3||y+43>=c.heightAccessor().getMaxBuildHeight())return Optional.empty();
        if(c.structureTemplateManager().get(ID).isEmpty())return Optional.empty();
        var origin=new BlockPos(x,y,z);
        return Optional.of(new GenerationStub(origin,b->b.addPiece(new Piece(c.structureTemplateManager(),origin))));
    }
    private static int height(GenerationContext c,int x,int z){return c.chunkGenerator().getFirstFreeHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState());}
    @Override public StructureType<?> type(){return DynastyStructures.SCENIC_FIRE_TREE.get();}

    /** Fixed north-facing entrances: template, effect coordinates and terrain survey share one frame. */
    public static final class Piece extends TemplateStructurePiece {
        private static StructurePlaceSettings settings(){return new StructurePlaceSettings().setIgnoreEntities(true).setKeepLiquids(false).setKnownShape(true);}
        public Piece(StructureTemplateManager manager,BlockPos origin){super(DynastyStructures.SCENIC_FIRE_TREE_PIECE.get(),0,manager,ID,ID.toString(),settings(),origin);}
        public Piece(StructurePieceSerializationContext context,CompoundTag tag){super(DynastyStructures.SCENIC_FIRE_TREE_PIECE.get(),tag,context.structureTemplateManager(),id->settings());}
        @Override protected void handleDataMarker(String marker,BlockPos pos,ServerLevelAccessor level,RandomSource random,BoundingBox clip){}
    }
}
