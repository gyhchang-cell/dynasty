package com.dynasty.structure.megabuild;

import com.google.gson.JsonObject;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.zip.GZIPOutputStream;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class SculptureGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void buildingCommandsOnlyExposeTwoPlaceActions(GameTestHelper h) {
        var root=h.getLevel().getServer().getCommands().getDispatcher().getRoot().getChild("dynasty_build");
        h.assertTrue(root!=null&&root.getChildren().size()==1,"Old building command branches remain");
        var place=root.getChild("place");
        h.assertTrue(place!=null&&place.getChildren().size()==2,"Expected exactly two place actions");
        for(String id:new String[]{"longque_sanctuary","yunqi_manor"}) {
            var action=place.getChild(id);
            h.assertTrue(action!=null&&action.getCommand()!=null&&action.getChildren().isEmpty(),"Place must execute without confirm/status branches");
        }
        h.succeed();
    }
    private static String hash(byte[] bytes)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));}
    static SculptureBlueprint tiny(int width,int height,int length,String solid)throws Exception{
        byte[] raw=new byte[width*height*length];Arrays.fill(raw,(byte)1);
        ByteArrayOutputStream out=new ByteArrayOutputStream();try(var zip=new GZIPOutputStream(out)){zip.write(raw);}byte[] zip=out.toByteArray();
        JsonObject m=new JsonObject();m.addProperty("version",1);m.addProperty("id","yunqi_manor");m.addProperty("title","QA original tiny sample");m.addProperty("format","dense-u8-gzip");m.addProperty("order","x+z*width+y*width*length");
        m.addProperty("width",width);m.addProperty("height",height);m.addProperty("length",length);m.addProperty("voxelCount",raw.length);m.addProperty("blockCount",raw.length);
        m.addProperty("sha256",hash(raw));m.addProperty("gzipSha256",hash(zip));var p=new com.google.gson.JsonArray();p.add("minecraft:air");p.add(solid);m.add("palette",p);
        return SculptureBlueprint.decode("yunqi_manor",m.toString().getBytes(StandardCharsets.UTF_8),zip);
    }
    static SculptureSavedData data(GameTestHelper h,SculptureBlueprint b,BlockPos origin){
        var d=new SculptureSavedData();d.id=b.id;d.hash=b.manifestSha256;d.dimension=h.getLevel().dimension().location().toString();d.origin=origin;return d;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void negativeCoordinatesCursorIsUniqueAndResumable(GameTestHelper h){
        var c=new SculptureCursor(-17,75,-31,35,7,33);var seen=new HashSet<BlockPos>();int steps=0;
        while(!c.done()){
            h.assertTrue(c.valid(),"Invalid live cursor");BlockPos p=new BlockPos(c.x(),c.y(),c.z());h.assertTrue(seen.add(p),"Duplicate voxel");
            h.assertTrue((p.getX()>>4)==c.chunkX()&&(p.getZ()>>4)==c.chunkZ(),"Wrong chunk ownership");
            if(++steps==139){var resumed=new SculptureCursor(-17,75,-31,35,7,33);resumed.chunk=c.chunk;resumed.cell=c.cell;h.assertTrue(resumed.valid()&&resumed.x()==c.x()&&resumed.y()==c.y()&&resumed.z()==c.z(),"Resume moved cursor");}
            c.next();
        }
        h.assertTrue(seen.size()==35*7*33&&c.progress()==1,"Cursor missed cells");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void checkpointAndManifestProtectPaletteAndPendingAnchor(GameTestHelper h)throws Exception{
        var a=tiny(2,2,2,"minecraft:stone");var b=tiny(2,2,2,"minecraft:diamond_block");
        h.assertTrue(a.sha256.equals(b.sha256)&&!a.manifestSha256.equals(b.manifestSha256),"Palette-only changes must invalidate checkpoint hash");
        var d=data(h,a,new BlockPos(-12,89,441));d.hash="";d.placedVoxels.set(3);d.altarWrites.add(1);
        var loaded=SculptureSavedData.load(d.save(new CompoundTag()));
        h.assertTrue(loaded.hash.isEmpty()&&loaded.origin.equals(d.origin)&&loaded.paused&&loaded.placedVoxels.get(3)&&loaded.altarWrites.contains(1),"Pending anchor/receipts lost");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void preflightAndLateConflictsNeverOverwrite(GameTestHelper h)throws Exception{
        var b=tiny(2,2,2,"minecraft:stone");BlockPos p=h.absolutePos(new BlockPos(3,5,3));var d=data(h,b,p);
        h.getLevel().setBlockAndUpdate(p,Blocks.DIAMOND_BLOCK.defaultBlockState());var j=new SculptureWorkshop.Job(h.getLevel().getServer(),d,b);boolean failed=false;
        try{j.step();}catch(IllegalStateException expected){failed=true;}
        h.assertTrue(failed&&d.placed==0&&h.getLevel().getBlockState(p).is(Blocks.DIAMOND_BLOCK),"Preflight overwrote block");
        h.getLevel().setBlockAndUpdate(p,Blocks.AIR.defaultBlockState());d=data(h,b,p);j=new SculptureWorkshop.Job(h.getLevel().getServer(),d,b);
        for(int n=0;n<100&&d.phase.equals("checking");n++)j.step();h.assertTrue(d.phase.equals("placing"),"Preflight did not complete");
        h.getLevel().setBlockAndUpdate(p,Blocks.GOLD_BLOCK.defaultBlockState());failed=false;try{j.step();}catch(IllegalStateException expected){failed=true;}
        h.assertTrue(failed&&h.getLevel().getBlockState(p).is(Blocks.GOLD_BLOCK),"Late conflict was overwritten");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void receiptRecoveryRepairsMissingOwnCellsButNeverAdoptsUnknown(GameTestHelper h)throws Exception{
        var b=tiny(2,2,2,"minecraft:stone");BlockPos p=h.absolutePos(new BlockPos(5,5,5));var d=data(h,b,p);d.phase="recovering";d.placed=2;d.placedVoxels.set(0);d.placedVoxels.set(1);
        h.getLevel().setBlockAndUpdate(p,Blocks.STONE.defaultBlockState());h.getLevel().setBlockAndUpdate(p.east(),Blocks.AIR.defaultBlockState());var j=new SculptureWorkshop.Job(h.getLevel().getServer(),d,b);
        for(int n=0;n<100&&d.phase.equals("recovering");n++)j.step();
        h.assertTrue(d.placedVoxels.get(0)&&!d.placedVoxels.get(1)&&d.placed==1,"Lost world cell should become a safe pending repair");
        for(int n=0;n<100&&d.phase.equals("placing");n++)j.step();h.assertTrue(d.placed==8&&h.getLevel().getBlockState(p.east()).is(Blocks.STONE),"Resume duplicated/missed blocks");
        var unknown=data(h,b,p);unknown.phase="recovering";var conflict=new SculptureWorkshop.Job(h.getLevel().getServer(),unknown,b);boolean failed=false;try{conflict.step();}catch(IllegalStateException expected){failed=true;}
        h.assertTrue(failed&&unknown.placedVoxels.isEmpty(),"Unknown matching material was wrongly claimed");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void changedReceiptBlockIsPreservedOnRecovery(GameTestHelper h)throws Exception{
        var b=tiny(2,2,2,"minecraft:stone");BlockPos p=h.absolutePos(new BlockPos(3,6,3));var d=data(h,b,p);d.phase="recovering";d.placedVoxels.set(0);d.placed=1;
        h.getLevel().setBlockAndUpdate(p,Blocks.EMERALD_BLOCK.defaultBlockState());boolean failed=false;
        try{new SculptureWorkshop.Job(h.getLevel().getServer(),d,b).step();}catch(IllegalStateException expected){failed=true;}
        h.assertTrue(failed&&h.getLevel().getBlockState(p).is(Blocks.EMERALD_BLOCK)&&d.placedVoxels.get(0),"Modified original receipt block was overwritten");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void directPlacementCompletesAllPhasesAndPreservesConflicts(GameTestHelper h)throws Exception{
        var b=tiny(9,9,9,"minecraft:stone");var p=h.absolutePos(new BlockPos(1,25,1));
        var d=data(h,b,p);var job=new SculptureWorkshop.Job(h.getLevel().getServer(),d,b);
        job.placeDirect();
        h.assertTrue(job.done&&!d.present(),"Direct placement must finish, not stop at the 256-block budget");
        for(int x=0;x<9;x++)for(int y=0;y<9;y++)for(int z=0;z<9;z++)
            h.assertTrue(h.getLevel().getBlockState(p.offset(x,y,z)).is(Blocks.STONE),"Direct placement missed a voxel");
        var blocked=data(h,b,p);boolean rejected=false;
        try{new SculptureWorkshop.Job(h.getLevel().getServer(),blocked,b).placeDirect();}catch(IllegalStateException expected){rejected=true;}
        h.assertTrue(rejected&&blocked.placed==0,"Direct mode bypassed preflight");
        blocked.direct=true;
        h.assertTrue(!SculptureSavedData.load(blocked.save(new CompoundTag())).direct,"Blocking mode must require fresh consent after restart");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void writeBudgetAndBuildHeightAreBounded(GameTestHelper h)throws Exception{
        var b=tiny(8,8,8,"minecraft:stone");BlockPos p=h.absolutePos(new BlockPos(2,10,2));var d=data(h,b,p);d.phase="placing";var j=new SculptureWorkshop.Job(h.getLevel().getServer(),d,b);j.step();
        h.assertTrue(d.placed>0&&d.placed<=256,"Per-step write budget broken");
        var high=data(h,b,new BlockPos(p.getX(),h.getLevel().getMaxBuildHeight()-3,p.getZ()));boolean failed=false;try{new SculptureWorkshop.Job(h.getLevel().getServer(),high,b);}catch(IllegalArgumentException expected){failed=true;}
        h.assertTrue(failed&&high.placed==0,"Height overflow not rejected before edits");h.succeed();
    }
}
