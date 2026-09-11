package com.dynasty;

import com.google.common.collect.ImmutableMultimap;
import com.google.common.collect.Multimap;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.ForgeMod;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.UUID;

/**
 * 兵器谱：从青铜剑到方天画戟的「进化链」武器，每一把都有独特机制。
 * Weapon roster: an evolution chain from bronze sword to the Fangtian halberd, each with its own gimmick.
 */
@SuppressWarnings("null")
public final class DynastyWeapons {

    private DynastyWeapons() {
    }

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    private static final UUID REACH_UUID = UUID.fromString("7a1c9e30-4b62-4f7d-8f2a-51c3d9e0a101");

    /** 长柄武器：攻击距离 +3，命中时轻挑目标 / polearm: +3 reach, light upward jab */
    public static class PolearmItem extends SwordItem {
        public PolearmItem(Tier tier, int damage, float speed, Item.Properties props) {
            super(tier, damage, speed, props);
        }

        @Override
        public Multimap<Attribute, AttributeModifier> getDefaultAttributeModifiers(EquipmentSlot slot) {
            Multimap<Attribute, AttributeModifier> base = super.getDefaultAttributeModifiers(slot);
            if (slot != EquipmentSlot.MAINHAND) {
                return base;
            }
            ImmutableMultimap.Builder<Attribute, AttributeModifier> builder = ImmutableMultimap.builder();
            builder.putAll(base);
            builder.put(ForgeMod.ENTITY_REACH.get(), new AttributeModifier(REACH_UUID,
                    "dynasty_polearm_reach", 3.0D, AttributeModifier.Operation.ADDITION));
            builder.put(ForgeMod.BLOCK_REACH.get(), new AttributeModifier(REACH_UUID,
                    "dynasty_polearm_block_reach", 2.0D, AttributeModifier.Operation.ADDITION));
            return builder.build();
        }

        @Override
        public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
            target.push(0.0D, 0.35D, 0.0D);
            return super.hurtEnemy(stack, target, attacker);
        }
    }

    /** 玉笛：右键吹奏，周围敌人虚弱 + 缓慢 / Jade Flute: area debuff */
    public static class FluteItem extends SwordItem {
        public FluteItem(Tier tier, int damage, float speed, Item.Properties props) {
            super(tier, damage, speed, props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (!level.isClientSide()) {
                int affected = 0;
                for (LivingEntity target : level.getEntitiesOfClass(LivingEntity.class,
                        player.getBoundingBox().inflate(8.0D), e -> e != player)) {
                    target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 20 * 6, 1));
                    target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 20 * 6, 1));
                    affected++;
                }
                player.sendSystemMessage(net.minecraft.network.chat.Component.literal(
                        "§d[玉笛] §r清音绕梁，" + affected + " 名敌人心神失守。"));
                level.playSound(null, player.blockPosition(), SoundEvents.NOTE_BLOCK_FLUTE.value(),
                        SoundSource.PLAYERS, 1.5F, 1.0F);
                player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 20 * 8, 0));
            }
            player.getCooldowns().addCooldown(this, 120);
            player.swing(hand, true);
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }

    /** 龙吟弓：箭矢伤害大增、强击退、可穿透 / Dragon Bow */
    public static class DragonBowItem extends BowItem {
        public DragonBowItem(Item.Properties props) {
            super(props);
        }

        @Override
        public AbstractArrow customArrow(AbstractArrow arrow) {
            arrow.setBaseDamage(arrow.getBaseDamage() * 3.0D + 50.0D);
            arrow.setKnockback(2);
            arrow.setPierceLevel((byte) 3);
            return super.customArrow(arrow);
        }
    }

    private static RegistryObject<Item> sword(String name, Tier tier, int dmg, float speed) {
        return ITEMS.register(name, () -> new SwordItem(tier, dmg, speed, new Item.Properties()));
    }

    // ---- 进化链 / evolution chain（攻击力逐个递加）----

    /** 1. 唐刀：攻速最快（2.8 次/秒）/ Tang Dao: fastest swing */
    public static final RegistryObject<Item> TANG_DAO =
            sword("tang_dao", DynastyTiers.BRONZE, 499, -1.0F);                         // 1000

    /** 2. 环首刀：受击后反击（力量）/ Huan Shou Dao: counter-attack */
    public static final RegistryObject<Item> HUAN_SHOU_DAO =
            sword("huan_shou_dao", DynastyTiers.BRONZE, 599, -2.2F);                    // 1100

    /** 3. 长枪：攻击距离 +3 / Chang Qiang: reach */
    public static final RegistryObject<Item> CHANG_QIANG = ITEMS.register("chang_qiang",
            () -> new PolearmItem(DynastyTiers.OFFICIAL_SILVER, 599, -2.6F, new Item.Properties())); // 1300

    /** 4. 玉笛：右键吹奏，范围削弱 / Jade Flute: area debuff */
    public static final RegistryObject<Item> YU_DI = ITEMS.register("yu_di",
            () -> new FluteItem(DynastyTiers.JADE, 549, -1.8F, new Item.Properties()));  // 1450

    /** 5. 巨阙重剑：击退 + 缓慢 / Juque Greatsword */
    public static final RegistryObject<Item> JUQUE_SWORD =
            sword("juque_sword", DynastyTiers.JADE, 799, -3.0F);                        // 1700

    /** 6. 破军战斧：无视一半士气减伤 / Po Jun Axe */
    public static final RegistryObject<Item> POJUN_AXE = ITEMS.register("pojun_axe",
            () -> new AxeItem(DynastyTiers.DRAGON_CRYSTAL, 450, -2.9F, new Item.Properties())); // 1750

    /** 7. 龙吟弓：远程重箭（穿透 3）/ Dragon Bow */
    public static final RegistryObject<Item> DRAGON_BOW = ITEMS.register("dragon_bow",
            () -> new DragonBowItem(new Item.Properties().durability(8000)));
}
