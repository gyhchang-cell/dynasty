package com.dynasty.cod3;

import io.netty.buffer.Unpooled;
import net.minecraft.gametest.framework.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_aurora_qa")
@PrefixGameTestTemplate(false)
public final class AuroraServerQa {
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void ancientArrayKeepsFixedStationsAcrossSavedClocks(GameTestHelper h) {
        var l=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();
        var block=l.getBlockState(BlockPos.containing(at));int before=0;for(var ignored:l.getAllEntities())before++;
        h.assertTrue(data.start(l,2,at),"array starts");int after=0;for(var ignored:l.getAllEntities())after++;
        h.assertTrue(before==after&&block.equals(l.getBlockState(BlockPos.containing(at))),"no ritual blocks, rewards or entities");
        var p=data.packets(l,at).get(0);var d=ScenicEventDefinition.of(2);h.assertTrue(p.duration()==1200&&d.from()==17000&&d.until()==19000&&d.weather()==ScenicEventDefinition.Weather.CLEAR,"actual midnight definition");
        var restored=ScenicEvents.load(data.save(new CompoundTag()));h.assertTrue(restored.packets(l,at).equals(data.packets(l,at)),"array save/reload");
        h.runAtTickTime(20,()->{var late=restored.packets(l,at).get(0);h.assertTrue(late.start()==p.start()&&late.seed()==p.seed()&&late.tick()>=20,"array late observer no rotation/restart");h.succeed();});
    }
    @GameTest(template="bow_ritual_test")
    public static void ancientArrayRequiresMidnightAndSuitableGround(GameTestHelper h) {
        h.assertTrue(ScenicAncientArray.visibility(18000,0)==1&&ScenicAncientArray.visibility(18000,1)==0&&ScenicAncientArray.visibility(6000,0)==0,"night/rain predicates");
        h.assertTrue(ScenicAncientArray.mesh(2,600,1200,24,false,1,(x,z)->Double.NaN).isEmpty(),"invalid ground skipped");
        h.assertTrue(ScenicAncientArray.mesh(2,600,1200,24,false,1,(x,z)->0).size()<=Cod3Catalog.find("scenic","scenic_02").get("budget").getAsInt(),"150 budget");h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void silverfallPersistsWithoutFluidWritesOrEntities(GameTestHelper h) {
        var l=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();
        var block=l.getBlockState(BlockPos.containing(at));int before=0;for(var ignored:l.getAllEntities())before++;
        h.assertTrue(data.start(l,8,at),"silverfall starts");int after=0;for(var ignored:l.getAllEntities())after++;
        h.assertTrue(before==after&&block.equals(l.getBlockState(BlockPos.containing(at))),"no water blocks or entities");
        var p=data.packets(l,at).get(0);var d=ScenicEventDefinition.of(8);
        h.assertTrue(p.duration()==1200&&p.sequence().equals("scenic_08")&&d.weather()==ScenicEventDefinition.Weather.CLEAR&&d.from()==0&&d.until()==23999,"clear all-day 60 second contract");
        var buf=new FriendlyByteBuf(Unpooled.buffer());try{Cod3VisualPacket.encode(p,buf);h.assertTrue(Cod3VisualPacket.decode(buf).equals(p),"water packet codec");}finally{buf.release();}
        var restored=ScenicEvents.load(data.save(new CompoundTag()));h.assertTrue(restored.packets(l,at).equals(data.packets(l,at)),"save/reload water clock");
        h.runAtTickTime(20,()->{var late=restored.packets(l,at).get(0);h.assertTrue(late.start()==p.start()&&late.seed()==p.seed()&&late.tick()>=20,"late water observer same time");h.assertTrue(restored.packets(l,at.add(257,0,0)).isEmpty(),"water regional boundary");h.succeed();});
    }
    @GameTest(template="bow_ritual_test")
    public static void silverfallUsesActualBorderAndBoundedWaterGeometry(GameTestHelper h) {
        var l=h.getLevel();var border=l.getWorldBorder();double size=border.getSize(),cx=border.getCenterX(),cz=border.getCenterZ();
        var at=h.absolutePos(new BlockPos(3,2,3));
        var player=new net.minecraft.server.level.ServerPlayer(l.getServer(),l,new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"silverfall-qa"));
        long day=l.getDayTime();boolean rain=l.isRaining();
        try{
            l.setDayTime(6000);l.setWeatherParameters(6000,6000,false,false);border.setCenter(at.getX(),at.getZ());border.setSize(1024);
            player.setPos(at.getX()+300,at.getY(),at.getZ());h.assertTrue(ScenicEventDefinition.of(8).eligible(player),"real border predicate accepts 212 blocks");
            player.setPos(at.getX(),at.getY(),at.getZ());h.assertTrue(!ScenicEventDefinition.of(8).eligible(player),"world interior rejected");
        }finally{border.setCenter(cx,cz);border.setSize(size);l.setDayTime(day);l.setWeatherParameters(6000,6000,rain,false);}
        h.assertTrue(ScenicSilverfall.mesh(8,600,1200,24,false,1).size()<=Cod3Catalog.find("scenic","scenic_08").get("budget").getAsInt(),"300 total geometry budget");
        h.assertTrue(ScenicSilverfall.mesh(8,600,1200,24,false,ScenicSilverfall.visibility(1)).isEmpty(),"rain stops celestial water");h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void firefliesKeepRainForestClockAndNeverModifyTerrain(GameTestHelper h) {
        var l=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();
        var block=l.getBlockState(BlockPos.containing(at));int before=0;for(var ignored:l.getAllEntities())before++;
        h.assertTrue(data.start(l,7,at),"firefly event starts");int after=0;for(var ignored:l.getAllEntities())after++;
        h.assertTrue(before==after&&block.equals(l.getBlockState(BlockPos.containing(at))),"no insect entities or soil changes");
        var p=data.packets(l,at).get(0);var d=ScenicEventDefinition.of(7);
        h.assertTrue(p.duration()==1800&&p.sequence().equals("scenic_07")&&d.from()==13000&&d.weather()==ScenicEventDefinition.Weather.RAIN,"existing rainy-night 90 second definition");
        var restored=ScenicEvents.load(data.save(new CompoundTag()));h.assertTrue(restored.packets(l,at).equals(data.packets(l,at)),"persist firefly anchor/clock/seed");
        h.runAtTickTime(20,()->{var late=restored.packets(l,at).get(0);h.assertTrue(late.start()==p.start()&&late.seed()==p.seed()&&late.tick()>=20,"late observer resumes same insect paths");h.succeed();});
    }
    @GameTest(template="bow_ritual_test")
    public static void firefliesRequireFullMoonRainAndRespectCatalogBudget(GameTestHelper h) {
        h.assertTrue(ScenicFireflies.visibility(18000,1,0)==1&&ScenicFireflies.visibility(18000,0,0)==0&&ScenicFireflies.visibility(18000,1,1)==0&&ScenicFireflies.visibility(6000,1,0)==0,"night/rain/full moon predicate");
        h.assertTrue(ScenicFireflies.mesh(7,600,1800,24,false,1,(x,z)->Double.NaN).isEmpty(),"invalid habitat suppressed");
        h.assertTrue(ScenicFireflies.mesh(7,600,1800,24,false,1,(x,z)->0).size()<=Cod3Catalog.find("scenic","scenic_07").get("budget").getAsInt(),"600 budget");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void goldenLeavesShareWorldClockWithoutTerrainWrites(GameTestHelper h) {
        var l=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();
        var block=l.getBlockState(BlockPos.containing(at));int count=0;for(var ignored:l.getAllEntities())count++;
        h.assertTrue(data.start(l,19,at),"leaf display starts");int after=0;for(var ignored:l.getAllEntities())after++;
        h.assertTrue(count==after&&l.getBlockState(BlockPos.containing(at)).equals(block),"no entity or terrain change");
        var p=data.packets(l,at).get(0);var d=ScenicEventDefinition.of(19);
        h.assertTrue(p.duration()==1200&&p.sequence().equals("scenic_19")&&d.from()==11000&&d.until()==13000&&d.weather()==ScenicEventDefinition.Weather.CLEAR,"existing dusk/60 second catalogue");
        var restored=ScenicEvents.load(data.save(new CompoundTag()));h.assertTrue(restored.packets(l,at).equals(data.packets(l,at)),"leaf save/reload");
        h.runAtTickTime(20,()->{var late=restored.packets(l,at).get(0);h.assertTrue(late.seed()==p.seed()&&late.start()==p.start()&&late.tick()>=20,"late observer leaf clock");h.succeed();});
    }
    @GameTest(template="bow_ritual_test")
    public static void goldenLeavesNeedCanopyAndClearDusk(GameTestHelper h) {
        h.assertTrue(ScenicGoldenLeaves.mesh(19,600,1200,24,false,1,(x,z)->new ScenicGoldenLeaves.Column(0,0)).isEmpty(),"no tree no foliage");
        h.assertTrue(ScenicGoldenLeaves.mesh(19,600,1200,24,false,ScenicGoldenLeaves.visibility(12000,1),(x,z)->new ScenicGoldenLeaves.Column(0,12)).isEmpty(),"rain hides foliage");
        h.assertTrue(ScenicGoldenLeaves.mesh(19,600,1200,24,false,1,(x,z)->new ScenicGoldenLeaves.Column(0,12)).size()<=Cod3Catalog.find("scenic","scenic_19").get("budget").getAsInt(),"bounded leaf mesh");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void sunHaloRetainsRegionClockAndThirtySecondLifetime(GameTestHelper h) {
        var l=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();
        int before=0;for(var ignored:l.getAllEntities())before++;
        h.assertTrue(data.start(l,21,at),"solar display starts");
        int after=0;for(var ignored:l.getAllEntities())after++;h.assertTrue(before==after,"no visual entities");
        var p=data.packets(l,at).get(0);var def=ScenicEventDefinition.of(21);var row=Cod3Catalog.find("scenic","scenic_21");
        h.assertTrue(p.sequence().equals("scenic_21")&&p.duration()==600&&p.entityId()==-1,"actual 30 second packet");
        h.assertTrue(def.from()==5500&&def.until()==6500&&def.weather()==ScenicEventDefinition.Weather.CLEAR&&def.dimension().equals("minecraft:overworld"),"noon clear overworld trigger");
        h.assertTrue(row.get("budget").getAsInt()==80&&ScenicSunHalo.mesh(21,300,600,24,false,1).size()<=80,"catalogue budget");
        var buf=new FriendlyByteBuf(Unpooled.buffer());try{Cod3VisualPacket.encode(p,buf);h.assertTrue(Cod3VisualPacket.decode(buf).equals(p),"solar packet codec");}finally{buf.release();}
        var restored=ScenicEvents.load(data.save(new CompoundTag()));h.assertTrue(restored.packets(l,at).equals(data.packets(l,at)),"solar save/reload identity");
        h.runAtTickTime(20,()->{
            var late=restored.packets(l,at.add(64,0,0)).get(0);h.assertTrue(late.seed()==p.seed()&&late.start()==p.start()&&late.tick()>=20,"late observer resumes same clouds");
            h.assertTrue(restored.packets(l,at.add(257,0,0)).isEmpty(),"region boundary");
            var expired=data.save(new CompoundTag());expired.getList("Active",10).getCompound(0).putLong("Start",l.getGameTime()-600);
            h.assertTrue(ScenicEvents.load(expired).packets(l,at).isEmpty(),"expired solar save removed");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test")
    public static void solarAndNightDisplaysHaveComplementaryVisibility(GameTestHelper h) {
        for(int day:new int[]{5500,6000,7100})h.assertTrue(ScenicSunHalo.skyVisibility(day,0)==1&&ScenicAurora.skyVisibility(day,0)==0,"noon versus night separation");
        h.assertTrue(ScenicSunHalo.skyVisibility(18000,0)==0&&ScenicAurora.skyVisibility(18000,0)==1,"night versus noon separation");
        h.assertTrue(ScenicSunHalo.mesh(21,300,600,24,false,ScenicSunHalo.skyVisibility(6000,1)).isEmpty(),"rain suppression");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void meteorsRetainIdentityAndNeverBecomeProjectiles(GameTestHelper h) {
        var l=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();
        int before=0;for(var ignored:l.getAllEntities())before++;
        h.assertTrue(data.start(l,20,at),"meteor scene starts");
        int after=0;for(var ignored:l.getAllEntities())after++;h.assertTrue(before==after,"no projectile or loot entity");
        var p=data.packets(l,at).get(0);var def=ScenicEventDefinition.of(20);
        h.assertTrue(p.sequence().equals("scenic_20")&&p.duration()==900&&p.entityId()==-1&&def.weather()==ScenicEventDefinition.Weather.CLEAR,"actual 45 second non-combat catalog");
        var restored=ScenicEvents.load(data.save(new CompoundTag()));h.assertTrue(restored.packets(l,at).equals(data.packets(l,at)),"meteor save/reload identity");
        h.runAtTickTime(20,()->{
            var late=restored.packets(l,at.add(64,0,0)).get(0);h.assertTrue(late.start()==p.start()&&late.seed()==p.seed()&&late.tick()>=20,"late observer resumes the original shower");
            h.assertTrue(restored.packets(l,at.add(257,0,0)).isEmpty(),"outside observer boundary");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test")
    public static void meteorFlightsAndAuroraShareNightWeatherButNotGeometry(GameTestHelper h) {
        h.assertTrue(ScenicMeteors.mesh(20,400,900,24,false,ScenicAurora.skyVisibility(18000,1)).isEmpty(),"rain suppression");
        h.assertTrue(ScenicMeteors.mesh(20,400,900,24,false,ScenicAurora.skyVisibility(6000,0)).isEmpty(),"day suppression");
        var stars=ScenicMeteors.mesh(20,400,900,24,false,1);h.assertTrue(!stars.isEmpty()&&stars.size()<=180,"bounded actual flight geometry");
        h.assertTrue(!stars.equals(ScenicMeteors.mesh(20,405,900,24,false,1)),"stars travel during their individual flights");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void auroraPersistsAndLateViewersUseTheSameWorldClock(GameTestHelper h) {
        var level=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();
        int before=0;for(var entity:level.getAllEntities())before++;
        h.assertTrue(data.start(level,15,at),"aurora start");int after=0;for(var entity:level.getAllEntities())after++;
        h.assertTrue(before==after,"no server visual entities");
        var p=data.packets(level,at).get(0);
        h.assertTrue(p.valid()&&p.sequence().equals("scenic_15")&&p.duration()==1800&&p.entityId()==-1,"production packet contract");
        var buf=new FriendlyByteBuf(Unpooled.buffer());try{Cod3VisualPacket.encode(p,buf);h.assertTrue(Cod3VisualPacket.decode(buf).equals(p),"packet codec");}finally{buf.release();}
        var restored=ScenicEvents.load(data.save(new CompoundTag()));
        h.assertTrue(restored.packets(level,at).equals(data.packets(level,at)),"save/restart identity");
        h.runAtTickTime(20,()->{
            var late=restored.packets(level,at.add(64,0,0)).get(0);
            h.assertTrue(late.seed()==p.seed()&&late.start()==p.start()&&late.origin().equals(at)&&late.tick()>=20,"late viewer does not restart or move the curtain");
            h.assertTrue(restored.packets(level,at.add(256.1,0,0)).isEmpty(),"outside region receives no packets");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test")
    public static void auroraCatalogAndNightWeatherRemainConsistent(GameTestHelper h) {
        var def=ScenicEventDefinition.of(15);var row=Cod3Catalog.find("scenic","scenic_15");
        h.assertTrue(def.dimension().equals("minecraft:overworld")&&def.weather()==ScenicEventDefinition.Weather.CLEAR&&def.from()==13000,"actual server prerequisites");
        h.assertTrue(def.duration()==1800&&row.get("sound").getAsString().equals("无声")&&row.get("budget").getAsInt()==300,"90 seconds, silent, bounded catalog");
        h.assertTrue(ScenicAurora.skyVisibility(18000,0)==1&&ScenicAurora.skyVisibility(6000,0)==0&&ScenicAurora.skyVisibility(18000,1)==0,"visible only on a clear night");
        h.assertTrue(ScenicAurora.mesh(15,600,1800,24,false,1).size()<=300,"mesh bounded without particle entities");h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void auroraExpiredOrFutureSavesCannotResurrectTheScene(GameTestHelper h) {
        var level=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var data=new ScenicEvents();data.start(level,15,at);
        var tag=data.save(new CompoundTag());var entry=tag.getList("Active",10).getCompound(0);entry.putLong("Start",level.getGameTime()-1800);
        h.assertTrue(ScenicEvents.load(tag).packets(level,at).isEmpty(),"expired save");entry.putLong("Start",level.getGameTime()+1);
        h.assertTrue(ScenicEvents.load(tag).packets(level,at).isEmpty(),"future save");h.succeed();
    }
}
