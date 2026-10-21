package com.dynasty.dungeon;

import com.dynasty.structure.DynastyStructurePiece;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Fixed connectors (x6, y1, z0/z15) form a 48-block path across three chunks. */
public final class DungeonProbePiece extends DynastyStructurePiece {
    public record Marker(BlockPos offset,String id,Block block,int symbol){}
    private final int part;
    private final BlockPos origin;
    private final UUID instance;
    public DungeonProbePiece(BlockPos origin,int part,UUID instance){
        super(DungeonContent.PROBE_PIECE.get(),part,new BoundingBox(origin.getX(),origin.getY(),origin.getZ()+part*16,
            origin.getX()+12,origin.getY()+6,origin.getZ()+part*16+15));
        this.origin=origin.immutable();this.part=part;this.instance=instance;setOrientation(Direction.SOUTH);
    }
    public DungeonProbePiece(StructurePieceSerializationContext context,CompoundTag tag){
        super(DungeonContent.PROBE_PIECE.get(),tag);part=tag.getInt("Part");origin=BlockPos.of(tag.getLong("Origin"));instance=tag.getUUID("Instance");
        if(part<0||part>2)throw new IllegalArgumentException("Invalid probe piece");
    }
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext context,CompoundTag tag){
        super.addAdditionalSaveData(context,tag);tag.putInt("Part",part);tag.putLong("Origin",origin.asLong());tag.putUUID("Instance",instance);
    }
    public static List<Marker> markers(){
        var markers=new ArrayList<Marker>();
        markers.add(new Marker(new BlockPos(6,0,7),"core",DungeonContent.CORE.get(),-1));
        for(int i=0;i<3;i++)markers.add(new Marker(new BlockPos(2+i*4,1,5),"seal_"+i,DungeonContent.SEAL.get(),i));
        for(int i=0;i<3;i++)markers.add(new Marker(new BlockPos(2+i*4,3,26),"eye_"+i,DungeonContent.EYE.get(),i+3));
        markers.add(new Marker(new BlockPos(6,0,20),"floor",DungeonContent.FLOOR.get(),-1));
        markers.add(new Marker(new BlockPos(6,0,23),"poison_arrow",DungeonContent.TRAP.get(),-1));
        for(int x=5;x<=7;x++)for(int y=1;y<=3;y++)markers.add(new Marker(new BlockPos(x,y,32),"trial_door",DungeonContent.DOOR.get(),-1));
        return List.copyOf(markers);
    }
    @Override public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,
            BoundingBox clip,ChunkPos chunk,BlockPos reference){
        // Each piece is under 1500 cells. StructurePiece applies chunk clipping
        // to every write; no ChunkEvent, force-load, or deferred global build.
        var stone=Blocks.DEEPSLATE_BRICKS.defaultBlockState();
        fill(level,clip,0,0,0,12,0,15,stone);
        walls(level,clip,0,1,0,12,5,15,stone);
        fill(level,clip,0,6,0,12,6,15,stone);
        fill(level,clip,1,1,1,11,5,14,Blocks.AIR.defaultBlockState());
        for(int z:new int[]{0,15})fill(level,clip,5,1,z,7,3,z,Blocks.AIR.defaultBlockState());
        // A few fixtures provide safe path lighting; the probe is not final art.
        set(level,clip,2,4,8,Blocks.SOUL_LANTERN.defaultBlockState());
        set(level,clip,10,4,8,Blocks.SOUL_LANTERN.defaultBlockState());
        BlockPos core=origin.offset(6,0,7);
        List<BlockPos> positions=markers().stream().map(m->origin.offset(m.offset())).toList();
        for(var marker:markers()){
            int localZ=marker.offset().getZ()-part*16;if(localZ<0||localZ>15)continue;
            set(level,clip,marker.offset().getX(),marker.offset().getY(),localZ,marker.block().defaultBlockState());
            BlockPos absolute=origin.offset(marker.offset());
            if(clip.isInside(absolute)&&level.getBlockEntity(absolute) instanceof DungeonMechanismBlockEntity be)
                be.configure(instance,"probe",marker.id(),core,marker.symbol(),marker.id().equals("core")?positions:List.of());
        }
        if(part==2)createChest(level,clip,random,6,1,10,new ResourceLocation("dynasty","dungeons/probe_supplies"));
    }
}
