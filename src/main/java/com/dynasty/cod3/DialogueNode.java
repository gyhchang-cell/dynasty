package com.dynasty.cod3;

import java.util.List;
import java.util.Objects;

/** Immutable dialogue data. Text is always a language key; conditions are evaluated on the server. */
public record DialogueNode(String id, String textKey, List<Condition> conditions, List<Choice> choices) {
    public DialogueNode {
        requireId(id);
        requireTextKey(textKey);
        conditions = List.copyOf(conditions);
        choices = List.copyOf(choices);
        if (choices.stream().map(Choice::id).distinct().count() != choices.size())
            throw new IllegalArgumentException("Duplicate dialogue choice: " + id);
    }

    public record Context(boolean firstMeeting, boolean worldChanged, String heldItem) {
        public Context { Objects.requireNonNull(heldItem); }
    }

    public enum ConditionType { FIRST_MEETING, WORLD_CHANGED, HOLDS_ITEM }

    public record Condition(ConditionType type, String value) {
        public Condition {
            Objects.requireNonNull(type);
            Objects.requireNonNull(value);
            if (type == ConditionType.HOLDS_ITEM && !value.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
                throw new IllegalArgumentException("Invalid dialogue item: " + value);
        }
        public boolean matches(Context context) {
            return switch (type) {
                case FIRST_MEETING -> context.firstMeeting();
                case WORLD_CHANGED -> context.worldChanged();
                case HOLDS_ITEM -> value.equals(context.heldItem());
            };
        }
    }

    public enum Action { TALK, TRADE, LEAVE, DELIVER, DRINK, DISMANTLE }

    public record Choice(String id, String textKey, List<Condition> conditions, Action action, String nextNode) {
        public Choice {
            requireId(id);
            requireTextKey(textKey);
            conditions = List.copyOf(conditions);
            Objects.requireNonNull(action);
            Objects.requireNonNull(nextNode);
            if (action == Action.TALK) requireId(nextNode);
            else if (!nextNode.isEmpty()) throw new IllegalArgumentException("Terminal action has a next node");
        }
        public boolean available(Context context) { return conditions.stream().allMatch(c -> c.matches(context)); }
    }

    public boolean available(Context context) { return conditions.stream().allMatch(c -> c.matches(context)); }

    private static void requireId(String value) {
        if (value == null || !value.matches("[a-z][a-z0-9_]{0,63}"))
            throw new IllegalArgumentException("Invalid dialogue identifier");
    }
    private static void requireTextKey(String value) {
        if (value == null || !value.matches("[a-z0-9_.]+"))
            throw new IllegalArgumentException("Dialogue text must be a language key");
    }
}
