package com.dynasty.structure;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import java.lang.reflect.*;

/** Replay the deterministic existing cuboid generator with writes clipped to each chunk. */
public final class LegacyBuildingPiece extends DynastyStructurePiece {
    private final BlockPos origin;private final ResourceLocation feature;private final long seed;
    public LegacyBuildingPiece(BlockPos p,ResourceLocation f,long s){super(DynastyStructures.LEGACY_BUILDING_PIECE.get(),0,new BoundingBox(p.getX()-48,p.getY()-32,p.getZ()-48,p.getX()+72,p.getY()+70,p.getZ()+72));origin=p;feature=f;seed=s;}
    public LegacyBuildingPiece(StructurePieceSerializationContext ctx,CompoundTag n){super(DynastyStructures.LEGACY_BUILDING_PIECE.get(),n);origin=BlockPos.of(n.getLong("Origin"));feature=new ResourceLocation(n.getString("Feature"));seed=n.getLong("Seed");}
    protected void addAdditionalSaveData(StructurePieceSerializationContext c,CompoundTag n){n.putLong("Origin",origin.asLong());n.putString("Feature",feature.toString());n.putLong("Seed",seed);}
    @SuppressWarnings("unchecked")
    public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos pivot){
        var raw=net.minecraftforge.registries.ForgeRegistries.FEATURES.getValue(feature);
        if(raw==null)return;
        WorldGenLevel clipped=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(proxy,method,args)->{
            // Match signatures, not mapped method names: production Forge uses SRG names.
            Class<?>[] types=method.getParameterTypes();
            if(types.length==3 && types[0]==net.minecraft.world.level.levelgen.Heightmap.Types.class && types[1]==int.class && types[2]==int.class)return origin.getY();
            if(args!=null&&args.length>0&&args[0] instanceof BlockPos p&&!clip.isInside(p)){
                if(types.length>=2 && types[1]==net.minecraft.world.level.block.state.BlockState.class)return false;
                if(types.length==1 && method.getReturnType()==boolean.class)return false;
                if(net.minecraft.world.level.block.entity.BlockEntity.class.isAssignableFrom(method.getReturnType()))return null;
            }
            try{return method.invoke(level,args);}catch(InvocationTargetException ex){throw ex.getCause();}
        });
        ((net.minecraft.world.level.levelgen.feature.Feature<NoneFeatureConfiguration>)raw).place(NoneFeatureConfiguration.INSTANCE,clipped,generator,RandomSource.create(seed),origin);
    }
}
