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
    public static final RegistryObject<Item> COLD_CONDENSED_WATER=plain("cold_condensed_water"), SUBMERGED_IRON_SCRAP=plain("submerged_iron_scrap"), WATER_GHOST_HAIR=plain("water_ghost_hair");
    public static final RegistryObject<Item> LUMINOUS_FISH_GLUE=plain("luminous_fish_glue"), SOFT_FISH_BONE=plain("soft_fish_bone"), PURE_SPIRIT_DROP=plain("pure_spirit_drop");
    public static final RegistryObject<Item> THIN_BAT_MEMBRANE=plain("thin_bat_membrane"), GREEN_PHOSPHOR=plain("green_phosphor"), GHOST_FACE_FLAKE=plain("ghost_face_flake");
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
    public static final RegistryObject<Item> BLACKENED_BONE=plain("blackened_bone");
    public static final RegistryObject<Item> CONGEALED_CORPSE_OIL=BlueprintEntities.ITEMS.register("congealed_corpse_oil",()->new Item(new Item.Properties()){
        @Override public int getBurnTime(ItemStack stack,@Nullable net.minecraft.world.item.crafting.RecipeType<?> recipeType){return 400;}
    });
    public static final RegistryObject<Item> STRONGMAN_WRIST_WEIGHT=register("strongman_wrist_weight",Use.CHAINMAIL);
    public static final RegistryObject<Item> WHITE_WAX_TEAR=plain("white_wax_tear");
    public static final RegistryObject<Item> WRONGED_SHROUD=register("wronged_shroud",Use.LEATHER_ARMOR);
    public static final RegistryObject<Item> PALE_MILK_TOOTH=plain("pale_milk_tooth");
    public static final RegistryObject<Item> TOUGH_BAMBOO_SLIVER=register("tough_bamboo_sliver",Use.BOWS);
    public static final RegistryObject<Item> PAPER_CUTTING_KNIFE=register("paper_cutting_knife",Use.SHEARS);
    public static final RegistryObject<Item> PAINTED_CINNABAR=plain("painted_cinnabar");
    public static final RegistryObject<Item> RED_TOAD_GLAND=plain("red_toad_gland");
    public static final RegistryObject<Item> TOUGH_TOAD_HIDE=register("tough_toad_hide",Use.LEATHER_ARMOR);
    public static final RegistryObject<Item> POISON_GEL=plain("poison_gel");
    public static final RegistryObject<Item> POINTED_DEAD_TOOTH=plain("pointed_dead_tooth");
    public static final RegistryObject<Item> RUSTED_HELMET_SPIKE=register("rusted_helmet_spike",Use.IRON_ARMOR);
    public static final RegistryObject<Item> YIN_AIR_SAC=BlueprintEntities.ITEMS.register("yin_air_sac",BreathSac::new);
    public static final RegistryObject<Item> RESONANT_SCORPION_SHELL=plain("resonant_scorpion_shell");
    public static final RegistryObject<Item> METAL_STING_NEEDLE=plain("metal_sting_needle");
    public static final RegistryObject<Item> PURE_YELLOW_SAND=plain("pure_yellow_sand");
    public static final RegistryObject<Item> ANCIENT_TREE_HEART=plain("ancient_tree_heart");
    public static final RegistryObject<Item> HARDENED_DEAD_BARK=BlueprintEntities.ITEMS.register("hardened_dead_bark",()->new Item(new Item.Properties()){
        @Override public int getBurnTime(ItemStack stack,@Nullable net.minecraft.world.item.crafting.RecipeType<?> recipeType){return 600;}
    });
    public static final RegistryObject<Item> GLOWING_PARASITE_MUSHROOM=BlueprintEntities.ITEMS.register("glowing_parasite_mushroom",()->new Item(new Item.Properties().food(
        new net.minecraft.world.food.FoodProperties.Builder().nutrition(2).saturationMod(.2F).alwaysEat()
            .effect(()->new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.NIGHT_VISION,400),1).build())){
        @Override public void appendHoverText(ItemStack stack,@Nullable Level level,List<Component> lines,TooltipFlag flag){
            lines.add(Component.translatable("tooltip.dynasty.glowing_parasite_mushroom").withStyle(ChatFormatting.GRAY));
        }
    });
    public static final RegistryObject<Item> YOUNG_JIAO_SCALE=register("young_jiao_scale",Use.LEATHER_ARMOR);
    public static final RegistryObject<Item> COLD_POOL_ESSENCE=BlueprintEntities.ITEMS.register("cold_pool_essence",BreathSac::new);
    public static final RegistryObject<Item> SLIPPERY_JIAO_GALL=BlueprintEntities.ITEMS.register("slippery_jiao_gall",Antidote::new);
    public static final RegistryObject<Item> WARDING_INSCRIPTION_SHARD=register("warding_inscription_shard",Use.SHIELD);
    public static final RegistryObject<Item> ANCIENT_BRONZE_CHAIN_RING=register("ancient_bronze_chain_ring",Use.CHAINMAIL);
    public static final RegistryObject<Item> HARD_BLUESTONE=plain("hard_bluestone");
    public static final RegistryObject<Item> BRONZE_CLOCKSPRING=register("bronze_clockspring",Use.CROSSBOW);
    public static final RegistryObject<Item> JOINERY_GEAR=register("joinery_gear",Use.BOWS);
    public static final RegistryObject<Item> FIRE_OIL_GLASS_BEAD=BlueprintEntities.ITEMS.register("fire_oil_glass_bead",()->new Item(new Item.Properties()){
        @Override public int getBurnTime(ItemStack stack,@Nullable net.minecraft.world.item.crafting.RecipeType<?> type){return 800;}
    });
    public static final RegistryObject<Item> BRONZE_BALL_JOINT=register("bronze_ball_joint",Use.CROSSBOW);
    public static final RegistryObject<Item> MINIATURE_OIL_NOZZLE=plain("miniature_oil_nozzle");
    public static final RegistryObject<Item> SERPENT_COPPER_PLATE=register("serpent_copper_plate",Use.SHIELD);
    public static final RegistryObject<Item> DIAMOND_DRILL_FRAGMENT=register("diamond_drill_fragment",Use.IRON_GEAR);
    public static final RegistryObject<Item> HEATPROOF_COPPER_PLATE=register("heatproof_copper_plate",Use.SHIELD);
    public static final RegistryObject<Item> REFINED_COAL_BALL=BlueprintEntities.ITEMS.register("refined_coal_ball",()->new Item(new Item.Properties()){
        @Override public int getBurnTime(ItemStack stack,@Nullable net.minecraft.world.item.crafting.RecipeType<?> type){return 2400;}
    });
    private static final class BreathSac extends Item {
        BreathSac(){super(new Properties().food(new net.minecraft.world.food.FoodProperties.Builder().nutrition(0).saturationMod(0).alwaysEat().build()));}
        @Override public ItemStack finishUsingItem(ItemStack stack,Level level,net.minecraft.world.entity.LivingEntity user){
            if(!level.isClientSide){user.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.SLOW_FALLING,200));
                user.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.WATER_BREATHING,200));}
            return super.finishUsingItem(stack,level,user);
        }
        @Override public void appendHoverText(ItemStack stack,@Nullable Level level,List<Component> lines,TooltipFlag flag){
            lines.add(Component.translatable("tooltip.dynasty.yin_air_sac").withStyle(ChatFormatting.GRAY));
        }
    }
    private enum Use { SHEARS, IRON_AXE, IRON_SWORD, IRON_GEAR, IRON_ARMOR, JADE_GEAR, LEATHER_ARMOR, LEATHER_BOOTS, SHIELD, CHAINMAIL, BOWS, CROSSBOW }
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
                case SHEARS->stack.is(Items.SHEARS);
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
