package com.dynasty.cod3;

import com.dynasty.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.sounds.*;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class BossSequenceRunner {
    public static final String KEY="dynasty_cod3_intro";
    public static boolean active(Mob boss){return boss.getPersistentData().contains(KEY)&&!boss.getPersistentData().getCompound(KEY).getBoolean("Finished");}
    public static boolean start(Mob boss){
        return start(boss,0);
    }
    public static boolean start(Mob boss,int previewTicks){
        var id=ForgeRegistries.ENTITY_TYPES.getKey(boss.getType());var def=Cod3Catalog.sequence("intros",id.toString());
        if(def==null||boss.getPersistentData().contains(KEY))return false;
        CompoundTag state=new CompoundTag();state.putString("Id",def.id());state.putInt("Tick",0);state.putInt("Watchdog",0);state.putInt("Preview",Math.max(0,Math.min(20,previewTicks)));boss.getPersistentData().put(KEY,state);
        boss.setNoAi(true);boss.setInvulnerable(true);boss.setTarget(null);boss.setPersistenceRequired();bar(boss,false);
        if(previewTicks>0)boss.setInvisible(true);
        return true;
    }
    public static void finish(Mob boss){
        boss.getPersistentData().getCompound(KEY).putBoolean("Finished",true);boss.setInvulnerable(false);boss.setNoAi(false);boss.setInvisible(false);bar(boss,true);
    }
    private static void bar(Mob boss,boolean show){if(boss instanceof DynastyBossCombat.BarHolder holder)holder.dynastyBossBar().setVisible(show);}
    public static void tick(Mob boss){
        if(!active(boss)||!(boss.level() instanceof ServerLevel level))return;
        var state=boss.getPersistentData().getCompound(KEY);var def=Cod3Catalog.sequence("intros",ForgeRegistries.ENTITY_TYPES.getKey(boss.getType()).toString());
        if(def==null){finish(boss);return;}
        if(state.getInt("Preview")>0){state.putInt("Preview",state.getInt("Preview")-1);return;}
        boss.setInvisible(false);
        int tick=state.getInt("Tick"),watchdog=state.getInt("Watchdog")+1;state.putInt("Watchdog",watchdog);
        boss.setNoAi(true);boss.setInvulnerable(true);boss.setTarget(null);bar(boss,false);
        if(tick>=def.totalTicks()||watchdog>=def.totalTicks()+40){
            if(watchdog>=def.totalTicks()+40)Dynasty.LOGGER.warn("[Dynasty][BossIntro] forced-to-combat boss={} arena={}",boss.getType(),def.arenaTag());
            finish(boss);return;
        }
        for(var step:def.steps())if(step.startTick()==tick){
            try {if(step.type()==BossSequenceDefinition.Type.SPAWN_CLIENT_VFX)Cod3Vfx.sequence(boss,def.id(),tick,step);else play(boss,step);}catch(RuntimeException e){Dynasty.LOGGER.warn("cod3 sequence step skipped {}",def.id(),e);}
        }
        // One-second local altar warning before stage sounds. No movement or camera modification.
        if(tick==20)level.playSound(null,boss.blockPosition(),SoundEvents.BEACON_ACTIVATE,SoundSource.HOSTILE,.8f,.75f);
        state.putInt("Tick",tick+1);
        if(tick%100==0)for(var p:level.players())if(p.distanceToSqr(boss)<=32*32)Cod3Vfx.sync(p,boss,def.id(),tick,def.totalTicks());
    }
    public static void play(Mob boss,BossSequenceDefinition.Step step){
        if(!(boss.level() instanceof ServerLevel level))return;
        switch(step.type()){
            case SPAWN_CLIENT_VFX->Cod3Vfx.send(level,step.vfx(),boss.position(),boss.getLookAngle(),Math.min(120,step.duration()),step.radius()/3);
            case PLAY_SOUND->level.playSound(null,boss.blockPosition(),SoundEvents.BEACON_AMBIENT,SoundSource.HOSTILE,.6f,.8f);
            case SET_BOSS_VISIBILITY->boss.setInvisible(false);
            case SET_MODEL_VARIANT,PLAY_BOSS_ANIMATION->boss.getPersistentData().putString("dynasty_cod3_visual_stage",step.detail());
            case WAIT->{}
        }
    }
    @SubscribeEvent public static void living(LivingEvent.LivingTickEvent e){if(e.getEntity() instanceof Mob boss&&!boss.level().isClientSide&&boss.isAlive())tick(boss);}
    @SubscribeEvent public static void tracking(PlayerEvent.StartTracking e){
        if(e.getEntity() instanceof ServerPlayer p&&e.getTarget() instanceof Mob boss&&active(boss)){
            var s=boss.getPersistentData().getCompound(KEY);var def=Cod3Catalog.sequence("intros",ForgeRegistries.ENTITY_TYPES.getKey(boss.getType()).toString());
            if(def!=null)Cod3Vfx.sync(p,boss,def.id(),s.getInt("Tick"),def.totalTicks());
        }
    }
    private BossSequenceRunner(){}
}
