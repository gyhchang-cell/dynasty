package com.dynasty.blueprint;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class PalanquinGameTests {
    private static TemplateMob chair(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1||y==8||x==0||x==15||z==0||z==15?Blocks.STONE:Blocks.AIR);
        var m=h.spawn(BlueprintEntities.YINYANG_ZHIJIAO_YOUHUN.get(),new BlockPos(7,2,7));m.setNoAi(true);return m;
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h){var c=h.spawn(EntityType.COW,new BlockPos(7,2,9));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);c.setHealth(200);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=105,batch="palanquin")
    public static void holdHasWarningFiniteDamageAndNoMountOrTeleport(GameTestHelper h){
        var mob=chair(h);var target=cow(h);var p=target.position();h.assertTrue(mob.startSkill(ArmySkills.PALANQUIN_HOLD,target),"24tick curtain tell starts");
        h.runAfterDelay(22,()->h.assertTrue(target.getHealth()==200&&!target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Tell harmless"));
        h.runAfterDelay(31,()->h.assertTrue(target.getHealth()<200&&mob.hookTargetId()==target.getId()&&target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)&&!target.isPassenger()&&target.position().equals(p),"Soft hold changes neither position nor riding state"));
        h.runAfterDelay(85,()->{h.assertTrue(mob.hookTargetId()<0&&!target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)&&target.getHealth()>=192,"Bounded two second hold expires");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="palanquin")
    public static void crouchEscapesAndReloadKeepsCooldownWithoutCaptive(GameTestHelper h){
        var mob=chair(h);var target=cow(h);mob.startSkill(ArmySkills.PALANQUIN_HOLD,target);
        h.runAfterDelay(30,()->target.setShiftKeyDown(true));
        h.runAfterDelay(42,()->{
            h.assertTrue(mob.hookTargetId()<0&&!target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Five crouch ticks break hold");
            var tag=new CompoundTag();mob.save(tag);mob.discard();var copy=BlueprintEntities.YINYANG_ZHIJIAO_YOUHUN.get().create(h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);
            h.assertTrue(copy.hookTargetId()<0&&!copy.startSkill(ArmySkills.PALANQUIN_HOLD,target),"Reload cannot resume captive or bypass cooldown");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="palanquin")
    public static void wallAndRescueDamageCancelHold(GameTestHelper h){
        var mob=chair(h);var target=cow(h);mob.startSkill(ArmySkills.PALANQUIN_HOLD,target);
        h.runAfterDelay(30,()->{h.assertTrue(mob.hookTargetId()==target.getId(),"Contact occurs");mob.hurt(mob.damageSources().mobAttack(target),8);});
        h.runAfterDelay(40,()->{h.assertTrue(mob.hookTargetId()<0&&!target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Damage rescues victim and leaves no debuff");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="palanquin_world")
    public static void actualSurfaceLandingAndMidnightMarkerPreventArbitrarySpawn(GameTestHelper h){
        var level=h.getLevel();var origin=new BlockPos(7168,40,7168);var piece=new com.dynasty.structure.TombAccessPiece(origin,70);var box=piece.getBoundingBox();
        for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){
            var chunk=level.getChunk(x,z);piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(4),new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,box.minY(),z*16,x*16+15,box.maxY(),z*16+15),chunk.getPos(),origin);
        }
        var p=piece.palanquinPosition();h.assertTrue(com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,p,BlueprintEntities.YINYANG_ZHIJIAO_YOUHUN.get().getDimensions().makeBoundingBox(p.getX()+.5,p.getY(),p.getZ()+.5)),"Real generated landing is wide and supported");
        var before=level.getDayTime();try{
            level.setDayTime(6000);h.assertTrue(!BlueprintSpawns.spawnPalanquin(level,"day-chair",p,p.offset(8,0,0)),"No daylight event");
            level.setDayTime(18000);String key="chair-"+java.util.UUID.randomUUID();h.assertTrue(BlueprintSpawns.spawnPalanquin(level,key,p,p.offset(8,0,0)),"Midnight spawns one main body");h.assertTrue(!BlueprintSpawns.spawnPalanquin(level,key,p,p.offset(8,0,0)),"Repeated entrants cannot add bearers or more chairs");
        }finally{level.setDayTime(before);}h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="palanquin")
    public static void fourBearersAndCurtainAreOneParsedRig(GameTestHelper h)throws Exception{
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var in=PalanquinGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/yinyang_zhijiao_youhun.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();var clips=gson.fromJson(json.get("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var n:java.util.List.of("idle","walk","run","attack","hold","hurt","death"))h.assertTrue(clips.getAnimation("animation.yinyang_zhijiao_youhun."+n).boneAnimations().length>0,"Parses "+n);
            for(int i=0;i<4;i++)h.assertTrue(json.getAsJsonObject("animations").getAsJsonObject("animation.yinyang_zhijiao_youhun.walk").getAsJsonObject("bones").has("bearer_"+i),"Independent bearer phase "+i);
        }h.succeed();
    }
}
