package com.dynasty;

import com.google.common.collect.ImmutableMultimap;
import com.google.common.collect.Multimap;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.server.level.ServerLevel;
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
 * 兵器谱（重制版）：从木矛一路进化到天子剑。
 *
 * 进化链（括号内为总攻击力）：
 *   木矛(5) → 石戈(9) → 铜刀(14) → 铁剑(20) → 青铜剑(34) → 唐刀(46) → 环首刀(62)
 *   → 长枪(82) → 玉笛(105) → 官银剑(132) → 玉剑(170) → 巨阙重剑(500)
 *   → 破军战斧(650) → 龙晶剑(1400) → 方天画戟(1900) → 玄天钺(2500) → 天子剑(3200)
 *   名器还会额外带「特攻」（DynastyBalance.WEAPON_BONUS，命中时再补固定伤害）：
 *   龙晶剑 +150 / 七星 +220 / 屠龙刀 +350 / 尚方宝剑 +400 / 天子剑 +500 …
 *   弓分两条支线（长弓是分叉点）：
 *     速射流：猎弓(×1.5+4) → 长弓(×2+20) → 神臂弓(×2.8+70) → 落雁弓(×3.3+120) → 天狼弓(×3.8+200、穿透 1)
 *     穿透流：长弓 → 龙吟弓(×3.5+150、穿透 3) → 射日弓(×4.5+280)
 *
 * 后半段每一把都要求「上一把武器 + 稀有材料 + Boss 掉落物（特定条件）」。
 *
 * Weapon roster: a real progression chain from a wooden spear to the Sword of Heaven.
 */
@SuppressWarnings("null")
public final class DynastyWeapons {

    private DynastyWeapons() {
    }

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    private static final UUID REACH_UUID = UUID.fromString("7a1c9e30-4b62-4f7d-8f2a-51c3d9e0a101");

    /** 长柄武器：攻击距离 +3，命中时轻挑目标 / polearm: +3 reach */
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

    /** 弓：把箭矢伤害按倍率放大 / bows scale arrow damage */
    public static class HuntingBowItem extends BowItem {
        private final double multiplier;
        private final double bonus;

        public HuntingBowItem(double multiplier, double bonus, Item.Properties props) {
            super(props);
            this.multiplier = multiplier;
            this.bonus = bonus;
        }

        public double visualDamageScore() {
            return this.multiplier * 2.0D + this.bonus;
        }

        @Override
        public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remainingTicks) {
            super.onUseTick(level, user, stack, remainingTicks);
            if (level instanceof ServerLevel server && user instanceof Player player) {
                DynastyBowRitual.onCharge(server, player, this,
                        stack.getUseDuration() - remainingTicks, visualDamageScore());
            }
        }

        @Override
        public void releaseUsing(ItemStack stack, Level level, LivingEntity user, int remainingTicks) {
            int chargedTicks = stack.getUseDuration() - remainingTicks;
            super.releaseUsing(stack, level, user, remainingTicks);
            if (level instanceof ServerLevel server && user instanceof Player player) {
                DynastyBowRitual.onRelease(server, player, this, chargedTicks, visualDamageScore());
            }
        }

