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
    private static ScenicEvents load(CompoundTag n){var d=new ScenicEvents();for(var x:n.getList("Active",10))d.active.add((CompoundTag)x);for(var x:n.getList("Cooldown",10)){var c=(CompoundTag)x;d.cooldown.put(c.getLong("Region"),c.getLong("At"));}return d;}
    @Override public CompoundTag save(CompoundTag n){var list=new ListTag();active.forEach(list::add);n.put("Active",list);var c=new ListTag();cooldown.forEach((k,v)->{var x=new CompoundTag();x.putLong("Region",k);x.putLong("At",v);c.add(x);});n.put("Cooldown",c);return n;}
    public boolean start(ServerLevel l,int number,Vec3 anchor){
        if(active.size()>=8)return false;var def=ScenicEventDefinition.of(number);var n=new CompoundTag();n.putInt("Number",number);n.putLong("Start",l.getGameTime());n.putLong("Seed",l.random.nextLong());n.putDouble("X",anchor.x);n.putDouble("Y",anchor.y);n.putDouble("Z",anchor.z);n.putInt("Duration",def.duration());active.add(n);setDirty();return true;
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%100!=0)return;
        var l=p.serverLevel();var data=get(l);long now=l.getGameTime();if(data.active.removeIf(n->now-n.getLong("Start")>=n.getInt("Duration")))data.setDirty();
        if(data.cooldown.entrySet().removeIf(row->now-row.getValue()>48000))data.setDirty();
        long region=net.minecraft.world.level.ChunkPos.asLong(p.getBlockX()>>7,p.getBlockZ()>>7);
        if(now-data.cooldown.getOrDefault(region,-48000L)>48000&&l.random.nextInt(120)==0){
            var eligible=new ArrayList<Integer>();for(int i=1;i<=25;i++)if(ScenicEventDefinition.of(i).eligible(p))eligible.add(i);
            if(!eligible.isEmpty()){int number=eligible.get(l.random.nextInt(eligible.size()));Vec3 f=p.getLookAngle().multiply(1,0,1).normalize();Vec3 anchor=p.position().add(f.scale(96));
                if(data.start(l,number,anchor)){data.cooldown.put(region,now);data.setDirty();}
            }
        }
        for(var n:data.active){Vec3 anchor=new Vec3(n.getDouble("X"),n.getDouble("Y"),n.getDouble("Z"));if(p.distanceToSqr(anchor)>256*256)continue;
            var d=ScenicEventDefinition.of(n.getInt("Number"));var packet=new Cod3VisualPacket(l.dimension().location().toString(),d.template(),-1,n.getLong("Seed"),n.getLong("Start"),n.getInt("Duration"),4,anchor,new Vec3(0,0,1),String.format(java.util.Locale.ROOT,"scenic_%02d",d.number()),(int)(now-n.getLong("Start")));
            com.dynasty.network.DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),packet);
        }
    }
}
