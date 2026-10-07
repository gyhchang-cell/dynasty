package com.dynasty.expansion;

import com.dynasty.Dynasty;
import com.dynasty.DynastyTrinketOnHit;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.network.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import java.util.function.Supplier;

/** Bounded visual-only message; nearby clients never receive camera or gameplay commands. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public record CombatFeedback(int type, double x, double y, double z, double sx, double sy, double sz) {
    public CombatFeedback(int type,double x,double y,double z){this(type,x,y,z,x,y,z);}
    public static void tether(LivingEntity from,net.minecraft.world.phys.Vec3 end) {
        if(!(from.level() instanceof ServerLevel level))return;
        var start=from.getEyePosition();
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(from.getX(),from.getY(),from.getZ(),32,level.dimension())),new CombatFeedback(14,end.x,end.y,end.z,start.x,start.y,start.z));
    }
    public static final int NORMAL=0, HEAVY=1, CRITICAL=2, BLOCK=3, PERFECT=4, ARMOR=5, STAGGER=6, KNOCKDOWN=7, LAUNCH=8, IMMUNE=9, THUNDER=10, WATER=11, STAR=12, HEAL=13;
    public static void send(LivingEntity target, int type) {
        if (!(target.level() instanceof ServerLevel level)) return;
        // Per-entity throttling also bounds AoE/proc feedback in crowded encounters.
        long now=level.getGameTime();
        var data=target.getPersistentData();
        if (data.contains("cod4FeedbackTick") && now-data.getLong("cod4FeedbackTick")<3) return;
        data.putLong("cod4FeedbackTick", now);
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(() -> new PacketDistributor.TargetPoint(target.getX(), target.getY(), target.getZ(), 32, level.dimension())), new CombatFeedback(type,target.getX(),target.getY()+target.getBbHeight()*.55,target.getZ()));
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void hit(LivingDamageEvent e) {
        if(e.isCanceled() || e.getAmount()<=0 || e.getEntity().level().isClientSide || DynastyTrinketOnHit.isSyntheticDamage()) return;
        if (!(e.getSource().getEntity() instanceof LivingEntity attacker)) return;
        var key=net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(attacker.getMainHandItem().getItem());
        if (key==null || !key.getNamespace().equals("dynasty")) return;
        String id=key.getPath();
        int type=id.contains("hammer") || id.contains("axe") ? HEAVY : id.equals("seven_star_saber") ? STAR : id.contains("trident") ? WATER : id.contains("spear") ? LAUNCH : NORMAL;
        if (e.getEntity().hasEffect(ExpansionEffects.BREAK.get())) type=ARMOR;
        if (attacker.fallDistance>0 && !attacker.onGround()) type=CRITICAL;
        send(e.getEntity(),type);
    }
    public static void encode(CombatFeedback p,FriendlyByteBuf b) { b.writeVarInt(p.type);b.writeDouble(p.x);b.writeDouble(p.y);b.writeDouble(p.z);b.writeDouble(p.sx);b.writeDouble(p.sy);b.writeDouble(p.sz); }
    public static CombatFeedback decode(FriendlyByteBuf b) {
        var p=new CombatFeedback(b.readVarInt(),b.readDouble(),b.readDouble(),b.readDouble(),b.readDouble(),b.readDouble(),b.readDouble());
        if (p.type<0 || p.type>14 || !Double.isFinite(p.x+p.y+p.z+p.sx+p.sy+p.sz) || new net.minecraft.world.phys.Vec3(p.x-p.sx,p.y-p.sy,p.z-p.sz).lengthSqr()>1024) throw new IllegalArgumentException("Invalid combat feedback");
        return p;
    }
    public static void handle(CombatFeedback p,Supplier<NetworkEvent.Context> supplier) {
        var ctx=supplier.get();
        if(ctx.getDirection()==NetworkDirection.PLAY_TO_CLIENT) ctx.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->ExpansionClient.feedback(p)));
        ctx.setPacketHandled(true);
    }
}
