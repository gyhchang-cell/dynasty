package com.dynasty.worldevent;

import com.dynasty.blueprint.TemplateMob;
import com.dynasty.blueprint.combat.Faction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.Level;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** Ordinary source-event rewards. None duplicates a cod1 artifact or registers a new creature. */
public final class WorldEventItems {
    public static final String PERMIT="DynastyArmyPermitUntil";
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,"dynasty");
    public static final RegistryObject<Item> COLD_IRON=ITEMS.register("refined_cold_iron",()->new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> XUANNIAO_FEATHER=ITEMS.register("xuanniao_shenyu",()->new Item(new Item.Properties().rarity(Rarity.RARE)));
    public static final RegistryObject<Item> EVOCATION=ITEMS.register("evocation_talisman",()->new Item(new Item.Properties().rarity(Rarity.RARE).stacksTo(16)){
        @Override public InteractionResultHolder<ItemStack> use(Level level,Player player,InteractionHand hand){
            var stack=player.getItemInHand(hand);if(!level.isClientSide){
                int affected=0;
                for(var mob:level.getEntitiesOfClass(net.minecraft.world.entity.Mob.class,player.getBoundingBox().inflate(12),e->e.isAlive()
                        &&(e.getMobType()==net.minecraft.world.entity.MobType.UNDEAD||e instanceof TemplateMob t&&t.faction()==Faction.SPIRITS))){
                    if(++affected>16)break;mob.addEffect(new MobEffectInstance(MobEffects.GLOWING,400),player);
                }
                if(!player.isCreative())stack.shrink(1);player.getCooldowns().addCooldown(this,200);
            }
            return InteractionResultHolder.sidedSuccess(stack,level.isClientSide);
        }
    });
    public static final RegistryObject<Item> OFFICIAL_DOCUMENT=ITEMS.register("official_travel_document",()->new Item(new Item.Properties().rarity(Rarity.UNCOMMON).stacksTo(16)){
        @Override public InteractionResultHolder<ItemStack> use(Level level,Player player,InteractionHand hand){
            var stack=player.getItemInHand(hand);if(!level.isClientSide){
                long until=player.getPersistentData().getLong(PERMIT);
                if(until>level.getGameTime()&&until<=level.getGameTime()+12000)return InteractionResultHolder.fail(stack);
                player.getPersistentData().putLong(PERMIT,level.getGameTime()+12000);
                if(!player.isCreative())stack.shrink(1);player.getCooldowns().addCooldown(this,200);
                player.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.dynasty.event.official_document"),true);
            }
            return InteractionResultHolder.sidedSuccess(stack,level.isClientSide);
        }
    });
    public static boolean permitted(TemplateMob mob,Player player){
        if(mob.faction()!=Faction.DYNASTY_ARMY||mob.getLastHurtByMob()==player)return false;
        long until=player.getPersistentData().getLong(PERMIT),now=mob.level().getGameTime();return until>now&&until<=now+12000;
    }
    private WorldEventItems(){}
}
