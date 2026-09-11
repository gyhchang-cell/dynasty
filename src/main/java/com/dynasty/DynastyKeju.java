package com.dynasty;

import com.dynasty.network.DynastyNetwork;
import com.dynasty.network.OpenKejuPacket;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.network.PacketDistributor;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 科举系统（服务端逻辑）：出题、判定、奖励；题目通过 GUI 展示。
 * Keju (imperial examination) server logic: questions, grading, rewards, shown in a GUI.
 */
@SuppressWarnings("null")
public final class DynastyKeju {

    private DynastyKeju() {
    }

    public static final String[][] QUESTIONS = {
            {"秦始皇统一六国是在公元前哪一年？", "前221年", "前206年", "前256年", "1"},
            {"“贞观之治”出现在哪个朝代？", "汉朝", "唐朝", "宋朝", "2"},
            {"科举制度正式创立于哪个朝代？", "隋朝", "明朝", "清朝", "1"},
            {"“文景之治”属于哪个朝代？", "秦朝", "汉朝", "唐朝", "2"},
            {"中国古代四大发明不包括？", "造纸术", "指南针", "地动仪", "3"},
            {"“开元盛世”是哪位皇帝在位时期？", "汉武帝", "唐玄宗", "宋太祖", "2"},
            {"《史记》的作者是谁？", "司马迁", "班固", "司马光", "1"},
    };

    private static final Map<UUID, Integer> PENDING = new HashMap<>();

    /** 打开科举界面：随机出题并发给玩家。/ Opens the exam GUI with a random question. */
    public static void openExam(ServerPlayer player) {
        int index = player.getRandom().nextInt(QUESTIONS.length);
        PENDING.put(player.getUUID(), index);
        DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                new OpenKejuPacket(index, QUESTIONS[index][0], QUESTIONS[index][1], QUESTIONS[index][2], QUESTIONS[index][3]));
    }

    /** 玩家当前待答题目下标（无则 null）。/ Pending question index for a player, or null. */
    public static Integer pending(net.minecraft.world.entity.player.Player player) {
        return PENDING.get(player.getUUID());
    }

    /** 判定答案并给予奖励。/ Grades the answer and grants rewards. */
    public static void handleAnswer(ServerPlayer player, int index, int choice) {
        Integer pending = PENDING.remove(player.getUUID());
        if (pending == null || pending != index) {
            player.sendSystemMessage(Component.literal("§c[科举] 题目已失效，请重新开始考试。"));
            return;
        }
        String correct = QUESTIONS[index][4];
        if (String.valueOf(choice).equals(correct)) {
            player.addEffect(new MobEffectInstance(DynastyEffects.DRAGON_MIGHT.get(), 20 * 180, 0));
            player.addEffect(new MobEffectInstance(DynastyEffects.SWIFT_WIND.get(), 20 * 180, 0));
            player.addEffect(new MobEffectInstance(DynastyEffects.MANDATE_OF_HEAVEN.get(), 20 * 180, 0));
            player.getInventory().add(new ItemStack(Items.WRITABLE_BOOK));
            player.sendSystemMessage(Component.literal("§a[科举] 金榜题名！你获得了官职认可（龙威 + 疾风 + 天命）"));
            DynastyQuestManager.notifyEvent(player, "keju");
        } else {
            player.sendSystemMessage(Component.literal("§c[科举] 答错了，正确答案是：" + correct));
        }
    }
}
