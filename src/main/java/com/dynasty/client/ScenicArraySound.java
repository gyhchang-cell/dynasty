package com.dynasty.client;

import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.ScenicAncientArray;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import java.util.*;

/** Owns only this scene's quiet local chant; rain, range, expiry and world changes stop the loop. */
final class ScenicArraySound extends AbstractTickableSoundInstance {
    private record Key(long seed,long start){}
    private static final Map<Key,ScenicArraySound> PLAYING=new HashMap<>();
    private final ClientLevel level;
    private final Cod3VisualPacket packet;
    private final long created;
    private ScenicArraySound(ClientLevel level,Cod3VisualPacket packet){
        super(SoundEvent.createVariableRangeEvent(new ResourceLocation("dynasty","scenic_ancient_array")),SoundSource.AMBIENT,RandomSource.create(packet.seed()));
        this.level=level;this.packet=packet;this.created=level.getGameTime();this.x=packet.origin().x;this.y=packet.origin().y+1;this.z=packet.origin().z;
        this.looping=true;this.delay=0;this.relative=false;this.attenuation=Attenuation.NONE;this.volume=volume(level,packet);
    }
    static void sync(ClientLevel level,List<Cod3VisualPacket> active){
        if(Minecraft.getInstance().options.getSoundSourceVolume(SoundSource.MASTER)<=0){clear();return;}
        var wanted=new HashSet<Key>();var manager=Minecraft.getInstance().getSoundManager();
        for(var p:active)if(p.sequence().equals("scenic_02")&&volume(level,p)>0){
            var key=new Key(p.seed(),p.start());wanted.add(key);var existing=PLAYING.get(key);
            if(existing!=null&&(existing.level!=level||existing.isStopped()||level.getGameTime()-existing.created>5&&!manager.isActive(existing))){manager.stop(existing);PLAYING.remove(key);}
            if(!PLAYING.containsKey(key)){var sound=new ScenicArraySound(level,p);PLAYING.put(key,sound);manager.play(sound);}
        }
        PLAYING.entrySet().removeIf(e->{if(wanted.contains(e.getKey()))return false;manager.stop(e.getValue());return true;});
    }
    static void clear(){var manager=Minecraft.getInstance().getSoundManager();PLAYING.values().forEach(manager::stop);PLAYING.clear();}
    private static float volume(ClientLevel level,Cod3VisualPacket p){
        var mc=Minecraft.getInstance();if(level==null||level!=mc.level||mc.player==null)return 0;
        return (float)ScenicAncientArray.soundVolume(level.getGameTime()-p.start(),p.duration(),mc.player.position().distanceTo(p.origin()),level.getDayTime(),level.getRainLevel(1));
    }
    @Override public boolean canStartSilent(){return true;}
    @Override public void tick(){volume=volume(level,packet);if(volume<=0)stop();}
}
