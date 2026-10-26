package com.dynasty.dungeon;

import com.dynasty.structure.DynastyStructurePiece;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import java.util.List;
import java.util.UUID;

public final class WangsiPiece extends DynastyStructurePiece {
    private final BlockPos origin;
    private final int columnX,columnZ;
    private final UUID instance;
    public static final BlockPos COURT_CORE=new BlockPos(44,16,94);
    public static final List<BlockPos> BLADES=List.of(new BlockPos(48,20,92),new BlockPos(48,20,96));
    public WangsiPiece(BlockPos origin,int cx,int cz,UUID instance){
        super(DungeonContent.WANGSI_PIECE.get(),cz*6+cx,new BoundingBox(origin.getX()+cx*16,origin.getY(),origin.getZ()+cz*16,
            origin.getX()+cx*16+15,origin.getY()+47,origin.getZ()+cz*16+15));
        this.origin=origin.immutable();columnX=cx;columnZ=cz;this.instance=instance;setOrientation(Direction.SOUTH);
    }
    public WangsiPiece(StructurePieceSerializationContext context,CompoundTag tag){
        super(DungeonContent.WANGSI_PIECE.get(),tag);origin=BlockPos.of(tag.getLong("Origin"));columnX=tag.getInt("ColumnX");columnZ=tag.getInt("ColumnZ");instance=tag.getUUID("Instance");
        if(columnX<0||columnX>=6||columnZ<0||columnZ>=8)throw new IllegalArgumentException("Invalid Wangsi column");
    }
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext context,CompoundTag tag){
        tag.putLong("Origin",origin.asLong());tag.putInt("ColumnX",columnX);tag.putInt("ColumnZ",columnZ);tag.putUUID("Instance",instance);
    }
    @Override public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos reference){
        for(int lx=0;lx<16;lx++)for(int lz=0;lz<16;lz++)for(int y=0;y<48;y++){
            var state=WangsiArchitecture.cell(columnX*16+lx,y,columnZ*16+lz);
            if(state!=null)set(level,clip,lx,y,lz,state);
        }
        mechanism(level,clip,COURT_CORE,true);
        for(var p:BLADES)mechanism(level,clip,p,false);
        loop(level,clip,WangsiLoop.CORE,true);loop(level,clip,WangsiLoop.LAMP,false);
        sluice(level,clip);
        sign(level,clip,new BlockPos(48,44,0),"阴阳界","生魂止步","酆都外郭","枉死城");
        sign(level,clip,new BlockPos(28,15,27),"生魂当铺","旧契未赎","柜中无主","请留归路");
        sign(level,clip,new BlockPos(59,15,27),"买命香火","烛灭客散","勿食供品","勿应招魂");
        sign(level,clip,new BlockPos(48,21,89),"阎罗内衙","火线亮起先退","等铡刀抬起","穿过后再前行");
    }
    private boolean owns(BlockPos p,BoundingBox clip){return boundingBox.isInside(origin.offset(p))&&clip.isInside(origin.offset(p));}
    private void put(WorldGenLevel level,BoundingBox clip,BlockPos p,BlockState state){
        set(level,clip,p.getX()-columnX*16,p.getY(),p.getZ()-columnZ*16,state);
    }
    private void mechanism(WorldGenLevel level,BoundingBox clip,BlockPos p,boolean core){
        if(!owns(p,clip))return;
        put(level,clip,p,(core?DungeonContent.CORE.get():DungeonContent.GUILLOTINE.get()).defaultBlockState()
            .setValue(DungeonMechanismBlock.FACING,Direction.SOUTH));
        if(level.getBlockEntity(origin.offset(p)) instanceof DungeonMechanismBlockEntity be){
            be.configure(instance,"wangsi_court",core?"wangsi_court_core":"guillotine_court",origin.offset(COURT_CORE),-1,
                core?List.of(origin.offset(COURT_CORE),origin.offset(BLADES.get(0)),origin.offset(BLADES.get(1))):List.of());
            if(core)be.configureRoom(0,false,origin.offset(44,17,89),origin.offset(52,21,100));
        }
    }
    private void sign(WorldGenLevel level,BoundingBox clip,BlockPos p,String a,String b,String c,String d){
        if(!owns(p,clip))return;
        put(level,clip,p,Blocks.DARK_OAK_WALL_SIGN.defaultBlockState().setValue(net.minecraft.world.level.block.WallSignBlock.FACING,Direction.NORTH));
        if(level.getBlockEntity(origin.offset(p)) instanceof SignBlockEntity sign){
            SignText text=new SignText();String[] rows={a,b,c,d};
            for(int i=0;i<4;i++)text=text.setMessage(i,Component.literal(rows[i]));
            if(a.equals("阴阳界"))text=text.setColor(net.minecraft.world.item.DyeColor.RED);
            sign.setText(text,true);sign.setWaxed(true);sign.setChanged();
        }
    }
    private void loop(WorldGenLevel level,BoundingBox clip,BlockPos p,boolean core){
        if(!owns(p,clip))return;
        put(level,clip,p,(core?DungeonContent.LOOP_GATE.get():DungeonContent.SOUL_LANTERN_TARGET.get()).defaultBlockState());
        if(level.getBlockEntity(origin.offset(p)) instanceof DungeonMechanismBlockEntity be){
            be.configure(instance,WangsiLoop.ROOM,core?"wangsi_loop_core":WangsiLoop.KEY,origin.offset(WangsiLoop.CORE),-1,
                core?List.of(origin.offset(WangsiLoop.CORE),origin.offset(WangsiLoop.LAMP)):List.of());
            if(core)be.configureRoom(0,false,origin.offset(21,13,43),origin.offset(24,15,44));
        }
    }
    public static List<BlockPos> sluiceGates(){
        var positions=new java.util.ArrayList<BlockPos>();
        for(int y=6;y<=8;y++){
            positions.add(new BlockPos(13,y,95));
            for(int x=14;x<=16;x++)positions.add(new BlockPos(x,y,100));
        }
        return List.copyOf(positions);
    }
    private void sluice(WorldGenLevel level,BoundingBox clip){
        var all=new java.util.ArrayList<BlockPos>();all.add(WangsiSluice.CORE);all.add(WangsiSluice.PUMP);all.addAll(sluiceGates());
        for(var p:all){
            if(!owns(p,clip))continue;
            boolean core=p.equals(WangsiSluice.CORE),pump=p.equals(WangsiSluice.PUMP);
            put(level,clip,p,(core?DungeonContent.CORE.get():pump?DungeonContent.SLUICE_CONTROLLER.get():DungeonContent.DOOR.get()).defaultBlockState());
            if(level.getBlockEntity(origin.offset(p)) instanceof DungeonMechanismBlockEntity be){
                be.configure(instance,WangsiSluice.ROOM,core?"wangsi_sluice_core":pump?"wangsi_pump":"wangsi_drain_gate",
                    origin.offset(WangsiSluice.CORE),pump?0:-1,core?all.stream().map(origin::offset).toList():List.of());
                if(core)be.configureRoom(1,false,origin.offset(5,12,76),origin.offset(18,21,100));
            }
        }
    }
}
