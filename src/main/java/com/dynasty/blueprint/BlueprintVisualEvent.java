package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.SkillDefinition;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.PacketDistributor;
import java.util.UUID;
import java.util.function.Supplier;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraft.server.level.ServerPlayer;

/** One bounded S2C event per action. No player input, camera transform, or client-supplied damage. */
@Mod.EventBusSubscriber(modid="dynasty")
public record BlueprintVisualEvent(ResourceLocation dimension, int entityId, UUID entityUuid, int targetId,
        long started, long seed, String key, int windup, int duration, Vec3 origin, Vec3 direction,
        double range, double angle, boolean cancelled) {
    public static void start(LivingEntity mob, SkillDefinition skill, Vec3 origin, Vec3 direction, int targetId) {
        if (!(mob.level() instanceof ServerLevel level)) return;
        send(mob, new BlueprintVisualEvent(level.dimension().location(), mob.getId(), mob.getUUID(), targetId,
                level.getGameTime(), seed(mob, level.getGameTime()), skill.key(), skill.windupTicks(), skill.totalTicks(),
                origin, direction, skill.maxRange(), skill.angleDegrees(), false));
    }
    private static long seed(LivingEntity mob, long start) {
        return mob.getUUID().getMostSignificantBits() ^ mob.getUUID().getLeastSignificantBits() ^ start;
    }
    private static BlueprintVisualEvent deathEvent(TemplateMob mob) {
        return new BlueprintVisualEvent(mob.level().dimension().location(),mob.getId(),mob.getUUID(),-1,
            mob.skillStartTime(),seed(mob,mob.skillStartTime()),"death_"+mob.blueprintId(),0,mob.deathDuration(),
            mob.position(),mob.getLookAngle(),1.5,360,false);
    }
    public static void death(TemplateMob mob) {
        if(mob.level() instanceof ServerLevel) send(mob,deathEvent(mob));
    }
    private static BlueprintVisualEvent birdDeath(com.dynasty.blueprint.elite.GhostCarriageBird bird) {
        return new BlueprintVisualEvent(bird.level().dimension().location(),bird.getId(),bird.getUUID(),-1,
            bird.skillStart(),seed(bird,bird.skillStart()),"death_guiche_jiushouniao",0,100,bird.position(),bird.getLookAngle(),2.5,360,false);
    }
    public static void death(com.dynasty.blueprint.elite.GhostCarriageBird bird) {
        if(bird.level() instanceof ServerLevel)send(bird,birdDeath(bird));
    }
    private static BlueprintVisualEvent spiderDeath(com.dynasty.blueprint.elite.SpiderWoman spider){return new BlueprintVisualEvent(spider.level().dimension().location(),spider.getId(),spider.getUUID(),-1,spider.skillStart(),seed(spider,spider.skillStart()),"death_gudu_tianzhunv",0,80,spider.position(),spider.getLookAngle(),2,360,false);}
    public static void death(com.dynasty.blueprint.elite.SpiderWoman spider){if(spider.level() instanceof ServerLevel)send(spider,spiderDeath(spider));}
    private static BlueprintVisualEvent alchemistDeath(com.dynasty.blueprint.elite.Alchemist caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_yinyang_liandan_fangshi",0,80,caster.position(),caster.getLookAngle(),2,360,false);}
    public static void death(com.dynasty.blueprint.elite.Alchemist caster){if(caster.level() instanceof ServerLevel)send(caster,alchemistDeath(caster));}
    private static BlueprintVisualEvent tideDeath(com.dynasty.blueprint.elite.TideYasha caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_fubo_xunhai_yecha",0,80,caster.position(),caster.getLookAngle(),2,360,false);}
    public static void death(com.dynasty.blueprint.elite.TideYasha caster){if(caster.level() instanceof ServerLevel)send(caster,tideDeath(caster));}
    private static BlueprintVisualEvent corpseDeath(com.dynasty.blueprint.elite.RageCorpse caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_banshan_jiazhou_shikuang",0,80,caster.position(),caster.getLookAngle(),3,360,false);}
    public static void death(com.dynasty.blueprint.elite.RageCorpse caster){if(caster.level() instanceof ServerLevel)send(caster,corpseDeath(caster));}
    private static BlueprintVisualEvent gorillaDeath(com.dynasty.blueprint.elite.BronzeGorilla caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_hanshan_tongjia_juyuan",0,90,caster.position(),caster.getLookAngle(),3,360,false);}
    public static void death(com.dynasty.blueprint.elite.BronzeGorilla caster){if(caster.level() instanceof ServerLevel)send(caster,gorillaDeath(caster));}
    private static BlueprintVisualEvent inkDeath(com.dynasty.blueprint.elite.InkAssassin caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_mojia_jueying_cike",0,60,caster.position(),caster.getLookAngle(),2,360,false);}
    public static void death(com.dynasty.blueprint.elite.InkAssassin caster){if(caster.level() instanceof ServerLevel)send(caster,inkDeath(caster));}
    private static BlueprintVisualEvent judgeDeath(com.dynasty.blueprint.elite.LampJudge caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1, caster.skillStart(),seed(caster,caster.skillStart()),"death_qingdeng_panguan_guichai",0,84,caster.position(),caster.getLookAngle(),2,360,false);}
    public static void death(com.dynasty.blueprint.elite.LampJudge caster){if(caster.level() instanceof ServerLevel)send(caster,judgeDeath(caster));}
    private static BlueprintVisualEvent eagleDeath(com.dynasty.blueprint.elite.GoldenEagle caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_liefeng_jindiao_yushi",0,90,caster.position(),caster.getLookAngle(),3,360,false);}
    public static void death(com.dynasty.blueprint.elite.GoldenEagle caster){if(caster.level() instanceof ServerLevel)send(caster,eagleDeath(caster));}
    private static BlueprintVisualEvent suanniDeath(com.dynasty.blueprint.elite.BronzeSuanni caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_zhenmu_suanni_tonghou",0,90,caster.position(),caster.getLookAngle(),3,360,false);}
    public static void death(com.dynasty.blueprint.elite.BronzeSuanni caster){if(caster.level() instanceof ServerLevel)send(caster,suanniDeath(caster));}
    private static BlueprintVisualEvent cauldronDeath(com.dynasty.blueprint.boss.TaoyanCauldron caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_taoyan_zhishi",0,200,caster.position(),caster.getLookAngle(),6,360,false);}
    public static void death(com.dynasty.blueprint.boss.TaoyanCauldron caster){if(caster.level() instanceof ServerLevel)send(caster,cauldronDeath(caster));}
    private static BlueprintVisualEvent kiteDeath(com.dynasty.blueprint.boss.WoodKite caster){return new BlueprintVisualEvent(caster.level().dimension().location(),caster.getId(),caster.getUUID(),-1,caster.skillStart(),seed(caster,caster.skillStart()),"death_luban_yisha",0,220,caster.position(),caster.getLookAngle(),4.5,360,false);}
    public static void death(com.dynasty.blueprint.boss.WoodKite caster){if(caster.level() instanceof ServerLevel)send(caster,kiteDeath(caster));}
    @SubscribeEvent public static void tracking(PlayerEvent.StartTracking event) {
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.boss.WoodKite caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<220)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),kiteDeath(caster));return;}
            var action=caster.attack();var skill=action.current();long age=level.getGameTime()-action.started();if(skill!=null&&age>=0&&age<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),caster.lockedPoint(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }

        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.boss.BlindMarshal caster&&caster.level() instanceof ServerLevel level){
            var action=caster.attack();var skill=action.current();if(!caster.isDeadOrDying()&&skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),caster.lockedPoint(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }

        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.boss.TaoyanCauldron caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<200)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),cauldronDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),skill.id()==505?caster.landing():action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.BronzeSuanni caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<90)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),suanniDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),caster.position(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.GoldenEagle caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<90)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),eagleDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),caster.landing(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.LampJudge caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<84)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),judgeDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),caster.mark(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.InkAssassin caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<60)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),inkDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),caster.mark(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.BronzeGorilla caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<90)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),gorillaDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),skill.id()==423?caster.landing():action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.RageCorpse caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<80)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),corpseDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),skill.id()==402?caster.landing():action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.TideYasha caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<80)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),tideDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.Alchemist caster&&caster.level() instanceof ServerLevel level){
            if(caster.isDeadOrDying()){if(caster.skillStart()>=0&&level.getGameTime()-caster.skillStart()<80)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),alchemistDeath(caster));return;}
            var action=caster.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),caster.getId(),caster.getUUID(),target==null?-1:target.getId(),action.started(),seed(caster,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.SpiderWoman spider&&spider.level() instanceof ServerLevel level){
            if(spider.isDeadOrDying()){if(spider.skillStart()>=0&&level.getGameTime()-spider.skillStart()<80)DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),spiderDeath(spider));return;}
            var action=spider.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),spider.getId(),spider.getUUID(),target==null?-1:target.getId(),action.started(),seed(spider,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }

        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.HammerGuardian hammer
            &&hammer.level() instanceof ServerLevel level&&hammer.isAlive()){
            var action=hammer.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),hammer.getId(),hammer.getUUID(),target==null?-1:target.getId(),action.started(),seed(hammer,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.GhostCarriageBird bird
            &&bird.isDeadOrDying()&&bird.skillStart()>=0&&bird.level().getGameTime()-bird.skillStart()<100){
            DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),birdDeath(bird));return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.FoxMatron fox
            &&fox.level() instanceof ServerLevel level&&fox.isAlive()&&!fox.isDecoy()){
            var action=fox.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),fox.getId(),fox.getUUID(),target==null?-1:target.getId(),action.started(),seed(fox,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.Jinwu jinwu
            &&jinwu.level() instanceof ServerLevel level&&jinwu.isAlive()){
            var action=jinwu.attack();var skill=action.current();if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),jinwu.getId(),jinwu.getUUID(),target==null?-1:target.getId(),action.started(),seed(jinwu,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.Mechanist mechanist
                &&mechanist.level() instanceof ServerLevel level&&mechanist.isAlive()){
            var action=mechanist.attack();var skill=action.current();
            if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),mechanist.getId(),mechanist.getUUID(),target==null?-1:target.getId(),
                    action.started(),seed(mechanist,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player&&event.getTarget() instanceof com.dynasty.blueprint.elite.GhostCarriageBird bird
                &&bird.level() instanceof ServerLevel level&&bird.isAlive()){
            var action=bird.attack();var skill=action.current();
            if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),new BlueprintVisualEvent(level.dimension().location(),bird.getId(),bird.getUUID(),target==null?-1:target.getId(),
                    action.started(),seed(bird,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),bird.telegraphOrigin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false));
            }return;
        }
        if(event.getEntity() instanceof ServerPlayer player && event.getTarget() instanceof com.dynasty.blueprint.elite.HeadlessGeneral elite
                && elite.level() instanceof ServerLevel level && elite.isAlive()) {
            var action=elite.attack();var skill=action.current();
            if(skill!=null&&level.getGameTime()-action.started()<skill.totalTicks()){
                var target=action.target()==null?null:level.getEntity(action.target());
                var packet=new BlueprintVisualEvent(level.dimension().location(),elite.getId(),elite.getUUID(),target==null?-1:target.getId(),
                    action.started(),seed(elite,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),
                    skill.id()==com.dynasty.blueprint.elite.HeadlessGeneral.THROW.id()?elite.landing():action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false);
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet);
            }return;
        }
        if (!(event.getEntity() instanceof ServerPlayer player) || !(event.getTarget() instanceof TemplateMob mob)
                || !(mob.level() instanceof ServerLevel level)) return;
        if(mob.isDeadOrDying()) {
            if(mob.skillStartTime()>=0 && level.getGameTime()-mob.skillStartTime()<mob.deathDuration())
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),deathEvent(mob));
            return;
        }
        var action=mob.attack(); var skill=action.current();
        if(skill==null || level.getGameTime()-action.started()>=skill.totalTicks()) return;
        var target=action.target()==null?null:level.getEntity(action.target());
        var packet=new BlueprintVisualEvent(level.dimension().location(),mob.getId(),mob.getUUID(),target==null?-1:target.getId(),
            action.started(),seed(mob,action.started()),skill.key(),skill.windupTicks(),skill.totalTicks(),
            action.origin(),action.direction(),skill.maxRange(),skill.angleDegrees(),false);
        DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet);
    }
    public static void cancel(LivingEntity mob) {
        if (!(mob.level() instanceof ServerLevel level)) return;
        send(mob, new BlueprintVisualEvent(level.dimension().location(), mob.getId(), mob.getUUID(), -1,
                level.getGameTime(), 0, "cancel", 0, 1, mob.position(), mob.getLookAngle(), 0, 0, true));
    }
    private static void send(LivingEntity mob, BlueprintVisualEvent event) {
        DynastyNetwork.CHANNEL.send(PacketDistributor.TRACKING_ENTITY.with(() -> mob), event);
    }
    public static void encode(BlueprintVisualEvent p, FriendlyByteBuf b) {
        b.writeResourceLocation(p.dimension); b.writeVarInt(p.entityId); b.writeUUID(p.entityUuid); b.writeVarInt(p.targetId);
        b.writeLong(p.started); b.writeLong(p.seed); b.writeUtf(p.key,64); b.writeVarInt(p.windup); b.writeVarInt(p.duration);
        b.writeDouble(p.origin.x);b.writeDouble(p.origin.y);b.writeDouble(p.origin.z);
        b.writeDouble(p.direction.x);b.writeDouble(p.direction.y);b.writeDouble(p.direction.z);
        b.writeDouble(p.range);b.writeDouble(p.angle);b.writeBoolean(p.cancelled);
    }
    public static BlueprintVisualEvent decode(FriendlyByteBuf b) {
        var p = new BlueprintVisualEvent(b.readResourceLocation(),b.readVarInt(),b.readUUID(),b.readVarInt(),
                b.readLong(),b.readLong(),b.readUtf(64),b.readVarInt(),b.readVarInt(),
                new Vec3(b.readDouble(),b.readDouble(),b.readDouble()), new Vec3(b.readDouble(),b.readDouble(),b.readDouble()),
                b.readDouble(),b.readDouble(),b.readBoolean());
        if (p.duration<1 || p.duration>1200 || p.windup<0 || p.windup>p.duration || p.range<0 || p.range>64
                || p.angle<0 || p.angle>360 || !Double.isFinite(p.range+p.angle+p.origin.lengthSqr()+p.direction.lengthSqr()))
            throw new IllegalArgumentException("Invalid blueprint visual event");
        return p;
    }
    public static void handle(BlueprintVisualEvent p, Supplier<NetworkEvent.Context> supplier) {
        var ctx=supplier.get();
        if(ctx.getDirection()==NetworkDirection.PLAY_TO_CLIENT) ctx.enqueueWork(() ->
                DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.dynasty.blueprint.client.BlueprintVisuals.accept(p)));
        ctx.setPacketHandled(true);
    }
}
