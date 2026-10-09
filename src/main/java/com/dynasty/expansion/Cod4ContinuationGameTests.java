package com.dynasty.expansion;

import com.dynasty.*;
import com.dynasty.cod3.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_cod4")
@PrefixGameTestTemplate(false)
public final class Cod4ContinuationGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"cod4-next"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(net.minecraft.world.phys.Vec3.atCenterOf(h.absolutePos(new BlockPos(2,2,2))));return p;
    }
    private static void suit(ServerPlayer p,String id,int count){
        var slots=new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};String[] suffix={"helmet","chestplate","leggings","boots"};
        for(int i=0;i<4;i++)p.setItemSlot(slots[i],i<count?new ItemStack(ExpansionContent.item(id+"_"+suffix[i])):ItemStack.EMPTY);
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void swindlerRequiresInjuryPaymentAndOwnedEvidenceAfterReload(GameTestHelper h){
        var p=player(h);var stranger=player(h);var mob=SecondaryMobs.TYPES.get("swindler").get().create(h.getLevel());
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("copper_coin"),2));
        mob.mobInteract(p,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==2,"Injury dialogue never charges a coin");
        mob.mobInteract(p,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==1,"One explicit payment");
        ItemStack fake=p.getInventory().items.stream().filter(s->s.is(Items.DEAD_BUSH)&&s.hasTag()).findFirst().orElseThrow().copy();
        var save=mob.saveWithoutId(new CompoundTag());h.assertTrue(save.getInt("Cod4Deception")==2&&save.getInt("Cod4Flee")==0,"Payment does not stand in for exposure");
        var restored=SecondaryMobs.TYPES.get("swindler").get().create(h.getLevel());restored.load(save);
        stranger.setShiftKeyDown(true);stranger.setItemInHand(InteractionHand.MAIN_HAND,fake.copy());restored.mobInteract(stranger,InteractionHand.MAIN_HAND);
        var check=new CompoundTag();restored.addAdditionalSaveData(check);h.assertTrue(check.getInt("Cod4Deception")==2,"Other player cannot spend the victim's evidence");
        p.setShiftKeyDown(true);p.setItemInHand(InteractionHand.MAIN_HAND,fake);restored.mobInteract(p,InteractionHand.MAIN_HAND);
        restored.addAdditionalSaveData(check);h.assertTrue(check.getInt("Cod4Deception")==3&&check.getInt("Cod4Flee")==200,"Owned proof exposes the scam and starts real fleeing");
        h.assertTrue(ItemStack.of(check.getCompound("Cod4Stolen")).getCount()==1,"One stolen coin survives reload for death return");
        restored.dropCustomDeathLoot(restored.damageSources().generic(),0,true);restored.addAdditionalSaveData(check);
        h.assertTrue(ItemStack.of(check.getCompound("Cod4Stolen")).isEmpty(),"Returned theft is consumed once");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void locustDamageRequiresVolumeContactAndRespectsCooldown(GameTestHelper h){
        var mob=SecondaryMobs.TYPES.get("locust_swarm").get().create(h.getLevel());var z=new Zombie(h.getLevel());
        z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);z.setHealth(1000);mob.setPos(0,2,0);z.setPos(1.25,2,0);
        h.assertTrue(mob.distanceToSqr(z)<3&&!mob.contactAttack(z)&&z.getHealth()==1000,"Near-but-not-touching target takes no contact damage");
        z.setPos(.2,2,0);h.assertTrue(mob.contactAttack(z)&&z.getHealth()<1000,"Intersecting body volume damages the target");
        h.assertTrue(!mob.contactAttack(z),"No second contact hit within twenty ticks");
        h.assertTrue(SecondaryMobs.TYPES.size()==30,"Swarm remains one entity, with no insect AI registrations");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void stoneHardeningAddsArmorAndExpiresWithoutResistance(GameTestHelper h){
        var mob=SecondaryMobs.TYPES.get("stone_sprite").get().create(h.getLevel());var z=new Zombie(h.getLevel());z.setPos(mob.position().add(4,0,0));
        double base=mob.getAttributeValue(Attributes.ARMOR);mob.beginStoneRoll(z);
        h.assertTrue(mob.getAttributeValue(Attributes.ARMOR)==base+12&&!mob.hasEffect(MobEffects.DAMAGE_RESISTANCE),"Hardening is actual armor, independent of potion resistance");
        h.assertTrue(mob.getDeltaMovement().horizontalDistanceSqr()>.3&&mob.animation().equals("special"),"Rolling couples movement to the special animation");
        mob.beginStoneRoll(z);h.assertTrue(mob.getAttributeValue(Attributes.ARMOR)==base+12,"Same UUID never stacks");
        for(int i=0;i<40;i++)mob.aiStep();h.assertTrue(mob.getAttributeValue(Attributes.ARMOR)==base,"Temporary armor expires");
        mob.beginStoneRoll(z);var save=new CompoundTag();mob.addAdditionalSaveData(save);mob.readAdditionalSaveData(save);
        h.assertTrue(mob.getAttributeValue(Attributes.ARMOR)==base,"Reload cannot retain an orphaned modifier");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void crossbowTrailSnapshotSurvivesHandSwap(GameTestHelper h){
        var p=player(h);var arrow=new net.minecraft.world.entity.projectile.Arrow(h.getLevel(),p);
        var crossbow=new ItemStack(ExpansionContent.REPEATING.get());arrow.getPersistentData().put("cod4FiringWeapon",crossbow.save(new CompoundTag()));
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.YU_DI.get()));
        EquipmentFeedback.arrow(new net.minecraftforge.event.entity.EntityJoinLevelEvent(arrow,h.getLevel()));
        h.assertTrue(arrow.getPersistentData().getString("cod3_trail_weapon").equals("dynasty:repeating_crossbow"),"VFX#4 captures the actual firing crossbow");
        h.assertTrue(EquipmentFeedback.firingWeapon(arrow,p).is(ExpansionContent.REPEATING.get()),"Changing hands cannot steal a projectile's identity");
        h.assertTrue(arrow.getPersistentData().getInt("cod3_trail_tint")==EquipmentFeedback.tint("repeating_crossbow"),"Snapshot owns color as well as weapon identity");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void guideMarkerExpiresAndNeverGivesPermanentMap(GameTestHelper h){
        var p=player(h);var other=player(h);ExpansionSupplies.mark(p,p.blockPosition().offset(15,0,0));
        var data=p.getPersistentData().getCompound("cod4Guide");h.assertTrue(data.getLong("Until")==p.level().getGameTime()+1200,"Sixty second game-time lifetime");
        h.assertTrue(!other.getPersistentData().contains("cod4Guide")&&p.getInventory().countItem(Items.FILLED_MAP)==0,"Personal marker creates no permanent map");
        data.putLong("Until",p.level().getGameTime());ExpansionSupplies.updateGuide(p);h.assertTrue(!p.getPersistentData().contains("cod4Guide"),"Marker stops at deadline");
        ExpansionSupplies.mark(p,p.blockPosition());p.getPersistentData().getCompound("cod4Guide").putString("Dimension","dynasty:underworld");
        ExpansionSupplies.updateGuide(p);h.assertTrue(!p.getPersistentData().contains("cod4Guide"),"Dimension mismatch clears old guidance");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void goldSealFirstPickupBonusIsExclusiveAndDoesNotRepeat(GameTestHelper h){
        h.assertTrue(DynastyMerit.firstObtainAmount(Set.of("gold_seal_charm"),25)==30,"Twenty percent first-pickup source bonus");
        h.assertTrue(DynastyMerit.firstObtainAmount(Set.of("gold_seal_charm","merit_badge"),25)==25,"Merit badge suppresses this exclusive bonus");
        h.assertTrue(DynastyMerit.firstObtainAmount(Set.of(),25)==25,"No charm, no source bonus");
        var p=player(h);equipCharm(p,new ItemStack(DynastyTrinkets.GOLD_SEAL_CHARM.get()));
        DynastyMerit.onFirstObtain(p,"dragon_crystal");int once=DynastyStats.getMerit(p);
        h.assertTrue(once==38,"Real first-obtain event adds 20% while retaining the original global 25% bonus and integer rounding");
        DynastyMerit.onFirstObtain(p,"dragon_crystal");h.assertTrue(DynastyStats.getMerit(p)==once,"Repeat pickup never awards merit twice");
        var q=player(h);q.getPersistentData().merge(p.getPersistentData().copy());DynastyMerit.onFirstObtain(q,"dragon_crystal");
        h.assertTrue(DynastyStats.getMerit(q)==once,"Existing first-pickup flag survives reconstructed player state");h.succeed();
    }
    private static void equipCharm(ServerPlayer p,ItemStack stack){
        if(!DynastyCuriosSetup.isLoaded())p.getInventory().setItem(9,stack);
        else try{
            Class<?> api=Class.forName("top.theillusivec4.curios.api.CuriosApi");
            var lazy=(net.minecraftforge.common.util.LazyOptional<?>)api.getMethod("getCuriosInventory",net.minecraft.world.entity.LivingEntity.class).invoke(null,p);
            var handler=lazy.resolve().orElseThrow();var type=Class.forName("top.theillusivec4.curios.api.type.capability.ICuriosItemHandler");
            var optional=(Optional<?>)type.getMethod("getStacksHandler",String.class).invoke(handler,"charm");var slots=optional.orElseThrow();
            var inventory=(net.minecraftforge.items.IItemHandlerModifiable)Class.forName("top.theillusivec4.curios.api.type.inventory.ICurioStacksHandler").getMethod("getStacks").invoke(slots);
            inventory.setStackInSlot(0,stack);
        }catch(ReflectiveOperationException failure){throw new IllegalStateException("Curios fixture failed",failure);}
        p.tickCount++;
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void taiyiReducesExistingFluteSkillAndGlowHasRealRequirements(GameTestHelper h){
        var p=player(h);suit(p,"taiyi",3);var flute=DynastyWeapons.YU_DI.get();p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(flute));
        flute.use(h.getLevel(),p,InteractionHand.MAIN_HAND);
        for(int i=0;i<107;i++)p.getCooldowns().tick();h.assertTrue(p.getCooldowns().isOnCooldown(flute),"Existing flute skill has 108-tick cooldown");
        p.getCooldowns().tick();h.assertTrue(!p.getCooldowns().isOnCooldown(flute),"Ten percent reduction applies beyond new Qimen skills");
        suit(p,"taiyi",4);p.experienceLevel=29;h.assertTrue(!EquipmentBehaviors.taiyiGlow(p),"Below milestone no golden glow");
        p.experienceLevel=30;h.assertTrue(EquipmentBehaviors.taiyiGlow(p)&&!EquipmentBehaviors.taiyiGlow(p),"Glow triggers once and preserves long cooldown");
        suit(p,"taiyi",0);h.assertTrue(EquipmentBehaviors.cooldown(p,120)==120,"Unequip removes future skill reduction");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void statusPacketCarriesLayersEntityAndRemoval(GameTestHelper h){
        var z=new Zombie(h.getLevel());z.addEffect(new MobEffectInstance(ExpansionEffects.THUNDER.get(),100,1));
        var packet=EffectPresentation.packet(z,4,false);
        h.assertTrue(packet.valid()&&packet.entityId()==z.getId()&&packet.tick()==1&&packet.sequence().equals("status_4"),"Two visible marks bind to the affected entity");
        var buf=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        try{Cod3VisualPacket.encode(packet,buf);h.assertTrue(Cod3VisualPacket.decode(buf).equals(packet),"Status payload round trip preserves layers and color");}finally{buf.release();}
        h.assertTrue(EffectPresentation.packet(z,4,true).sequence().equals("status_clear_4"),"Removal has explicit client clear instruction");
        for(int i=1;i<=8;i++)h.assertTrue(EffectPresentation.packet(z,i,true).valid(),"Each of eight status visuals uses existing valid wire schema");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void yangBenefitsUndeadDamageWithoutReenteringSyntheticProcs(GameTestHelper h){
        var p=player(h);var target=new Zombie(h.getLevel());for(int i=0;i<3;i++)ExpansionEffects.apply(p,ExpansionEffects.YANG,100);
        var event=new LivingHurtEvent(target,target.damageSources().playerAttack(p),100);EffectPresentation.yangDamage(event);
        h.assertTrue(Math.abs(event.getAmount()-124)<.001,"Three Yang layers add specific undead damage benefit");
        var synthetic=new LivingHurtEvent(target,target.damageSources().playerAttack(p),100);
        DynastyTrinketOnHit.syntheticDamage(()->EffectPresentation.yangDamage(synthetic));h.assertTrue(synthetic.getAmount()==100,"Synthetic accessory damage is not amplified a second time");h.succeed();
    }
    private Cod4ContinuationGameTests(){}
}
