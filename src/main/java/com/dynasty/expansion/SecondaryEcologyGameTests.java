package com.dynasty.expansion;

import com.dynasty.structure.megabuild.*;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class SecondaryEcologyGameTests {
    private static final Set<UUID> CREATED=new HashSet<>();
    private static Long day;
    private static Boolean spawning;
    private static void ecology(GameTestHelper h){
        if(day==null){day=h.getLevel().getDayTime();spawning=h.getLevel().getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING);}
        h.getLevel().setDayTime(18000);h.getLevel().updateSkyBrightness();h.getLevel().getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,h.getLevel().getServer());
    }
    @AfterBatch(batch="cod4_secondary_ecology") public static void cleanup(ServerLevel l){
        for(var id:CREATED){var entity=l.getEntity(id);if(entity!=null)entity.discard();}CREATED.clear();
        if(day!=null){l.setDayTime(day);l.updateSkyBrightness();l.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(spawning,l.getServer());day=null;}
    }
    private static BlockPos surface(GameTestHelper h,String biome){
        ecology(h);var p=h.absolutePos(new BlockPos(6,2,6));p=new BlockPos(p.getX(),132,p.getZ());
        for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++){
            h.getLevel().setBlock(p.offset(x,-1,z),Blocks.STONE.defaultBlockState(),2);
            for(int y=0;y<=8;y++)h.getLevel().setBlock(p.offset(x,y,z),Blocks.AIR.defaultBlockState(),2);
        }
        biome(h,p,biome);return p;
    }
    private static void biome(GameTestHelper h,BlockPos pos,String biome){
        var a=pos.offset(-4,-3,-4);var b=pos.offset(4,8,4);
        h.getLevel().getServer().getCommands().performPrefixedCommand(h.getLevel().getServer().createCommandSourceStack().withLevel(h.getLevel()).withPermission(4).withSuppressedOutput(),
            "fillbiome "+a.getX()+" "+a.getY()+" "+a.getZ()+" "+b.getX()+" "+b.getY()+" "+b.getZ()+" minecraft:"+biome);
    }
    private static EntityType<SecondaryMob> type(String id){return SecondaryMobs.TYPES.get(id).get();}
    private static boolean rule(GameTestHelper h,BlockPos pos,String id){return SpawnPlacements.checkSpawnRules(type(id),h.getLevel(),MobSpawnType.NATURAL,pos,h.getLevel().random);}
    private static SecondaryMob probe(GameTestHelper h,BlockPos pos,String id){var mob=type(id).create(h.getLevel());mob.moveTo(Vec3.atBottomCenterOf(pos));return mob;}
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_ecology",setupTicks=20)
    public static void allThirtyEnterActualWeightedBiomeListsAndEggCommandsRemainAvailable(GameTestHelper h){
        ecology(h);var biomes=h.getLevel().registryAccess().registryOrThrow(Registries.BIOME);var at=h.absolutePos(new BlockPos(2,2,2));
        for(var spec:SecondaryMobs.SPECS){var type=type(spec.id());
            h.assertTrue(biomes.stream().anyMatch(b->b.getMobSettings().getMobs(type.getCategory()).unwrap().stream().anyMatch(e->e.type==type&&e.getWeight().asInt()==1&&e.minCount==1&&e.maxCount==1)),"Actual loaded native biome modifier provides bounded weighted spawn entry: "+spec.id());
            h.assertTrue(SpawnPlacements.checkSpawnRules(type,h.getLevel(),MobSpawnType.SPAWN_EGG,at,h.getLevel().random)&&SpawnPlacements.checkSpawnRules(type,h.getLevel(),MobSpawnType.COMMAND,at,h.getLevel().random),"Registered natural habitat cannot remove existing egg/command entrance: "+spec.id());
            h.assertTrue(!SpawnPlacements.checkSpawnRules(type,h.getLevel(),MobSpawnType.CHUNK_GENERATION,at,h.getLevel().random)&&SpawnPlacements.checkSpawnRules(type,h.getLevel(),MobSpawnType.SPAWNER,at,h.getLevel().random),"Incomplete chunk-generation placement declines before live-server queries while original spawner remains available: "+spec.id());
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_ecology",setupTicks=20)
    public static void snowWolfAndSwampJunglePythonUseNativeBiomeAndPhysicalPlacement(GameTestHelper h){
        var at=surface(h,"snowy_plains");h.assertTrue(rule(h,at,"gray_wolf"),"Registered native wolf predicate accepts actual snowy plains");
        for(String biome:new String[]{"swamp","jungle"}){biome(h,at,biome);var python=probe(h,at,"giant_python");h.assertTrue(rule(h,at,"giant_python")&&ForgeEventFactory.checkSpawnPosition(python,h.getLevel(),MobSpawnType.NATURAL),"Actual native biome and Forge obstruction path accept requested python habitat: "+biome);}
        h.getLevel().setBlock(at,Blocks.STONE.defaultBlockState(),3);h.assertTrue(!rule(h,at,"giant_python"),"Solid body collision rejects real natural spawn");
        h.getLevel().setBlock(at,Blocks.AIR.defaultBlockState(),3);h.getLevel().setBlock(at.below(),Blocks.AIR.defaultBlockState(),3);h.assertTrue(!rule(h,at,"giant_python"),"No standing floor is not a valid land spawn");
        var remote=new BlockPos(30000000,132,30000000);var tickets=new HashSet<>(h.getLevel().getForcedChunks());h.assertTrue(!SecondarySpawnHooks.eligible(h.getLevel(),remote,"giant_python")&&tickets.equals(h.getLevel().getForcedChunks()),"Unloaded query rejects without acquiring a forced chunk ticket");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_ecology",setupTicks=20)
    public static void waterRequiresConnectedPoolAndNativeLiquidObstructionAllowsOnlyAquaticActors(GameTestHelper h){
        var at=surface(h,"river");h.getLevel().setBlock(at,Blocks.WATER.defaultBlockState(),3);h.assertTrue(!rule(h,at,"river_imp"),"One-block puddle cannot open an aquatic spawn");
        for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=-2;y<=2;y++)h.getLevel().setBlock(at.offset(x,y,z),Blocks.WATER.defaultBlockState(),3);
        for(String id:new String[]{"river_imp","drowning_ghost","carp_spirit","snail_maiden","crab_soldier"}){
            var mob=probe(h,at,id);h.assertTrue(rule(h,at,id)&&mob.checkSpawnObstruction(h.getLevel())&&ForgeEventFactory.checkSpawnPosition(mob,h.getLevel(),MobSpawnType.NATURAL),"Real connected water passes both registered and native Forge liquid/obstruction checks: "+id);
        }
        var land=probe(h,at,"gray_wolf");h.assertTrue(!land.checkSpawnObstruction(h.getLevel())&&!rule(h,at,"gray_wolf"),"Aquatic exception does not make ordinary land actors spawn in water");
        h.getLevel().getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(false,h.getLevel().getServer());h.assertTrue(!rule(h,at,"river_imp"),"Native no-mob-spawning rule stops habitat/helper spawn");h.getLevel().getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,h.getLevel().getServer());
        var palace=h.getLevel().getServer().getLevel(com.dynasty.block.DynastyPortalBlock.DRAGON_PALACE);h.assertTrue(palace!=null,"Actual original Dragon Palace dimension exists");
        var seaPos=new BlockPos(8,120,8);palace.getChunk(0,0);
        var a=seaPos.offset(-3,-2,-3);var b=seaPos.offset(3,2,3);
        palace.getServer().getCommands().performPrefixedCommand(palace.getServer().createCommandSourceStack().withLevel(palace).withPermission(4).withSuppressedOutput(),"fillbiome "+a.getX()+" "+a.getY()+" "+a.getZ()+" "+b.getX()+" "+b.getY()+" "+b.getZ()+" minecraft:warm_ocean");
        for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=-2;y<=2;y++)palace.setBlock(seaPos.offset(x,y,z),Blocks.WATER.defaultBlockState(),3);
        var crab=type("crab_soldier").create(palace);crab.moveTo(Vec3.atBottomCenterOf(seaPos));
        h.assertTrue(SpawnPlacements.checkSpawnRules(type("crab_soldier"),palace,MobSpawnType.NATURAL,seaPos,palace.random)&&ForgeEventFactory.checkSpawnPosition(crab,palace,MobSpawnType.NATURAL),"Requested Dragon Palace crab habitat passes real native dimension, ocean, water and obstruction checks");
        h.assertTrue(!SpawnPlacements.checkSpawnRules(type("gray_wolf"),palace,MobSpawnType.NATURAL,seaPos,palace.random),"Specific palace crab entrance does not allow ordinary overworld species in other realms");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_ecology",setupTicks=20,timeoutTicks=300)
    public static void realDarkCaveAndDesertScorpionHaveDistinctHabitatChecks(GameTestHelper h){
        ecology(h);var at=h.absolutePos(new BlockPos(6,2,6));at=new BlockPos(at.getX(),20,at.getZ());final var pos=at;
        for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)for(int y=-1;y<=6;y++)h.getLevel().setBlock(pos.offset(x,y,z),(y==-1||y==6||Math.abs(x)==4||Math.abs(z)==4?Blocks.STONE:Blocks.AIR).defaultBlockState(),2);
        biome(h,pos,"dripstone_caves");h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getMaxLocalRawBrightness(pos)<=7&&!h.getLevel().canSeeSky(pos),"Wait for actual native cave darkness/lighting propagation"))
            .thenExecute(()->{
                for(String id:new String[]{"stone_sprite","bat_demon","corpse_beetle","stone_worm","clockwork_rat","venom_scorpion"})h.assertTrue(rule(h,pos,id),"Registered natural predicate supports actual cave ecology: "+id);
                h.getLevel().setBlock(pos,Blocks.LAVA.defaultBlockState(),3);h.assertTrue(!rule(h,pos,"stone_worm"),"Native cave actor rejects lava");
                h.getLevel().setBlock(pos,Blocks.AIR.defaultBlockState(),3);biome(h,pos,"desert");h.assertTrue(rule(h,pos,"venom_scorpion")&&!rule(h,pos,"stone_worm"),"Desert scorpion and deep-cave worm remain distinct actual biome predicates");h.succeed();
            });
    }
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_ecology",setupTicks=20)
    public static void nativeNightCoastDesertAndRainWindowsRetainActualPredicates(GameTestHelper h){
        var at=surface(h,"forest");h.assertTrue(rule(h,at,"red_fox"),"Original forest-night fox has an actual native natural entrance");
        try{h.getLevel().setDayTime(6000);h.getLevel().updateSkyBrightness();h.assertTrue(!rule(h,at,"red_fox"),"Native day cannot substitute for original night window");}
        finally{h.getLevel().setDayTime(18000);h.getLevel().updateSkyBrightness();}
        biome(h,at,"beach");h.assertTrue(rule(h,at,"jingwei_bird"),"Existing bird's requested real coast biome is now reachable");
        biome(h,at,"desert");h.assertTrue(rule(h,at,"gray_falcon"),"Existing falcon's real desert biome is now reachable");
        boolean raining=h.getLevel().isRaining(),thunder=h.getLevel().isThundering();float rainLevel=h.getLevel().getRainLevel(1),thunderLevel=h.getLevel().getThunderLevel(1);
        try{
            h.getLevel().setWeatherParameters(10000,0,false,false);h.getLevel().setRainLevel(0);h.getLevel().setThunderLevel(0);h.assertTrue(rule(h,at,"locust_swarm"),"Native dry weather opens original desert swarm");
            h.getLevel().setWeatherParameters(0,10000,true,false);h.getLevel().setRainLevel(1);h.assertTrue(!rule(h,at,"locust_swarm"),"Original global rainy-weather exclusion remains intact, including arid biomes");
        }finally{h.getLevel().setWeatherParameters(10000,raining?10000:0,raining,thunder);h.getLevel().setRainLevel(rainLevel);h.getLevel().setThunderLevel(thunderLevel);}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_secondary_ecology",setupTicks=20,timeoutTicks=200)
    public static void loadedRealCityStartOpensMechanicalSpawnAndThreeActualActorsReachLocalCap(GameTestHelper h){
        var at=surface(h,"plains");h.assertTrue(!rule(h,at,"wooden_magpie")&&!rule(h,at,"clockwork_rat"),"Ordinary surface plains are not an authored mechanism city");
        var structure=h.getLevel().registryAccess().registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("dynasty:tiangong_citadel"));var chunk=new ChunkPos(at);
        var nativeChunk=h.getLevel().getChunk(chunk.x,chunk.z);var old=nativeChunk.getStartForStructure(structure);
        var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(h.getLevel().registryAccess().lookupOrThrow(Registries.BIOME),h.getLevel().registryAccess().lookupOrThrow(Registries.STRUCTURE_SET),h.getLevel().registryAccess().lookupOrThrow(Registries.PLACED_FEATURE));
        settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(192,Blocks.STONE));settings.updateLayers();var generator=new net.minecraft.world.level.levelgen.FlatLevelSource(settings);
        var start=structure.generate(h.getLevel().registryAccess(),generator,generator.getBiomeSource(),h.getLevel().getChunkSource().randomState(),h.getLevel().getStructureManager(),h.getLevel().getSeed(),chunk,0,h.getLevel(),b->true);
        h.assertTrue(start.isValid()&&start.getPieces().size()==1,"Original registered city generator forms an actual valid native StructureStart");nativeChunk.setStartForStructure(structure,start);
        h.assertTrue(rule(h,at,"wooden_magpie")&&rule(h,at,"clockwork_rat"),"Existing loaded-only structure references activate original city actors");
        var mobs=new ArrayList<SecondaryMob>();for(int i=0;i<3;i++){var mob=SecondarySpawnHooks.spawn(h.getLevel(),at.offset(i-1,0,0),"wooden_magpie");h.assertTrue(mob!=null&&!mob.isNoAi(),"Actual bounded encounter helper uses original native AI actor");mobs.add(mob);CREATED.add(mob.getUUID());}
        h.startSequence().thenWaitUntil(()->h.assertTrue(mobs.stream().allMatch(m->h.getLevel().getEntity(m.getUUID())==m&&m.tickCount>0),"Wait for real spawned actors becoming entity-visible and ticking"))
            .thenExecute(()->{
                try{h.assertTrue(!rule(h,at,"wooden_magpie")&&SecondarySpawnHooks.spawn(h.getLevel(),at,"wooden_magpie")==null,"Three actual living local actors close native type cap; no silent unadded mob returned");}
                finally{mobs.forEach(Entity::discard);nativeChunk.setStartForStructure(structure,old==null?StructureStart.INVALID_START:old);}h.succeed();
            });
    }
}
