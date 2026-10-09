package com.dynasty.cod3;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@GameTestHolder("dynasty_cod3")
@PrefixGameTestTemplate(false)
public final class NpcDialogueGameTests {
    @GameTest(template = "bow_ritual_test")
    public static void graphRoutesFirstOrdinaryWorldAndItemTopics(GameTestHelper h) {
        for (String role : NpcContent.NPCS.keySet()) {
            var graph = DialogueGraph.forRole(role);
            h.assertTrue(graph.entry(new DialogueNode.Context(true, false, "minecraft:air")).id().equals("first"), "First meeting lost");
            h.assertTrue(graph.entry(new DialogueNode.Context(false, false, "minecraft:air")).id().equals("ordinary"), "Ordinary fallback lost");
            h.assertTrue(graph.entry(new DialogueNode.Context(false, true, "minecraft:air")).id().equals("changed"), "World condition ignored");
            for (var node : graph.nodes().values()) for (var condition : node.conditions())
                if (condition.type() == DialogueNode.ConditionType.HOLDS_ITEM) {
                    var item = ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation(condition.value()));
                    h.assertTrue(item != null && item != net.minecraft.world.item.Items.AIR, "Dialogue references unregistered item");
                    h.assertTrue(graph.entry(new DialogueNode.Context(false, false, condition.value())).id().equals("special"), "Held item topic missing");
                }
        }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test")
    public static void definitionsRejectBrokenLinksAndRemainImmutable(GameTestHelper h) {
        var choices = new ArrayList<DialogueNode.Choice>();
        choices.add(new DialogueNode.Choice("leave", "cod3.dynasty.dialogue.leave", List.of(), DialogueNode.Action.LEAVE, ""));
        var node = new DialogueNode("ordinary", "cod3.dynasty.dialogue.talk", List.of(), choices);
        var nodes = new HashMap<String, DialogueNode>(); nodes.put(node.id(), node);
        var entries = new ArrayList<>(List.of("ordinary"));
        var graph = new DialogueGraph(nodes, entries);
        choices.clear(); nodes.clear(); entries.clear();
        h.assertTrue(graph.nodes().size() == 1 && graph.entries().size() == 1 && node.choices().size() == 1, "Mutable data escaped into graph");
        boolean rejected = false;
        try {
            var bad = new DialogueNode("ordinary", "cod3.dynasty.dialogue.talk", List.of(), List.of(
                    new DialogueNode.Choice("talk", "cod3.dynasty.dialogue.talk", List.of(), DialogueNode.Action.TALK, "missing")));
            new DialogueGraph(Map.of("ordinary", bad), List.of("ordinary"));
        } catch (IllegalArgumentException expected) { rejected = true; }
        h.assertTrue(rejected, "Broken successor was accepted");
        rejected = false;
        try { new DialogueNode("ordinary", "硬编码对白", List.of(), List.of()); }
        catch (IllegalArgumentException expected) { rejected = true; }
        h.assertTrue(rejected, "Non-language-key text was accepted");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test")
    public static void playersKeepSeparateNodesAndOldButtonsCannotReplay(GameTestHelper h) {
        var npc = npc(h, "lao_chen"); var p = player(h, npc); var q = player(h, npc);
        NpcDialogue.open(p, npc); NpcDialogue.open(q, npc);
        var a = NpcDialogue.session(p.getUUID()); var b = NpcDialogue.session(q.getUUID());
        h.assertTrue(a != null && b != null && !a.token().equals(b.token()), "Shared session token");
        h.assertTrue(!NpcDialogue.choose(q, a.token(), "talk"), "Another player's token was accepted");
        h.assertTrue(!NpcDialogue.choose(p, a.token(), "special"), "Unshown item-gated choice was accepted");
        h.assertTrue(NpcDialogue.choose(p, a.token(), "talk"), "Successor did not execute");
        h.assertTrue(NpcDialogue.session(p.getUUID()).node().equals("ordinary"), "Wrong successor");
        h.assertTrue(!NpcDialogue.choose(p, a.token(), "trade"), "Old node button replayed");
        h.assertTrue(NpcDialogue.session(q.getUUID()).equals(b), "Player A changed player B's conversation");
        h.assertTrue(NpcDialogue.choose(q, b.token(), "leave") && NpcDialogue.session(q.getUUID()) == null, "Leave did not close session");
        NpcDialogue.logout(new PlayerEvent.PlayerLoggedOutEvent(p)); npc.discard(); h.succeed();
    }

    @GameTest(template = "bow_ritual_test")
    public static void heldItemChangesAreRecheckedBeforeExecutingTheChoice(GameTestHelper h) {
        var npc = npc(h, "lao_chen"); var p = player(h, npc);
        var item = ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:blueprint"));
        p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(item));
        NpcDialogue.open(p, npc); var old = NpcDialogue.session(p.getUUID());
        h.assertTrue(old.node().equals("special"), "Item condition did not select special node");
        p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
        h.assertTrue(!NpcDialogue.choose(p, old.token(), "trade"), "Changed condition executed stale node action");
        h.assertTrue(!NpcDialogue.session(p.getUUID()).node().equals("special"), "Unavailable node was not refreshed");
        h.assertTrue(!NpcDialogue.choose(p, old.token(), "leave"), "Old token survived condition refresh");
        NpcDialogue.logout(new PlayerEvent.PlayerLoggedOutEvent(p)); npc.discard(); h.succeed();
    }

