package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.boss.EnderDragonPart;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Dragon-only presentation. Multipart contact belongs to the real hit part, not parent bounds. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class DragonDecal {
    public static final String CUE="equipment_dragon_slayer_decal",STAMP="cod3_dragon_decal_at";
    public static final int DURATION=12;
    private static final class TargetTags {
        static final TagKey<EntityType<?>> TARGETS=TagKey.create(Registries.ENTITY_TYPE,new ResourceLocation(Dynasty.MODID,"dragon_decal_targets"));
    }
    private record Contact(UUID player,UUID parent,String dimension,long tick,Vec3 offset,Vec3 normal,double scale,int partSlot) {}
    private static final List<Contact> CONTACTS=new ArrayList<>();
    public record Vertex(Vec3 position,double u,double v) {}
    public record Triangle(Vertex a,Vertex b,Vertex c,double alpha) {}
    public static boolean target(Entity entity){return entity!=null&&entity.getType().is(TargetTags.TARGETS);}
    private static boolean weapon(net.minecraft.world.item.ItemStack stack) {
        return !stack.isEmpty()&&new ResourceLocation(Dynasty.MODID,"dragon_slayer").equals(ForgeRegistries.ITEMS.getKey(stack.getItem()));
    }
    public static Vec3 surface(Entity entity,Vec3 normal) {
        return entity.position().add(0,entity.getBbHeight()*.55,0).add(normal.scale(entity.getBbWidth()*.5+.025));
    }
    private static Vec3 normal(ServerPlayer player,Entity victim) {
        return TangWind.horizontal(player.position().subtract(victim.position()),player.getLookAngle().scale(-1));
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void partAttack(AttackEntityEvent event) {
        if(event.isCanceled()||!(event.getEntity() instanceof ServerPlayer player)||!weapon(player.getMainHandItem())
                ||!(event.getTarget() instanceof EnderDragonPart part)||!target(part.parentMob)
                ||!(part.level() instanceof ServerLevel level))return;
        CONTACTS.removeIf(c->c.player().equals(player.getUUID()));
        int slot=0;var parts=part.parentMob.getSubEntities();for(int i=0;i<parts.length;i++)if(parts[i]==part){slot=i+1;break;}
        if(slot==0)return;
        if(CONTACTS.size()>=32)CONTACTS.remove(0);
        var normal=normal(player,part);
        CONTACTS.add(new Contact(player.getUUID(),part.parentMob.getUUID(),level.dimension().location().toString(),level.getGameTime(),
                surface(part,normal).subtract(part.parentMob.position()),normal,Math.max(.45,Math.min(1.4,part.getBbWidth()*.8)),slot));
    }
    /** Pure packet selection from final damage, used unchanged by the server observer. */
    public static Cod3VisualPacket cueFor(LivingDamageEvent event) {
        if(event.isCanceled()||event.getAmount()<=0||!Float.isFinite(event.getAmount())||!target(event.getEntity())
                ||!(event.getSource().getEntity() instanceof ServerPlayer player)||event.getSource().getDirectEntity()!=player
                ||!event.getSource().is(DamageTypes.PLAYER_ATTACK)||com.dynasty.DynastyTrinketOnHit.isSyntheticDamage()
                ||com.dynasty.QinglongDescent.isDragonDamage(event.getSource())||com.dynasty.DynastyBowRitual.isSolarDamage(event.getSource())
                ||com.dynasty.EdictSpells.isSpell(event.getSource())
                ||!(event.getEntity().level() instanceof ServerLevel level))return null;
        var victim=event.getEntity();var n=normal(player,victim);var offset=surface(victim,n).subtract(victim.position());
        double size=Math.max(.45,Math.min(1.4,victim.getBbWidth()*.8));int partSlot=0;
        if(victim instanceof EnderDragon) {
            Contact found=null;
            for(var c:CONTACTS)if(c.player().equals(player.getUUID())&&c.parent().equals(victim.getUUID())
                    &&c.tick()==level.getGameTime()&&c.dimension().equals(level.dimension().location().toString())){found=c;break;}
            if(found==null)return null;
            offset=found.offset();n=found.normal();size=found.scale();partSlot=found.partSlot();
        } else if(!weapon(EquipmentFeedback.sourceWeapon(event)))return null;
        var p=packet(level.dimension().location().toString(),victim.getId(),level.getGameTime(),size,offset,n,partSlot);
        return accepts(p)?p:null;
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void hit(LivingDamageEvent event) {
        var p=cueFor(event);
        if(event.getSource().getEntity() instanceof ServerPlayer player) {
            CONTACTS.removeIf(c->c.player().equals(player.getUUID())&&c.parent().equals(event.getEntity().getUUID()));
            if(p==null)return;
            var data=player.getPersistentData();if(data.contains(STAMP)&&data.getLong(STAMP)==p.start())return;
            data.putLong(STAMP,p.start());
            var level=(ServerLevel)event.getEntity().level();var world=event.getEntity().position().add(p.origin());
            DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(world.x,world.y,world.z,32,level.dimension())),p);
        }
    }
    @SubscribeEvent public static void clear(TickEvent.ServerTickEvent e){if(e.phase==TickEvent.Phase.END)CONTACTS.clear();}
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){CONTACTS.clear();}
    /** Origin in this dedicated cue is victim-local; no existing cue or wire field changes. */
    public static Cod3VisualPacket packet(String dim,int actor,long start,double scale,Vec3 offset,Vec3 normal) {
        return packet(dim,actor,start,scale,offset,normal,0);
    }
    public static Cod3VisualPacket packet(String dim,int actor,long start,double scale,Vec3 offset,Vec3 normal,int partSlot) {
        return new Cod3VisualPacket(dim,17,actor,0,start,DURATION,scale,offset,normal,CUE,partSlot,0xffffff);
    }
    public static boolean accepts(Cod3VisualPacket p) {
        return p!=null&&p.valid()&&CUE.equals(p.sequence())&&p.template()==17&&p.entityId()>=0&&p.tick()<=8
                &&p.tint()==0xffffff&&p.duration()==DURATION&&p.scale()>=.45&&p.scale()<=1.4
                &&p.origin().lengthSqr()<=32*32&&p.direction().lengthSqr()>.9&&p.direction().lengthSqr()<1.1&&Math.abs(p.direction().y)<1e-6;
    }
    /** Actual current part pose, including turns; packet snapshot remains a server contact receipt. */
    public static Vec3 anchor(Cod3VisualPacket p,Entity actor,double partial) {
        if(!accepts(p)||actor==null||actor.isRemoved()||!Double.isFinite(partial)||partial<0||partial>1)return null;
        Entity contact=actor;
        if(p.tick()>0){if(!(actor instanceof EnderDragon dragon)||p.tick()>dragon.getSubEntities().length)return null;contact=dragon.getSubEntities()[p.tick()-1];}
        var feet=new Vec3(net.minecraft.util.Mth.lerp(partial,contact.xOld,contact.getX()),net.minecraft.util.Mth.lerp(partial,contact.yOld,contact.getY()),net.minecraft.util.Mth.lerp(partial,contact.zOld,contact.getZ()));
        return p.tick()==0?feet.add(p.origin()):feet.add(0,contact.getBbHeight()*.55,0).add(p.direction().scale(contact.getBbWidth()*.5+.025));
    }
    public static List<Triangle> geometry(Cod3VisualPacket p,double age,Vec3 feet) {
        if(!accepts(p)||!Double.isFinite(age)||age<0||age>=DURATION||feet==null||!Double.isFinite(feet.lengthSqr()))return List.of();
        var c=feet.add(p.origin());var r=new Vec3(p.direction().z,0,-p.direction().x).scale(p.scale()*.5);var u=new Vec3(0,p.scale()*.5,0);
        var a=new Vertex(c.subtract(r).add(u),0,0);var b=new Vertex(c.add(r).add(u),1,0);
        var d=new Vertex(c.subtract(r).subtract(u),0,1);var e=new Vertex(c.add(r).subtract(u),1,1);
        double alpha=(1-age/DURATION)*.85;
        return List.of(new Triangle(a,d,e,alpha),new Triangle(a,e,b,alpha));
    }
    private DragonDecal() {}
}
