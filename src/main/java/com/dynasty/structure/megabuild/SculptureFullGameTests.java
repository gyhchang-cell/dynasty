package com.dynasty.structure.megabuild;

import com.dynasty.ritual.ZhenyuanNodeBlockEntity;
import com.dynasty.ritual.ZhenyuanRitualSavedData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTestGenerator;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.gametest.framework.TestFunction;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Collection;
import java.util.HexFormat;
import java.util.List;

/** Opt-in, real millions-of-blocks QA. Only run in the dedicated Gradle GameTest world. */
@GameTestHolder("dynasty_sculpture_full") @PrefixGameTestTemplate(false)
public final class SculptureFullGameTests {
    @GameTestGenerator public static Collection<TestFunction> originalArtworkPlacement(){
        if(!Boolean.getBoolean("dynasty.sculptureFullQa"))return List.of();
        return List.of(new TestFunction("sculpture_full","dynasty_sculpture_full.original_artwork_placement","dynasty_sculpture_full:sculpture_test",24000,0,true,SculptureFullGameTests::run));
    }
    private static void run(GameTestHelper h){
        try{
            h.getLevel().getGameRules().getRule(GameRules.RULE_RANDOMTICKING).set(0,h.getLevel().getServer());
            new Runner(h).start(0);
        }catch(Exception e){h.fail("Full sculpture QA setup: "+e);}
    }
    static final class Runner {
        final GameTestHelper h;final StringBuilder report=new StringBuilder("{\"saveScope\":\"dedicated GameTest world only\",\"results\":[");
        final String[] ids={"longque_sanctuary","yunqi_manor"};SculptureBlueprint blueprint;SculptureWorkshop.Job job;
        BlockPos origin;int which,verifyIndex,nonAir,lights;MessageDigest digest;long started;
        Runner(GameTestHelper h){this.h=h;}
        void start(int index)throws Exception{
            which=index;started=System.currentTimeMillis();blueprint=SculptureBlueprint.load(h.getLevel().getServer().getResourceManager(),ids[index]);
            origin=new BlockPos(16384+index*2048,90,16384);var data=SculptureGameTests.data(h,blueprint,origin);job=new SculptureWorkshop.Job(h.getLevel().getServer(),data,blueprint);
            digest=MessageDigest.getInstance("SHA-256");verifyIndex=nonAir=lights=0;h.runAfterDelay(1,this::tick);
        }
        void tick(){
            try{
                long deadline=System.nanoTime()+35_000_000;
                if(!job.done){
                    if(Boolean.getBoolean("dynasty.sculptureDirectQa")){
                        job.placeDirect();h.runAfterDelay(1,this::tick);return;
                    }
                    // QA may call several unchanged production-budget steps; live commands call only one.
                    for(int step=0;step<32&&!job.done&&System.nanoTime()<deadline;step++)job.step();
                    h.runAfterDelay(1,this::tick);return;
                }
                // Every source voxel, including air, is compared against the live world and hashed back.
                int scanned=0;BlockPos.MutableBlockPos pos=new BlockPos.MutableBlockPos();
                while(verifyIndex<blueprint.volume()&&scanned++<65536&&System.nanoTime()<deadline){
                    int x=verifyIndex%blueprint.width,z=verifyIndex/blueprint.width%blueprint.length,y=verifyIndex/(blueprint.width*blueprint.length);
                    int id=Byte.toUnsignedInt(blueprint.voxels[verifyIndex]);pos.set(origin.getX()+x,origin.getY()+y,origin.getZ()+z);
                    BlockState actual=h.getLevel().getBlockState(pos);
                    boolean lightAddition=id==0&&blueprint.ritualCore!=null&&actual.is(net.minecraft.world.level.block.Blocks.LIGHT);
                    if(lightAddition) {
                        lights++;
                        h.assertTrue(actual.getValue(net.minecraft.world.level.block.LightBlock.LEVEL)<=11,"Mouth light too bright");
                    }
                    if(!actual.equals(job.palette[id])&&!lightAddition)throw new IllegalStateException("Full voxel mismatch "+pos+" expected="+job.palette[id]+" actual="+actual);
                    digest.update((byte)id);if(id!=0)nonAir++;verifyIndex++;
                }
                if(verifyIndex<blueprint.volume()){h.runAfterDelay(1,this::tick);return;}
                String actualHash=HexFormat.of().formatHex(digest.digest());h.assertTrue(actualHash.equals(blueprint.sha256)&&nonAir==blueprint.blockCount,"World full hash/count differs");
                if(blueprint.ritualCore!=null){
                    h.assertTrue(lights>=10&&lights<=42,"Unexpected sparse mouth light count: "+lights);
                    System.out.println("MOUTH_SPARSE_LIGHTS_VERIFIED="+lights);
                    int[] c=blueprint.ritualCore;BlockPos core=origin.offset(c[0],c[1],c[2]);var session=ZhenyuanRitualSavedData.get(h.getLevel()).at(h.getLevel(),core);
                    h.assertTrue(session!=null&&session.nodes.size()==5,"Five altar nodes were not bound");
                    h.assertTrue(h.getLevel().getBlockState(core.below()).isFaceSturdy(h.getLevel(),core.below(),Direction.UP),"Return floor not solid");
                    for(var node:blueprint.ritualNodes){BlockPos p=origin.offset(node.x(),node.y(),node.z());h.assertTrue(h.getLevel().getBlockEntity(p) instanceof ZhenyuanNodeBlockEntity,"Missing real dynamic-orb block entity");
                        boolean reachable=false;for(int dx=-3;dx<=3;dx++)for(int dz=-3;dz<=3;dz++)for(int dy=-2;dy<=1;dy++){
                            BlockPos feet=p.offset(dx,dy,dz);if(feet.distSqr(p)>16)continue;
                            if(h.getLevel().isEmptyBlock(feet)&&h.getLevel().isEmptyBlock(feet.above())&&h.getLevel().getBlockState(feet.below()).isFaceSturdy(h.getLevel(),feet.below(),Direction.UP))reachable=true;
                        }h.assertTrue(reachable,"Offering pedestal has no close standing space: "+node.slot());}
                    // Both sides of the open mouth have walkable platform columns (not blocked by new stairs).
                    for(int sign:new int[]{-1,1}){boolean open=false;for(int dx=6;dx<=12;dx++)for(int dz=-3;dz<=3;dz++){
                        BlockPos feet=core.offset(sign*dx,0,dz);if(h.getLevel().isEmptyBlock(feet)&&h.getLevel().isEmptyBlock(feet.above())&&h.getLevel().getBlockState(feet.below()).isFaceSturdy(h.getLevel(),feet.below(),Direction.UP))open=true;
                    }h.assertTrue(open,"Mouth left/right ring was blocked");}
                }
                if(which>0)report.append(',');report.append("{\"id\":\"").append(ids[which]).append("\",\"blocks\":").append(nonAir).append(",\"voxelsVerified\":").append(verifyIndex).append(",\"sha256\":\"").append(actualHash).append("\",\"elapsedMs\":").append(System.currentTimeMillis()-started).append("}");
                if(which+1<ids.length){start(which+1);return;}
                report.append("]}");Path output=Path.of(System.getProperty("dynasty.sculptureQaReport","sculpture-full-qa.json"));Files.createDirectories(output.toAbsolutePath().getParent());Files.writeString(output,report,StandardCharsets.UTF_8);h.succeed();
            }catch(Exception e){h.fail("Full sculpture QA: "+e);}
        }
    }
}