    @GameTest(template = "bow_ritual_test")
    public static void firstMeetingPersistsAndDistanceAndLogoutCloseSessions(GameTestHelper h) {
        var npc = npc(h, "han_chong"); var p = player(h, npc);
        NpcDialogue.open(p, npc);
        h.assertTrue(NpcDialogue.session(p.getUUID()).firstMeeting(), "First meeting was not recognized");
        h.assertTrue(p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).getBoolean("cod3_npc_met_han_chong"), "Meeting receipt not persistent");
        NpcDialogue.open(p, npc);
        h.assertTrue(!NpcDialogue.session(p.getUUID()).firstMeeting(), "Meeting repeated on reopen");
        var session = NpcDialogue.session(p.getUUID()); p.setPos(p.getX() + 20, p.getY(), p.getZ());
        h.assertTrue(!NpcDialogue.choose(p, session.token(), "talk") && NpcDialogue.session(p.getUUID()) == null, "Distant action remained valid");
        p.setPos(npc.getX(), npc.getY(), npc.getZ()); NpcDialogue.open(p, npc);
        NpcDialogue.logout(new PlayerEvent.PlayerLoggedOutEvent(p));
        h.assertTrue(NpcDialogue.session(p.getUUID()) == null, "Logout retained a conversation");
        npc.discard(); h.succeed();
    }

    @GameTest(template = "bow_ritual_test")
    public static void busyMerchantAndMissingNpcCannotBeAddressed(GameTestHelper h) {
        var npc = npc(h, "baibao_jin"); var p = player(h, npc); var q = player(h, npc);
        npc.setTradingPlayer(p); NpcDialogue.open(q, npc); var session = NpcDialogue.session(q.getUUID());
        h.assertTrue(!NpcDialogue.choose(q, session.token(), "trade") && npc.getTradingPlayer() == p, "Trade stole another player's merchant");
        h.assertTrue(NpcDialogue.session(q.getUUID()).equals(session), "Failed trade consumed the session");
        npc.setTradingPlayer(null); npc.discard();
        h.assertTrue(!NpcDialogue.choose(q, session.token(), "talk") && NpcDialogue.session(q.getUUID()) == null, "Removed NPC remained addressable");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test")
    public static void dimensionAndRespawnInvalidateOnlyTheAffectedPlayer(GameTestHelper h) {
        var npc = npc(h, "baibao_jin"); var p = player(h, npc); var q = player(h, npc);
        NpcDialogue.open(p, npc); NpcDialogue.open(q, npc);
        var other = NpcDialogue.session(q.getUUID());
        NpcDialogue.dimension(new PlayerEvent.PlayerChangedDimensionEvent(p, h.getLevel().dimension(), net.minecraft.world.level.Level.NETHER));
        h.assertTrue(NpcDialogue.session(p.getUUID()) == null && NpcDialogue.session(q.getUUID()).equals(other), "Dimension change cleared other player's node");
        NpcDialogue.respawn(new PlayerEvent.PlayerRespawnEvent(q, false));
        h.assertTrue(NpcDialogue.session(q.getUUID()) == null, "Respawn retained dialogue actions");
        npc.discard(); h.succeed();
    }

    private static DynastyNpcEntity npc(GameTestHelper h, String role) {
        var npc = NpcContent.NPCS.get(role).get().create(h.getLevel());
        npc.moveTo(h.absolutePos(new BlockPos(3, 2, 3)), 0, 0); npc.setNoAi(true);
        h.getLevel().addFreshEntity(npc); return npc;
    }
    private static FakePlayer player(GameTestHelper h, DynastyNpcEntity npc) {
        var p = new FakePlayer(h.getLevel(), new GameProfile(UUID.randomUUID(), "cod3-dialogue"));
        p.setPos(npc.getX(), npc.getY(), npc.getZ()); return p;
    }
}
