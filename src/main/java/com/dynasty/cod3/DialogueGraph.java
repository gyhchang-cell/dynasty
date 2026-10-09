package com.dynasty.cod3;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Validates every successor before a conversation can be opened. No executable commands in dialogue data. */
public record DialogueGraph(Map<String, DialogueNode> nodes, List<String> entries) {
    public DialogueGraph {
        nodes = Map.copyOf(nodes);
        entries = List.copyOf(entries);
        if (nodes.isEmpty() || entries.isEmpty()) throw new IllegalArgumentException("Empty dialogue graph");
        for (var entry : nodes.entrySet()) {
            if (!entry.getKey().equals(entry.getValue().id())) throw new IllegalArgumentException("Node key mismatch");
            for (var choice : entry.getValue().choices())
                if (choice.action() == DialogueNode.Action.TALK && !nodes.containsKey(choice.nextNode()))
                    throw new IllegalArgumentException("Missing successor: " + choice.nextNode());
        }
        for (var id : entries) if (!nodes.containsKey(id)) throw new IllegalArgumentException("Missing entry: " + id);
        boolean fallback = false;
        for (var id : entries) if (nodes.get(id).conditions().isEmpty()) fallback = true;
        if (!fallback) throw new IllegalArgumentException("Dialogue requires an unconditional fallback");
    }

    public DialogueNode entry(DialogueNode.Context context) {
        return entries.stream().map(nodes::get).filter(n -> n.available(context)).findFirst().orElseThrow();
    }

    public static DialogueGraph forRole(String role) {
        if (!role.matches("[a-z][a-z0-9_]+")) throw new IllegalArgumentException("Invalid NPC role");
        String prefix = "cod3.dynasty.npc." + role + ".";
        var changed = List.of(new DialogueNode.Condition(DialogueNode.ConditionType.WORLD_CHANGED, ""));
        String item = switch (role) {
            case "lao_chen" -> "dynasty:blueprint";
            case "han_chong" -> "dynasty:bamboo_slip";
            case "baibao_jin" -> "dynasty:copper_coin";
            default -> "";
        };
        var special = item.isEmpty() ? List.<DialogueNode.Condition>of()
                : List.of(new DialogueNode.Condition(DialogueNode.ConditionType.HOLDS_ITEM, item));
        var choices = new java.util.ArrayList<DialogueNode.Choice>();
        choices.add(new DialogueNode.Choice("talk", "cod3.dynasty.dialogue.talk", List.of(), DialogueNode.Action.TALK, "ordinary"));
        choices.add(new DialogueNode.Choice("changed", "cod3.dynasty.dialogue.changed", changed, DialogueNode.Action.TALK, "changed"));
        if (!item.isEmpty()) choices.add(new DialogueNode.Choice("special", "cod3.dynasty.dialogue.special", special, DialogueNode.Action.TALK, "special"));
        choices.add(new DialogueNode.Choice("trade", "cod3.dynasty.dialogue.trade", List.of(), DialogueNode.Action.TRADE, ""));
        choices.add(new DialogueNode.Choice("leave", "cod3.dynasty.dialogue.leave", List.of(), DialogueNode.Action.LEAVE, ""));
        var nodes = new LinkedHashMap<String, DialogueNode>();
        nodes.put("first", new DialogueNode("first", prefix + "first",
                List.of(new DialogueNode.Condition(DialogueNode.ConditionType.FIRST_MEETING, "")), choices));
        nodes.put("ordinary", new DialogueNode("ordinary", prefix + "ordinary", List.of(), choices));
        nodes.put("changed", new DialogueNode("changed", prefix + "changed", changed, choices));
        var entries = new java.util.ArrayList<String>();
        if (!item.isEmpty()) {
            nodes.put("special", new DialogueNode("special", prefix + "special", special, choices));
            entries.add("special");
        }
        entries.addAll(List.of("changed", "first", "ordinary"));
        return new DialogueGraph(nodes, entries);
    }

    /** The existing nonce/choice engine also owns the boat's paid delivery. */
    public static DialogueGraph forGhostBoat() {
        var leave = new DialogueNode.Choice("leave", "cod3.dynasty.dialogue.leave", List.of(), DialogueNode.Action.LEAVE, "");
        var trade = new DialogueNode.Choice("trade", "cod3.dynasty.dialogue.trade", List.of(), DialogueNode.Action.TRADE, "");
        var talk = new DialogueNode.Choice("talk", "cod4.dynasty.ghost_boat.talk", List.of(), DialogueNode.Action.TALK, "asked");
        var deliver = new DialogueNode.Choice("deliver", "cod4.dynasty.ghost_boat.deliver",
                List.of(new DialogueNode.Condition(DialogueNode.ConditionType.HOLDS_ITEM, "dynasty:cinnabar")), DialogueNode.Action.DELIVER, "");
        var nodes = new LinkedHashMap<String, DialogueNode>();
        nodes.put("first", new DialogueNode("first", "cod4.dynasty.ghost_boat.first", List.of(), List.of(talk, leave)));
        nodes.put("asked", new DialogueNode("asked", "cod4.dynasty.ghost_boat.asked", List.of(), List.of(deliver, trade, leave)));
        nodes.put("done", new DialogueNode("done", "cod4.dynasty.ghost_boat.done", List.of(), List.of(trade, leave)));
        return new DialogueGraph(nodes, List.of("first"));
    }
}
