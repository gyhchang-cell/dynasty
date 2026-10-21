package com.dynasty.client;

import com.dynasty.cod3.Cod3VisualPacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import java.util.*;

/** Only this scene's quiet directional cue; ownership allows immediate weather/world cleanup. */
final class ScenicStoneGodSound extends AbstractTickableSoundInstance {
    private record Key(long seed,long start){}
    private static final Map<Key,ScenicStoneGodSound> PLAYING=new HashMap<>();
    private final ClientLevel level;
    private final Cod3VisualPacket packet;
    private final long created;
    private ScenicStoneGodSound(ClientLevel level,Cod3VisualPacket packet){
        super(SoundEvents.AMETHYST_BLOCK_CHIME,SoundSource.AMBIENT,RandomSource.create(packet.seed()));
        this.level=level;this.packet=packet;this.created=level.getGameTime();this.looping=false;this.relative=false;
        this.attenuation=Attenuation.NONE;this.pitch=.55f;update();
    }
    static void sync(ClientLevel level,List<Cod3VisualPacket> active){
        var mc=Minecraft.getInstance();
        if(mc.options.getSoundSourceVolume(SoundSource.MASTER)<=0){clear();return;}
        var manager=mc.getSoundManager();
        PLAYING.entrySet().removeIf(e->{var s=e.getValue();
            if(s.level==level&&active.contains(s.packet)&&!s.isStopped()&&s.gain()>0&&(level.getGameTime()-s.created<=5||manager.isActive(s)))return false;
            manager.stop(s);return true;
        });
        
        for(var p:active)if(p.sequence().equals("scenic_06")&&Math.floorMod(level.getGameTime()-p.start(),160)==80){
            var key=new Key(p.seed(),p.start());
            if(!PLAYING.containsKey(key)){
                var sound=new ScenicStoneGodSound(level,p);
                if(sound.volume>0){PLAYING.put(key,sound);manager.play(sound);}
            }
        }
    }
    static void clear(){var manager=Minecraft.getInstance().getSoundManager();PLAYING.values().forEach(manager::stop);PLAYING.clear();}
    private float gain(){
        var mc=Minecraft.getInstance();if(mc.level!=level||mc.player==null)return 0;
        if(!ScenicStoneGodGround.valid(level,packet))return 0;
        return (float)com.dynasty.cod3.ScenicStoneGodSite.soundVolume(level.getGameTime()-packet.start(),packet.duration(),packet.origin().distanceTo(mc.player.position()),com.dynasty.cod3.ScenicStoneGodSite.visibility(level));
    }
    private void update(){
        var at=packet.origin().add(0,18,0);x=at.x;y=at.y;z=at.z;volume=gain();
    }
    @Override public void tick(){update();if(volume<=0)stop();}
}
