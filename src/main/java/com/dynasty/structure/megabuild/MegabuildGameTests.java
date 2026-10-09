package com.dynasty.structure.megabuild;
import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder(Dynasty.MODID) @PrefixGameTestTemplate(false)
public final class MegabuildGameTests {
    @GameTest(template="bow_ritual_test")
    public static void realStairFourRotations(GameTestHelper h){
        for(int rot=0;rot<4;rot++){
            var origin=new BlockPos(5008+rot*32,100,5008);
            var piece=new MegabuildPiece(MegabuildStructures.CITADEL_PIECE.get(),0,origin,seed->{
                var b=new Blueprint(16,8,16);b.set(8,1,8,Blueprint.Kind.STAIR_S);return b;
            },0,rot,16,8);
            var level=h.getLevel();level.getChunkAt(origin);
            piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,piece.getBoundingBox(),new net.minecraft.world.level.ChunkPos(origin),origin);
            int x=8,z=8;net.minecraft.core.Direction direction=net.minecraft.core.Direction.SOUTH;
            for(int i=0;i<rot;i++){int oldX=x;x=15-z;z=oldX;direction=direction.getClockWise();}
            h.assertTrue(level.getBlockState(origin.offset(x,1,z)).getValue(net.minecraft.world.level.block.StairBlock.FACING)==direction,"Real-world stair direction wrong at rotation "+rot);
        }h.succeed();
    }
    // Keep the121 native chunk writes and their real light/spawner assertions
    // out of the default batch's simultaneous combat/structure fixtures.
    @GameTest(template="bow_ritual_test",batch="megabuild_workshop_native",timeoutTicks=600)
    public static void fullWorkshopPlacement(GameTestHelper h){
        var level=h.getLevel();
        var origin=new BlockPos(2048,100,2048);
        var job=new MegabuildWorkshop.Job(level.getServer().createCommandSourceStack().withLevel(level),true,origin);
        boolean[] scheduled={false};
        h.onEachTick(()->{
            if(!job.done){job.step();return;}
            if(scheduled[0])return;
            scheduled[0]=true;
            h.assertTrue(job.failure==null,"Actual placement failed: "+job.failure);
            h.assertTrue(level.getBlockEntity(origin.offset(83,1,112)) instanceof net.minecraft.world.level.block.entity.ChestBlockEntity,"Vault chest missing");
            h.assertTrue(level.getBlockState(origin.offset(87,1,7)).getCollisionShape(level,origin.offset(87,1,7)).isEmpty(),"Entry obstructed");
            h.assertTrue(level.getBlockState(origin.offset(48,1,122)).is(net.minecraft.world.level.block.Blocks.ANVIL),"Workshop missing");
            h.assertTrue(level.getBlockState(origin.offset(18,1,33)).getValue(net.minecraft.world.level.block.StairBlock.FACING)==net.minecraft.core.Direction.SOUTH,"Stair mirrored in actual world");
            var cageChunks=new java.util.HashSet<net.minecraft.world.level.ChunkPos>();
            for(int[] c:new TiangongCitadel(0).cages){var cp=new net.minecraft.world.level.ChunkPos(origin.offset(c[0],c[1],c[2]));cageChunks.add(cp);level.setChunkForced(cp.x,cp.z,true);}
            h.runAfterDelay(80,()->{
                var city=new TiangongCitadel(0);
                for(int[] c:city.cages){
                    var p=origin.offset(c[0],c[1],c[2]);
                    h.assertTrue(level.getBlockEntity(p) instanceof net.minecraft.world.level.block.entity.SpawnerBlockEntity,"Cage missing");
                    for(int dx=-2;dx<=2;dx++)for(int dz=-2;dz<=2;dz++)for(int dy=-1;dy<=1;dy++){
                        var q=p.offset(dx,dy,dz);
                        h.assertTrue(level.getBrightness(net.minecraft.world.level.LightLayer.BLOCK,q)==0,"Spawn cell lit: "+q);
                        h.assertTrue(level.getBrightness(net.minecraft.world.level.LightLayer.SKY,q)==0,"Skylight leaks: "+q);
                    }
                }
                var player=new net.minecraftforge.common.util.FakePlayer(level,new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"cage-qa"));
                player.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);level.addNewPlayer(player);
                var difficulty=level.getDifficulty();
                try{
                    level.getServer().setDifficulty(net.minecraft.world.Difficulty.NORMAL,true);
                    for(int ci=0;ci<2;ci++){
                        int[] c=city.cages.get(ci);var p=origin.offset(c[0],c[1],c[2]);
                        player.moveTo(p.getX()+0.5,p.getY()+1,p.getZ()+0.5);
                        var sp=(net.minecraft.world.level.block.entity.SpawnerBlockEntity)level.getBlockEntity(p);
                        var k=city.blueprint().at(c[0],c[1],c[2]);
                        for(int attempt=0;attempt<40;attempt++){
                            var tag=CityEncounters.spawnerTag(k);tag.putShort("Delay",(short)0);
                            sp.load(tag);sp.getSpawner().serverTick(level,p);
                        }
                        var type=ci==0?net.minecraft.world.entity.EntityType.ZOMBIE:net.minecraft.world.entity.EntityType.SKELETON;
                        h.assertTrue(!level.getEntities(type,new net.minecraft.world.phys.AABB(p).inflate(5),e->true).isEmpty(),"Cage did not actually spawn "+type);
                    }
                }finally{
                    level.players().remove(player);
                    player.discard();for(var cp:cageChunks)level.setChunkForced(cp.x,cp.z,false);
                    level.getServer().setDifficulty(difficulty,true);
                }
                h.succeed();
            });
        });
    }
    static class Capture extends MegabuildPiece {
        final Map<BlockPos,String> writes=new HashMap<>();
        Capture(int rot){super(MegabuildStructures.CITADEL_PIECE.get(),0,new BlockPos(32,70,48),MegabuildStructures::citadel,42,rot,176,56);}
        Capture(CompoundTag tag){super(MegabuildStructures.CITADEL_PIECE.get(),tag,MegabuildStructures::citadel,176,56);}
        @Override protected void placeBlock(WorldGenLevel l,BlockState s,int x,int y,int z,BoundingBox b){
            BlockPos world=world(x,y,z);
            if(!b.isInside(world))throw new AssertionError("Work escaped requested chunk");
            writes.put(world,s.toString());
        }
        @Override protected boolean createChest(WorldGenLevel l,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation t){
            if(!b.isInside(world(x,y,z)))throw new AssertionError("Loot outside requested chunk");
            writes.put(world(x,y,z),t.toString());return true;
        }
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=200)
    public static void clippingRotationReloadAndLoot(GameTestHelper h){
        for(int rot=0;rot<4;rot++){
            var p=new Capture(rot);
            var box=new BoundingBox(112,70,144,127,125,159);
            p.postProcess(null,null,null,RandomSource.create(0),box,null,BlockPos.ZERO);
            h.assertTrue(p.writes.size()==16*16*56,"Must process one chunk, including clearing rooms");
            var restored=new Capture(p.createTag(null));
            restored.postProcess(null,null,null,RandomSource.create(0),box,null,BlockPos.ZERO);
            h.assertTrue(restored.writes.equals(p.writes),"NBT reload or rotation changed geometry");
            h.assertTrue(p.createTag(null).getInt("MegabuildLayout")==6,"Version missing");
        }
        for(String id:new String[]{"tiangong_citadel","tiangong_mining_estate"})
            h.assertTrue(h.getLevel().registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).containsKey(new ResourceLocation("dynasty",id)),"Missing structure "+id);
        for(String id:new String[]{"tiangong_common","tiangong_rich"})
            h.assertTrue(h.getLevel().getServer().getLootData().getLootTable(new ResourceLocation("dynasty","chests/"+id))!=net.minecraft.world.level.storage.loot.LootTable.EMPTY,"Missing loot");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void workshopTemplatesLoad(GameTestHelper h){
        for(String id:new String[]{"tiangong_citadel","tiangong_mining_estate"}){
            var template=h.getLevel().getStructureManager().get(new ResourceLocation("dynasty",id));
            h.assertTrue(template.isPresent(),"Workshop template missing");
            int size=id.equals("tiangong_citadel")?176:96;
            h.assertTrue(template.get().getSize().getX()==size && template.get().getSize().getZ()==size,"Template bounds mismatch");
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=200)
    public static void usableGeometry(GameTestHelper h){
        TiangongCitadel.main(new String[0]);MiningEstate.main(new String[0]);
        var b=new TiangongCitadel(0).blueprint();
        var old=PlayerCityEdits.originalWithEdits();
        int retained=0,structural=0,roomAir=0;
        var city=new TiangongCitadel(0);
        for(int x=0;x<176;x++)for(int y=0;y<56;y++)for(int z=0;z<176;z++){
            if(old.at(x,y,z)!=Blueprint.Kind.LIGHT)continue;
            var k=b.at(x,y,z);
            if(k==Blueprint.Kind.LIGHT){retained++;continue;}
            if(k!=Blueprint.Kind.AIR){structural++;continue;}
            boolean allowed=false;
            for(int[] c:city.cages)if(x>=c[0]-10&&x<=c[0]+4&&z>=c[2]-10&&z<=c[2]+4&&y>=c[1]-1&&y<=c[1]+4)allowed=true;
            if(x>=73&&x<=75&&z>=44&&z<=52&&y>=1&&y<=10)allowed=true;
            if(x==87&&(z==41||z==71)&&y>=1&&y<=5)allowed=true;
            if(x>=85&&x<=89&&z==101&&y>=2&&y<=3)allowed=true;
            h.assertTrue(allowed,"Player light removed outside bounded renovation: "+x+","+y+","+z);roomAir++;
        }
        System.out.println("Player lights: retained="+retained+", replaced by architecture="+structural+", local cleared="+roomAir);
        h.assertTrue(retained+structural+roomAir==807350,"Player edit accounting incomplete");
        h.assertTrue(b.countByCategory().get("建筑主体")>100000,"Do not inflate size with foundation fill");
        String export=System.getProperty("dynasty.megabuild.export");
        if(export!=null)try{
            MegabuildTemplateExport.write(b,java.nio.file.Path.of(export,"tiangong_citadel.nbt"));
            MegabuildTemplateExport.write(new MiningEstate(0).blueprint(),java.nio.file.Path.of(export,"tiangong_mining_estate.nbt"));
        }catch(Exception e){throw new RuntimeException(e);}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void mixedTreasure(GameTestHelper h){
        for(String id:new String[]{"tiangong_common","tiangong_rich"}){
            var table=h.getLevel().getServer().getLootData().getLootTable(new ResourceLocation("dynasty","chests/"+id));
            var params=new net.minecraft.world.level.storage.loot.LootParams.Builder(h.getLevel())
                .withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.ORIGIN,net.minecraft.world.phys.Vec3.ZERO)
                .create(net.minecraft.world.level.storage.loot.parameters.LootContextParamSets.CHEST);
            for(int i=0;i<32;i++){
                var loot=table.getRandomItems(params,i);
                h.assertTrue(loot.stream().anyMatch(s->net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(s.getItem()).getNamespace().equals("dynasty")),"No mod supplies");
                h.assertTrue(loot.stream().anyMatch(s->net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(s.getItem()).getNamespace().equals("minecraft")),"No vanilla supplies");
            }
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=300)
    public static void renovationPreservesLaterEdits(GameTestHelper h){
        var level=h.getLevel();var origin=new BlockPos(4096,100,4096);
        var job=new CityRenovation.Job(level.getServer().createCommandSourceStack().withLevel(level),origin);
        // Select three genuinely changed cells in one stripe, not hand-picked unchanged samples.
        var selected=new ArrayList<BlockPos>();
        for(int x=0;x<176&&selected.size()<3;x++){
            selected.clear();
            for(int y=0;y<56&&selected.size()<3;y++)for(int z=0;z<176&&selected.size()<3;z++)
                if(job.before.at(x,y,z)!=job.after.at(x,y,z)&&job.before.at(x,y,z)==Blueprint.Kind.LIGHT)
                    selected.add(new BlockPos(x,y,z));
        }
        h.assertTrue(selected.size()==3,"Missing patch samples");
        var apply=selected.get(0);var changed=selected.get(1);var chest=selected.get(2);
        level.setBlock(origin.offset(apply),MegabuildPiece.blockState(Blueprint.Kind.LIGHT),3);
        level.setBlock(origin.offset(changed),net.minecraft.world.level.block.Blocks.GOLD_BLOCK.defaultBlockState(),3);
        level.setBlock(origin.offset(chest),net.minecraft.world.level.block.Blocks.CHEST.defaultBlockState(),3);
        var originalChest=(net.minecraft.world.level.block.entity.ChestBlockEntity)level.getBlockEntity(origin.offset(chest));
        originalChest.setItem(0,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.DIAMOND,7));
        job.x=apply.getX();job.step();
        h.assertTrue(level.getBlockState(origin.offset(apply)).equals(MegabuildPiece.blockState(job.after.at(apply.getX(),apply.getY(),apply.getZ()))),"Expected delta not applied");
        h.assertTrue(level.getBlockState(origin.offset(changed)).is(net.minecraft.world.level.block.Blocks.GOLD_BLOCK),"Later player edit overwritten");
        h.assertTrue(level.getBlockEntity(origin.offset(chest))==originalChest&&originalChest.getItem(0).getCount()==7,"Original chest inventory destroyed");
        h.assertTrue(job.conflicts>0&&job.preservedChests>0,"Preservation not accounted");
        h.succeed();
    }
}