        @Override
        public AbstractArrow customArrow(AbstractArrow arrow) {
            arrow.setBaseDamage(arrow.getBaseDamage() * this.multiplier + this.bonus);
            DynastyBowRitual.trackArrow(arrow, this, visualDamageScore());
            return super.customArrow(arrow);
        }
    }

    /** 后羿弓：毕业弓共享分级法阵，另有物品栏动态光泽。 */
    public static class HouyiBowItem extends HuntingBowItem {
        public HouyiBowItem(Item.Properties props) {
            super(4.0D, 300D, props);
        }

        @Override
        public boolean isFoil(ItemStack stack) {
            return true;
        }
    }

    /** 龙渊剑：保留原有攻击数值，增加物品栏动态附魔光泽。 */
    public static class LongyuanSwordItem extends SwordItem {
        public LongyuanSwordItem(Tier tier, int damage, float speed, Item.Properties props) {
            super(tier, damage, speed, props);
        }

        @Override
        public boolean isFoil(ItemStack stack) {
            return true;
        }
    }

    /** 龙吟弓 / 天狼弓：箭矢伤害大增，可带击退与穿透 / damage bows with knockback + pierce */
    public static class DragonBowItem extends BowItem {
        private final double multiplier;
        private final double bonus;
        private final int knockback;
        private final int pierce;

        public DragonBowItem(double multiplier, double bonus, int knockback, int pierce,
                             Item.Properties props) {
            super(props);
            this.multiplier = multiplier;
            this.bonus = bonus;
            this.knockback = knockback;
            this.pierce = pierce;
        }

        public double visualDamageScore() {
            return this.multiplier * 2.0D + this.bonus;
        }

        @Override
        public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remainingTicks) {
            super.onUseTick(level, user, stack, remainingTicks);
            if (level instanceof ServerLevel server && user instanceof Player player) {
                DynastyBowRitual.onCharge(server, player, this,
                        stack.getUseDuration() - remainingTicks, visualDamageScore());
            }
        }

        @Override
        public void releaseUsing(ItemStack stack, Level level, LivingEntity user, int remainingTicks) {
            int chargedTicks = stack.getUseDuration() - remainingTicks;
            super.releaseUsing(stack, level, user, remainingTicks);
            if (level instanceof ServerLevel server && user instanceof Player player) {
                DynastyBowRitual.onRelease(server, player, this, chargedTicks, visualDamageScore());
            }
        }

        @Override
        public AbstractArrow customArrow(AbstractArrow arrow) {
            arrow.setBaseDamage(arrow.getBaseDamage() * this.multiplier + this.bonus);
            arrow.setKnockback(this.knockback);
            arrow.setPierceLevel((byte) this.pierce);
            DynastyBowRitual.trackArrow(arrow, this, visualDamageScore());
            return super.customArrow(arrow);
        }
    }

    private static RegistryObject<Item> sword(String name, Tier tier, int dmg, float speed) {
        return ITEMS.register(name, () -> new SwordItem(tier, dmg, speed, new Item.Properties()));
    }

    // ========== 一、基础期：原版同级，伤害不高（开局不再直接 1000）==========

    /** 1. 木矛 / Wooden spear：5 伤害 */
    public static final RegistryObject<Item> MU_MAO =
            sword("mu_mao", DynastyTiers.PRIMITIVE, 4, -2.0F);                          // 5

    /** 2. 石戈 / Stone dagger-axe：9 伤害 */
    public static final RegistryObject<Item> SHI_GE =
            sword("shi_ge", DynastyTiers.STONE, 7, -2.2F);                              // 9

    /** 3. 铜刀 / Copper sabre：14 伤害（原版铜锭） */
    public static final RegistryObject<Item> TONG_DAO =
            sword("tong_dao", DynastyTiers.COPPER, 10, -2.0F);                          // 14

    /** 4. 铁剑 / Iron sword：20 伤害 */
    public static final RegistryObject<Item> TIE_JIAN =
            sword("tie_jian", DynastyTiers.IRON, 14, -2.4F);                            // 20

    /** 5. 猎弓 / Hunting bow：箭矢 ×1.5 + 4 */
    public static final RegistryObject<Item> LIE_GONG = ITEMS.register("lie_gong",
            () -> new HuntingBowItem(1.5D, 4.0D, new Item.Properties().durability(420)));

    // ========== 二、王朝期（青铜起进入高数值）==========

    /** 6. 唐刀 / Tang Dao：46，攻速最快 */
    public static final RegistryObject<Item> TANG_DAO =
            sword("tang_dao", DynastyTiers.BRONZE, 23, -1.0F);

    /** 7. 环首刀 / Huan Shou Dao：62，受击后获得力量 II */
    public static final RegistryObject<Item> HUAN_SHOU_DAO =
            sword("huan_shou_dao", DynastyTiers.BRONZE, 39, -2.2F);

    /** 8. 长弓 / Longbow：箭矢 ×2 + 20 */
    public static final RegistryObject<Item> CHANG_GONG = ITEMS.register("chang_gong",
            () -> new HuntingBowItem(2.0D, 20.0D, new Item.Properties().durability(1600)));

    /** 9. 长枪 / Chang Qiang：82，攻击距离 +3 */
    public static final RegistryObject<Item> CHANG_QIANG = ITEMS.register("chang_qiang",
            () -> new PolearmItem(DynastyTiers.OFFICIAL_SILVER, 41, -2.6F, new Item.Properties()));

    /** 10. 玉笛 / Jade Flute：105，右键范围削弱 */
    public static final RegistryObject<Item> YU_DI = ITEMS.register("yu_di",
            () -> new FluteItem(DynastyTiers.JADE, 34, -1.8F, new Item.Properties()));

    /** 11. 巨阙重剑 / Juque Greatsword：500，击退 + 缓慢 II */
    public static final RegistryObject<Item> JUQUE_SWORD =
            sword("juque_sword", DynastyTiers.JADE, 429, -3.0F);

    // ========== 三、名将期（需要 Boss 掉落物）==========

    /** 12. 破军战斧 / Po Jun Axe：650，无视一半士气减伤（需叛将首级） */
    public static final RegistryObject<Item> POJUN_AXE = ITEMS.register("pojun_axe",
            () -> new AxeItem(DynastyTiers.DRAGON_CRYSTAL, 509, -2.9F, new Item.Properties()));

    /** 13. 龙吟弓 / Dragon Bow：箭矢 ×3.5 + 150、穿透 3（需凤凰羽 + 龙鳞） */
    public static final RegistryObject<Item> DRAGON_BOW = ITEMS.register("dragon_bow",
            () -> new DragonBowItem(3.5D, 150.0D, 2, 3, new Item.Properties().durability(8000)));

    // ========== 四、帝兵期（需要多件 Boss 掉落物）==========

    /** 14. 玄天钺 / Xuantian Axe：2500，破甲（需龙帝玉玺） */
    public static final RegistryObject<Item> XUANTIAN_AXE = ITEMS.register("xuantian_axe",
            () -> new AxeItem(DynastyTiers.DRAGON_CRYSTAL, 2359, -3.0F, new Item.Properties()));

    /** 15. 天子剑 / Sword of Heaven：3200（毕业武器，原版上限已解除），命中回气 + 对王朝敌人加伤 */
    public static final RegistryObject<Item> TIANZI_SWORD =
            sword("tianzi_sword", DynastyTiers.DRAGON_CRYSTAL, 3059, -2.2F);

    // ========== 五、扩展兵器（2024 补充：掉落 / 条件获得，不只是合成）==========

    /** 16. 斩马刀 / Horse-Cleaver：180（合成：环首刀 + 精钢×3） */
    public static final RegistryObject<Item> ZHANMA_DAO =
            sword("zhanma_dao", DynastyTiers.OFFICIAL_SILVER, 189, -2.4F);

    /** 17. 鱼肠剑 / Yuchang Dagger：200、攻速极快（刺客稀有掉落） */
    public static final RegistryObject<Item> YUCHANG_DAGGER =
            sword("yuchang_dagger", DynastyTiers.BRONZE, 177, -1.2F);

    /** 18. 青釭剑 / Qinggang Sword：600（击败宦官首脑必掉） */
    public static final RegistryObject<Item> QINGGANG_SWORD =
            sword("qinggang_sword", DynastyTiers.JADE, 529, -2.0F);

    /** 19. 御赐金锏 / Gilded Mace：600（官阶到尚书·第 12 阶，朝廷御赐） */
    public static final RegistryObject<Item> GILDED_MACE =
            sword("gilded_mace", DynastyTiers.JADE, 729, -2.6F);

    /** 20. 倚天剑 / Yitian Sword：800（击败叛将必掉） */
    public static final RegistryObject<Item> YITIAN_SWORD =
            sword("yitian_sword", DynastyTiers.JADE, 729, -2.0F);

    /** 21. 龙胆亮银枪 / Dragon Spear：1100、攻击距离 +3（击败亡故始皇必掉） */
    public static final RegistryObject<Item> DRAGON_SPEAR = ITEMS.register("dragon_spear",
            () -> new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 959, -2.4F, new Item.Properties()));

    /** 22. 射日弓 / Sunbow：箭矢 ×4.5 + 280（白天击败凤凰后领悟） */
    public static final RegistryObject<Item> SUNBOW = ITEMS.register("sunbow",
            () -> new HuntingBowItem(4.5D, 280.0D, new Item.Properties().durability(9000)));

    /** 23. 七星宝刀 / Seven-Star Saber：1600（击败 5 种 Boss 后习得） */
    public static final RegistryObject<Item> SEVEN_STAR_SABER =
            sword("seven_star_saber", DynastyTiers.DRAGON_CRYSTAL, 1459, -2.2F);

    /** 24. 屠龙刀 / Dragon Slayer：2300（合成：龙晶剑 + 龙宫玉印 + 龙帝玉玺） */
    public static final RegistryObject<Item> DRAGON_SLAYER =
            sword("dragon_slayer", DynastyTiers.DRAGON_CRYSTAL, 2159, -2.4F);

    /** 25. 尚方宝剑 / Imperial Sword：2800（官阶到丞相·第 17 阶，御赐） */
    public static final RegistryObject<Item> SUPREME_SWORD =
            sword("supreme_sword", DynastyTiers.DRAGON_CRYSTAL, 2659, -2.0F);

    // ========== 六、弓·速射支线（长弓 → 神臂弓 → 落雁弓 → 天狼弓）==========
    // 弓系从长弓一分为二：这条是「速射」，另一条（龙吟弓 → 射日弓）是「穿透」。
    // The bow tree forks at the longbow: this is the rapid-fire branch.

    /** 26. 神臂弓 / Shenbi Bow：箭矢 ×2.8 + 70（长弓 + 精钢×3 + 丝绸×2 + 图纸） */
    public static final RegistryObject<Item> SHENBI_BOW = ITEMS.register("shenbi_bow",
            () -> new HuntingBowItem(2.8D, 70.0D, new Item.Properties().durability(3000)));

    /** 27. 落雁弓 / Luoyan Bow：箭矢 ×3.3 + 120（神臂弓 + 精钢×4 + 银锭×2 + 图纸） */
    public static final RegistryObject<Item> LUOYAN_BOW = ITEMS.register("luoyan_bow",
            () -> new HuntingBowItem(3.3D, 120.0D, new Item.Properties().durability(6000)));

    /** 28. 天狼弓 / Tianlang Bow：箭矢 ×3.8 + 200、穿透 1（落雁弓 + 龙晶×2 + 精钢×6） */
    public static final RegistryObject<Item> TIANLANG_BOW = ITEMS.register("tianlang_bow",
            () -> new DragonBowItem(3.8D, 200.0D, 1, 1, new Item.Properties().durability(7500)));
    /** 30. 龙渊剑 / Longyuan Sword：1800，特攻 +200 */
    public static final RegistryObject<Item> LONGYUAN_SWORD =
            ITEMS.register("longyuan_sword",
                    () -> new LongyuanSwordItem(DynastyTiers.DRAGON_CRYSTAL, 1659, -2.0F, new Item.Properties()));
    /** 31. 巨灵斧 / Juling Axe：2200，特攻 +300 */
    public static final RegistryObject<Item> JULING_AXE = ITEMS.register("juling_axe",
            () -> new AxeItem(DynastyTiers.DRAGON_CRYSTAL, 2059, -3.0F, new Item.Properties()));
    /** 32. 青龙偃月刀 / Qinglong Guandao：2600，特攻 +350 */
    public static final RegistryObject<Item> QINGLONG_DAO =
            sword("qinglong_dao", DynastyTiers.DRAGON_CRYSTAL, 2459, -2.4F);
    /** 33. 霸王枪 / Overlord Spear：3000，特攻 +400（长柄，攻击距离 +3）*/
    public static final RegistryObject<Item> BAWANG_SPEAR = ITEMS.register("bawang_spear",
            () -> new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 2859, -2.4F, new Item.Properties()));
    /** 34. 后羿弓 / Houyi Bow：箭矢 ×4.0 + 300（毕业弓） */
    public static final RegistryObject<Item> HOUYI_BOW = ITEMS.register("houyi_bow",
            () -> new HouyiBowItem(new Item.Properties().durability(12000)));
    /** 35. 雷霆锤 / Thunder Hammer：3300，特攻 +450 */
    public static final RegistryObject<Item> LEITING_HAMMER = ITEMS.register("leiting_hammer",
            () -> new AxeItem(DynastyTiers.DRAGON_CRYSTAL, 3159, -3.1F, new Item.Properties()));
    /** 36. 太乙拂尘 / Taiyi Whisk：3600，特攻 +500（长柄，攻击距离 +3）*/
    public static final RegistryObject<Item> TAIYI_WHISK = ITEMS.register("taiyi_whisk",
            () -> new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 3459, -2.2F, new Item.Properties()));
    /** 37. 玄武盾刀 / Xuanwu Blade：4000，特攻 +550 */
    public static final RegistryObject<Item> XUANWU_BLADE =
            sword("xuanwu_blade", DynastyTiers.DRAGON_CRYSTAL, 3859, -2.6F);
    /** 38. 朱雀羽扇 / Zhuque Fan：4400，特攻 +600 */
    public static final RegistryObject<Item> ZHUQUE_FAN =
            sword("zhuque_fan", DynastyTiers.DRAGON_CRYSTAL, 4259, -2.0F);
    /** 39. 混元珠杖 / Hunyuan Staff：5000，特攻 +800（长柄，攻击距离 +3）*/
    public static final RegistryObject<Item> HUNYUAN_STAFF = ITEMS.register("hunyuan_staff",
            () -> new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 4859, -2.4F, new Item.Properties()));

    // ========== 六、第三十二轮的 6 把帝兵（材料 / 贴图 / 配方见 tools/art/gen_weapons4.py）==========

    /** 40. 麒麟战斧 / Qilin War Axe：2000，特攻 +250 */
    public static final RegistryObject<Item> QILIN_WAR_AXE = ITEMS.register("qilin_war_axe",
            () -> new AxeItem(DynastyTiers.DRAGON_CRYSTAL, 1859, -2.9F, new Item.Properties()));
    /** 41. 太乙法剑 / Taiyi Sword：2300，特攻 +300 */
    public static final RegistryObject<Item> TAIYI_SWORD =
            sword("taiyi_sword", DynastyTiers.DRAGON_CRYSTAL, 2159, -2.2F);
    /** 42. 白虎戟 / White Tiger Glaive：2600，特攻 +330（长柄，攻击距离 +3）*/
    public static final RegistryObject<Item> BAIHU_GLAIVE = ITEMS.register("baihu_glaive",
            () -> new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 2459, -2.8F, new Item.Properties()));
    /** 43. 雷霆枪 / Thunder Spear：2900，特攻 +360（长柄，攻击距离 +3）*/
    public static final RegistryObject<Item> THUNDER_SPEAR = ITEMS.register("thunder_spear",
            () -> new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 2759, -2.6F, new Item.Properties()));
    /** 44. 紫微刀 / Ziwei Saber：3200，特攻 +400 */
    public static final RegistryObject<Item> ZIWEI_SABER =
            sword("ziwei_saber", DynastyTiers.DRAGON_CRYSTAL, 3059, -2.4F);
    /** 45. 朱雀弓 / Vermilion Bow：箭矢 ×4.0 + 300、穿透 2（特攻 +300） */
    public static final RegistryObject<Item> ZHUQUE_BOW = ITEMS.register("zhuque_bow",
            () -> new DragonBowItem(4.0D, 300.0D, 2, 4, new Item.Properties().durability(9000)));
}
