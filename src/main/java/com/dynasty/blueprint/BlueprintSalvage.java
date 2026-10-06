package com.dynasty.blueprint;

import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.AnvilUpdateEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegistryObject;

/** Real recovered components: vanilla anvil owns inventory/XP consumption and multiplayer updates. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class BlueprintSalvage {
    public static final RegistryObject<Item> KAISHAN_AXE_BLADE=register("kaishan_axe_blade",Use.IRON_AXE);
    public static final RegistryObject<Item> REFINED_WROUGHT_IRON=register("refined_wrought_iron",Use.IRON_GEAR);
    public static final RegistryObject<Item> BROKEN_HEART_MIRROR=register("broken_heart_mirror",Use.IRON_ARMOR);
    public static final RegistryObject<Item> YIN_JADE_SHARD=register("yin_jade_shard",Use.JADE_GEAR);
    public static final RegistryObject<Item> NETHER_TATTER=register("nether_tatter",Use.LEATHER_ARMOR);
    public static final RegistryObject<Item> ANCIENT_COIN_RUST=BlueprintEntities.ITEMS.register("ancient_coin_rust",()->new Item(new Item.Properties()));
    public static final RegistryObject<Item> BROKEN_IRON_BLADE=register("broken_iron_blade",Use.IRON_SWORD);
    public static final RegistryObject<Item> COARSE_LINEN=register("coarse_linen",Use.LEATHER_ARMOR);
    public static final RegistryObject<Item> HEAVY_SHIELD_REMNANT=register("heavy_shield_remnant",Use.SHIELD);
    public static final RegistryObject<Item> WROUGHT_IRON_BILLET=register("wrought_iron_billet",Use.IRON_GEAR);
    public static final RegistryObject<Item> DAMAGED_CHAINMAIL=register("damaged_chainmail",Use.CHAINMAIL);
    public static final RegistryObject<Item> DRY_PEACH_BRANCH=register("dry_peach_branch",Use.BOWS);
    public static final RegistryObject<Item> SHANXIAO_CLAW=register("shanxiao_claw",Use.IRON_AXE);
    public static final RegistryObject<Item> GHOST_FACE_FUR=register("ghost_face_fur",Use.LEATHER_ARMOR);
    public static final RegistryObject<Item> GREEN_BEAST_GALL=BlueprintEntities.ITEMS.register("green_beast_gall",Antidote::new);
    public static final RegistryObject<Item> IRON_SPEARHEAD=register("iron_spearhead",Use.IRON_GEAR);
    public static final RegistryObject<Item> TOUGH_WOOD_SHAFT=register("tough_wood_shaft",Use.BOWS);
    public static final RegistryObject<Item> RUSTED_LAMELLAR_PLATE=register("rusted_lamellar_plate",Use.IRON_ARMOR);
    public static final RegistryObject<Item> SHORT_CROSSBOW_BOLT=BlueprintEntities.ITEMS.register("short_crossbow_bolt",()->new ArrowItem(new Item.Properties()));
    public static final RegistryObject<Item> BRONZE_GEAR_PART=register("bronze_gear_part",Use.CROSSBOW);
    public static final RegistryObject<Item> FINE_STEEL_CHAIN=register("fine_steel_chain",Use.CHAINMAIL);
    public static final RegistryObject<Item> IRON_GRAPPLING_CLAW=register("iron_grappling_claw",Use.IRON_AXE);
    public static final RegistryObject<Item> SWIFT_BOOT_SCRAP=register("swift_boot_scrap",Use.LEATHER_BOOTS);
    public static final RegistryObject<Item> POOR_GUNPOWDER=plain("poor_gunpowder");
    public static final RegistryObject<Item> POTTERY_FRAGMENT=plain("pottery_fragment");
    public static final RegistryObject<Item> BLOODIED_CLOTH=register("bloodied_cloth",Use.LEATHER_ARMOR);
    public static final RegistryObject<Item> BROKEN_TIGER_TALLY=plain("broken_tiger_tally");
    public static final RegistryObject<Item> BLACK_ARMY_BANNER_SCRAP=plain("black_army_banner_scrap");
    public static final RegistryObject<Item> VENGEFUL_WAR_SOUL=plain("vengeful_war_soul");
    private enum Use { IRON_AXE, IRON_SWORD, IRON_GEAR, IRON_ARMOR, JADE_GEAR, LEATHER_ARMOR, LEATHER_BOOTS, SHIELD, CHAINMAIL, BOWS, CROSSBOW }
    private static RegistryObject<Item> register(String id,Use use){return BlueprintEntities.ITEMS.register(id,()->new ComponentItem(use));}
    private static RegistryObject<Item> plain(String id){return BlueprintEntities.ITEMS.register(id,()->new Item(new Item.Properties()));}
    private BlueprintSalvage(){}
    static void bootstrap(){}
    private static final class ComponentItem extends Item {
        final Use use;
        ComponentItem(Use use){super(new Properties());this.use=use;}
        boolean accepts(ItemStack stack){
            var iron=new ItemStack(Items.IRON_INGOT);
            boolean tool=stack.getItem() instanceof TieredItem item&&item.getTier().getRepairIngredient().test(iron);
            boolean armor=stack.getItem() instanceof ArmorItem item&&item.getMaterial().getRepairIngredient().test(iron);
            return switch(use){case IRON_AXE->tool&&stack.getItem() instanceof AxeItem;case IRON_SWORD->tool&&stack.getItem() instanceof SwordItem;
                case IRON_GEAR->tool||armor;case IRON_ARMOR->armor;
                case SHIELD->stack.is(Items.SHIELD);
                case CHAINMAIL->stack.getItem() instanceof ArmorItem item&&item.getMaterial()==ArmorMaterials.CHAIN;
                case BOWS->stack.is(Items.BOW)||stack.is(Items.CROSSBOW);
                case CROSSBOW->stack.is(Items.CROSSBOW);
                case LEATHER_BOOTS->stack.getItem() instanceof ArmorItem item&&item.getMaterial()==ArmorMaterials.LEATHER&&item.getType()==ArmorItem.Type.BOOTS;
                case LEATHER_ARMOR->stack.getItem() instanceof ArmorItem item&&item.getMaterial()==ArmorMaterials.LEATHER;
                case JADE_GEAR->stack.getItem() instanceof TieredItem toolItem&&toolItem.getTier().getRepairIngredient().test(new ItemStack(com.dynasty.DynastyItems.JADE.get()))
                    ||stack.getItem() instanceof ArmorItem armorItem&&armorItem.getMaterial().getRepairIngredient().test(new ItemStack(com.dynasty.DynastyItems.JADE.get()));};
        }
        @Override public void appendHoverText(ItemStack stack,@Nullable Level level,List<Component> lines,TooltipFlag flag){
            lines.add(Component.translatable("tooltip.dynasty.salvage."+use.name().toLowerCase(java.util.Locale.ROOT)).withStyle(ChatFormatting.GRAY));
        }
    }
    private static final class Antidote extends Item {
        Antidote(){super(new Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(0).saturationMod(0).alwaysEat().build()));}
        @Override public ItemStack finishUsingItem(ItemStack stack,Level level,net.minecraft.world.entity.LivingEntity user){
            if(!level.isClientSide)user.removeEffect(net.minecraft.world.effect.MobEffects.POISON);
            return super.finishUsingItem(stack,level,user);
        }
        @Override public void appendHoverText(ItemStack stack,@Nullable Level level,List<Component> lines,TooltipFlag flag){
            lines.add(Component.translatable("tooltip.dynasty.green_beast_gall").withStyle(ChatFormatting.GRAY));
        }
    }
    @SubscribeEvent public static void repair(AnvilUpdateEvent event){
        var base=event.getLeft();var material=event.getRight();
        if(!(material.getItem() instanceof ComponentItem part)||base.getCount()!=1||!base.isDamaged()||!part.accepts(base))return;
        int perPart=Math.max(1,base.getMaxDamage()/4);
        int count=Math.min(material.getCount(),(base.getDamageValue()+perPart-1)/perPart);
        var output=base.copy();output.setDamageValue(Math.max(0,base.getDamageValue()-count*perPart));
        if(event.getName()!=null){
            if(event.getName().isBlank())output.resetHoverName();
            else if(!event.getName().equals(base.getHoverName().getString()))output.setHoverName(Component.literal(event.getName()));
        }
        // Respect accumulated prior work. Clamp arithmetic; never turn a huge NBT value into negative/free cost.
        long prior=Math.max(0,base.getBaseRepairCost());
        event.setCost((int)Math.min(Integer.MAX_VALUE,prior+count+1));event.setMaterialCost(count);
        output.setRepairCost((int)Math.min(Integer.MAX_VALUE,prior*2+1));event.setOutput(output);
    }
}
