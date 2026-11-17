package com.dynasty.cod3;

import com.dynasty.*;
import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_qi_qa") @PrefixGameTestTemplate(false)
public final class BowDrawGameTests {
    private static ServerPlayer player(GameTestHelper h) {
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"bow-draw-qa"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new net.minecraft.core.BlockPos(4,2,4))));
        p.setNoGravity(true);h.getLevel().addNewPlayer(p);return p;
    }
    private static void close(GameTestHelper h,ServerPlayer p) {
        for(var e:h.getLevel().getEntitiesOfClass(AbstractArrow.class,p.getBoundingBox().inflate(20)))if(e.getOwner()==p)e.discard();
        h.getLevel().removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);
    }
    private static void tick(ServerPlayer p,int ticks) {for(int i=0;i<ticks;i++)p.doTick();}
    @GameTest(template="bow_ritual_test",batch="bow_draw")
    public static void fullHintMatchesActualNativeCriticalReleaseAndPaysOriginalAmmoOnce(GameTestHelper h) {
        String[] names={"lie_gong","chang_gong","dragon_bow","zhuxing_bow","fengling_bow"};
        for(String name:names) {
            var p=player(h);
            try {
                var stack=new ItemStack(ExpansionContent.item(name));h.assertTrue(stack.getItem() instanceof BowItem,"Original registered bow exists: "+name);
                p.setItemInHand(InteractionHand.MAIN_HAND,stack);p.getInventory().setItem(10,new ItemStack(Items.ARROW,8));
                stack.use(h.getLevel(),p,InteractionHand.MAIN_HAND);
                var start=BowDrawProgress.read(p);h.assertTrue(start!=null&&!start.full(),"Real use starts below full: "+name);
                int required=name.equals("lie_gong")||name.equals("chang_gong")?16:20;
                tick(p,required-1);var almost=BowDrawProgress.read(p);
                h.assertTrue(almost!=null&&!almost.full()&&almost.ticks()==required-1,"One native tick early cannot claim full: "+name);
                tick(p,1);var full=BowDrawProgress.read(p);
                h.assertTrue(full!=null&&full.full()&&full.fraction()==1,"Exact native threshold shows full: "+name);
                p.releaseUsingItem();
                var arrows=h.getLevel().getEntitiesOfClass(AbstractArrow.class,p.getBoundingBox().inflate(8),a->a.getOwner()==p);
                h.assertTrue(arrows.size()==1&&arrows.get(0).isCritArrow(),"Full hint matches one actual fully drawn original arrow: "+name);
                h.assertTrue(p.getInventory().getItem(10).getCount()==7&&stack.getDamageValue()==1,"Original native release pays one arrow and one durability: "+name);
                h.assertTrue(BowDrawProgress.read(p)==null,"Release clears hint without a delayed timer: "+name);
            } finally {close(h,p);}
        } h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="bow_cancel")
    public static void offhandDrawAndCanceledUseNeverLeaveOrTransferReadyState(GameTestHelper h) {
        var p=player(h);var other=player(h);
        try {
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));
            var bow=new ItemStack(DynastyWeapons.CHANG_GONG.get());p.setItemInHand(InteractionHand.OFF_HAND,bow);
            p.getInventory().setItem(10,new ItemStack(Items.ARROW,8));bow.use(h.getLevel(),p,InteractionHand.OFF_HAND);tick(p,16);
            h.assertTrue(BowDrawProgress.read(p)!=null&&BowDrawProgress.read(p).full(),"Actual offhand draw uses its own original threshold");
            h.assertTrue(BowDrawProgress.read(other)==null,"Other player's state is independent");
            p.stopUsingItem();h.assertTrue(BowDrawProgress.read(p)==null,"Cancel immediately clears readiness");
            h.assertTrue(p.getInventory().getItem(10).getCount()==8&&bow.getDamageValue()==0,"Canceled drawing cannot spend ammo/durability");
            bow.use(h.getLevel(),p,InteractionHand.OFF_HAND);h.assertTrue(!BowDrawProgress.read(p).full(),"A new draw cannot inherit previous readiness");
            p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(Items.STICK));
            h.assertTrue(BowDrawProgress.read(p)==null,"Swapped active stack cannot advertise old bow readiness");
            h.succeed();
        } finally {close(h,p);close(h,other);}
    }
    @GameTest(template="bow_ritual_test",batch="bow_reject")
    public static void missingAmmoCrossbowForeignBowAndSpellAnimationCannotMasqueradeAsDynastyDraw(GameTestHelper h) {
        var p=player(h);
        try {
            var bow=new ItemStack(DynastyWeapons.CHANG_GONG.get());p.setItemInHand(InteractionHand.MAIN_HAND,bow);
            bow.use(h.getLevel(),p,InteractionHand.MAIN_HAND);h.assertTrue(BowDrawProgress.read(p)==null,"Rejected no-ammo input does not show charge");
            for(Item item:new Item[]{Items.BOW,Items.CROSSBOW,DynastyWeapons.CHILING_BRUSH.get()}) {
                p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(item));p.startUsingItem(InteractionHand.MAIN_HAND);tick(p,20);
                h.assertTrue(BowDrawProgress.read(p)==null,"Unrelated bow/crossbow/spell animation stays in original feedback: "+item);p.stopUsingItem();
            }h.succeed();
        } finally {close(h,p);}
    }
}
