package com.dynasty.workshop;

import com.dynasty.Dynasty;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.*;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraftforge.registries.*;
import java.util.*;

/** Six original reusable relics. Server owns charges, cooldown and effects; no per-tick scanning. */
public final class DynastyTreasures {
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final List<String> IDS=List.of("mingyuan_soul_lantern","longmai_prism","chengque_mending_seal","zhengwu_oath_tally","zhouguang_star_leaf","chixiao_ember");
    static {for(int i=0;i<IDS.size();i++){final int kind=i;ITEMS.register(IDS.get(i),()->new Treasure(kind));}}
    public static final class Treasure extends Item {
        private final int kind;
        Treasure(int kind){super(new Properties().durability(24).rarity(Rarity.EPIC));this.kind=kind;}
        @Override public boolean isFoil(ItemStack stack){return true;}
        @Override public void appendHoverText(ItemStack s,Level l,List<Component> tips,TooltipFlag f){tips.add(Component.translatable("treasure.dynasty."+IDS.get(kind)));}
        @Override public InteractionResultHolder<ItemStack> use(Level level,Player player,InteractionHand hand){
            ItemStack held=player.getItemInHand(hand);
            if(level.isClientSide)return InteractionResultHolder.success(held);
            if(player.getCooldowns().isOnCooldown(this))return InteractionResultHolder.fail(held);
            var world=(ServerLevel)level;boolean changed=true;
            switch(kind){
                case 0 -> {
                    var spirits=world.getEntitiesOfClass(LivingEntity.class,player.getBoundingBox().inflate(18),e->e!=player&&e.getMobType()==MobType.UNDEAD);
                    spirits.forEach(e->e.addEffect(new MobEffectInstance(MobEffects.GLOWING,200)));
                    changed=!spirits.isEmpty();
                }
                case 1 -> {player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,1200));player.addEffect(new MobEffectInstance(MobEffects.DIG_SPEED,600));}
                case 2 -> {
                    ItemStack target=player.getItemInHand(hand==InteractionHand.MAIN_HAND?InteractionHand.OFF_HAND:InteractionHand.MAIN_HAND);
                    changed=target.isDamageableItem()&&target.isDamaged()&&!(target.getItem() instanceof Treasure);
                    if(changed)target.setDamageValue(Math.max(0,target.getDamageValue()-Math.max(1,target.getMaxDamage()/5)));
                }
                case 3 -> {
                    player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,200));
                    world.getEntitiesOfClass(Player.class,player.getBoundingBox().inflate(8),p->p!=player&&p.isAlliedTo(player))
                        .forEach(p->p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,200)));
                }
                case 4 -> {
                    // Read the existing ledger, never force-load chunks or scan the whole dimension.
                    com.dynasty.ritual.ZhenyuanRitualSavedData.Session nearest=null;double distance=96*96;
                    var origin=player.blockPosition();
                    for(var session:com.dynasty.ritual.ZhenyuanRitualSavedData.get(world).sessions()){
                        if(session.dimension.equals(world.dimension().location().toString())&&session.core.distSqr(origin)<distance){nearest=session;distance=session.core.distSqr(origin);}
                    }
                    changed=nearest!=null;
                    if(changed)player.displayClientMessage(Component.translatable("treasure.dynasty.altar_read",Integer.bitCount(nearest.mask&15)),true);
                }
                case 5 -> player.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE,1200));
            }
            if(!changed){player.displayClientMessage(Component.translatable("treasure.dynasty.no_target"),true);return InteractionResultHolder.fail(held);}
            player.getCooldowns().addCooldown(this,kind==3?600:100);
            if(!player.getAbilities().instabuild)held.hurtAndBreak(1,player,p->p.broadcastBreakEvent(hand));
            world.sendParticles(kind==5?ParticleTypes.FLAME:kind==0?ParticleTypes.SOUL:ParticleTypes.ENCHANT,player.getX(),player.getY()+1,player.getZ(),16,.6,.5,.6,.01);
            world.playSound(null,player.blockPosition(),SoundEvents.AMETHYST_BLOCK_CHIME,SoundSource.PLAYERS,.7f,.8f+kind*.08f);
            return InteractionResultHolder.consume(held);
        }
    }
    private DynastyTreasures(){}
}
