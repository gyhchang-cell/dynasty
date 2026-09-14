package com.dynasty;

import com.dynasty.entity.DynastyBossMechanics;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.Map;

/**
 * Boss 机制的战斗结算 + 首杀奖励。
 *
 * ① 护盾：护盾期间伤害被削掉 {@link DynastyBossMechanics#shieldCut}，并且只有**玩家**的攻击
 *    才算「打盾」的次数；打满次数 → 破盾 → 进入破绽窗口。
 * ② 破绽：窗口期内受到的伤害 ×倍率，玩家这时候集火才打得动高血量 Boss。
 * ③ 首杀：第一次击杀每个 Boss / 神兽，额外给功名与主题材料（一种只给一次），
 *    让「打 Boss」除了掉落之外还有明确的目标感。
 *
 * Combat resolution for the boss mechanics plus once-per-player first-kill rewards.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyBossCombat {

    private DynastyBossCombat() {
    }

    // ---------------------------------------------------------------- ①② 护盾 / 破绽
    @SubscribeEvent
    public static void onHurt(LivingHurtEvent event) {
        LivingEntity victim = event.getEntity();
        if (victim.level().isClientSide() || !DynastyBalance.isBossOrBeast(victim.getType())) {
            return;
        }
        boolean byPlayer = event.getSource().getEntity() instanceof Player;

        // 护盾：先削伤害，再记一次「打盾」
        if (DynastyBossMechanics.shielded(victim)) {
            float amount = event.getAmount() * (float) (1.0D - DynastyBossMechanics.shieldCut(victim));
            event.setAmount(Math.max(1.0F, amount));
            if (!byPlayer) {
                return;                                  // 小怪打不破盾，只能玩家来
            }
            Player attacker = (Player) event.getSource().getEntity();
            if (DynastyBossMechanics.hitShield(victim) && victim instanceof Mob mob) {
                DynastyBossMechanics.breakShield(mob, bossBarOf(mob), 140, 2.5D);
            } else {
                attacker.displayClientMessage(Component.literal("§d护盾：还需 "
                        + DynastyBossMechanics.shieldLeft(victim) + " 下"), true);
            }
            return;
        }

        // 破绽：集火窗口
        if (DynastyBossMechanics.weak(victim)) {
            event.setAmount((float) (event.getAmount() * DynastyBossMechanics.weakMultiplier(victim)));
        }
    }

    /** Boss 条：Boss 类自己暴露的（见 DynastyBosses 的 dynastyBossBar）/ boss bar accessor */
    private static net.minecraft.server.level.ServerBossEvent bossBarOf(Mob mob) {
        return mob instanceof BarHolder holder ? holder.dynastyBossBar() : null;
    }

    /** 有 Boss 条的 Boss 实现这个接口，护盾 / 破绽配色才能同步 / implemented by bosses */
    public interface BarHolder {
        net.minecraft.server.level.ServerBossEvent dynastyBossBar();
    }

    // ---------------------------------------------------------------- ③ 首杀奖励
    /** 首杀奖励表：Boss / 神兽 id → 功名 + 主题材料 / once-per-player first-kill table */
    private record FirstKill(int merit, String item, int count, String note) {
    }

    private static final Map<String, FirstKill> FIRST_KILL = new HashMap<>();

    static {
        FIRST_KILL.put("dragon_emperor",
                new FirstKill(400, "dragon_emperor_seal", 1, "龙帝玉玺到手：终盘装备的唯一凭据"));
        FIRST_KILL.put("undead_first_emperor",
                new FirstKill(300, "emperor_bone", 1, "帝骸骨到手：玄天 / 太乙系的强化材料"));
        FIRST_KILL.put("nine_heaven_general",
                new FirstKill(300, "sky_token", 1, "天界令牌到手：九霄的通行证"));
        FIRST_KILL.put("dragon_king",
                new FirstKill(320, "sea_token", 1, "龙宫令牌到手：龙鳞甲的前置"));
        FIRST_KILL.put("rebel_general",
                new FirstKill(240, "rebel_head", 1, "叛将首级到手：破军系兵器的前置"));
        FIRST_KILL.put("eunuch_mastermind",
                new FirstKill(240, "eunuch_token", 1, "内廷令牌到手：内造兵器的前置"));
        FIRST_KILL.put("phoenix", new FirstKill(120, "dragon_scale", 2, "凤凰羽落：龙鳞系材料"));
        FIRST_KILL.put("qilin", new FirstKill(120, "jade", 4, "麒麟献玉：玉料不愁"));
        FIRST_KILL.put("nian_beast", new FirstKill(100, "refined_steel", 3, "年兽镇宅：精钢入手"));
        FIRST_KILL.put("nine_tailed_fox", new FirstKill(100, "silk", 4, "狐尾丝线：织造材料"));
    }

    @SubscribeEvent
    public static void onDeath(LivingDeathEvent event) {
        if (event.getEntity().level().isClientSide()) {
            return;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(event.getEntity().getType());
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return;
        }
        FirstKill reward = FIRST_KILL.get(id.getPath());
        if (reward == null) {
            return;
        }
        LivingEntity credit = event.getEntity().getKillCredit();
        if (!(credit instanceof ServerPlayer player)) {
            return;
        }
        String flag = "dynasty_firstkill_" + id.getPath();
        if (player.getPersistentData().getBoolean(flag)) {
            return;                                        // 一种只给一次 / once per player
        }
        player.getPersistentData().putBoolean(flag, true);

        DynastyStats.addMerit(player, reward.merit());
        ResourceLocation key = ResourceLocation.tryBuild(Dynasty.MODID, reward.item());
        Item item = key == null ? null : ForgeRegistries.ITEMS.getValue(key);
        if (item != null) {
            ItemStack stack = new ItemStack(item, reward.count());
            if (!player.getInventory().add(stack)) {
                player.drop(stack, false);
            }
        }
        player.displayClientMessage(Component.literal("§6[首杀] §r" + reward.note()
                + " §7(功名 +" + reward.merit() + ")"), false);
        player.playNotifySound(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, net.minecraft.sounds.SoundSource.MASTER,
                0.8F, 1.0F);
    }
}
