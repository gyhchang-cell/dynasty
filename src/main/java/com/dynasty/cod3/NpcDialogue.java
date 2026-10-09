package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Per-player node and nonce. Each click rechecks the displayed choice and current server conditions. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class NpcDialogue {
    record Session(UUID npc, String dimension, long expires, DialogueGraph graph, String node,
                   boolean firstMeeting, String token, List<String> offered) {}
    private static final Map<UUID, Session> SESSIONS = new HashMap<>();
    private static final Map<String, DialogueGraph> GRAPHS = new HashMap<>();

    public static void open(ServerPlayer player, DynastyNpcEntity npc) {
        if (player.level() != npc.level() || !player.isAlive() || player.isSpectator()
                || !npc.isAlive() || player.distanceToSqr(npc) > 36) return;
        if (com.dynasty.expansion.SmallInteractions.isGhostBoat(npc)) {
            if (!com.dynasty.expansion.SmallInteractions.ghostBoatContext(player, npc)) return;
            npc.beginConversation(player);
            var graph = GRAPHS.computeIfAbsent("ghost_boat", ignored -> DialogueGraph.forGhostBoat());
            var root = com.dynasty.expansion.EquipmentBehaviors.saved(player);
            String node = SecretTracker.ghostBoatClaimed(player) ? "done" : root.getBoolean("site_ghost_market_boat_talked") ? "asked" : "first";
            show(player, npc, graph, graph.nodes().get(node), false);
            return;
        }
        npc.beginConversation(player);
        if (com.dynasty.expansion.SmallInteractions.isPoisonTea(npc)) {
            if (!com.dynasty.expansion.SmallInteractions.poisonTeaContext(player, npc)) return;
            var graph = GRAPHS.computeIfAbsent("poison_tea", ignored -> DialogueGraph.forPoisonTea());
            String node = com.dynasty.expansion.EquipmentBehaviors.saved(player).getBoolean("site_wayside_tea_stall_inspected") ? "inspected" : "first";
            show(player, npc, graph, graph.nodes().get(node), false);
            return;
        }
        String flag = "cod3_npc_met_" + npc.role;
        var saved = player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        boolean first = !saved.getBoolean(flag);
        var graph = GRAPHS.computeIfAbsent(npc.role, DialogueGraph::forRole);
        show(player, npc, graph, graph.entry(context(player, npc, first)), first);
        saved.putBoolean(flag, true);
        player.getPersistentData().put(Player.PERSISTED_NBT_TAG, saved);
    }

    private static DialogueNode.Context context(ServerPlayer player, DynastyNpcEntity npc, boolean first) {
        var item = ForgeRegistries.ITEMS.getKey(player.getMainHandItem().getItem());
        return new DialogueNode.Context(first, npc.worldChanged(), item == null ? "" : item.toString());
    }

    private static void show(ServerPlayer player, DynastyNpcEntity npc, DialogueGraph graph, DialogueNode node, boolean first) {
        var context = context(player, npc, first);
        var choices = node.choices().stream().filter(c -> c.available(context)).toList();
        String token = UUID.randomUUID().toString();
        SESSIONS.put(player.getUUID(), new Session(npc.getUUID(), player.level().dimension().location().toString(),
                player.level().getGameTime() + 200, graph, node.id(), first, token,
                choices.stream().map(DialogueNode.Choice::id).toList()));
        player.sendSystemMessage(npc.getDisplayName().copy().append(Component.literal(": "))
                .append(Component.translatable(node.textKey())));
        for (var choice : choices) player.sendSystemMessage(Component.translatable(choice.textKey()).withStyle(s ->
                s.withColor(net.minecraft.ChatFormatting.GOLD).withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND,
                        "/dynasty_dialogue " + token + " " + choice.id()))));
    }

    public static boolean choose(ServerPlayer player, String token, String choiceId) {
        var session = SESSIONS.get(player.getUUID());
        if (session == null || !session.token().equals(token)) return false;
        if (!valid(player, session)) { SESSIONS.remove(player.getUUID()); return false; }
        var npc = (DynastyNpcEntity) player.serverLevel().getEntity(session.npc());
        var context = context(player, npc, session.firstMeeting());
        var node = session.graph().nodes().get(session.node());
        if (!node.available(context)) {
            show(player, npc, session.graph(), session.graph().entry(context), session.firstMeeting());
            return false;
        }
        if (!session.offered().contains(choiceId)) return false;
        var choice = node.choices().stream().filter(c -> c.id().equals(choiceId) && c.available(context)).findFirst();
        if (choice.isEmpty()) return false;
        return switch (choice.get().action()) {
            case TALK -> {
                var next = session.graph().nodes().get(choice.get().nextNode());
                if (!next.available(context)) yield false;
                if (com.dynasty.expansion.SmallInteractions.isGhostBoat(npc))
                    com.dynasty.expansion.EquipmentBehaviors.saved(player).putBoolean("site_ghost_market_boat_talked", true);
                if (com.dynasty.expansion.SmallInteractions.isPoisonTea(npc))
                    com.dynasty.expansion.EquipmentBehaviors.saved(player).putBoolean("site_wayside_tea_stall_inspected", true);
                show(player, npc, session.graph(), next, session.firstMeeting());
                yield true;
            }
            case DELIVER -> {
                if (!com.dynasty.expansion.SmallInteractions.deliverGhostBoat(player, npc)) yield false;
                show(player, npc, session.graph(), session.graph().nodes().get("done"), session.firstMeeting());
                yield true;
            }
            case DRINK -> {
                if (!com.dynasty.expansion.SmallInteractions.drinkPoisonTea(player, npc)) yield false;
                show(player, npc, session.graph(), node, session.firstMeeting());
                yield true;
            }
            case DISMANTLE -> {
                if (!com.dynasty.expansion.SmallInteractions.flipPoisonTea(player, npc)) yield false;
                SESSIONS.remove(player.getUUID());
                yield true;
            }
            case TRADE -> {
                if (!npc.trade(player)) yield false;
                SESSIONS.remove(player.getUUID());
                yield true;
            }
            case LEAVE -> { SESSIONS.remove(player.getUUID()); yield true; }
        };
    }

    private static boolean valid(ServerPlayer player, Session session) {
        if (!player.isAlive() || player.isSpectator() || session.expires() <= player.level().getGameTime()
                || !session.dimension().equals(player.level().dimension().location().toString())) return false;
        var entity = player.serverLevel().getEntity(session.npc());
        return entity instanceof DynastyNpcEntity npc && npc.isAlive() && player.distanceToSqr(npc) <= 36
                && (!com.dynasty.expansion.SmallInteractions.isGhostBoat(npc) || com.dynasty.expansion.SmallInteractions.ghostBoatContext(player, npc))
                && (!com.dynasty.expansion.SmallInteractions.isPoisonTea(npc) || com.dynasty.expansion.SmallInteractions.poisonTeaContext(player, npc));
    }

    static Session session(UUID player) { return SESSIONS.get(player); }

    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("dynasty_dialogue")
                .then(Commands.argument("session", StringArgumentType.word())
                .then(Commands.argument("choice", StringArgumentType.word()).executes(c ->
                        choose(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "session"),
                                StringArgumentType.getString(c, "choice")) ? 1 : 0))));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || SESSIONS.isEmpty()) return;
        var server = net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();
        if (server == null || server.getTickCount() % 100 != 0) return;
        SESSIONS.entrySet().removeIf(entry -> {
            var player = server.getPlayerList().getPlayer(entry.getKey());
            return player == null || !valid(player, entry.getValue());
        });
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) { SESSIONS.remove(event.getEntity().getUUID()); }
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent event) { SESSIONS.remove(event.getEntity().getUUID()); }
    @SubscribeEvent public static void respawn(PlayerEvent.PlayerRespawnEvent event) { SESSIONS.remove(event.getEntity().getUUID()); }
    @SubscribeEvent public static void stop(ServerStoppedEvent event) { SESSIONS.clear(); GRAPHS.clear(); }
    private NpcDialogue() {}
}
