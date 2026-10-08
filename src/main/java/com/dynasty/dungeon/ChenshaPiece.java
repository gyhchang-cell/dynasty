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
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Global connector coordinates are shared by all 16x16 columns, including negative coordinates. */
public final class ChenshaPiece extends DynastyStructurePiece {
    public record Marker(BlockPos offset,String room,String id,Block block,int symbol){}
    private final BlockPos origin;
    private final int columnX,columnZ;
    private final UUID instance;
    public ChenshaPiece(BlockPos origin,int cx,int cz,UUID instance){
        super(DungeonContent.CHENSHA_PIECE.get(),cz*4+cx,new BoundingBox(origin.getX()+cx*16,origin.getY(),origin.getZ()+cz*16,
            origin.getX()+cx*16+15,origin.getY()+79,origin.getZ()+cz*16+15));
        this.origin=origin.immutable();columnX=cx;columnZ=cz;this.instance=instance;setOrientation(Direction.SOUTH);
    }
    public ChenshaPiece(StructurePieceSerializationContext context,CompoundTag tag){
        super(DungeonContent.CHENSHA_PIECE.get(),tag);origin=BlockPos.of(tag.getLong("Origin"));columnX=tag.getInt("ColumnX");columnZ=tag.getInt("ColumnZ");instance=tag.getUUID("Instance");
        if(columnX<0||columnX>=4||columnZ<0||columnZ>=6)throw new IllegalArgumentException("Invalid chensha column");
    }
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext context,CompoundTag tag){
        tag.putLong("Origin",origin.asLong());tag.putInt("ColumnX",columnX);tag.putInt("ColumnZ",columnZ);tag.putUUID("Instance",instance);
    }
    private static boolean in(int v,int min,int max){return v>=min&&v<=max;}
    private static boolean rect(int x,int z,int x0,int z0,int x1,int z1){return in(x,x0,x1)&&in(z,z0,z1);}
    private static BlockState shell(){return DungeonContent.MASONRY.get().defaultBlockState();}
    /** null leaves the natural terrain untouched. Each column writes only its authored cells. */
    public static BlockState cell(int x,int y,int z){
        BlockState result=null;
        // Entry mound and three-seal hall at the natural surface datum.
        if(rect(x,z,25,0,39,11)&&in(y,72,79))result=y==72||y==79||x==25||x==39||z==0||z==11?shell():Blocks.AIR.defaultBlockState();
        if(rect(x,z,30,0,34,1)&&in(y,73,76))result=Blocks.AIR.defaultBlockState();
        // Upper ambulatory around a 20-block deep horse burial well.
        if(rect(x,z,4,33,59,88)&&in(y,48,57))result=y==48||y==57||x==4||x==59||z==33||z==88?shell():Blocks.AIR.defaultBlockState();
        if(rect(x,z,17,40,25,48)&&in(y,28,55))result=y==28||x==17||x==25||z==40||z==48?shell():Blocks.AIR.defaultBlockState();
        if(rect(x,z,18,41,24,47)&&y==28)result=Blocks.BONE_BLOCK.defaultBlockState();
        // Nine independent vaulted chambers linked by three-block-wide bronze chain bridges.
        if(rect(x,z,4,32,59,89)&&in(y,18,33)){
            boolean chamber=false,edge=false;
            for(int cx:new int[]{4,24,44})for(int cz:new int[]{32,52,72})if(rect(x,z,cx,cz,cx+15,cz+15)){
                chamber=true;edge=x==cx||x==cx+15||z==cz||z==cz+15;
            }
            boolean bridge=in(x,30,33)||in(z,58,61)||in(z,38,41)||in(z,78,81);
            if(y==18)result=Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState();
            else if(y<24)result=Blocks.AIR.defaultBlockState();
            else if(chamber)result=y==24||y==33||edge?shell():Blocks.AIR.defaultBlockState();
            else result=y==24&&bridge?Blocks.CUT_COPPER.defaultBlockState():Blocks.AIR.defaultBlockState();
            if(chamber&&edge&&bridge&&in(y,25,28))result=Blocks.AIR.defaultBlockState();
            if(y==31&&!chamber&&bridge)result=Blocks.CHAIN.defaultBlockState();
        }
        // Side entrances of the mercury room narrow to two blocks so the
        // authored seal doors can close every approach within the marker budget.
        if((x==24||x==39)&&(z==58||z==61)&&in(y,25,28))result=shell();
        // Spherical-ish imperial vault and an annular hazardous moat surrounding the dragon dais.
        if(rect(x,z,8,2,55,29)&&in(y,0,17)){
            double d=Math.pow((x-31.5)/23.5,2)+Math.pow((z-15.5)/13.5,2);
            int roof=8+(int)(9*Math.sqrt(Math.max(0,1-d)));
            if(d<=1.1&&y<=roof)result=y==0||y==roof||d>1?shell():Blocks.AIR.defaultBlockState();
            if(y==0&&d>.55&&d<.8)result=Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState();
            if(rect(x,z,25,10,38,21)&&y==1)result=Blocks.QUARTZ_BLOCK.defaultBlockState();
        }
        // Do not let the arena's north wall block the downward stair connector.
        if(in(x,30,34)&&in(z,27,29)&&in(y,1,4))result=Blocks.AIR.defaultBlockState();
        // Secret artisans' chamber behind one intentionally breakable wall. Outer shell stays protected.
        if(rect(x,z,49,87,61,94)&&in(y,24,31))result=y==24||y==31||x==49||x==61||z==87||z==94?shell():Blocks.AIR.defaultBlockState();
        if(in(x,51,53)&&z==87&&in(y,25,27))result=Blocks.CRACKED_STONE_BRICKS.defaultBlockState();
        // One-way permanent lift shaft and landing connect lower arena to the entrance hall.
        if(rect(x,z,40,6,44,10)&&in(y,0,76))result=y==0||x==40||x==44||z==6||z==10?shell():Blocks.AIR.defaultBlockState();
        if(in(x,40,42)&&z==8&&in(y,1,3))result=Blocks.AIR.defaultBlockState();
        if(in(x,37,42)&&z==8&&in(y,73,75))result=Blocks.AIR.defaultBlockState();
        if(in(x,39,43)&&z==8&&y==72)result=shell();
        // Spike basin beneath the grouped resettable panels.
        if(rect(x,z,30,40,34,42)&&in(y,43,47))result=y==43?shell():Blocks.AIR.defaultBlockState();
        if(rect(x,z,30,40,34,42)&&y==44)result=Blocks.POINTED_DRIPSTONE.defaultBlockState();
        // A restored trap floor must not seal survivors in the pit. This side
        // ladder leads only back to the upper gallery, never past a progression seal.
        if(x==35&&z==41&&in(y,43,51))result=y==43?shell():Blocks.AIR.defaultBlockState();
        if(x==36&&z==41&&in(y,44,48))result=shell();
        if(x==35&&z==41&&in(y,44,48))result=Blocks.LADDER.defaultBlockState()
            .setValue(net.minecraft.world.level.block.LadderBlock.FACING,Direction.WEST);
        // Connectors have final precedence over room floors/ceilings. Otherwise
        // the middle gallery erases the last nine steps of the descending run.
        if(in(x,29,35)){
            int floor=in(z,10,34)?82-z:-1;
            if(floor>=0&&in(y,floor,floor+5))
                result=y==floor||y==floor+5||x==29||x==35?shell():Blocks.AIR.defaultBlockState();
            floor=in(z,59,83)?107-z:-1;
            if(floor>=0&&in(y,floor,floor+5))
                result=y==floor||y==floor+5||x==29||x==35?shell():Blocks.AIR.defaultBlockState();
            floor=in(z,28,52)?z-28:-1;
            if(floor>=0&&in(y,floor,floor+5))
                result=y==floor||y==floor+5||x==29||x==35?shell():Blocks.AIR.defaultBlockState();
        }
        return result;
    }
    /** Airborne cod1 skull per side chamber; no arbitrary cave or mercury-trial spawn points. */
    public static List<BlockPos> middleSkullOffsets(){
        return List.of(new BlockPos(12,28,60),new BlockPos(52,28,60));
    }
    public static List<Marker> markers(){
        var result=new ArrayList<Marker>();
        result.add(new Marker(new BlockPos(27,72,5),"entrance","entrance_core",DungeonContent.CORE.get(),-1));
        for(int i=0;i<3;i++)result.add(new Marker(new BlockPos(27+i*5,73,5),"entrance","seal_"+i,DungeonContent.SEAL.get(),i));
        gate(result,"entrance","entrance_gate",10,73);
        result.add(new Marker(new BlockPos(27,48,37),"shendao","shendao_core",DungeonContent.CORE.get(),-1));
        for(int x=30;x<=34;x++)for(int z=40;z<=42;z++)result.add(new Marker(new BlockPos(x,48,z),"shendao","floor_pit",DungeonContent.FLOOR.get(),-1));
        result.add(new Marker(new BlockPos(30,48,51),"shendao","poison_arrow_a",DungeonContent.TRAP.get(),-1));
        result.add(new Marker(new BlockPos(34,48,54),"shendao","poison_arrow_b",DungeonContent.TRAP.get(),-1));
        result.add(new Marker(new BlockPos(25,24,55),"mercury","mercury_core",DungeonContent.CORE.get(),-1));
        for(int i=0;i<3;i++)result.add(new Marker(new BlockPos(25+i*6,28,57),"mercury","eye_"+i,DungeonContent.EYE.get(),i+3));
        gate(result,"mercury","trial_entry",67,25);gate(result,"mercury","mercury_exit",52,25);
        for(int x:new int[]{24,39})for(int z=59;z<=60;z++)for(int y=25;y<=28;y++)
            result.add(new Marker(new BlockPos(x,y,z),"mercury","trial_entry_side_"+x,DungeonContent.DOOR.get(),-1));
        result.add(new Marker(new BlockPos(24,0,12),"imperial_vault","vault_core",DungeonContent.CORE.get(),-1));
        result.add(new Marker(new BlockPos(20,1,9),"imperial_vault","return_lift",DungeonContent.SHORTCUT_STELE.get(),-1));
        result.add(new Marker(new BlockPos(41,1,8),"imperial_vault","return_lift",DungeonContent.ELEVATOR.get(),-1));
        return List.copyOf(result);
    }
    private static void gate(List<Marker> markers,String room,String id,int z,int y){
        for(int x=30;x<=34;x++)for(int dy=0;dy<4;dy++)markers.add(new Marker(new BlockPos(x,y+dy,z),room,id,DungeonContent.DOOR.get(),-1));
    }
    public static BlockPos core(String room){return markers().stream().filter(m->m.room().equals(room)&&m.block()==DungeonContent.CORE.get()).findFirst().orElseThrow().offset();}
    @Override public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos reference){
        for(int lx=0;lx<16;lx++)for(int lz=0;lz<16;lz++)for(int y=0;y<80;y++){
            int x=columnX*16+lx,z=columnZ*16+lz;var state=cell(x,y,z);
            if(state!=null)set(level,clip,lx,y,lz,state);
        }
        var all=markers();
        for(var marker:all){
            if(marker.offset().getX()/16!=columnX||marker.offset().getZ()/16!=columnZ)continue;
            var state=marker.block().defaultBlockState();
            if(marker.id().equals("poison_arrow_b"))state=state.setValue(DungeonMechanismBlock.FACING,Direction.NORTH);
            set(level,clip,marker.offset().getX()%16,marker.offset().getY(),marker.offset().getZ()%16,state);
            var absolute=origin.offset(marker.offset());
            if(clip.isInside(absolute)&&level.getBlockEntity(absolute) instanceof DungeonMechanismBlockEntity be){
                var controller=origin.offset(core(marker.room()));
                be.configure(instance,marker.room(),marker.id(),controller,marker.symbol(),marker.block()==DungeonContent.CORE.get()?
                    all.stream().filter(m->m.room().equals(marker.room())).map(m->origin.offset(m.offset())).toList():List.of());
                if(marker.block()==DungeonContent.CORE.get()){
                    int required=marker.room().equals("entrance")?7:marker.room().equals("mercury")?56:0;
                    be.configureRoom(required,marker.room().equals("mercury"),origin.offset(25,25,53),origin.offset(38,31,66));
                }
                if(marker.block()==DungeonContent.ELEVATOR.get())be.setDestination(origin.offset(41,73,8));
            }
        }
        fixture(level,clip,new BlockPos(52,25,91),Blocks.CHEST.defaultBlockState(),new ResourceLocation("dynasty:dungeons/chensha_artisan_supplies"));
        for(BlockPos lamp:List.of(new BlockPos(27,75,7),new BlockPos(37,75,7),new BlockPos(12,53,38),new BlockPos(53,53,83),
                new BlockPos(26,30,60),new BlockPos(37,30,60),new BlockPos(20,6,10),new BlockPos(44,6,21)))
            fixture(level,clip,lamp,Blocks.SOUL_LANTERN.defaultBlockState(),null);
    }
    private void fixture(WorldGenLevel level,BoundingBox clip,BlockPos relative,BlockState state,ResourceLocation loot){
        var p=origin.offset(relative);if(!boundingBox.isInside(p)||!clip.isInside(p))return;
        set(level,clip,relative.getX()-columnX*16,relative.getY(),relative.getZ()-columnZ*16,state);
        if(loot!=null&&level.getBlockEntity(p) instanceof ChestBlockEntity chest)chest.setLootTable(loot,instance.getLeastSignificantBits()^p.asLong());
    }
}
