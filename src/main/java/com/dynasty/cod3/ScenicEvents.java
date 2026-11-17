package com.dynasty.cod3;

import com.dynasty.*;
import net.minecraft.nbt.*;
import net.minecraft.server.level.*;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** Server sends seed/anchor/start only. Late observers resume; no terrain writes or AI entities. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class ScenicEvents extends SavedData {
    private final List<CompoundTag> active=new ArrayList<>();
    private final Map<Long,Long> cooldown=new HashMap<>();
    public static ScenicEvents get(ServerLevel l){return l.getDataStorage().computeIfAbsent(ScenicEvents::load,ScenicEvents::new,"dynasty_cod3_scenic");}
    static ScenicEvents load(CompoundTag n){
        var data=new ScenicEvents();
        for(var tag:n.getList("Active",10)){
            var entry=((CompoundTag)tag).copy();int number=entry.getInt("Number");
            if(number<1||number>25||number==13||data.active.size()>=8||!Double.isFinite(entry.getDouble("X"))||!Double.isFinite(entry.getDouble("Y"))||!Double.isFinite(entry.getDouble("Z")))continue;
            entry.putInt("Duration",ScenicEventDefinition.of(number).duration());data.active.add(entry);
        }
        for(var tag:n.getList("Cooldown",10)){var entry=(CompoundTag)tag;data.cooldown.put(entry.getLong("Region"),entry.getLong("At"));}
        data.wasRaining=n.getBoolean("WasRaining");data.rainEndedAt=n.contains("RainEndedAt")?n.getLong("RainEndedAt"):Long.MIN_VALUE;return data;
    }
    private boolean wasRaining;
    private long rainEndedAt=Long.MIN_VALUE;
    public boolean recentlyCleared(ServerLevel level){return rainEndedAt!=Long.MIN_VALUE&&!level.isRaining()&&level.getGameTime()>=rainEndedAt&&level.getGameTime()-rainEndedAt<=2400;}
    @SubscribeEvent public static void weather(TickEvent.LevelTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.level instanceof ServerLevel level)||level.getGameTime()%20!=0)return;
        var data=get(level);boolean rain=level.isRaining();
        if(data.wasRaining!=rain){if(data.wasRaining)data.rainEndedAt=level.getGameTime();data.wasRaining=rain;data.setDirty();}
    }
    @Override public CompoundTag save(CompoundTag n){var list=new ListTag();active.forEach(entry->list.add(entry.copy()));n.put("Active",list);var c=new ListTag();cooldown.forEach((k,v)->{var x=new CompoundTag();x.putLong("Region",k);x.putLong("At",v);c.add(x);});n.put("Cooldown",c);n.putBoolean("WasRaining",wasRaining);if(rainEndedAt!=Long.MIN_VALUE)n.putLong("RainEndedAt",rainEndedAt);return n;}
    public boolean start(ServerLevel l,int number,Vec3 anchor){
        if(number<1||number>25||number==13||anchor==null||!Double.isFinite(anchor.lengthSqr()))return false;
        expire(l.getGameTime());var def=ScenicEventDefinition.of(number);
        ScenicGhostShipRoute.Route ship=null;
        if(number==3){ship=ScenicGhostShipRoute.find(l,anchor);if(ship==null)return false;anchor=ship.origin();}
        ScenicStoneGodSite.Site stone=null;
        if(number==6){stone=ScenicStoneGodSite.find(l,anchor);if(stone==null)return false;anchor=stone.origin();}
        if(number==14){anchor=ScenicMirageSite.find(l,anchor);if(anchor==null)return false;}
        if(number==17){anchor=ScenicDragonPalaceSite.find(l,anchor);if(anchor==null)return false;}
        if(number==4){anchor=ScenicGhostArmySite.find(l,anchor);if(anchor==null)return false;}
        if(number==22){anchor=ScenicGhostMarketSite.find(l,anchor);if(anchor==null)return false;}
        if(number==18){anchor=ScenicGreatWallSite.find(l,anchor);if(anchor==null)return false;}
        final Vec3 fixedAnchor=anchor;
        if(active.size()>=8||!def.allowsDimension(l.dimension().location().toString())||active.stream().anyMatch(entry->entry.getInt("Number")==number&&new Vec3(entry.getDouble("X"),entry.getDouble("Y"),entry.getDouble("Z")).distanceToSqr(fixedAnchor)<128*128))return false;var n=new CompoundTag();n.putInt("Number",number);n.putLong("Start",l.getGameTime());n.putLong("Seed",l.random.nextLong());n.putDouble("X",anchor.x);n.putDouble("Y",anchor.y);n.putDouble("Z",anchor.z);n.putInt("Duration",def.duration());if(ship!=null){n.putDouble("DX",ship.direction().x);n.putDouble("DZ",ship.direction().z);}if(stone!=null){n.putDouble("DX",stone.direction().x);n.putDouble("DZ",stone.direction().z);}active.add(n);setDirty();return true;
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%100!=0)return;
        var l=p.serverLevel();var data=get(l);long now=l.getGameTime();if(data.active.removeIf(n->now-n.getLong("Start")>=n.getInt("Duration")))data.setDirty();
        if(data.cooldown.entrySet().removeIf(row->now-row.getValue()>48000))data.setDirty();
        long region=net.minecraft.world.level.ChunkPos.asLong(p.getBlockX()>>7,p.getBlockZ()>>7);
        if(now-data.cooldown.getOrDefault(region,-48000L)>48000&&l.random.nextInt(120)==0){
            var eligible=new ArrayList<Integer>();for(int i=1;i<=25;i++)if(ScenicEventDefinition.of(i).eligible(p))eligible.add(i);
            if(!eligible.isEmpty()){int number=eligible.get(l.random.nextInt(eligible.size()));Vec3 f=p.getLookAngle().multiply(1,0,1).normalize();Vec3 anchor=p.position().add(f.scale(96));
                if(number==17){var water=ScenicDragonPalaceSite.nearObserver(l,p.position(),p.getLookAngle());if(water!=null)anchor=water;}
                if(number==6){var site=ScenicStoneGodSite.nearObserver(l,p.position(),p.getLookAngle());if(site!=null)anchor=site.origin();}
                if(number==3){var route=ScenicGhostShipRoute.nearObserver(l,p.position(),p.getLookAngle());if(route!=null)anchor=route.origin();}
                if(data.start(l,number,anchor)){data.cooldown.put(region,now);data.setDirty();}
            }
        }
        sync(p);
    }
    private void expire(long now){if(active.removeIf(entry->now<entry.getLong("Start")||now-entry.getLong("Start")>=entry.getInt("Duration")))setDirty();}
    public List<Cod3VisualPacket> packets(ServerLevel level,Vec3 viewer){
        long now=level.getGameTime();expire(now);var result=new ArrayList<Cod3VisualPacket>();
        for(var entry:active){
            Vec3 anchor=new Vec3(entry.getDouble("X"),entry.getDouble("Y"),entry.getDouble("Z"));if(viewer.distanceToSqr(anchor)>256*256)continue;
            var def=ScenicEventDefinition.of(entry.getInt("Number"));if(!def.allowsDimension(level.dimension().location().toString()))continue;
            Vec3 direction=new Vec3(0,0,1);
            if(def.number()==3){direction=new Vec3(entry.getDouble("DX"),0,entry.getDouble("DZ"));if(ScenicGhostShipRoute.visibility(level)<=0||!ScenicGhostShipRoute.valid(level,new ScenicGhostShipRoute.Route(anchor,direction)))continue;}
            if(def.number()==6){direction=new Vec3(entry.getDouble("DX"),0,entry.getDouble("DZ"));if(ScenicStoneGodSite.visibility(level)<=0||!ScenicStoneGodSite.valid(level,new ScenicStoneGodSite.Site(anchor,direction)))continue;}
            if(def.number()==14&&(ScenicMirageSite.visibility(level)<=0||!ScenicMirageSite.valid(level,anchor)))continue;
            if(def.number()==17&&!ScenicDragonPalaceSite.valid(level,anchor))continue;
            if(def.number()==4&&(ScenicGhostArmySite.visibility(level)<=0||!ScenicGhostArmySite.valid(level,anchor)||!ScenicGreatWallSite.battlefieldNear(level,anchor)))continue;
            if(def.number()==22&&(ScenicGhostMarketSite.visibility(level)<=0||!ScenicGhostMarketSite.valid(level,anchor)))continue;
            if(def.number()==18&&(ScenicGreatWallSite.visibility(level)<=0||!ScenicGreatWallSite.valid(level,anchor)||!ScenicGreatWallSite.battlefieldNear(level,anchor)))continue;
            result.add(new Cod3VisualPacket(level.dimension().location().toString(),def.template(),-1,entry.getLong("Seed"),entry.getLong("Start"),entry.getInt("Duration"),def.number()==3||def.number()==6||def.number()==14||def.number()==17||def.number()==18||def.number()==4||def.number()==22?1:4,anchor,direction,String.format(Locale.ROOT,"scenic_%02d",def.number()),(int)(now-entry.getLong("Start"))));
        }
        return List.copyOf(result);
    }
    public static void sync(ServerPlayer player){for(var packet:get(player.serverLevel()).packets(player.serverLevel(),player.position()))com.dynasty.network.DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet);}
    @SubscribeEvent public static void login(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent event){if(event.getEntity() instanceof ServerPlayer player)sync(player);}
    @SubscribeEvent public static void dimension(net.minecraftforge.event.entity.player.PlayerEvent.PlayerChangedDimensionEvent event){if(event.getEntity() instanceof ServerPlayer player)sync(player);}
}
