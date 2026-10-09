package com.dynasty;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.items.IItemHandlerModifiable;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/** Event-level integration tests: real registered items, real Curios when installed, actual world LOS. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class SchoolCombatGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void refinementTooltipShowsOnlyRank(GameTestHelper h) {
        if(Boolean.getBoolean("dynasty.externalQolQa")) {
            h.assertTrue(net.minecraftforge.fml.ModList.get().isLoaded("ftbultimine"),"FTB Ultimine loaded");
            h.assertTrue(net.minecraftforge.fml.ModList.get().isLoaded("worldedit"),"WorldEdit loaded");
        }
        ItemStack stack=new ItemStack(accessory("wanjun_ring"));
        stack.getOrCreateTag().putInt(DynastyAccessoryRefining.KEY,5);
        var brief=new ArrayList<net.minecraft.network.chat.Component>();
        var detail=new ArrayList<net.minecraft.network.chat.Component>();
        DynastyAccessoryRefining.tooltip(stack,brief,detail);
        h.assertTrue(brief.size()==1 && brief.get(0).getString().equals("淬炼 +5"),"Only refinement rank is shown");
        h.assertTrue(detail.isEmpty(),"No cost or duplicate damage lines on the item");
        h.assertTrue(DynastyAccessoryRefining.materialCost(4)==2 && DynastyAccessoryRefining.xpCost(4)==6,"+4 to +5 costs two jade and six XP levels");
        h.succeed();
    }
    public static final class SyntheticObserver {
        final UUID victim;
        int count;
        float amount;
        float primaryIncoming;
        boolean playerSource;
        SyntheticObserver(LivingEntity victim) { this.victim = victim.getUUID(); }
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority = net.minecraftforge.eventbus.api.EventPriority.HIGHEST)
        public void original(LivingHurtEvent event) {
            if (event.getEntity().getUUID().equals(victim) && !DynastyTrinketOnHit.isSyntheticDamage())
                primaryIncoming = event.getAmount();
        }
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority = net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public void observe(LivingHurtEvent event) {
            if (event.getEntity().getUUID().equals(victim) && DynastyTrinketOnHit.isSyntheticDamage()) {
                count++;
                amount = event.getAmount();
                playerSource = event.getSource().is(net.minecraft.world.damagesource.DamageTypes.PLAYER_ATTACK)
                        && event.getSource().getEntity() instanceof net.minecraft.world.entity.player.Player;
            }
        }
    }
    private static final class Fighter extends FakePlayer {
        float strength = 1F;
        Fighter(GameTestHelper h) {
            super(h.getLevel(), new GameProfile(UUID.randomUUID(), "school-test"));
            setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4, 2, 4))));
            setNoGravity(true);
            h.getLevel().addNewPlayer(this);
        }
        // Controlled pre-attack cooldown fixture; production captures this before vanilla resets it.
        @Override public float getAttackStrengthScale(float partial) { return strength; }
    }
    private static Fighter fighter(GameTestHelper h, Item item) {
        Fighter player = new Fighter(h);
        player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(item));
        return player;
    }
    private static LivingEntity enemy(GameTestHelper h, int x, int z) {
        var mob = h.spawn(EntityType.ZOMBIE, x, 2, z);
        mob.setNoAi(true);
        mob.setNoGravity(true);
        return mob;
    }
    private static LivingHurtEvent hit(net.minecraft.world.entity.player.Player player, LivingEntity target, float amount) {
        DynastySchoolCombat.attack(new AttackEntityEvent(player, target));
        var event = new LivingHurtEvent(target, player.damageSources().playerAttack(player), amount);
        DynastySchoolCombat.hurt(event);
        return event;
    }
    private static void close(Fighter player) {
        DynastySchoolCombat.forget(player);
        DynastyTrinkets.forget(player);
        player.discard();
    }
    private static Item accessory(String id) { return ForgeRegistries.ITEMS.getValue(new ResourceLocation(Dynasty.MODID, id)); }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 60)
    public static void newAccessoriesAreRealPassivesWithTypedDamageAndRemoval(GameTestHelper h) {
        Fighter p=fighter(h,net.minecraft.world.item.Items.IRON_SWORD);
        try {
            var target=enemy(h,5,5);
            String[] ids={"pojun_ring","wuqu_sword_knot","baizhan_ring","qixing_sword_knot",
                "xuanjia_clasp","shanyue_bracelet","beichen_heartguard","xuanyue_armlet",
                "yanling_thumbring","shenji_quiver","guanri_thumbring","zhuiri_quiver",
                "lingwen_pendant","leibu_seal","ziwei_talisman_chain","taiqing_talisman_case",
                "wanjun_ring","tianheng_sword_knot","zhenhai_heartguard","buzhou_armlet",
                "sheyue_thumbring","jinwu_quiver","sanqing_talisman_chain","yuxu_talisman_case"};
            String[] slots={"ring","belt","ring","belt","body","bracelet","body","bracelet",
                "ring","back","ring","back","necklace","charm","necklace","charm",
                "ring","belt","body","bracelet","ring","back","necklace","charm"};
            for(int i=0;i<ids.length;i++) {
                ItemStack stack=new ItemStack(accessory(ids[i]));
                h.assertTrue(!stack.isEmpty(),"Accessory registered: "+ids[i]);
                p.getInventory().setItem(9,stack); DynastyTrinkets.forget(p);
                h.assertTrue(DynastyTrinkets.activeIds(p).contains(ids[i])==!DynastyCuriosSetup.isLoaded(),"Inventory cannot impersonate Curios");
                p.getInventory().setItem(9,ItemStack.EMPTY); equip(p,slots[i],stack);
                var data=DynastyAccessoryData.get(ids[i]);
                h.assertTrue(data!=null&&DynastySchoolAccessories.count(DynastyTrinkets.activeIds(p),data.school())==1,"New accessory selects its school");
                p.getAttribute(Attributes.ARMOR_TOUGHNESS).setBaseValue(20);
                var event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
                DynastySchoolProgression.onHurt(event);
                double expected=switch(data.kind()) {case "melee" -> data.amount(); case "toughness" -> .12;default -> 0;};
                h.assertTrue(Math.abs(event.getAmount()-100*(1+expected))<.001,"Only melee bonuses affect an ordinary sword: "+ids[i]);
                Arrow arrow=new Arrow(h.getLevel(),p);
                event=new LivingHurtEvent(target,p.damageSources().arrow(arrow,p),100);
                DynastySchoolProgression.onHurt(event);
                expected=data.kind().equals("arrow")?data.amount():0;
                h.assertTrue(Math.abs(event.getAmount()-100*(1+expected))<.001,"Only owned arrow bonuses affect arrow damage: "+ids[i]);
                p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.CHILING_BRUSH.get()));
                event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
                DynastySchoolProgression.onHurt(event);
                expected=switch(data.kind()) {case "melee","edict" -> data.amount();case "toughness" -> .12;default -> 0;};
                h.assertTrue(Math.abs(event.getAmount()-100*(1+expected))<.001,"Ritual brush accepts edict and melee bonus once: "+ids[i]);
                event=new LivingHurtEvent(target,p.damageSources().thorns(p),100);
                DynastySchoolProgression.onHurt(event);
                h.assertTrue(event.getAmount()==100,"No accidental thorns scaling");
                p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(net.minecraft.world.item.Items.IRON_SWORD));
                equip(p,slots[i],ItemStack.EMPTY);
                event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
                DynastySchoolProgression.onHurt(event);
                h.assertTrue(event.getAmount()==100,"Unequipping removes damage bonus: "+ids[i]);
                h.assertTrue(h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty",ids[i])).isPresent(),"Recipe loaded: "+ids[i]);
            }
            h.assertTrue(Math.abs(DynastySchoolAccessories.bonus(java.util.Set.of("pojun_ring","baizhan_ring"),true,false,false,0)-.4)<1e-9,"Bonuses add, do not multiply");
            h.assertTrue(DynastySchoolAccessories.bonus(java.util.Set.of("xuanyue_armlet"),true,false,false,10000)==.6,"Toughness conversion capped at 60%");
            DynastyTrinkets.applySpecAttr(p,"xuanyue_armlet",0,12,30);
            h.assertTrue(p.getAttributeValue(Attributes.ARMOR_TOUGHNESS)==50,"Toughness stat really applies");
            DynastyTrinkets.clearAttrs(p,"xuanyue_armlet");
            h.assertTrue(p.getAttributeValue(Attributes.ARMOR_TOUGHNESS)==20,"Toughness modifier removable without residue");
        } finally {close(p);}
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void accessoryRefiningUsesRealAnvilAndPreservesInvestment(GameTestHelper h) {
        Fighter p=fighter(h,net.minecraft.world.item.Items.IRON_SWORD);
        try {
            ItemStack base=new ItemStack(accessory("baizhan_ring"));
            base.getOrCreateTag().putInt(DynastyAccessoryRefining.KEY,24);
            base.getOrCreateTag().putString("foreign_data","keep-me");
            base.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING,2);
            base.setHoverName(net.minecraft.network.chat.Component.literal("旧日战戒"));
            var menu=new net.minecraft.world.inventory.AnvilMenu(0,p.getInventory());
            menu.getSlot(0).set(base);
            menu.getSlot(1).set(new ItemStack(accessory("dragon_crystal"),16));
            menu.createResult();
            h.assertTrue(DynastyAccessoryRefining.level(menu.getSlot(2).getItem())==25,"Real anvil produces rank 25");
            h.assertTrue(DynastyAccessoryRefining.level(base)==24 && menu.getSlot(1).getItem().getCount()==16,"Preview consumes nothing");
            p.experienceLevel=0;
            h.assertTrue(!menu.getSlot(2).mayPickup(p),"Insufficient XP cannot take result");
            p.experienceLevel=50;
            ItemStack refined=menu.getSlot(2).remove(1); menu.getSlot(2).onTake(p,refined);
            h.assertTrue(p.experienceLevel==24 && menu.getSlot(1).getItem().getCount()==9 && menu.getSlot(0).getItem().isEmpty(),"Taking consumes exact 26 levels and 7 crystals");
            h.assertTrue(refined.isEnchanted() && refined.getHoverName().getString().equals("旧日战戒") && refined.getTag().getString("foreign_data").equals("keep-me"),"All foreign NBT preserved");
            var recipe=(net.minecraft.world.item.crafting.SmithingRecipe)h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","wanjun_ring")).orElseThrow();
            var input=new net.minecraft.world.SimpleContainer(new ItemStack(accessory("blueprint")),refined,new ItemStack(accessory("xuantian_jade")));
            h.assertTrue(recipe.matches(input,h.getLevel()),"Third tier smithing accepts actual predecessor");
            ItemStack evolved=recipe.assemble(input,h.getLevel().registryAccess());
            h.assertTrue(evolved.is(accessory("wanjun_ring")) && DynastyAccessoryRefining.level(evolved)==25 && evolved.isEnchanted() && evolved.getTag().getString("foreign_data").equals("keep-me"),"Evolution keeps refinement and foreign NBT");
            menu.getSlot(0).set(evolved); menu.getSlot(1).set(new ItemStack(accessory("jade"),64));menu.createResult();
            h.assertTrue(menu.getSlot(2).getItem().isEmpty(),"Wrong tier material cannot refine");
            menu.getSlot(1).set(new ItemStack(accessory("xuantian_jade"),1));menu.createResult();
            h.assertTrue(menu.getSlot(2).getItem().isEmpty(),"Insufficient material cannot refine");
            evolved.getOrCreateTag().putInt(DynastyAccessoryRefining.KEY,100);
            menu.getSlot(0).set(evolved);menu.getSlot(1).set(new ItemStack(accessory("sky_token"),64));menu.createResult();
            p.experienceLevel=40;
            h.assertTrue(DynastyAccessoryRefining.level(menu.getSlot(2).getItem())==101 && menu.getSlot(2).mayPickup(p),"Past rank100 works in survival, not too expensive");
            h.assertTrue(DynastyAccessoryRefining.materialCost(Integer.MAX_VALUE)==64 && DynastyAccessoryRefining.xpCost(Integer.MAX_VALUE)==39,"Cost arithmetic cannot overflow");
        } finally {close(p);}
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void refinedAccessoryRequiresEquipmentAndCorrectDamage(GameTestHelper h) {
        // Forge intentionally rejects advancement awards to FakePlayer.
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"refining-test"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),
            new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(net.minecraft.world.item.Items.IRON_SWORD));
        h.getLevel().addNewPlayer(p);
        try {
            ItemStack ring=new ItemStack(accessory("wanjun_ring"));
            ring.getOrCreateTag().putInt(DynastyAccessoryRefining.KEY,25);
            equip(p,"ring",ring);
            h.assertTrue(Math.abs(DynastyAccessoryRefining.damageBonus(p,p.damageSources().playerAttack(p))-.2)<.0001,"Rank25 adds 20 percent melee");
            Arrow arrow=new Arrow(h.getLevel(),p);
            h.assertTrue(DynastyAccessoryRefining.damageBonus(p,p.damageSources().arrow(arrow,p))==0,"Melee refinement cannot buff arrows");
            h.assertTrue(DynastyAccessoryRefining.damageBonus(p,p.damageSources().thorns(p))==0,"No thorn scaling");
            p.tickCount=20;
            DynastyAccessoryRefining.milestones(new TickEvent.PlayerTickEvent(TickEvent.Phase.END,p));
            var adv=p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty","refine_sword_15"));
            h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Actual rank awards lower milestone");
            adv=p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty","refine_sword_30"));
            h.assertTrue(!p.getAdvancements().getOrStartProgress(adv).isDone(),"Cannot award unearned milestone");
            equip(p,"ring",ItemStack.EMPTY);
            h.assertTrue(DynastyAccessoryRefining.damageBonus(p,p.damageSources().playerAttack(p))==0,"Removal clears bonus immediately");
            ItemStack ranged=new ItemStack(accessory("sheyue_thumbring"));ranged.getOrCreateTag().putInt(DynastyAccessoryRefining.KEY,25);equip(p,"ring",ranged);
            h.assertTrue(Math.abs(DynastyAccessoryRefining.damageBonus(p,p.damageSources().arrow(arrow,p))-.2)<.0001,"Ranged refinement buffs owned arrows");
            equip(p,"ring",ItemStack.EMPTY);
            ItemStack ritual=new ItemStack(accessory("sanqing_talisman_chain"));ritual.getOrCreateTag().putInt(DynastyAccessoryRefining.KEY,25);equip(p,"necklace",ritual);
            h.assertTrue(DynastyAccessoryRefining.damageBonus(p,p.damageSources().playerAttack(p))==0,"Edict refinement not ordinary sword");
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.CHILING_BRUSH.get()));
            h.assertTrue(Math.abs(DynastyAccessoryRefining.damageBonus(p,p.damageSources().playerAttack(p))-.2)<.0001,"Edict refinement buffs ritual weapons");
        } finally {DynastySchoolCombat.forget(p);DynastyTrinkets.forget(p);p.discard();}
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void branchPassivesAndRecipesWorkWithoutActiveInputs(GameTestHelper h) {
        Fighter p=fighter(h,DynastyWeapons.BEICHEN_SPEAR.get());
        try {
            LivingEntity target=enemy(h,5,5);
            p.getAttribute(Attributes.ARMOR_TOUGHNESS).setBaseValue(50);
            var event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
            DynastyBranchWeapons.onHurt(event);
            h.assertTrue(Math.abs(event.getAmount()-140)<.001,"Spear converts toughness to damage");
            h.assertTrue(DynastyBranchWeapons.bonus("beichen_spear",1000,true)==.6F,"Conversion is bounded");
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.CHENGYING_SWORD.get()));
            event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
            DynastyBranchWeapons.onHurt(event);
            h.assertTrue(Math.abs(event.getAmount()-120)<.001,"Healthy-target sword passive works");
            target.setHealth(target.getMaxHealth()/2);
            event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
            DynastyBranchWeapons.onHurt(event);
            h.assertTrue(event.getAmount()==100,"Sword does not keep healthy bonus below threshold");
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.LEIFU_STAFF.get()));
            event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
            DynastyBranchWeapons.onHurt(event);
            h.assertTrue(Math.abs(event.getAmount()-115)<.001&&target.getEffect(MobEffects.MOVEMENT_SLOWDOWN).getDuration()==60,
                    "Staff passively damages and slows without a keybind");
            Arrow original=new Arrow(h.getLevel(),p);original.setDeltaMovement(1,.2,3);
            var wind=((net.minecraft.world.item.BowItem)DynastyWeapons.FENGLING_BOW.get()).customArrow(original);
            h.assertTrue(wind==original&&wind.getDeltaMovement().equals(new Vec3(1,.2,3))&&wind.getPierceLevel()==1,
                    "Wind bow preserves vanilla arrow identity and trajectory");
            String[][] recipes={{"beichen_spear","zhenyue_blade","refined_steel","juque_sword","dragon_crystal"},
                    {"chengying_sword","liuyun_sword","jade","sword_dragon_crystal","dragon_crystal"},
                    {"fengling_bow","zhuxing_bow","refined_steel","shenbi_bow","refined_steel"},
                    {"leifu_staff","chiling_brush","jade","taiyi_sword","dragon_crystal"}};
            for(String[] spec:recipes)for(int step=0;step<2;step++) {
                ItemStack trained=new ItemStack(accessory(step==0?spec[1]:spec[0]));
                trained.getOrCreateTag().putInt("fixture_growth",25);
                trained.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING,2);
                var input=new net.minecraft.world.SimpleContainer(new ItemStack(DynastyRelics.BLUEPRINT.get()),trained,
                        new ItemStack(accessory(step==0?spec[2]:spec[4])));
                var recipe=(net.minecraft.world.item.crafting.SmithingRecipe)h.getLevel().getRecipeManager()
                        .byKey(new ResourceLocation("dynasty","branch_"+spec[0]+(step==0?"":"_advance"))).orElseThrow();
                h.assertTrue(recipe.matches(input,h.getLevel()),"Branch recipe inputs match");
                var output=recipe.assemble(input,h.getLevel().registryAccess());
                h.assertTrue(output.is(accessory(step==0?spec[0]:spec[3]))&&output.getTag().equals(trained.getTag()),
                        "Every branch evolution preserves weapon investment");
            }
        } finally {close(p);}
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolMasteryTracksKillsAndScalesWithoutChangingTheWeapon(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.ZHENYUE_BLADE.get());
        try {
            LivingEntity target = enemy(h, 5, 4);
            h.assertTrue(DynastySchoolProgression.practicePoints(20) == 1
                    && DynastySchoolProgression.practicePoints(800) == 8,
                    "High-health enemies must award more practice, but points have a cap");
            h.assertTrue(DynastySchoolProgression.requiredForNext(0) == 8
                    && DynastySchoolProgression.requiredForNext(10) > DynastySchoolProgression.requiredForNext(1),
                    "Later ranks must take progressively more practice");
            for (int i = 0; i < 8; i++) {
                LivingHurtEvent swing = hit(p, target, 100);
                DynastySchoolProgression.onHurt(swing);
                h.assertTrue(swing.getAmount() == 100, "Rank zero must not alter unadorned blade damage");
                LivingEntity victim = enemy(h, 5, 5);
                DynastySchoolProgression.onKill(new net.minecraftforge.event.entity.living.LivingDeathEvent(victim, swing.getSource()));
                DynastySchoolProgression.onKill(new net.minecraftforge.event.entity.living.LivingDeathEvent(victim, swing.getSource()));
            }
            h.assertTrue(DynastySchoolProgression.rank(p, "guard") == 1
                    && DynastySchoolProgression.rank(p, "sword") == 0,
                    "Only the used school earns permanent mastery");
            LivingHurtEvent stronger = hit(p, target, 100);
            DynastySchoolProgression.onHurt(stronger);
            h.assertTrue(Math.abs(stronger.getAmount() - 114) < .001,
                    "Rank one applies the documented 1.14 multiplier to the existing damage event");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void expandedEvolutionPreservesInvestment(GameTestHelper h) {
        String[][] paths={
                {"guard_pojun","juque_sword","pojun_axe","rebel_head"},
                {"guard_juling","pojun_axe","juling_axe","emperor_bone"},
                {"guard_leiting","juling_axe","leiting_hammer","sky_token"},
                {"sword_seven_star","sword_dragon_crystal","seven_star_saber","jade"},
                {"sword_dragon_slayer","seven_star_saber","dragon_slayer","sea_token"},
                {"sword_supreme","dragon_slayer","supreme_sword","dragon_emperor_seal"},
                {"archer_luoyan","shenbi_bow","luoyan_bow","jade"},
                {"archer_tianlang","luoyan_bow","tianlang_bow","dragon_crystal"},
                {"archer_zhuque","tianlang_bow","zhuque_bow","phoenix_feather"},
                {"talisman_zhuque_fan","taiyi_whisk","zhuque_fan","phoenix_feather"},
                {"talisman_hunyuan_fan","zhuque_fan","hunyuan_staff","dragon_emperor_seal"}};
        int count=0;
        for (String[] path : paths) {
            var recipe=(net.minecraft.world.item.crafting.SmithingRecipe)h.getLevel().getRecipeManager()
                    .byKey(new ResourceLocation("dynasty","evolution_path_"+path[0])).orElseThrow();
            ItemStack trained=new ItemStack(accessory(path[1]));
            h.assertTrue(DynastyWeaponProgression.eligible(trained),"Evolution base is a real weapon");
            trained.getOrCreateTagElement(DynastyWeaponProgression.KEY).putInt("level",7);
            trained.getOrCreateTagElement(DynastyWeaponProgression.KEY).putLong("xp",19);
            trained.getOrCreateTag().putInt(DynastyAccessoryRefining.KEY,30);
            trained.setHoverName(net.minecraft.network.chat.Component.literal("百战旧兵"));
            trained.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING,3);
            var input=new net.minecraft.world.SimpleContainer(new ItemStack(DynastyRelics.BLUEPRINT.get()),
                    trained,new ItemStack(accessory(path[3])));
            h.assertTrue(recipe.matches(input,h.getLevel()),"Published evolution inputs match");
            ItemStack result=recipe.assemble(input,h.getLevel().registryAccess());
            h.assertTrue(DynastyWeaponProgression.eligible(result)&&result.is(accessory(path[2])),"Evolution yields the specified usable weapon");
            h.assertTrue(trained.getTag().equals(result.getTag()),"All level, XP, refinement, name and enchantment data survives");
            input.setItem(2,new ItemStack(net.minecraft.world.item.Items.DIRT));
            h.assertTrue(!recipe.matches(input,h.getLevel()),"Wrong materials never match");
            count++;
        }
        h.assertTrue(count==11,"All eleven expanded weapon evolutions are registered");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void weaponKillLevelAndSmithingPreserveInvestment(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.LIUYUN_SWORD.get());
        try {
            for (int i=0; i<10; i++) {
                LivingEntity target=enemy(h,5,5);
                DynastySchoolProgression.onKill(new net.minecraftforge.event.entity.living.LivingDeathEvent(
                        target,p.damageSources().playerAttack(p)));
            }
            ItemStack trained=p.getMainHandItem();
            h.assertTrue(DynastyWeaponProgression.level(trained)==2, "Ten ordinary kills produce weapon level 2");
            trained.setHoverName(net.minecraft.network.chat.Component.literal("My trained blade"));
            trained.enchant(net.minecraft.world.item.enchantment.Enchantments.SHARPNESS,2);
            var container=new net.minecraft.world.SimpleContainer(
                    new ItemStack(DynastyRelics.BLUEPRINT.get()),trained,new ItemStack(DynastyItems.DRAGON_CRYSTAL.get()));
            var recipe=h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","evolve_sword_1")).orElseThrow();
            var smith=(net.minecraft.world.item.crafting.SmithingRecipe)recipe;
            h.assertTrue(smith.matches(container,h.getLevel()),"Registered evolution accepts the documented materials");
            ItemStack evolved=smith.assemble(container,h.getLevel().registryAccess());
            h.assertTrue(evolved.is(DynastyGear.SWORD_DRAGON_CRYSTAL.get()),"Evolution produces a different, stronger weapon");
            h.assertTrue(evolved.getTag().equals(trained.getTag()),"Smithing preserves all growth, names and enchantments");
            h.assertTrue(DynastyWeaponProgression.level(evolved)==2,"Level 2 remains level 2 after evolution");
            container.setItem(2,new ItemStack(net.minecraft.world.item.Items.DIRT));
            h.assertTrue(!smith.matches(container,h.getLevel()),"Wrong materials cannot evolve a weapon");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void arrowGrowthBelongsToFiringBowAfterSwap(GameTestHelper h) {
        Fighter p=fighter(h,DynastyWeapons.ZHUXING_BOW.get());
        try {
            ItemStack original=p.getMainHandItem();
            Arrow arrow=new Arrow(h.getLevel(),p);
            DynastyWeaponProgression.onArrow(new net.minecraftforge.event.entity.EntityJoinLevelEvent(arrow,h.getLevel()));
            p.getInventory().setItem(10,original);
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.HOUYI_BOW.get()));
            LivingEntity target=enemy(h,5,5);
            DynastySchoolProgression.onKill(new net.minecraftforge.event.entity.living.LivingDeathEvent(target,p.damageSources().arrow(arrow,p)));
            h.assertTrue(DynastyWeaponProgression.progress(original)==1,"Noncritical arrow kill rewards the firing bow");
            h.assertTrue(DynastyWeaponProgression.progress(p.getMainHandItem())==0,"Newly held bow gets no stolen XP");
        } finally { close(p); }
        h.succeed();

    }

    /** No Curios class references in the enclosing test class: standalone mod testing still boots. */
    static void equip(net.minecraft.world.entity.player.Player player, String slot, ItemStack stack) {
        if (!DynastyCuriosSetup.isLoaded()) player.getInventory().setItem(9, stack);
        else try {
            Class<?> api = Class.forName("top.theillusivec4.curios.api.CuriosApi");
            var lazy = (LazyOptional<?>) api.getMethod("getCuriosInventory", LivingEntity.class).invoke(null, player);
            Object handler = lazy.resolve().orElseThrow();
            Class<?> handlerApi = Class.forName("top.theillusivec4.curios.api.type.capability.ICuriosItemHandler");
            var optional = (Optional<?>) handlerApi.getMethod("getStacksHandler", String.class).invoke(handler, slot);
            Object slots = optional.orElseThrow();
            Class<?> stacksApi = Class.forName("top.theillusivec4.curios.api.type.inventory.ICurioStacksHandler");
            var inventory = (IItemHandlerModifiable) stacksApi.getMethod("getStacks").invoke(slots);
            inventory.setStackInSlot(0, stack);
        } catch (ReflectiveOperationException failure) { throw new IllegalStateException("Real Curios equipment fixture failed", failure); }
        DynastyTrinkets.forget(player); // model the next tick after equipment change, not an old same-tick cache
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolComboIsFullStrengthSingleTargetAndSourceBound(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.LIUYUN_SWORD.get());
        try {
            LivingEntity a = enemy(h, 5, 4), b = enemy(h, 5, 5);
            h.assertTrue(hit(p, a, 100).getAmount() == 100, "First hit must not gain a bonus");
            h.assertTrue(hit(p, a, 100).getAmount() == 100, "Second hit must not gain a bonus");
            var sweep = new LivingHurtEvent(b, p.damageSources().playerAttack(p), 100);
            DynastySchoolCombat.hurt(sweep);
            h.assertTrue(sweep.getAmount() == 100, "Swept/synthetic damage must not consume explicit-target combo");
            h.assertTrue(hit(p, a, 100).getAmount() == 150, "Third fully charged hit must gain exactly 50 percent");
            h.assertTrue(a.getHealth() == a.getMaxHealth(), "School hook must not recursively hurt entities");
            hit(p, a, 100); hit(p, b, 100);
            h.assertTrue(hit(p, a, 100).getAmount() == 100, "Target switch must reset combo");
            p.strength = .5F; hit(p, a, 100); p.strength = 1F;
            h.assertTrue(hit(p, a, 100).getAmount() == 100 && DynastySchoolCombat.state(p).combo == 1, "Weak attack must reset combo");
            var s = DynastySchoolCombat.state(p); s.combo = 2; s.comboTick = DynastySchoolCombat.now(p) - 61;
            h.assertTrue(hit(p, a, 100).getAmount() == 100, "Expired three-second chain must restart");
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.TIE_JIAN.get()));
            hit(p, a, 100);
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.LIUYUN_SWORD.get()));
            h.assertTrue(hit(p, a, 100).getAmount() == 100 && s.combo == 1, "Weapon swap must reset combo");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolGuardOneCounterAndCooldown(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.ZHENYUE_BLADE.get());
        try {
            LivingEntity target = enemy(h, 5, 4);
            p.startUsingItem(InteractionHand.MAIN_HAND);
            var block = new ShieldBlockEvent(p, p.damageSources().mobAttack(target), 20);
            DynastySchoolCombat.block(block);
            h.assertTrue(block.getBlockedDamage() == 10, "Guard blocks half, never complete invulnerability");
            h.assertTrue(DynastySchoolCombat.state(p).counterUntil == DynastySchoolCombat.now(p) + 60, "Base counter lasts exactly 60 ticks");
            DynastySchoolCombat.block(new ShieldBlockEvent(p, p.damageSources().mobAttack(target), 20));
            p.releaseUsingItem();
            h.assertTrue(p.getCooldowns().isOnCooldown(DynastyWeapons.ZHENYUE_BLADE.get()), "Release must start guard cooldown");
            h.assertTrue(Math.abs(hit(p, target, 100).getAmount() - 135) < .001, "Counter bonus must be 35 percent");
            h.assertTrue(hit(p, target, 100).getAmount() == 100, "Repeated blocks must never stack multiple counters");
            var s = DynastySchoolCombat.state(p); s.counterUntil = DynastySchoolCombat.now(p) - 1;
            h.assertTrue(hit(p, target, 100).getAmount() == 100, "Expired counter must not trigger");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolArrowMarkBelongsToFiringWeaponAndShooter(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.ZHUXING_BOW.get());
        try {
            LivingEntity target = enemy(h, 5, 4), other = enemy(h, 5, 5);
            var bow = (DynastySchoolWeapons.StarBow) DynastyWeapons.ZHUXING_BOW.get();
            Arrow first = new Arrow(h.getLevel(), p); bow.customArrow(first); first.setCritArrow(true);
            var one = new LivingHurtEvent(target, p.damageSources().arrow(first, p), 100); DynastySchoolCombat.hurt(one);
            h.assertTrue(one.getAmount() == 100, "First fully drawn arrow only marks");
            var replay = new LivingHurtEvent(target, p.damageSources().arrow(first, p), 100); DynastySchoolCombat.hurt(replay);
            h.assertTrue(replay.getAmount() == 100, "One arrow cannot consume its own mark on repeated/piercing hits");
            Arrow second = new Arrow(h.getLevel(), p); bow.customArrow(second); second.setCritArrow(true);
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.TIANZI_SWORD.get()));
            var two = new LivingHurtEvent(target, p.damageSources().arrow(second, p), 100);
            h.assertTrue(DynastySchoolCombat.firingWeapon(two.getSource(), p.getMainHandItem()).is(bow), "In-flight arrow keeps bow, not currently held imperial sword");
            DynastySchoolCombat.hurt(two);
            h.assertTrue(two.getAmount() == 140, "Second charged arrow consumes mark for exactly 40 percent");
            Arrow ordinary = new Arrow(h.getLevel(), p); ordinary.setCritArrow(true);
            var normal = new LivingHurtEvent(other, p.damageSources().arrow(ordinary, p), 100); DynastySchoolCombat.hurt(normal);
            h.assertTrue(normal.getAmount() == 100 && DynastySchoolCombat.state(p).marked == null, "Ordinary arrows cannot create school marks");
            Arrow weak = new Arrow(h.getLevel(), p); bow.customArrow(weak);
            var partial = new LivingHurtEvent(other, p.damageSources().arrow(weak, p), 100); DynastySchoolCombat.hurt(partial);
            h.assertTrue(DynastySchoolCombat.state(p).marked == null, "Partial draw cannot create marks");
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(bow));
            for (LivingEntity victim : List.of(target, other, target)) {
                Arrow a = new Arrow(h.getLevel(), p); bow.customArrow(a); a.setCritArrow(true);
                var damage = new LivingHurtEvent(victim, p.damageSources().arrow(a, p), 100); DynastySchoolCombat.hurt(damage);
                h.assertTrue(damage.getAmount() == 100, "Changing target replaces, never accumulates marks");
            }
            DynastySchoolCombat.state(p).markedTick = DynastySchoolCombat.now(p) - 161;
            Arrow expired = new Arrow(h.getLevel(), p); bow.customArrow(expired); expired.setCritArrow(true);
            var damage = new LivingHurtEvent(target, p.damageSources().arrow(expired, p), 100); DynastySchoolCombat.hurt(damage);
            h.assertTrue(damage.getAmount() == 100, "Expired mark cannot burst");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolEdictBoundedVisibleHostilesOnlyAndCooldown(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.CHILING_BRUSH.get());
        Fighter ally = fighter(h, DynastyWeapons.TIE_JIAN.get());
        try {
            List<LivingEntity> targets = new ArrayList<>();
            for (int i = 0; i < 11; i++) targets.add(enemy(h, 5 + i % 2, 3 + i % 3));
            var sheep = h.spawn(EntityType.SHEEP, 5, 2, 4); sheep.setNoAi(true);
            var hidden = enemy(h, 4, 7);
            // Full-height wall, not an AABB-only approximation to visibility.
            for (int x = 1; x <= 7; x++) for (int y = 1; y <= 5; y++) h.setBlock(new BlockPos(x, y, 6), Blocks.STONE);
            h.assertTrue(!p.hasLineOfSight(hidden), "Fixture wall must actually obstruct eyes");
            int affected = DynastySchoolCombat.startEdict(p);
            h.assertTrue(affected == 8, "Edict must affect exactly the nearest eight eligible enemies");
            h.assertTrue(targets.stream().filter(t -> t.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)).count() == 8, "CC target cap must be enforced");
            h.assertTrue(!hidden.hasEffect(MobEffects.MOVEMENT_SLOWDOWN), "No wall penetration");
            h.assertTrue(!sheep.hasEffect(MobEffects.MOVEMENT_SLOWDOWN) && !ally.hasEffect(MobEffects.MOVEMENT_SLOWDOWN), "No passive animals or players");
            h.assertTrue(DynastySchoolCombat.startEdict(p) == 0, "Repeated right-click during cooldown must do nothing");
        } finally { close(p); close(ally); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 80)
    public static void schoolEdictStandStillChargeCannotStackOrSurviveMovement(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.CHILING_BRUSH.get());
        try {
            LivingEntity target = enemy(h, 5, 4);
            equip(p, "back", new ItemStack(accessory("dingfeng_silk")));
            p.startUsingItem(InteractionHand.MAIN_HAND);
            DynastySchoolCombat.startEdict(p);
            var s = DynastySchoolCombat.state(p);
            DynastySchoolCombat.chargeEdict(p);
            h.assertTrue(s.edictUntil < 0, "Starting the cast cannot instantly grant charged damage");
            h.assertTrue(p.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE) >= .5, "Equipped silk only adds resistance while charging");
            p.setPos(p.position().add(.3, 0, 0)); DynastySchoolCombat.chargeEdict(p);
            h.assertTrue(s.chargeStart < 0 && s.edictUntil < 0, "Moving from cast origin cancels, not pauses charging");
            h.assertTrue(p.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE) < .5, "Canceled charge must remove transient resistance");
            p.getCooldowns().removeCooldown(DynastyWeapons.CHILING_BRUSH.get());
            p.startUsingItem(InteractionHand.MAIN_HAND); DynastySchoolCombat.startEdict(p);
            h.runAfterDelay(39, () -> {
                DynastySchoolCombat.chargeEdict(p);
                h.assertTrue(s.edictUntil < 0, "39 real game ticks may not complete a 40-tick charge");
            });
            h.runAfterDelay(41, () -> {
                try {
                    DynastySchoolCombat.chargeEdict(p);
                    h.assertTrue(s.edictUntil == DynastySchoolCombat.now(p) + 80 && !p.isUsingItem(), "Stationary 40 ticks grants one four-second charge and ends use");
                    h.assertTrue(p.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE) < .5, "Completed charge must remove resistance");
                    h.assertTrue(hit(p, target, 100).getAmount() == 150, "Prepared brush hit gets exactly 50 percent");
                    h.assertTrue(hit(p, target, 100).getAmount() == 100, "Prepared brush must be consumed once");
                    h.succeed();
                } finally { close(p); }
            });
        } catch (RuntimeException | Error failure) { close(p); throw failure; }
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolAccessoriesOnlyApplyInRealEquipmentSlots(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.ZHENYUE_BLADE.get());
        try {
            String[] ids = {"zhenguan_mirror", "huben_bracer", "liancheng_tassel", "tayun_pendant", "guanxing_pendant", "mingxian_ring", "sitian_seal", "dingfeng_silk"};
            String[] slots = {"body", "bracelet", "belt", "necklace", "necklace", "ring", "charm", "back"};
            for (int i = 0; i < ids.length; i++) {
                ItemStack stack = new ItemStack(accessory(ids[i]));
                p.getInventory().setItem(9, stack); DynastyTrinkets.forget(p);
                h.assertTrue(DynastySchoolCombat.has(p, ids[i]) == !DynastyCuriosSetup.isLoaded(), "Inventory cannot activate " + ids[i] + " when Curios is installed");
                p.getInventory().setItem(9, ItemStack.EMPTY); equip(p, slots[i], stack);
                h.assertTrue(DynastySchoolCombat.has(p, ids[i]), "Real equipped accessory must activate: " + ids[i]);
                equip(p, slots[i], ItemStack.EMPTY);
                h.assertTrue(!DynastySchoolCombat.has(p, ids[i]), "Removing accessory must deactivate: " + ids[i]);
            }
            equip(p, "body", new ItemStack(accessory("zhenguan_mirror")));
            p.startUsingItem(InteractionHand.MAIN_HAND);
            var target = enemy(h, 5, 4);
            DynastySchoolCombat.block(new ShieldBlockEvent(p, p.damageSources().mobAttack(target), 20));
            h.assertTrue(DynastySchoolCombat.state(p).counterUntil == DynastySchoolCombat.now(p) + 120, "Equipped mirror extends actual counter timer to six seconds");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolTrialsRequireRealMechanicAndCarryNoReward(GameTestHelper h) {
        // Forge PlayerAdvancements.award intentionally refuses FakePlayer. Use a real server player,
        // with a harmless disconnected packet queue and explicit pre-attack cooldown fixture.
        var p = new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(), h.getLevel(),
                new GameProfile(UUID.randomUUID(), "school-trial")) {
            @Override public float getAttackStrengthScale(float partial) { return 1F; }
        };
        p.connection = new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),
                new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND), p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4, 2, 4))));
        p.setNoGravity(true);
        p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.LIUYUN_SWORD.get()));
        h.getLevel().addNewPlayer(p);
        try {
            var advancement = h.getLevel().getServer().getAdvancements().getAdvancement(new ResourceLocation(Dynasty.MODID, "build_sword_trial"));
            h.assertTrue(advancement != null, "Trial advancement must be loaded");
            LivingEntity target = enemy(h, 5, 4);
            hit(p, target, 100); hit(p, target, 100);
            h.assertTrue(!p.getAdvancements().getOrStartProgress(advancement).isDone(), "Hits without a kill must not pass the first-kill trial");
            hit(p, target, 100);
            h.assertTrue(!p.getAdvancements().getOrStartProgress(advancement).isDone(), "A combo must not replace a kill");
            DynastySchoolProgression.onKill(new net.minecraftforge.event.entity.living.LivingDeathEvent(target, p.damageSources().playerAttack(p)));
            h.assertTrue(p.getAdvancements().getOrStartProgress(advancement).isDone(), "Killing an enemy grants the first-kill trial");
            var arrow = new Arrow(h.getLevel(), p); arrow.setCritArrow(true);
            var source = p.damageSources().arrow(arrow, p);
            h.assertTrue(DynastySchoolCombat.firingWeapon(source, p.getMainHandItem()).is(DynastyWeapons.LIUYUN_SWORD.get()), "Legacy untagged damage must preserve old weapon pipeline");
        } finally { DynastySchoolCombat.forget(p); DynastyTrinkets.forget(p); p.discard(); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolRealPlayerAttackAndGuardDamagePipeline(GameTestHelper h) {
        // Unlike event-unit fixtures, this uses unmodified Player.attack/hurt, cooldown reset and tick logic.
        var p = h.makeMockSurvivalPlayer();
        p.setNoGravity(true);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4, 2, 4))));
        p.setOnGround(true);
        try {
            LivingEntity target = enemy(h, 5, 4);
            target.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1024);
            target.getAttribute(Attributes.ARMOR).setBaseValue(0);
            target.setHealth(1024);
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.LIUYUN_SWORD.get()));
            float[] losses = new float[3];
            for (int n = 0; n < 3; n++) {
                for (int tick = 0; tick < 20; tick++) p.tick();
                p.setOnGround(true);
                p.setSprinting(false);
                target.invulnerableTime = 0;
                float before = target.getHealth();
                p.attack(target);
                losses[n] = before - target.getHealth();
                h.assertTrue(DynastySchoolCombat.state(p).combo == (n == 2 ? 0 : n + 1), "Real attack must retain pre-reset cooldown snapshot for hit " + n);
            }
            h.assertTrue(losses[0] > 0 && Math.abs(losses[1] - losses[0]) < .05 && Math.abs(losses[2] - losses[0] * 1.5F) < .05,
                    "Actual health losses must be base/base/150 percent: " + java.util.Arrays.toString(losses));
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.ZHENYUE_BLADE.get()));
            p.setYRot(-90); p.yRotO = -90;
            p.setHealth(p.getMaxHealth());
            p.startUsingItem(InteractionHand.MAIN_HAND);
            for (int tick = 0; tick < 6; tick++) p.tick();
            h.assertTrue(p.isBlocking(), "Real vanilla shield checks must accept the guard blade after the five-tick raise");
            p.invulnerableTime = 0;
            float before = p.getHealth();
            p.hurt(p.damageSources().mobAttack(target), 8);
            float frontalDamage = before - p.getHealth();
            h.assertTrue(DynastySchoolCombat.state(p).counterUntil >= DynastySchoolCombat.now(p), "Real ShieldBlockEvent must arm counter");
            var rear = enemy(h, 3, 4);
            p.invulnerableTime = 0;
            before = p.getHealth();
            p.hurt(p.damageSources().mobAttack(rear), 8);
            float rearDamage = before - p.getHealth();
            // Player.hurt difficulty-scales mob damage before ShieldBlockEvent (EASY: 8 -> 5).
            // Compare against the same real unblocked attack, not an assumed NORMAL-difficulty 8.
            h.assertTrue(frontalDamage > 0 && rearDamage > 0 && Math.abs(frontalDamage * 2 - rearDamage) < .01,
                    "Front must take exactly 50% of unblocked rear damage: front=" + frontalDamage + " rear=" + rearDamage);
            p.releaseUsingItem();
            h.assertTrue(p.getCooldowns().isOnCooldown(DynastyWeapons.ZHENYUE_BLADE.get()), "Actual release retains cooldown");
        } finally { DynastySchoolCombat.forget(p); DynastyTrinkets.forget(p); p.discard(); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolMainlineBossesAreEligibleButFriendlySoldiersAreNot(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.CHILING_BRUSH.get());
        try {
            for (String id : List.of("undead_first_emperor", "dragon_emperor", "rebel_general", "eunuch_mastermind", "nine_heaven_general", "dragon_king")) {
                var type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(Dynasty.MODID, id));
                var mob = (LivingEntity) type.create(h.getLevel());
                h.assertTrue(mob != null && DynastySchoolCombat.hostile(p, mob), "Mainline boss must implement hostile school targeting: " + id);
                h.assertTrue(DynastySchoolCombat.boss(mob), "Boss control duration must be reduced: " + id);
            }
            var type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(Dynasty.MODID, "imperial_soldier"));
            h.assertTrue(!DynastySchoolCombat.hostile(p, (LivingEntity) type.create(h.getLevel())), "Friendly recruited soldiers must not be school targets");
            h.assertTrue(SchoolCombatRules.edictDuration(true, false) == 20 && SchoolCombatRules.edictDuration(true, true) == 40,
                    "Boss CC duration must be capped even with seal");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolGuardStopAndHotbarSwapCannotBypassCooldown(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.ZHENYUE_BLADE.get());
        try {
            Item blade = DynastyWeapons.ZHENYUE_BLADE.get();
            p.startUsingItem(InteractionHand.MAIN_HAND);
            // Same stopUsingItem path used by the real hotbar/F-swap packet handler.
            p.stopUsingItem();
            h.assertTrue(p.getCooldowns().isOnCooldown(blade), "stopUsingItem must impose guard cooldown even without releaseUsing");
            for (int i = 0; i < 20; i++) p.getCooldowns().tick();
            float afterTwenty = p.getCooldowns().getCooldownPercent(blade, 0);
            p.stopUsingItem();
            h.assertTrue(afterTwenty == p.getCooldowns().getCooldownPercent(blade, 0), "Repeated stop must not refresh cooldown");
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.TIE_JIAN.get()));
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(blade));
            var use = blade.use(h.getLevel(), p, InteractionHand.MAIN_HAND);
            h.assertTrue(use.getResult() == net.minecraft.world.InteractionResult.FAIL, "Swapping away and back cannot re-enter guard during cooldown");
            for (int i = 0; i < 99; i++) p.getCooldowns().tick();
            h.assertTrue(p.getCooldowns().isOnCooldown(blade), "Cooldown must persist through tick 119");
            p.getCooldowns().tick();
            h.assertTrue(!p.getCooldowns().isOnCooldown(blade), "Cooldown must expire exactly at 120 ticks");
        } finally { close(p); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolRealTrinketExecuteCannotRecurseOrBorrowCounter(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.ZHENYUE_BLADE.get());
        LivingEntity target = enemy(h, 5, 4);
        target.getAttribute(Attributes.ARMOR).setBaseValue(0);
        target.setHealth(2);
        var observer = new SyntheticObserver(target);
        net.minecraftforge.common.MinecraftForge.EVENT_BUS.register(observer);
        try {
            equip(p, "charm", new ItemStack(accessory("bone_reaper_tally"))); // 100% execute below 20%, max HP <= 80
            var s = DynastySchoolCombat.state(p);
            s.held = "zhenyue_blade";
            s.counterUntil = DynastySchoolCombat.now(p) + 60;
            p.attack(target); // real Forge NORMAL trinket hook creates nested playerAttack damage
            h.assertTrue(observer.count == 1, "Execute must issue exactly one secondary event, never a recursive proc chain: " + observer.count);
            h.assertTrue(observer.playerSource, "Synthetic damage must preserve player's damage/kill credit");
            // Vanilla hurt cooldown passes only (new damage - original lastHurt) into LivingHurtEvent.
            h.assertTrue(Math.abs(observer.amount - (180 - observer.primaryIncoming)) < .01,
                    "Execute must remain 4*20+100 minus vanilla cooldown delta, without borrowing counter: " + observer.amount);
            h.assertTrue(!target.isAlive(), "Actual execute still deals its original lethal damage");
            h.assertTrue(!DynastyTrinketOnHit.isSyntheticDamage(), "Nested damage context must be cleared after return");

            var throwingTarget = new net.minecraft.world.entity.monster.Zombie(h.getLevel()) {
                @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
                    throw new IllegalStateException("synthetic-cleanup-fixture");
                }
            };
            throwingTarget.setHealth(2);
            boolean threw = false;
            try { DynastyTrinketOnHit.after(p, throwingTarget, 1); }
            catch (IllegalStateException expected) { threw = "synthetic-cleanup-fixture".equals(expected.getMessage()); }
            h.assertTrue(threw && !DynastyTrinketOnHit.isSyntheticDamage(), "Even an external hurt exception must not leak synthetic context to next attack");
        } finally {
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(observer);
            close(p);
        }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void schoolLifestealUsesFinalBonusOnceAndPreservesSpecialDamage(GameTestHelper h) {
        Fighter p = fighter(h, DynastyWeapons.LIUYUN_SWORD.get());
        try {
            LivingEntity target = enemy(h, 5, 4);
            equip(p, "ring", new ItemStack(accessory("lifedrain_ring"))); // deterministic 12%
            p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);
            p.setHealth(10);
            var s = DynastySchoolCombat.state(p);
            s.held = "liuyun_sword"; s.combo = 2; s.comboTarget = target.getUUID(); s.comboTick = DynastySchoolCombat.now(p);
            DynastySchoolCombat.attack(new AttackEntityEvent(p, target));
            var finalHit = new LivingHurtEvent(target, p.damageSources().playerAttack(p), 100);
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(finalHit);
            h.assertTrue(finalHit.getAmount() == 150, "Actual bus ordering applies school finisher");
            h.assertTrue(Math.abs(p.getHealth() - 28) < .001, "Lifesteal must heal 12% of 150 exactly once, not 100 or twice: " + p.getHealth());

            p.setHealth(10);
            var registry = h.getLevel().registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.DAMAGE_TYPE);
            var solarKey = net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.DAMAGE_TYPE,
                    new ResourceLocation(Dynasty.MODID, "solar_judgment"));
            var solar = new LivingHurtEvent(target, new net.minecraft.world.damagesource.DamageSource(registry.getHolderOrThrow(solarKey), p, p), 100);
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(solar);
            h.assertTrue(p.getHealth() == 10 && solar.getAmount() == 100, "Solar fixed-percent blast must still bypass weapon/proc pipeline");

            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));
            var contact = new LivingHurtEvent(target, p.damageSources().playerAttack(p), 100);
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(contact);
            h.assertTrue(p.getHealth() == 10, "Original deferred Qinglong contact must not heal early");
            var dragonKey = net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.DAMAGE_TYPE,
                    new ResourceLocation(Dynasty.MODID, "qinglong_descent"));
            var landing = new LivingHurtEvent(target, new net.minecraft.world.damagesource.DamageSource(registry.getHolderOrThrow(dragonKey), p, p), 100);
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(landing);
            h.assertTrue(landing.getAmount() == 100 && Math.abs(p.getHealth() - 22) < .001,
                    "Resolved Qinglong damage must keep stored amount and heal once only on landing");
        } finally { close(p); }
        h.succeed();
    }
}
